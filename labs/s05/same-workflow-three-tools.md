# Section 5 in three tools

| Concern | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|
| Undo inside a session | Checkpoints and rewind | Checkpoints / restore | Undo in the editor; commits |
| Isolated working copy | `git worktree`; subagents with `isolation: worktree` | `git worktree`; background/parallel agents (check your version) | `git worktree`; the cloud agent works on its own branch |
| Specialised helpers | Project subagents in `.claude/agents/*.md` | Custom modes / rules (check your version) | Custom agents in `.github/agents/*.agent.md` |
| Automatic checks after edits | Hooks in `.claude/settings.json` (e.g. `PostToolUse`, exit 2 = feedback) | Hooks in `.cursor/hooks.json` (e.g. `afterFileEdit`; exit 2 blocks) | Git hooks and CI; agent hooks per current docs |
| Always-on safety net | `make install-hooks` (git pre-commit) and CI | Same | Same |

Verified against vendor documentation on 5 October 2026; these features change often.
