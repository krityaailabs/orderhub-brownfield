"""The issue-to-PR pipeline (Project 3): run an agent on one issue, bounded, checked and audited.

Order of operations for `run` (each refusal is audited and nothing else happens):
  1. kill switch present?                 -> stopped
     triggered by a bot (e.g. the agent's own PR events)? -> refused
  2. issue labelled for agents?            -> refused
  3. runs in the last hour < limit?        -> refused (rate limit)
  4. open agent PRs < limit?               -> refused
  5. open PR for the same issue?           -> duplicate
  6. agent runs in a fresh worktree, with a timeout
  7. scope and budget guardrails           -> rejected
  8. same change already open?             -> duplicate
  9. required checks in the worktree       -> checks-failed
 10. PR record + patch saved; status "awaiting-human"
`approve` is the human merge gate: an agent identity can never approve, and the patch must still
apply. Approval commits the change on a branch `agent/pr-N` for a person to merge.
"""

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import dedup, guardrails

DEFAULT_CONFIG = {
    "issue_label": "agent-ok",
    "agent_identity": "orderhub-agent",
    "bot_identities": ["orderhub-agent", "github-actions[bot]", "dependabot[bot]"],
    "kill_switch": ".agent-pipeline/STOP",
    "state_dir": "out/agent-pipeline",
    "allowed_paths": ["services/orders/**", "docs/**"],
    "denied_paths": [".github/**", ".claude/**", "**/AGENTS.md", "requirements.lock", "tools/agent_pipeline/**",
                     "legacy/billing/test/golden/**", "instructor/**"],
    "budget": {"max_files": 8, "max_changed_lines": 300, "max_minutes": 20, "max_usd": 3.0},
    "max_runs_per_hour": 6,
    "max_open_prs": 3,
    "required_checks": [],
}


def load_config(repo: Path, overrides: dict | None = None) -> dict:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    file = repo / "ci" / "agent-pipeline.json"
    if file.exists():
        config.update(json.loads(file.read_text()))
    config.update(overrides or {})
    return config


def _git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if check and result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


# ---------- audit log (append-only, hash-chained) ----------

def _state(repo: Path, config: dict) -> Path:
    path = repo / config["state_dir"]
    (path / "prs").mkdir(parents=True, exist_ok=True)
    return path


def audit_entries(repo: Path, config: dict) -> list[dict]:
    file = _state(repo, config) / "audit.jsonl"
    if not file.exists():
        return []
    return [json.loads(line) for line in file.read_text().splitlines() if line.strip()]


def audit(repo: Path, config: dict, event: str, now: datetime | None = None, **fields) -> dict:
    entries = audit_entries(repo, config)
    prev = entries[-1]["hash"] if entries else "0" * 64
    entry = {"ts": (now or datetime.now(timezone.utc)).isoformat(), "event": event, **fields, "prev": prev}
    entry["hash"] = hashlib.sha256((prev + json.dumps(entry, sort_keys=True)).encode()).hexdigest()
    with (_state(repo, config) / "audit.jsonl").open("a") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def verify_audit(repo: Path, config: dict) -> list[str]:
    """Return problems if any entry was edited, removed or reordered."""
    problems, prev = [], "0" * 64
    for i, entry in enumerate(audit_entries(repo, config), start=1):
        body = {k: v for k, v in entry.items() if k != "hash"}
        expected = hashlib.sha256((prev + json.dumps(body, sort_keys=True)).encode()).hexdigest()
        if entry.get("prev") != prev or entry.get("hash") != expected:
            problems.append(f"audit entry {i} ({entry.get('event')}) does not match the chain")
        prev = entry.get("hash", "")
    return problems


# ---------- PR records ----------

def prs(repo: Path, config: dict) -> list[dict]:
    folder = _state(repo, config) / "prs"
    return [json.loads(p.read_text()) for p in sorted(folder.glob("PR-*.json"), key=lambda p: int(p.stem[3:]))]


def _save_pr(repo: Path, config: dict, pr: dict) -> None:
    (_state(repo, config) / "prs" / f"{pr['id']}.json").write_text(json.dumps(pr, indent=2, sort_keys=True))


def _issue_id(issue_path: Path) -> str:
    return issue_path.stem


