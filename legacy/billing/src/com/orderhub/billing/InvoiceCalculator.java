package com.orderhub.billing;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.HashMap;
import java.util.Map;

/** Calculates tax and gross amounts for invoices. Amounts are in minor units. */
public class InvoiceCalculator {

    // Rates in basis points. Last reviewed with finance in 2021.
    private static final Map<String, Integer> RATES = new HashMap<String, Integer>();
    static {
        RATES.put("GB", 2000);
        RATES.put("FR", 2000);
        RATES.put("IT", 2200);
        RATES.put("IN", 1800);
        RATES.put("AE", 500);
        RATES.put("AU", 1000);
        RATES.put("JP", 1000);
        RATES.put("NG", 750);
    }

    public static int rateBasisPoints(String country) {
        Integer r = RATES.get(country);
        return r == null ? 0 : r.intValue();
    }

    public static long tax(long netMinor, String country) {
        BigDecimal t = BigDecimal.valueOf(netMinor)
                .multiply(BigDecimal.valueOf(rateBasisPoints(country)))
                .divide(BigDecimal.valueOf(10000));
        return t.setScale(0, RoundingMode.HALF_EVEN).longValue();
    }

    public static long gross(long netMinor, String country) {
        return netMinor + tax(netMinor, country);
    }
}
