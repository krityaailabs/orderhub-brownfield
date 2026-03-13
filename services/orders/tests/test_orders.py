from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from orderhub import orders
from orderhub.models import Product


def place(client, items, code=None, customer_id=1):
    body = {"customer_id": customer_id, "items": items}
    if code:
        body["discount_code"] = code
    return client.post("/orders", json=body)


def test_place_order_computes_totals(client: TestClient) -> None:
    r = place(client, [{"sku": "PEN-GEL-BLK", "quantity": 4}, {"sku": "MUG-350", "quantity": 1}])
    assert r.status_code == 201
    body = r.json()
    assert body["subtotal_minor"] == 249 * 4 + 1250
    assert body["total_minor"] == body["subtotal_minor"]
    assert body["total_display"] == "22.46 USD"


def test_place_order_with_discount_on_round_amount(client: TestClient) -> None:
    r = place(client, [{"sku": "STAND-LAP", "quantity": 2}], code="SAVE10")
    assert r.status_code == 201
    assert r.json()["total_minor"] == 8190


def test_sku_is_case_insensitive(client: TestClient) -> None:
    assert place(client, [{"sku": "mug-350", "quantity": 1}]).status_code == 201


def test_unknown_sku_is_rejected(client: TestClient) -> None:
    assert place(client, [{"sku": "NOPE", "quantity": 1}]).status_code == 422


def test_inactive_product_is_rejected(client: TestClient) -> None:
    assert place(client, [{"sku": "HDPHN-WIRED", "quantity": 1}]).status_code == 422


def test_out_of_stock_is_rejected(client: TestClient) -> None:
    assert place(client, [{"sku": "PLANNER-26", "quantity": 1}]).status_code == 409


def test_inactive_discount_code_is_rejected(client: TestClient) -> None:
    assert place(client, [{"sku": "MUG-350", "quantity": 1}], code="SUMMER25").status_code == 422


def test_unknown_customer_is_rejected(client: TestClient) -> None:
    assert place(client, [{"sku": "MUG-350", "quantity": 1}], customer_id=999).status_code == 404


def test_placing_an_order_reduces_stock(client: TestClient, session: Session) -> None:
    place(client, [{"sku": "DESK-LAMP", "quantity": 3}])
    session.expire_all()
    assert session.get(Product, 3).stock == 117


def test_get_order(client: TestClient) -> None:
    order_id = place(client, [{"sku": "MUG-350", "quantity": 2}]).json()["id"]
    r = client.get(f"/orders/{order_id}")
    assert r.status_code == 200
    assert r.json()["lines"][0]["quantity"] == 2


def test_get_missing_order(client: TestClient) -> None:
    assert client.get("/orders/12345").status_code == 404


def test_list_orders_filters_by_status(client: TestClient) -> None:
    a = place(client, [{"sku": "MUG-350", "quantity": 1}]).json()["id"]
    place(client, [{"sku": "MUG-350", "quantity": 1}])
    client.post(f"/orders/{a}/cancel")
    cancelled = client.get("/orders", params={"status": "CANCELLED"}).json()
    assert [o["id"] for o in cancelled] == [a]


def test_cancel_restores_stock(client: TestClient, session: Session) -> None:
    order_id = place(client, [{"sku": "BAG-TOTE", "quantity": 5}]).json()["id"]
    r = client.post(f"/orders/{order_id}/cancel")
    assert r.json()["status"] == "CANCELLED"
    session.expire_all()
    assert session.get(Product, 5).stock == 220


def test_billing_handoff_skips_cancelled_orders(client: TestClient, session: Session, tmp_path) -> None:
    keep = place(client, [{"sku": "MUG-350", "quantity": 1}]).json()["id"]
    drop = place(client, [{"sku": "MUG-350", "quantity": 1}]).json()["id"]
    client.post(f"/orders/{drop}/cancel")
    today = datetime.now(timezone.utc).date()
    path = orders.write_billing_handoff(session, today, str(tmp_path))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "order_id,customer_name,country,currency,subtotal_minor,total_minor"
    assert [line.split(",")[0] for line in lines[1:]] == [str(keep)]
