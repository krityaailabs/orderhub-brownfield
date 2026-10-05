package com.orderhub.billing;

/** The original calculation, unchanged: InvoiceCalculator (HALF_EVEN on the net amount). */
public class LegacyTaxPolicy implements TaxPolicy {

    public long tax(OrderRecord r) {
        return InvoiceCalculator.tax(r.totalMinor, r.country);
    }

    public int newPathCount() {
        return 0;
    }
}
