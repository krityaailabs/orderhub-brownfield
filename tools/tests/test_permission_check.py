import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from permission_check import check  # noqa: E402

GOOD = {
    "permissions": {
        "allow": ["Bash(make test)", "Bash(make lint)", "Bash(git diff *)"],
        "deny": ["Bash(git push *)", "Bash(curl *)", "Bash(wget *)", "Bash(ssh *)", "Bash(scp *)",
                 "Bash(pip install *)", "Bash(npm install *)", "Read(./.env)", "Edit(./instructor/**)"],
    },
    "sandbox": {"enabled": True},
}


def with_perms(**changes):
    perms = {**GOOD["permissions"], **changes}
    return {"permissions": perms, "sandbox": {"enabled": True}}


def test_good_profile_passes():
    assert check(GOOD) == ([], [])


def test_blanket_and_unapproved_allows_are_problems():
    problems, _ = check(with_perms(allow=["Bash", "WebFetch", "Bash(* test)", "Bash(rm -rf build)"]))
    assert problems == ["blanket allow: Bash", "blanket allow: WebFetch", "wildcard before the command: Bash(* test)",
                        "Bash allow outside the approved commands: Bash(rm -rf build)"]


def test_missing_denies_are_named():
    problems, _ = check(with_perms(deny=["Bash(git push:*)", "Read(./.env)"]))
    assert problems == ["missing deny: curl", "missing deny: wget", "missing deny: ssh", "missing deny: scp",
                        "missing deny: pip install", "missing deny: npm install", "missing deny: edit instructor/"]


def test_bypass_mode_and_missing_section():
    assert "defaultMode bypassPermissions skips every prompt" in check(with_perms(defaultMode="bypassPermissions"))[0]
    assert check({})[0][0].startswith("no permissions section")


def test_sandbox_is_a_warning_not_a_problem():
    problems, warnings = check({"permissions": GOOD["permissions"]})
    assert problems == [] and warnings == ["sandbox not enabled (recommended on macOS, Linux and WSL2)"]
