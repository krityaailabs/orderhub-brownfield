# Spec: Idempotent order cancellation

- **Issue:** Q12
- **Status:** Agreed
- **Owner:** Platform team, with warehouse operations

## Intent

Cancelling an order has the same effect however many times the request is sent, so client retries never restore stock twice, and the warehouse count matches OrderHub.

## Context

- `orders.cancel_order` restores stock for each line and sets status CANCELLED (`services/orders/orderhub/orders.py`).
- The mobile app retries `POST /orders/{id}/cancel` after a timeout (issue Q12).
- Cancelled orders are excluded from the billing handoff; returns (Section 4) apply only to SHIPPED orders.

## Constraints

- Integer stock arithmetic; one database commit per request.
- Existing tests must not be edited (ADR 0002's spirit applies to tests: changes need approval).
- The billing handoff columns and `make billing-demo` must not change.
- No new dependencies.

## Acceptance criteria

- **AC-1** Given a PLACED order for 5 × BAG-TOTE and stock 220, when it is cancelled twice without an idempotency key, then stock is 220 after both requests and both return 200 with status CANCELLED.
- **AC-2** Given a PLACED order, when `POST /orders/{id}/cancel` is sent twice with the same `Idempotency-Key`, then both responses are identical and the cancellation runs once.
- **AC-3** Given a key already used to cancel order A, when the same key is sent to cancel order B, then the response is 422 with "idempotency key reused for a different request" and order B is unchanged.
- **AC-4** Given a SHIPPED order, when it is cancelled, then the response is 409 and nothing changes, with or without a key; a failed request's key can be used again.
- **AC-5** Given cancelled orders, when the billing handoff is written, then they are excluded and the columns are unchanged.

## Non-goals

- Idempotency keys for other endpoints (follow-up issue: order placement and returns).
- Expiring stored keys (follow-up; keys are small and few at today's volumes).
- Changing the mobile app's retry behaviour.

## Open questions

- How long should keys be kept? **Decision:** forever for now; revisit when the table exceeds 1 million rows (owner: platform team).
