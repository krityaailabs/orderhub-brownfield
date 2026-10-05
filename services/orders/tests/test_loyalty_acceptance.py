"""Acceptance tests for docs/specs/loyalty.md (Q20). Written before the implementation; team-owned."""

from datetime import datetime, timezone

from orderhub import orders


def place(client, items, customer_id=2, code=None):
    body = {"customer_id": customer_id, "items": items, **({"discount_code": code} if code else {})}
    return client.post("/orders", json=body).json()


def ship(client, order):
    return client.post(f"/orders/{order['id']}/ship")


def ret(client, order, sku, qty=1):
    return client.post(f"/orders/{order['id']}/returns", json={"items": [{"sku": sku, "quantity": qty}]})


def points(client, customer_id=2):
    return client.get(f"/customers/{customer_id}/points").json()


def from_order(data, order):
    return [e for e in data["entries"] if e["order_id"] == order["id"]]


def test_ac1_shipping_credits_one_point_per_full_100_minor_units(client):
    before = points(client)["balance"]
    order = place(client, [{"sku": "STAND-LAP", "quantity": 2}], code="SAVE10")
    assert order["total_minor"] == 8190
    assert ship(client, order).status_code == 200
    data = points(client)
    assert data["balance"] == before + 81
    assert [(e["kind"], e["points"]) for e in from_order(data, order)] == [("earn", 81)]


def test_ac2_points_are_credited_once_even_if_ship_is_retried(client):
    order = place(client, [{"sku": "MUG-350", "quantity": 3}])
    ship(client, order)
    once = points(client)["balance"]
    assert ship(client, order).status_code == 409
    assert points(client)["balance"] == once


def test_ac3_cancelled_orders_earn_nothing(client):
    before = points(client)["balance"]
    order = place(client, [{"sku": "DESK-LAMP", "quantity": 1}])
    assert points(client)["balance"] == before
    client.post(f"/orders/{order['id']}/cancel")
    assert points(client)["balance"] == before
    assert from_order(points(client), order) == []


def test_ac4_a_partial_return_claws_back_proportionally(client):
    order = place(client, [{"sku": "STAND-LAP", "quantity": 2}], code="SAVE10")
    ship(client, order)
    assert ret(client, order, "STAND-LAP").json()["refund_minor"] == 4095
    entries = from_order(points(client), order)
    assert [(e["kind"], e["points"]) for e in entries] == [("clawback", -40), ("earn", 81)]
    assert sum(e["points"] for e in entries) == 41


def test_ac5_a_full_return_over_several_returns_removes_exactly_the_earned_points(client):
    before = points(client)["balance"]
    order = place(client, [{"sku": "STAND-LAP", "quantity": 2}, {"sku": "PEN-GEL-BLK", "quantity": 3}], code="SAVE10")
    ship(client, order)
    for sku in ["PEN-GEL-BLK", "STAND-LAP", "PEN-GEL-BLK", "STAND-LAP", "PEN-GEL-BLK"]:
        assert ret(client, order, sku).status_code == 201
    entries = from_order(points(client), order)
    assert sum(e["points"] for e in entries) == 0
    assert points(client)["balance"] == before


def test_ac6_support_sees_balance_and_history_newest_first(client):
    first = place(client, [{"sku": "MUG-350", "quantity": 1}])
    second = place(client, [{"sku": "NB-A5", "quantity": 2}])
    ship(client, first)
    ship(client, second)
    r = client.get("/customers/2/points")
    assert r.status_code == 200
    data = r.json()
    assert data["customer_id"] == 2
    assert [e["order_id"] for e in data["entries"]][:2] == [second["id"], first["id"]]
    assert set(data["entries"][0]) == {"kind", "order_id", "points", "created_at"}
    assert data["balance"] == sum(e["points"] for e in data["entries"])
    assert client.get("/customers/9999/points").status_code == 404


def test_ac7_billing_handoff_is_unchanged_by_loyalty(client, session, tmp_path):
    order = place(client, [{"sku": "STAND-LAP", "quantity": 1}])
    ship(client, order)
    path = orders.write_billing_handoff(session, datetime.now(timezone.utc).date(), str(tmp_path))
    header, row = path.read_text(encoding="utf-8").splitlines()[:2]
    assert header == "order_id,customer_name,country,currency,subtotal_minor,total_minor"
    assert len(row.split(",")) == 6
