# Capstone metrics (reference)

The reference was built in one working session with an AI agent, slice by slice, as separate commits (squashed into the `s15` tag). Line counts are measured from the commits; times were not measured and are left for you to fill in for your own capstone.

## Delivery

| Slice | Changed lines | Criteria | Tests added |
|---|---|---|---|
| Spec + plan | 74 | — | — |
| Acceptance tests | 97 | AC-1 to AC-7 | 7 |
| S1 ledger, earn, endpoint | 122 | AC-1, AC-2, AC-3, AC-6 | — |
| S2 clawback | 61 | AC-4, AC-5 | 2 property tests |
| S3 guards + context | 22 | AC-7 | 6 |
| **Total** | **376** | 7 | 15 |

Largest slice: 122 lines (budget 300).

## Quality

| Measure | Value |
|---|---|
| Acceptance tests that failed first for the right reason | 6 of 7 (AC-7 is a guard that passes before and after) |
| Attempts rejected in review | 1 (S2 attempt 1, caught by AC-5) |
| Plan corrections during implementation | 1 (endpoint moved into S1) |
| Findings from review-flags that needed an answer | 2 (API-SURFACE on S1) |
| Existing tests edited | 0 |
| Defects found after merge | 0 so far (no production use) |
| Python tests after the capstone | 103 passed (88 before) |

## What these numbers don't show

- Time: not measured in the reference. In your own capstone, record agent time and your time (spec, review, fixes) per slice; your time is the number that matters for the team.
- Whether marketing's rule (one point per full 1.00) is the right business rule. The tests prove the rule is implemented, not that it's wise.
- Production behaviour: volume, concurrency (two returns at the same moment), and support's actual questions.
