"""Comparison run for Project 2 (Lecture 8.8): old path vs new path, record by record.

Runs the legacy batch twice on the same recorded cases (legacy/billing/test/golden):
  old path: BILLING_NEW_TAX_COUNTRIES unset   (InvoiceCalculator in Java)
  new path: BILLING_NEW_TAX_COUNTRIES=<list>  (tax from tax_YYYYMMDD.csv, written by
            services/orders/orderhub/billing_tax.py)
and reports every record that differs. It also checks two things a byte comparison can miss:
  - the new path was actually used ("tax: new path for N of M records", N > 0), so a batch that
    ignores the switch can't pass by producing the old output twice
  - in each output, the trailer's gross total equals the sum of the detail records' gross amounts
    (finance rejects the file when they disagree; see the Section 8 incident)

Usage: python tools/billing_compare.py [COUNTRIES]     (default "*": route every country)
"""

import csv
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "services" / "orders"))

import billing_golden as bg  # noqa: E402
from orderhub import billing_tax  # noqa: E402

NEW_PATH = re.compile(r"tax: new path for (\d+) of (\d+) records")


def trailer_problems(data: bytes) -> list[str]:
    """Return problems if the trailer's count or gross total disagrees with the detail records."""
    records = [r.decode("iso-8859-1") for r in data.split(b"\r\n") if r]
    details = [r for r in records if r.startswith("D")]
    trailer = next((r for r in records if r.startswith("T")), None)
    if trailer is None:
        return ["no trailer record"]
    problems = []
    if int(trailer[1:7]) != len(details):
        problems.append(f"trailer count {int(trailer[1:7])} != {len(details)} detail records")
    gross_sum = sum(int(d[68:79]) for d in details)
    if int(trailer[7:20]) != gross_sum:
        problems.append(f"trailer gross {int(trailer[7:20])} != sum of detail gross {gross_sum}")
    return problems


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    countries = args[0] if args else "*"
    source = bg.GOLDEN / f"orders_{bg.STAMP}.csv"
    if not source.exists():
        print("compare: no recorded cases (run: python tools/billing_golden.py record)")
        return 1
    rows = source.read_text(encoding="utf-8").splitlines()
    cases = list(csv.DictReader(rows))
    classes = bg.build()
    tmp = Path(tempfile.mkdtemp(prefix="billing-compare-"))
    try:
        handoff = tmp / "handoff"
        handoff.mkdir()
        shutil.copy(source, handoff / source.name)
        tax_lines = ["order_id,tax_minor"] + [
            f"{c['order_id']},{billing_tax.tax_minor(int(c['total_minor']), c['country'])}" for c in cases]
        (handoff / f"tax_{bg.STAMP}.csv").write_text("\n".join(tax_lines) + "\n", encoding="utf-8")
        old, _ = bg.run_batch(classes, handoff, tmp / "old", env={"BILLING_NEW_TAX_COUNTRIES": ""})
        new, out = bg.run_batch(classes, handoff, tmp / "new", env={"BILLING_NEW_TAX_COUNTRIES": countries})
    finally:
        shutil.rmtree(classes, ignore_errors=True)
        shutil.rmtree(tmp, ignore_errors=True)
    failures = []
    m = NEW_PATH.search(out)
    routed = int(m.group(1)) if m else 0
    print(f"compare: new path used for {routed} of {len(cases)} records (BILLING_NEW_TAX_COUNTRIES={countries})")
    if routed == 0:
        failures.append("the new path was not used: does the batch read BILLING_NEW_TAX_COUNTRIES?")
    diffs = bg.diff_records(old, new, limit=10**6)
    print(f"compare: {len(diffs)} differing record(s)" + (" (first 5 shown)" if len(diffs) > 5 else ""))
    for d in diffs[:5]:
        print("  " + d.replace("\n", "\n  "))
    if diffs:
        failures.append("old and new outputs differ")
    for label, data in (("old", old), ("new", new)):
        for problem in trailer_problems(data):
            failures.append(f"{label} output: {problem}")
    for f in failures:
        print(f"compare: FAILED {f}")
    if not failures:
        print("compare: zero differences; trailers consistent.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
