# Lab s12 expected output

## `make metrics` (on the synthetic history)

```
history: 256 merged pull requests, 59 deployments -> /tmp/orderhub-history and labs/s12/data/ (synthetic)
```

| Group | PRs | Per week | Size (median / p90) | Over 300 lines | First review h | Merge h | Rework |
|---|---|---|---|---|---|---|---|
| Baseline, all | 87 | 6.8 | 74 / 165 | 1% (1/87) | 4.5 / 11.1 | 13.1 / 27.6 | 9% (8/87) |
| Pilot, all | 169 | 13.1 | 134 / 294 | 9% (16/169) | 5 / 12 | 16.9 / 31.7 | 14% (18/128) |
| Pilot, agent-assisted (people) | 102 | 7.9 | 170 / 349 | 14% (14/102) | 5 / 12.1 | 17.8 / 38.5 | 17% (13/77) |
| Pilot, not agent-assisted | 54 | 4.2 | 97.5 / 221 | 4% (2/54) | 4.8 / 12 | 14.1 / 22.7 | 12% (5/41) |
| Pilot, bot (dependency bumps) ⚠ small | 13 | 1.0 | 2 / 2 | 0% (0/13) | 5.9 / 7.3 | 14.4 / 35 | 0% (0/10) |

Same people (heavy users: ana, ben, chen, eli):

| Group | PRs | Per week | Size | Over 300 | First review h | Merge h | Rework |
|---|---|---|---|---|---|---|---|
| Heavy users, baseline | 45 | 3.5 | 63 / 147 | 0% (0/45) | 4.6 / 9.8 | 12.6 / 27.2 | 9% (4/45) |
| Heavy users, pilot | 107 | 8.3 | 150 / 304 | 11% (12/107) | 4.9 / 11.6 | 17.1 / 30.7 | 16% (13/79) |
| Everyone else, baseline | 42 | 3.3 | 88.5 / 180 | 2% (1/42) | 4 / 13.8 | 13.4 / 28.2 | 10% (4/42) |
| Everyone else, pilot | 49 | 3.8 | 108 / 283 | 8% (4/49) | 5.2 / 12.1 | 17 / 31.1 | 13% (5/39) |

| Period | Deployments | Change failure rate | Unplanned (deployment rework) | Lead time h |
|---|---|---|---|---|
| baseline | 23 | 13% | 13% (3/23) | 54 / 125.5 |
| pilot | 36 | 28% | 28% (10/36) | 54.3 / 124.9 |

Checks on your implementation:
- Count lock files and the pilot's median size rises from 134 to 152 lines, and the bot's from 2 to 567: one weekly bot PR distorts the picture.
- Drop the 21-day eligibility rule and pilot rework falls from 14% (18/128) to 12% (21/169): recent work looks better only because it hasn't had time to fail.

## `make cost-model` (reference `cost-scenarios.json`)

| Scenario | Arm | Licence | Enablement | Usage | Author | Review | Rework | Total per PR | Per month | Assumptions |
|---|---|---|---|---|---|---|---|---|---|---|
| small | baseline | 0.00 | 0.00 | 0.00 | 2780.00 | 50.00 | 36.00 | **2866.00** | 82,541 | 5 of 10 |
| small | agents | 4.49 | 67.42 | 3.00 | 1120.00 | 100.00 | 68.00 | **1362.91** | 97,039 | 8 of 10 |
| medium | baseline | 0.00 | 0.00 | 0.00 | 2780.00 | 50.00 | 36.00 | **2866.00** | 412,704 | 5 of 10 |
| medium | agents | 4.49 | 44.94 | 3.00 | 1120.00 | 100.00 | 68.00 | **1340.44** | 477,196 | 8 of 10 |
| large | baseline | 0.00 | 0.00 | 0.00 | 2780.00 | 50.00 | 36.00 | **2866.00** | 2,063,520 | 5 of 10 |
| large | agents | 3.60 | 22.47 | 3.00 | 1120.00 | 100.00 | 68.00 | **1317.07** | 2,344,380 | 8 of 10 |

Units are illustrative, not a currency. Your numbers will differ if you chose different assumptions; what must match is that every number has a source and the model refuses to run otherwise.
