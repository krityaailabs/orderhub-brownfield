"""Order operations: place, read, list, cancel, and the nightly billing handoff."""

import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import pricing
from .errors import Conflict, NotFound, ValidationFailed
from .models import Customer, DiscountCode, Order, OrderLine, Product

VALID_STATUSES = {"PLACED", "SHIPPED", "CANCELLED"}
RETURN_WINDOW = timedelta(days=30)


def place_order(session: Session, customer_id: int, items: list[dict], currency: str,
                discount_code: str | None = None) -> Order:
    """items: [{"sku": str, "quantity": int}, ...]"""
    if not items:
        raise ValidationFailed("an order needs at least one item")
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise NotFound(f"customer {customer_id} not found")

    lines: list[OrderLine] = []
    for item in items:
        product = session.scalar(select(Product).where(Product.sku == item["sku"].strip().upper()))
        if product is None or not product.active:
            raise ValidationFailed(f"unknown product {item['sku']}")
        qty = int(item["quantity"])
        if qty < 1:
            raise ValidationFailed("quantity must be at least 1")
        if product.stock < qty:
            raise Conflict(f"not enough stock for {product.sku}")
        product.stock -= qty
        lines.append(OrderLine(product_id=product.id, quantity=qty, unit_price_minor=product.unit_price_minor))

    sub = pricing.subtotal([(line.unit_price_minor, line.quantity) for line in lines])
    total = sub
    code = None
    if discount_code:
        dc = session.get(DiscountCode, discount_code.strip().upper())
        if dc is None or not dc.active:
            raise ValidationFailed("discount code is not valid")
        total = pricing.apply_percentage_discount(sub, dc.percent)
        code = dc.code

    order = Order(customer_id=customer.id, currency=currency, subtotal_minor=sub,
                  discount_code=code, total_minor=total, lines=lines)
    session.add(order)
    session.commit()
    return order


def get_order(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise NotFound(f"order {order_id} not found")
    return order


def list_orders(session: Session, status: str | None = None, limit: int = 50) -> list[dict]:
    query = select(Order).order_by(Order.id)
    if status:
        query = query.where(Order.status == status)
    result = []
    for order in session.scalars(query.limit(limit)):
        # Each access below loads lazily: one query for the customer and one for the lines, per order.
        result.append({
            "id": order.id,
            "customer_email": order.customer.email,
            "status": order.status,
            "total_minor": order.total_minor,
            "line_count": len(order.lines),
        })
    return result


def cancel_order(session: Session, order_id: int) -> Order:
    order = get_order(session, order_id)
    if order.status == "SHIPPED":
        raise Conflict("shipped orders cannot be cancelled")
    for line in order.lines:
        product = session.get(Product, line.product_id)
        product.stock += line.quantity
    order.status = "CANCELLED"
    session.commit()
    return order


def ship_order(session: Session, order_id: int) -> Order:
    """Mark a PLACED order as SHIPPED. Shipping a SHIPPED or CANCELLED order is a Conflict.
    Spec: docs/specs/returns.md, slice S1."""
    raise NotImplementedError("Lab s04: implement ship_order")


def _as_utc(moment: datetime) -> datetime:
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def return_items(session: Session, order_id: int, items: list[dict], now: datetime | None = None) -> int:
    """Return units of a SHIPPED order and record the refund. Returns the refund in minor units.

    items: [{"sku": str, "quantity": int}, ...]
    Rules (docs/specs/returns.md):
      AC-6: order must be SHIPPED, otherwise Conflict.
      AC-4: allowed only while now < created_at + 30 days, otherwise ValidationFailed("return window closed").
      AC-5: quantity must be 1..(bought - already returned) for each sku, otherwise ValidationFailed;
            on any validation error nothing changes.
      AC-1, AC-2: refund per item = pricing.refund_for_units for the returned units.
      AC-3: if this return makes every unit of the order returned, the refund is the remainder
            (total_minor - refunded_minor) so that refunds sum to the total exactly.
      AC-7: returned units go back into stock.
    Updates line.returned_quantity and order.refunded_minor, then commits.
    """
    raise NotImplementedError("Lab s04: implement return_items")


def write_billing_handoff(session: Session, business_date: date, out_dir: str) -> Path:
    """Write the CSV file that the legacy billing batch reads at 02:00.

    Format agreed with the billing team in 2018. Do not change the column order.
    """
    path = Path(out_dir) / f"orders_{business_date:%Y%m%d}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = session.scalars(select(Order).where(Order.status != "CANCELLED").order_by(Order.id))
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["order_id", "customer_name", "country", "currency", "subtotal_minor", "total_minor"])
        for order in rows:
            if order.created_at.date() != business_date:
                continue
            writer.writerow([order.id, order.customer.name, order.customer.country, order.currency,
                             order.subtotal_minor, order.total_minor])
    return path
