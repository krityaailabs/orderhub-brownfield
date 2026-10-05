"""Risk-first review helper: point a reviewer at the parts of a diff to read first.

It does not approve anything and it does not find every problem. It flags the patterns that
agent pull requests most often hide in plain sight, in the order a reviewer should read them:

  DELETED-CHECK  a removed condition, raise, assert, bound (min/max) or validator in domain code
  TEST-CHANGE    removed or changed lines in an existing test file
  MOCK-IN-TEST   a new test that patches application code (is the mock hiding the code under review?)
  DEPENDENCY     a change to a dependency file, with the packages added or removed
  DUPLICATE-DEP  a new package doing the job of one already in the lock file (e.g. two HTTP clients)
  NEW-IMPORT     an import of a third-party module that is not in the lock file (phantom dependency)
  API-SURFACE    a new or changed route or request/response schema: a contract with clients
  CONTRACT       a change to the billing handoff or the legacy billing code
  SIZE           more changed lines than the review budget
  OUT-OF-SCOPE   a changed file that is not in the slice's declared list (--files)

Usage:
  python tools/review_flags.py                       (diff of HEAD against origin/main or main)
  python tools/review_flags.py --base s06-start      (diff of HEAD against a ref)
  python tools/review_flags.py --diff labs/s06/prs/R5.diff
  python tools/review_flags.py --files services/orders/orderhub/orders.py,services/orders/tests/test_orders.py
"""

import argparse
import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_PATHS = ("services/orders/orderhub/", "legacy/billing/src/")
TEST_PATHS = ("services/orders/tests/", "tools/tests/", "legacy/billing/test/")
DEPENDENCY_FILES = ("requirements.lock", "requirements.txt", "pyproject.toml", "pom.xml", "package.json")
LOCAL_MODULES = {"orderhub", "tools", "conftest"}
# Import name -> distribution name, where they differ.
IMPORT_ALIASES = {"yaml": "pyyaml", "dateutil": "python-dateutil", "pytest": "pytest", "_pytest": "pytest",
                  "sqlalchemy": "sqlalchemy", "fastapi": "fastapi", "pydantic": "pydantic"}
# Packages that do the same job; adding a second one is usually a review question.
FAMILIES = {
    "HTTP client": {"requests", "httpx", "httpx2", "aiohttp", "urllib3"},
    "date handling": {"python-dateutil", "arrow", "pendulum"},
}
ORDER = ["DELETED-CHECK", "TEST-CHANGE", "MOCK-IN-TEST", "DEPENDENCY", "DUPLICATE-DEP", "NEW-IMPORT",
         "API-SURFACE", "CONTRACT", "SIZE", "OUT-OF-SCOPE"]

CHECK_PATTERN = re.compile(
    r"^\s*(raise\b|if\b|elif\b|assert\b)|\b(min|max)\(|"
    r"\b(ge|le|gt|lt|min_length|max_length)\s*=|\bextra\s*=\s*['\"]forbid")
MOCK_PATTERN = re.compile(r"monkeypatch\.setattr|mock\.patch|(?<![\w.])patch(\.object)?\(|MagicMock|\bMock\(")
ROUTE_PATTERN = re.compile(r"@app\.(get|post|put|patch|delete)\(")
IMPORT_PATTERN = re.compile(r"^\s*(?:from\s+([A-Za-z_][\w]*)[\w.]*\s+import|import\s+([A-Za-z_][\w]*))")


@dataclass
class FileDiff:
    path: str
    is_new: bool = False
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)


def parse_diff(diff_text: str) -> list[FileDiff]:
    """Parse unified diff text (any context size) into per-file added and removed lines."""
    files: list[FileDiff] = []
    current: FileDiff | None = None
    old_is_null = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            current = None
            old_is_null = False
        elif line.startswith("--- "):
            old_is_null = line.strip() == "--- /dev/null"
        elif line.startswith("+++ "):
            path = re.sub(r"^\+\+\+ (b/)?", "", line).strip()
            if path == "/dev/null":
                current = None
                continue
            current = FileDiff(path=path, is_new=old_is_null)
            files.append(current)
        elif current is None or line.startswith("@@"):
            continue
        elif line.startswith("+"):
            current.added.append(line[1:])
        elif line.startswith("-"):
            current.removed.append(line[1:])
    # A deleted file has "+++ /dev/null"; record its removals against the old path.
    for block in re.split(r"(?m)^diff --git ", diff_text):
        if "\n+++ /dev/null" in block:
            m = re.search(r"(?m)^--- (?:a/)?(.+)$", block)
            if m:
                fd = FileDiff(path=m.group(1).strip())
                fd.removed = [ln[1:] for ln in block.splitlines()
                              if ln.startswith("-") and not ln.startswith("---")]
                files.append(fd)
    return files


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def lock_packages(lock_text: str) -> set[str]:
    names = set()
    for line in lock_text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(_norm(re.split(r"[=<>!~\[ ;]", line, maxsplit=1)[0]))
    return names


def _package_lines(lines: list[str]) -> set[str]:
    return lock_packages("\n".join(lines))


def is_test(path: str) -> bool:
    return path.startswith(TEST_PATHS) or Path(path).name.startswith("test_")


