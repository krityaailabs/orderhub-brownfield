# The Agentic Delivery Loop (one page)

> Agents make code cheap. They do not make correctness cheap.

| # | Step | The question you answer |
|---|---|---|
| 1 | FRAME | Is this task agent-shaped? Which autonomy level? |
| 2 | CONTEXT | Does the agent know the commands, conventions and boundaries? Are the context files current? |
| 3 | SPEC | Intent, constraints, acceptance criteria, non-goals |
| 4 | PLAN | The agent proposes a plan; a human approves or rejects it |
| 5 | SLICE | Is each unit small enough to finish and to review? |
| 6 | TEST FIRST | Failing acceptance tests that a human owns |
| 7 | IMPLEMENT | The agent loop: scoped, with checkpoints and tests running |
| 8 | VERIFY | Tests, types, lint, security scan, and actually running it |
| 9 | REVIEW | Risk-first human review of the diff |
| 10 | INTEGRATE | Required checks, merge, release |
| 11 | MEASURE | Pull-request size, review time, rework, change failure, cost |
| 12 | LEARN | Update context, commands and specs; a short retrospective |

**Seven mental models**

1. The agent writes the code. You own it.
2. Context is the codebase's API for the agent.
3. The spec is the unit of work, not the prompt.
4. Tests are the contract the agent cannot argue with.
5. Review is the new bottleneck.
6. The agent has your keyboard.
7. Measure outcomes, not keystrokes.
