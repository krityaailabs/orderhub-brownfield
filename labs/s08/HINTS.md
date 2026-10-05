# Lab s08 hints

## The map (8.2)
Ask the agent to read, not to change: "Map legacy/billing. For every claim, cite the file and line. List what you couldn't confirm under Unknowns." Then check three of its claims yourself. Look hard at `HandoffReader`: what happens to a customer name with a comma? What does `docs/RECORD_LAYOUT.txt` say about amount widths, and what does the code write?

## cases() (8.3)
Build the special cases first: one per requirement in the docstring (a half-way case per country, 0, 99_999_999, a long name, accents, a non-Latin-1 name, two unrated countries). Then fill to 50 with a readable pattern, cycling through the rated countries. Half-way totals: JP and AU `1005`, `2405`; IN `25`, `75`; NG `20`, `60`.

## The seam (8.4)
1. `TaxPolicy` interface with `long tax(OrderRecord r)`. `LegacyTaxPolicy` calls `InvoiceCalculator.tax`.
2. `SwitchedTaxPolicy(Set<String> countries, Map<Long, Long> newTax)`: for a routed country, use the side-file value; if it's missing, throw (fail loudly: never fall back silently for a routed record). Otherwise delegate to the legacy policy. `"*"` routes every country.
3. `FixedWidthExport.detail(r, policy)` **and** the trailer sum in `write(...)` must use the same policy. (Read the incident before you skip this.)
4. `NightlyBatch` reads `BILLING_NEW_TAX_COUNTRIES`; if non-empty, reads `tax_YYYYMMDD.csv` from the handoff folder and prints `tax: new path for N of M records`.
5. Keep the old `detail(r)` and `write(records, day, path)` working (they delegate with the legacy policy), so the self-test and anything else that calls them still work.

## tax_minor (8.4)
`q, r = divmod(net_minor * rate, 10000)`; round up if `2 * r > 10000`, or if `2 * r == 10000` and `q` is odd.
