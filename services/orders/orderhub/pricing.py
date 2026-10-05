"""Pricing rules.

Business rules (from the finance team's pricing note, 2023):
  * Line total = unit price x quantity, in minor units.
  * A discount code takes a whole percentage off the order subtotal.
  * The discount amount is rounded half-up to the nearest minor unit,
    and the total is subtotal minus the rounded discount.
"""


def line_total(unit_price_minor: int, quantity: int) -> int:
    if quantity < 1:
        raise ValueError("quantity must be at least 1")
    return unit_price_minor * quantity


def subtotal(lines: list[tuple[int, int]]) -> int:
    """lines: (unit_price_minor, quantity) pairs."""
    return sum(line_total(price, qty) for price, qty in lines)


def apply_percentage_discount(amount_minor: int, percent: int) -> int:
    """Return the total after taking `percent` off `amount_minor`."""
    if not 0 <= percent <= 90:
        raise ValueError("percent must be between 0 and 90")
    if amount_minor < 0:
        raise ValueError("amount must not be negative")
    # Integer arithmetic only: round the discount half-up, then subtract it.
    discount = (amount_minor * percent + 50) // 100
    return amount_minor - discount


def format_money(amount_minor: int, currency: str) -> str:
    """Format minor units for display, for example 1999 USD -> '19.99 USD'."""
    sign = "-" if amount_minor < 0 else ""
    amount_minor = abs(amount_minor)
    return f"{sign}{amount_minor // 100}.{amount_minor % 100:02d} {currency}"


def refund_for_units(unit_price_minor: int, quantity: int, subtotal_minor: int, total_minor: int) -> int:
    """Refund for returning `quantity` units of a line, before the remainder rule.

    The order-level discount (subtotal - total) is shared across lines in proportion to their value.
    The returned units' share is rounded half-up to the minor unit and subtracted from their value:
        value = unit_price_minor * quantity
        share = round_half_up(discount * value / subtotal)
        refund = value - share
    Spec: docs/specs/returns.md, AC-2. The final return of an order uses the remainder rule instead
    (see orders.return_items, AC-3).
    """
    raise NotImplementedError("Lab s04: implement refund_for_units")
