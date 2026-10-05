"""Tests for tools/secret_scan.py (Lab s07). Fake credentials are built at runtime, so this file
contains no credential-shaped string itself."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import secret_scan as ss  # noqa: E402

FAKE_AWS = "AKIA" + "Q7ZT" * 4                      # 20 chars, AWS access-key-id shape
FAKE_GH = "ghp_" + "a1B2c3D4e5" * 4                  # GitHub token shape
FAKE_PEM = "-----BEGIN " + "RSA PRIVATE KEY-----"
RANDOM = "7f3a9c2e1b8d4f60a5c7"                      # 20 chars, looks random


@pytest.mark.parametrize("value,expected", [
    ("your-api-key-here-123", True), ("EXAMPLEKEY1234567890", True), ("<token goes here>", True),
    ("${WAREHOUSE_TOKEN}", True), ("xxxxxxxxxxxxxxxxxxxx", True), ("0000000000000000", True),
    (RANDOM, False), ("whk_live_9a8b7c6d5e4f3a2b1c0d", False),
])
def test_is_placeholder(value, expected):
    assert ss.is_placeholder(value) is expected


@pytest.mark.parametrize("line,rule", [
    (f"key = '{FAKE_AWS}'", "aws-access-key-id"),
    (FAKE_PEM, "private-key"),
    (f"GH = '{FAKE_GH}'", "github-token"),
    (f'token = os.environ.get("APP_TOKEN", "{RANDOM}")', "env-default"),
    (f'api_key = "{RANDOM}"', "assigned-secret"),
    (f'"client_secret": "{RANDOM}",', "assigned-secret"),
])
def test_each_rule_finds_its_shape(line, rule):
    findings = ss.find_secrets("app/x.py", "ok = 1\n" + line + "\n")
    assert [(f.line, f.rule) for f in findings] == [(2, rule)]


def test_preview_is_redacted():
    finding = ss.find_secrets("x.py", f'api_key = "{RANDOM}"')[0]
    assert finding.preview == "7f3a... 20 chars"
    assert RANDOM not in str(finding)


def test_one_finding_per_line_first_rule_wins():
    findings = ss.find_secrets("x.py", f'aws_secret = "{FAKE_AWS}"')
    assert [f.rule for f in findings] == ["aws-access-key-id"]


def test_placeholders_short_values_and_env_reads_are_not_findings():
    text = "\n".join([
        'api_key = "your-api-key-here-123456"',
        'password = "short"',
        'token = os.environ["APP_TOKEN"]',
        'token = os.environ.get("APP_TOKEN")',
        "The token rotation policy is in docs.",
    ])
    assert ss.find_secrets("x.py", text) == []


def test_allow_marker_skips_the_line_only():
    text = f'api_key = "{RANDOM}"  # secret-scan: allow fixture for a parser test\napi_key = "{RANDOM}"\n'
    assert [f.line for f in ss.find_secrets("x.py", text)] == [2]


@pytest.mark.parametrize("path,found", [(".env", True), ("deploy/prod.env", True), (".env.example", False)])
def test_env_files_are_findings(path, found):
    findings = ss.find_secrets(path, f'API_KEY="{RANDOM}"\n')
    assert (findings == [ss.Finding(path, 1, "env-file", "committed .env file")]) is found


def test_main_exit_codes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(ss, "ROOT", tmp_path)
    (tmp_path / "clean.py").write_text("x = 1\n")
    (tmp_path / "leak.py").write_text(f'api_key = "{RANDOM}"\n')
    assert ss.main(["clean.py"]) == 0
    assert ss.main(["clean.py", "leak.py"]) == 1
    assert "leak.py:1: assigned-secret (7f3a... 20 chars)" in capsys.readouterr().out
