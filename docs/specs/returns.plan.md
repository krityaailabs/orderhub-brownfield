# Plan: Partial returns with exact refunds

Spec: `docs/specs/returns.md`. Each slice is one pull request: failing acceptance tests first, then the change, then `make test`, `make lint` and `make billing-demo`.

### S1: Mark an order shipped
- Criteria: AC-6
- Size: ~60 lines
- Depends on: none
- Change: `ship_order` in `orders.py` (PLACED → SHIPPED; SHIPPED or CANCELLED → 409) and `POST /orders/{id}/ship`. Tests for the transitions.

### S2: Return whole units without a discount
- Criteria: AC-1, AC-5, AC-7
- Size: ~150 lines
- Depends on: S1
- Change: `returned_quantity` on `OrderLine`; `return_items` in `orders.py`; `POST /orders/{id}/returns` returning the refund; quantity checks; restock.

### S3: Allocate the discount exactly
- Criteria: AC-2, AC-3
- Size: ~100 lines
- Depends on: S2
- Change: `pricing.refund_for_units` with proportional allocation rounded half-up, and the remainder rule for the final return; property-based test that the sum of refunds equals the total.

### S4: Window and status rules
- Criteria: AC-4, AC-6
- Size: ~60 lines
- Depends on: S2
- Change: 30-day window check using `created_at`; reject PLACED and CANCELLED with 409.

### S5: Guard the billing contract
- Criteria: AC-8
- Size: ~40 lines
- Depends on: none
- Change: a test that runs the handoff writer and checks the header and column positions; add `make billing-demo` to CI.

## Risks

- `created_at` is stored without a time zone in SQLite; compare in UTC.
- Existing orders have no `returned_quantity`; default to 0.
