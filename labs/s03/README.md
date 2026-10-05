# Lab s03: spec and plan for the OrderHub returns feature (Section 3)

**Start tag:** `s03-start` · **Solved tag:** `s03` · **Time:** 2–3 hours · **Agent usage:** recommended for the interview (3.3) and the plan (3.4)

At `s03-start`, `make test` fails on purpose: `tools/tests/test_spec_check.py` (5 stub functions in `tools/spec_check.py`) and `tools/tests/test_returns_spec.py` (the spec and plan you'll write) describe the work.

| Lecture | Task | Done when |
|---|---|---|
| 3.1 | Rewrite the one-line prompt in `prompt.md` as three questions the agent should have asked | Compared with `ANSWERS.md` |
| 3.2 | Score `weak-spec.md` with the rubric; improve it | `python tools/spec_check.py labs/s03/weak-spec.md labs/s03/weak-spec.plan.md` lists the problems you expected |
| 3.3 | Run the interview on issue Q7 (`docs/issues/Q7.md`); keep only questions that change the spec | Your question list, compared with `ANSWERS.md` |
| 3.4 | Approve or reject the three plans in `plans/` with written reasons | Compared with `ANSWERS.md` |
| 3.5 | Write `docs/specs/returns.md` and `docs/specs/returns.plan.md` from the template | `make spec-check` passes; `test_returns_spec.py` passes |
| 3.6 | Fill the trade-off table in `spec-approaches.md` | Compared with `ANSWERS.md` |
| 3.7 | Slice the loyalty epic in `loyalty-epic.md` | Compared with `ANSWERS.md` |
| 3.8 | Implement the five stubs in `tools/spec_check.py` | `make test` passes |

```bash
git switch -c my-s03 s03-start
python -m pytest tools/tests/test_spec_check.py -q
make spec-check
make test
```

Hints: `HINTS.md`. Problems: `TROUBLESHOOTING.md`. Expected output: `EXPECTED_OUTPUT.md`.

## Break it (5 minutes)

In your plan, change one slice's size to `~900 lines` and remove `AC-8` from every slice. Run `make spec-check` and read both problems. Put them back.

## Same workflow in three tools

All three tools have a planning or "ask before acting" mode. Ask for a plan against the spec, with slices, criteria and sizes, and no edits. See `same-workflow-three-tools.md`.
