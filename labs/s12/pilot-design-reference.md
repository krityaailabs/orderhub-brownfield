# Pilot design: reference (OrderHub, illustrative)

This is the design the OrderHub team *should* have used. The lab's history shows what happened with a volunteer pilot instead.

| Part | Reference design |
|---|---|
| **Question** | Should all three OrderHub teams adopt the coding agent chosen in ADR 0003 for feature slices, with the team kit and policy from Section 11? |
| **Teams and people** | All three teams (24 engineers). No individuals are singled out; results are reported per team. |
| **Assignment** | Stepped (stepped-wedge): team order drawn at random; team 1 starts in week 1, team 2 in week 5, team 3 in week 9. Every team has its own before and after, and in each period some teams haven't started, so seasonal effects show up in both. |
| **Baseline** | 13 weeks of history before week 1 for every team, from the Lab s12 scripts. |
| **Primary measure** | Lead time for changes, median and p90 per team. DORA measures commit to production; the Lab s12 report measures opened to deployed, which is close enough if it's measured the same way before and after. |
| **Guardrails** | Rework (21-day fix or revert) and change failure rate. Pause a team's rollout if either is more than 5 points above that team's baseline for 3 consecutive weeks; review before continuing. Also watched: PRs over the 300-line budget. |
| **Duration and size** | 16 weeks; about 40–60 merged PRs per team per period. Enough to see large changes in lead time; rework and failure rates need the full period, and small changes won't be distinguishable from noise. Say so in the results. |
| **Enablement** | The same half-day session, kit and policy for every team, in the week the team starts; one champion per team with 10% of their time set aside. |
| **Things that could fool us** | Novelty (early enthusiasm fades; look at the last 4 weeks separately). Seasonality (the spring release; the stepped design covers it). Other changes (a CI speed-up in week 6 would help everyone; log every process change). Gaming (people know PR counts are watched; we don't report per person). |
| **Main bias and how the design handles it** | Self-selection, the bias that ruined the first pilot. Handled by including everyone, randomising team order, and comparing each team with itself. |
| **Decision rule** | Expand if lead time improves for at least two of three teams **and** no guardrail is breached at the end. Change and retry (smaller slices, stricter size budget) if lead time improves but a guardrail is breached. Stop if lead time doesn't improve for any team. |
| **What we'll publish** | A one-page result to engineering and leadership with the measures, the assumptions in the cost model and the caveats, whatever the outcome. |
