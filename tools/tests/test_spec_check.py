"""Tests for tools/spec_check.py. They fail at s03-start (stubs) and pass at s03."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import spec_check as sc  # noqa: E402

GOOD = """# Spec: X
## Intent
Why.
## Context
What exists.
## Constraints
Rules.
## Acceptance criteria
- **AC-1** Given a basket, when I pay, then I get a receipt.
- **AC-2** Given an empty basket, when I pay, then I see an error.
- **AC-3** Given a paid order, when I refresh, then it is still paid.
## Non-goals
- Refunds.
## Open questions
None.
"""

PLAN = """# Plan
### S1: Receipt
- Criteria: AC-1, AC-3
- Size: ~120 lines
- Depends on: none
### S2: Empty basket
- Criteria: AC-2
- Size: ~40 lines
- Depends on: S1
"""


def test_parse_criteria_reads_bold_ids_in_order():
    assert sc.parse_criteria(GOOD) == [
        ("AC-1", "Given a basket, when I pay, then I get a receipt."),
        ("AC-2", "Given an empty basket, when I pay, then I see an error."),
        ("AC-3", "Given a paid order, when I refresh, then it is still paid."),
    ]


def test_parse_criteria_without_section_is_empty():
    assert sc.parse_criteria("# nothing here") == []


def test_good_spec_has_no_problems():
    assert sc.check_spec(GOOD) == []


def test_missing_sections_are_reported():
    text = GOOD.replace("## Non-goals\n- Refunds.\n", "").replace("## Context\nWhat exists.\n", "")
    assert sc.check_spec(text) == ["missing section: Context", "missing section: Non-goals"]


def test_too_few_criteria():
    text = GOOD.replace("- **AC-3** Given a paid order, when I refresh, then it is still paid.\n", "")
    assert "too few acceptance criteria: 2 (minimum 3)" in sc.check_spec(text)


def test_criteria_ids_must_be_sequential():
    text = GOOD.replace("**AC-3**", "**AC-7**")
    assert "criteria ids must be AC-1..AC-n in order" in sc.check_spec(text)


def test_criterion_needs_given_when_then_in_order():
    text = GOOD.replace("Given a basket, when I pay, then I get a receipt.", "It should work when I pay.")
    assert "AC-1: needs Given, When and Then in that order" in sc.check_spec(text)
    text = GOOD.replace(
        "Given a basket, when I pay, then I get a receipt.", "Then a receipt, given a basket, when paid."
    )
    assert "AC-1: needs Given, When and Then in that order" in sc.check_spec(text)


def test_words_inside_other_words_do_not_count():
    text = GOOD.replace("Given a basket, when I pay, then I get a receipt.", "Forgiven whenever thenceforth.")
    assert "AC-1: needs Given, When and Then in that order" in sc.check_spec(text)


def test_non_goals_need_a_bullet_and_todo_is_flagged():
    text = GOOD.replace("- Refunds.", "We'll see. TODO")
    problems = sc.check_spec(text)
    assert "non-goals: list at least one" in problems and "unresolved TODO" in problems


def test_parse_slices():
    assert sc.parse_slices(PLAN) == [
        {"id": "S1", "title": "Receipt", "criteria": ["AC-1", "AC-3"], "size": 120, "depends": []},
        {"id": "S2", "title": "Empty basket", "criteria": ["AC-2"], "size": 40, "depends": ["S1"]},
    ]


def test_good_plan_has_no_problems():
    assert sc.check_slices(sc.parse_slices(PLAN), ["AC-1", "AC-2", "AC-3"]) == []


def test_slice_problems_are_all_reported():
    plan = """### S1: Big bang
- Criteria: AC-1, AC-9
- Size: ~900 lines
- Depends on: S2
### S2: Nothing
- Depends on: none
"""
    assert sc.check_slices(sc.parse_slices(plan), ["AC-1", "AC-2"]) == [
        "S1: unknown criterion AC-9",
        "S1: ~900 lines is over the 300 line review budget; split it",
        "S1: depends on S2, which is not an earlier slice",
        "S2: covers no acceptance criterion",
        "S2: no size estimate",
        "AC-2: not covered by any slice",
    ]


def test_empty_plan():
    assert sc.check_slices([], ["AC-1"]) == ["no slices"]
