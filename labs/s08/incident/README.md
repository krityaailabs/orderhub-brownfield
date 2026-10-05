# Incident: the modernised service broke the nightly batch (Lecture 8.7)

Composite incident for training. Evidence is in this folder. Work it before reading `../ANSWERS.md`.

**Tuesday, 04:10.** The finance system rejects `BILL20260309.DAT` (business day 9 March). The nightly batch at 02:00 reported success. On Monday afternoon, a first attempt at the tax strangler (written with an agent, reviewed, merged) was switched on for JP and AU.

| File | What it is |
|---|---|
| `pr-summary.md` | The pull request description for the first attempt |
| `diff-excerpt.patch` | The two parts of the diff that matter |
| `compare-run.txt` | The comparison run attached to the pull request |
| `batch-output.txt` | The 02:00 batch log |
| `finance-rejection.txt` | The message from the finance system |
| `ops-rerun.txt` | What the on-call engineer found by rerunning the legacy path |

Write: hypothesis, evidence, root cause (there are three contributing causes), mitigation, permanent fix, detection signal.
