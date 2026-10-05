# Incident 5.7: the agent fixed the bug by deleting the check

**System:** OrderHub cancellation, during an L3 session on a different task: "make the mobile app's cancel retries stop failing".

**Symptom:** A week after the change merged, warehouse operations reports that two orders that had already left the warehouse were cancelled by customers, their stock was restored, and the goods were never returned. Finance refunded both.

**Evidence:** `diff.patch` and `pr-summary.md` (composite, for teaching).

What would you check first?
