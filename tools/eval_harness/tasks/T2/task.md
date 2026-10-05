# T2: Filter the order list by customer

Support wants `GET /orders?customer_id=N` to return only that customer's orders (an unknown customer gives an empty list). `customer_id` must be a positive integer (422 otherwise). Existing filters keep working and can be combined.
