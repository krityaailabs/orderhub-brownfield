"""New path for the billing tax calculation (Section 8, Project 2: strangler).

The legacy batch (legacy/billing, InvoiceCalculator.java) calculates tax on each order's total.
This module moves that calculation into the order service, one country at a time. It writes a
side file next to the nightly handoff, `tax_YYYYMMDD.csv` (order_id,tax_minor). The orders CSV
itself is unchanged (returns AC-8; legacy/billing/AGENTS.md). The batch uses the side file only
for the countries listed in BILLING_NEW_TAX_COUNTRIES; everything else stays on the legacy path.

Contract with the legacy calculation (pinned by legacy/billing/test/golden and
tools/billing_compare.py): same rates, same rounding (HALF_EVEN on the net amount), same result
for every order. Integer arithmetic only (ADR 0001).
"""

import csv
from datetime import date
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Order

# Basis points. Must match InvoiceCalculator.RATES (legacy/billing); unknown countries pay no tax.
RATES_BP = {"GB": 2000, "FR": 2000, "IT": 2200, "IN": 1800, "AE": 500, "AU": 1000, "JP": 1000, "NG": 750}


def tax_minor(net_minor: int, country: str) -> int:
    """Tax in minor units on a net amount, exactly as the legacy batch calculates it.

    tax = net_minor * rate_bp / 10000, rounded to a whole minor unit with HALF_EVEN
    (a remainder of exactly one half rounds to the even neighbour: 100.5 -> 100, 101.5 -> 102).
    Unknown countries have rate 0. Use integer arithmetic only (divmod), never floats.
    Raise ValueError for a negative net_minor (the legacy batch never receives one)."""
    if net_minor < 0:
        raise ValueError("net_minor must not be negative")
    quotient, remainder = divmod(net_minor * RATES_BP.get(country, 0), 10000)
    if 2 * remainder > 10000 or (2 * remainder == 10000 and quotient % 2 == 1):
        quotient += 1
    return quotient


def write_tax_handoff(session: Session, business_date: date, out_dir: str) -> Path:
    """Write tax_YYYYMMDD.csv (order_id,tax_minor) for the same orders as write_billing_handoff."""
    path = Path(out_dir) / f"tax_{business_date:%Y%m%d}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = session.scalars(select(Order).where(Order.status != "CANCELLED").order_by(Order.id))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["order_id", "tax_minor"])
        for order in rows:
            if order.created_at.date() != business_date:
                continue
            writer.writerow([order.id, tax_minor(order.total_minor, order.customer.country)])
    return path
