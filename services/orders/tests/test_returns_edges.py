"""Edge cases added after mutation testing (Lab 4.6): each test kills a mutant that the
acceptance and property tests let survive."""

from datetime import timedelta

import pytest
from sqlalchemy.orm import Session

from orderhub import orders, pricing
from orderhub.errors import ValidationFailed


def test_discount_share_rounds_half_up_not_down() -> None:
    # NB-A5 (1001) + PEN-GEL-BLK (249), STAFF30: discount 375, total 875.
    # The pen's share is 375 * 249 / 1250 = 74.7, which rounds half-up to 75, so the refund is 174.
    assert pricing.refund_for_units(249, 1, 1250, 875) == 174


def test_return_exactly_30_days_after_the_order_is_rejected(session: Session) -> None:
    order = orders.place_order(session, 1, [{"sku": "MUG-350", "quantity": 1}], "USD")
    orders.ship_order(session, order.id)
    created = order.created_at
    with pytest.raises(ValidationFailed, match="return window closed"):
        orders.return_items(session, order.id, [{"sku": "MUG-350", "quantity": 1}], now=created + timedelta(days=30))
