# The same workflow in three tools (Section 0)

The workflow is identical: test first, fix, verify, review. Only where you type differs. Interfaces change often; check each tool's documentation.

| Step | Claude Code | Cursor | GitHub Copilot |
|---|---|---|---|
| Start | Run `claude` in the repository root (terminal), or use the IDE extension | Open the folder; open the Agent panel | Open the folder in VS Code; open Copilot Chat in agent mode (if your plan includes it) |
| Ask for a failing test first | Paste the first request from quick-win.md | Same request | Same request |
| Approve commands | Approve the test command when asked | Approve the terminal command | Approve the terminal command |
| Ask for the fix | Paste the second request | Same | Same |
| Verify | `make test`, `make lint` in your own terminal | Same | Same |
| Review | `git diff` | Review the diff view, then `git diff` | Review the diff view, then `git diff` |

**No agent?** Write the test and the fix yourself. The tests decide either way.
