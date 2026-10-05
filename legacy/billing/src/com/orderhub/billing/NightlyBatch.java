package com.orderhub.billing;

import java.io.File;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

/**
 * Nightly billing batch. Scheduled at 02:00 server time.
 * Usage: NightlyBatch <handoff-dir> <out-dir> <yyyy-MM-dd>
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
        FixedWidthExport.write(records, day, out);
        System.out.println("wrote " + records.size() + " records to " + out);
    }
}
