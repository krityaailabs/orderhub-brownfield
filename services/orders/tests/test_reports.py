from datetime import datetime, timezone


def test_daily_sales_counts_todays_orders(client):
    client.post("/orders", json={"customer_id": 1, "items": [{"sku": "MUG-350", "quantity": 2}]})
    today = datetime.now(timezone.utc).date().isoformat()
    report = client.get("/reports/daily-sales", params={"date": today}).json()
    assert report["orders"] >= 1
    assert report["total_minor"] > 0
