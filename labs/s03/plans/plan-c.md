# Plan C (proposed by the agent for slice S3 of the returns spec)

1. Implement `refund_for_units` in `pricing.py` using `round(line_value / subtotal * discount)`.
2. Update `return_items` to subtract the allocated discount.
3. Run `make test-py`.
4. Write tests for AC-2 and AC-3 once the implementation works.

Estimated ~80 lines.
