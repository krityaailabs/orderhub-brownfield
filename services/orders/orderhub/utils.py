"""Assorted helpers. Some of these predate pricing.py."""


def money_str(minor: int, currency: str = "USD") -> str:
    # TODO: replace with pricing.format_money (duplicate helper, kept for the CSV handoff).
    return "%.2f %s" % (minor / 100.0, currency)


def normalise_sku(sku: str) -> str:
    return sku.strip().upper()
