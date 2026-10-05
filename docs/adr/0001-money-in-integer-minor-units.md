# ADR 0001: Money in integer minor units

- **Status:** Accepted
- **Date:** 2026-10-05

## Context

Issue Q0 showed a one-cent error caused by float arithmetic in `pricing.apply_percentage_discount`. Finance reconciles to the cent. Floats cannot represent most decimal amounts exactly, and conversions such as `int()` truncate rather than round.

## Decision

All money in OrderHub is stored, passed and calculated as integer minor units (for example, cents). Rounding is explicit and uses integer arithmetic, with the rule stated next to the code (for discounts: round the discount half-up, then subtract).

## Consequences

- Display formatting happens only at the edges (`pricing.format_money`).
- Any `float` in money code is a review finding.
- Currencies with zero or three decimal places need care in the billing export (implied two decimals); see `legacy/billing/AGENTS.md`.

## Applies to

`services/orders/orderhub/pricing.py`, `orders.py`, any new money code.
