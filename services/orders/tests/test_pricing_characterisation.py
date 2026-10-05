"""Characterisation (golden master) tests for the discount calculator (Lecture 4.7).

They pin what the code does today across a grid of inputs, so a refactor that changes any
result fails loudly. They don't say the results are right; the spec and ADR 0001 do that.
To regenerate after an intended change: UPDATE_GOLDEN=1 python -m pytest tests/test_pricing_characterisation.py
"""

import json
import os
from pathlib import Path

from orderhub import pricing

GOLDEN = Path(__file__).parent / "golden" / "discounts.json"
AMOUNTS = [0, 1, 3, 5, 49, 50, 99, 100, 101, 249, 999, 1001, 1748, 2475, 9100, 12345, 99999]
PERCENTS = [0, 1, 5, 10, 15, 25, 30, 33, 50, 90]


def current() -> dict[str, int]:
    return {f"{a}@{p}": pricing.apply_percentage_discount(a, p) for a in AMOUNTS for p in PERCENTS}


def test_discount_results_match_the_golden_master():
    if os.environ.get("UPDATE_GOLDEN") == "1":
        GOLDEN.write_text(json.dumps(current(), indent=0, sort_keys=True) + "\n", encoding="utf-8")
    expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
    actual = current()
    changed = {k: (expected.get(k), v) for k, v in actual.items() if expected.get(k) != v}
    assert not changed, f"{len(changed)} result(s) differ from the golden master, e.g. {list(changed.items())[:3]}"
