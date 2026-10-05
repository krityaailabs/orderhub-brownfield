package com.orderhub.billing;

/** One row of the nightly handoff file written by the order service. */
public class OrderRecord {
    public final long orderId;
    public final String customerName;
    public final String country;
    public final String currency;
    public final long subtotalMinor;
    public final long totalMinor;

    public OrderRecord(long orderId, String customerName, String country, String currency,
                       long subtotalMinor, long totalMinor) {
        this.orderId = orderId;
        this.customerName = customerName;
        this.country = country;
        this.currency = currency;
        this.subtotalMinor = subtotalMinor;
        this.totalMinor = totalMinor;
    }
}
