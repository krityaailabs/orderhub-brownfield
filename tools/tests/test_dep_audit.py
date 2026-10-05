import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dep_audit import audit  # noqa: E402

BASE = "# baseline\nfastapi\nhttpx\npytest\n"
DECISIONS = "| hypothesis 6.168.4 | Section 4 | ... |"


def test_baseline_only_lock_passes():
    assert audit("fastapi==1.0\nhttpx==0.28.1\npytest==9.1.1\n", BASE, DECISIONS) == []


def test_ranges_are_problems():
    assert audit("fastapi>=1.0\nhttpx==0.28.1\n", BASE, DECISIONS) == ["not pinned exactly: fastapi>=1.0"]


def test_new_package_needs_a_recorded_decision():
    assert audit("fastapi==1.0\nhypothesis==6.168.4\narrow==1.3.0\n", BASE, DECISIONS) == [
        "no decision recorded in docs/dependencies.md: arrow"]


def test_duplicate_http_client_is_a_problem_even_if_recorded():
    problems = audit("httpx==0.28.1\nrequests==2.32.5\n", BASE, DECISIONS + "\n| requests 2.32.5 | ... |")
    assert problems == ["duplicate HTTP client: requests added; already have httpx"]


def test_repository_lock_passes():
    root = Path(__file__).resolve().parents[2]
    assert audit((root / "requirements.lock").read_text(), (root / "tools/dep_baseline.txt").read_text(),
                 (root / "docs/dependencies.md").read_text()) == []
