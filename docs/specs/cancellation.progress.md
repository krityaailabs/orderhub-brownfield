# Progress: Idempotent order cancellation

| Slice | State | Commit | Notes |
|---|---|---|---|
| S1 | done | see `git log --grep "Q12"` | Reproduction test failed with stock 225 (one extra restock of 5), then passed |
| S2 | done | | Fingerprint ignores JSON key order and whitespace |
| S3 | done | | Only 2xx outcomes are stored, so a 409 can be retried after the cause is fixed |
| S4 | done | | Hook selects checks by changed paths |

## Decisions made during implementation
- Keys longer than 128 characters are rejected with 422.

## Rules the agent needed reminding of (move to AGENTS.md or an ADR)
- "Don't change existing tests": once, when the old cancel test seemed to conflict (it didn't).

## Next step
- Follow-up issues for idempotency on order placement and returns.
