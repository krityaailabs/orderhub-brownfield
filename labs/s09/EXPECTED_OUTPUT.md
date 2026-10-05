# Expected output: Lab s09

## At s09-start
`make test`: Python 88 passed; tools `20 failed, 157 passed` (guardrails, reviewer filter, dedup and bump, Project 3).
`python tools/agent_pipeline/reviewer_filter.py` → `non-actionable kept per PR 6.0 · actionable kept 20 · actionable dropped 0`.

## At s09
`make test`: Python 88 passed; tools `177 passed`. `make security` 5 of 5.
```
$ python tools/pipeline.py run docs/issues/Q21.md -- python tools/agent_pipeline/fake_agent.py --patch labs/s09/fixtures/q21-fix.patch
{ "status": "pr_opened", "issue": "Q21", "pr": "PR-1", "files": ["services/orders/orderhub/orders.py", "services/orders/tests/test_orders.py"], "changed_lines": 12, ... }
$ python tools/pipeline.py approve PR-1 --by orderhub-agent
{ "status": "refused", "reason": "orderhub-agent is an agent or bot identity and cannot approve" }
$ python tools/pipeline.py approve PR-1 --by "Asha Rao"
{ "status": "approved", "pr": "PR-1", "branch": "agent/pr-1" }
$ python tools/pipeline.py verify-audit
audit: 4 entries, chain intact
```
Storm: `40 triggers -> {"duplicate": 39, "pr_opened": 1}`; `--stop-after 5` → `{"duplicate": 4, "pr_opened": 1, "stopped": 35}`; `--as-bot` → `{"pr_opened": 1, "refused": 39}`.
Reviewer filter (solved config): `non-actionable kept per PR 0.0 · actionable kept 20 · actionable dropped 0`.
