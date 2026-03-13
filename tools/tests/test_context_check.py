"""Tests for tools/context_check.py. They fail at tag s02-start (stubs) and pass at s02."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import context_check as cc  # noqa: E402


def make_repo(tmp_path: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp_path


# find_instruction_files


def test_finds_every_kind_of_instruction_file(tmp_path):
    root = make_repo(
        tmp_path,
        {
            "AGENTS.md": "x",
            "legacy/billing/AGENTS.md": "x",
            "CLAUDE.md": "x",
            "sub/CLAUDE.local.md": "x",
            ".github/copilot-instructions.md": "x",
            ".github/instructions/py.instructions.md": "x",
            ".cursor/rules/style.mdc": "x",
            "README.md": "not an instruction file",
            ".venv/lib/AGENTS.md": "ignored: inside .venv",
        },
    )
    assert cc.find_instruction_files(root) == [
        ".cursor/rules/style.mdc",
        ".github/copilot-instructions.md",
        ".github/instructions/py.instructions.md",
        "AGENTS.md",
        "CLAUDE.md",
        "legacy/billing/AGENTS.md",
        "sub/CLAUDE.local.md",
    ]


# claude_code_loads


def test_claude_reads_agents_md_when_there_is_no_claude_md(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "root"})
    assert cc.claude_code_loads(root) == ["AGENTS.md"]


def test_claude_md_hides_agents_md_by_default(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "root", "CLAUDE.md": "claude only"})
    assert cc.claude_code_loads(root) == ["CLAUDE.md"]


def test_a_personal_claude_local_md_also_hides_agents_md(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "team rules", "CLAUDE.local.md": "my notes"})
    assert cc.claude_code_loads(root) == ["CLAUDE.local.md"]


def test_claude_md_importing_agents_md_loads_both(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "team rules", "CLAUDE.md": "@AGENTS.md\nClaude-specific line\n"})
    assert cc.claude_code_loads(root) == ["CLAUDE.md", "AGENTS.md"]


def test_import_inside_backticks_is_not_an_import(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "x", "CLAUDE.md": "see `@AGENTS.md` for details\n"})
    assert cc.claude_code_loads(root) == ["CLAUDE.md"]


def test_nested_agents_md_loads_when_a_file_there_is_opened(tmp_path):
    root = make_repo(
        tmp_path,
        {"AGENTS.md": "root", "legacy/billing/AGENTS.md": "billing", "legacy/billing/src/X.java": "class X {}"},
    )
    assert cc.claude_code_loads(root) == ["AGENTS.md"]
    assert cc.claude_code_loads(root, opened="legacy/billing/src/X.java") == ["AGENTS.md", "legacy/billing/AGENTS.md"]


def test_root_claude_md_also_stops_nested_agents_md(tmp_path):
    root = make_repo(
        tmp_path,
        {
            "AGENTS.md": "root",
            "CLAUDE.md": "@AGENTS.md\n",
            "legacy/billing/AGENTS.md": "billing",
            "legacy/billing/X.java": "",
        },
    )
    assert cc.claude_code_loads(root, opened="legacy/billing/X.java") == ["CLAUDE.md", "AGENTS.md"]


def test_both_mode_reads_claude_md_then_agents_md(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "a", "CLAUDE.local.md": "b", "legacy/AGENTS.md": "c", "legacy/X.java": ""})
    assert cc.claude_code_loads(root, opened="legacy/X.java", mode="claude-md-and-agents-md") == [
        "CLAUDE.local.md",
        "AGENTS.md",
        "legacy/AGENTS.md",
    ]


def test_claude_md_only_mode_never_reads_agents_md(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "a"})
    assert cc.claude_code_loads(root, mode="claude-md") == []


def test_unknown_mode_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        cc.claude_code_loads(tmp_path, mode="everything")


# copilot_loads


def test_github_chat_reads_only_copilot_instructions(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "a", ".github/copilot-instructions.md": "c", "CLAUDE.md": "x"})
    assert cc.copilot_loads(root, "github-chat") == [".github/copilot-instructions.md"]


def test_cloud_agent_reads_instructions_agents_and_claude_md(tmp_path):
    root = make_repo(
        tmp_path,
        {
            "AGENTS.md": "a",
            ".github/copilot-instructions.md": "c",
            "CLAUDE.md": "x",
            ".github/instructions/java.instructions.md": "---\napplyTo: 'legacy/**/*.java'\n---\nJava rules",
            "legacy/AGENTS.md": "legacy",
        },
    )
    assert cc.copilot_loads(root, "cloud-agent", "legacy/src/X.java") == [
        ".github/copilot-instructions.md",
        ".github/instructions/java.instructions.md",
        "AGENTS.md",
        "legacy/AGENTS.md",
        "CLAUDE.md",
    ]


def test_vscode_does_not_read_claude_md(tmp_path):
    root = make_repo(tmp_path, {"AGENTS.md": "a", "CLAUDE.md": "x"})
    assert cc.copilot_loads(root, "vscode") == ["AGENTS.md"]


def test_unknown_copilot_surface_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        cc.copilot_loads(tmp_path, "email")


# cursor_loads


def test_cursor_applies_always_rules_glob_rules_and_nested_agents(tmp_path):
    root = make_repo(
        tmp_path,
        {
            ".cursor/rules/always.mdc": "---\nalwaysApply: true\n---\nalways",
            ".cursor/rules/java.mdc": "---\nglobs: legacy/**/*.java\nalwaysApply: false\n---\njava",
            ".cursor/rules/web.mdc": "---\nglobs: web/**\n---\nweb",
            "AGENTS.md": "a",
            "legacy/AGENTS.md": "l",
            "CLAUDE.md": "not read by Cursor",
        },
    )
    assert cc.cursor_loads(root, "legacy/src/X.java") == [
        ".cursor/rules/always.mdc",
        ".cursor/rules/java.mdc",
        "AGENTS.md",
        "legacy/AGENTS.md",
    ]


# content checks


def test_required_sections():
    assert cc.check_required_sections("# T\n## Commands\n## Boundaries and limits\n") == ["Conventions"]
    assert cc.check_required_sections("## commands\n## Conventions\n## Boundaries\n") == []


def test_check_commands_reports_only_missing_backticked_targets():
    makefile = "setup:\n\tx\ntest:\n\tx\nlint:\n\tx\n"
    text = "Run `make test`, then `make lint`, then `make deploy`. Don't make it pass by editing tests."
    assert cc.check_commands(text, makefile) == ["deploy"]


@pytest.mark.parametrize(
    "line",
    [
        "AWS key AKIAABCDEFGHIJKLMNOP",
        "-----BEGIN RSA PRIVATE KEY-----",
        "token sk-abcdefghijklmnopqrstuvwxyz123456",
        "password = hunter22hunter",
    ],
)
def test_secret_patterns_are_found(line):
    findings = cc.check_no_secrets("fine line\n" + line)
    assert len(findings) == 1 and findings[0].startswith("line 2: ")


def test_plain_text_mentioning_secrets_is_not_a_finding():
    assert cc.check_no_secrets("Never commit secrets or .env files.\nThe password policy is in docs.") == []


def test_size_limit():
    assert cc.check_size("x\n" * 200) is None
    assert "201 lines" in cc.check_size("x\n" * 201)
