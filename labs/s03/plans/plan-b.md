# Plan B (proposed by the agent for "implement the returns spec")

1. Create a new `returns` module with models, service, API and refund engine.
2. Refactor `pricing.py` into a `Money` class used everywhere, to make refunds cleaner.
3. Implement all criteria AC-1 to AC-8.
4. Update existing tests to use the `Money` class.
5. Add a `refund_minor` column to the billing CSV so finance can see refunds.
6. Run the tests.

Estimated ~1,100 lines across 14 files.
