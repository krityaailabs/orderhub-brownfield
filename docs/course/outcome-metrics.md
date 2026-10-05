# Outcome metrics worksheet (Lecture 12.1)

Activity metrics count what people and tools do. Outcome metrics count what users and the business get. Replace three activity metrics your team watches with outcome metrics; give each a source and an owner.

| Activity metric (what's counted now) | Why it misleads | Outcome metric instead | Source | Owner |
|---|---|---|---|---|
| Lines of code, or "% written by AI" | More code is more to review and maintain; rewards size | Lead time for changes (commit to production) | CD system, Git | |
| Accepted suggestions / acceptance rate | Measures clicks; accepted code may be rewritten next day | Rework rate (PRs fixed or reverted within 21 days) | Git trailers or labels | |
| Pull requests opened or merged per person | Splits and inflates; ignores failures; invites gaming | Merged PRs per week **with** change failure rate and rework beside it | Code host, CD | |
| Hours "saved" from a survey | Self-report; people overestimate speed-ups (METR, 2025) | Time to merge (median, p90) and lead time | Code host, CD | |
| Number of agent sessions or prompts | Usage, not value | Cost per merged PR with its assumptions listed (Lab s12) | Billing export, metrics report | |
| | | | | |
| | | | | |
| | | | | |

Rules of thumb:
1. Pair every speed metric with a stability metric (throughput with change failure rate and rework).
2. Report median and p90, and the group size; mark small groups.
3. Compare the same people or teams before and after, not users against non-users.
4. Never use these metrics to rate individuals: they're for the system of work. Once they're used for performance reviews, they stop measuring anything.
