"""HTTP API (FastAPI)."""

from fastapi import Depends, FastAPI, Header, Query, Request
from fastapi.responses import JSONResponse

from . import customers, idempotency, loyalty, notify, orders, pricing
from .config import Settings, load_settings
from .db import Base, make_engine, make_session_factory
from .errors import OrderHubError
from .schemas import (
    CustomerIn,
    CustomerOut,
    CustomerPatch,
    LineOut,
    LoyaltyEntryOut,
    OrderIn,
    OrderOut,
    PointsOut,
    ReturnIn,
    ReturnOut,
)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    engine = make_engine(settings.database_url)
    Base.metadata.create_all(engine)
    SessionLocal = make_session_factory(engine)

    app = FastAPI(title="OrderHub", version="2.7.3")
    app.state.settings = settings
    app.state.session_factory = SessionLocal

    def get_session():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    @app.exception_handler(OrderHubError)
    async def domain_error(_: Request, exc: OrderHubError):
        return JSONResponse(status_code=exc.status_code, content={"error": str(exc)})

    def order_out(order) -> OrderOut:
        return OrderOut(
            id=order.id, customer_id=order.customer_id, status=order.status, currency=order.currency,
            subtotal_minor=order.subtotal_minor, discount_code=order.discount_code,
            total_minor=order.total_minor,
            total_display=pricing.format_money(order.total_minor, order.currency),
            lines=[LineOut(product_id=line.product_id, quantity=line.quantity,
                           unit_price_minor=line.unit_price_minor) for line in order.lines],
        )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/customers", status_code=201, response_model=CustomerOut)
    def create_customer(body: CustomerIn, session=Depends(get_session)):
        c = customers.create_customer(session, body.email, body.name, body.country)
        return CustomerOut(id=c.id, email=c.email, name=c.name, country=c.country)

    @app.patch("/customers/{customer_id}", response_model=CustomerOut)
    def update_customer(customer_id: int, body: CustomerPatch, session=Depends(get_session)):
        c = customers.update_customer(session, customer_id, name=body.name)
        return CustomerOut(id=c.id, email=c.email, name=c.name, country=c.country)

    @app.get("/customers/{customer_id}/points", response_model=PointsOut)
    def customer_points(customer_id: int, session=Depends(get_session)):
        customers.get_customer(session, customer_id)  # 404 for an unknown customer (loyalty AC-6)
        ledger = [LoyaltyEntryOut(kind=e.kind, order_id=e.order_id, points=e.points, created_at=e.created_at)
                  for e in loyalty.entries(session, customer_id)]
        return PointsOut(customer_id=customer_id, balance=loyalty.balance(session, customer_id), entries=ledger)

    @app.post("/orders", status_code=201, response_model=OrderOut)
    def place_order(body: OrderIn, session=Depends(get_session)):
        order = orders.place_order(session, body.customer_id, [i.model_dump() for i in body.items],
                                   settings.currency, body.discount_code)
        return order_out(order)

    @app.get("/orders/{order_id}", response_model=OrderOut)
    def get_order(order_id: int, session=Depends(get_session)):
        return order_out(orders.get_order(session, order_id))

    @app.get("/orders")
    def list_orders(status: str | None = None, limit: int = Query(50, ge=1, le=200), session=Depends(get_session)):
        return orders.list_orders(session, status=status, limit=limit)

    app.state.notify_transport = None  # tests inject httpx.MockTransport here

    def notify_warehouse(body: dict) -> None:
        if settings.warehouse_webhook_url:
            lines = [{"product_id": line["product_id"], "quantity": line["quantity"]} for line in body["lines"]]
            notify.order_cancelled(settings.warehouse_webhook_url, body["id"], lines,
                                   transport=app.state.notify_transport, token=settings.warehouse_token)

    def cancel_and_notify(session, order_id: int) -> dict:
        already_cancelled = orders.get_order(session, order_id).status == "CANCELLED"
        body = order_out(orders.cancel_order(session, order_id)).model_dump()
        if not already_cancelled:
            notify_warehouse(body)
        return body

    @app.post("/orders/{order_id}/cancel", response_model=OrderOut)
    def cancel_order(order_id: int, session=Depends(get_session),
                     idempotency_key: str | None = Header(default=None)):
        if idempotency_key is None:
            return cancel_and_notify(session, order_id)
        fingerprint = idempotency.request_fingerprint("POST", f"/orders/{order_id}/cancel", None)
        stored = idempotency.lookup(session, idempotency_key, fingerprint)
        if stored is not None:
            return JSONResponse(status_code=stored[0], content=stored[1])
        body = cancel_and_notify(session, order_id)
        idempotency.record(session, idempotency_key, fingerprint, 200, body)
        return body

    @app.post("/orders/{order_id}/ship", response_model=OrderOut)
    def ship_order(order_id: int, session=Depends(get_session)):
        return order_out(orders.ship_order(session, order_id))

    @app.post("/orders/{order_id}/returns", status_code=201, response_model=ReturnOut)
    def return_items(order_id: int, body: ReturnIn, session=Depends(get_session)):
        refund = orders.return_items(session, order_id, [i.model_dump() for i in body.items])
        order = orders.get_order(session, order_id)
        return ReturnOut(order_id=order_id, refund_minor=refund, refunded_total_minor=order.refunded_minor)

    return app


app = create_app()
