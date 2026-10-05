"""HTTP API (FastAPI)."""

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from . import customers, orders, pricing
from .config import Settings, load_settings
from .db import Base, make_engine, make_session_factory
from .errors import OrderHubError
from .schemas import CustomerIn, CustomerOut, LineOut, OrderIn, OrderOut


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

    @app.post("/orders", status_code=201, response_model=OrderOut)
    def place_order(body: OrderIn, session=Depends(get_session)):
        order = orders.place_order(session, body.customer_id, [i.model_dump() for i in body.items],
                                   settings.currency, body.discount_code)
        return order_out(order)

    @app.get("/orders/{order_id}", response_model=OrderOut)
    def get_order(order_id: int, session=Depends(get_session)):
        return order_out(orders.get_order(session, order_id))

    @app.get("/orders")
    def list_orders(status: str | None = None, limit: int = 50, session=Depends(get_session)):
        return orders.list_orders(session, status=status, limit=min(limit, 200))

    @app.post("/orders/{order_id}/cancel", response_model=OrderOut)
    def cancel_order(order_id: int, session=Depends(get_session)):
        return order_out(orders.cancel_order(session, order_id))

    return app


app = create_app()
