# Lab s08 troubleshooting

**`javac: not found`.** The legacy module needs a JDK (any version that supports `--release 8`, e.g. 17 or 21). `make doctor` checks.

**The golden check fails after I recorded it.** Something changed the output. Read the first differing record: the fields are fixed-width, so count positions (name 12–41, net 47–57, tax 58–68, gross 69–79, 1-based). Never re-record to make it pass.

**`compare` says the new path was used for 0 records.** The batch isn't reading `BILLING_NEW_TAX_COUNTRIES`, or isn't printing `tax: new path for N of M records`.

**`compare` reports differences only for a few records.** Look at their amounts: are they exact half-way cases? Then `tax_minor` isn't rounding half to even.

**`trailer gross ... != sum of detail gross`.** The trailer is computed with a different tax than the details. Use one policy, and one tax value per record, for both.

**The batch throws `no new-path tax for order N`.** That's the safety net: a routed order has no row in `tax_YYYYMMDD.csv`. Check the side file covers the same orders as the handoff.

**Japanese characters print as `??`.** Correct: the export is ISO-8859-1 (implicit contract 3). Don't "fix" it in this project.