def _labelled(issue_text: str, label: str) -> bool:
    m = re.search(r"^\*\*Labels:\*\*\s*(.+)$", issue_text, flags=re.M)
    return bool(m) and label in [x.strip() for x in m.group(1).split(",")]


# ---------- run ----------

def run(repo: Path, issue_path: Path, agent_cmd: list[str], config: dict | None = None,
        now: datetime | None = None, actor: str = "person") -> dict:
    repo = Path(repo).resolve()
    config = config or load_config(repo)
    now = now or datetime.now(timezone.utc)
    issue = _issue_id(issue_path)

    def finish(status: str, **fields) -> dict:
        audit(repo, config, status, now=now, issue=issue, **fields)
        return {"status": status, "issue": issue, **fields}

    if (repo / config["kill_switch"]).exists():
        return finish("stopped", reason=f"kill switch {config['kill_switch']} is present")
    if actor in config["bot_identities"]:
        return finish("refused", reason=f"triggered by a bot ({actor}): agents don't trigger agents")
    if not _labelled(Path(issue_path).read_text(), config["issue_label"]):
        return finish("refused", reason=f"issue is not labelled {config['issue_label']}")
    recent = [e for e in audit_entries(repo, config) if e["event"] == "run_started"
              and datetime.fromisoformat(e["ts"]) > now - timedelta(hours=1)]
    if len(recent) >= config["max_runs_per_hour"]:
        return finish("refused", reason=f"rate limit: {len(recent)} runs in the last hour")
    existing = prs(repo, config)
    open_prs = [p for p in existing if p["status"] == "awaiting-human"]
    if len(open_prs) >= config["max_open_prs"]:
        return finish("refused", reason=f"{len(open_prs)} agent PRs already await review")
    duplicate = dedup.is_duplicate(issue, "", existing)
    if duplicate:
        return finish("duplicate", pr=duplicate)

    audit(repo, config, "run_started", now=now, issue=issue, actor=config["agent_identity"])
    worktree = Path(tempfile.mkdtemp(prefix="agent-run-"))
    shutil.rmtree(worktree)
    _git(repo, "worktree", "add", "--detach", str(worktree), "HEAD")
    try:
        started = time.monotonic()
        try:
            result = subprocess.run(agent_cmd, cwd=worktree, capture_output=True, text=True, check=False,
                                    timeout=config["budget"].get("max_minutes", 60) * 60,
                                    env={**_env(), "ISSUE_FILE": str(Path(issue_path).resolve())})
        except subprocess.TimeoutExpired:
            return finish("rejected", problems=["agent timed out"])
        minutes = (time.monotonic() - started) / 60
        usd = _reported_cost(result.stdout)
        _git(worktree, "add", "-A")
        diff = _git(worktree, "diff", "--cached", "--binary", "HEAD")
        files, lines = _numstat(_git(worktree, "diff", "--cached", "--numstat", "HEAD"))
        problems = guardrails.check_scope(files, config["allowed_paths"], config["denied_paths"])
        problems += guardrails.check_budget(guardrails.DiffStats(files, lines, minutes, usd), config["budget"])
        if result.returncode != 0:
            problems.insert(0, f"agent exited {result.returncode}")
        if problems:
            return finish("rejected", problems=problems, files=files, changed_lines=lines)
        diff_hash = hashlib.sha256(diff.encode()).hexdigest()[:16]
        duplicate = dedup.is_duplicate(issue, diff_hash, existing)
        if duplicate:
            return finish("duplicate", pr=duplicate, diff_hash=diff_hash)
        for name, command in _checks(config):
            check = subprocess.run(command, cwd=worktree, capture_output=True, text=True, check=False, shell=False)
            if check.returncode != 0:
                tail = (check.stdout + check.stderr).strip().splitlines()[-3:]
                return finish("checks-failed", check=name, output=tail, files=files)
        pr_id = f"PR-{len(existing) + 1}"
        (_state(repo, config) / "prs" / f"{pr_id}.patch").write_text(diff)
        pr = {"id": pr_id, "issue": issue, "diff_hash": diff_hash, "files": files, "changed_lines": lines,
              "minutes": round(minutes, 2), "usd": usd, "status": "awaiting-human", "author": config["agent_identity"],
              "created": now.isoformat()}
        _save_pr(repo, config, pr)
        return finish("pr_opened", pr=pr_id, diff_hash=diff_hash, files=files, changed_lines=lines)
    finally:
        _git(repo, "worktree", "remove", "--force", str(worktree), check=False)


