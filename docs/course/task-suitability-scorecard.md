# Task-suitability scorecard (is it agent-shaped?)

Score each criterion 0, 1 or 2. Run `python tools/task_scorecard.py --spec N --verify N --blast N --context N --review N --novelty N` to get the recommendation.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| **Spec clarity** | No acceptance criteria | Some, not testable | Clear, testable criteria |
| **Verifiability** | Nothing can check the result | Partly testable | Tests can decide "done" |
| **Blast radius** | Money, security, data, external contracts | Shared code, reversible with effort | Small, local, easy to revert |
| **Context** | Undocumented, no pattern to copy | Partly documented | Conventions written down or a clear pattern exists |
| **Review cost** | Large diff across many files | Medium | Small diff, quick to review |
| **Familiarity** | New design work | Some novelty | Well-trodden pattern |

| Total | Recommendation |
|---|---|
| 9 to 12 | Agent (L2 to L3) |
| 6 to 8 | Agent with close supervision (L1 to L2) |
| 0 to 5 | Human leads, agent assists (L0 to L1) |

**Caps:** blast radius 0 means at most close supervision; verifiability 0 means human-led until something can check the result.
