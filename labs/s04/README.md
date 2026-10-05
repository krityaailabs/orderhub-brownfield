# Lab s04 and Project 1: returns, from spec to green build (Section 4)

**Start tag:** `s04-start` · **Solved tag:** `s04` · **Time:** 3–5 hours · **Agent usage:** recommended, one slice per session

At `s04-start` the acceptance tests for AC-1 to AC-8 are already written (by the team, before any code) and they fail. Your job is to make them pass without editing them.

| Lecture | Task | Done when |
|---|---|---|
| 4.1 | Name who owns each of five test types in your team today | Written answer |
| 4.2 | Read `services/orders/tests/test_returns_acceptance.py`; run it and see every test fail for the right reason | `NotImplementedError` from the three stubs, not import errors |
| 4.3 | Implement `ship_order` and `return_items` (`orders.py`) and `refund_for_units` (`pricing.py`), one slice at a time | All 10 acceptance tests pass |
| 4.4 | Investigate `incident/`; implement `find_test_edits` in `tools/protect_tests.py`; run `make protect-tests` | Guard tests pass; the tampered diff is blocked |
| 4.5 | Write the two property-based tests marked `Lab 4.5` in `test_returns_properties.py` | Both pass; one of them fails if you remove the remainder rule |
| 4.6 | Run `make mutate`; add tests that kill the two surviving mutants | `8 of 8 mutants killed` |
| 4.7 | Watch the characterisation demo; run `tests/test_pricing_characterisation.py` | Passes; you can explain what it does and doesn't prove |
| 4.8 | Project 1 review checklist (`project1-checklist.md`) | Every box ticked; `make test`, `make lint`, `make billing-demo` pass |

```bash
git switch -c my-s04 s04-start
cd services/orders && python -m pytest -q tests/test_returns_acceptance.py   # 10 fail
```

Rules for this lab (they're in AGENTS.md too): don't edit any existing test; one slice per session; failing tests before code; `make test`, `make lint` and `make billing-demo` before you call a slice done.

Hints: `HINTS.md`. Problems: `TROUBLESHOOTING.md`. Expected output: `EXPECTED_OUTPUT.md`.

## Break it (5 minutes)

After everything passes, change one expected number in `test_returns_acceptance.py`, commit, and run `make protect-tests`. Then undo the commit.
