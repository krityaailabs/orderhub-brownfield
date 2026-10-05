# Plan: Loyalty points (earn only)

Spec: `docs/specs/loyalty.md`. One slice per pull request; acceptance tests first; the billing golden check and the security gate run on every slice.

Map of the change: `models.py` (LoyaltyEntry) ← `loyalty.py` (points_for, credit_shipment, claw_back, balance, entries) ← `orders.py` (ship_order, return_items call loyalty in the same transaction) ← `api.py` (GET /customers/{id}/points).

### S1: Ledger, earning on shipment, and the support endpoint
- Criteria: AC-1, AC-2, AC-3, AC-6
- Size: ~190 lines
- Depends on: none
- Change: `LoyaltyEntry` model with a unique earn per order; `loyalty.points_for`, `credit_shipment`, `balance`, `entries`; `ship_order` credits before its commit; `GET /customers/{id}/points`.
- Revised during S1: the acceptance tests read points through the API, so the endpoint (planned as S3) had to come first. Merged into S1; still under 300 lines.

### S2: Clawback on returns
- Criteria: AC-4, AC-5
- Size: ~120 lines
- Depends on: S1
- Change: `loyalty.claw_back` (cumulative, proportional); `return_items` calls it before its commit; property test: any full return sequence removes exactly the earned points.

### S3: Guard billing and context
- Criteria: AC-7
- Size: ~40 lines
- Depends on: S1, S2
- Change: acceptance test for the handoff header; golden check in the definition of done; AGENTS.md line about the ledger and the billing boundary.
