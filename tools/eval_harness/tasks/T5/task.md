# T5: Cap the quantity per order line at 99

Warehouse can't pick more than 99 of one item per order. `POST /orders` with a quantity of 100 or more must return 422 with "quantity must be at most 99"; 99 is fine. Applies wherever orders are placed (API and `orders.place_order`).
