# AGENTS.md: legacy/billing

The nightly billing batch. Runs at 02:00; finance collects its output at 04:00. Treat every format here as an external contract.

## Commands

- Build and self-test: `./build.sh` (from this folder), or `make test-java` from the repository root
- Run the batch end to end: `make billing-demo` from the repository root

## Contracts (do not break)

- **Input:** `orders_YYYYMMDD.csv` written by `services/orders/orderhub/orders.py` (`write_billing_handoff`). `HandoffReader` splits on commas and reads columns **by position**: 0 order_id, 1 customer_name, 2 country, 3 currency, 4 subtotal_minor, 5 total_minor. Inserting or reordering columns breaks the batch. Extra columns appended at the end are ignored.
- **Output:** `BILLYYYYMMDD.DAT`, fixed width, 80 characters per record, ISO-8859-1, CRLF line endings. Layout is in `FixedWidthExport.java`.
- `docs/RECORD_LAYOUT.txt` (2017) is out of date: it says amounts are 10 characters; the code writes 11. The code is what finance currently receives.
- Tax rounding is `HALF_EVEN` on the invoice net amount (`InvoiceCalculator`). It is not documented elsewhere. Do not change it without finance sign-off.

## Conventions

- Source must compile with `javac --release 8`: no `var`, no records, no text blocks.
- No new libraries. The module has no dependency manager yet.

## Boundaries

- Do not change the export layout, encoding, line endings or rounding without an issue that records finance's agreement.
- Add characterisation tests before refactoring anything here.
