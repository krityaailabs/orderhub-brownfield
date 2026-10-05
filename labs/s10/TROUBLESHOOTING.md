# Lab s10 troubleshooting

**`patch did not apply` for your own recording.** Record against the same base the harness uses (`HEAD` of your branch, or pass a base). Generate the patch with `git diff -- services legacy`, not with your editor's export.

**Every task fails `full suite`.** Something in your environment: run `make test-py` on the base first; it must be green before you evaluate anything.

**Your tool passes a task you think is wrong.** Good catch: write it in the review log, and add a held-out test for it, as the reference ADR does for T3. Don't change the result by hand.

**The harness is slow.** Each task runs the full suite in a fresh worktree. Run `--tasks` one at a time while recording; run everything once at the end.
