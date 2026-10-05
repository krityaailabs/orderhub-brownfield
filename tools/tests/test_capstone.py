"""Capstone (Section 15): every deliverable is present and meets the brief."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import capstone_check  # noqa: E402


def test_capstone_deliverables(capsys):
    result = capstone_check.main([])
    assert result == 0, capsys.readouterr().out
