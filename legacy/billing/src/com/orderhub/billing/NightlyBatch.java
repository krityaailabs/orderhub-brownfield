package com.orderhub.billing;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Set;

/**
 * Nightly billing batch. Scheduled at 02:00 server time.
 * Usage: NightlyBatch <handoff-dir> <out-dir> <yyyy-MM-dd>
 * Optional: BILLING_NEW_TAX_COUNTRIES=JP,AU (or *) takes tax for those countries from
 * <handoff-dir>/tax_yyyyMMdd.csv (Project 2 strangler). Unset or empty: legacy calculation only.
 */
public class NightlyBatch {

    public static void main(String[] args) throws Exception {
        if (args.length != 3) {
            System.err.println("usage: NightlyBatch <handoff-dir> <out-dir> <yyyy-MM-dd>");
            System.exit(2);
        }
        Date day = new SimpleDateFormat("yyyy-MM-dd").parse(args[2]);
        String stamp = new SimpleDateFormat("yyyyMMdd").format(day);
        String in = args[0] + File.separator + "orders_" + stamp + ".csv";
        List<OrderRecord> records = HandoffReader.read(in);
        new File(args[1]).mkdirs();
        String out = args[1] + File.separator + "BILL" + stamp + ".DAT";
        TaxPolicy policy = new LegacyTaxPolicy();
        Set<String> countries = SwitchedTaxPolicy.parseCountries(System.getenv("BILLING_NEW_TAX_COUNTRIES"));
        if (!countries.isEmpty()) {
            String taxFile = args[0] + File.separator + "tax_" + stamp + ".csv";
            policy = new SwitchedTaxPolicy(countries, SwitchedTaxPolicy.readTaxFile(taxFile));
        }
        FixedWidthExport.write(records, day, out, policy);
        if (!countries.isEmpty()) {
            System.out.println("tax: new path for " + policy.newPathCount() + " of " + records.size() + " records");
        }
        System.out.println("wrote " + records.size() + " records to " + out);
    }
}
