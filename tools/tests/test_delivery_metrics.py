"""Lab s12 (Lectures 12.3 and 12.4): delivery metrics and the cost model measure what they claim."""

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "metrics"))
sys.path.insert(0, str(ROOT / "labs" / "s12"))

import build_history  # noqa: E402
import cost_model  # noqa: E402
import delivery_metrics as dm  # noqa: E402

T0 = datetime(2026, 3, 2, 12, 0, tzinfo=timezone.utc)


def pr(number, day, fixes=(), reverts=()):
    return {"pr": number, "merged_at": T0 + timedelta(days=day), "fixes": list(fixes), "reverts": list(reverts)}


# ---------------------------------------------------------------- size

def test_size_counts_added_and_deleted_lines():
    assert dm.changed_lines([(10, 4, "app/orders/a.py"), (6, 0, "tests/test_a.py")]) == 20


def test_size_ignores_generated_and_binary_files():
    files = [(3, 1, "app/a.py"), (400, 380, "requirements.lock"), (-1, -1, "docs/diagram.png"),
             (50, 0, "web/generated/client.ts")]
    assert dm.changed_lines(files) == 4


# ---------------------------------------------------------------- review time

def test_review_hours_from_opened():
    event = {"opened_at": "2026-03-02T09:00:00Z", "first_review_at": "2026-03-02T13:30:00Z",
             "merged_at": "2026-03-03T09:00:00Z"}
    assert dm.review_hours(event) == (4.5, 24.0)


def test_unreviewed_pr_waits_until_merge():
    event = {"opened_at": "2026-03-02T09:00:00Z", "first_review_at": "", "merged_at": "2026-03-02T10:15:00Z"}
    assert dm.review_hours(event) == (1.2, 1.2)


# ---------------------------------------------------------------- change failure

def test_change_failure_rate_counts_deployments():
    deploys = [{"outcome": "ok"}, {"outcome": "failed"}, {"outcome": "ok"}]
    assert dm.change_failure_rate(deploys) == 0.333


def test_change_failure_rate_without_deployments_is_unknown_not_zero():
    assert dm.change_failure_rate([]) is None


# ---------------------------------------------------------------- rework

def test_fix_or_revert_within_window_is_rework():
    prs = [pr(1, 0), pr(2, 0), pr(3, 5, fixes=[1]), pr(4, 30, reverts=[2])]
    assert dm.rework(prs, T0 + timedelta(days=100)) == (1, 4)


def test_recent_prs_are_not_yet_eligible():
    prs = [pr(1, 0), pr(2, 90)]
    assert dm.rework(prs, T0 + timedelta(days=100)) == (0, 1)


def test_fixes_from_outside_the_group_count():
    group = [pr(1, 0)]
    everyone = group + [pr(9, 3, fixes=[1])]
    assert dm.rework(group, T0 + timedelta(days=100)) == (0, 1)
    assert dm.rework(group, T0 + timedelta(days=100), everyone) == (1, 1)


# ---------------------------------------------------------------- end to end on the lab's history

@pytest.fixture(scope="module")
def history(tmp_path_factory):
    path = tmp_path_factory.mktemp("history") / "repo"
    prs, _deploys = build_history.generate()
    build_history.build_repo(prs, path)
    return path


def test_history_is_reproducible_and_matches_the_exports(history, tmp_path):
    prs, deploys = build_history.generate()
    build_history.write_csvs(prs, deploys, tmp_path)
    for name in ("pr_events.csv", "deploys.csv"):
        assert (tmp_path / name).read_text() == (build_history.DATA / name).read_text()
    assert len(dm.load_git(history)) == len(prs) == 256


def test_report_on_the_lab_history(history):
    text = dm.report(history, datetime(2026, 4, 6, tzinfo=timezone.utc))
    assert "| Baseline, all | 87 | 6.8 | 74 / 165 | 1% (1/87) | 4.5 / 11.1 | 13.1 / 27.6 | 9% (8/87) |" in text
    assert "| Pilot, agent-assisted (people) | 102 |" in text and "17% (13/77) |" in text
    assert "| baseline | 23 | 13% | 13% (3/23) | 54 / 125.5 |" in text and "| pilot | 36 | 28% |" in text


def test_metrics_script_explains_a_missing_history(tmp_path, capsys):
    assert dm.main(["--repo", str(tmp_path / "nothing")]) == 2
    assert "build_history.py" in capsys.readouterr().out


# ---------------------------------------------------------------- cost model

def params(**overrides):
    base = {name: {"value": 1, "source": "assumption: test"} for name in cost_model.PARAMETERS}
    base["rework_rate"] = {"value": 0.5, "source": "measured: test"}
    base.update(overrides)
    return base


def test_every_number_needs_a_value_and_a_source():
    p = params(licence_per_engineer_month={"value": None, "source": "quote: x"},
               author_hours_per_pr={"value": 2, "source": "my guess"})
    del p["engineers"]
    assert cost_model.validate(p) == ["engineers: missing", "licence_per_engineer_month: no value",
                                      "author_hours_per_pr: no source"]


def test_cost_per_merged_pr_by_part():
    p = params(loaded_cost_per_engineer_hour={"value": 100, "source": "assumption: x"},
               licence_per_engineer_month={"value": 40, "source": "quote: x"},
               merged_prs_per_engineer_month={"value": 8, "source": "measured: x"},
               enablement_hours_per_engineer_month={"value": 4, "source": "assumption: x"},
               agent_usage_per_pr={"value": 3, "source": "measured: x"},
               author_hours_per_pr={"value": 10, "source": "assumption: x"},
               review_hours_per_pr={"value": 1, "source": "assumption: x"},
               rework_rate={"value": 0.2, "source": "measured: x"},
               rework_hours_per_reworked_pr={"value": 4, "source": "assumption: x"},
               engineers={"value": 10, "source": "assumption: x"})
    r = cost_model.cost_per_merged_pr(p)
    assert r == {"licence": 5.0, "enablement": 50.0, "usage": 3, "author": 1000, "review": 100, "rework": 80.0,
                 "total": 1238.0, "assumptions": 6, "monthly": 99040}


def test_cost_model_refuses_to_guess():
    with pytest.raises(ValueError, match="engineers: no value"):
        cost_model.cost_per_merged_pr(params(engineers={"value": None, "source": "assumption: x"}))


def test_scenarios_file_runs_with_every_number_sourced():
    config = json.loads((ROOT / "labs" / "s12" / "cost-scenarios.json").read_text())
    out = cost_model.table(config)
    assert not out.startswith("cost model refused"), out
    assert out.count("\n") == 1 + 2 * len(config["scenarios"])


def test_build_history_runs_as_a_script(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / "labs" / "s12" / "build_history.py"), str(tmp_path / "h")],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0 and "256 merged pull requests" in result.stdout
