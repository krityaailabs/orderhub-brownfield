# AGENTS.md: OrderHub Brownfield

Instructions for coding agents (and new joiners). Keep this file short; detail lives in nested AGENTS.md files and docs/adr/.

## Project

OrderHub is an order and fulfilment platform with history.
- `services/orders/`: order service, Python 3.11+, FastAPI, SQLAlchemy. Tests in `services/orders/tests/`.
- `legacy/billing/`: nightly billing batch, Java (built for Java 8). **Read `legacy/billing/AGENTS.md` before changing anything it reads or writes.**
- `tools/`: course and project tooling, with tests in `tools/tests/`.

## Commands

Run from the repository root. Use these exact commands; do not invent others.
- Set up: `make setup`
- All tests (Python, tools and Java): `make test`
- Python tests only: `make test-py`
- Lint: `make lint`
- End-to-end billing check (order service → CSV handoff → Java batch): `make billing-demo`
- Context check: `make context-check`
- Spec and plan check: `make spec-check`
- Mutation tests for returns: `make mutate`
- Test-tampering guard: `make protect-tests`

A change is done only when `make test`, `make lint` and, if it touches the billing handoff, `make billing-demo` all pass.

## Conventions

- Money is integer minor units (cents) everywhere. Never use floats for money. See `docs/adr/0001-money-in-integer-minor-units.md`.
  - Good: `discount = (amount_minor * percent + 50) // 100`
  - Bad: `round(amount_minor * 0.9)`
- Domain errors are raised as `NotFound`, `Conflict` or `ValidationFailed` from `orderhub/errors.py`; the API maps them to status codes. Do not return error dicts from domain code.
- No broad `except Exception:` in application code.
- Stored datetimes without a time zone are UTC (SQLite returns them naive); compare in UTC.
- Pricing helpers are pure functions of their arguments; order-history rules (such as the refund remainder rule) live in `orders.py`.
- Tests: pytest, one behaviour per test, names that read as sentences (`test_cancel_restores_stock`).
- New dependencies need a reviewed reason. See `docs/adr/0002-no-new-dependencies-without-review.md`.

## Boundaries

- Never edit an existing test to make it pass. If a test looks wrong, stop and say so.
- Never change the CSV handoff columns or the billing export layout without an issue that says finance has agreed. Both are read by other programs.
- Never commit secrets, `.env` files or real customer data. All data here is synthetic.
- Do not modify `requirements.lock` except as the result of a reviewed dependency change.
- Do not touch `instructor/` (course material; not part of the product).

## Working agreement

- Before editing, list the files you read and the files you expect to change.
- Keep each change small enough to review in ten minutes; split larger work.
- When unsure about a business rule, ask. Do not guess.
