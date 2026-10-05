# Scheduled jobs (Section 9)

| Job | What it does | Trigger | Success | Owner | Stop it |
|---|---|---|---|---|---|
| dep-bump | One patch-level bump in `requirements.lock` per run | weekly (Monday 06:10 UTC) | one changed line; `tools/dep_audit.py`; in CI also install + full tests + golden + security gate | platform team | `python tools/pipeline.py stop` (or the AGENT_PIPELINE_ENABLED repository variable) |

Run locally:
```bash
python tools/pipeline.py run --config ci/jobs/dep-bump.json ci/jobs/dep-bump.issue.md -- python tools/agent_pipeline/jobs/dep_bump.py apply
```
The job inherits every pipeline guardrail (kill switch, bot-trigger guard, dedup, limits, audit, human merge gate) and narrows the scope to the lock file.
