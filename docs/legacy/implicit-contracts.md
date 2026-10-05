# Implicit contracts in the billing export (Lecture 8.6)

Things the finance system and the batch depend on that no specification states. Each has a test in `tools/tests/test_billing_contracts.py` that runs the real batch.

| # | Contract | Where it lives | Test |
|---|---|---|---|
| 1 | Every record is exactly 80 characters | `FixedWidthExport.RECORD_LENGTH`, `pad` | `test_every_record_is_80_characters_with_crlf` |
| 2 | CRLF after every record, including the trailer | `FixedWidthExport.write` | same |
| 3 | ISO-8859-1: accents kept as single bytes; characters outside Latin-1 become `?` | `OutputStreamWriter(..., "ISO-8859-1")` | `test_encoding_is_iso_8859_1` |
| 4 | Names truncated to 30 characters, never wrapped | `fit(name, 30)` | `test_long_names_are_truncated_to_30` |
| 5 | Amounts are 11 digits, zero-filled (not 10, as RECORD_LAYOUT.txt says) | `zero(value, 11)` | `test_amount_fields_are_11_digits` |
| 6 | Tax rounds HALF_EVEN on the total | `InvoiceCalculator.tax` | `test_tax_rounds_half_even` |
| 7 | Unknown countries pay no tax | `rateBasisPoints` | `test_unknown_country_pays_no_tax` |
| 8 | Header date is `ddMMyy` (two-digit year) | `FixedWidthExport.header` | `test_header_date_is_ddmmyy` |
| 9 | Trailer count and gross total equal the detail records | `FixedWidthExport.write` | `test_trailer_matches_details` |
| 10 | Records are in input order (order id order from the handoff) | `HandoffReader`, `write` | `test_records_keep_input_order` |
| 11 | A comma in a name stops the batch (known issue Q16, pinned, not endorsed) | `HandoffReader` split on `,` | `test_comma_in_a_name_stops_the_batch_known_issue_q16` |
