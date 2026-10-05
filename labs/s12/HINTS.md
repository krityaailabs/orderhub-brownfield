# Lab s12 hints

## changed_lines
Sum `added + deleted` over the rows, skipping any path that matches a `GENERATED` pattern with `fnmatch.fnmatch`, and any row where Git reported `-` (binary), which the loader turns into `-1`.

## review_hours
Parse with `_ts`. An empty `first_review_at` means it was merged without review: use the merge time for both. Hours are `(end - opened).total_seconds() / 3600`, rounded to one place.

## change_failure_rate
Count deployments, not pull requests. No deployments means "unknown" (`None`), not 0%: a dashboard that shows 0% for a period with no deployments is lying.

## rework
1. Build `{pr: merged_at}` for the group.
2. Look for fixes and reverts in `all_prs` when it's given (a fix can come from another person, or land after the period ends).
3. A target counts once, however many fixes it had, and only if the fix merged after it and within the window (`<= 21 days`).
4. Eligible = merged at least 21 days before `data_end`. Leave the rest out of both numbers.

## validate and cost_per_merged_pr
Check the parameters in `PARAMETERS` order, then unknown names sorted. A source must *start with* `measured:`, `quote:` or `assumption:`. Sum the unrounded parts for the total; round each part only for display.

## cost-scenarios.json
Take measured values from your `metrics-report.md`: PRs per engineer-month (PRs ÷ engineers ÷ weeks × 4.33) and rework rate for each arm. Review **effort** isn't in the exports (they record waiting time), so it's an assumption: say so. Put arm-specific overrides inside the scenario under the arm's name, so a volume discount doesn't leak into the baseline.
