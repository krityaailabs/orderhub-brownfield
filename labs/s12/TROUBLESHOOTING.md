# Lab s12 troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `no Git history at /tmp/orderhub-history` | The history hasn't been built | `python labs/s12/build_history.py /tmp/orderhub-history` (or `make metrics`) |
| `git log` error about `trailers` options, or every trailer column empty on the lab history | Git older than about 2.25 doesn't support `%(trailers:key=...,separator=...)` | Upgrade Git; `git --version` |
| Agent-assisted and fixes columns all empty on your own repository | Your commits don't carry the trailers | Agree the convention first (README, "Using your own data"); export labels instead if you can't change commit messages |
| Report numbers differ slightly from EXPECTED_OUTPUT | You changed `REWORK_WINDOW_DAYS`, `GENERATED` or the rollout date | Reset them, compare, then change one thing at a time |
| `cost model refused to run` | A parameter has no value, or a source that doesn't start with `measured:`, `quote:` or `assumption:` | Read the list it prints; fix each line |
| The baseline arm shows a licence cost | A scenario override sits at scenario level instead of under `"agents"` | Move arm-specific overrides into the scenario's `"agents"` section |
| Windows: `make` not found | | Use WSL, or run the commands under each target in the Makefile |
