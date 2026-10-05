# Lab s06 answers

## 6.1 Review minutes (one reasonable set)

At a careful pace of 200 to 400 changed lines an hour for domain code: R4 (63 lines) 10–15 minutes; R5 (121) 20–30 minutes; R3 (about 570) one and a half to three hours if read line by line, which is why it should be split. A sensible team limit: 300 changed lines including tests, and formatting never mixed with behaviour.

## 6.2 R8 with the checklist

- Task vs summary: the task was the name; the PR adds email "for flexibility". Unasked scope.
- `update_customer` sets `email` with no `@` check and no case-insensitive duplicate check (both exist in `create_customer`). `{"email": "not-an-email"}` is accepted. An exact duplicate hits the database's unique constraint and returns a 500; a case variant (`AIKO.TANAKA@example.com`) is accepted, creating two customers whose emails differ only by case, which `create_customer` deliberately prevents (Q1).
- API surface: clients can now change a customer's email, which may be how they log in or receive receipts. That's a product and security decision, not a typo fix.
- Tests cover only the asked-for path.
- Outcome: **change**. Keep `PATCH` for `name`; forbid other fields.

## 6.3 R3 triage (570 lines, ten minutes)

Behaviour changes hidden in a "no behaviour change" PR (verified by comparing the syntax trees of every file before and after):
1. `api.py`: `min(limit, 200)` became `min(limit, 2000)`. `review-flags` reports it as DELETED-CHECK.
2. `orders.py` `write_billing_handoff`: `encoding="utf-8"` was removed. On a server whose default encoding isn't UTF-8, customer names with non-ASCII characters are written differently or fail, and the legacy batch reads the file. `review-flags` does **not** flag it: the line has no check pattern and doesn't mention the handoff. Only reading `orders.py` (AGENTS.md says it writes the handoff) finds it.

The second DELETED-CHECK flag (a `raise` in `return_items`) is a false positive: the formatter re-wrapped the line. Everything else is formatting and test type hints.
Outcome: **split**. One PR with formatting only (mechanically checkable: the syntax trees are identical), one with type hints, and each behaviour change as its own PR with a reason, or dropped.

## 6.4 R4

`GET /orders?limit=30` sent **34** queries at `s06-start` (one for the orders, one per order for its lines, plus customers and products as they're first touched). After `joinedload(Order.customer)` and `selectinload(Order.lines).selectinload(OrderLine.product)`: **3**. Note the comment R4 deleted: the original code said, in plain words, that each order loaded its customer and lines lazily. The agent removed the warning and made the problem worse.
Unasked change: `limit=0` returns everything, and the endpoint's clamp was removed. Restored as `Query(50, ge=1, le=200)`: `limit=0` and `limit=201` are 422.

## 6.5 R5

- **Invented API:** `requests.post(..., retries=3)`. `requests` has no `retries` argument (retries live on a urllib3 `Retry` mounted through an adapter). With the webhook configured, every cancel would raise `TypeError` **after** the cancellation was committed: the customer gets a 500, the mobile app retries, and the warehouse is never told.
- **Duplicate dependency:** `requests` added although `httpx` is already locked (ADR 0002). `review-flags` reports DUPLICATE-DEP.
- **Mocked test:** the only test replaced `notify.order_cancelled` with a lambda, so `notify.py` never ran in CI. MOCK-IN-TEST.
- Repair: `httpx.Client(transport=httpx.HTTPTransport(retries=3), timeout=5)`, a `transport` parameter for tests, return `False` and log on failure, never fail the cancel, notify only when the order actually changed to CANCELLED.

## 6.6 R6: your review vs the automated one

The automated comments are right about the SQL built with an f-string (fix with a bound parameter) and the free-form `date` parameter. What they miss, because they need business context:
1. **Cancelled orders are counted as sales.** Every other money report (the billing handoff) excludes `CANCELLED`.
2. **Refunds are ignored.** `refunded_minor` from returns isn't subtracted, so "sales" overstates revenue after returns.
3. The test passes with any positive number (`>= 1`, `> 0`), so neither problem could fail it.
Typical automated strength: patterns visible in the diff. Typical blind spot: rules that live elsewhere (specs, other modules, finance's definitions).

## 6.7 Gallery decisions

| PR | Decision | The risk |
|---|---|---|
| R1 | Reject | Property and characterisation tests silently skipped in CI; the safety net is gone where it matters. Make them faster or run them nightly, visibly. |
| R2 | Reject | The test passes `now` explicitly, so it can't be timing-sensitive: the premise wasn't checked. Moving to 31 days removes the boundary check that killed a mutant in Section 4, and the agent wrote its own `[test-change-approved]`. Approval must come from a named person. |
| R3 | Split | Two behaviour changes hidden in 570 lines of formatting (see 6.3). |
| R4 | Change | N+1 (34 queries for 30 orders) and an unasked unbounded `limit=0`. |
| R5 | Change | Invented `retries=`, duplicate HTTP client, test that mocks the code under review, cancel fails if the call fails. |
| R6 | Change | SQL injection; counts cancelled orders; ignores refunds. |
| R7 | Reject | `except Exception` turns a crash into a silently incomplete billing file. Finance would bill from partial data. Fail loudly, or skip with a count that the batch reconciles. |
| R8 | Change | Unasked, unvalidated email changes. |
| R9 | Reject | Pins replaced by ranges: builds are no longer reproducible, and pydantic/starlette can move to a new major version unreviewed. Upgrade one pinned version at a time and read the changelog. |
| R10 | Reject | Logs every header and body: customer names and emails, and any credentials sent in headers. Log identifiers (order id, request id), not payloads. Section 7 covers this. |

## 6.8 Done when

All eight regression tests in the solved tag fail on `s06-start` and pass on `s06`; `instructor/s06` hidden tests pass. Two R4/R5 agent tests were replaced, with `[test-change-approved]` and a reason in the commit message, because they asserted the wrong behaviour (`limit=0` returns all; the warehouse call mocked away).

## Break it

`review-flags` sees text patterns in the diff. "Email changes need the same validation as create" is a rule in another function and a product decision; no diff pattern carries it. The checklist's "task vs summary" and "what can clients now do" questions do.
