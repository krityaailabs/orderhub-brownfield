package com.orderhub.billing;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

/** Reads orders_YYYYMMDD.csv. Header line is skipped. */
public class HandoffReader {

    public static List<OrderRecord> read(String path) throws IOException {
        List<OrderRecord> out = new ArrayList<OrderRecord>();
        BufferedReader in = new BufferedReader(new InputStreamReader(new FileInputStream(path), "UTF-8"));
        try {
            String line = in.readLine(); // header
            while ((line = in.readLine()) != null) {
                if (line.trim().length() == 0) {
                    continue;
                }
                String[] f = line.split(",");
                out.add(new OrderRecord(Long.parseLong(f[0]), f[1], f[2], f[3],
                        Long.parseLong(f[4]), Long.parseLong(f[5])));
            }
        } finally {
            in.close();
        }
        return out;
    }
}
