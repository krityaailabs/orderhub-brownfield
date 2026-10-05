# Review checklist for agent pull requests

Use it in this order: risk first, then correctness, then the rest. Stop and send the PR back as soon as a section fails; don't keep reading a PR you're going to reject.

Run `make review-flags` (or `python tools/review_flags.py --diff FILE`) first. It tells you where to look, not whether to merge.

## 0. Before you read the code (1 minute)

- [ ] **Size.** Over the review budget (300 changed lines, tests included)? Ask for a split, or read risk-first and say so in the review.
- [ ] **Task vs summary.** Read the issue or slice first, then the PR summary. Does the summary describe the task, and only the task?
- [ ] **Files.** Do the changed files match the plan's declared files? Any file outside the list is a question.

## 1. Risk (read these lines first)

- [ ] **Deleted lines in domain code.** Every removed condition, `raise`, bound (`min`/`max`/`limit`), validator or check: what did it prevent, and who decided that no longer matters?
- [ ] **Tests.** Any changed or deleted lines in existing tests? (Treat as a business-rule change; needs `[test-change-approved]` and a named human.)
- [ ] **Mocks.** Does a new test patch out the code under review? If the only test mocks the new behaviour, the behaviour is untested.
- [ ] **Dependencies.** Any new package? Is it needed, does it exist, is it maintained, does it duplicate one we have (ADR 0002)?
- [ ] **Contracts.** API routes and schemas (what clients can now send or receive), the billing handoff, the legacy billing code.
- [ ] **Money, stock, permissions.** Integer minor units (ADR 0001); stock changes happen once; nobody can change what they shouldn't.

## 2. Correctness

- [ ] Each acceptance criterion maps to a test that failed before the change.
- [ ] Edge cases: empty, zero, one, maximum, duplicate, retry, already-done.
- [ ] Every external call: what happens when it fails, times out or is retried? Does a failure there undo, or wrongly fail, our own committed work?
- [ ] Every API call and method used actually exists in the pinned version (check the library, not the agent's word).

## 3. Performance

- [ ] Loops that touch the database or the network: how many queries or calls for 1 item, for 100? (Use `count_queries` in tests.)
- [ ] Every list or query has a bound. "Return everything" is a decision, not a convenience.
- [ ] No file or connection opened per item when one would do (chatty I/O).

## 4. The rest

- [ ] Names, structure and comments are clear to a reader who wasn't in the session.
- [ ] The progress file and PR summary record decisions made during implementation.
- [ ] Anything the agent needed telling twice is proposed as a line for AGENTS.md.

## Outcome

Merge · Change (list the specific changes) · Split (name the slices) · Reject (say why, and what the task needs first).
