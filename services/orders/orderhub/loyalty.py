"""Loyalty points, earn only (docs/specs/loyalty.md, issue Q20).

Points live in an append-only ledger (LoyaltyEntry). Earning happens when an order ships;
clawback happens when units are returned. Both are added to the caller's session and committed
in the same transaction as the ship or return that causes them. Integers only (ADR 0001).
Redemption is a non-goal: it changes totals, tax and the billing file, and needs finance.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import LoyaltyEntry, Order

MINOR_UNITS_PER_POINT = 100


def points_for(total_minor: int) -> int:
    """One point per full 100 minor units of the order total (after discount)."""
    return max(total_minor, 0) // MINOR_UNITS_PER_POINT


def credit_shipment(session: Session, order: Order) -> LoyaltyEntry:
    """Add the earn entry for a newly shipped order. The caller commits (ship_order).

    Called once per order: ship_order only ships PLACED orders, and a unique index on earn entries
    per order backs that up at the database level (AC-2)."""
    entry = LoyaltyEntry(customer_id=order.customer_id, order_id=order.id, kind="earn",
                         points=points_for(order.total_minor))
    session.add(entry)
    return entry


def balance(session: Session, customer_id: int) -> int:
    """Sum of the customer's ledger entries (0 if none)."""
    total = session.scalar(select(func.coalesce(func.sum(LoyaltyEntry.points), 0))
                           .where(LoyaltyEntry.customer_id == customer_id))
    return int(total)


def entries(session: Session, customer_id: int) -> list[LoyaltyEntry]:
    """The customer's ledger, newest first (ties broken by id, newest first)."""
    query = (select(LoyaltyEntry).where(LoyaltyEntry.customer_id == customer_id)
             .order_by(LoyaltyEntry.created_at.desc(), LoyaltyEntry.id.desc()))
    return list(session.scalars(query))


def claw_back(session: Session, order: Order, refunded_before_minor: int) -> LoyaltyEntry | None:
    """Add the clawback entry for a return. The caller commits (return_items), after updating
    order.refunded_minor to include this return.

    Cumulative and proportional (AC-4, AC-5): after this return, the points removed for the order
    in total are floor(earned * refunded_total / order_total). This entry is the difference from
    what was removed before. A full return (refunded_total == order_total) therefore removes
    exactly what was earned, whatever the sequence of returns. No entry if nothing changes."""
    earned = points_for(order.total_minor)
    if earned == 0 or order.total_minor == 0:
        return None
    removed_before = earned * refunded_before_minor // order.total_minor
    removed_after = earned * order.refunded_minor // order.total_minor
    if removed_after == removed_before:
        return None
    entry = LoyaltyEntry(customer_id=order.customer_id, order_id=order.id, kind="clawback",
                         points=-(removed_after - removed_before))
    session.add(entry)
    return entry
