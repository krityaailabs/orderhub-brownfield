import pytest
from orderhub import orders
from orderhub.errors import ValidationFailed


def test_t5_quantity_over_99_is_rejected_by_the_api(client):
    r = client.post("/orders", json={"customer_id": 1, "items": [{"sku": "NB-A5", "quantity": 100}]})
    assert r.status_code == 422
    ok = client.post("/orders", json={"customer_id": 1, "items": [{"sku": "NB-A5", "quantity": 99}]})
    assert ok.status_code == 201


def test_t5_domain_function_enforces_it_too(session):
    with pytest.raises(ValidationFailed, match="quantity must be at most 99"):
        orders.place_order(session, 1, [{"sku": "NB-A5", "quantity": 100}], "USD")
