"""Lab s09 (Lectures 9.5 and 9.6): deduplication and the dependency-bump choice."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_pipeline.dedup import is_duplicate  # noqa: E402
from agent_pipeline.jobs.dep_bump import apply_bump, choose_bump, parse_version  # noqa: E402

PRS = [
    {"id": "PR-1", "issue": "Q21", "diff_hash": "aaa", "status": "rejected"},
    {"id": "PR-2", "issue": "Q22", "diff_hash": "bbb", "status": "awaiting-human"},
    {"id": "PR-3", "issue": "Q23", "diff_hash": "ccc", "status": "approved"},
    {"id": "PR-4", "issue": "Q24", "diff_hash": "ddd", "status": "merged"},
]


def test_open_pr_for_the_same_issue_is_a_duplicate():
    assert is_duplicate("Q22", "zzz", PRS) == "PR-2"
    assert is_duplicate("Q23", "", PRS) == "PR-3"


def test_same_change_from_another_issue_is_a_duplicate():
    assert is_duplicate("Q99", "bbb", PRS) == "PR-2"


def test_closed_prs_never_block_a_new_run():
    assert is_duplicate("Q21", "aaa", PRS) is None
    assert is_duplicate("Q24", "ddd", PRS) is None
    assert is_duplicate("Q30", "eee", []) is None


LOCK = "# pinned\nfastapi==0.142.2\npytest==9.1.1\nruff==0.16.10\nSQLAlchemy==2.1.3\nstarlette==1.7.0\n"
AVAILABLE = {"fastapi": ["0.142.2", "0.142.3", "0.143.0"], "pytest": ["9.2.0", "10.0.0rc1"],
             "ruff": ["0.16.9", "0.16.10", "0.16.11", "0.17.0"], "sqlalchemy": ["2.1.4", "2.1.5b1"],
             "starlette": ["1.7.1.post1"]}


def test_parse_version_accepts_plain_numbers_only():
    assert parse_version("0.16.10") == (0, 16, 10)
    assert [parse_version(v) for v in ("2.1.5b1", "10.0.0rc1", "2.9.0.post0", "1.0+local")] == [None] * 4


def test_first_patch_bump_in_file_order():
    assert choose_bump(LOCK, AVAILABLE) == ("fastapi", "0.142.2", "0.142.3")


def test_hold_minor_only_numeric_compare_and_names():
    assert choose_bump(LOCK, AVAILABLE, hold=["fastapi"]) == ("ruff", "0.16.10", "0.16.11")
    assert choose_bump(LOCK, AVAILABLE, hold=["fastapi", "ruff"]) == ("SQLAlchemy", "2.1.3", "2.1.4")
    assert choose_bump(LOCK, AVAILABLE, hold=["fastapi", "ruff", "sqlalchemy"]) is None


def test_apply_bump_changes_exactly_one_line():
    assert apply_bump(LOCK, "ruff", "0.16.11") == LOCK.replace("ruff==0.16.10", "ruff==0.16.11")
