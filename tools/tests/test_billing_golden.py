"""Lab s08 (Lecture 8.3): 50 recorded invoice cases pin the legacy batch's output."""

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import billing_golden as bg  # noqa: E402


def test_cases_cover_what_the_export_depends_on():
    rows = bg.cases()
    assert [r["order_id"] for r in rows] == list(range(1, 51))
    assert rows == bg.cases(), "cases must be deterministic"
    countries = Counter(r["country"] for r in rows)
    assert all(countries[c] >= 2 for c in bg.LEGACY_RATES)
    assert len([c for c in countries if c not in bg.LEGACY_RATES]) >= 2
    for c in ("JP", "AU", "IN", "NG"):
        assert any(r["country"] == c and r["total_minor"] * bg.LEGACY_RATES[c] % 10000 == 5000 for r in rows), c
    totals = {r["total_minor"] for r in rows}
    assert 0 in totals and 99_999_999 in totals
    assert all(r["subtotal_minor"] >= r["total_minor"] >= 0 and r["currency"] == "USD" for r in rows)
    names = [r["customer_name"] for r in rows]
    assert any(len(n) > 30 for n in names)
    assert any(any(127 < ord(ch) < 256 for ch in n) for n in names)
    assert any(any(ord(ch) > 255 for ch in n) for n in names)
    assert not any("," in n for n in names)


def test_recorded_input_matches_cases():
    recorded = (bg.GOLDEN / f"orders_{bg.STAMP}.csv").read_text(encoding="utf-8")
    assert recorded == bg.handoff_csv(bg.cases())


def test_legacy_output_is_unchanged():
    assert bg.check() == 0
