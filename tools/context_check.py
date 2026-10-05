"""Context smoke test: check the repository's agent context pack, and simulate which
instruction files each coding tool loads.

Usage: python tools/context_check.py        (or: make context-check)

The loader simulations encode the vendors' documented rules as verified on 5 October 2026
(Claude Code memory docs, GitHub Copilot custom-instructions support table, Cursor rules docs).
They are a teaching model, not the tools themselves: re-verify when the tools change.
"""

import fnmatch
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "node_modules", "build", "out", "__pycache__", ".pytest_cache", ".ruff_cache"}
CLAUDE_NAMES = ("CLAUDE.md", ".claude/CLAUDE.md", "CLAUDE.local.md")
REQUIRED_SECTIONS = ("Commands", "Conventions", "Boundaries")
MAX_LINES = 200
SECRET_PATTERNS = [
    ("AWS access key id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("API key style token", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("assigned password or secret",
     re.compile(r"(?i)\b(password|passwd|secret|api_key|apikey)\s*[:=]\s*['\"]?[^\s'\"<>]{6,}")),
]
COPILOT_SURFACES = ("github-chat", "cloud-agent", "code-review", "vscode", "cli")


def _walk(root: Path):
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def find_instruction_files(root: Path) -> list[str]:
    """Return repository-relative paths (POSIX style, sorted) of every agent instruction file:
    AGENTS.md and CLAUDE.md files at any depth, .claude/CLAUDE.md, CLAUDE.local.md,
    .github/copilot-instructions.md, .github/instructions/**/*.instructions.md and
    .cursor/rules/**/*.mdc."""
    raise NotImplementedError("Lab s02: implement find_instruction_files")


def _ancestors(root: Path, cwd: str) -> list[Path]:
    """Directories from the repository root down to cwd (inclusive)."""
    target = (root / cwd).resolve()
    chain = [target]
    while chain[-1] != root.resolve():
        chain.append(chain[-1].parent)
    return list(reversed(chain))


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _imports(root: Path, claude_file: Path) -> list[Path]:
    out = []
    in_fence = False
    for line in claude_file.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in re.finditer(r"(?<![`\w])@([\w./\-]+)", line):
            candidate = (claude_file.parent / match.group(1)).resolve()
            if candidate.is_file():
                out.append(candidate)
    return out


def claude_code_loads(root: Path, cwd: str = ".", opened: str | None = None,
                      mode: str = "claude-md-or-agents-md") -> list[str]:
    """Simulate which project instruction files Claude Code loads.

    cwd: directory Claude Code was started in (relative to root).
    opened: a file Claude reads during the session (relative to root); subdirectory files on its
            path below cwd load on demand.
    mode: the "Project instructions" setting: claude-md-or-agents-md (default),
          claude-md-and-agents-md, or claude-md.
    Rules: CLAUDE.md, .claude/CLAUDE.md and CLAUDE.local.md load from cwd and every directory above.
    In the default mode, AGENTS.md (and .claude/AGENTS.md) load only if none of those three exist in
    cwd or above; then a subdirectory's AGENTS.md loads when a file there is opened and that
    subdirectory has none of the three files of its own. @path imports in a CLAUDE.md are expanded.
    Returns repository-relative paths in load order, without duplicates."""
    raise NotImplementedError("Lab s02: implement claude_code_loads")


def _frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip().strip("'\"")
    return data


def _matches(globs: str, path: str | None) -> bool:
    if not globs:
        return False
    if path is None:
        return False
    return any(fnmatch.fnmatch(path, g.strip()) for g in globs.split(",") if g.strip())


