# Model cost per task: parameters sheet (Lecture 10.3)

Prices change often. Fill in today's prices from each vendor's own pricing page, and write the date. This sheet deliberately contains no prices.

**Cost per task ≈ Σ over turns of (input tokens × input price + output tokens × output price) / 1,000,000**, plus any cache reads/writes your provider bills separately. Agentic tasks re-send context every turn, so input tokens dominate; prompt caching can reduce them a lot.

| Parameter | Model 1 | Model 2 | Where to get it |
|---|---|---|---|
| Input price per million tokens | | | vendor pricing page (date: ____ ) |
| Output price per million tokens | | | vendor pricing page |
| Cached-input price per million tokens | | | vendor pricing page |
| Typical turns per task (your harness) | | | `labs/s10/recordings/*/meta.json` or your own runs |
| Average input tokens per turn | | | the agent's JSON/usage output |
| Average output tokens per turn | | | the agent's JSON/usage output |
| Share of input served from cache | | | usage output |
| **Estimated cost per task** | | | `python tools/eval_harness/cost_per_task.py ...` |
| **Success rate on your tasks** | | | the harness |
| **Cost per successful task** = cost per task ÷ success rate | | | |

Then add the person's time: review minutes per task (from your review log) × your loaded cost per minute, plus rework for failed tasks. The cheapest model per call is often not the cheapest per *successful, reviewed* change.

## Data constraints (answer before comparing prices)

- May this code and its context leave your network? To which providers and regions?
- Is a zero-data-retention option or a cloud provider route (your own cloud account) required?
- Is a local or self-hosted model required for some repositories? What success rate does it reach on your harness?
