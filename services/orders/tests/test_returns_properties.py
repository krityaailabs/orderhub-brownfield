"""Property-based tests for refunds (Lab 4.5). Hypothesis generates orders and return sequences;
the properties must hold for all of them, not just the examples in the spec."""

from hypothesis import given, settings
from hypothesis import strategies as st

from orderhub import orders, pricing, seed
from orderhub.db import Base, make_engine, make_session_factory

SKUS = ["NB-A5", "PEN-GEL-BLK", "DESK-LAMP", "MUG-350", "BAG-TOTE", "CABLE-USBC", "STAND-LAP"]
CODES = [None, "SAVE10", "WELCOME15", "STAFF30"]

lines_strategy = st.lists(
    st.tuples(st.sampled_from(SKUS), st.integers(1, 4)), min_size=1, max_size=4, unique_by=lambda t: t[0]
)


def fresh_session():
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = make_session_factory(engine)()
    seed.load(session)
    return session


def place_and_ship(session, lines, code):
    order = orders.place_order(session, 1, [{"sku": s, "quantity": q} for s, q in lines], "USD", code)
    orders.ship_order(session, order.id)
    return order


@settings(max_examples=60, deadline=None)
@given(lines=lines_strategy, code=st.sampled_from(CODES), data=st.data())
def test_refunds_of_a_fully_returned_order_sum_to_its_total(lines, code, data) -> None:
    session = fresh_session()
    order = place_and_ship(session, lines, code)
    units = [sku for sku, qty in lines for _ in range(qty)]
    order_of_returns = data.draw(st.permutations(units))
    refunds = [orders.return_items(session, order.id, [{"sku": sku, "quantity": 1}]) for sku in order_of_returns]
    assert sum(refunds) == order.total_minor


@settings(max_examples=60, deadline=None)
@given(lines=lines_strategy, code=st.sampled_from(CODES), data=st.data())
def test_every_refund_is_non_negative_and_never_exceeds_what_is_left(lines, code, data) -> None:
    session = fresh_session()
    order = place_and_ship(session, lines, code)
    units = [sku for sku, qty in lines for _ in range(qty)]
    count = data.draw(st.integers(1, len(units)))
    refunded = 0
    for sku in data.draw(st.permutations(units))[:count]:
        refund = orders.return_items(session, order.id, [{"sku": sku, "quantity": 1}])
        assert refund >= 0
        refunded += refund
        assert refunded <= order.total_minor


@given(price=st.integers(1, 100_000), qty=st.integers(1, 20))
def test_without_a_discount_the_refund_is_the_full_value(price, qty) -> None:
    subtotal = price * qty * 2
    assert pricing.refund_for_units(price, qty, subtotal, subtotal) == price * qty
