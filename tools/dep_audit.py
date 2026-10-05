"""Dependency audit for the CI security gate (Lecture 7.4).

Checks requirements.lock against ADR 0002:
  1. Every line pins an exact version (name==version). Ranges make builds unreproducible and let
     an unreviewed major version in (the R9 pull request in Section 6).
  2. Every package that isn't in the original baseline (tools/dep_baseline.txt) has a row in
     docs/dependencies.md, naming why it's needed and who approved it.
  3. No newly added package duplicates the job of one already locked (for example a second HTTP
     client), using the same families as tools/review_flags.py.

What it can't tell you: whether a package name is the one you meant, whether it's maintained, or
whether its latest release is trustworthy. Those are the three questions of the audit worksheet
(docs/course/dependency-audit.md), and they need a person and the package's real page.

Usage: python tools/dep_audit.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from review_flags import FAMILIES, _norm  # noqa: E402

PIN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*==[A-Za-z0-9.+!_-]+$")


def audit(lock_text: str, baseline_text: str, decisions_text: str) -> list[str]:
    problems: list[str] = []
    names: list[str] = []
    for line in lock_text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        if not PIN.match(line):
            problems.append(f"not pinned exactly: {line}")
        names.append(_norm(re.split(r"[=<>!~\[ ;]", line, maxsplit=1)[0]))
    baseline = {_norm(n.strip()) for n in baseline_text.splitlines() if n.strip() and not n.startswith("#")}
    decisions = _norm(decisions_text)
    added = [n for n in names if n not in baseline]
    for name in added:
        if not re.search(rf"(^|[^a-z0-9-]){re.escape(name)}([^a-z0-9-]|$)", decisions):
            problems.append(f"no decision recorded in docs/dependencies.md: {name}")
    for family, members in FAMILIES.items():
        for name in added:
            if name in members:
                others = sorted((set(names) - {name}) & members)
                if others:
                    problems.append(f"duplicate {family}: {name} added; already have {', '.join(others)}")
    return problems


def main() -> int:
    problems = audit((ROOT / "requirements.lock").read_text(), (ROOT / "tools" / "dep_baseline.txt").read_text(),
                     (ROOT / "docs" / "dependencies.md").read_text())
    for p in problems:
        print(f"DEPENDENCY  {p}")
    print(f"dep-audit: {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
