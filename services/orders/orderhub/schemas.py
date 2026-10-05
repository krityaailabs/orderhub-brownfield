"""Request and response models for the HTTP API."""

from pydantic import BaseModel, Field


class CustomerIn(BaseModel):
    email: str
    name: str
    country: str = Field(min_length=2, max_length=2)


class CustomerPatch(BaseModel):
    name: str | None = None
    email: str | None = None


class CustomerOut(BaseModel):
    id: int
    email: str
    name: str
    country: str


class ItemIn(BaseModel):
    sku: str
    quantity: int = Field(ge=1)


class OrderIn(BaseModel):
    customer_id: int
    items: list[ItemIn]
    discount_code: str | None = None


class LineOut(BaseModel):
    product_id: int
    quantity: int
    unit_price_minor: int


class OrderOut(BaseModel):
    id: int
    customer_id: int
    status: str
    currency: str
    subtotal_minor: int
    discount_code: str | None
    total_minor: int
    total_display: str
    lines: list[LineOut]


class ReturnIn(BaseModel):
    items: list[ItemIn]


class ReturnOut(BaseModel):
    order_id: int
    refund_minor: int
    refunded_total_minor: int
