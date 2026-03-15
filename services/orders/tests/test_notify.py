import pytest
from fastapi.testclient import TestClient

from orderhub import notify, seed
from orderhub.api import create_app
from orderhub.config import Settings

WEBHOOK = "https://warehouse.example/hooks/orderhub"


@pytest.fixture
def calls(monkeypatch):
    recorded = []
    monkeypatch.setattr(notify, "order_cancelled", lambda *args: recorded.append(args))
    return recorded


@pytest.fixture
def hooked_client(tmp_path, calls):
    app = create_app(Settings("sqlite://", "USD", str(tmp_path), WEBHOOK))
    with app.state.session_factory() as session:
        seed.load(session)
    return TestClient(app)


def test_cancel_notifies_the_warehouse(hooked_client, calls):
    order = hooked_client.post("/orders", json={"customer_id": 1, "items": [{"sku": "MUG-350", "quantity": 2}]}).json()
    assert hooked_client.post(f"/orders/{order['id']}/cancel").status_code == 200
    assert calls == [(WEBHOOK, order["id"], [{"product_id": order["lines"][0]["product_id"], "quantity": 2}])]
