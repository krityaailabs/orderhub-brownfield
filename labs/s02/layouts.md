# Exercise 2.2: which instruction files load?

For each layout, write which files Claude Code (default setting, started at the root), Copilot's cloud agent and Cursor load when working on `legacy/billing/X.java`. Then check your answers with `tools/context_check.py` once you have implemented it (Lab 2.8).

| Layout | Files in the repository |
|---|---|
| A | `AGENTS.md`, `legacy/billing/AGENTS.md` |
| B | `AGENTS.md`, `legacy/billing/AGENTS.md`, `CLAUDE.local.md` (a developer's personal notes) |
| C | `AGENTS.md`, `legacy/billing/AGENTS.md`, `CLAUDE.md` containing only `@AGENTS.md` |
| D | `CLAUDE.md` (all rules), `.github/copilot-instructions.md`, no AGENTS.md |
