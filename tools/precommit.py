"""Run the checks that matter for the files a commit changes.

Used by the git pre-commit hook (tools/hooks/pre-commit, installed with `make install-hooks`) and
callable by any agent's hook. Fast by design: it runs only the checks the changed paths need.

Usage: python tools/precommit.py            (checks staged files)
       python tools/precommit.py FILE...     (checks the given files)
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

CHECKS = {
    "lint": [PY, "-m", "ruff", "check", "services/orders", "tools"],
    "python-tests": [PY, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "services/orders/tests",
                     "--ignore=services/orders/tests/test_returns_properties.py"],
    "tool-tests": [PY, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tools/tests"],
    "java": ["legacy/billing/build.sh"],
    "billing-demo": [PY, "tools/e2e_billing.py"],
    "context": [PY, "tools/context_check.py"],
    "specs": [PY, "tools/spec_check.py"],
    "protect-tests": [PY, "tools/protect_tests.py"],
}
ORDER = list(CHECKS)


def select_checks(paths: list[str]) -> list[str]:
    """Return the names of the checks to run for the changed paths, in ORDER, without duplicates.

    Rules (paths are repository-relative, POSIX style):
      - any .py file                                 -> lint
      - under services/orders/                       -> python-tests
      - under tools/                                 -> tool-tests
      - under legacy/billing/                        -> java and billing-demo
      - services/orders/orderhub/orders.py           -> billing-demo (it writes the handoff)
      - an AGENTS.md, CLAUDE.md or .github/copilot-instructions.md -> context
      - under docs/specs/                            -> specs
      - under any tests/ or test/ directory          -> protect-tests
    Paths that match nothing need no checks."""
    raise NotImplementedError("Lab s05: implement select_checks")


def staged_files() -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], cwd=ROOT,
                         capture_output=True, text=True, check=False).stdout
    return [line for line in out.splitlines() if line]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    paths = argv or staged_files()
    checks = select_checks(paths)
    if not checks:
        print("precommit: no checks needed for these files.")
        return 0
    failed = []
    for name in checks:
        result = subprocess.run(CHECKS[name], cwd=ROOT, capture_output=True, text=True, check=False)
        print(f"precommit: {'ok    ' if result.returncode == 0 else 'FAILED'} {name}")
        if result.returncode != 0:
            failed.append(name)
            tail = (result.stdout + result.stderr).strip().splitlines()[-8:]
            print("\n".join("    " + line for line in tail), file=sys.stderr)
    if failed:
        print(f"precommit: {len(failed)} check(s) failed: {', '.join(failed)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotImplementedError as exc:
        print(f"Not implemented yet: {exc}. See labs/s05/README.md.")
        sys.exit(2)
