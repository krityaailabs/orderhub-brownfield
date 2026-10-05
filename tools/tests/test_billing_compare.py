"""Lab s08 (Project 2): old and new tax paths give byte-identical exports for every recorded case."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import billing_compare  # noqa: E402

DETAIL = ("D" + "0000000001" + "Emma Clarke".ljust(30) + "GB" + "USD" + "00000001000" + "00000000200"
          + "00000001200")


def test_trailer_check_accepts_a_consistent_file_and_rejects_a_wrong_total():
    good = ("H150126ORDERHUB".ljust(80) + "\r\n" + DETAIL.ljust(80) + "\r\n"
            + ("T" + "000001" + "0000000001200").ljust(80) + "\r\n").encode("iso-8859-1")
    assert billing_compare.trailer_problems(good) == []
    bad = good.replace(b"T0000010000000001200", b"T0000010000000001201")
    assert billing_compare.trailer_problems(bad) == ["trailer gross 1201 != sum of detail gross 1200"]


def test_old_and_new_paths_are_identical_for_all_countries(capsys):
    assert billing_compare.main(["*"]) == 0
    out = capsys.readouterr().out
    assert "new path used for 50 of 50 records" in out
    assert "zero differences" in out
