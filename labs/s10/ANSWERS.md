# Lab s10 answers

## 10.4 Harness results on the two illustrative recordings

| Tool | Success | Cost (all tasks) | Cost per success | Median review min | Median lines | Failures |
|---|---|---|---|---|---|---|
| tool-a | 5/5 (100%) | $1.59 | $0.32 | 5.0 | 11 | none |
| tool-b | 3/5 (60%) | $0.34 | $0.11 | 2.0 | 4 | T2: acceptance; T4: acceptance |

What the table doesn't show on its own:
- **Tool B's T3 passed every check and is still wrong** (review log): it merges quantities before validating them. The held-out tests didn't cover it. Harness success is necessary, not sufficient; the review log is part of the evaluation.
- **Tool A's T3 took 14 review minutes** because it renamed every variable in `place_order` unasked. Correct, but expensive to review.
- **Cost per success favours B; cost per merged change favours A** once rework and review time are counted (see the reference ADR).

## 10.5 ADR
Reference: `docs/adr/0003-coding-agent-selection.md`. A good ADR states the constraints checked first (data, permissions, context file), the evidence table, the decision in one sentence, the consequences including the sample-size caveat, and a re-evaluation date.

## 10.3 Cost sheet
Use `python tools/eval_harness/cost_per_task.py` with today's prices. The common mistake is comparing price per token: compare cost per **successful, reviewed** task, and include cache pricing (agents re-send context each turn).
