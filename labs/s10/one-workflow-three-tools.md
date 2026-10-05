# One workflow, three tools: comparison sheet (Lecture 10.2)

Run the same slice (for example task T2, the customer filter) through the Section 5 workflow in each tool you have: context, spec, plan, slice, tests first, loop, review. Note what changes and what stays the same.

| Step | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|
| Where the context file is read from (AGENTS.md, CLAUDE.md, rules) | | | |
| How you give the spec and plan | | | |
| How the agent runs tests and sees failures | | | |
| How you approve or block commands (permissions) | | | |
| Hooks / automatic checks after edits | | | |
| Checkpoints, undo, worktrees | | | |
| How the change becomes a PR | | | |
| Cost visibility per task | | | |
| What surprised you | | | |

**What stays the same in every tool:** the spec, the held-out tests, the definition of done, the review checklist, the security gate. If any of those changed between tools, your workflow depends on the tool, and that's the first thing to fix.
