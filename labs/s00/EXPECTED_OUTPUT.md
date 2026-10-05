# Expected output: Lab s00

Captured from a clean install on Linux, Python 3.13, OpenJDK 21, on 5 October 2026. Dates in file names and the header record will show your own date.

`make doctor`
```
OK    python >= 3.11         3.13.16
OK    package fastapi        installed
OK    package sqlalchemy     installed
OK    package pydantic       installed
OK    package pytest         installed
OK    package httpx          installed
OK    java >= 11 (javac)     java 21
OK    git                    /usr/bin/git
OK    ruff (lint)            found

All required checks passed.
```

`make test` (last lines)
```
27 passed in 0.46s
PASS UK tax is 20 percent
PASS unknown country has no tax
PASS detail record is 80 characters
PASS detail record starts with D and padded id
all checks passed
```

`make billing-demo`
```
handoff: out/handoff/orders_20261005.csv
wrote 3 records to .../out/billing/BILL20261005.DAT
BILL20261005.DAT: 5 records, 410 bytes, record lengths [80]
  H051026ORDERHUB
  D0000000001Emma Clarke                   GBUSD000000025000000000050000000003000
  D0000000002Priya Nair                    INUSD000000033990000000061200000004011
  D0000000003Aiko Tanaka                   JPUSD000000030030000000030000000003303
  T0000030000000010314
```
(Records are padded with spaces to 80 characters; trailing spaces are not shown here.)
