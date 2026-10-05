# Section 2: reference answers

## 2.1 Context, code or neither

| # | Where | Why |
|---|---|---|
| 1 | Context | Agents guess commands; give the exact one |
| 2 | Code | Visible from imports and dependencies |
| 3 | Context (and an ADR) | A rule, not something the code proves; old code still breaks it |
| 4 | Context (nested, legacy/billing) | An implicit contract nothing in Python reveals |
| 5 | Code | Readable in `place_order`, and covered by a test |
| 6 | Context (nested, legacy/billing) | Explains why the format is a contract; not in code |
| 7 | **Neither** | Secrets never go in context files or prompts |
| 8 | Context | Avoids guessing; one line |
| 9 | Context | A working rule the agent must follow |
| 10 | Neither | Irrelevant to the work, and personal |
| 11 | Context (nested) | The documentation is wrong; the agent would otherwise trust it |
| 12 | Code | Discoverable by search |
| 13 | Context (nested) | Not enforced anywhere visible; an agent will use modern Java |
| 14 | Context | A convention with an example |
| 15 | **Neither** | Real personal data never goes to an agent |
| 16 | Context (short) | A convention; the code shows it, but a pointer saves exploration |
| 17 | Code | In the lock file; repeating it creates drift |
| 18 | Context (nested, and an ADR later) | Undocumented business rule with an approval requirement |
| 19 | Neither | Changes every fortnight; goes in the spec for a task, not in context |
| 20 | Context | A boundary |

Rule of thumb: context is for what the agent cannot reliably discover and must not get wrong. Repeating what the code already says creates drift.

## 2.2 Which instruction files load? (working on `legacy/billing/X.java`)

Computed with `tools/context_check.py` (documented rules, verified 5 October 2026).

| Layout | Claude Code (default, started at root) | Copilot cloud agent | Cursor |
|---|---|---|---|
| A | AGENTS.md, legacy/billing/AGENTS.md | AGENTS.md, legacy/billing/AGENTS.md | AGENTS.md, legacy/billing/AGENTS.md |
| B | CLAUDE.local.md | AGENTS.md, legacy/billing/AGENTS.md | AGENTS.md, legacy/billing/AGENTS.md |
| C | CLAUDE.md, AGENTS.md | AGENTS.md, legacy/billing/AGENTS.md, CLAUDE.md | AGENTS.md, legacy/billing/AGENTS.md |
| D | CLAUDE.md | .github/copilot-instructions.md, CLAUDE.md | none |

Notes. **B** is the trap: a personal `CLAUDE.local.md` switches off every AGENTS.md for that developer's Claude Code sessions. **C** keeps the root rules through the import, but loses the nested billing rules for Claude Code unless you also import them or add `legacy/billing/CLAUDE.md`. **D** works for Claude Code and Copilot's cloud agent, and gives Cursor nothing.

## 2.6 Continue, compact or restart?

1. **Restart** (with a short summary). The session is long, it has already broken a context rule, and it has read sixty files. Start fresh for the third slice with the spec, the plan and a two-line summary of what's done.
2. **Continue.** Early, focused, nothing to lose.
3. **Restart.** Unrelated task; old context is actively misleading the plans.

## 2.7 Review: five context files that make agents worse

| File | Problem | Fix |
|---|---|---|
| cf1 | Vague rules with no examples ("follow best practices", "be careful with money") give the agent nothing to act on | Concrete, checkable rules with a good and a bad example |
| cf2 | A command that doesn't exist (`make check-style`) and a contradiction (integer money, but floats in the API) | Run `make context-check`; resolve the contradiction (format at the edge with `format_money`) |
| cf3 | A 640-line novel: history and copied API docs crowd out the rules and go stale | Keep it short; move detail to docs and nested files; link to them |
| cf4 | A real-looking password in a command | Remove it, rotate the credential, use environment variables or a secrets manager; scan context files for secrets |
| cf5 | A personal `CLAUDE.local.md` silently stopped Claude Code reading the team's AGENTS.md, so the handoff rule was never loaded | Put personal preferences in `~/.claude/CLAUDE.md` (doesn't block AGENTS.md), or set Project instructions to `claude-md-and-agents-md`; add `CLAUDE.local.md` to `.gitignore` with a comment; `make context-check` warns about it |
