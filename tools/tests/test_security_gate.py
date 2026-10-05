"""Lab s07 (Lectures 7.3 and 7.8): secret scanning runs at commit time, and CI runs the gate."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import security_gate  # noqa: E402


def test_pre_commit_hook_runs_the_secret_scanner_on_staged_files():
    hook = (ROOT / "tools" / "hooks" / "pre-commit").read_text()
    assert "tools/secret_scan.py" in hook
    assert "tools/precommit.py" in hook


def test_ci_has_a_security_workflow_that_runs_the_gate_on_pull_requests():
    workflow = ROOT / ".github" / "workflows" / "security.yml"
    assert workflow.exists()
    text = workflow.read_text()
    assert "pull_request" in text
    assert "tools/security_gate.py" in text


def test_gate_reports_every_check_and_fails_if_any_fails(monkeypatch, capsys):
    results = {"secrets": (False, "SECRET  a.py:1: assigned-secret (abcd... 20 chars)"), "static": (True, "")}
    monkeypatch.setattr(security_gate, "CHECKS", {"secrets": [], "static": []})
    monkeypatch.setattr(security_gate, "run", lambda name, command: results[name])
    assert security_gate.main() == 1
    out = capsys.readouterr().out
    assert "security: FAILED secrets" in out and "security: ok     static" in out
    assert "security-gate: 1 of 2 checks passed; failed: secrets" in out
