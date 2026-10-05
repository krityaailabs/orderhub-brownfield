# Section 5: reference answers

## 5.5 Debugging Q12

- **Reproduction:** cancel the same order twice; BAG-TOTE stock goes from 215 to 220 to 225.
- **Hypothesis:** the second cancel restores stock again because `cancel_order` only checks for SHIPPED.
- **Evidence:** the reproduction test fails with 225; reading `cancel_order` confirms there is no CANCELLED check.
- **Fix:** return the order unchanged when it is already CANCELLED. One line, plus the test that proves it.
- **Rejected fixes an agent might offer:** catching the second call in the mobile app (not ours to change); adding a database lock (doesn't address a sequential retry); "re-computing stock from orders" (a redesign, not a fix).

## 5.7 Incident: fixed by deleting the check

- **Hypothesis:** the shipped-order rule was removed to stop the 409.
- **Evidence:** the diff deletes the SHIPPED check; the PR says "simplified so cancel always succeeds"; no test protected the rule at the domain level for the mobile retry case.
- **Root cause:** the task was framed as "stop the error", and a business rule was the error.
- **Mitigation:** revert; contact the two customers; recover stock figures.
- **Permanent fix:** acceptance test AC-4 (shipped orders conflict); review rule "read deletions first"; spec non-goal "never cancel shipped orders"; the client should treat 409 on retry as "already shipped".
- **Detection signal:** diffs that delete `raise` statements or conditions in domain code.
- **Context update:** AGENTS.md boundary: "Never remove a business rule to make an error go away; ask."

## 5.4 Which slices can run in parallel?

S2 (idempotency store) and S4 (hooks) touch disjoint files, so they can run in parallel worktrees. S3 depends on S2. S1 should go first because it fixes the bug and adds the reproduction test both later slices rely on.
