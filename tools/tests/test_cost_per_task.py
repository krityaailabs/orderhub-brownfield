import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval_harness"))

from cost_per_task import cost_per_task  # noqa: E402


def test_cost_without_cache():
    assert round(cost_per_task(3.0, 15.0, 10, 20_000, 1_000), 4) == 0.75


def test_cache_reduces_input_cost():
    assert round(cost_per_task(3.0, 15.0, 10, 20_000, 1_000, cache_share=0.5, cache_price=0.3), 4) == 0.48
