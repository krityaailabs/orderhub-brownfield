# Spec: Loyalty points (earn only)

- **Issue:** Q20
- **Status:** Agreed (marketing; finance on billing and redemption)
- **Owner:** Orders team

## Intent

Customers earn loyalty points for what they actually keep, so marketing can launch a rewards programme in the spring and support can answer "where are my points?". Earning only; spending comes later.

## Context

- An order is PLACED, then SHIPPED or CANCELLED (`orders.ship_order`, `orders.cancel_order`). Returns apply only to SHIPPED orders and refund in minor units, summing exactly to the total on a full return (`orders.return_items`, returns spec AC-3).
- `ship_order` raises Conflict when the order isn't PLACED, so a retried ship returns 409.
- The nightly billing handoff and the legacy batch must not change (Q20, finance; billing golden master).
- Money and points are integers (ADR 0001).

## Constraints

- Points are an append-only ledger (earn and clawback entries), not a mutable balance: support needs history, and audits need every change.
- Earning and clawback happen in the same database transaction as the ship or return that causes them.
- No new dependencies; the security gate and the billing golden check stay green.
- Existing tests are not edited.

## Acceptance criteria

- **AC-1** Given customer 2 places an order for 2 × STAND-LAP with SAVE10 (total 8190), when the order is shipped, then customer 2's balance increases by 81 (one point per full 100 minor units of the total) and the ledger has one earn entry of 81 for that order.
- **AC-2** Given a SHIPPED order, when ship is requested again, then the response is 409 and the balance is unchanged (points are credited once per order).
- **AC-3** Given a PLACED order, when it is cancelled, then no points are credited, before or after the cancellation.
- **AC-4** Given the shipped order from AC-1 (81 points), when 1 × STAND-LAP is returned (refund 4095), then a clawback entry of -40 is recorded: floor(81 × 4095 / 8190) = 40, and the balance from that order is 41.
- **AC-5** Given a shipped order, when its units are returned over several returns until every unit is returned, then the clawbacks sum to exactly minus the points earned, and the balance from that order is 0.
- **AC-6** Given customer 2 with entries, when support calls `GET /customers/2/points`, then the response is 200 with `balance` and `entries` (kind, order_id, points, created_at), newest first; for an unknown customer, 404.
- **AC-7** Given loyalty points are in place, when the billing handoff is written and the legacy batch runs, then the handoff still has six columns and the billing golden check passes.

## Non-goals

- Redemption (spending points). Needs finance: it changes totals, tax and the billing file.
- Expiry of points, tiers, bonus campaigns.
- Backfilling points for orders shipped before launch.
- Showing points to customers (support-facing endpoint only for launch).

## Open questions

- Should points earned on a fully returned order be shown in history at all? **Decision:** yes, with the clawback; support asked for the full trail (owner: support lead).
- Rounding of partial clawbacks: **Decision:** cumulative and proportional (AC-4, AC-5), so a full return always removes exactly what was earned (owner: orders team; marketing agreed).
