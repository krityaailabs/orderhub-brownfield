"""Regression tests for issues Q0 and Q1, merged from Section 0."""

from orderhub import pricing


def test_q0_discount_rounds_half_up_on_the_discount():
    assert pricing.apply_percentage_discount(1001, 10) == 901


def test_q0_reported_order_totals_901(client):
    r = client.post("/orders", json={"customer_id": 1, "items": [{"sku": "NB-A5", "quantity": 1}],
                                     "discount_code": "SAVE10"})
    assert r.json()["total_minor"] == 901


def test_q1_email_check_ignores_case(client):
    r = client.post("/customers", json={"email": "Aiko.Tanaka@Example.com", "name": "Aiko", "country": "JP"})
    assert r.status_code == 409
