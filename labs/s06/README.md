# Lab s06: review and repair three agent pull requests (Section 6)

**Start tag:** `s06-start` · **Solved tag:** `s06` · **Time:** 2–3 hours · **Agent usage:** optional for the repairs; the reviewing is yours

At `s06-start`, three agent pull requests have been merged exactly as written: **R4** (order lines in `GET /orders`), **R5** (warehouse webhook on cancel) and **R8** (`PATCH /customers/{id}`). Their diffs and summaries are in `prs/`. **CI is green.** That's the point: every problem in this lab passes the tests.

| Lecture | Task | Done when |
|---|---|---|
| 6.1 | Estimate review minutes for R4 (63 lines), R5 (121) and R3 (about 570); set your team's limit | Written answer |
| 6.2 | Review R8 with `docs/course/review-checklist.md`; record each finding | Findings list |
| 6.3 | Triage `prs/R3.diff` in ten minutes: merge, change or split | Decision plus the behaviour-changing lines |
| 6.4 | Count the queries `GET /orders?limit=30` sends (use the `count_queries` fixture); fix the N+1 and restore a bound on `limit` | Your query-count test fails before the fix and passes after |
| 6.5 | Find the non-existent method and the duplicate dependency in R5; fix both | Your notifier test (with `httpx.MockTransport`) fails before and passes after |
| 6.6 | Review `prs/R6.diff` yourself, then compare with the automated comments in `prs/R6.md` | Comparison written |
| 6.7 | Decide on the ten PRs in `pr-gallery.md` | Score against `ANSWERS.md` |
| 6.8 | Repair R4, R5 and R8; each fix has a regression test that failed before it | `make test`, `make lint` pass; your new tests fail on `s06-start` |

```bash
git switch -c my-s06 s06-start
make review-flags DIFF=labs/s06/prs/R5.diff
cd services/orders && python -m pytest -q          # green: the problems pass CI
```

## Review each pull request as a branch

Every agent PR is also a real branch, so you can review it the way you would on your code host: check it out, read the diff against its base, run the tests and the review flags. Each branch is one commit by `OrderHub Agent` on top of `review/base` (OrderHub just before the PRs).

| Branch | PR | At `s06-start` |
|---|---|---|
| `pr/R3-tidy-up` | R3: formatting and type hints (about 570 lines) | Not merged (Lecture 6.3 triage) |
| `pr/R4-order-lines` | R4: order lines in `GET /orders` | Merged as written |
| `pr/R5-warehouse-webhook` | R5: warehouse webhook on cancel | Merged as written |
| `pr/R6-daily-sales-report` | R6: daily sales report endpoint | Not merged (Lecture 6.6 exercise) |
| `pr/R8-customer-name` | R8: `PATCH /customers/{id}` | Merged as written |

```bash
git fetch origin 'refs/heads/pr/*:refs/remotes/origin/pr/*' 'refs/heads/review/*:refs/remotes/origin/review/*'   # if your clone didn't fetch them
git branch review/base origin/review/base        # once: a local name for the base (skip if it already exists)
git switch pr/R5-warehouse-webhook               # creates the local branch from origin/pr/... the first time
git log -1                                        # the PR description
git diff review/base...HEAD                       # the PR, exactly as a code host shows it
make review-flags BASE=review/base                # same flags as on prs/R5.diff
cd services/orders && python -m pytest -q         # green on every PR branch
git switch my-s06                                 # back to your repair branch
```

Merging `pr/R4-order-lines`, `pr/R5-warehouse-webhook` and `pr/R8-customer-name` into `review/base` gives exactly the code at `s06-start`. Do your repairs on a branch from `s06-start`, as above, not on the PR branches.

No Git history (you downloaded a zip)? The same changes are in `prs/*.diff`; everything in this lab works from those files.

## Rules for the repairs

1. **Test first.** Write the regression test, run it on the unrepaired code, and see it fail for the right reason. Then fix.
2. **Repair, don't revert.** Each PR's task was legitimate. Keep what was asked for; remove or fix what wasn't.
3. **Don't edit the agent's tests to make your fix pass** unless the test itself is the problem; if so, say why in your commit message.
4. **No new dependencies** (ADR 0002). Everything you need is already in `requirements.lock`.

## Break it (5 minutes)

Run `make review-flags DIFF=labs/s06/prs/R8.diff`. It flags the API surface but not the missing email validation. Write one sentence on why no pattern-based tool would catch that, and what in the checklist does.
