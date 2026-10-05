"""Lab s07 (Lecture 7.6): fix the two labelled snippets so the scanner is clean and they still work."""

import sqlite3
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNIPPETS = ROOT / "labs" / "s07" / "snippets"
sys.path.insert(0, str(SNIPPETS))

import fix_me_shell  # noqa: E402
import fix_me_sql  # noqa: E402


def test_the_two_fixed_snippets_have_no_security_findings():
    result = subprocess.run([sys.executable, "-m", "ruff", "check", "--select", "S", "--output-format", "concise",
                             str(SNIPPETS / "fix_me_sql.py"), str(SNIPPETS / "fix_me_shell.py")],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout


def test_labelled_examples_still_show_their_finding():
    result = subprocess.run([sys.executable, "-m", "ruff", "check", "--select", "S", "--output-format", "concise",
                             str(SNIPPETS)], capture_output=True, text=True, check=False)
    for rule in ("S301", "S324", "S105", "S501"):
        assert rule in result.stdout


def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, country TEXT)")
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?)",
                     [(1, "Aiko", "JP"), (2, "Ben", "GB"), (3, "Chloé O'Neil", "FR"), (4, "Kenji", "JP")])
    return conn


def test_sql_snippet_returns_the_right_rows():
    assert fix_me_sql.customers_in_country(db(), "JP") == [(1, "Aiko"), (4, "Kenji")]


def test_sql_snippet_treats_input_as_data():
    # A quote in the input must be data, not SQL: the f-string version fails with a syntax error.
    assert fix_me_sql.customers_in_country(db(), "O'Neil") == []


def test_shell_snippet_creates_the_archive_and_treats_names_as_data(tmp_path):
    folder = tmp_path / "handoff"
    folder.mkdir()
    (folder / "orders 2026;x.csv").write_text("order_id\n1\n")
    dest = tmp_path / "out.tar.gz"
    fix_me_shell.archive_handoff(str(folder), "orders 2026;x.csv", str(dest))
    with tarfile.open(dest) as archive:
        assert archive.getnames() == ["orders 2026;x.csv"]
