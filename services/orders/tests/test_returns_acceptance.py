"""Acceptance tests for the returns spec (docs/specs/returns.md). Owned by the team, written
before the implementation. Do not edit these to make code pass; change the spec first."""

from datetime import datetime, timedelta, timezone

from orderhub import orders
from orderhub.models import Order, Product


def shipped_order(client, items, code=None):
    body = {"customer_id": 3, "items": items}
    if code:
        body["discount_code"] = code
    order = client.post("/orders", json=body).json()
    assert client.post(f"/orders/{order['id']}/ship").status_code == 200
    return order


def ret(client, order_id, items):
    return client.post(f"/orders/{order_id}/returns", json={"items": items})


def test_ac1_return_one_unit_without_discount(client):
    order = shipped_order(client, [{"sku": "MUG-350", "quantity": 2}])
    r = ret(client, order["id"], [{"sku": "MUG-350", "quantity": 1}])
    assert r.status_code == 201
    assert r.json()["refund_minor"] == 1250


def test_ac2_discount_share_is_allocated_by_value(client):
    order = shipped_order(client, [{"sku": "STAND-LAP", "quantity": 2}], code="SAVE10")
    assert (order["subtotal_minor"], order["total_minor"]) == (9100, 8190)
    assert ret(client, order["id"], [{"sku": "STAND-LAP", "quantity": 1}]).json()["refund_minor"] == 4095


def test_ac3_refunds_sum_to_the_total_exactly(client):
    order = shipped_order(client, [{"sku": "PEN-GEL-BLK", "quantity": 2}, {"sku": "MUG-350", "quantity": 1}],
                          code="WELCOME15")
    assert order["total_minor"] == 1486
    refunds = [ret(client, order["id"], [{"sku": sku, "quantity": 1}]).json()["refund_minor"]
               for sku in ("PEN-GEL-BLK", "MUG-350", "PEN-GEL-BLK")]
    assert refunds == [212, 1063, 211]
    assert sum(refunds) == 1486


def test_ac4_return_window_closes_after_30_days(client, session):
    order = shipped_order(client, [{"sku": "MUG-350", "quantity": 1}])
    db_order = session.get(Order, order["id"])
    db_order.created_at = datetime.now(timezone.utc) - timedelta(days=30, seconds=1)
    session.commit()
    r = ret(client, order["id"], [{"sku": "MUG-350", "quantity": 1}])
    assert r.status_code == 422
    assert "return window closed" in r.json()["error"]


def test_ac4_return_allowed_just_inside_the_window(client, session):
    order = shipped_order(client, [{"sku": "MUG-350", "quantity": 1}])
    db_order = session.get(Order, order["id"])
    db_order.created_at = datetime.now(timezone.utc) - timedelta(days=29, hours=23)
    session.commit()
    assert ret(client, order["id"], [{"sku": "MUG-350", "quantity": 1}]).status_code == 201


def test_ac5_cannot_return_more_than_remains_and_nothing_changes(client, session):
    order = shipped_order(client, [{"sku": "MUG-350", "quantity": 2}])
    assert ret(client, order["id"], [{"sku": "MUG-350", "quantity": 1}]).status_code == 201
    session.expire_all()
    stock_before = session.get(Product, 4).stock
    r = ret(client, order["id"], [{"sku": "MUG-350", "quantity": 2}])
    assert r.status_code == 422
    session.expire_all()
    assert session.get(Product, 4).stock == stock_before
    assert session.get(Order, order["id"]).refunded_minor == 1250


def test_ac6_placed_and_cancelled_orders_cannot_be_returned(client):
    placed = client.post("/orders", json={"customer_id": 3, "items": [{"sku": "MUG-350", "quantity": 1}]}).json()
    assert ret(client, placed["id"], [{"sku": "MUG-350", "quantity": 1}]).status_code == 409
    client.post(f"/orders/{placed['id']}/cancel")
    assert ret(client, placed["id"], [{"sku": "MUG-350", "quantity": 1}]).status_code == 409


def test_ac6_only_placed_orders_can_be_shipped(client):
    order = shipped_order(client, [{"sku": "MUG-350", "quantity": 1}])
    assert client.post(f"/orders/{order['id']}/ship").status_code == 409


def test_ac7_returned_units_are_restocked(client, session):
    order = shipped_order(client, [{"sku": "DESK-LAMP", "quantity": 2}])
    session.expire_all()
    before = session.get(Product, 3).stock
    ret(client, order["id"], [{"sku": "DESK-LAMP", "quantity": 1}])
    session.expire_all()
    assert session.get(Product, 3).stock == before + 1


def test_ac8_billing_handoff_columns_are_unchanged_after_returns(client, session, tmp_path):
    order = shipped_order(client, [{"sku": "MUG-350", "quantity": 2}])
    ret(client, order["id"], [{"sku": "MUG-350", "quantity": 1}])
    path = orders.write_billing_handoff(session, datetime.now(timezone.utc).date(), str(tmp_path))
    header, row = path.read_text(encoding="utf-8").splitlines()[:2]
    assert header == "order_id,customer_name,country,currency,subtotal_minor,total_minor"
    fields = row.split(",")
    assert len(fields) == 6 and fields[0] == str(order["id"]) and fields[3] == "USD"
