"""Check an agent permission profile against the team's least-privilege policy.

Reads the "permissions" (and "sandbox") sections of a Claude Code settings file, by default
.claude/settings.json, and reports every way it is looser than the policy below. The policy is
the point of Lecture 7.2; the tool only makes it checkable in CI. Other tools (Cursor, Copilot)
have their own formats; apply the same policy to them by hand or with a small adapter.

Policy (deny-by-default for anything that leaves the machine or touches secrets):
  1. No blanket allows: no bare "Bash", "Bash(*)", "WebFetch", "WebFetch(domain:*)", "Edit" or
     "Write" in allow, and no allow rule with a `*` before the subcommand (e.g. "Bash(* test)").
  2. Every Bash allow rule starts with an approved prefix (APPROVED_BASH): the project's own
     make targets and read-only git commands.
  3. These are denied: pushing (git push), network tools in the shell (curl, wget, ssh, scp),
     package installs (pip install, npm install), reading .env files and editing instructor/.
  4. defaultMode is not "bypassPermissions" (or "dontAsk" with broad allows).
  5. Recommended, reported as a warning only: sandbox.enabled true (needs macOS, Linux or WSL2).

Known limit (from the Claude Code documentation): a Bash deny rule matches the command text the
agent writes; it doesn't stop the same program run another way (an absolute path, `sh -c`, a
script). Deny rules reduce accidents; the sandbox and CI are the boundaries that hold.

Usage: python tools/permission_check.py [SETTINGS_FILE]
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVED_BASH = ("make ", "git status", "git diff", "git log", "git show", "git branch", "git worktree list")
BLANKET_ALLOWS = {"bash", "bash(*)", "webfetch", "webfetch(domain:*)", "edit", "write", "edit(*)", "write(*)",
                  "edit(**)", "write(**)"}
REQUIRED_DENIES = {
    "git push": r"^Bash\(git push( \*|:\*)?\)$",
    "curl": r"^Bash\(curl( \*|:\*)?\)$",
    "wget": r"^Bash\(wget( \*|:\*)?\)$",
    "ssh": r"^Bash\(ssh( \*|:\*)?\)$",
    "scp": r"^Bash\(scp( \*|:\*)?\)$",
    "pip install": r"^Bash\((\S*/)?(python3? -m )?pip install( \*|:\*)?\)$",
    "npm install": r"^Bash\(npm install( \*|:\*)?\)$",
    "read .env": r"^Read\(\./\.env\*?\)$|^Read\(\*\*/\.env\*?\)$|^Read\(\./\*\*/\.env\*?\)$",
    "edit instructor/": r"^(Edit|Write)\(\./instructor/\*\*\)$",
}


def _bash_command(rule: str) -> str | None:
    m = re.fullmatch(r"Bash\((.*)\)", rule)
    return m.group(1) if m else None


def check(settings: dict) -> tuple[list[str], list[str]]:
    """Return (problems, warnings) for a settings dict."""
    problems: list[str] = []
    warnings: list[str] = []
    perms = settings.get("permissions") or {}
    allow = list(perms.get("allow") or [])
    deny = list(perms.get("deny") or [])
    if not perms:
        problems.append("no permissions section: every action falls back to the tool's defaults")
    for rule in allow:
        if rule.strip().lower() in BLANKET_ALLOWS:
            problems.append(f"blanket allow: {rule}")
            continue
        command = _bash_command(rule)
        if command is None:
            continue
        head = command.split("*", 1)[0]
        if "*" in command and not head.strip():
            problems.append(f"wildcard before the command: {rule}")
        elif not command.startswith(APPROVED_BASH):
            problems.append(f"Bash allow outside the approved commands: {rule}")
    for name, pattern in REQUIRED_DENIES.items():
        if not any(re.match(pattern, rule) for rule in deny):
            problems.append(f"missing deny: {name}")
    mode = perms.get("defaultMode")
    if mode == "bypassPermissions":
        problems.append("defaultMode bypassPermissions skips every prompt")
    if not (settings.get("sandbox") or {}).get("enabled"):
        warnings.append("sandbox not enabled (recommended on macOS, Linux and WSL2)")
    return problems, warnings


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else ROOT / ".claude" / "settings.json"
    settings = json.loads(path.read_text())
    problems, warnings = check(settings)
    for p in problems:
        print(f"PROBLEM  {p}")
    for w in warnings:
        print(f"WARNING  {w}")
    rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    print(f"permission-check: {rel}: {len(problems)} problem(s), {len(warnings)} warning(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
