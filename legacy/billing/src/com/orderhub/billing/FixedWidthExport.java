package com.orderhub.billing;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

/** Writes the fixed-width file collected by the finance system at 04:00. */
public class FixedWidthExport {

    static final int RECORD_LENGTH = 80;

    public static String header(Date businessDate) {
        return pad("H" + new SimpleDateFormat("ddMMyy").format(businessDate) + "ORDERHUB", RECORD_LENGTH);
    }

    public static String detail(OrderRecord r) {
        long tax = InvoiceCalculator.tax(r.totalMinor, r.country);
        long gross = r.totalMinor + tax;
        StringBuilder sb = new StringBuilder();
        sb.append("D");
        sb.append(zero(r.orderId, 10));
        sb.append(fit(r.customerName, 30));
        sb.append(fit(r.country, 2));
        sb.append(fit(r.currency, 3));
        sb.append(zero(r.totalMinor, 11));
        sb.append(zero(tax, 11));
        sb.append(zero(gross, 11));
        return pad(sb.toString(), RECORD_LENGTH);
    }

    public static String trailer(int count, long grossSum) {
        return pad("T" + zero(count, 6) + zero(grossSum, 13), RECORD_LENGTH);
    }

    public static void write(List<OrderRecord> records, Date businessDate, String path) throws IOException {
        Writer w = new OutputStreamWriter(new FileOutputStream(path), "ISO-8859-1");
        try {
            w.write(header(businessDate));
            w.write("\r\n");
            long sum = 0;
            for (OrderRecord r : records) {
                w.write(detail(r));
                w.write("\r\n");
                sum += InvoiceCalculator.gross(r.totalMinor, r.country);
            }
            w.write(trailer(records.size(), sum));
            w.write("\r\n");
        } finally {
            w.close();
        }
    }

    static String zero(long value, int width) {
        String s = Long.toString(value);
        while (s.length() < width) {
            s = "0" + s;
        }
        return s;
    }

    static String fit(String value, int width) {
        if (value.length() > width) {
            return value.substring(0, width);
        }
        return pad(value, width);
    }

    static String pad(String value, int width) {
        StringBuilder sb = new StringBuilder(value);
        while (sb.length() < width) {
            sb.append(' ');
        }
        return sb.toString();
    }
}
