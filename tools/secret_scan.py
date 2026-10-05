"""Secret scanner: stop keys, tokens and private keys before they reach a commit.

Defensive tool for Lab s07. It looks for credential-shaped strings in text files and reports the
path, line, rule and a redacted preview (the first four characters and the length; never the
whole value). It is deliberately small, so you can read all of it. Known limits:

  - It finds credential-shaped strings, not every secret. A password like "summer2026" assigned to
    a variable called `x` is invisible to it.
  - Long random-looking literals assigned to names containing "token", "secret", "password" or
    "api_key" are reported even when they are test data. Mark a deliberate fixture with an inline
    `# secret-scan: allow <reason>` comment, and review those comments like code.
  - Dedicated scanners (gitleaks, trufflehog, GitHub secret scanning) know hundreds of provider
    formats and verify some keys live. Use one in CI as well if you can; this tool teaches the idea
    and runs anywhere with no new dependency.

Usage:
  python tools/secret_scan.py            (staged files; used by the pre-commit hook)
  python tools/secret_scan.py --all      (every tracked file; used by the CI security gate)
  python tools/secret_scan.py FILE...    (the given files)
"""

import fnmatch
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOW_MARKER = "secret-scan: allow"
IGNORE_FILE = ".secret-scan-ignore"
PLACEHOLDER_WORDS = ("example", "placeholder", "changeme", "change-me", "dummy", "your-", "your_", "xxxx",
                     "<", "${", "{{", "redacted")
SKIP_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".zip", ".bundle", ".class", ".jar", ".pdf", ".ico")

# (rule name, compiled pattern, index of the group holding the secret value; 0 = whole match)
RULES = [
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), 0),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----"), 0),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), 0),
    ("env-default", re.compile(
        r"(?i)environ(?:\.get)?\(\s*['\"][A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API_?KEY)[A-Z0-9_]*['\"]"
        r"\s*,\s*['\"]([^'\"\s]{12,})['\"]"), 1),
    ("assigned-secret", re.compile(
        r"(?i)\b[a-z0-9_]*(?:secret|token|password|passwd|api_?key)[a-z0-9_]*['\"]?\s*[:=]\s*['\"]([^'\"\s]{16,})['\"]"),
        1),
]


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    rule: str
    preview: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule} ({self.preview})"


def redact(value: str) -> str:
    """Show the first four characters and the length, never the whole value."""
    return f"{value[:4]}... {len(value)} chars"


def is_placeholder(value: str) -> bool:
    """Return True if value is obviously not a real secret.

    Rules (case-insensitive):
      - it contains any of PLACEHOLDER_WORDS (e.g. "example", "changeme", "<", "${")
      - or it is one character repeated (e.g. "xxxxxxxxxxxxxxxx", "0000000000000000")
    Everything else is treated as possibly real."""
    lowered = value.lower()
    if any(word in lowered for word in PLACEHOLDER_WORDS):
        return True
    return len(set(lowered)) == 1


def find_secrets(path: str, text: str) -> list[Finding]:
    """Return the findings for one file's text, in line order.

    Rules:
      - A file named `.env` or ending in `.env` (but not `.env.example`) is itself a finding:
        one Finding(path, 1, "env-file", "committed .env file"), and nothing else is scanned.
      - For every line, apply each rule in RULES. For a match, the secret value is the group
        given by the rule's group index (0 = the whole match).
      - Skip the match if is_placeholder(value) is True.
      - Skip the whole line if it contains ALLOW_MARKER.
      - Report at most one finding per line: the first rule (in RULES order) that matches.
      - Line numbers start at 1. The preview is redact(value)."""
    name = Path(path).name
    if name == ".env" or name.endswith(".env"):
        return [Finding(path, 1, "env-file", "committed .env file")]
    findings: list[Finding] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if ALLOW_MARKER in line:
            continue
        for rule, pattern, group in RULES:
            hit = next((m.group(group) for m in pattern.finditer(line) if not is_placeholder(m.group(group))), None)
            if hit is not None:
                findings.append(Finding(path, number, rule, redact(hit)))
                break
    return findings


def _git(*args: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False).stdout
    return [line for line in out.splitlines() if line]


def ignored_globs() -> list[str]:
    file = ROOT / IGNORE_FILE
    if not file.exists():
        return []
    globs = [line.split("#", 1)[0].strip() for line in file.read_text().splitlines()]
    return [g for g in globs if g]


def scan_paths(paths: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    ignore = ignored_globs()
    for rel in paths:
        if rel.endswith(SKIP_SUFFIXES) or any(fnmatch.fnmatch(rel, g) for g in ignore):
            continue
        file = ROOT / rel
        if not file.is_file():
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(find_secrets(rel, text))
    return findings


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args == ["--all"]:
        paths = _git("ls-files")
    elif args:
        paths = args
    else:
        paths = _git("diff", "--cached", "--name-only", "--diff-filter=ACM")
    findings = scan_paths(paths)
    for finding in findings:
        print(f"SECRET  {finding}")
    if findings:
        print(f"secret-scan: {len(findings)} finding(s). Remove the value, rotate it if it was real, "
              "and load it from the environment.")
        return 1
    print(f"secret-scan: {len(paths)} file(s) clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
