# Spec: Partial returns with exact refunds

- **Issue:** Q7
- **Status:** Agreed
- **Owner:** Product (customer operations), with finance sign-off on AC-2 and AC-3

## Intent

Customers can return some or all units of a shipped order within 30 days and receive a refund that is exact to the minor unit, so customer operations stops handling returns by hand and finance can reconcile refunds without adjustments.

## Context

- Orders, lines and stock live in `services/orders/orderhub/` (`orders.py`, `models.py`).
- Discounts apply to the whole order subtotal (`pricing.apply_percentage_discount`); a line has no discount of its own.
- Money is integer minor units (ADR 0001).
- The billing CSV handoff is read by `legacy/billing` by column position (`legacy/billing/AGENTS.md`).
- There is no "shipped" transition today; orders are created as PLACED.

## Constraints

- Integer minor units only; rounding rules stated in the code (ADR 0001).
- The billing CSV handoff columns and `make billing-demo` output must not change.
- Existing tests must not be edited.
- No new dependencies (ADR 0002).

## Acceptance criteria

- **AC-1** Given a SHIPPED order with 2 × MUG-350 and no discount, when the customer returns 1 × MUG-350, then the refund is 1250 and 1 unit of that line is recorded as returned.
- **AC-2** Given a SHIPPED order with 2 × STAND-LAP and code SAVE10 (subtotal 9100, total 8190), when the customer returns 1 × STAND-LAP, then the refund is 4095 (the line's share of the discount is allocated in proportion to its value and rounded half-up).
- **AC-3** Given a SHIPPED order with 2 × PEN-GEL-BLK and 1 × MUG-350 and code WELCOME15 (total 1486), when the customer returns one pen, then the mug, then the last pen, then the refunds are 212, 1063 and 211, and their sum equals the order total exactly (the final return receives the remainder).
- **AC-4** Given a SHIPPED order created more than 30 days (30 × 24 hours) before the request, when the customer asks to return any unit, then the request is rejected with 422 and "return window closed".
- **AC-5** Given a line of 2 units with 1 already returned, when the customer asks to return 2 more, then the request is rejected with 422 and nothing changes.
- **AC-6** Given an order that is PLACED or CANCELLED, when the customer asks to return any unit, then the request is rejected with 409 (PLACED orders are cancelled, not returned).
- **AC-7** Given a successful return of 1 × DESK-LAMP, when the return is recorded, then DESK-LAMP stock increases by 1.
- **AC-8** Given any number of returns, when `make billing-demo` runs, then the handoff columns and the billing file layout are unchanged.

## Non-goals

- Paying the refund to the customer's card or bank (payments integration is a separate issue).
- Exchanges, store credit and return shipping labels.
- Returning part of a unit, or returning more than was bought.
- Reporting refunds to finance in the billing file (follow-up issue after finance agrees a format).
- Customer emails.

## Open questions

- Is day 30 inclusive? **Decision:** a return is allowed while the request time is before `created_at + 30 days` (product, agreed).
- Who can mark an order shipped? **Decision:** an internal endpoint for now; access control is out of scope (owner: platform team).