def flag(diff_text: str, lock_text: str = "", files: list[str] | None = None, budget: int = 300) -> list[tuple]:
    """Return (FLAG, path, detail) tuples in risk-first ORDER."""
    flags: list[tuple] = []
    parsed = parse_diff(diff_text)
    locked = lock_packages(lock_text)
    stdlib = set(sys.stdlib_module_names)
    added_pkgs: set[str] = set()
    removed_pkgs: set[str] = set()
    total = 0
    for fd in parsed:
        total += len(fd.added) + len(fd.removed)
        added_set = {a.strip() for a in fd.added}
        if fd.path.startswith(DOMAIN_PATHS):
            for line in fd.removed:
                if CHECK_PATTERN.search(line) and line.strip() not in added_set:
                    flags.append(("DELETED-CHECK", fd.path, line.strip()))
        if is_test(fd.path):
            if not fd.is_new:
                for line in fd.removed:
                    if line.strip():
                        flags.append(("TEST-CHANGE", fd.path, line.strip()))
            for line in fd.added:
                if MOCK_PATTERN.search(line):
                    flags.append(("MOCK-IN-TEST", fd.path, line.strip()))
        if Path(fd.path).name in DEPENDENCY_FILES:
            plus, minus = _package_lines(fd.added), _package_lines(fd.removed)
            added_pkgs |= plus - minus
            removed_pkgs |= minus - plus
            detail = ", ".join([f"+{p}" for p in sorted(plus - minus)] + [f"-{p}" for p in sorted(minus - plus)])
            flags.append(("DEPENDENCY", fd.path, detail or "changed"))
        if fd.path.endswith(".py") and not is_test(fd.path):
            for line in fd.added:
                m = IMPORT_PATTERN.match(line)
                if not m:
                    continue
                mod = m.group(1) or m.group(2)
                if mod in stdlib or mod in LOCAL_MODULES or mod.startswith("_") and mod != "_pytest":
                    continue
                dist = _norm(IMPORT_ALIASES.get(mod, mod))
                if dist not in locked and dist not in added_pkgs:
                    flags.append(("NEW-IMPORT", fd.path, f"{mod} is not in requirements.lock"))
        if fd.path.endswith("schemas.py") and (fd.added or fd.removed):
            flags.append(("API-SURFACE", fd.path, "request/response models changed"))
        for line in fd.added + fd.removed:
            if ROUTE_PATTERN.search(line):
                flags.append(("API-SURFACE", fd.path, line.strip()))
        if fd.path.startswith("legacy/billing/") or (
                fd.path.endswith("orderhub/orders.py")
                and any("handoff" in ln.lower() or "csv" in ln.lower() for ln in fd.added + fd.removed)):
            flags.append(("CONTRACT", fd.path, "billing handoff or legacy billing changed"))
        if files is not None and not any(fnmatch.fnmatch(fd.path, pat) for pat in files):
            flags.append(("OUT-OF-SCOPE", fd.path, "not in the declared file list"))
    for family, members in FAMILIES.items():
        for pkg in sorted(added_pkgs & members):
            others = sorted((locked - added_pkgs - removed_pkgs) & members)
            if others:
                flags.append(("DUPLICATE-DEP", "requirements.lock", f"{pkg} added; {family} already provided by "
                              + ", ".join(others)))
    if total > budget:
        flags.append(("SIZE", "*", f"{total} changed lines (budget {budget}): ask for a split or read risk-first"))
    return sorted(flags, key=lambda f: ORDER.index(f[0]))


def render(results: list[tuple], per_file: int = 3) -> list[str]:
    """Format flags one per line; collapse long runs of the same flag in one file."""
    lines: list[str] = []
    seen: dict[tuple[str, str], int] = {}
    for name, path, _ in results:
        seen[(name, path)] = seen.get((name, path), 0) + 1
    shown: dict[tuple[str, str], int] = {}
    for name, path, detail in results:
        key = (name, path)
        shown[key] = shown.get(key, 0) + 1
        if shown[key] <= per_file:
            lines.append(f"{name:<14}{path}: {detail}")
        elif shown[key] == per_file + 1:
            lines.append(f"{name:<14}{path}: ... and {seen[key] - per_file} more")
    return lines


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False).stdout


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", help="ref to diff against (default: origin/main, else main)")
    ap.add_argument("--diff", help="read the diff from a file instead of git")
    ap.add_argument("--files", help="comma-separated declared files or globs for the slice")
    ap.add_argument("--budget", type=int, default=300)
    args = ap.parse_args(argv)
    if args.diff:
        diff_text = Path(args.diff).read_text()
    else:
        base = args.base or ("origin/main" if _git("rev-parse", "--verify", "-q", "origin/main") else "main")
        if not _git("rev-parse", "--verify", "-q", f"{base}^{{commit}}"):
            print(f"review-flags: unknown ref {base!r}. If it's a remote branch, create it locally first "
                  f"(for example: git branch {base} origin/{base}), or pass --diff FILE.")
            return 2
        diff_text = _git("diff", f"{base}...HEAD")
    lock = ROOT / "requirements.lock"
    lock_text = lock.read_text() if lock.exists() else ""
    files = [f.strip() for f in args.files.split(",")] if args.files else None
    results = flag(diff_text, lock_text, files, args.budget)
    for line in render(results):
        print(line)
    print(f"review-flags: {len(results)} flag(s). Flags say where to read first, not whether to merge.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
