# Lab s09 hints

## check_scope / check_budget (9.3)
1. `if not paths: return ["no changes"]`. Then, per path: denied first, then allowed.
2. Budget: check each key only if present: `if "max_files" in budget and len(stats.files) > budget["max_files"]: ...`. Keep the order in the docstring.
3. For cost: if `max_usd` is set and `stats.usd is None`, that's its own problem.

## reviewer-filter.json (9.4)
Look at what the non-actionable comments have in common: severity, category, and repeated text. Try `min_severity`, `drop_categories` and `dedupe` one at a time, and watch `actionable dropped`. One category contains both noise and one real finding per few PRs: don't drop that one.

## choose_bump (9.5)
Compare parsed tuples, not strings. `parse_version("0.16.10") > parse_version("0.16.9")` is True; the strings compare the other way.

## is_duplicate (9.6)
Only open PRs ("awaiting-human", "approved") count. Match on issue, or on a non-empty diff hash.

## The storm (9.6)
`python tools/agent_pipeline/storm.py 40` with your dedup: 1 PR, 39 duplicates. `--as-bot` shows the bot-trigger guard; `--stop-after 5` shows the kill switch.
