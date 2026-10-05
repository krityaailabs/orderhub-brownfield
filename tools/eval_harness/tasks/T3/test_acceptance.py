from orderhub.models import Product


def test_t3_repeated_skus_become_one_line(client, session):
    stock = session.query(Product).filter_by(sku="MUG-350").one().stock
    order = client.post("/orders", json={"customer_id": 1, "items": [
        {"sku": "MUG-350", "quantity": 1}, {"sku": "mug-350", "quantity": 2}, {"sku": "NB-A5", "quantity": 1}]}).json()
    assert [(line["quantity"]) for line in order["lines"]] == [3, 1]
    assert order["subtotal_minor"] == 3 * 1250 + 1001
    session.expire_all()
    assert session.query(Product).filter_by(sku="MUG-350").one().stock == stock - 3
