"""Estimate model cost per task (Lecture 10.3). Prices are inputs: take them from the vendor's page.

Usage:
  python tools/eval_harness/cost_per_task.py --in-price 3 --out-price 15 --turns 12 \
      --in-tokens 18000 --out-tokens 900 [--cache-share 0.6 --cache-price 0.3] [--success-rate 0.8]
"""

import argparse
import sys


def cost_per_task(in_price: float, out_price: float, turns: int, in_tokens: int, out_tokens: int,
                  cache_share: float = 0.0, cache_price: float | None = None) -> float:
    """Prices are per million tokens. cache_share of input tokens are billed at cache_price."""
    cache_price = in_price if cache_price is None else cache_price
    per_turn_in = in_tokens * ((1 - cache_share) * in_price + cache_share * cache_price)
    return turns * (per_turn_in + out_tokens * out_price) / 1_000_000


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    for name in ("in-price", "out-price"):
        ap.add_argument(f"--{name}", type=float, required=True)
    ap.add_argument("--turns", type=int, required=True)
    ap.add_argument("--in-tokens", type=int, required=True)
    ap.add_argument("--out-tokens", type=int, required=True)
    ap.add_argument("--cache-share", type=float, default=0.0)
    ap.add_argument("--cache-price", type=float)
    ap.add_argument("--success-rate", type=float)
    a = ap.parse_args(argv)
    cost = cost_per_task(a.in_price, a.out_price, a.turns, a.in_tokens, a.out_tokens, a.cache_share, a.cache_price)
    print(f"cost per task: ${cost:.3f}")
    if a.success_rate:
        print(f"cost per successful task: ${cost / a.success_rate:.3f} (success rate {a.success_rate:.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
