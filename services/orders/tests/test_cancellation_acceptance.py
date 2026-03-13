"""Acceptance tests for docs/specs/cancellation.md (issue Q12). Team-owned; do not edit to pass."""

from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from orderhub import orders
from orderhub.models import Order, Product


def place(client, sku="BAG-TOTE", qty=5):
    return client.post("/orders", json={"customer_id": 6, "items": [{"sku": sku, "quantity": qty}]}).json()


def test_ac1_cancelling_twice_restores_stock_once(client: TestClient, session: Session) -> None:
    order = place(client)
    first = client.post(f"/orders/{order['id']}/cancel")
    second = client.post(f"/orders/{order['id']}/cancel")
    assert (first.status_code, second.status_code) == (200, 200)
    assert first.json()["status"] == second.json()["status"] == "CANCELLED"
    session.expire_all()
    assert session.get(Product, 5).stock == 220


def test_ac2_same_key_returns_the_same_response_and_runs_once(client: TestClient, session: Session) -> None:
    order = place(client)
    headers = {"Idempotency-Key": "app-7f3a-cancel-1"}
    first = client.post(f"/orders/{order['id']}/cancel", headers=headers)
    second = client.post(f"/orders/{order['id']}/cancel", headers=headers)
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    session.expire_all()
    assert session.get(Product, 5).stock == 220


def test_ac3_key_reused_for_another_order_is_rejected(client: TestClient, session: Session) -> None:
    a, b = place(client), place(client, sku="MUG-350", qty=1)
    headers = {"Idempotency-Key": "app-reused-key"}
    assert client.post(f"/orders/{a['id']}/cancel", headers=headers).status_code == 200
    r = client.post(f"/orders/{b['id']}/cancel", headers=headers)
    assert r.status_code == 422
    assert "idempotency key reused for a different request" in r.json()["error"]
    session.expire_all()
    assert session.get(Order, b["id"]).status == "PLACED"


def test_ac4_shipped_order_conflicts_and_the_key_can_be_used_again(client: TestClient, session: Session) -> None:
    order = place(client, sku="MUG-350", qty=1)
    client.post(f"/orders/{order['id']}/ship")
    headers = {"Idempotency-Key": "app-shipped-1"}
    assert client.post(f"/orders/{order['id']}/cancel", headers=headers).status_code == 409
    assert client.post(f"/orders/{order['id']}/cancel").status_code == 409
    other = place(client, sku="MUG-350", qty=1)
    assert client.post(f"/orders/{other['id']}/cancel", headers=headers).status_code == 200


def test_ac5_cancelled_orders_stay_out_of_the_handoff(client: TestClient, session: Session, tmp_path) -> None:
    keep, drop = place(client, sku="MUG-350", qty=1), place(client, sku="MUG-350", qty=1)
    client.post(f"/orders/{drop['id']}/cancel")
    client.post(f"/orders/{drop['id']}/cancel")
    path = orders.write_billing_handoff(session, datetime.now(timezone.utc).date(), str(tmp_path))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "order_id,customer_name,country,currency,subtotal_minor,total_minor"
    assert [line.split(",")[0] for line in lines[1:]] == [str(keep["id"])]
