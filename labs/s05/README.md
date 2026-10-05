# Lab s05: idempotent cancellation across three modules (Section 5)

**Start tag:** `s05-start` · **Solved tag:** `s05` · **Time:** 2–3 hours · **Agent usage:** recommended

At `s05-start`, these fail on purpose: `test_cancellation_acceptance.py` (AC-1 to AC-4; the Q12 bug is real), `test_idempotency.py` (three stubs in `orderhub/idempotency.py`), and `tools/tests/test_precommit.py` (one stub in `tools/precommit.py`).

| Lecture | Task | Done when |
|---|---|---|
| 5.1 | Map a recent change of your own onto the twelve steps; mark skipped steps | Written answer |
| 5.2 | Slice S2 of `docs/specs/cancellation.plan.md`: the three functions in `orderhub/idempotency.py` (the `IdempotencyRecord` model is provided). Slice S3: the `Idempotency-Key` wiring in `api.py` is provided; run a review session that maps each line to AC-2, AC-3 and AC-4. Keep `docs/specs/cancellation.progress.md` (template in `progress-template.md`) | Progress file updated after each session |
| 5.3 | Use a worktree for S2; make a deliberate mess; recover with a checkpoint or by discarding the worktree | `git worktree list` shows it; main checkout untouched |
| 5.4 | Run S2 (idempotency store) and S4 (hooks) in parallel worktrees; merge both | No conflicts; tests pass |
| 5.5 | Debug Q12 from a failing reproduction; fix it | `test_ac1_cancelling_twice_restores_stock_once` passes |
| 5.6 | Implement `select_checks` in `tools/precommit.py`; `make install-hooks`; commit a change and watch the hook | Hook runs and blocks a failing commit |
| 5.7 | Investigate `incident/` | Compared with `ANSWERS.md` |
| 5.8 | Everything green | `make test`, `make lint`, `make spec-check`, `make billing-demo` pass |

```bash
git switch -c my-s05 s05-start
cd services/orders && python -m pytest -q tests/test_cancellation_acceptance.py tests/test_idempotency.py
```

## Worktrees in two commands

```bash
git worktree add ../ohb-s2 -b s05-s2      # a second working copy on its own branch
git worktree remove ../ohb-s2             # discard it when merged (or abandoned)
```

## Break it (5 minutes)

Install the hook (`make install-hooks`), change an expected number in any existing test, and try to commit. Read which checks ran and why the commit was blocked. Undo the change.
