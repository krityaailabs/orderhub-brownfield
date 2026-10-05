# Section 1: reference answers

## 1.1 Autonomy ladder

| Item | Level | One control |
|---|---|---|
| 1. Tab completion | L0 | You accept or reject each suggestion; linters and tests on save |
| 2. Paste a stack trace, copy the fix | L1 | You decide what enters the file; reproduce the bug before applying |
| 3. Terminal agent asking before each edit and command | L2 | Approve each edit and command; read every diff |
| 4. Auto-accept in a worktree, stop when tests pass | L3 | Isolated worktree, command allow-list, tests that a human owns, diff review before merge |
| 5. Cloud agent opens a pull request from an issue | L4 | Required checks and a human merge gate; branch protection |
| 6. Nightly agent across every repository | L5 | Policy, budgets, rate limits, sampled review, audit log, kill switch |

The price of each step up: less human attention per change, so more of the safety has to live in tests, permissions and review rules.

## 1.2 Harness labels

A = the model (proposes the next action) · B = context files and instructions (AGENTS.md, CLAUDE.md and similar) · C = the permission check (ask, allow or deny; sandbox rules) · D = the tools (read, search, edit, run, fetch, MCP servers) · E = your repository and machine · F = the tool result, added to the conversation.

**Trust boundary:** draw it around everything the tools can reach (E) and around every tool result coming back (F). Anything read from files, issues, web pages or command output is *input to the model* and may contain text that tries to steer it. The model never executes anything itself; the harness does, under the permissions you set.

## 1.3 Files an agent needs to read for Q3

- `services/orders/orderhub/orders.py` (the writer)
- `services/orders/tests/test_orders.py` (the existing test)
- `legacy/billing/src/com/orderhub/billing/HandoffReader.java` (the **consumer**: it reads columns by position)
- `legacy/billing/src/com/orderhub/billing/OrderRecord.java` and `NightlyBatch.java` (what the batch does with the fields)
- `legacy/billing/docs/RECORD_LAYOUT.txt` (does the email need to reach the finance file?)
- `README.md` or `Makefile` (how to run *all* the checks, including `make billing-demo`)

The key insight: the issue names one Python function, but the contract is shared with a Java program that never mentions Python. The only link between them is a file name pattern, `orders_YYYYMMDD.csv`. An agent finds the consumer only if someone tells it, or if it searches for that pattern.

## 1.4 Failure patterns

| Diff | Pattern | Evidence |
|---|---|---|
| d1 | **Invented API** | `ilike_exact` does not exist on SQLAlchemy columns (checked against the pinned version). The broad `except Exception` hides the error, so the duplicate check silently stops working |
| d2 | **Scope creep** | The one-line fix comes with a rename, a fivefold increase in the list limit and a different default currency. None was requested |
| d3 | **Test tampering** | The test for `SAVE10` (10%) now expects the 12% result (8008 instead of 8190). The code may be right for a new rule, but the test that protected the old one was rewritten to match |
| d4 | **Context loss** | Earlier in the session the agent agreed money stays in integer minor units. This new function returns a float in major units |
| d5 | **Confident wrong fix** | `round()` gives 901 for the reported case, but Python rounds halves to even and works in floats: for 3 minor units at 50% it returns 2, where the rule gives 1 |
| d6 | **Silent deletion** | The test went green because a business rule was deleted: shipped orders can now be cancelled and their stock "restored" |

## 1.5 Transcript: the first wrong turn

**Step 2.** The agent searched only for the function name, so it only found Python files. The first wrong turn is the search, not the edit. Evidence: no search for `orders_`, `handoff` or `csv` across the repository; `legacy/` never opened; acceptance criterion 2 ignored in the final message; `make test` and `make billing-demo` never run.

Applying `q3-wrong-turn.patch` proves it: Python tests pass (27), the Java self-test passes (4 of 4), and the nightly batch fails with `NumberFormatException: For input string: "USD"`. Inserting a column shifted every field after it, and the Java reader reads by position.

A safe change appends the new column at the end (the reader ignores extra columns), adds a test that runs the batch, and asks finance whether the email must reach the fixed-width file at all.

## 1.6 Answer to a manager (example)

"Most developers using these tools believe they're faster, but the best controlled study so far found experienced developers on their own codebases were slower, and later results are uncertain. DORA's research suggests AI amplifies whatever practices a team already has, and it found more AI adoption going with less stable delivery. So the honest answer is: it depends on how we work, and we should measure our own delivery before and after rather than assume."

## Workshop 1.7: reference scores

Computed with `tools/task_scorecard.py`. Order: spec, verify, blast, context, review, novelty. Your scores may differ by a point; the recommendation and the reason matter more.

| # | Item | Scores | Total | Recommendation | Why |
|---|---|---|---|---|---|
| B1 | Fix issue Q1 (case-insensitive email check) | 2 2 2 2 2 2 | 12 | agent (L2-L3) | Clear criteria, easy to test, one function |
| B2 | Add pagination parameters to GET /orders | 2 2 2 1 2 2 | 11 | agent (L2-L3) | Common pattern; API change is additive |
| B3 | Change how VAT is rounded in the legacy billing export | 1 1 0 0 2 1 | 5 | human leads, agent assists (L0-L1) | Money, finance contract, undocumented behaviour |
| B4 | Write characterisation tests for InvoiceCalculator | 1 2 2 1 1 1 | 8 | agent with close supervision (L1-L2) | Read-only for production code; tests are the output |
| B5 | Rename orders.py functions to match the team's naming guide | 2 2 1 2 0 2 | 9 | agent (L2-L3) | Mechanical but touches many files; the diff will be hard to review: slice the task first |
| B6 | Decide whether OrderHub should split billing into its own service | 0 0 1 0 1 0 | 2 | human leads, agent assists (L0-L1) | Architecture decision; nothing to test; nothing can verify the result: add a test or another check first, then re-score |
| B7 | Upgrade SQLAlchemy to the next minor version | 1 2 1 1 1 1 | 7 | agent with close supervision (L1-L2) | Tests exist; release notes needed |
| B8 | Add the customer email to the billing handoff (Q3) | 2 1 0 1 2 1 | 7 | agent with close supervision (L1-L2) | External contract with the Java batch; blast radius is high: a human approves every step |
| B9 | Investigate 'orders sometimes show the wrong total' (no reproduction yet) | 0 0 0 1 1 0 | 2 | human leads, agent assists (L0-L1) | No spec, no reproduction, money; nothing can verify the result: add a test or another check first, then re-score |
| B10 | Add a /health/ready endpoint that checks the database | 2 2 2 1 2 2 | 11 | agent (L2-L3) | Small, testable, well-known pattern |
| B11 | Generate API documentation from the FastAPI schema | 1 1 2 1 2 2 | 9 | agent (L2-L3) | Low risk; output needs a human read |
| B12 | Rotate the database credentials in production | 1 0 0 0 1 1 | 3 | human leads, agent assists (L0-L1) | Security operation; not a code task; nothing can verify the result: add a test or another check first, then re-score |
