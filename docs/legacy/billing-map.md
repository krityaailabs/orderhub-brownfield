# Module map: legacy/billing

Written with an agent in Lecture 8.2, then checked by hand. Every statement cites a file; anything we couldn't confirm is under "Unknowns and risks". Line references are to `s08-start`.

## Entry points

- `run_batch.sh <handoff-dir> <out-dir> <yyyy-MM-dd>`: builds if `build/classes` is missing, then runs `com.orderhub.billing.NightlyBatch` (`run_batch.sh`).
- `NightlyBatch.main` (`NightlyBatch.java`): exactly three arguments, otherwise prints usage and exits 2. Scheduled at 02:00 server time (class comment; the scheduler itself isn't in this repository).
- `build.sh`: compiles `src` and `test` with `javac --release 8` and runs `BillingSelfTest` (4 checks).
- Called end to end by `tools/e2e_billing.py` (`make billing-demo`) and the CI job `billing-contract`.

## Data flow

1. `NightlyBatch` parses the date with `yyyy-MM-dd` and builds `<handoff-dir>/orders_yyyyMMdd.csv`.
2. `HandoffReader.read` reads it as UTF-8, skips the header line and blank lines, splits each line on `,` and reads columns **by position**: 0 order_id, 1 customer_name, 2 country, 3 currency, 4 subtotal_minor, 5 total_minor (`HandoffReader.java`). Extra trailing columns are ignored.
3. For each `OrderRecord`, `FixedWidthExport.detail` asks `InvoiceCalculator.tax(totalMinor, country)`: rate in basis points from a hard-coded map (GB, FR 2000; IT 2200; IN 1800; AE 500; AU, JP 1000; NG 750; anything else 0), `BigDecimal`, **HALF_EVEN** to whole minor units. Tax is on the **total** (after discount), not the subtotal; `subtotalMinor` is read but never used.
4. `FixedWidthExport.write` writes header, one detail per record (input order), and a trailer whose gross total is computed **separately** via `InvoiceCalculator.gross` (`FixedWidthExport.java`).

## Side effects

- Creates `<out-dir>` (`mkdirs`) after reading the input; writes `<out-dir>/BILLyyyyMMdd.DAT`, overwriting any existing file.
- Prints `wrote N records to <path>` on stdout. Exceptions go to stderr with exit 1 (no catch anywhere).
- If an exception happens while writing, the file is left **partially written** (the writer is closed in `finally`).
- No database, no network, no environment variables at `s08-start`.

## Contracts

- **Input** (owned by `services/orders/orderhub/orders.py`, `write_billing_handoff`): header `order_id,customer_name,country,currency,subtotal_minor,total_minor`; UTF-8; read by position.
- **Output** (read by the finance system at 04:00): `BILLyyyyMMdd.DAT`; **80** characters per record; **ISO-8859-1**; **CRLF** line endings, including after the trailer.
  - Header: `H` + business date `ddMMyy` + `ORDERHUB`, space-padded.
  - Detail: `D` + order id (10, zero-filled) + name (30, truncated or space-padded) + country (2) + currency (3) + net (11) + tax (11) + gross (11), zero-filled; then space-padded to 80.
  - Trailer: `T` + count (6) + gross total (13).
- **Rounding**: HALF_EVEN on the tax (`InvoiceCalculator.java`). Documented only in `legacy/billing/AGENTS.md`.
- `docs/RECORD_LAYOUT.txt` (rev 3, 2017) is **out of date**: it says amounts are 10 characters at positions 47–76; the code writes 11 (positions 47–79). The code is what finance receives.

## Unknowns and risks

- **A comma in a customer name stops the batch.** Python's `csv` writer quotes `"Smith, John"`; `HandoffReader` splits on every comma, so column 4 becomes `USD` and `Long.parseLong` throws: no output file at all. Confirmed by running the batch on a one-line file. Logged as issue Q16; not fixed in Project 2 (out of scope; the golden cases exclude commas and a test pins the current behaviour).
- **Characters outside ISO-8859-1** (for example Japanese names) are written as `?` by the encoder. Finance receives `?? ??`. Whether finance knows is unknown.
- Names longer than 30 characters are silently truncated.
- Who changes `RATES`, and how finance is told, isn't recorded ("last reviewed with finance in 2021").
- Header date uses `ddMMyy` (two-digit year); the file name uses `yyyyMMdd`.
- The batch runs in server time; `NightlyBatch` parses the date without a time zone. Whether the server is UTC is unknown.
- The self-test (4 checks, 2019) covers almost nothing; before Project 2 there were no tests of the file as finance receives it.
