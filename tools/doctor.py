"""Check that this machine can run the OrderHub Brownfield labs.

Usage: python tools/doctor.py   (or: make doctor)
Exit code 0 means every required check passed.
"""

import importlib.util
import shutil
import subprocess
import sys

REQUIRED_PY = (3, 11)
PACKAGES = ["fastapi", "sqlalchemy", "pydantic", "pytest", "httpx"]


def java_major() -> int | None:
    if shutil.which("java") is None:
        return None
    out = subprocess.run(["java", "-version"], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "version" in line:
            v = line.split('"')[1]
            return int(v.split(".")[1]) if v.startswith("1.") else int(v.split(".")[0])
    return None


def main() -> int:
    rows = []
    ok = sys.version_info[:2] >= REQUIRED_PY
    rows.append(("python >= 3.11", ok, sys.version.split()[0], True))
    for pkg in PACKAGES:
        found = importlib.util.find_spec(pkg) is not None
        rows.append((f"package {pkg}", found, "installed" if found else "missing: run make setup", True))
    jm = java_major()
    rows.append(("java >= 11 (javac)", jm is not None and jm >= 11 and shutil.which("javac") is not None,
                 f"java {jm}" if jm else "not found", True))
    rows.append(("git", shutil.which("git") is not None, shutil.which("git") or "not found", True))
    rows.append(("ruff (lint)", shutil.which("ruff") is not None or importlib.util.find_spec("ruff") is not None,
                 "found" if importlib.util.find_spec("ruff") else "optional", False))
    failed = 0
    for name, passed, detail, required in rows:
        mark = "OK  " if passed else ("FAIL" if required else "WARN")
        print(f"{mark}  {name:<22} {detail}")
        if required and not passed:
            failed += 1
    print("\nAll required checks passed." if not failed else f"\n{failed} required check(s) failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
