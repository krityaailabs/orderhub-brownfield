"""Property-based tests for refunds (Lab 4.5). Hypothesis generates orders and return sequences;
the properties must hold for all of them, not just the examples in the spec."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from orderhub import orders, pricing, seed
from orderhub.db import Base, make_engine, make_session_factory

SKUS = ["NB-A5", "PEN-GEL-BLK", "DESK-LAMP", "MUG-350", "BAG-TOTE", "CABLE-USBC", "STAND-LAP"]
CODES = [None, "SAVE10", "WELCOME15", "STAFF30"]

lines_strategy = st.lists(st.tuples(st.sampled_from(SKUS), st.integers(1, 4)), min_size=1, max_size=4,
                          unique_by=lambda t: t[0])


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
def test_refunds_of_a_fully_returned_order_sum_to_its_total(lines, code, data):
    # Lab 4.5: place and ship an order from the generated lines, return every unit one at a time
    # in the drawn order, and assert the refunds sum to the order total.
    pytest.fail("Lab 4.5: write this property-based test")


@settings(max_examples=60, deadline=None)
@given(lines=lines_strategy, code=st.sampled_from(CODES), data=st.data())
def test_every_refund_is_non_negative_and_never_exceeds_what_is_left(lines, code, data):
    # Lab 4.5: return a drawn number of units in a drawn order; assert each refund >= 0 and the
    # running total never exceeds the order total.
    pytest.fail("Lab 4.5: write this property-based test")


@given(price=st.integers(1, 100_000), qty=st.integers(1, 20))
def test_without_a_discount_the_refund_is_the_full_value(price, qty):
    subtotal = price * qty * 2
    assert pricing.refund_for_units(price, qty, subtotal, subtotal) == price * qty
