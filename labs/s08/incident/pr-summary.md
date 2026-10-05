## Move tax calculation to the order service (strangler, step 1)

- New `billing_tax.py` computes tax in Python; writes `tax_YYYYMMDD.csv` next to the handoff.
- Java: new `TaxPolicy` seam. `FixedWidthExport.detail()` now takes the tax from the policy; countries in `BILLING_NEW_TAX_COUNTRIES` use the Python value.
- Rounding: "standard rounding (round half up), which is what finance expects".
- Verified with a comparison run on 20 recorded orders: **zero differences**. All tests pass.
- Rollout: JP and AU first (low volume).