def copilot_loads(root: Path, surface: str, path: str | None = None) -> list[str]:
    """Simulate which instruction files GitHub Copilot reads on a surface.

    Supported (GitHub docs, custom-instructions support table, checked 5 Oct 2026):
      .github/copilot-instructions.md: every surface
      .github/instructions/**/*.instructions.md (when applyTo matches path): every surface except github-chat
      AGENTS.md: every surface except github-chat (root, plus nested AGENTS.md on the path; nested
                 support is per GitHub's changelog and should be re-verified)
      CLAUDE.md: cloud-agent and cli only
    """
    raise NotImplementedError("Lab s02: implement copilot_loads")


def cursor_loads(root: Path, path: str | None = None) -> list[str]:
    """Simulate which rules Cursor's agent applies when working on `path`.

    Project rules: .cursor/rules/**/*.mdc with alwaysApply: true, or whose globs match path.
    AGENTS.md: root, then nested AGENTS.md files on the path (more specific last, taking precedence).
    CLAUDE.md is not part of Cursor's documented rule types and is not loaded here."""
    raise NotImplementedError("Lab s02: implement cursor_loads")


def check_required_sections(text: str) -> list[str]:
    """Return the REQUIRED_SECTIONS that have no level-2 heading (## Name...) in text, in order."""
    raise NotImplementedError("Lab s02: implement check_required_sections")


def check_commands(text: str, makefile_text: str) -> list[str]:
    """Return every `make <target>` command written in backticks in text whose target is not defined
    in the Makefile. Only backticked commands count: prose such as "make it pass" is not a command."""
    raise NotImplementedError("Lab s02: implement check_commands")


def check_no_secrets(text: str) -> list[str]:
    """Return one finding per line that looks like a secret: 'line N: <kind>'."""
    raise NotImplementedError("Lab s02: implement check_no_secrets")


def check_size(text: str, max_lines: int = MAX_LINES) -> str | None:
    lines = len(text.splitlines())
    return None if lines <= max_lines else f"{lines} lines (limit {max_lines}); move detail into nested files or docs"


def main(root: Path | None = None) -> int:
    root = (root or Path(__file__).resolve().parents[1]).resolve()
    errors = 0
    makefile = (root / "Makefile").read_text(encoding="utf-8") if (root / "Makefile").is_file() else ""
    files = find_instruction_files(root)
    print("Instruction files:", ", ".join(files) or "none")
    agents = [f for f in files if f.endswith("AGENTS.md")]
    if "AGENTS.md" not in agents:
        print("ERROR  no root AGENTS.md")
        errors += 1
    for rel in agents:
        text = (root / rel).read_text(encoding="utf-8")
        problems = []
        if rel == "AGENTS.md":
            problems += [f"missing section '## {s}'" for s in check_required_sections(text)]
        problems += [f"'make {t}' is not a Makefile target" for t in check_commands(text, makefile)]
        problems += [f"possible secret ({f})" for f in check_no_secrets(text)]
        size = check_size(text)
        if size:
            problems.append(size)
        for p in problems:
            print(f"ERROR  {rel}: {p}")
        errors += len(problems)
        if not problems:
            print(f"OK     {rel}")
    for rel in files:
        if rel.endswith("CLAUDE.local.md"):
            print(f"WARN   {rel} exists: Claude Code (default setting) will stop reading AGENTS.md for you")
    print("\nSimulated loading (documented rules, 5 Oct 2026):")
    probe = "legacy/billing/src/com/orderhub/billing/HandoffReader.java"
    print("  Claude Code, start at root           :", claude_code_loads(root))
    print("  Claude Code, after opening legacy file:", claude_code_loads(root, opened=probe))
    print("  Copilot cloud agent, legacy file     :", copilot_loads(root, "cloud-agent", probe))
    print("  Copilot GitHub.com chat              :", copilot_loads(root, "github-chat"))
    print("  Cursor, legacy file                  :", cursor_loads(root, probe))
    print("\nContext check passed." if not errors else f"\nContext check failed: {errors} error(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotImplementedError as exc:
        print(f"Not implemented yet: {exc}. See labs/s02/README.md.")
        sys.exit(2)
