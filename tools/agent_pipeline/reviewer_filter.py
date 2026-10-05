"""Tune an automated reviewer for signal (Lecture 9.4).

Automated reviewers post many comments; people stop reading them when most aren't worth acting on.
This filter sits between the reviewer's raw output and the pull request, using a small config
(ci/reviewer-filter.json). It's measured against comments that people have already triaged
(labs/s09/review-comments.json: each comment has "actionable": true or false).

Usage: python tools/agent_pipeline/reviewer_filter.py     (prints the metrics for the current config)
"""

import fnmatch
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "ci" / "reviewer-filter.json"
COMMENTS = ROOT / "labs" / "s09" / "review-comments.json"
SEVERITY = ["info", "nit", "low", "medium", "high"]


def keep(comments: list[dict], config: dict) -> list[dict]:
    """The comments that would be posted, in input order."""
    floor = SEVERITY.index(config.get("min_severity", "info"))
    dropped = set(config.get("drop_categories", []))
    ignored = config.get("ignore_paths", [])
    seen: set[tuple[str, str]] = set()
    out = []
    for c in comments:
        if SEVERITY.index(c["severity"]) < floor or c["category"] in dropped:
            continue
        if any(fnmatch.fnmatch(c["file"], g) for g in ignored):
            continue
        key = (c["file"], c["text"].strip().lower())
        if config.get("dedupe") and key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def metrics(prs: list[dict], config: dict) -> dict:
    kept_noise = kept_signal = lost_signal = 0
    for pr in prs:
        kept = keep(pr["comments"], config)
        kept_ids = {id(c) for c in kept}
        for c in pr["comments"]:
            if c["actionable"] and id(c) not in kept_ids:
                lost_signal += 1
        kept_noise += sum(1 for c in kept if not c["actionable"])
        kept_signal += sum(1 for c in kept if c["actionable"])
    return {"prs": len(prs), "non_actionable_per_pr": round(kept_noise / len(prs), 2),
            "actionable_kept": kept_signal, "actionable_dropped": lost_signal}


def main() -> int:
    prs = json.loads(COMMENTS.read_text())["prs"]
    config = json.loads(CONFIG.read_text())
    m = metrics(prs, config)
    print(f"reviewer-filter: {m['prs']} PRs · non-actionable kept per PR {m['non_actionable_per_pr']} · "
          f"actionable kept {m['actionable_kept']} · actionable dropped {m['actionable_dropped']}")
    ok = m["non_actionable_per_pr"] < 1 and m["actionable_dropped"] == 0
    target = "meets the target" if ok else "target: < 1 non-actionable per PR, 0 actionable dropped"
    print("reviewer-filter: " + target)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
