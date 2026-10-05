# Lab s12 answers

## 12.3 What the metrics report says (synthetic history)

1. **Throughput went up.** 6.8 → 13.1 merged PRs a week; the heavy users went from 3.5 to 8.3 a week as a group.
2. **The changes got bigger.** Median size 74 → 134 lines overall, 170 for agent-assisted PRs; PRs over the 300-line budget went from 1% to 14% of agent-assisted work.
3. **Waiting grew with size.** Time to merge 13.1 → 16.9 hours (median); the p90 for agent-assisted PRs is 38.5 hours. First review barely moved, so that's the wrong tile to watch (D5).
4. **Lead time didn't move.** Opened to deployed: 54 hours median before and after (p90 about 125). This lead time starts when the PR is opened, so it can't show time saved writing the code; what it shows is that once a change exists, it reaches users no sooner: review waits grew and deployments are still twice a week.
5. **Stability got worse.** Rework 9% → 14% overall, 17% for agent-assisted work; change failure rate 13% → 28%; unplanned deployments 3 of 23 → 10 of 36.
6. **Same people, before and after.** The heavy users are ana, ben and chen, who volunteered, plus eli, who didn't but ended up using agents for most pull requests. Heavy users' rework rose 9% → 16%; everyone else's 10% → 13%. Both groups are small enough that the second difference may be noise.

The pattern (individual output up, delivery no faster, stability down, larger batches) is similar in shape to what DORA's 2024 report described at industry level: individual productivity up, delivery throughput and stability slightly down, with larger batches suggested as one explanation. This data was generated to show that shape, so it's an illustration, not more evidence.

What to do next: enforce the size budget (Section 11), slice agent work smaller (Section 5), and watch rework and change failure rate as guardrails in the next phase. Throughput alone would have called this pilot a success.

## 12.4 Cost model

Cost per merged PR roughly halves in every scenario (2,866 → about 1,340 units), but **monthly spend rises about 14–18%**. Both are true. The per-PR figure falls because:
- the author-hours number is an assumption divided by a measured PR count from a **self-selected** group (Lecture 12.5), and
- **a PR isn't the same unit any more**: agent-assisted PRs are about twice as big for the same people (63 → 150 lines median).

Team size barely matters (licence and enablement are small parts); author hours and rework dominate. Before quoting any total, read the "Assumptions" column: 8 of 10 numbers behind the agents arm are assumptions.

## 12.5 Pilot design: the main bias

Self-selection. The pilot group volunteered; they were already enthusiastic and comfortable with change. Comparing them with everyone else measures the people as much as the tools. Fixes: compare each group with its own baseline; better, roll out to teams in a random or staggered order (stepped-wedge) so every team has a before and an after; set the decision rule before you look. Reference: `labs/s12/pilot-design-reference.md` (solved tag).

## 12.6 Five dashboards that lie

| # | Measures | Flaw | Show instead |
|---|---|---|---|
| D1 | Accepted suggestions counted as lines | Activity, not outcome; counts lines later rewritten or deleted; tells you nothing about delivery or quality | Throughput with stability guardrails (rework, change failure rate) for the same people before and after |
| D2 | Merged PRs per week | Includes a new weekly bot PR (1 a week); PRs got about twice as big; says nothing about failures. Throughput without stability | PRs a week next to size, rework and change failure rate, bot work shown separately |
| D3 | Output of volunteers vs non-volunteers | Selection: different people, different work; the group comparison credits the tool with the people | Each group against its own baseline (3.5 → 8.3 vs 3.3 → 3.8 a week), with rework for both |
| D4 | Rework over all PRs, including the last three weeks | Right-censoring: recent PRs haven't had 21 days to need a fix, so pilot rework looks low; and it mixes cohorts | 14% (18/128) with the eligibility rule; 17% for agent-assisted work |
| D5 | Wait for first review | Picked the stage that didn't move; time to merge rose (13.1 → 16.9 h median; p90 38.5 h for agent work) | Opened-to-merged time, median and p90, by cohort |
