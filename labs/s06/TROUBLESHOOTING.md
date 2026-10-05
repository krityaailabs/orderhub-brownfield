# Lab s06 troubleshooting

**`count_queries` counts more than I expect after the fix.** Count only inside the `with` block, after placing the orders. Placing orders sends many queries; listing should send three or four.

**`selectinload` and `.limit()` together.** That's fine: `selectinload` runs a second query for the lines of the orders the first query returned. `joinedload` on a collection with `.limit()` is the one to avoid (the limit applies to joined rows).

**My notifier test hits the network.** Pass `transport=httpx.MockTransport(handler)`. Nothing in the lab should make a real HTTP call.

**`TestClient` raises instead of returning 500.** That's `TestClient`'s default (`raise_server_exceptions=True`), and it's useful: the exception tells you what broke.

**Removing `requests` from requirements.lock doesn't uninstall it.** Pip doesn't remove packages. `.venv/bin/python -m pip uninstall -y requests` and re-run the tests, or recreate the environment with `make setup`.

**protect-tests blocks my commit.** You changed lines in an existing test (the R4 or R5 agent tests). If the test asserted the wrong behaviour, that's a legitimate change: add `[test-change-approved]` and the reason to the commit message, and name who approved it in the PR.
