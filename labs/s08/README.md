# Lab s08 / Project 2: strangle the legacy billing calculation (Section 8)

**Start tag:** `s08-start` · **Solved tag:** `s08` · **Time:** 4–6 hours (Project 2, intermediate) · **Agent usage:** recommended, with the brownfield playbook

The legacy batch (`legacy/billing`, Java built for Java 8) calculates tax on each order and writes the fixed-width file finance collects at 04:00. Project 2 moves the tax calculation into the order service, **one country at a time**, behind a switch, with **byte-identical output** on the old and new paths.

At `s08-start`, these fail on purpose:
- `tests/test_billing_tax.py` (Python): `orderhub/billing_tax.py` `tax_minor` is a stub
- `tools/tests/test_billing_map.py`: `docs/legacy/billing-map.md` is a template
- `tools/tests/test_billing_golden.py`: `tools/billing_golden.py` `cases()` is a stub; nothing is recorded
- `tools/tests/test_billing_compare.py`: the Java batch has no seam and ignores `BILLING_NEW_TAX_COUNTRIES`

| Lecture | Task | Done when |
|---|---|---|
| 8.1 | Write the brownfield playbook (map, pin, change, verify) for one module you know | Written answer |
| 8.2 | Map `legacy/billing` with an agent: entry points, data flow, side effects, contracts, unknowns | `docs/legacy/billing-map.md` complete; `test_billing_map.py` passes |
| 8.3 | Design 50 cases in `cases()`; `python tools/billing_golden.py record`; pin them | `test_billing_golden.py` passes; `python tools/billing_golden.py check` → 52 records identical (header, 50 details, trailer) |
| 8.4 | Introduce a `TaxPolicy` seam in Java; read `tax_YYYYMMDD.csv` for countries in `BILLING_NEW_TAX_COUNTRIES`; implement `tax_minor` | `python tools/billing_compare.py JP` → zero differences, new path used |
| 8.5 | Write the upgrade plan for the billing module; run batch 1 (`--release 11`) | `python tools/billing_golden.py check --release 11` passes |
| 8.6 | List the implicit contracts in the export; add a test for each | One test per contract |
| 8.7 | Investigate `incident/` | Compared with `ANSWERS.md` |
| 8.8 | Project 2 complete | `python tools/billing_compare.py` (all countries) → zero differences, trailers consistent; `make test`, `make billing-demo`, golden check pass |

```bash
git switch -c my-s08 s08-start
make test-java                                   # the legacy self-test still passes
python tools/billing_compare.py                  # fails: no recorded cases yet
```

## Rules for this project

1. **Map, pin, change, verify**, in that order. No change to `legacy/billing/src` before the golden check passes.
2. The golden files are re-recorded only for an intended, agreed change, never to make a check pass.
3. The orders CSV is unchanged (returns AC-8). The new path adds a side file; the legacy reader is untouched.
4. Java stays `javac --release 8` compatible until the upgrade plan says otherwise. No new libraries.
5. With the switch off (unset or empty), the batch behaves exactly as before.
