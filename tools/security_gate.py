"""CI security gate (Lab s07): run every security check, report each one, fail if any fails.

  secrets      tools/secret_scan.py --all        credential-shaped strings in tracked files
  permissions  tools/permission_check.py         the agent permission profile meets the policy
  static       ruff --select S on product code   common weakness classes (CWE) in our code
  dependencies tools/dep_audit.py                pinned, recorded, no duplicates (ADR 0002)
  canary       tools/untrusted_text.py canary    no sign an agent followed injected text

Static analysis ignores two rules in this repository, both known false positives here:
S603 (subprocess call: check for untrusted input) and S607 (partial executable path). Every
subprocess call in tools/ uses a fixed argument list with git, java or the repository's Python.
Tests are excluded (S101 flags every assert). Re-check these exclusions when the code changes.

Usage: python tools/security_gate.py          (exit 1 if any check fails)
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
CHECKS = {
    "secrets": [PY, "tools/secret_scan.py", "--all"],
    "permissions": [PY, "tools/permission_check.py"],
    "static": [PY, "-m", "ruff", "check", "--select", "S", "--ignore", "S603,S607", "--exclude", "tools/tests",
               "--output-format", "concise", "services/orders/orderhub", "tools"],
    "dependencies": [PY, "tools/dep_audit.py"],
    "canary": [PY, "tools/untrusted_text.py", "canary"],
}


def run(name: str, command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    except Exception as exc:  # noqa: BLE001 - a check that can't start is a failed check, reported
        return False, f"could not run {name}: {exc}"
    return result.returncode == 0, (result.stdout + result.stderr).strip()


def main() -> int:
    failed = []
    for name, command in CHECKS.items():
        ok, output = run(name, command)
        print(f"security: {'ok    ' if ok else 'FAILED'} {name}")
        if not ok:
            failed.append(name)
            for line in output.splitlines()[-12:]:
                print(f"    {line}")
    print(f"security-gate: {len(CHECKS) - len(failed)} of {len(CHECKS)} checks passed"
          + (f"; failed: {', '.join(failed)}" if failed else "."))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
