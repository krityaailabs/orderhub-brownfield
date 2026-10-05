# Plan A (proposed by the agent for slice S2 of the returns spec)

1. Read `orders.py`, `models.py`, `pricing.py`, `test_orders.py`, `legacy/billing/AGENTS.md`.
2. Write failing tests for AC-1, AC-5 and AC-7 in `services/orders/tests/test_returns.py`.
3. Add `returned_quantity: int = 0` to `OrderLine`.
4. Add `return_items(session, order_id, items)` in `orders.py`: check quantities, compute the refund as unit price × quantity (no discount in this slice), increment `returned_quantity`, restock.
5. Add `POST /orders/{id}/returns` in `api.py`.
6. Run `make test`, `make lint`, `make billing-demo`.

Files changed: `models.py`, `orders.py`, `api.py`, `schemas.py`, new `tests/test_returns.py`. Estimated ~150 lines.
