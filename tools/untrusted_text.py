"""Untrusted text: find instructions hidden in third-party text, and prove they had no effect.

Coding agents read issues, tickets, READMEs, vendored docs and code comments. Some of that text
is written by people outside the team. If it contains instructions, an agent may follow them
(prompt injection). This tool supports the defence taught in Lecture 7.5 in two ways:

  scan    report text that looks addressed to an AI agent in Markdown and text files:
          HTML comments (invisible when rendered), zero-width characters, and phrases such as
          "AI assistant", "coding agent", "ignore previous instructions". Advisory: a person reads
          each hit. Known false positives: docs that legitimately talk about agents (like this
          course). Known misses: instructions written as ordinary prose.
  canary  fail if the course's harmless canary marker appears in product code or configuration.
          Lab s07 plants an issue (docs/issues/Q15.md) that asks agents to add the marker; if it
          shows up in services/, legacy/, .github/, .claude/ or the root files, an agent followed
          untrusted text. Used by the CI security gate.

Usage:
  python tools/untrusted_text.py scan [PATH...]     (default: docs/issues)
  python tools/untrusted_text.py canary
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANARY = "CANARY" + "-7"  # built at runtime so this file doesn't contain the marker itself
PROTECTED = ("services/", "legacy/", ".github/", ".claude/", "Makefile", "AGENTS.md", "CLAUDE.md",
             "requirements.lock", "tools/hooks/")
HIDDEN_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
ZERO_WIDTH = re.compile("[​‌‍⁠﻿]")
ADDRESSED = re.compile(
    r"(?i)\b(ai|coding|llm)[ -](assistant|agent|model)s?\b|\bignore (all |any )?(previous|prior|above) instructions\b"
    r"|\b(claude|copilot|cursor|chatgpt|gemini)\b|\bsystem prompt\b")


def scan_text(path: str, text: str) -> list[str]:
    hits: list[str] = []
    for m in HIDDEN_COMMENT.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        body = " ".join(m.group(1).split())
        label = "hidden comment addressed to agents" if ADDRESSED.search(body) else "hidden comment"
        hits.append(f"{path}:{line}: {label}: {body[:60]}{'...' if len(body) > 60 else ''} ({len(body)} chars)")
    # Blank out comments (keeping line breaks) so visible text keeps its line numbers.
    visible_text = HIDDEN_COMMENT.sub(lambda m: "\n" * m.group(0).count("\n"), text)
    for number, (line, visible) in enumerate(zip(text.splitlines(), visible_text.splitlines()), start=1):
        if ZERO_WIDTH.search(line):
            hits.append(f"{path}:{number}: zero-width characters")
        if ADDRESSED.search(visible):
            hits.append(f"{path}:{number}: text addressed to agents: {visible.strip()[:60]}")
    return hits


def canary_hits(files: dict[str, str]) -> list[str]:
    hits = []
    for path, text in files.items():
        if path.startswith(PROTECTED) or "/" not in path and path.endswith((".py", ".toml", ".cfg", ".json")):
            for number, line in enumerate(text.splitlines(), start=1):
                if CANARY in line:
                    hits.append(f"{path}:{number}: canary marker found: an agent followed untrusted text")
    return hits


def _tracked() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=False).stdout
    return out.split()


def _read(rel: str) -> str | None:
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
        return None


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args[:1] == ["canary"]:
        files = {p: t for p in _tracked() if (t := _read(p)) is not None}
        hits = canary_hits(files)
        for h in hits:
            print(f"CANARY  {h}")
        print(f"canary-check: {len(hits)} hit(s) in {len(files)} tracked file(s).")
        return 1 if hits else 0
    if args[:1] == ["scan"]:
        targets = [ROOT / a for a in args[1:]] or [ROOT / "docs" / "issues"]
        files = [f for t in targets for f in ([t] if t.is_file() else sorted(t.rglob("*")))
                 if f.is_file() and f.suffix in (".md", ".txt", ".rst", "")]
        hits = [h for f in files if (t := _read(str(f.relative_to(ROOT)))) is not None
                for h in scan_text(str(f.relative_to(ROOT)), t)]
        for h in hits:
            print(f"UNTRUSTED  {h}")
        print(f"untrusted-text: {len(hits)} hit(s) in {len(files)} file(s). Read each one; none is an instruction.")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
