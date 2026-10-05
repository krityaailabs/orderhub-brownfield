# Project 1 review checklist (returns)

Use this on your own pull requests before you call Project 1 done, and on any agent's.

- [ ] Every acceptance criterion AC-1 to AC-8 has a test that failed before the code and passes now
- [ ] No existing test line was changed (`make protect-tests` passes)
- [ ] Money uses integer arithmetic only; no `float`, no `round()` (ADR 0001)
- [ ] The remainder rule is implemented and tested (AC-3; property test)
- [ ] Validation errors change nothing (AC-5): stock and refunded totals are unchanged
- [ ] The 30-day boundary is tested at exactly 30 days (edge test)
- [ ] `make mutate` kills every mutant
- [ ] `make test`, `make lint`, `make billing-demo` pass; the handoff columns are unchanged (AC-8)
- [ ] The change is split into slices of under 300 lines each, matching `docs/specs/returns.plan.md`
- [ ] Each slice's PR description lists the criteria it covers and the files read
