"""Dependency-bump job (Lecture 9.5): one patch-level bump per run, through the pipeline.

Success criteria for the PR it opens: the lock file changes by exactly one line; the bump is
patch-level (same major.minor); the dependency audit passes; and, in CI, the full test suite,
the billing golden check and the security gate pass with the new version installed.

The job doesn't need a language model at all: choosing and applying a bump is deterministic.
That's the point of the lecture: automate toil with the simplest tool that meets the criteria,
and keep the same guardrails (scope, budget, dedup, required checks, human merge gate).
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AVAILABLE = Path(__file__).with_name("available_versions.json")


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_version(text: str) -> tuple[int, ...] | None:
    """(major, minor, patch, ...) for a plain numeric version like "2.1.3"; None for anything else
    (pre-releases like "2.1.5b1" or "10.0.0rc1", post-releases like "2.9.0.post0", local versions)."""
    if not re.fullmatch(r"\d+(\.\d+)+", text):
        return None
    return tuple(int(x) for x in text.split("."))


def choose_bump(lock_text: str, available: dict[str, list[str]], hold: list[str] = ()) -> tuple[str, str, str] | None:
    """Return (name, current, new) for the single patch-level bump this run should make, or None.

    Rules:
      - go through requirements.lock lines in file order ("name==version"; skip blanks and comments)
      - skip packages in `hold` (compare names with _norm, so "SQLAlchemy" matches "sqlalchemy")
      - look the package up in `available` by _norm(name); missing means no candidates
      - a candidate is a version that parse_version() accepts, has the same major and minor as the
        current version, and is greater than it (compare the parsed tuples, not strings: "0.16.10" > "0.16.9")
      - choose the highest candidate for that package
      - return the first package, in file order, that has a candidate; the name as written in the lock
    """
    raise NotImplementedError("Lab s09: implement choose_bump")


def apply_bump(lock_text: str, name: str, new: str) -> str:
    """Replace exactly one line "name==old" with "name==new"."""
    pattern = re.compile(rf"^{re.escape(name)}==\S+$", flags=re.M)
    updated, count = pattern.subn(f"{name}=={new}", lock_text)
    if count != 1:
        raise ValueError(f"expected exactly one line for {name}, found {count}")
    return updated


def main(argv: list[str] | None = None) -> int:
    """`python dep_bump.py apply` (run by the pipeline inside its worktree) applies the chosen bump."""
    args = sys.argv[1:] if argv is None else argv
    lock = Path("requirements.lock")
    available = json.loads(AVAILABLE.read_text())
    hold = [h for h in args[1:]] if len(args) > 1 else []
    choice = choose_bump(lock.read_text(), available, hold)
    if choice is None:
        print(json.dumps({"type": "result", "result": "nothing to bump", "total_cost_usd": 0.0}))
        return 0
    name, old, new = choice
    lock.write_text(apply_bump(lock.read_text(), name, new))
    print(json.dumps({"type": "result", "result": f"{name} {old} -> {new}", "total_cost_usd": 0.0}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
