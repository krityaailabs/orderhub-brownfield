package com.orderhub.billing;

/**
 * Seam for the tax calculation (Section 8, Project 2). The export asks the policy for each
 * record's tax, for the detail record and for the trailer total alike.
 */
public interface TaxPolicy {

    long tax(OrderRecord r);

    /** Number of records whose tax came from the new path (for the batch log). */
    int newPathCount();
}
