# Capstone (Section 15): ship the loyalty-points feature end to end

**Start tag:** `s15-start` · **Reference solution:** `s15` · **Time:** 6–10 hours · **Agent usage:** expected, with everything from Sections 0–8

Ship issue **Q20** (`docs/issues/Q20.md`) on OrderHub using the full Agentic Delivery Loop, and review it like a staff engineer. There is no stub to fill in: you write the spec, the plan, the tests and the code, and you produce the evidence.

## Deliverables (checked by `python tools/capstone_check.py`)

| # | Deliverable | Where |
|---|---|---|
| 1 | Spec with at least 5 acceptance criteria, non-goals and open questions; passes `make spec-check` | `docs/specs/loyalty.md` |
| 2 | Slice plan, every slice ≤ 300 lines, every criterion covered | `docs/specs/loyalty.plan.md` |
| 3 | Progress notes, every slice marked done | `docs/specs/loyalty.progress.md` |
| 4 | Acceptance tests written first, one or more per criterion (`test_ac1_...`, `test_ac2_...`) | `services/orders/tests/test_loyalty_acceptance.py` |
| 5 | Review notes: each pull request, one **rejected attempt** and why, findings by layer | `docs/capstone/review.md` |
| 6 | Metrics: delivery (slices, lines, time) and quality (findings by layer, defects after merge) | `docs/capstone/metrics.md` |
| 7 | Retrospective, including the context-file lines you added | `docs/capstone/retro.md` |
| 8 | At least one line about loyalty in `AGENTS.md` | `AGENTS.md` |

`python tools/capstone_check.py --full` also runs the Python tests, the billing golden check and the security gate: all must pass.

## Constraints

- The nightly billing file must not change (Q20, finance). The billing golden check proves it.
- Integer arithmetic (ADR 0001). No new dependencies (ADR 0002). The security gate stays green.
- Every slice is a pull request (or a commit, if you work alone) at a green state, reviewed with `docs/course/review-checklist.md` and `make review-flags`.
- Redemption is out of scope. If your agent starts on it, that's a review finding.

## Rubric

See `rubric.md`. Score yourself before you compare with the reference (Lectures 15.2–15.4).

```bash
git switch -c my-capstone s15-start
python tools/capstone_check.py          # 0 of 8 at the start
```
