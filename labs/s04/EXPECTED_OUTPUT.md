# Expected output: Lab s04

## At s04-start

`cd services/orders && python -m pytest -q tests/test_returns_acceptance.py` → `10 failed` (each with `NotImplementedError: Lab s04: implement ...`).
`make test-py` → `13 failed, 30 passed` (10 acceptance, 2 property tests for you to write, 1 property test that calls the stub).

## After 4.3 (stubs implemented)

Acceptance tests: `10 passed`.

`python tools/mutate.py --tests tests/test_returns_acceptance.py`
```
SURVIVED  rounding: half-up becomes floor
killed    discount share ignored
SURVIVED  value ignores quantity
killed    partial refund uses the whole order's discount
killed    remainder rule removed
SURVIVED  window boundary: >= becomes >
killed    restock removed
killed    status check accepts PLACED

5 of 8 mutants killed (62%).
```

## After 4.5 (property tests written)

`python tools/mutate.py --tests tests/test_returns_acceptance.py tests/test_returns_properties.py`
```
SURVIVED  rounding: half-up becomes floor
killed    discount share ignored
killed    value ignores quantity
killed    partial refund uses the whole order's discount
killed    remainder rule removed
SURVIVED  window boundary: >= becomes >
killed    restock removed
killed    status check accepts PLACED

6 of 8 mutants killed (75%).
```

## After 4.6 (edge tests added): `make mutate`
```
killed    rounding: half-up becomes floor
killed    discount share ignored
killed    value ignores quantity
killed    partial refund uses the whole order's discount
killed    remainder rule removed
killed    window boundary: >= becomes >
killed    restock removed
killed    status check accepts PLACED

8 of 8 mutants killed (100%).
```

## Solved tag

`make test`: Python `46 passed`; tools `66 passed`; legacy `all checks passed`. `make protect-tests`: `OK: no existing test lines changed since main.`
