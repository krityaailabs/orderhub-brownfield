## Task

Issue / spec / slice: <!-- link, e.g. docs/specs/cancellation.md S2 -->

## What changed and why

<!-- One paragraph. If an agent wrote the code, say which tool and at what autonomy level (L1-L5). -->

## Declared files vs changed files

<!-- Paste the plan's file list. Explain any file outside it. -->

## Risk notes (fill in or write "none")

- Deleted checks, conditions or bounds:
- Changed existing tests (needs [test-change-approved]):
- New dependencies (ADR 0002):
- API, schema or billing-handoff changes:
- External calls and their failure behaviour:

## Evidence

- [ ] Each acceptance criterion has a test that failed before this change
- [ ] `make test`, `make lint` pass; `make billing-demo` if orders.py or legacy/ changed
- [ ] `make review-flags` output read; each flag answered above

## Decisions and context-file proposals

<!-- Decisions made during implementation; anything the agent needed telling twice. -->
