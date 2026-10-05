# Delivery metrics: baseline before 2026-04-06, pilot from 2026-04-06

Source: `/tmp/orderhub-history` (256 merged pull requests), `pr_events.csv`, `deploys.csv`. Review times are calendar hours (median / p90). Size excludes generated files. Rework: fix or revert within 21 days; pull requests merged in the last 21 days are not yet eligible. Groups under 20 pull requests are marked ⚠ small.

## Pull requests

| Group | PRs | Per week | Size (median / p90) | Over 300 lines | First review h | Merge h | Rework |
|---|---|---|---|---|---|---|---|
| Baseline, all | 87 | 6.8 | 74 / 165 | 1% (1/87) | 4.5 / 11.1 | 13.1 / 27.6 | 9% (8/87) |
| Pilot, all | 169 | 13.1 | 134 / 294 | 9% (16/169) | 5 / 12 | 16.9 / 31.7 | 14% (18/128) |
| Pilot, agent-assisted (people) | 102 | 7.9 | 170 / 349 | 14% (14/102) | 5 / 12.1 | 17.8 / 38.5 | 17% (13/77) |
| Pilot, not agent-assisted | 54 | 4.2 | 97.5 / 221 | 4% (2/54) | 4.8 / 12 | 14.1 / 22.7 | 12% (5/41) |
| Pilot, bot (dependency bumps) ⚠ small | 13 | 1.0 | 2 / 2 | 0% (0/13) | 5.9 / 7.3 | 14.4 / 35 | 0% (0/10) |

## Same people, before and after

Heavy agent users in the pilot (half or more of their pull requests agent-assisted): ana, ben, chen, eli. Compare each group with itself, not with the other group.

| Group | PRs | Per week | Size (median / p90) | Over 300 lines | First review h | Merge h | Rework |
|---|---|---|---|---|---|---|---|
| Heavy users, baseline | 45 | 3.5 | 63 / 147 | 0% (0/45) | 4.6 / 9.8 | 12.6 / 27.2 | 9% (4/45) |
| Heavy users, pilot | 107 | 8.3 | 150 / 304 | 11% (12/107) | 4.9 / 11.6 | 17.1 / 30.7 | 16% (13/79) |
| Everyone else, baseline | 42 | 3.3 | 88.5 / 180 | 2% (1/42) | 4 / 13.8 | 13.4 / 28.2 | 10% (4/42) |
| Everyone else, pilot | 49 | 3.8 | 108 / 283 | 8% (4/49) | 5.2 / 12.1 | 17 / 31.1 | 13% (5/39) |

## Deployments

Lead time: opened to deployed, hours (median / p90), for pull requests shipped in the period.

| Period | Deployments | Change failure rate | Unplanned (deployment rework) | Lead time h |
|---|---|---|---|---|
| baseline | 23 | 13% | 13% (3/23) | 54 / 125.5 |
| pilot | 36 | 28% | 28% (10/36) | 54.3 / 124.9 |
