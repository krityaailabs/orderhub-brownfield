"""Lab s07 (Lecture 7.2): the repository's own agent permission profile meets the policy."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from permission_check import check  # noqa: E402


def test_repository_profile_meets_the_policy():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
    problems, _ = check(settings)
    assert problems == []


def test_profile_keeps_the_after_edit_hook():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
    commands = [h["command"] for entry in settings["hooks"]["PostToolUse"] for h in entry["hooks"]]
    assert "python3 tools/hooks/agent_after_edit.py" in commands
