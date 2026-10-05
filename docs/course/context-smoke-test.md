# Context smoke test: three tools (manual part of Lab 2.8)

`make context-check` checks the files. This checks what your agent actually believes. Start a fresh session in the repository root for each tool you use, and ask exactly these four questions. Record the answers.

1. "What command runs all the tests in this repository?"   Expected: `make test`
2. "How is money represented in this codebase?"             Expected: integer minor units, never floats
3. "Can you add a column to the billing handoff CSV?"       Expected: not without finance's agreement; the Java batch reads it by position (appending is the only safe option, and needs agreement)
4. "Which instruction files did you read?"                  Expected: AGENTS.md (and legacy/billing/AGENTS.md once working there)

| Tool and version | Q1 | Q2 | Q3 | Q4 | Date |
|---|---|---|---|---|---|
| | | | | | |

If an answer is wrong, fix the context file, not the question. Run it again after any change to AGENTS.md.
