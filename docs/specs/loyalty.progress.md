# Progress: Loyalty points (earn only)

| Slice | State | Commit | Notes |
|---|---|---|---|
| S1 | done | "Capstone S1" | Endpoint moved in from the old S3: the acceptance tests read points through the API. 122 changed lines |
| S2 | done | "Capstone S2" | Attempt 1 rejected (per-return rounding left 2 points after a full return; AC-5). Cumulative proportional clawback; property tests |
| S3 | done | "Capstone S3" | Unique earn per order proven at the database level; AGENTS.md line; golden check and security gate green |

## Decisions made during implementation
- Earn and clawback entries are added to the caller's session and committed with the ship or return (one transaction).
- Clawback is cumulative: removed so far = floor(earned × refunded_total / order_total); a return that changes nothing adds no entry.
- Ledger order: newest first by created_at, then id (two entries can share a timestamp in tests).

## Rules the agent needed reminding of (move to AGENTS.md or an ADR)
- None needed in the reference session. The billing boundary went into AGENTS.md anyway (S3), because it lives in the issue and the spec, not in the code, and the next session won't read either unless told to.

## Next step
- Redemption: needs a spec with finance (totals, tax, billing file). Not started.
