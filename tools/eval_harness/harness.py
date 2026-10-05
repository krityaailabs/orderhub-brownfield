"""Evaluation harness for coding agents on your own repository (Section 10, Lab s10).

Each task is a small, real change with HELD-OUT acceptance tests the tool never sees. For each
tool and task, the harness takes the tool's change (a recorded patch), applies it to a fresh
worktree of HEAD, copies the held-out tests in, and runs:

  acceptance   the task's held-out tests
  full suite   every existing Python test (did it break anything?)
  lint         ruff on the service
  scope        changed files inside the task's allowed paths

It then joins the tool's cost and time (meta.json) and the human review log (review-log.csv),
and summarises each tool: success rate, cost per successful task, review minutes, failures.

Usage:
  python tools/eval_harness/harness.py                          all tools in labs/s10/recordings, all tasks
  python tools/eval_harness/harness.py --tools tool-a --tasks T1,T4

Fairness rules the harness enforces or assumes (Lecture 10.4):
  - same tasks, same base commit, same held-out tests for every tool
  - the tool never sees the acceptance tests (keep them outside the repository in real use)
  - success needs all four checks, not just the acceptance tests
  - cost counts every attempt, including failures
"""

import csv
import fnmatch
import json
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TASKS = Path(__file__).resolve().parent / "tasks"
RECORDINGS = ROOT / "labs" / "s10" / "recordings"
REVIEW_LOG = ROOT / "labs" / "s10" / "review-log.csv"
RESULTS = ROOT / "labs" / "s10" / "results.json"


def is_success(result: dict) -> bool:
    """A task succeeds only if the patch applied AND acceptance, full suite and lint all passed AND
    every changed file was in scope. Anything else is a failure, however close."""
    return all(result[k] for k in ("applied", "acceptance", "full_suite", "lint", "in_scope"))


def _reason(result: dict) -> str:
    for key, reason in (("applied", "patch did not apply"), ("acceptance", "acceptance"),
                        ("full_suite", "full suite"), ("lint", "lint"), ("in_scope", "out of scope")):
        if not result[key]:
            return reason
    return ""


def summarise(results: list[dict]) -> dict[str, dict]:
    """Summarise results per tool, in order of first appearance. For each tool return:

      tasks                 number of tasks attempted
      successes             number for which is_success() is True
      success_rate          successes / tasks, rounded to 2 places
      total_usd             sum of usd over ALL attempted tasks, rounded to 2 places
      cost_per_success      total_usd / successes rounded to 2 places, or None if no successes
      median_review_minutes median review_minutes over SUCCESSFUL tasks (None if no successes)
      median_changed_lines  median changed_lines over SUCCESSFUL tasks (None if no successes)
      failures              {task: reason} for each failed task, where reason is the FIRST failing
                            check in this order: "patch did not apply", "acceptance", "full suite",
                            "lint", "out of scope"
    Use statistics.median for medians."""
    summary: dict[str, dict] = {}
    for tool in dict.fromkeys(r["tool"] for r in results):
        mine = [r for r in results if r["tool"] == tool]
        ok = [r for r in mine if is_success(r)]
        total = round(sum(r["usd"] for r in mine), 2)
        summary[tool] = {
            "tasks": len(mine),
            "successes": len(ok),
            "success_rate": round(len(ok) / len(mine), 2),
            "total_usd": total,
            "cost_per_success": round(total / len(ok), 2) if ok else None,
            "median_review_minutes": statistics.median(r["review_minutes"] for r in ok) if ok else None,
            "median_changed_lines": statistics.median(r["changed_lines"] for r in ok) if ok else None,
            "failures": {r["task"]: _reason(r) for r in mine if not is_success(r)},
        }
    return summary


def _run(cmd: list[str], cwd: Path) -> bool:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False).returncode == 0


def _review_log() -> dict[tuple[str, str], dict]:
    if not REVIEW_LOG.exists():
        return {}
    with REVIEW_LOG.open(newline="") as handle:
        return {(r["tool"], r["task"]): {"review_minutes": float(r["review_minutes"]), "findings": r["findings"]}
                for r in csv.DictReader(handle)}


def run_task(tool: str, task: str, base: str = "HEAD") -> dict:
    meta = json.loads((RECORDINGS / tool / "meta.json").read_text()).get(task, {})
    allowed = json.loads((TASKS / task / "meta.json").read_text())["allowed_paths"]
    patch = RECORDINGS / tool / f"{task}.patch"
    result = {"tool": tool, "task": task, "applied": False, "acceptance": False, "full_suite": False, "lint": False,
              "in_scope": False, "changed_lines": 0, "usd": meta.get("usd", 0.0), "minutes": meta.get("minutes"),
              **_review_log().get((tool, task), {"review_minutes": None, "findings": ""})}
    worktree = Path(tempfile.mkdtemp(prefix=f"eval-{tool}-{task}-"))
    shutil.rmtree(worktree)
    subprocess.run(["git", "-C", str(ROOT), "worktree", "add", "--detach", str(worktree), base],
                   check=True, capture_output=True)
    try:
        if not patch.exists() or not _run(["git", "apply", str(patch)], worktree):
            return result
        result["applied"] = True
        subprocess.run(["git", "add", "-A"], cwd=worktree, check=True, capture_output=True)
        numstat = subprocess.run(["git", "diff", "--cached", "--numstat"], cwd=worktree, capture_output=True,
                                 text=True).stdout.splitlines()
        files = [row.split("\t", 2)[2] for row in numstat]
        result["changed_lines"] = sum(int(a) + int(r) for a, r, _ in (row.split("\t", 2) for row in numstat)
                                      if a.isdigit() and r.isdigit())
        result["in_scope"] = bool(files) and all(any(fnmatch.fnmatch(f, g) for g in allowed) for f in files)
        held_out = worktree / "services" / "orders" / "tests" / f"test_heldout_{task.lower()}.py"
        shutil.copy(TASKS / task / "test_acceptance.py", held_out)
        tests = worktree / "services" / "orders"
        py = sys.executable
        result["acceptance"] = _run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(held_out)], tests)
        result["full_suite"] = _run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests",
                                     f"--deselect=tests/{held_out.name}"], tests)
        held_out.unlink()
        result["lint"] = _run([py, "-m", "ruff", "check", "services/orders"], worktree)
        return result
    finally:
        subprocess.run(["git", "-C", str(ROOT), "worktree", "remove", "--force", str(worktree)], capture_output=True)


def report(summary: dict[str, dict]) -> str:
    lines = ["| Tool | Success | Cost (all tasks) | Cost per success | Median review min | Median lines | Failures |",
             "|---|---|---|---|---|---|---|"]
    for tool, s in summary.items():
        failures = "; ".join(f"{t}: {r}" for t, r in s["failures"].items()) or "none"
        cps = f"${s['cost_per_success']:.2f}" if s["cost_per_success"] is not None else "n/a"
        lines.append(f"| {tool} | {s['successes']}/{s['tasks']} ({s['success_rate']:.0%}) | ${s['total_usd']:.2f} | "
                     f"{cps} | {s['median_review_minutes']} | {s['median_changed_lines']} | {failures} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    tools = args[args.index("--tools") + 1].split(",") if "--tools" in args else \
        sorted(p.name for p in RECORDINGS.iterdir() if p.is_dir())
    tasks = args[args.index("--tasks") + 1].split(",") if "--tasks" in args else \
        sorted(p.name for p in TASKS.iterdir() if p.is_dir())
    results = [run_task(tool, task) for tool in tools for task in tasks]
    RESULTS.write_text(json.dumps(results, indent=1))
    print(report(summarise(results)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
