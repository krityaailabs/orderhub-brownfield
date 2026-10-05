"""Lab s08 (Lecture 8.2): the module map for legacy/billing is complete."""

from pathlib import Path

MAP = Path(__file__).resolve().parents[2] / "docs" / "legacy" / "billing-map.md"
SECTIONS = ["## Entry points", "## Data flow", "## Side effects", "## Contracts", "## Unknowns and risks"]


def test_map_has_every_section_and_no_todos():
    text = MAP.read_text()
    for section in SECTIONS:
        assert section in text
    assert "TODO" not in text


def test_map_records_the_facts_a_change_would_break():
    text = MAP.read_text()
    for fact in ["NightlyBatch", "HandoffReader", "by position", "ISO-8859-1", "CRLF", "HALF_EVEN", "80",
                 "RECORD_LAYOUT.txt", "comma"]:
        assert fact in text, fact
