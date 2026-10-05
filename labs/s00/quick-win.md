# Quick win: a tested fix with a coding agent (Lecture 0.3) and your exercise (Q1)

## What the lecture shows (issue Q0)

1. Read `docs/issues/Q0.md`.
2. **Test first.** Ask the agent to write a test that reproduces the issue, and to run it. You should see it fail. Do not let it touch the code yet.
3. **Fix.** Ask the agent to make the test pass without changing any other test.
4. **Verify.** Run `make test` and `make lint` yourself.
5. **Review.** Read the diff. Did it change only what the issue asked? Did it edit any existing test?

Example request (any tool):

> Read docs/issues/Q0.md. First add a test in services/orders/tests that reproduces the bug and run it to show it fails. Do not change any application code yet.

Then:

> Now fix the bug so the new test passes. Do not modify existing tests. Run the whole Python test suite and show me the result.

## Your exercise: issue Q1

Repeat the same four steps for `docs/issues/Q1.md`: test first, fix, verify, review. Use any agent, or none.

### Hint ladder (open one at a time)

<details><summary>Hint 1</summary>Look at how create_customer checks for an existing customer.</details>
<details><summary>Hint 2</summary>The comparison is case-sensitive. SQL has a function to compare without case.</details>
<details><summary>Hint 3</summary>Compare the lower-cased stored email with the lower-cased input. Your test should post an existing email with different capitals and expect 409.</details>

### Review checklist for the agent's change

- [ ] A new test fails before the fix and passes after it
- [ ] No existing test was edited or deleted
- [ ] The change is limited to the customer check
- [ ] `make test` and `make lint` pass
