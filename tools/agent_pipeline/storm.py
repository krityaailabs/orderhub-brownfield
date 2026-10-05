"""Simulate the runaway pull-request storm from the Section 9 incident (Lecture 9.6).

A scheduled "flaky-test triage" job is triggered once per failing CI run. Its own pull requests
run CI, a flaky test fails, and that triggers the job again. This replays N triggers against a
throwaway copy of a tiny repository, with the pipeline's real guardrails, and reports what
happened to each trigger.

Usage: python tools/agent_pipeline/storm.py [TRIGGERS] [--stop-after N] [--as-bot]
"""

import json
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_pipeline import pipeline  # noqa: E402

FAKE_AGENT = Path(__file__).with_name("fake_agent.py")
ISSUE = """# FLAKY-1: test_daily_report_window is flaky

**Labels:** agent-ok

Triage the flaky test and propose a fix.
"""


def make_repo(root: Path) -> Path:
    repo = root / "repo"
    (repo / "services" / "orders").mkdir(parents=True)
    (repo / "services" / "orders" / "flaky.py").write_text("x = 1\n")
    (repo / "docs" / "issues").mkdir(parents=True)
    (repo / "docs" / "issues" / "FLAKY-1.md").write_text(ISSUE)
    (repo / ".gitignore").write_text("out/\n.agent-pipeline/\n")
    commit = ["-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "init"]
    for args in (["init", "-q"], ["add", "-A"], commit):
        subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
    return repo


def simulate(triggers: int = 40, stop_after: int | None = None, as_bot: bool = False) -> Counter:
    tmp = Path(tempfile.mkdtemp(prefix="storm-"))
    try:
        repo = make_repo(tmp)
        config = pipeline.load_config(repo, {"allowed_paths": ["services/**"], "required_checks": [],
                                             "max_runs_per_hour": 100, "max_open_prs": 100})
        start = datetime(2026, 3, 10, 1, 0, tzinfo=timezone.utc)
        outcomes = Counter()
        for i in range(triggers):
            if stop_after is not None and i == stop_after:
                (repo / config["kill_switch"]).parent.mkdir(parents=True, exist_ok=True)
                (repo / config["kill_switch"]).write_text("stop\n")
            result = pipeline.run(repo, repo / "docs" / "issues" / "FLAKY-1.md",
                                  [sys.executable, str(FAKE_AGENT), "--touch", "services/orders/flaky.py"],
                                  config, now=start + timedelta(seconds=30 * i),
                                  actor=config["agent_identity"] if as_bot and i > 0 else "ci-failure")
            outcomes[result["status"]] += 1
        return outcomes
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    triggers = int(args[0]) if args and args[0].isdigit() else 40
    stop_after = int(args[args.index("--stop-after") + 1]) if "--stop-after" in args else None
    outcomes = simulate(triggers, stop_after, "--as-bot" in args)
    print(f"storm: {triggers} triggers -> " + json.dumps(dict(sorted(outcomes.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
