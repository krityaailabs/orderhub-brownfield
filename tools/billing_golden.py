"""Characterisation (golden master) tests for the legacy billing batch (Lab s08, Lecture 8.3).

Pins what the legacy batch does today, byte for byte, for a recorded set of invoice cases, before
anyone refactors it. The recorded files live in legacy/billing/test/golden/:

  orders_20260115.csv   the input: 50 cases in the handoff format the batch reads
  BILL20260115.DAT      the output the legacy batch produced for them (ISO-8859-1, CRLF)

Usage:
  python tools/billing_golden.py record     run the batch on cases() and (re)write both files
  python tools/billing_golden.py check      run the batch on the recorded input; compare bytes
  python tools/billing_golden.py check --release 11   same, compiled with javac --release 11

Re-record only when a change to the output is intended and agreed with finance, and say so in the
commit message. A failing check means the batch's behaviour changed.
"""

import csv
import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BILLING = ROOT / "legacy" / "billing"
GOLDEN = BILLING / "test" / "golden"
DAY = "2026-01-15"
STAMP = "20260115"
HEADER = ["order_id", "customer_name", "country", "currency", "subtotal_minor", "total_minor"]
LEGACY_RATES = {"GB": 2000, "FR": 2000, "IT": 2200, "IN": 1800, "AE": 500, "AU": 1000, "JP": 1000, "NG": 750}


def cases() -> list[dict]:
    """Return exactly 50 invoice cases (dicts with the HEADER keys), deterministic, covering:

      - order_id 1 to 50, in order; currency "USD"; subtotal_minor >= total_minor >= 0
      - every country in LEGACY_RATES at least twice, plus at least two countries with no rate
        (for example "US" and "ZZ")
      - for each of JP, AU, IN and NG, at least one exact half-way case: total_minor * rate % 10000
        == 5000 (where HALF_EVEN and HALF_UP give different answers)
      - total_minor of 0 at least once, and 99_999_999 (the largest 8-digit amount) at least once
      - a customer_name longer than 30 characters (the export truncates at 30)
      - a customer_name with Latin-1 accents (for example "Chloé Dubois", "Søren Østergaard")
      - a customer_name with characters outside Latin-1 (for example "田中 花子"): the export is
        ISO-8859-1, so they can't be written as they are
      - no customer_name containing a comma (see the billing map: the batch splits on commas)

    Tip: build the special cases first, then fill the rest with a simple, readable pattern. Don't
    use random numbers: the cases must be identical on every run."""
    raise NotImplementedError("Lab s08: design the 50 golden cases")


def handoff_csv(rows: list[dict]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(HEADER)
    for row in rows:
        writer.writerow([row[h] for h in HEADER])
    return buffer.getvalue()


def build(release: str | None = None) -> Path:
    """Compile the legacy batch into a temporary folder and return the classes directory."""
    out = Path(tempfile.mkdtemp(prefix="billing-classes-"))
    sources = [str(p) for p in sorted((BILLING / "src").rglob("*.java"))]
    rel = release or os.environ.get("JAVA_RELEASE", "8")
    subprocess.run(["javac", "-nowarn", "-Xlint:-options", "--release", rel, "-encoding", "UTF-8", "-d", str(out),
                    *sources], check=True, capture_output=True, text=True)
    return out


def run_batch(classes: Path, handoff_dir: Path, out_dir: Path, env: dict | None = None) -> tuple[bytes, str]:
    """Run NightlyBatch for DAY; return (DAT bytes, stdout)."""
    result = subprocess.run(["java", "-cp", str(classes), "com.orderhub.billing.NightlyBatch", str(handoff_dir),
                             str(out_dir), DAY], capture_output=True, text=True,
                            env={**os.environ, **(env or {})})
    if result.returncode != 0:
        raise RuntimeError(f"batch failed ({result.returncode}): {result.stderr.strip()[-400:]}")
    return (out_dir / f"BILL{STAMP}.DAT").read_bytes(), result.stdout


def diff_records(expected: bytes, actual: bytes, limit: int = 5) -> list[str]:
    exp, act = expected.split(b"\r\n"), actual.split(b"\r\n")
    lines = []
    for i in range(max(len(exp), len(act))):
        e = exp[i] if i < len(exp) else b"<missing>"
        a = act[i] if i < len(act) else b"<missing>"
        if e != a:
            lines.append(f"record {i + 1}:\n  expected {e.decode('iso-8859-1')}\n  actual   {a.decode('iso-8859-1')}")
    return lines[:limit] + ([f"... and {len(lines) - limit} more"] if len(lines) > limit else [])


def record() -> int:
    rows = cases()
    GOLDEN.mkdir(parents=True, exist_ok=True)
    (GOLDEN / f"orders_{STAMP}.csv").write_text(handoff_csv(rows), encoding="utf-8")
    classes = build()
    with tempfile.TemporaryDirectory() as tmp:
        data, out = run_batch(classes, GOLDEN, Path(tmp))
    shutil.rmtree(classes, ignore_errors=True)
    (GOLDEN / f"BILL{STAMP}.DAT").write_bytes(data)
    print(f"recorded {len(rows)} cases; {out.strip()}; {len(data)} bytes")
    return 0


def check(release: str | None = None) -> int:
    expected_path = GOLDEN / f"BILL{STAMP}.DAT"
    if not expected_path.exists():
        print("golden: nothing recorded yet (run: python tools/billing_golden.py record)")
        return 1
    classes = build(release)
    with tempfile.TemporaryDirectory() as tmp:
        actual, _ = run_batch(classes, GOLDEN, Path(tmp))
    shutil.rmtree(classes, ignore_errors=True)
    expected = expected_path.read_bytes()
    if actual == expected:
        count = len(expected.split(b"\r\n")) - 1
        print(f"golden: {count} records identical (javac --release {release or '8'})")
        return 0
    print("golden: OUTPUT CHANGED")
    print("\n".join(diff_records(expected, actual)))
    return 1


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["record"]:
        return record()
    if args[:1] == ["check"]:
        release = args[2] if args[1:2] == ["--release"] and len(args) > 2 else None
        return check(release)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
