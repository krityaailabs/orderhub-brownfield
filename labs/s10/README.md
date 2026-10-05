# Lab s10: an evaluation harness for coding agents on your repository (Section 10)

**Start tag:** `s10-start` · **Solved tag:** `s10` · **Time:** 2–3 hours (plus your own tool runs) · **Agent usage:** the agents are what's being evaluated

Choose tools by measured results on **your** tasks, not by demos or public benchmarks. The harness (`tools/eval_harness/harness.py`) runs five real OrderHub tasks (`tools/eval_harness/tasks/T1`–`T5`, each with held-out acceptance tests) against each tool's recorded changes, and checks: held-out acceptance, the full test suite, lint and scope. It joins each tool's cost and time and your review log, and summarises.

The repository includes **two illustrative recordings** (`labs/s10/recordings/tool-a`, `tool-b`): synthetic patches and metadata, so the harness runs offline. Replace them with your own tools' runs.

At `s10-start`, `tools/tests/test_eval_harness.py` fails: `is_success` and `summarise` are stubs.

| Lecture | Task | Done when |
|---|---|---|
| 10.1 | Place your team's tools on `docs/course/tool-landscape.md` | Table filled; overlaps marked |
| 10.2 | Run one slice through three tools (or follow the recording); fill `one-workflow-three-tools.md` | One-page comparison |
| 10.3 | Estimate cost per task for two models with `docs/course/model-cost-parameters.md` | Sheet filled with today's prices and their date |
| 10.4 | Implement `is_success` and `summarise`; run the harness on both recordings; add one run of your own | `test_eval_harness.py` passes; `labs/s10/results.json` written |
| 10.5 | Write the tool-selection ADR (`docs/adr/0003-...`) from your results | ADR with the trade-off table; compare with the reference |

```bash
git switch -c my-s10 s10-start
python tools/eval_harness/harness.py --tools tool-b --tasks T1,T4     # fails until the stubs are done
```

## Recording your own tool's run (per task)

1. `git worktree add ../eval-T2 s10-start` and give your tool **only** `tools/eval_harness/tasks/T2/task.md` (never the acceptance tests).
2. Let it work with your normal workflow; then `git -C ../eval-T2 diff -- services legacy > labs/s10/recordings/<your-tool>/T2.patch`.
3. Add its minutes, cost and turns to `labs/s10/recordings/<your-tool>/meta.json`; review the patch and add a row to `review-log.csv`.
4. `python tools/eval_harness/harness.py --tools <your-tool>`.
