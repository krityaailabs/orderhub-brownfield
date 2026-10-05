def place(client, customer_id):
    body = {"customer_id": customer_id, "items": [{"sku": "MUG-350", "quantity": 1}]}
    return client.post("/orders", json=body).json()


def test_t2_customer_filter(client):
    a, b = place(client, 1), place(client, 2)
    ids = [o["id"] for o in client.get("/orders", params={"customer_id": 2}).json()]
    assert b["id"] in ids and a["id"] not in ids
    assert client.get("/orders", params={"customer_id": 9999}).json() == []


def test_t2_customer_filter_is_validated_and_combines(client):
    assert client.get("/orders", params={"customer_id": 0}).status_code == 422
    order = place(client, 3)
    client.post(f"/orders/{order['id']}/cancel")
    ids = [o["id"] for o in client.get("/orders", params={"customer_id": 3, "status": "CANCELLED"}).json()]
    assert ids == [order["id"]]
