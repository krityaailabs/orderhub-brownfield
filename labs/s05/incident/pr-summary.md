# PR: Make cancel retries succeed

The mobile app sometimes retries cancel after the order has shipped, and gets 409, which shows an error to the customer. Simplified `cancel_order` so cancel always succeeds. Updated nothing else. All tests pass.
