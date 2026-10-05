"""Tests for the warehouse notification (R5, repaired in Lab s06).

The R5 test replaced notify.order_cancelled with a lambda, so the code under review never ran.
These tests run notify.py itself against httpx.MockTransport."""

import json

import httpx
import pytest
from fastapi.testclient import TestClient

from orderhub import notify, seed
from orderhub.api import create_app
from orderhub.config import Settings

WEBHOOK = "https://warehouse.example/hooks/orderhub"


def recording(status=204):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        return httpx.Response(status)

    return seen, httpx.MockTransport(handler)


def test_notifier_posts_the_cancellation_once():
    seen, transport = recording()
    assert notify.order_cancelled(WEBHOOK, 7, [{"product_id": 1, "quantity": 2}], transport=transport) is True
    assert seen == [{"event": "order.cancelled", "order_id": 7, "lines": [{"product_id": 1, "quantity": 2}]}]


def test_notifier_reports_failure_without_raising():
    _, transport = recording(status=503)
    assert notify.order_cancelled(WEBHOOK, 7, [], transport=transport) is False

    def unreachable(request):
        raise httpx.ConnectError("warehouse unreachable")

    assert notify.order_cancelled(WEBHOOK, 7, [], transport=httpx.MockTransport(unreachable)) is False


@pytest.fixture
def hooked(tmp_path):
    app = create_app(Settings("sqlite://", "USD", str(tmp_path), WEBHOOK))
    with app.state.session_factory() as session:
        seed.load(session)
    return app


def test_cancel_notifies_the_warehouse_once(hooked):
    seen, hooked.state.notify_transport = recording()
    client = TestClient(hooked)
    order = client.post("/orders", json={"customer_id": 1, "items": [{"sku": "MUG-350", "quantity": 2}]}).json()
    assert client.post(f"/orders/{order['id']}/cancel").status_code == 200
    assert client.post(f"/orders/{order['id']}/cancel").status_code == 200
    assert seen == [{"event": "order.cancelled", "order_id": order["id"],
                     "lines": [{"product_id": order["lines"][0]["product_id"], "quantity": 2}]}]


def test_cancel_succeeds_when_the_warehouse_is_down(hooked):
    _, hooked.state.notify_transport = recording(status=503)
    client = TestClient(hooked)
    order = client.post("/orders", json={"customer_id": 1, "items": [{"sku": "MUG-350", "quantity": 1}]}).json()
    r = client.post(f"/orders/{order['id']}/cancel")
    assert r.status_code == 200 and r.json()["status"] == "CANCELLED"
