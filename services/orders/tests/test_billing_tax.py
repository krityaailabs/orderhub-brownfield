"""Lab s08 (Project 2): the new tax path matches the legacy calculation exactly."""

import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from orderhub import billing_tax, orders


@pytest.mark.parametrize("net,country,tax", [
    (1000, "GB", 200), (1000, "ZZ", 0), (0, "IT", 0), (12345, "IT", 2716),
    (1005, "JP", 100),   # 100.5 -> 100 (half to even)
    (1015, "JP", 102),   # 101.5 -> 102 (half to even)
    (1006, "AU", 101),   # 100.6 -> 101
    (25, "IN", 4),       # 4.5 -> 4
    (75, "IN", 14),      # 13.5 -> 14
    (20, "NG", 2),       # 1.5 -> 2
    (60, "NG", 4),       # 4.5 -> 4
    (99_999_999, "IT", 22_000_000),
])
def test_tax_matches_the_legacy_rule(net, country, tax):
    assert billing_tax.tax_minor(net, country) == tax


def test_integer_arithmetic_for_large_amounts():
    # A float-based version gets this wrong: 9007199254740993 isn't representable as a float.
    assert billing_tax.tax_minor(9_007_199_254_740_993, "GB") == 1_801_439_850_948_199


def test_negative_net_is_rejected():
    with pytest.raises(ValueError):
        billing_tax.tax_minor(-1, "GB")


def test_rates_match_the_legacy_source():
    java = (Path(__file__).resolve().parents[3] / "legacy/billing/src/com/orderhub/billing/InvoiceCalculator.java")
    legacy = {c: int(r) for c, r in re.findall(r'RATES\.put\("([A-Z]{2})", (\d+)\)', java.read_text())}
    assert legacy == billing_tax.RATES_BP


def test_tax_side_file_covers_the_same_orders_as_the_handoff(session, tmp_path):
    a = orders.place_order(session, 1, [{"sku": "MUG-350", "quantity": 1}], "USD")
    b = orders.place_order(session, 2, [{"sku": "NB-A5", "quantity": 2}], "USD")
    orders.cancel_order(session, b.id)
    today = datetime.now(timezone.utc).date()
    handoff = orders.write_billing_handoff(session, today, str(tmp_path)).read_text().splitlines()
    tax = billing_tax.write_tax_handoff(session, today, str(tmp_path)).read_text().splitlines()
    assert tax[0] == "order_id,tax_minor"
    assert [r.split(",")[0] for r in tax[1:]] == [r.split(",")[0] for r in handoff[1:]] == [str(a.id)]
