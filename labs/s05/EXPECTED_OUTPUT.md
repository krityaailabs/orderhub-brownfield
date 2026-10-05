# Expected output: Lab s05

## At s05-start

`cd services/orders && python -m pytest -q tests/test_cancellation_acceptance.py tests/test_idempotency.py` → `11 failed, 1 passed`.
AC-1 fails with `assert 225 == 220`: the Q12 bug (the second cancel restores 5 more units).

## At s05

`make test`: Python `58 passed`; tools `73 passed`; legacy `all checks passed`. `make spec-check` lists `cancellation.md` and `returns.md` as OK.

## The pre-commit hook blocking a changed test (after `make install-hooks`)

```
precommit: ok     lint
precommit: FAILED python-tests
    E       assert 4095 == 4096
    1 failed, 44 passed
precommit: FAILED protect-tests
    BLOCKED: 1 existing test line(s) changed since origin/main without approval:
      services/orders/tests/test_returns_acceptance.py: - assert ret(...)["refund_minor"] == 4095
precommit: 2 check(s) failed: python-tests, protect-tests
```

## Worktrees

```
$ git worktree add ../ohb-s2 -b s05-s2
$ git worktree list
/path/to/orderhub-brownfield  <commit> [my-s05]
/path/to/ohb-s2               <commit> [s05-s2]
```
