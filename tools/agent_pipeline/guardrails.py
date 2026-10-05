"""Guardrails for unattended agents (Lecture 9.3): what a run may change, and how much."""

import fnmatch
from dataclasses import dataclass


@dataclass(frozen=True)
class DiffStats:
    files: list[str]          # changed paths, repository-relative, POSIX style
    changed_lines: int        # added + removed lines
    minutes: float            # wall-clock time the agent ran
    usd: float | None         # cost reported by the agent (None if it didn't report one)


def matches(path: str, globs: list[str]) -> bool:
    """True if path matches any glob. `**/` also matches at the top level ("**/AGENTS.md" matches "AGENTS.md")."""
    for g in globs:
        if fnmatch.fnmatch(path, g) or (g.startswith("**/") and fnmatch.fnmatch(path, g[3:])):
            return True
    return False


def check_scope(paths: list[str], allowed: list[str], denied: list[str]) -> list[str]:
    """Return one problem per path that the run may not change, in the order given.

    Rules:
      - a path matching any `denied` glob is a problem: "denied path: <path>" (denied wins over allowed)
      - otherwise, a path matching no `allowed` glob is a problem: "outside allowed paths: <path>"
      - an empty `paths` list is a problem too: ["no changes"] (a run that changes nothing opens no PR)
    Use matches() for glob matching."""
    if not paths:
        return ["no changes"]
    problems = []
    for path in paths:
        if matches(path, denied):
            problems.append(f"denied path: {path}")
        elif not matches(path, allowed):
            problems.append(f"outside allowed paths: {path}")
    return problems


def check_budget(stats: DiffStats, budget: dict) -> list[str]:
    """Return one problem per exceeded limit, in this order: files, lines, minutes, usd.

    budget keys (all optional; a missing key means no limit): max_files, max_changed_lines,
    max_minutes, max_usd. Messages:
      "too many files: <n> > <max>"            (n = number of changed files)
      "too many changed lines: <n> > <max>"
      "too long: <minutes:.1f> min > <max> min"
      "too expensive: $<usd:.2f> > $<max:.2f>"
    If max_usd is set and the agent reported no cost (usd is None), that is a problem too:
      "cost not reported (max_usd is set)"   (an unmeasured budget is not a budget)."""
    problems = []
    if "max_files" in budget and len(stats.files) > budget["max_files"]:
        problems.append(f"too many files: {len(stats.files)} > {budget['max_files']}")
    if "max_changed_lines" in budget and stats.changed_lines > budget["max_changed_lines"]:
        problems.append(f"too many changed lines: {stats.changed_lines} > {budget['max_changed_lines']}")
    if "max_minutes" in budget and stats.minutes > budget["max_minutes"]:
        problems.append(f"too long: {stats.minutes:.1f} min > {budget['max_minutes']} min")
    if "max_usd" in budget:
        if stats.usd is None:
            problems.append("cost not reported (max_usd is set)")
        elif stats.usd > budget["max_usd"]:
            problems.append(f"too expensive: ${stats.usd:.2f} > ${budget['max_usd']:.2f}")
    return problems
