# Timeline (on-call engineer)

- 07:40 Paged by notification volume. 140 open PRs from orderhub-agent.
- 07:44 Disabled the workflow in the repository settings (the only stop available).
- 07:52 Closed 139 PRs with a script; kept PR-1 for review. Every PR changed the same line of the same test.
- 08:10 Found the trigger: `workflow_run` on every completed CI run, including runs on the agent's own PRs.
- 08:30 The test is flaky because it builds "now" from the wall clock near midnight UTC. PR-1 widened the test's time window instead of fixing the clock, the same pattern as R2 in Section 6. Rejected.
