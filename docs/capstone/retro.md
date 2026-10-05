# Capstone retrospective (reference)

## What went well

- Writing all seven acceptance tests before any code made the plan's mistake visible at once: nothing could pass until the endpoint existed.
- AC-5 (a full return over several returns) caught the rejected attempt that AC-4 alone would have passed. Specifying the sum, not just one example, was the most valuable line in the spec.
- Reusing the Section 4 property-test strategies made the clawback property tests a 30-line job.
- The billing golden check and the security gate gave a one-command answer to finance's only requirement.

## What didn't

- The plan's slice order was wrong (endpoint last). The fix was cheap here; on a bigger feature it would have meant a slice with no passing criterion. Next time: ask "how will the first slice's tests observe the behaviour?" while planning.
- The first clawback passed the single-example criterion (AC-4) by coincidence. Without AC-5, it would have merged.
- Times weren't measured. For a real team, that's the first metric to add.

## Context-file lines

- Loyalty points are an append-only ledger; add earn and clawback entries in the same transaction as the ship or return; never update or delete entries.
- Points never touch the billing handoff; redemption is out of scope until finance agrees.

## One thing I'd do differently

Write the property test for the clawback sum before the first implementation, not after the rejected attempt. The spec already said "exactly"; a property is the natural test for "exactly".
