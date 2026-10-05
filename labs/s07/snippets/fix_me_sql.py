# Labelled example for Lab s07: CWE-89 (SQL injection). Scanner rule: ruff S608.
# Fixed: the value is passed as a query parameter, so the database treats it as data, never as SQL.
import sqlite3


def customers_in_country(conn: sqlite3.Connection, country: str) -> list[tuple[int, str]]:
    """Return (id, name) of customers in a country, ordered by id."""
    return conn.execute("SELECT id, name FROM customers WHERE country = ? ORDER BY id", (country,)).fetchall()
