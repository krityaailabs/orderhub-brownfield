"""Guard against test tampering: fail when a change edits or deletes lines in existing test files.

Adding new tests is always fine. Changing an existing test needs a human decision, recorded by
putting "[test-change-approved]" in a commit message of the change (or ALLOW_TEST_EDITS=1 locally).

Usage: python tools/protect_tests.py [BASE]     (default BASE: origin/main, falling back to main)
"""

import os
import re  # noqa: F401  (used once the Lab s04 stub is implemented)
import subprocess
import sys

TEST_PATHS = ["services/orders/tests", "tools/tests", "legacy/billing/test"]
APPROVAL = "[test-change-approved]"


def find_test_edits(diff_text: str) -> list[tuple[str, str]]:
    """Given `git diff --unified=0` output, return (file, removed_line) for every line removed or
    changed in a test file that already existed. Lines removed from a new file (`--- /dev/null`)
    and pure additions don't count. Blank removed lines are ignored. Order is preserved."""
    raise NotImplementedError("Lab s04: implement find_test_edits")


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False).stdout


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    base = argv[0] if argv else ("origin/main" if _git("rev-parse", "--verify", "-q", "origin/main") else "main")
    diff = _git("diff", "--unified=0", f"{base}...HEAD", "--", *TEST_PATHS)
    diff += _git("diff", "--unified=0", "HEAD", "--", *TEST_PATHS)
    edits = find_test_edits(diff)
    if not edits:
        print(f"OK: no existing test lines changed since {base}.")
        return 0
    messages = _git("log", "--format=%B", f"{base}..HEAD")
    if APPROVAL in messages or os.environ.get("ALLOW_TEST_EDITS") == "1":
        print(f"{len(edits)} existing test line(s) changed, with approval recorded.")
        return 0
    print(f"BLOCKED: {len(edits)} existing test line(s) changed since {base} without approval:")
    for path, removed in edits[:20]:
        print(f"  {path}: - {removed.strip()}")
    print(f"If a human has decided the test was wrong, add {APPROVAL} to the commit message.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
