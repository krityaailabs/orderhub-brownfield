# Lab s09 troubleshooting

**`refused: issue is not labelled agent-ok`.** The issue needs a line that starts with `**Labels:**` and lists `agent-ok`.

**`git worktree add` fails.** A previous run may have left a worktree; `git worktree prune`. The pipeline needs a clean `HEAD` commit to branch from.

**A run is `rejected` with `cost not reported`.** Your agent command didn't print a JSON line with `total_cost_usd`. Real headless agents report it with `--output-format json`; the fake agent does unless you pass `--no-cost`.

**`checks-failed` on a change that passes locally.** Checks run in the run's worktree, from `HEAD` plus the agent's change only. Uncommitted local changes aren't there.

**Approval says `patch no longer applies`.** `main` moved since the run. Reject the PR and rerun the issue: that's safer than resolving an agent's conflict by hand.

**The storm test leaves temp folders.** The simulation deletes its temporary repository; if a run was interrupted, delete `storm-*` folders in your temp directory.
