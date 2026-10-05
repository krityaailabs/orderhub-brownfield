def test_t1_status_filter_ignores_case_and_spaces(client):
    order = client.post("/orders", json={"customer_id": 1, "items": [{"sku": "MUG-350", "quantity": 1}]}).json()
    client.post(f"/orders/{order['id']}/ship")
    ids = [[o["id"] for o in client.get("/orders", params={"status": s}).json()]
           for s in ("SHIPPED", "shipped", " Shipped ")]
    assert ids[0] == ids[1] == ids[2] and order["id"] in ids[0]
