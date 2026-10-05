# Expected output: Capstone

## At s15-start
`python tools/capstone_check.py` → `capstone: 0 of 8 checks passed.` (every deliverable missing). `make test`: Python 88 passed; tools `1 failed` (`test_capstone.py`), the rest pass.

## At s15 (reference)
```
capstone: ok     spec
...
capstone: ok     context
capstone: ok     python tests: 103 passed
capstone: ok     billing golden: golden: 52 records identical (javac --release 8)
capstone: ok     security gate: security-gate: 5 of 5 checks passed.
capstone: 11 of 11 checks passed.
```
The reference's acceptance tests, run before any loyalty code existed: 6 failed, 1 passed (AC-7 is a guard).
The rejected S2 attempt (per-return rounding): `test_ac5_...` fails with `assert 2 == 0`.

Your numbers will differ: the check verifies that the evidence exists, the rubric (`rubric.md`) judges its quality.
