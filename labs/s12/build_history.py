"""Build the SYNTHETIC OrderHub delivery history for Lab s12 (Section 12).

Nothing here is real team data. The script generates, deterministically (fixed seed), 26 weeks of a
fictional eight-person team's pull requests, half before and half after an agent rollout, and writes:

  <repo>                         a Git repository: one squash commit per merged pull request, with trailers
                                 PR, Author, Agent-Assisted, Fixes-PR and Reverts-PR (what your code host
                                 writes when it squash-merges, plus two trailers your team would add)
  labs/s12/data/pr_events.csv    the code host's export: opened, first review, merged (UTC)
  labs/s12/data/deploys.csv      the CD system's export: every deployment, scheduled or unplanned, its
                                 outcome, and the pull requests it shipped

The numbers in the generator are invented to make the lab's points visible (bigger agent-assisted pull
requests, longer review waits, a self-selected pilot group). They are not findings about any tool.

Usage: python labs/s12/build_history.py [/tmp/orderhub-history]     (default path shown)
"""

import csv
import math
import random
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
START = datetime(2026, 1, 5, tzinfo=timezone.utc)      # Monday, week 1
ROLLOUT = datetime(2026, 4, 6, tzinfo=timezone.utc)    # Monday, week 14: agents available to the pilot
END = datetime(2026, 7, 5, 23, 59, tzinfo=timezone.utc)
WEEKS = 26
VOLUNTEERS = ("ana", "ben", "chen")                     # self-selected pilot group
OTHERS = ("dev", "eli", "fay", "gus", "hana")
BOT = "orderhub-bot"
AREAS = ("orders", "returns", "inventory", "billing", "api", "customers")


def _lognormal(rng: random.Random, median: float, spread: float) -> float:
    return median * math.exp(rng.gauss(0, spread))


def _working_time(rng: random.Random, day: datetime) -> datetime:
    return day.replace(hour=rng.randint(8, 16), minute=rng.randint(0, 59))


def generate() -> tuple[list[dict], list[dict]]:
    """Return (pull requests, deployments). Each PR: number, author, agent, opened, first_review, merged,
    files [(path, added, deleted)], fixes, reverts, incident."""
    rng = random.Random(12)
    prs: list[dict] = []
    for week in range(WEEKS):
        monday = START + timedelta(weeks=week)
        pilot = monday >= ROLLOUT
        for author in VOLUNTEERS + OTHERS:
            rate = 1.0 if author in VOLUNTEERS else 0.8
            if pilot and author in VOLUNTEERS:
                rate = 1.7
            for _ in range(sum(rng.random() < rate / 2 for _ in range(2)) + (rng.random() < rate - 1)):
                agent = pilot and rng.random() < (0.85 if author in VOLUNTEERS else 0.2)
                median = (240 if agent else 110) * (0.8 if author in VOLUNTEERS else 1.0)
                size = max(4, int(_lognormal(rng, median, 0.6)))
                opened = _working_time(rng, monday + timedelta(days=rng.randint(0, 4)))
                prs.append(_pr(rng, author, agent, opened, size, volunteer=author in VOLUNTEERS))
        if pilot:  # weekly dependency bump from the Section 9 pipeline: tiny manifest change, big lock file
            opened = (monday + timedelta(days=1)).replace(hour=6, minute=0)
            pr = _pr(rng, BOT, True, opened, 2, volunteer=False, rework=False)
            lock = ("requirements.lock", rng.randint(150, 600), rng.randint(150, 600))
            pr["files"] = [("requirements.txt", 1, 1), lock]
            prs.append(pr)
    fixes = []
    for pr in prs:
        if pr.pop("_rework"):
            gap = timedelta(days=rng.uniform(1, 14))
            opened = pr["merged"] + gap
            fix = _pr(rng, pr["author"], pr["agent"], opened, max(3, int(_lognormal(rng, 25, 0.5))),
                      volunteer=pr["author"] in VOLUNTEERS, rework=False)
            fix["_of"] = pr
            fix["_revert"] = rng.random() < 0.15
            if fix["_revert"]:
                fix["files"] = [(p, d, a) for p, a, d in pr["files"]]
            fixes.append(fix)
    prs = [p for p in prs + fixes if p["merged"] <= END]
    prs.sort(key=lambda p: p["opened"])
    for number, pr in enumerate(prs, start=1):
        pr["number"] = number
    for pr in prs:
        of = pr.pop("_of", None)
        revert = pr.pop("_revert", False)
        pr["fixes"] = [of["number"]] if of and not revert else []
        pr["reverts"] = [of["number"]] if of and revert else []
        if of:
            of["incident"] = of["incident"] or revert
    return prs, _deployments(rng, prs)


def _pr(rng: random.Random, author: str, agent: bool, opened: datetime, size: int, volunteer: bool,
        rework: bool = True) -> dict:
    first_review = opened + timedelta(hours=_lognormal(rng, 4, 0.7) * (1 + size / 400))
    merged = first_review + timedelta(hours=_lognormal(rng, 6, 0.7) * (1 + size / 250))
    area = rng.choice(AREAS)
    added = max(1, int(size * rng.uniform(0.55, 0.85)))
    tests = max(0, int(added * rng.uniform(0.2, 0.45)))
    files = [(f"app/{area}/module_{rng.randint(1, 9)}.py", added - tests, size - added),
             (f"tests/{area}/test_module_{rng.randint(1, 9)}.py", tests, 0)]
    p_rework = (0.03 + size / 4000) if volunteer and not agent else (0.04 + size / 3000)
    if agent:
        p_rework += 0.06
    reworked = rework and rng.random() < p_rework
    return {"author": author, "agent": agent, "opened": opened, "first_review": first_review, "merged": merged,
            "files": [f for f in files if f[1] or f[2]], "incident": reworked and rng.random() < 0.5,
            "_rework": reworked}


