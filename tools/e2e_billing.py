"""End to end: place sample orders, write the CSV handoff, run the legacy Java batch.

Usage: python tools/e2e_billing.py   (or: make billing-demo)
Writes into ./out/ (git-ignored).
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "services" / "orders"))

from orderhub import orders, seed  # noqa: E402
from orderhub.db import Base, make_engine, make_session_factory  # noqa: E402


def main() -> int:
    engine = make_engine("sqlite://")
    Base.metadata.create_all(engine)
    out = ROOT / "out"
    with make_session_factory(engine)() as session:
        seed.load(session)
        orders.place_order(session, 5, [{"sku": "MUG-350", "quantity": 2}], "USD")
        orders.place_order(session, 3, [{"sku": "DESK-LAMP", "quantity": 1}], "USD", "WELCOME15")
        orders.place_order(session, 1, [{"sku": "NB-A5", "quantity": 3}], "USD")
        today = datetime.now(timezone.utc).date()
        handoff = orders.write_billing_handoff(session, today, str(out / "handoff"))
    print("handoff:", handoff.relative_to(ROOT))
    run = subprocess.run(
        [
            str(ROOT / "legacy" / "billing" / "run_batch.sh"),
            str(out / "handoff"),
            str(out / "billing"),
            today.isoformat(),
        ],
        capture_output=True,
        text=True,
    )
    print(run.stdout.strip())
    if run.returncode != 0:
        print(run.stderr)
        return run.returncode
    dat = next((out / "billing").glob("BILL*.DAT"))
    data = dat.read_bytes()
    records = data.split(b"\r\n")[:-1]
    print(f"{dat.name}: {len(records)} records, {len(data)} bytes, record lengths {sorted({len(r) for r in records})}")
    for r in records:
        print("  " + r.decode("iso-8859-1"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
