"""Project 3 acceptance tests (Lecture 9.7): issue to PR with guardrails, a human merge gate and an
audit log. Each test runs the real pipeline against a throwaway git repository."""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from agent_pipeline import pipeline, storm  # noqa: E402

AGENT = [sys.executable, str(ROOT / "tools" / "agent_pipeline" / "fake_agent.py")]
NOW = datetime(2026, 3, 10, 9, 0, tzinfo=timezone.utc)


@pytest.fixture
def repo(tmp_path):
    repo = storm.make_repo(tmp_path)
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("name: ci\n")
    (repo / "docs" / "issues" / "Q21.md").write_text("# Q21\n\n**Labels:** agent-ok\n\nFix it.\n")
    (repo / "docs" / "issues" / "Q30.md").write_text("# Q30\n\n**Labels:** needs-design\n\nBig change.\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.com", "-c", "user.name=t",
                    "commit", "-qm", "more"], check=True)
    return repo


def config(repo, **overrides):
    base = {"allowed_paths": ["services/**", "docs/**"], "required_checks": [],
            "budget": {"max_files": 3, "max_changed_lines": 50, "max_minutes": 5, "max_usd": 1.0}}
    return pipeline.load_config(repo, {**base, **overrides})


def run(repo, issue="Q21", *agent_args, cfg=None, now=NOW, actor="person"):
    return pipeline.run(repo, repo / "docs" / "issues" / f"{issue}.md", AGENT + list(agent_args),
                        cfg or config(repo), now=now, actor=actor)


def test_in_scope_change_opens_a_pr_awaiting_a_human(repo):
    result = run(repo, "Q21", "--touch", "services/orders/flaky.py")
    assert result["status"] == "pr_opened" and result["pr"] == "PR-1"
    (pr,) = pipeline.prs(repo, config(repo))
    assert pr["status"] == "awaiting-human" and pr["files"] == ["services/orders/flaky.py"] and pr["usd"] == 0.08


def test_out_of_scope_and_over_budget_changes_are_rejected(repo):
    rejected = run(repo, "Q21", "--touch", ".github/workflows/ci.yml")
    assert rejected["problems"] == ["denied path: .github/workflows/ci.yml"]
    result = run(repo, "Q21", "--touch", "services/orders/flaky.py", "--lines", "60", "--cost", "2.5")
    assert result["problems"] == ["too many changed lines: 60 > 50", "too expensive: $2.50 > $1.00"]
    assert pipeline.prs(repo, config(repo)) == []


def test_failing_required_check_opens_no_pr(repo):
    cfg = config(repo, required_checks=[{"name": "tests", "command": [sys.executable, "-c", "raise SystemExit(1)"]}])
    result = run(repo, "Q21", "--touch", "services/orders/flaky.py", cfg=cfg)
    assert result["status"] == "checks-failed" and result["check"] == "tests"
    assert pipeline.prs(repo, cfg) == []


def test_unlabelled_issue_bot_trigger_and_kill_switch_are_refused(repo):
    assert run(repo, "Q30", "--touch", "services/orders/flaky.py")["status"] == "refused"
    assert "bot" in run(repo, "Q21", "--touch", "services/orders/flaky.py", actor="orderhub-agent")["reason"]
    (repo / ".agent-pipeline").mkdir()
    (repo / ".agent-pipeline" / "STOP").write_text("stop\n")
    assert run(repo, "Q21", "--touch", "services/orders/flaky.py")["status"] == "stopped"


def test_second_run_for_an_open_issue_is_a_duplicate_and_rate_limit_applies(repo):
    run(repo, "Q21", "--touch", "services/orders/flaky.py")
    assert run(repo, "Q21", "--touch", "services/orders/flaky.py")["status"] == "duplicate"
    cfg = config(repo, max_runs_per_hour=1)
    later = NOW + timedelta(minutes=5)
    (repo / "docs" / "issues" / "Q22.md").write_text("# Q22\n\n**Labels:** agent-ok\n")
    assert "rate limit" in run(repo, "Q22", "--touch", "docs/x.md", cfg=cfg, now=later)["reason"]


def test_only_a_named_person_can_approve_and_approval_creates_a_branch(repo):
    run(repo, "Q21", "--touch", "services/orders/flaky.py")
    cfg = config(repo)
    assert pipeline.approve(repo, "PR-1", "", cfg)["status"] == "refused"
    assert "cannot approve" in pipeline.approve(repo, "PR-1", "orderhub-agent", cfg)["reason"]
    result = pipeline.approve(repo, "PR-1", "Asha Rao", cfg)
    assert result == {"status": "approved", "pr": "PR-1", "branch": "agent/pr-1"}
    log = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%an%n%B", "agent/pr-1"],
                         capture_output=True, text=True).stdout
    assert log.startswith("orderhub-agent\nQ21: agent change (PR-1)") and "Approved-by: Asha Rao" in log
    assert pipeline.approve(repo, "PR-1", "Asha Rao", cfg)["status"] == "refused"


def test_audit_log_records_every_decision_and_detects_tampering(repo):
    run(repo, "Q21", "--touch", ".github/workflows/ci.yml")
    run(repo, "Q21", "--touch", "services/orders/flaky.py")
    pipeline.approve(repo, "PR-1", "Asha Rao", config(repo))
    cfg = config(repo)
    events = [e["event"] for e in pipeline.audit_entries(repo, cfg)]
    assert events == ["run_started", "rejected", "run_started", "pr_opened", "approved"]
    assert pipeline.verify_audit(repo, cfg) == []
    log = repo / "out" / "agent-pipeline" / "audit.jsonl"
    lines = log.read_text().splitlines()
    entry = json.loads(lines[1])
    entry["problems"] = []
    lines[1] = json.dumps(entry, sort_keys=True)
    log.write_text("\n".join(lines) + "\n")
    assert pipeline.verify_audit(repo, cfg) == ["audit entry 2 (rejected) does not match the chain"]


def test_storm_is_contained_by_deduplication_and_the_kill_switch():
    assert storm.simulate(20) == {"pr_opened": 1, "duplicate": 19}
    assert storm.simulate(20, as_bot=True) == {"pr_opened": 1, "refused": 19}
    assert storm.simulate(20, stop_after=0) == {"stopped": 20}
