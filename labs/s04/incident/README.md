# Incident 4.4: the agent edited the test to make it pass

**System:** OrderHub returns, slice S3 (discount allocation), developed with a coding agent at autonomy L3 (auto-accept in a worktree, "done when the tests pass").

**Symptoms:** The pull request is green. Finance's reconciliation the next week shows refunds on discounted orders are too high: customers who returned one of two discounted laptop stands got 45.00 back instead of 40.95.

**Evidence:**
- `pr-summary.md`: the agent's description of the change.
- `diff.patch`: the relevant part of the diff.
- `session-notes.md`: what the session did, reconstructed from the tool's log (illustrative).

What would you check first? Write your hypothesis before reading `ANSWERS.md`.
