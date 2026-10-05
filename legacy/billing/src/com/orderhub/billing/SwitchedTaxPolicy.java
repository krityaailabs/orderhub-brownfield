package com.orderhub.billing;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Strangler switch: countries listed in BILLING_NEW_TAX_COUNTRIES take their tax from
 * tax_YYYYMMDD.csv (written by the order service); all others use the legacy calculation.
 * "*" routes every country. A routed record with no new-path value stops the batch: it never
 * falls back silently.
 */
public class SwitchedTaxPolicy implements TaxPolicy {

    private final Set<String> countries;
    private final Map<Long, Long> newTax;
    private final TaxPolicy legacy = new LegacyTaxPolicy();
    private int newPathCount = 0;

    public SwitchedTaxPolicy(Set<String> countries, Map<Long, Long> newTax) {
        this.countries = countries;
        this.newTax = newTax;
    }

    public long tax(OrderRecord r) {
        if (!countries.contains("*") && !countries.contains(r.country)) {
            return legacy.tax(r);
        }
        Long value = newTax.get(Long.valueOf(r.orderId));
        if (value == null) {
            throw new IllegalStateException("no new-path tax for order " + r.orderId + " (" + r.country + ")");
        }
        newPathCount++;
        return value.longValue();
    }

    public int newPathCount() {
        return newPathCount;
    }

    /** Parse "JP,AU" (or "*") into a set; empty or null means the switch is off. */
    public static Set<String> parseCountries(String value) {
        Set<String> out = new HashSet<String>();
        if (value == null) {
            return out;
        }
        for (String part : value.split(",")) {
            String c = part.trim();
            if (c.length() > 0) {
                out.add(c);
            }
        }
        return out;
    }

    /** Read tax_YYYYMMDD.csv: header order_id,tax_minor, then one row per order. */
    public static Map<Long, Long> readTaxFile(String path) throws IOException {
        Map<Long, Long> out = new HashMap<Long, Long>();
        if (!new File(path).exists()) {
            return out;
        }
        BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(path), "UTF-8"));
        try {
            String line = in.readLine(); // header
            while ((line = in.readLine()) != null) {
                if (line.trim().length() == 0) {
                    continue;
                }
                String[] f = line.split(",");
                out.put(Long.valueOf(Long.parseLong(f[0].trim())), Long.valueOf(Long.parseLong(f[1].trim())));
            }
        } finally {
            in.close();
        }
        return out;
    }
}
