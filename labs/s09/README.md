# Lab s09 / Project 3: an issue-to-PR pipeline with a human merge gate (Section 9)

**Start tag:** `s09-start` · **Solved tag:** `s09` · **Time:** 4–6 hours (Project 3, advanced) · **Agent usage:** recommended

Wave 2. This lab branches from `s08` (it doesn't contain the capstone).

The pipeline (`tools/agent_pipeline/`, CLI `tools/pipeline.py`) runs an agent on one labelled issue, in a fresh git worktree, and only opens a PR record if the change stays in scope, within budget and passes the required checks. A person approves; an agent identity never can. Every decision goes into a hash-chained audit log. The agent is any command: a real headless agent, or `fake_agent.py`, which makes scripted changes so everything runs offline.

At `s09-start`, these fail on purpose:
- `tools/tests/test_guardrails.py`: `check_scope`, `check_budget` are stubs (9.3)
- `tools/tests/test_reviewer_filter.py`: `ci/reviewer-filter.json` lets every comment through (9.4)
- `tools/tests/test_dedup_and_bump.py`: `choose_bump` (9.5) and `is_duplicate` (9.6) are stubs
- `tools/tests/test_pipeline_project3.py`: the Project 3 acceptance tests (need all of the above)

| Lecture | Task | Done when |
|---|---|---|
| 9.1 | Run `ci/headless-lint-fix.sh`: a headless job with inputs, a bounded run, and its own exit check | It exits 0 when lint passes and non-zero when it doesn't |
| 9.2 | Assign issue **Q21** (`docs/issues/Q21.md`) to a cloud agent, or follow the recording; review its PR | Review notes written |
| 9.3 | Implement `check_scope` and `check_budget`; review the limits in `ci/agent-pipeline.json` | `test_guardrails.py` passes |
| 9.4 | Tune `ci/reviewer-filter.json` | `python tools/agent_pipeline/reviewer_filter.py`: < 1 non-actionable per PR, 0 actionable dropped |
| 9.5 | Implement `choose_bump` | `test_dedup_and_bump.py -k bump` passes |
| 9.6 | Investigate `incident/`; implement `is_duplicate`; run the storm with the kill switch | `python tools/agent_pipeline/storm.py 40 --stop-after 5` stops 35 runs |
| 9.7 | Project 3: run Q21 end to end, approve as yourself, verify the audit log | `test_pipeline_project3.py` passes; `python tools/pipeline.py verify-audit` → chain intact |

## Run Q21 end to end (after the stubs are done)

```bash
python tools/pipeline.py run docs/issues/Q21.md -- \
  python tools/agent_pipeline/fake_agent.py --patch labs/s09/fixtures/q21-fix.patch
python tools/pipeline.py status
python tools/pipeline.py approve PR-1 --by "orderhub-agent"     # refused: agents can't approve
python tools/pipeline.py approve PR-1 --by "Your Name"          # branch agent/pr-1, ready to merge
python tools/pipeline.py verify-audit
```

With Claude Code installed and an API key set, replace the fake agent with a real one, for example:
`claude --bare -p "$(cat docs/issues/Q21.md) Follow AGENTS.md. Tests first." --max-turns 20 --output-format json --allowedTools "Read,Edit,Bash(make test-py),Bash(make lint)"`.

## Rules

1. The pipeline's own code and config (`tools/agent_pipeline/**`, `ci/**`) are denied to the agent. Changes to them are made by people and reviewed.
2. A run that fails a guardrail or a check opens nothing. There is no "open it anyway" flag, on purpose.
3. Approval needs a named person who isn't an agent or bot identity.
