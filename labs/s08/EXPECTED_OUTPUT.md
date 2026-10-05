# Expected output: Lab s08

## At s08-start
`make test`: Python `15 failed, 73 passed` (`test_billing_tax.py`); tools `6 failed, 133 passed` (map, golden, compare). Legacy self-test: 4 checks pass.
`python tools/billing_compare.py` → `compare: no recorded cases (run: python tools/billing_golden.py record)`.

## After recording (before changing Java)
```
recorded 50 cases; wrote 50 records to .../BILL20260115.DAT; 4264 bytes
golden: 52 records identical (javac --release 8)
```
`python tools/billing_compare.py` with the original Java fails, because the batch ignores the switch:
```
compare: new path used for 0 of 50 records (BILLING_NEW_TAX_COUNTRIES=*)
compare: FAILED the new path was not used: does the batch read BILLING_NEW_TAX_COUNTRIES?
```

## At s08
```
compare: new path used for 50 of 50 records (BILLING_NEW_TAX_COUNTRIES=*)
compare: 0 differing record(s)
compare: zero differences; trailers consistent.
```
With a half-up `tax_minor` (the incident's version), the same run reports the five half-way cases that round differently (orders 4, 6, 14, 15 and 25) and the trailer:
```
compare: 6 differing record(s) (first 5 shown)
  record 5:
    expected D0000000004Arjun Mehta                   INUSD000000000250000000000400000000029
    actual   D0000000004Arjun Mehta                   INUSD000000000250000000000500000000030
```
`make test`: Python `88 passed`; tools `152 passed`. Legacy self-test: 8 checks pass. `python tools/billing_golden.py check --release 11` → 52 records identical.
