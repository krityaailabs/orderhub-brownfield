# Lab s08 answers

## 8.1 The brownfield playbook
Map (read, cite, list unknowns) → Pin (characterisation tests on the outputs others depend on) → Change (smallest step behind a seam, switch off by default) → Verify (old vs new on the same inputs, then a limited rollout). One sentence per step in your own module, plus the one thing you'd check before the first change.

## 8.2 The map
See `docs/legacy/billing-map.md` in the solved tag. The facts people miss: the reader works **by position**; tax is on the **total**, not the subtotal; the trailer total is computed by a **separate call**; a failed write leaves a **partial file**; `RECORD_LAYOUT.txt` is wrong about amount widths; and a **comma in a name stops the batch** (Q16).

## 8.3 Golden cases
Any set that satisfies the docstring works. The solved `cases()` starts with 15 special cases (each requirement once or twice), then fills to 50 with `Customer NN`, cycling through the rated countries. `python tools/billing_golden.py record` → `recorded 50 cases; 4264 bytes` (52 records × 82 bytes). Record **before** touching the Java.

## 8.4 The seam
- `TaxPolicy` (interface), `LegacyTaxPolicy` (InvoiceCalculator), `SwitchedTaxPolicy` (side file for routed countries; throws if a routed order has no value).
- `FixedWidthExport.write(records, day, path, policy)` computes every record's tax **once** and uses it for both the detail and the trailer sum, and builds every record before opening the file (no partial file on failure).
- `NightlyBatch` reads `BILLING_NEW_TAX_COUNTRIES`; prints `tax: new path for N of M records` when the switch is on.
- `tax_minor`: `divmod`, round half to even, integers only.
- `python tools/billing_compare.py JP` → `new path used for 6 of 50 records`, zero differences.

## 8.5 Upgrade
`docs/legacy/upgrade-plan.md`: five batches, each with verify and rollback. Batch 1: `python tools/billing_golden.py check --release 11` → 52 records identical. The risk most people miss: Java 18 made UTF-8 the default charset; this module is safe only because both its reader and writer name their charsets.

## 8.6 Implicit contracts
`docs/legacy/implicit-contracts.md`: 11 contracts, 13 tests in `tools/tests/test_billing_contracts.py` (the rounding test has four cases). Q16 is pinned, not endorsed: the test documents today's behaviour so that a fix is a visible, intended change.

## 8.7 Incident
- **Hypothesis:** the new path computed different tax for some records, and the trailer didn't include the difference.
- **Evidence:** `ops-rerun.txt` (2 records differ by +1 tax, both exact halves: JP 1005, AU 2405); `diff-excerpt.patch` (`int(x + 0.5)` is half-up; the trailer still sums `InvoiceCalculator.gross`); `finance-rejection.txt` (trailer 2 lower than the details).
- **Root cause, three parts:** (1) the implicit rounding contract (HALF_EVEN) wasn't carried over: "standard rounding" is half-up; (2) the seam covered the detail record but not the trailer, so the file disagreed with itself; (3) the comparison run had 20 cases with no half-way amounts and didn't check the trailer, so it couldn't fail on either problem.
- **Mitigation:** switch off; rerun on the legacy path; send finance the legacy file (done at 05:07).
- **Permanent fix:** HALF_EVEN with integers; one policy for details and trailer; golden cases with a half-way case per affected country; the comparison checks trailers and that the new path was used; both in CI.
- **Detection signal:** `billing_compare` in CI (fails on any differing record or inconsistent trailer); and, in production, a pre-send check that the trailer equals the sum of the details.

## 8.8 Project 2
`python tools/billing_compare.py` → `new path used for 50 of 50 records`, `0 differing record(s)`, `zero differences; trailers consistent.` Golden check passes; `make test`, `make billing-demo` pass. Rollout plan: one country at a time, starting with the lowest volume, with the comparison run on the previous day's real handoff before each step.
