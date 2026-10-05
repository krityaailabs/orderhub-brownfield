"""Lab s10 (Lecture 10.4): the evaluation harness scores tools fairly."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval_harness"))

import harness  # noqa: E402

CHECKS = ("applied", "acceptance", "full_suite", "lint", "in_scope")


def result(tool, task, usd, review, lines, fail=None):
    r = {"tool": tool, "task": task, "usd": usd, "review_minutes": review, "changed_lines": lines}
    r.update({k: True for k in CHECKS})
    if fail:
        r[fail] = False
        if fail == "applied":
            r.update({k: False for k in CHECKS})
    return r


@pytest.mark.parametrize("fail", CHECKS)
def test_every_check_is_required_for_success(fail):
    assert harness.is_success(result("a", "T1", 0.1, 2, 5)) is True
    assert harness.is_success(result("a", "T1", 0.1, 2, 5, fail=fail)) is False


def test_summary_counts_cost_of_failures_and_names_the_first_failing_check():
    results = [result("x", "T1", 0.30, 4, 10), result("x", "T2", 0.50, 9, 30, fail="full_suite"),
               result("x", "T3", 0.20, 2, 6), result("y", "T1", 0.05, 1, 2, fail="applied"),
               result("y", "T2", 0.05, 1, 2, fail="lint")]
    s = harness.summarise(results)
    assert list(s) == ["x", "y"]
    assert s["x"] == {"tasks": 3, "successes": 2, "success_rate": 0.67, "total_usd": 1.0, "cost_per_success": 0.5,
                      "median_review_minutes": 3.0, "median_changed_lines": 8.0, "failures": {"T2": "full suite"}}
    assert s["y"]["cost_per_success"] is None and s["y"]["median_review_minutes"] is None
    assert s["y"]["failures"] == {"T1": "patch did not apply", "T2": "lint"}


def test_harness_runs_real_tasks_against_recordings():
    results = [harness.run_task("tool-b", "T1"), harness.run_task("tool-b", "T4")]
    assert harness.is_success(results[0]) and results[0]["changed_lines"] == 2
    assert results[1]["applied"] and not results[1]["acceptance"]
    assert harness.summarise(results)["tool-b"]["failures"] == {"T4": "acceptance"}
