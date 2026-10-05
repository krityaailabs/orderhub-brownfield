# Capstone rubric (Lecture 15.4)

Score each row 0–3. 0 missing · 1 present but weak · 2 solid · 3 exemplary (evidence a reviewer could check without asking you anything).

| # | Area | 3 looks like | Score |
|---|---|---|---|
| 1 | Framing | Task scored for agent suitability; autonomy level stated per slice; risky parts kept human-led | |
| 2 | Context | AGENTS.md updated; the agent didn't need the same rule twice (or the progress notes say what it needed) | |
| 3 | Spec | Concrete Given/When/Then with numbers; non-goals include redemption and billing; open questions have owners | |
| 4 | Plan | Vertical slices ≤ 300 lines; dependencies explicit; riskiest slice isolated | |
| 5 | Tests | Acceptance tests failed first for the right reason; at least one property or edge test on the points arithmetic; no existing test edited | |
| 6 | Implementation | Integer arithmetic; points credited once even on retries; returns claw back exactly; ledger append-only | |
| 7 | Review | Risk-first notes for each PR; review-flags output answered; one rejected attempt with a reason | |
| 8 | Safety | Security gate green; no new dependency; billing golden check unchanged; permission profile intact | |
| 9 | Measurement | PR sizes, review time, findings by layer, defects after merge; honest about what wasn't measured | |
| 10 | Retrospective | What the agent was good and bad at on this feature; context-file lines added; one thing you'd do differently | |

**Total /30.** 24+ ready to show an employer or a client. 18–23: fix the weakest two rows. Below 18: revisit the sections behind your lowest rows.
