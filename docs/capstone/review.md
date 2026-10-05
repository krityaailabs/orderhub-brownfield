# Capstone review notes (reference)

Reviewed risk-first with `docs/course/review-checklist.md` and `make review-flags` on each slice's diff.

## Pull requests

| PR / slice | Lines | review-flags | Risk-first findings | Outcome |
|---|---|---|---|---|
| Spec + plan | 74 | — | Redemption, backfill and customer-facing display listed as non-goals; finance's "no billing change" recorded as AC-7 | Merge |
| Acceptance tests | 97 | — (new test file) | Six of seven failed first, for the right reason (no points endpoint); AC-7 passes before and after by design (a guard) | Merge |
| S1 ledger, earn, endpoint | 122 | API-SURFACE ×2 (new GET route; new response models) | New route is read-only, returns points only, 404 for unknown customers; earn happens inside `ship_order`'s transaction; unique earn per order backs up the PLACED check | Merge |
| S2 clawback | 61 | none | Arithmetic is integer-only; `refunded_before` captured before the update; property tests cover any full return sequence | Merge (after one rejected attempt) |
| S3 guards + context | 22 | none | Database rejects a second earn entry; AGENTS.md line reviewed for scope | Merge |

## Rejected attempt

**S2, attempt 1.** The first clawback removed `floor(refund_minor / 100)` points per return. It passed AC-4: for the 4095 refund it removes 40, which happens to equal the proportional answer. It failed AC-5: after returning every unit of a 2 × STAND-LAP + 3 × PEN-GEL-BLK order over five returns, **2 points remained** on a fully returned order (`assert 2 == 0`). Per-return rounding loses a fraction of a point on every return, and the losses add up.
**Accepted version:** cumulative and proportional: the total removed after each return is `floor(earned × refunded_total / total)`, and each entry is the difference, so a full return always removes exactly what was earned. Two property tests (60 examples each) now guard it.

## Findings by layer

| Layer | Findings |
|---|---|
| Tests (failed first?) | Acceptance tests failed first (6 of 7; AC-7 is a guard). AC-5 caught the rejected attempt; AC-4 alone would not have |
| Plan | Dependency error found during S1: the endpoint had to come before any criterion could pass; plan revised and recorded |
| review-flags | API-SURFACE on S1 (answered above); nothing else |
| Your review | Unique earn per order should hold at the database level, not only in `ship_order`; added in S3 with a test |
| Security gate | 5 of 5 on every slice; no new dependency |
| Golden / billing checks | Golden 52 records identical; comparison zero differences; billing demo unchanged |
