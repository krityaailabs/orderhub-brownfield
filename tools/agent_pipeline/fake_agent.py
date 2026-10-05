"""A deterministic stand-in for a headless agent, for tests and demonstrations (Section 9).

A real run would call, for example:
  claude --bare -p "$(cat prompt.md)" --max-turns 20 --output-format json \
         --allowedTools "Read,Edit,Bash(make test-py),Bash(make lint)"
This script instead makes a scripted change in the current directory and prints the same kind of
JSON result line, including total_cost_usd, so the pipeline's guardrails can be exercised offline.

Options (combine freely):
  --patch FILE        apply a unified diff (git apply)
  --touch PATH        append one comment line to PATH (creating it if needed)
  --lines N           with --touch: append N lines instead of one
  --cost USD          reported cost (default 0.08); --no-cost reports none
  --sleep SECONDS     pretend to work for a while
  --exit CODE         exit with this code after making the changes
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--patch", action="append", default=[])
    ap.add_argument("--touch", action="append", default=[])
    ap.add_argument("--lines", type=int, default=1)
    ap.add_argument("--cost", type=float, default=0.08)
    ap.add_argument("--no-cost", action="store_true")
    ap.add_argument("--sleep", type=float, default=0)
    ap.add_argument("--exit", type=int, default=0)
    args = ap.parse_args(argv)
    for patch in args.patch:
        subprocess.run(["git", "apply", str(Path(patch).resolve())], check=True)
    for path in args.touch:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a") as handle:
            for i in range(args.lines):
                handle.write(f"# change {i + 1} by fake agent\n")
    time.sleep(args.sleep)
    result = {"type": "result", "result": "done", "num_turns": 3}
    if not args.no_cost:
        result["total_cost_usd"] = args.cost
    print(json.dumps(result))
    return args.exit


if __name__ == "__main__":
    sys.exit(main())
