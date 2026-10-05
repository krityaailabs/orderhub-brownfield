"""Ledger guards for loyalty points (capstone S3)."""

import pytest
from sqlalchemy.exc import IntegrityError

from orderhub import loyalty, orders


def test_database_rejects_a_second_earn_entry_for_the_same_order(session):
    order = orders.place_order(session, 2, [{"sku": "MUG-350", "quantity": 1}], "USD")
    orders.ship_order(session, order.id)
    loyalty.credit_shipment(session, order)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
    assert loyalty.balance(session, 2) == loyalty.points_for(order.total_minor)


@pytest.mark.parametrize("total,points", [(0, 0), (99, 0), (100, 1), (1299, 12), (8190, 81)])
def test_points_for_is_one_per_full_100_minor_units(total, points):
    assert loyalty.points_for(total) == points
