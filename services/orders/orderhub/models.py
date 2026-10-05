"""ORM models.

Money is stored as integer minor units (cents, paise) in the order tables.
Older code paths (see pricing.py) still do some arithmetic in floats.
"""

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(2))
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    unit_price_minor: Mapped[int]
    stock: Mapped[int]
    active: Mapped[bool] = mapped_column(default=True)


class DiscountCode(Base):
    __tablename__ = "discount_codes"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    percent: Mapped[int]  # whole percent, 1..90
    active: Mapped[bool] = mapped_column(default=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    status: Mapped[str] = mapped_column(String(16), default="PLACED")
    currency: Mapped[str] = mapped_column(String(3))
    subtotal_minor: Mapped[int]
    discount_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    total_minor: Mapped[int]
    refunded_minor: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    customer: Mapped[Customer] = relationship(back_populates="orders")
    lines: Mapped[list["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderLine(Base):
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    unit_price_minor: Mapped[int]
    returned_quantity: Mapped[int] = mapped_column(default=0)

    order: Mapped[Order] = relationship(back_populates="lines")
    product: Mapped[Product] = relationship()


class IdempotencyRecord(Base):
    """Stored outcome of a request made with an Idempotency-Key header."""

    __tablename__ = "idempotency_records"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    status_code: Mapped[int]
    response_json: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
