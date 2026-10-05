# Section 1 exercises: How Coding Agents Actually Work

No repository tag for this section. Everything here works at tag `s00` plus the Section 1 materials.

| Lecture | Exercise | Files |
|---|---|---|
| 1.1 | Place six tools or modes on the L0 to L5 ladder, with one control each | `autonomy-ladder.md` |
| 1.2 | Label the harness diagram; mark the trust boundary | `harness-diagram.md` |
| 1.3 | For issue Q3, list the files you'd expect an agent to need to read | `docs/issues/Q3.md` |
| 1.4 | Match six short diffs to the six failure patterns | `failure-diffs/` |
| 1.5 | Annotate the Q3 transcript with the first wrong turn and the evidence; then prove it | `docs/transcripts/s01/q3-illustrative-session.md`, `q3-wrong-turn.patch` |
| 1.6 | Write a three-sentence answer to a manager: "do agents make teams faster?" | — |
| 1.7 | Score twelve backlog items with the task scorecard | `backlog.md`, `tools/task_scorecard.py` |

Reference answers: `ANSWERS.md`. Try each exercise before you open it.

## Prove the Q3 wrong turn (Lecture 1.5, about 5 minutes)

```bash
git switch -c s01-q3-experiment s00
git apply labs/s01/q3-wrong-turn.patch
make test            # Python and Java both pass
make billing-demo    # the nightly batch fails
git switch -         # back to where you were
git branch -D s01-q3-experiment
```
