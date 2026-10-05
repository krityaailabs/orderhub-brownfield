# Lab s04 hints

## refund_for_units
1. Work in integers. The discount is `subtotal - total`; the returned units' value is `price * quantity`.
2. The share is `discount * value / subtotal`, rounded half-up. For non-negative integers, `round_half_up(a / b) == (2*a + b) // (2*b)`.
3. Validate inputs first: quantity at least 1; subtotal positive; 0 <= total <= subtotal.

## ship_order
1. Only PLACED orders can be shipped; anything else is `Conflict`.

## return_items
1. Check the status (Conflict) and the window (ValidationFailed "return window closed") before anything else. Compare in UTC; SQLite returns naive datetimes.
2. Validate every requested item before changing anything (AC-5). Add up quantities per SKU first, so the same SKU twice counts together.
3. If this return empties the order, the refund is `total - refunded_so_far` (AC-3). Otherwise sum `refund_for_units` per SKU. Then update `returned_quantity`, stock and `refunded_minor`, and commit once.

## find_test_edits
1. Track the current file from `--- a/...` lines; `--- /dev/null` means a new file, so ignore its lines.
2. Count lines that start with `-` (but not `---`); skip blank ones.

## Property tests
1. Use `st.permutations(units)` to return units in a random order.
2. The first property: refunds of a fully returned order sum to its total. The second: each refund is non-negative and the running total never exceeds the order total.
