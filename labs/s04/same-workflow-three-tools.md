# Section 4 in three tools

| Step | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|
| Run only the slice's tests in the loop | Put the command in the request; allow it without prompting if you trust it | Same; allow the command in the agent's terminal | Same, in agent mode or the cloud agent's instructions |
| Stop editing tests | Boundary in AGENTS.md, plus a hook or `make protect-tests` (Section 5) | Boundary in AGENTS.md, plus `make protect-tests` in CI | Boundary in AGENTS.md, plus `make protect-tests` as a required check |
| Ask for a property-based test | "Write a Hypothesis test that the refunds of a fully returned order sum to its total" | Same | Same |

The tests decide in every tool. Interfaces change; check your version's documentation.
