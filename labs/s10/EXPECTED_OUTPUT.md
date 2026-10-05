# Expected output: Lab s10

## At s10-start
`make test`: Python 88 passed; tools `7 failed, 179 passed` (`test_eval_harness.py`: stubs).

## At s10
`python tools/eval_harness/harness.py` (about 75 seconds: ten worktrees, each with the held-out tests, the full suite and lint):
```
| Tool | Success | Cost (all tasks) | Cost per success | Median review min | Median lines | Failures |
|---|---|---|---|---|---|---|
| tool-a | 5/5 (100%) | $1.59 | $0.32 | 5.0 | 11 | none |
| tool-b | 3/5 (60%) | $0.34 | $0.11 | 2.0 | 4 | T2: acceptance; T4: acceptance |
```
`make test`: tools `186 passed`.
