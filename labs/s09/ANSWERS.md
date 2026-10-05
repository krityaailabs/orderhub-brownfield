# Lab s09 answers

## 9.1 Headless job
`ci/headless-lint-fix.sh`: input = the repository at HEAD; bounded run (`timeout 600`, `--max-turns 15`, allow-listed tools); output = a working-tree change; exit criterion = `make lint`, run by the job itself, not taken from the agent's report. Introduce a lint error, run it: exit 0 after the fix. Make an error the fixer can't fix (for example a line that's too long inside a string): the job exits non-zero.

## 9.2 Q21 with a cloud agent
A good PR changes `list_orders` to compare `status.strip().upper()` and adds one test with three spellings. Review points: does it change anything else (the API's status handling, other filters)? Does the test fail on the old code? Did the agent touch files outside `services/orders`?

## 9.3 Guardrails
Solved `check_scope`/`check_budget` in the tag. The repository limits (`ci/agent-pipeline.json`): allowed `services/orders/**`, `docs/**`; denied `.github/**`, `.claude/**`, every `AGENTS.md`, `requirements.lock`, the pipeline itself, `ci/**`, the golden files and `instructor/**`; budget 8 files, 300 lines, 20 minutes, $3.00; 6 runs an hour; 3 open PRs. An unreported cost with a cost cap is a failure: an unmeasured budget isn't a budget.

## 9.4 Reviewer filter
`{"min_severity": "medium", "drop_categories": ["style"], "dedupe": true}` → 0.0 non-actionable per PR, 20 actionable kept, 0 dropped. `min_severity: medium` with `dedupe` alone gives 0.8 (meets the target). The trap: dropping `docs` removes two real findings (a docstring that misstates the return value).

## 9.5 Dependency bump
With the synthetic snapshot: `fastapi 0.142.2 → 0.142.3`; holding fastapi: `ruff 0.16.10 → 0.16.11` (string comparison would wrongly treat 0.16.9 as newer than 0.16.10). Pre-releases (`2.1.5b1`, `10.0.0rc1`) and post-releases are never chosen; minor bumps (`0.143.0`) are left for a person. The job needs no model at all.

## 9.6 Incident
- **Hypothesis:** the job re-triggered itself through its own PRs' CI runs.
- **Evidence:** `job-config.yml` triggers on every completed CI run, including `pull_request` runs by `orderhub-agent`; the audit shows run_started entries triggered by PR-1's CI.
- **Root cause (four missing controls):** no check of who triggered the run (agents triggered agents); no deduplication (140 PRs for one issue, same diff); no rate or open-PR limit; no kill switch other than disabling the workflow by hand.
- **Mitigation:** disable the workflow; close duplicates; reject PR-1 (it weakened the test).
- **Permanent fix:** trigger only on people's actions or a schedule; dedup on issue and diff hash; max runs per hour and max open PRs; a kill switch an on-call person can flip (`python tools/pipeline.py stop`, or a repository variable checked by the first step); timeouts and a concurrency group.
- **Detection signal:** more than N agent PRs or runs in an hour pages someone; the pipeline's audit log makes it countable.
- Storm simulation with the fixes: 40 triggers → 1 PR, 39 duplicates; `--as-bot` → 1 PR, 39 refused; `--stop-after 5` → 1 PR, 4 duplicates, 35 stopped.

## 9.7 Project 3
`python tools/pipeline.py run docs/issues/Q21.md -- python tools/agent_pipeline/fake_agent.py --patch labs/s09/fixtures/q21-fix.patch` → `pr_opened`, PR-1, 2 files, 12 changed lines, with the real required checks (lint, Python tests, security gate). `approve --by orderhub-agent` → refused. `approve --by "Your Name"` → branch `agent/pr-1`, commit authored by `orderhub-agent` with `Approved-by: Your Name`. `verify-audit` → chain intact; edit any audit line and it reports which entry broke the chain.
