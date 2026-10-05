# T3: Merge repeated SKUs when an order is placed

`POST /orders` with `[{"sku": "MUG-350", "quantity": 1}, {"sku": "mug-350", "quantity": 2}]` creates two order lines today. It should create one line with quantity 3 (and take 3 from stock). Totals don't change.
