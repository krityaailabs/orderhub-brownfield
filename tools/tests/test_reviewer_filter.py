"""Lab s09 (Lecture 9.4): the repository's reviewer filter meets the signal target."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "agent_pipeline"))

import reviewer_filter as rf  # noqa: E402


def test_filter_rules():
    comments = [{"severity": "nit", "category": "style", "file": "a.py", "text": "x"},
                {"severity": "high", "category": "security", "file": "a.py", "text": "Bound parameter"},
                {"severity": "high", "category": "security", "file": "a.py", "text": "bound parameter "},
                {"severity": "medium", "category": "style", "file": "t/test_a.py", "text": "y"}]
    kept = rf.keep(comments, {"min_severity": "low", "dedupe": True, "ignore_paths": ["t/*"]})
    assert kept == [comments[1]]


def test_repository_config_meets_the_target():
    prs = json.loads(rf.COMMENTS.read_text())["prs"]
    m = rf.metrics(prs, json.loads(rf.CONFIG.read_text()))
    assert m["actionable_dropped"] == 0, m
    assert m["non_actionable_per_pr"] < 1, m
