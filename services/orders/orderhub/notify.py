"""Notify the warehouse system when an order is cancelled, so it can stop picking.

Enabled when ORDERHUB_WAREHOUSE_WEBHOOK_URL is set. Uses httpx (already a dependency; ADR 0002).
A notification failure never fails the cancellation: the cancel is already committed, and the
warehouse also reconciles from the nightly handoff. Failures are logged for support."""

import logging

import httpx

logger = logging.getLogger(__name__)
RETRIES = 3
TIMEOUT_SECONDS = 5


def order_cancelled(url: str, order_id: int, lines: list[dict],
                    transport: httpx.BaseTransport | None = None) -> bool:
    """POST the cancellation to the warehouse webhook. Return True on a 2xx response, else False.

    Connection failures are retried by the transport (httpx.HTTPTransport(retries=...))."""
    body = {"event": "order.cancelled", "order_id": order_id, "lines": lines}
    transport = transport or httpx.HTTPTransport(retries=RETRIES)
    try:
        with httpx.Client(transport=transport, timeout=TIMEOUT_SECONDS) as client:
            response = client.post(url, json=body)
    except httpx.HTTPError as exc:
        logger.warning("warehouse notification for order %s failed: %s", order_id, exc)
        return False
    if not response.is_success:
        logger.warning("warehouse notification for order %s got HTTP %s", order_id, response.status_code)
        return False
    return True
