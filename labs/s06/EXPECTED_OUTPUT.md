# Expected output: Lab s06

## At s06-start

`make test`: Python `63 passed`; tools `85 passed`; legacy `all checks passed`. Everything is green: the problems pass CI.

`make review-flags DIFF=labs/s06/prs/R5.diff`:
```
MOCK-IN-TEST  services/orders/tests/test_notify.py: monkeypatch.setattr(notify, "order_cancelled", lambda *args: recorded.append(args))
DEPENDENCY    requirements.lock: +requests
DUPLICATE-DEP requirements.lock: requests added; HTTP client already provided by httpx, httpx2
review-flags: 3 flag(s). Flags say where to read first, not whether to merge.
```

`make review-flags DIFF=labs/s06/prs/R4.diff`:
```
DELETED-CHECK services/orders/orderhub/api.py: return orders.list_orders(session, status=status, limit=min(limit, 200))
```

Query count for `GET /orders?limit=30` with 30 two-line orders: `34` at s06-start.

## At s06

`make test`: Python `69 passed`; tools `85 passed`; legacy `all checks passed`. Query count: `3`.
Your regression tests, run against s06-start code: 8 failed (for example `AssertionError: 34 queries`, `TypeError: order_cancelled() got an unexpected keyword argument 'transport'`, `assert 200 == 422`).
