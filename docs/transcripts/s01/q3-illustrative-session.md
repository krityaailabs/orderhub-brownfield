# Session transcript: issue Q3 (ILLUSTRATIVE)

> **This transcript is constructed for teaching.** It is not a recording of any specific tool or model. It shows a pattern seen often in real sessions. The code change it describes is real: it is in `labs/s01/q3-wrong-turn.patch`, and you can apply it and run it yourself. The instructor's recorded session replaces this file when Lecture 1.5 is filmed.

**Request from the developer**

> Read docs/issues/Q3.md and implement it. Run the tests when you're done.

| Step | Agent action (tool call) | Result |
|---|---|---|
| 1 | Read `docs/issues/Q3.md` | Issue text |
| 2 | Search the code for `write_billing_handoff` | Found in `services/orders/orderhub/orders.py` and `services/orders/tests/test_orders.py` |
| 3 | Read `services/orders/orderhub/orders.py` | Full file |
| 4 | Read `services/orders/tests/test_orders.py` | Full file |
| 5 | Edit `orders.py`: add `customer_email` to the header **after `customer_name`**, and `order.customer.email` to each row in the same position | Edit applied |
| 6 | Edit `test_orders.py`: update the expected header line | Edit applied |
| 7 | Run `cd services/orders && python -m pytest -q` | 27 passed |
| 8 | Reply to the developer | see below |

**Agent's final message**

> I've added the customer's email to the billing handoff. The CSV now has a `customer_email` column next to `customer_name`, and every row includes the customer's email address. I updated the existing handoff test to expect the new header. All 27 tests pass.

**What the agent never did**

- It never searched for the file name pattern `orders_` or for `handoff` outside the Python service.
- It never opened `legacy/billing/`.
- It never ran `make test` (which includes the Java build) or `make billing-demo`.
- Acceptance criterion 2 ("the nightly billing batch keeps working") is not mentioned in its final message.
