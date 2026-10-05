"""Property tests for loyalty clawback (capstone S2). Reuses the order strategies from Lab 4.5."""

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import select
from test_returns_properties import CODES, fresh_session, lines_strategy, place_and_ship

from orderhub import loyalty, orders
from orderhub.models import LoyaltyEntry


def order_points(session, order_id):
    return [e.points for e in session.scalars(select(LoyaltyEntry).where(LoyaltyEntry.order_id == order_id))]


@settings(max_examples=60, deadline=None)
@given(lines=lines_strategy, code=st.sampled_from(CODES), data=st.data())
def test_any_full_return_sequence_removes_exactly_the_earned_points(lines, code, data):
    session = fresh_session()
    order = place_and_ship(session, lines, code)
    units = [sku for sku, qty in lines for _ in range(qty)]
    for sku in data.draw(st.permutations(units)):
        orders.return_items(session, order.id, [{"sku": sku, "quantity": 1}])
    assert sum(order_points(session, order.id)) == 0


@settings(max_examples=60, deadline=None)
@given(lines=lines_strategy, code=st.sampled_from(CODES), data=st.data())
def test_points_from_an_order_never_go_negative_or_above_what_was_earned(lines, code, data):
    session = fresh_session()
    order = place_and_ship(session, lines, code)
    earned = loyalty.points_for(order.total_minor)
    units = [sku for sku, qty in lines for _ in range(qty)]
    count = data.draw(st.integers(1, len(units)))
    for sku in data.draw(st.permutations(units))[:count]:
        orders.return_items(session, order.id, [{"sku": sku, "quantity": 1}])
        remaining = sum(order_points(session, order.id))
        assert 0 <= remaining <= earned
