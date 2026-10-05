from pathlib import Path

DOC = Path(__file__).resolve().parents[3] / "legacy" / "billing" / "docs" / "RECORD_LAYOUT.txt"


def test_t4_layout_document_matches_the_code():
    text = DOC.read_text()
    for line in ("pos 47-57", "pos 58-68", "pos 69-79"):
        assert line in text
    assert "pos 47-56" not in text and "80" in text
