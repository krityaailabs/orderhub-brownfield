"""Capstone check (Section 15): are the deliverables present, and do they meet the brief?

It checks the evidence, not the quality: a capstone can pass every check and still score low on
the rubric (labs/s15/rubric.md). Each check prints ok or the first thing that's missing.

Usage:
  python tools/capstone_check.py           structure and evidence checks
  python tools/capstone_check.py --full    also run the Python tests, the billing golden check and
                                           the security gate
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import spec_check  # noqa: E402

SPEC = ROOT / "docs" / "specs" / "loyalty.md"
PLAN = ROOT / "docs" / "specs" / "loyalty.plan.md"
PROGRESS = ROOT / "docs" / "specs" / "loyalty.progress.md"
TESTS = ROOT / "services" / "orders" / "tests" / "test_loyalty_acceptance.py"
REVIEW = ROOT / "docs" / "capstone" / "review.md"
METRICS = ROOT / "docs" / "capstone" / "metrics.md"
RETRO = ROOT / "docs" / "capstone" / "retro.md"
MIN_CRITERIA = 5


def _read(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def _has_headings(text: str, headings: list[str]) -> str | None:
    for h in headings:
        if not re.search(rf"^##\s+{re.escape(h)}\b", text, flags=re.M | re.I):
            return f"missing section '## {h}'"
    return None


def check_spec() -> str | None:
    text = _read(SPEC)
    if text is None:
        return f"missing {SPEC.relative_to(ROOT)}"
    problems = spec_check.check_spec(text)
    if problems:
        return problems[0]
    if len(spec_check.parse_criteria(text)) < MIN_CRITERIA:
        return f"fewer than {MIN_CRITERIA} acceptance criteria"
    return None


def check_plan() -> str | None:
    spec, plan = _read(SPEC), _read(PLAN)
    if plan is None:
        return f"missing {PLAN.relative_to(ROOT)}"
    ids = [c for c, _ in spec_check.parse_criteria(spec or "")]
    problems = spec_check.check_slices(spec_check.parse_slices(plan), ids)
    return problems[0] if problems else None


def check_progress() -> str | None:
    plan, progress = _read(PLAN) or "", _read(PROGRESS)
    if progress is None:
        return f"missing {PROGRESS.relative_to(ROOT)}"
    for s in spec_check.parse_slices(plan):
        if not re.search(rf"^\|\s*{s['id']}\s*\|\s*done\b", progress, flags=re.M | re.I):
            return f"slice {s['id']} not marked done"
    return None


def check_tests() -> str | None:
    text = _read(TESTS)
    if text is None:
        return f"missing {TESTS.relative_to(ROOT)}"
    names = re.findall(r"^def (test_\w+)", text, flags=re.M)
    for cid, _ in spec_check.parse_criteria(_read(SPEC) or ""):
        tag = "ac" + cid.split("-")[1] + "_"
        if not any(n.startswith("test_" + tag) for n in names):
            return f"no test named test_{tag}... for {cid}"
    return None


def check_review() -> str | None:
    text = _read(REVIEW)
    if text is None:
        return f"missing {REVIEW.relative_to(ROOT)}"
    return _has_headings(text, ["Pull requests", "Rejected attempt", "Findings by layer"])


def check_metrics() -> str | None:
    text = _read(METRICS)
    if text is None:
        return f"missing {METRICS.relative_to(ROOT)}"
    missing = _has_headings(text, ["Delivery", "Quality"])
    if missing:
        return missing
    rows = [r for r in text.splitlines() if r.startswith("|") and re.search(r"\d", r) and "---" not in r]
    return None if len(rows) >= 3 else "fewer than 3 table rows with numbers"


def check_retro() -> str | None:
    text = _read(RETRO)
    if text is None:
        return f"missing {RETRO.relative_to(ROOT)}"
    missing = _has_headings(text, ["What went well", "What didn't", "Context-file lines"])
    if missing:
        return missing
    section = re.split(r"^##\s+Context-file lines.*$", text, flags=re.M | re.I)[1]
    section = re.split(r"^##\s", section, flags=re.M)[0]
    return None if re.search(r"^\s*-\s+\S", section, flags=re.M) else "no context-file lines listed"


def check_agents_md() -> str | None:
    return None if "loyalty" in (ROOT / "AGENTS.md").read_text().lower() else "AGENTS.md doesn't mention loyalty"


CHECKS = [("spec", check_spec), ("plan", check_plan), ("progress", check_progress), ("tests", check_tests),
          ("review", check_review), ("metrics", check_metrics), ("retro", check_retro), ("context", check_agents_md)]
FULL = [("python tests", [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "services/orders/tests"]),
        ("billing golden", [sys.executable, "tools/billing_golden.py", "check"]),
        ("security gate", [sys.executable, "tools/security_gate.py"])]


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    passed = 0
    total = len(CHECKS)
    for name, fn in CHECKS:
        problem = fn()
        print(f"capstone: {'ok    ' if problem is None else 'MISSING'} {name}" + (f": {problem}" if problem else ""))
        passed += problem is None
    if "--full" in args:
        for name, command in FULL:
            total += 1
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            ok = result.returncode == 0
            last = (result.stdout.strip().splitlines() or [""])[-1]
            print(f"capstone: {'ok    ' if ok else 'FAILED'} {name}: {last}")
            passed += ok
    print(f"capstone: {passed} of {total} checks passed.")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
