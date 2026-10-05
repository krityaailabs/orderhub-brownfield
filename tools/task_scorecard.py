"""Task-suitability scorecard: is this task agent-shaped?

Score six criteria from 0 to 2 and get a recommended way of working and autonomy level.
The scorecard supports a decision; it does not make it.

Usage:
    python tools/task_scorecard.py --spec 2 --verify 2 --blast 1 --context 2 --review 2 --novelty 1
"""

import argparse
import sys
from dataclasses import dataclass

CRITERIA = {
    "spec": "Spec clarity: are there testable acceptance criteria?",
    "verify": "Verifiability: can tests decide when it is done?",
    "blast": "Blast radius: 2 = small and reversible, 0 = money, security, data or external contracts",
    "context": "Context: are conventions written down, or is there an existing pattern to follow?",
    "review": "Review cost: 2 = small diff a human can review quickly",
    "novelty": "Familiarity: 2 = well-trodden pattern, 0 = new design work",
}


@dataclass(frozen=True)
class Recommendation:
    total: int
    mode: str
    autonomy: str
    reasons: tuple[str, ...]


def score(spec: int, verify: int, blast: int, context: int, review: int, novelty: int) -> Recommendation:
    values = {"spec": spec, "verify": verify, "blast": blast, "context": context, "review": review,
              "novelty": novelty}
    for name, value in values.items():
        if value not in (0, 1, 2):
            raise ValueError(f"{name} must be 0, 1 or 2, got {value!r}")
    total = sum(values.values())
    reasons: list[str] = []

    if total >= 9:
        mode, autonomy = "agent", "L2-L3"
    elif total >= 6:
        mode, autonomy = "agent with close supervision", "L1-L2"
    else:
        mode, autonomy = "human leads, agent assists", "L0-L1"

    # Caps: some single criteria outweigh the total.
    if blast == 0 and mode != "human leads, agent assists":
        mode, autonomy = "agent with close supervision", "L1-L2"
        reasons.append("blast radius is high: a human approves every step")
    if verify == 0:
        mode, autonomy = "human leads, agent assists", "L0-L1"
        reasons.append("nothing can verify the result: add a test or another check first, then re-score")
    if spec == 0 and verify > 0:
        reasons.append("no acceptance criteria: write the spec before handing it over")
    if review == 0:
        reasons.append("the diff will be hard to review: slice the task first")
    return Recommendation(total, mode, autonomy, tuple(reasons))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name, help_text in CRITERIA.items():
        parser.add_argument(f"--{name}", type=int, required=True, help=help_text)
    args = parser.parse_args(argv)
    rec = score(args.spec, args.verify, args.blast, args.context, args.review, args.novelty)
    print(f"total {rec.total}/12 -> {rec.mode} (autonomy {rec.autonomy})")
    for reason in rec.reasons:
        print(f"  - {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