def _deployments(rng: random.Random, prs: list[dict]) -> list[dict]:
    """Scheduled deployments Tuesday and Thursday at 15:00 ship everything merged since the last one. A
    deployment that ships a PR with an incident fails. Fix and revert PRs for incidents ship in an
    unplanned deployment as soon as they merge."""
    by_number = {p["number"]: p for p in prs}
    urgent = {p["number"] for p in prs if any(by_number[n]["incident"] for n in p["fixes"] + p["reverts"])}
    deploys, shipped, last = [], set(), START
    day = START
    events = []
    while day <= END:
        if day.weekday() in (1, 3):
            events.append(("scheduled", day.replace(hour=15, minute=0)))
        day += timedelta(days=1)
    events += [("unplanned", by_number[n]["merged"] + timedelta(minutes=rng.randint(20, 90))) for n in urgent]
    for kind, at in sorted(events, key=lambda e: e[1]):
        if at > END:
            continue
        if kind == "scheduled":
            batch = [p["number"] for p in prs if last < p["merged"] <= at and p["number"] not in shipped]
            last = at
        else:
            batch = [n for n in urgent if by_number[n]["merged"] <= at and n not in shipped]
        if not batch:
            continue
        shipped.update(batch)
        cause = next((n for n in batch if by_number[n]["incident"]), None)
        deploys.append({"deployed_at": at, "kind": kind, "prs": batch, "outcome": "failed" if cause else "ok",
                        "cause": cause or ""})
    for i, d in enumerate(deploys, start=1):
        d["deploy"] = f"D{i:03d}"
    return deploys


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def write_csvs(prs: list[dict], deploys: list[dict], folder: Path = DATA) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "pr_events.csv").open("w", newline="") as handle:
        w = csv.writer(handle)
        w.writerow(["pr", "author", "opened_at", "first_review_at", "merged_at"])
        for p in prs:
            w.writerow([p["number"], p["author"], _iso(p["opened"]), _iso(p["first_review"]), _iso(p["merged"])])
    with (folder / "deploys.csv").open("w", newline="") as handle:
        w = csv.writer(handle)
        w.writerow(["deploy", "deployed_at", "kind", "outcome", "cause_pr", "prs"])
        for d in deploys:
            w.writerow([d["deploy"], _iso(d["deployed_at"]), d["kind"], d["outcome"], d["cause"],
                        " ".join(str(n) for n in d["prs"])])


def build_repo(prs: list[dict], path: Path) -> None:
    """Write the history with one `git fast-import` stream (one process, a second or two)."""
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)
    contents: dict[str, list[str]] = {}
    out: list[bytes] = []

    def data(text: str) -> None:
        raw = text.encode()
        out.append(b"data %d\n" % len(raw) + raw + b"\n")

    def commit(message: str, when: datetime, changed: dict[str, str]) -> None:
        stamp = f"{int(when.timestamp())} +0000"
        out.append(b"commit refs/heads/main\n")
        out.append(f"committer history <history@example.invalid> {stamp}\n".encode())
        data(message)
        for name, text in changed.items():
            out.append(f"M 100644 inline {name}\n".encode())
            data(text)

    commit("Initial commit\n", START - timedelta(days=1),
           {"README.md": "Synthetic delivery history for OrderHub Lab s12. Not real data.\n"})
    for p in sorted(prs, key=lambda p: p["merged"]):
        changed = {}
        for name, added, deleted in p["files"]:
            lines = contents.get(name, [])
            lines = lines[min(deleted, len(lines)):] + [f"# PR {p['number']} line {i}" for i in range(added)]
            contents[name] = lines
            changed[name] = "\n".join(lines) + ("\n" if lines else "")
        trailers = [f"PR: #{p['number']}", f"Author: {p['author']}", f"Agent-Assisted: {'yes' if p['agent'] else 'no'}"]
        trailers += [f"Fixes-PR: #{n}" for n in p["fixes"]] + [f"Reverts-PR: #{n}" for n in p["reverts"]]
        title = ("Revert" if p["reverts"] else "Fix" if p["fixes"] else "Change") + f" #{p['number']}"
        commit(title + "\n\n" + "\n".join(trailers) + "\n", p["merged"], changed)
    subprocess.run(["git", "fast-import", "--quiet"], cwd=path, input=b"".join(out), check=True)
    subprocess.run(["git", "checkout", "-q", "main"], cwd=path, check=True)


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else Path(tempfile.gettempdir()) / "orderhub-history"
    prs, deploys = generate()
    write_csvs(prs, deploys)
    build_repo(prs, path)
    print(f"history: {len(prs)} merged pull requests, {len(deploys)} deployments -> {path} "
          f"and {DATA.relative_to(HERE.parents[1])}/ (synthetic)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
