"""Lab s09 (Lecture 9.3): scope and budget guardrails for unattended agents."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_pipeline.guardrails import DiffStats, check_budget, check_scope, matches  # noqa: E402

ALLOWED = ["services/orders/**", "docs/**"]
DENIED = [".github/**", "**/AGENTS.md", "requirements.lock", "services/orders/orderhub/payments/**"]


def test_matches_handles_top_level_double_star():
    assert matches("AGENTS.md", ["**/AGENTS.md"]) and matches("legacy/billing/AGENTS.md", ["**/AGENTS.md"])


def test_paths_inside_scope_pass():
    assert check_scope(["services/orders/orderhub/orders.py", "docs/issues/Q21.md"], ALLOWED, DENIED) == []


def test_denied_wins_and_outside_is_reported_in_order():
    paths = [".github/workflows/ci.yml", "services/orders/AGENTS.md", "tools/precommit.py",
             "services/orders/orderhub/payments/charge.py", "requirements.lock"]
    assert check_scope(paths, ALLOWED, DENIED) == [
        "denied path: .github/workflows/ci.yml", "denied path: services/orders/AGENTS.md",
        "outside allowed paths: tools/precommit.py", "denied path: services/orders/orderhub/payments/charge.py",
        "denied path: requirements.lock"]


def test_no_changes_is_a_problem():
    assert check_scope([], ALLOWED, DENIED) == ["no changes"]


BUDGET = {"max_files": 3, "max_changed_lines": 100, "max_minutes": 10, "max_usd": 1.5}


def test_within_budget():
    assert check_budget(DiffStats(["a", "b"], 100, 9.9, 1.5), BUDGET) == []


def test_every_exceeded_limit_is_reported_in_order():
    stats = DiffStats(["a", "b", "c", "d"], 101, 12.25, 2.0)
    assert check_budget(stats, BUDGET) == ["too many files: 4 > 3", "too many changed lines: 101 > 100",
                                           "too long: 12.2 min > 10 min", "too expensive: $2.00 > $1.50"]


def test_unreported_cost_is_a_problem_only_when_capped():
    assert check_budget(DiffStats(["a"], 1, 1.0, None), BUDGET) == ["cost not reported (max_usd is set)"]
    assert check_budget(DiffStats(["a"], 1, 1.0, None), {"max_files": 3}) == []


def test_missing_keys_mean_no_limit():
    assert check_budget(DiffStats(["a"] * 50, 10_000, 600.0, 99.0), {}) == []
