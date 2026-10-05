package com.orderhub.billing;

/** Minimal self-test, run by build.sh. Added in 2019; nobody has extended it since. */
public class BillingSelfTest {

    private static int failures = 0;

    private static void check(String name, boolean ok) {
        System.out.println((ok ? "PASS " : "FAIL ") + name);
        if (!ok) {
            failures++;
        }
    }

    public static void main(String[] args) {
        check("UK tax is 20 percent", InvoiceCalculator.tax(1000, "GB") == 200);
        check("unknown country has no tax", InvoiceCalculator.tax(1000, "ZZ") == 0);
        OrderRecord r = new OrderRecord(42, "Emma Clarke", "GB", "USD", 1250, 1250);
        check("detail record is 80 characters", FixedWidthExport.detail(r).length() == 80);
        check("detail record starts with D and padded id", FixedWidthExport.detail(r).startsWith("D0000000042"));
        if (failures > 0) {
            System.out.println(failures + " check(s) failed");
            System.exit(1);
        }
        System.out.println("all checks passed");
    }
}
