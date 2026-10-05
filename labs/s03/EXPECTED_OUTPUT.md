# Expected output: Lab s03

At the solved tag, `make spec-check`:
```
OK    returns.md + returns.plan.md
```

`make test`: Python `27 passed`; tools `62 passed`; legacy `all checks passed`.

At `s03-start`: `python -m pytest tools/tests -q` shows `18 failed, 44 passed`; `make spec-check` prints `No specs found in docs/specs.` until you add the returns spec, then `Not implemented yet: Lab s03: implement ...` until the stubs are done.

The weak spec (`python tools/spec_check.py labs/s03/weak-spec.md labs/s03/weak-spec.plan.md`) reports eight problems; see `ANSWERS.md`.
