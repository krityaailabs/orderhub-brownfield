"""Hook for coding agents: after the agent edits a file, run the checks for that file.

Claude Code (PostToolUse, matcher Edit|Write) passes JSON on stdin with tool_input.file_path.
Exit code 2 sends the failure back to the agent as feedback so it can fix it.
Other tools: adapt the stdin parsing to their payload (see docs/course/hooks.md).
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def edited_path(payload: dict) -> str | None:
    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or payload.get("file_path")
    if not path:
        return None
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    rel = edited_path(payload)
    if not rel:
        return 0
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "precommit.py"), rel],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"Checks failed after editing {rel}:\n{result.stdout}{result.stderr}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
