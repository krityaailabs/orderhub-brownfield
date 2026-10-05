# Lab s02: OrderHub context pack (Section 2)

**Start tag:** `s02-start` · **Solved tag:** `s02` · **Time:** 2–3 hours across the section · **Agent usage:** optional (low)

At `s02-start`, `make test` fails on purpose: the context-pack tests and the context-check tests describe work you haven't done yet. Your job is to make them pass.

| Lecture | Task | Done when |
|---|---|---|
| 2.1 | Sort the twenty facts in `facts.md` into context, code or neither | Compared with `ANSWERS.md` |
| 2.2 | Predict which instruction files load in the four layouts in `layouts.md` | Checked with the simulator once you've built it (2.8) |
| 2.3 | Write the root `AGENTS.md` from the template already in place | `test_root_agents_md_*` pass |
| 2.4 | Write two ADRs in `docs/adr/` from `template.md`: money in integer minor units; no new dependencies without review | `test_two_accepted_adrs_exist` passes |
| 2.5 | Add `legacy/billing/AGENTS.md` (the handoff contract, encoding, layout) and `web/AGENTS.md`; add `.github/copilot-instructions.md` as a pointer; add `CLAUDE.local.md` to `.gitignore` | `test_legacy_billing_*`, `test_copilot_pointer_*`, `test_no_claude_local_md_*` pass |
| 2.6 | Choose continue, compact or restart for the three sessions in `sessions.md` | Compared with `ANSWERS.md` |
| 2.7 | Review the five context files in `review/` | Compared with `ANSWERS.md` |
| 2.8 | Implement the seven stub functions in `tools/context_check.py`; run `make context-check`; then do the manual three-tool smoke test in `docs/course/context-smoke-test.md` | `make test` passes; `make context-check` passes |

## Steps for 2.8

```bash
git switch -c my-s02 s02-start
python -m pytest tools/tests/test_context_check.py -q     # 7 functions to implement; read each docstring
make context-check
make test
```

Hints: `HINTS.md` (three levels). Problems: `TROUBLESHOOTING.md`. Expected output: `EXPECTED_OUTPUT.md`.

## Break it (5 minutes)

Create an empty `CLAUDE.local.md` at the repository root and run `make context-check`. Read the warning and the simulated Claude Code line. Then delete the file. If you use Claude Code, start a session with and without that file, and look at which instruction file it reports loading.

## Same workflow in three tools

See `same-workflow-three-tools.md`.
