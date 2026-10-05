# Lab s06 hints

## R4: N+1 and the unbounded list (6.4)
1. Write the test first: place 30 orders, then `with count_queries() as statements: client.get("/orders", params={"limit": 30})`, and assert a small constant (say `<= 5`). Print `len(statements)` the first time: it's 30-something.
2. Load what the loop touches up front: `joinedload(Order.customer)`, `selectinload(Order.lines).selectinload(OrderLine.product)` in `.options(...)`.
3. For the bound, let FastAPI validate it: `limit: int = Query(50, ge=1, le=200)`. Then `limit=0` and `limit=201` are 422, and the domain function always applies `.limit(limit)`.
4. Keep `lines` in the output: that part was asked for.

## R5: invented API and duplicate dependency (6.5)
1. Check the claim: `python -c "import inspect, requests; print(inspect.signature(requests.Session.request))"`. There is no `retries`.
2. We already have an HTTP client: `httpx`. Retries live on the transport: `httpx.HTTPTransport(retries=3)`.
3. Give `order_cancelled` a `transport=None` parameter so tests can pass `httpx.MockTransport(handler)`; return `True` on 2xx and `False` on an HTTP error or a non-2xx, without raising.
4. In the API, notify only when the order actually changed to CANCELLED (a repeat cancel is a no-op), and use `app.state.notify_transport` so tests can inject a transport.
5. Remove `requests` from `requirements.lock`. Replace the agent's monkeypatched test with one that exercises `notify.py` itself.

## R8: the unasked field (6.8)
1. The task was the name. Make `CustomerPatch` accept only `name` (non-empty) and forbid other fields: `model_config = ConfigDict(extra="forbid")`.
2. `update_customer` takes only `name`.
3. Regression test: `PATCH` with `{"email": ...}` returns 422 and the email is unchanged.
