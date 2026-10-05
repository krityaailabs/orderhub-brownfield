# Coding-agent tool landscape by surface and autonomy (Lecture 10.1)

Checked 6 October 2026. Products and names change often: re-check before relying on any row. The map is about **surface** (where the agent runs) and **autonomy** (how much it does before a person looks), not about which product is "best".

| Surface | Typical autonomy | Examples (check current names) | Suits | Watch out for |
|---|---|---|---|---|
| Editor completion and chat | L0–L1: suggests, you accept | Copilot in VS Code/JetBrains, Cursor Tab and chat | small edits, learning a codebase | accepting without reading |
| Editor agent mode | L2: multi-file edits, runs commands with approval | Cursor agent, Copilot agent mode, Claude Code in the IDE | slices of a planned change | long sessions drifting (Section 5) |
| Terminal agent | L2–L3: plans, edits, runs tests, commits | Claude Code CLI, other CLI agents | scripted and multi-step work, worktrees | permissions (Section 7) |
| Headless / CI agent | L3–L4: runs unattended in a pipeline | `claude -p`, Claude Code GitHub Action, agent SDKs | toil, issue-to-PR (Section 9) | storms, budgets, scope |
| Cloud / background agent | L3–L4: works on a branch in a hosted environment, opens a PR | Copilot cloud agent, Claude Code on the web, Cursor background agents | parallel hand-offs | workflow approval, secrets, review load |
| Automated reviewer | advisory: comments only | Copilot code review, Code Review for Claude Code, Cursor Bugbot | a fast second reader (Section 6) | noise; never the approver |

**Exercise:** place every tool your team uses (or pays for) in this table. Note overlaps: two tools on the same row with the same autonomy are usually one too many.
