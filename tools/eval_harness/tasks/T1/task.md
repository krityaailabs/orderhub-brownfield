# T1: The order list's status filter ignores case and spaces (issue Q21)

`GET /orders?status=shipped` returns nothing; `status=SHIPPED` works. Make the filter accept any case and surrounding spaces. Change nothing else.
