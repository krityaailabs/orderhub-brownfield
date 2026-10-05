# Incident: the runaway pull-request storm (Lecture 9.6)

Composite incident for training. Work it before reading `../ANSWERS.md`.

**Saturday, 07:40.** The on-call engineer wakes to 140 notifications. Between 01:00 and 01:20, the scheduled "flaky-test triage" agent job opened **140 pull requests**, every one titled "Fix flaky test_daily_report_window". CI ran on each of them: about 1,100 runner minutes. The model-usage bill for the night was about 30 times the usual. Nothing was merged (branch protection held).

| File | What it is |
|---|---|
| `job-config.yml` | The job's trigger and settings, as merged three weeks earlier |
| `audit-excerpt.txt` | The first and last few entries of the pipeline log |
| `timeline.md` | What the on-call engineer did, and when |

Write: hypothesis, evidence, root cause (four missing controls), mitigation, permanent fix, detection signal.
