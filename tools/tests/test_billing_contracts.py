"""Implicit contracts of the legacy billing export (Lecture 8.6): one test per contract.

Each test runs the real batch on a small handoff file. See docs/legacy/implicit-contracts.md."""

import shutil
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import billing_golden as bg  # noqa: E402
from billing_compare import trailer_problems  # noqa: E402


@pytest.fixture(scope="module")
def classes():
    out = bg.build()
    yield out
    shutil.rmtree(out, ignore_errors=True)


def export(classes, rows):
    tmp = Path(tempfile.mkdtemp())
    try:
        (tmp / "h").mkdir()
        full = [{"order_id": i + 1, "currency": "USD", "subtotal_minor": r[2], "total_minor": r[2],
                 "customer_name": r[0], "country": r[1]} for i, r in enumerate(rows)]
        (tmp / "h" / f"orders_{bg.STAMP}.csv").write_text(bg.handoff_csv(full), encoding="utf-8")
        data, _ = bg.run_batch(classes, tmp / "h", tmp / "o")
        return data
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def details(data):
    return [r for r in data.split(b"\r\n") if r.startswith(b"D")]


def test_every_record_is_80_characters_with_crlf(classes):
    data = export(classes, [("Emma Clarke", "GB", 1250), ("Ben Carter", "US", 99)])
    assert data.endswith(b"\r\n") and b"\n" not in data.replace(b"\r\n", b"")
    assert {len(r) for r in data.split(b"\r\n")[:-1]} == {80}


def test_encoding_is_iso_8859_1(classes):
    data = export(classes, [("Søren Østergaard", "DK", 100), ("田中 花子", "JP", 100)])
    first, second = details(data)
    assert first[11:27] == "Søren Østergaard".encode("iso-8859-1")
    assert second[11:16] == b"?? ??"


def test_long_names_are_truncated_to_30(classes):
    (record,) = details(export(classes, [("Bartholomew Montgomery-Fitzwilliam", "GB", 100)]))
    assert record[11:41] == b"Bartholomew Montgomery-Fitzwil" and record[41:43] == b"GB"


def test_amount_fields_are_11_digits(classes):
    (record,) = details(export(classes, [("A", "GB", 99_999_999)]))
    assert record[46:57] == b"00099999999" and record[57:68] == b"00020000000" and record[68:79] == b"00119999999"


@pytest.mark.parametrize("country,net,tax", [("JP", 1005, b"00000000100"), ("JP", 1015, b"00000000102"),
                                             ("IN", 25, b"00000000004"), ("NG", 20, b"00000000002")])
def test_tax_rounds_half_even(classes, country, net, tax):
    (record,) = details(export(classes, [("A", country, net)]))
    assert record[57:68] == tax


def test_unknown_country_pays_no_tax(classes):
    (record,) = details(export(classes, [("A", "US", 5000)]))
    assert record[57:68] == b"00000000000" and record[68:79] == b"00000005000"


def test_header_date_is_ddmmyy(classes):
    assert export(classes, [("A", "GB", 1)]).startswith(b"H150126ORDERHUB ")


def test_trailer_matches_details(classes):
    data = export(classes, [("A", "GB", 1250), ("B", "JP", 1005), ("C", "ZZ", 7)])
    assert trailer_problems(data) == []
    assert data.split(b"\r\n")[-2][:20] == b"T0000030000000002612"


def test_records_keep_input_order(classes):
    ids = [r[1:11] for r in details(export(classes, [("A", "GB", 1), ("B", "FR", 2), ("C", "IT", 3)]))]
    assert ids == [b"0000000001", b"0000000002", b"0000000003"]


def test_comma_in_a_name_stops_the_batch_known_issue_q16(classes):
    # Pins current behaviour (Q16), so a fix is a visible, intended change. Not a requirement.
    with pytest.raises(RuntimeError, match="NumberFormatException"):
        export(classes, [("Smith, John", "GB", 1000)])
