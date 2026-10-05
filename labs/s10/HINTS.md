# Lab s10 hints

## is_success
`all(result[k] for k in ("applied", "acceptance", "full_suite", "lint", "in_scope"))`.

## summarise
1. Tools in first-appearance order: `dict.fromkeys(r["tool"] for r in results)`.
2. Cost counts every attempted task, not only the successes; cost per success divides that total by the number of successes.
3. Medians over successful tasks only, with `statistics.median`; `None` when there are no successes.
4. The failure reason is the first failing check in the order given; a patch that doesn't apply has every check False, so its reason is "patch did not apply".
