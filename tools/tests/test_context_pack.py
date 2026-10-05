"""Checks the repository's own context pack (Lab s02). Fails at s02-start, passes at s02."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import context_check as cc  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_root_agents_md_has_the_required_sections():
    assert cc.check_required_sections(read("AGENTS.md")) == []


def test_every_make_command_in_context_files_exists():
    makefile = read("Makefile")
    for rel in cc.find_instruction_files(ROOT):
        assert cc.check_commands(read(rel), makefile) == [], rel


def test_root_agents_md_states_the_money_rule_and_the_test_rule():
    text = read("AGENTS.md").lower()
    assert "minor units" in text
    assert "never edit an existing test" in text or "do not edit existing tests" in text


def test_legacy_billing_has_its_own_agents_md_describing_the_positional_contract():
    text = read("legacy/billing/AGENTS.md").lower()
    assert "position" in text and "handoff" in text
    assert "iso-8859-1" in text


def test_context_files_are_short_and_contain_no_secrets():
    for rel in cc.find_instruction_files(ROOT):
        assert cc.check_size(read(rel)) is None, rel
        assert cc.check_no_secrets(read(rel)) == [], rel


def test_copilot_pointer_refers_to_agents_md():
    assert "AGENTS.md" in read(".github/copilot-instructions.md")


def test_no_claude_local_md_and_it_is_ignored():
    assert not any(f.endswith("CLAUDE.local.md") for f in cc.find_instruction_files(ROOT))
    assert re.search(r"^CLAUDE\.local\.md$", read(".gitignore"), flags=re.M)


def test_two_accepted_adrs_exist():
    adrs = sorted((ROOT / "docs" / "adr").glob("0*.md"))
    assert len(adrs) >= 2
    for adr in adrs[:2]:
        text = adr.read_text(encoding="utf-8")
        assert "**Status:** Accepted" in text, adr.name
        assert "## Decision" in text and "## Applies to" in text, adr.name


def test_all_three_tools_load_the_billing_rules_when_working_on_billing():
    probe = "legacy/billing/src/com/orderhub/billing/HandoffReader.java"
    assert "legacy/billing/AGENTS.md" in cc.claude_code_loads(ROOT, opened=probe)
    assert "legacy/billing/AGENTS.md" in cc.copilot_loads(ROOT, "cloud-agent", probe)
    assert "legacy/billing/AGENTS.md" in cc.cursor_loads(ROOT, probe)
