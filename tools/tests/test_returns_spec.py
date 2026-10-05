"""Checks the returns spec and plan written in Lab s03. Fails at s03-start, passes at s03."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import spec_check as sc  # noqa: E402

SPECS = Path(__file__).resolve().parents[2] / "docs" / "specs"


def spec_text() -> str:
    return (SPECS / "returns.md").read_text(encoding="utf-8")


def plan_text() -> str:
    return (SPECS / "returns.plan.md").read_text(encoding="utf-8")


def test_returns_spec_and_plan_pass_the_rubric():
    assert sc.check_pair(SPECS / "returns.md", SPECS / "returns.plan.md") == []


def test_spec_pins_the_money_with_concrete_numbers():
    criteria = " ".join(text for _, text in sc.parse_criteria(spec_text()))
    assert "4095" in criteria, "a criterion should pin the discounted refund for 1 x STAND-LAP with SAVE10"
    assert "30 days" in criteria


def test_spec_says_what_it_does_not_do():
    non_goals = sc._section(sc.parse_sections(spec_text()), "Non-goals").lower()
    assert "card" in non_goals or "payment" in non_goals
    assert "billing" in non_goals


def test_spec_protects_the_billing_contract():
    assert "billing-demo" in spec_text()


def test_plan_has_at_least_four_reviewable_slices():
    slices = sc.parse_slices(plan_text())
    assert len(slices) >= 4
    assert all(s["size"] is not None and s["size"] <= 300 for s in slices)
