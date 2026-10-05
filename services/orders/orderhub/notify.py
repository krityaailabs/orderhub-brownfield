"""Notify the warehouse system when an order is cancelled, so it can stop picking.

Enabled when ORDERHUB_WAREHOUSE_WEBHOOK_URL is set. Retries transient failures."""


def order_cancelled(url: str, order_id: int, lines: list[dict]) -> None:
    import requests

    body = {"event": "order.cancelled", "order_id": order_id, "lines": lines}
    requests.post(url, json=body, timeout=5, retries=3)