def _env() -> dict:
    import os
    return dict(os.environ)


def _checks(config: dict) -> list[tuple[str, list[str]]]:
    """Required checks from the config; "{python}" in a command is this interpreter."""
    import sys
    return [(c["name"], [sys.executable if part == "{python}" else part for part in c["command"]])
            for c in config["required_checks"]]


def _reported_cost(stdout: str) -> float | None:
    for line in reversed(stdout.strip().splitlines()):
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "total_cost_usd" in data:
            return float(data["total_cost_usd"])
    return None


def _numstat(text: str) -> tuple[list[str], int]:
    files, lines = [], 0
    for row in text.splitlines():
        added, removed, path = row.split("\t", 2)
        files.append(path)
        lines += (int(added) if added.isdigit() else 0) + (int(removed) if removed.isdigit() else 0)
    return files, lines


# ---------- the human merge gate ----------

def approve(repo: Path, pr_id: str, by: str, config: dict | None = None, now: datetime | None = None) -> dict:
    repo = Path(repo).resolve()
    config = config or load_config(repo)
    pr = next((p for p in prs(repo, config) if p["id"] == pr_id), None)
    who = (by or "").strip()
    if pr is None:
        return {"status": "refused", "reason": f"no such PR {pr_id}"}
    if not who:
        reason = "approval needs a named person (--by)"
    elif who in config["bot_identities"] or who == config["agent_identity"]:
        reason = f"{who} is an agent or bot identity and cannot approve"
    elif pr["status"] != "awaiting-human":
        reason = f"{pr_id} is {pr['status']}, not awaiting-human"
    else:
        reason = None
    if reason:
        audit(repo, config, "approval_refused", now=now, pr=pr_id, by=who or None, reason=reason)
        return {"status": "refused", "reason": reason}
    branch = f"agent/{pr_id.lower()}"
    worktree = Path(tempfile.mkdtemp(prefix="agent-approve-"))
    shutil.rmtree(worktree)
    _git(repo, "worktree", "add", "-b", branch, str(worktree), "HEAD")
    try:
        patch = _state(repo, config) / "prs" / f"{pr_id}.patch"
        applied = subprocess.run(["git", "-C", str(worktree), "apply", "--index", str(patch)],
                                 capture_output=True, text=True, check=False)
        if applied.returncode != 0:
            _git(repo, "worktree", "remove", "--force", str(worktree), check=False)
            _git(repo, "branch", "-D", branch, check=False)
            audit(repo, config, "approval_refused", now=now, pr=pr_id, by=who, reason="patch no longer applies")
            return {"status": "refused", "reason": "patch no longer applies; rerun the issue"}
        message = f"{pr['issue']}: agent change ({pr_id})\n\nApproved-by: {who}\n"
        subprocess.run(["git", "-C", str(worktree), "-c", f"user.name={config['agent_identity']}",
                        "-c", f"user.email={config['agent_identity']}@users.noreply.example",
                        "commit", "-q", "-m", message], check=True, capture_output=True)
    finally:
        _git(repo, "worktree", "remove", "--force", str(worktree), check=False)
    pr["status"] = "approved"
    pr["approved_by"] = who
    pr["branch"] = branch
    _save_pr(repo, config, pr)
    audit(repo, config, "approved", now=now, pr=pr_id, by=who, branch=branch)
    return {"status": "approved", "pr": pr_id, "branch": branch}


def reject(repo: Path, pr_id: str, by: str, reason: str, config: dict | None = None) -> dict:
    repo = Path(repo).resolve()
    config = config or load_config(repo)
    pr = next((p for p in prs(repo, config) if p["id"] == pr_id), None)
    if pr is None or pr["status"] != "awaiting-human":
        return {"status": "refused", "reason": f"{pr_id} is not awaiting review"}
    pr["status"] = "rejected"
    pr["rejected_by"] = by
    pr["reason"] = reason
    _save_pr(repo, config, pr)
    audit(repo, config, "rejected_by_human", pr=pr_id, by=by, reason=reason)
    return {"status": "rejected", "pr": pr_id}
