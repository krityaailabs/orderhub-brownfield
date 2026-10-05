# Troubleshooting: Lab s04

| Symptom | Likely cause | Fix |
|---|---|---|
| `AC-3` gives `[212, 1063, 212]` | The last return used the allocation, not the remainder | When no units remain after this return, refund `total - refunded_minor` |
| `AC-4` passes but the 30-day edge test fails | `>` instead of `>=` at the boundary | Allowed only while now < created_at + 30 days |
| `TypeError: can't compare offset-naive and offset-aware datetimes` | SQLite returns naive datetimes | Treat a naive `created_at` as UTC |
| `AC-5` fails because stock changed | Updates made before all items were validated | Validate everything first, then update |
| Hypothesis reports `FailedHealthCheck` | A function-scoped fixture inside a `@given` test | Create the session inside the test, as the provided helper does |
| `make mutate` says "tests fail on the unmutated code" | Something is still failing | Run `make test-py` and fix that first |
