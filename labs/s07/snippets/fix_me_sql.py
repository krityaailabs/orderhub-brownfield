# Labelled example for Lab s07: CWE-89 (SQL injection). Scanner rule: ruff S608.
# Not used by OrderHub. Fix it so the scanner is clean and tests/test_snippets pass.
import sqlite3


def customers_in_country(conn: sqlite3.Connection, country: str) -> list[tuple[int, str]]:
    """Return (id, name) of customers in a country, ordered by id."""
    query = f"SELECT id, name FROM customers WHERE country = '{country}' ORDER BY id"
    return conn.execute(query).fetchall()
