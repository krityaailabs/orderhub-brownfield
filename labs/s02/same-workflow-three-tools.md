# Section 2 in three tools

| Concern | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|
| Shared file it reads | `AGENTS.md` when no CLAUDE.md, .claude/CLAUDE.md or CLAUDE.local.md exists in the start folder or above (default setting); or import it with `@AGENTS.md` from a CLAUDE.md | `AGENTS.md`, including nested files (more specific wins) | `AGENTS.md` on the cloud agent, code review, VS Code and CLI; not GitHub.com chat |
| Tool-specific file | `CLAUDE.md`, `.claude/rules/*.md` (path-scoped) | `.cursor/rules/*.mdc` (alwaysApply or globs) | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md` (applyTo) |
| How to check what loaded | It reports the AGENTS.md it loaded at session start; ask it to list its instructions | Rules panel; ask the agent which rules apply | Check the references shown in the response; ask which instructions it used |
| Personal preferences | `~/.claude/CLAUDE.md` (does not stop AGENTS.md loading) | User rules | Personal instructions in your settings |

Verified against vendor documentation on 5 October 2026. Interfaces change: check before recording or teaching.
