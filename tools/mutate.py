"""A small, dependency-free mutation tester for the course labs.

It applies one source mutation at a time, runs the chosen tests, and reports whether the tests
noticed (killed the mutant) or not (the mutant survived). Files are always restored.

Usage:
    python tools/mutate.py                         # default mutants, acceptance + property tests
    python tools/mutate.py --tests tests/test_returns_acceptance.py

A surviving mutant is a change to the code that your tests cannot tell apart from the original.
Some survivors are harmless (equivalent mutants); each one deserves a look.
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "services" / "orders"


@dataclass(frozen=True)
class Mutant:
    name: str
    path: str  # relative to services/orders
    old: str
    new: str


MUTANTS = [
    Mutant(
        "rounding: half-up becomes floor",
        "orderhub/pricing.py",
        "share = (2 * discount * value + subtotal_minor) // (2 * subtotal_minor)",
        "share = (2 * discount * value) // (2 * subtotal_minor)",
    ),
    Mutant("discount share ignored", "orderhub/pricing.py", "return value - share", "return value"),
    Mutant(
        "value ignores quantity",
        "orderhub/pricing.py",
        "    value = unit_price_minor * quantity\n    discount =",
        "    value = unit_price_minor\n    discount =",
    ),
    Mutant(
        "partial refund uses the whole order's discount",
        "orderhub/pricing.py",
        "    discount = subtotal_minor - total_minor\n    share",
        "    discount = subtotal_minor - total_minor\n    value = max(value, subtotal_minor)\n    share",
    ),
    Mutant("remainder rule removed", "orderhub/orders.py", "if remaining_after == 0:", "if remaining_after < 0:"),
    Mutant(
        "window boundary: >= becomes >",
        "orderhub/orders.py",
        "if now >= _as_utc(order.created_at) + RETURN_WINDOW:",
        "if now > _as_utc(order.created_at) + RETURN_WINDOW:",
    ),
    Mutant("restock removed", "orderhub/orders.py", "line.product.stock += qty", "line.product.stock += 0"),
    Mutant(
        "status check accepts PLACED",
        "orderhub/orders.py",
        'if order.status != "SHIPPED":\n        raise Conflict(f"only SHIPPED',
        'if order.status == "CANCELLED":\n        raise Conflict(f"only SHIPPED',
    ),
]

DEFAULT_TESTS = sorted(str(p.relative_to(SERVICE)) for p in (SERVICE / "tests").glob("test_returns_*.py"))


def run_tests(tests: list[str]) -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "-p", "no:cacheprovider", *tests],
        cwd=SERVICE,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the course mutation tests.")
    parser.add_argument("--tests", nargs="+", default=DEFAULT_TESTS, help="test files, relative to services/orders")
    args = parser.parse_args(argv)
    if not run_tests(args.tests):
        print("The tests fail on the unmutated code. Fix them first.")
        return 2
    survived, skipped = [], []
    for m in MUTANTS:
        path = SERVICE / m.path
        original = path.read_text(encoding="utf-8")
        if original.count(m.old) != 1:
            print(f"SKIP      {m.name} (pattern not found exactly once)")
            skipped.append(m.name)
            continue
        try:
            path.write_text(original.replace(m.old, m.new), encoding="utf-8")
            killed = not run_tests(args.tests)
        finally:
            path.write_text(original, encoding="utf-8")
        print(f"{'killed  ' if killed else 'SURVIVED'}  {m.name}")
        if not killed:
            survived.append(m.name)
    total = len(MUTANTS) - len(skipped)
    killed_count = total - len(survived)
    print(
        f"\n{killed_count} of {total} mutants killed ({100 * killed_count // max(total, 1)}%)"
        + (f"; {len(skipped)} skipped" if skipped else "")
        + "."
    )
    return 1 if survived or skipped else 0


if __name__ == "__main__":
    sys.exit(main())
