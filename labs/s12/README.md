# Lab s12: delivery metrics and cost per merged pull request (Section 12)

**Start tag:** `s12-start` · **Solved tag:** `s12` · **Time:** 2–3 hours · **Agent usage:** optional; the point is the measures, not the code

Measure outcomes, not keystrokes. You'll pull four measures out of Git history and CI/CD exports, split them fairly, and then put a price on a merged pull request without inventing numbers.

**The data is synthetic.** `build_history.py` generates 26 weeks of a fictional eight-person OrderHub team (13 weeks before an agent rollout on 6 April 2026, 13 after), deterministically:

- a Git repository with one squash commit per merged pull request and trailers `PR`, `Author`, `Agent-Assisted`, `Fixes-PR`, `Reverts-PR`;
- `data/pr_events.csv`, the code host's export (opened, first review, merged);
- `data/deploys.csv`, the CD system's export (every deployment, scheduled or unplanned, its outcome and the pull requests it shipped).

The generator's numbers were chosen to make this lab's points visible. They are not findings about any tool. Swap in your own exports when you've done the lab once.

At `s12-start`, `tools/tests/test_delivery_metrics.py` fails: the four measures and the cost model are stubs, and `cost-scenarios.json` has no numbers yet.

| Lecture | Task | Done when |
|---|---|---|
| 12.1 | Fill `docs/course/outcome-metrics.md`: replace three activity metrics your team uses | Three rows with outcome metric, source and owner |
| 12.3 | Implement `changed_lines`, `review_hours`, `change_failure_rate` and `rework` in `tools/metrics/delivery_metrics.py`; run `make metrics` | Metrics tests pass; `labs/s12/metrics-report.md` written |
| 12.4 | Implement `validate` and `cost_per_merged_pr` in `tools/metrics/cost_model.py`; fill `cost-scenarios.json` for small, medium and large teams, every number with a source | `make cost-model` prints the table; cost tests pass |
| 12.5 | Fill `docs/course/pilot-design.md` for your team | Design names its main bias and its decision rule |
| 12.6 | Decide on the five dashboards in `dashboards.md` before reading the answers | Your verdicts written down |

```bash
git switch -c my-s12 s12-start
make metrics            # builds /tmp/orderhub-history, then runs the report (fails until the measures are done)
make cost-model         # refuses to run until every parameter has a value and a source
make test-tools         # includes tools/tests/test_delivery_metrics.py
```

## The four measures

| Measure | Definition used here | Source | Why this one |
|---|---|---|---|
| Size | Added + deleted lines per merged PR, excluding generated files (`*.lock`, `*/generated/*`, ...) and binaries | Git numstat | Review quality falls with size (Section 6); lock files aren't reviewed line by line |
| Review time | Hours from opened to first review, and opened to merged (calendar hours) | Code host export | Waiting is where agent speed disappears |
| Change failure rate | Failed deployments / all deployments | CD export | DORA's stability measure; what users feel |
| Rework | Share of merged PRs fixed or reverted by a later PR within 21 days; PRs merged in the last 21 days aren't eligible yet | Git trailers | Catches the cost that throughput hides |

Everything is reported by period (baseline, pilot), by cohort (agent-assisted or not), and for **the same people before and after**, which is the comparison to trust most.

## Using your own data

1. Export merged PRs with opened, first-review and merged times from your code host into `pr_events.csv` (same columns).
2. Export deployments from your CD system into `deploys.csv`: `kind` is `scheduled` or `unplanned`; `outcome` is `ok` or `failed` (rolled back, hotfixed or caused an incident).
3. Agree a convention for agent-assisted work and for fixes: trailers on the squash commit (`Agent-Assisted: yes`, `Fixes-PR: #123`), or labels you export. Without it, rework and cohorts can't be measured.
4. `python tools/metrics/delivery_metrics.py --repo /path/to/your/repo --rollout YYYY-MM-DD`.
