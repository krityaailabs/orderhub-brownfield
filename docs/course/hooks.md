# Hooks: running checks automatically while agents work (Section 5)

Three layers, from most portable to most tool-specific. Verified against vendor documentation on 5 October 2026; re-check before use.

| Layer | Where | What it does | Bypass |
|---|---|---|---|
| Git pre-commit hook | `tools/hooks/pre-commit` (install: `make install-hooks`) | Runs `tools/precommit.py` on staged files: lint, the right tests, Java build, context and spec checks, test-tampering guard | `git commit --no-verify` (visible in review) |
| Claude Code hook | `.claude/settings.json`, `PostToolUse` with matcher `Edit|Write` | Runs `tools/hooks/agent_after_edit.py` after each edit; exit code 2 returns the failure to the agent as feedback | Project settings can be changed; review them like code |
| Cursor hook | `.cursor/hooks.json` (`version: 1`, events such as `afterFileEdit`, `beforeShellExecution`) | Same script, with the payload parsing adapted to Cursor's event format; exit code 2 blocks | As above |
| CI | `.github/workflows/ci.yml` | The final, unbypassable layer (Section 7 makes checks required) | None |

The git hook and CI work for every tool and for people. Agent hooks give faster feedback inside the session.
