"""Cost per merged pull request, from parameters you can defend (Section 12, Lecture 12.4).

Every parameter carries a value AND a source. The model refuses to run if any value or source is missing,
and it reports how many of the numbers behind each result are assumptions, so nobody can quote a cost
without seeing what it rests on. Sources start with one of:

  measured:    from your own data (the metrics report, your billing export, a time study)
  quote:       a price or term from a contract or a vendor's published price list, with its date
  assumption:  a number you chose; say why, and replace it when you can

Model, per merged pull request (rate = loaded cost per engineer hour):

  licence     = licence_per_engineer_month / merged_prs_per_engineer_month
  enablement  = enablement_hours_per_engineer_month x rate / merged_prs_per_engineer_month
  usage       = agent_usage_per_pr
  author      = author_hours_per_pr x rate
  review      = review_hours_per_pr x rate
  rework      = rework_rate x rework_hours_per_reworked_pr x rate
  total       = the sum

Parameters merge in order: shared < arm (baseline or agents) < scenario (small, medium, large) < the
scenario's own section for that arm (for example a volume discount that only applies to the agents arm).

Usage: python tools/metrics/cost_model.py [labs/s12/cost-scenarios.json]
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARAMETERS = ("engineers", "loaded_cost_per_engineer_hour", "licence_per_engineer_month", "agent_usage_per_pr",
              "merged_prs_per_engineer_month", "author_hours_per_pr", "review_hours_per_pr", "rework_rate",
              "rework_hours_per_reworked_pr", "enablement_hours_per_engineer_month")
SOURCE_KINDS = ("measured:", "quote:", "assumption:")
PARTS = ("licence", "enablement", "usage", "author", "review", "rework")


def validate(params: dict) -> list[str]:
    """Problems with a merged parameter set, one string per problem, in PARAMETERS order:
      "<name>: missing"                 the parameter isn't there at all
      "<name>: no value"                value is None
      "<name>: no source"               source missing, empty, or not starting with one of SOURCE_KINDS
      "<name>: must be > 0"             merged_prs_per_engineer_month and engineers must be positive
      "<name>: must be 0..1"            rework_rate outside 0 to 1
    Unknown parameter names are problems too ("<name>: unknown"), after the known ones, sorted."""
    problems = []
    for name in PARAMETERS:
        entry = params.get(name)
        if entry is None:
            problems.append(f"{name}: missing")
            continue
        value, source = entry.get("value"), str(entry.get("source") or "")
        if value is None:
            problems.append(f"{name}: no value")
        if not source.startswith(SOURCE_KINDS):
            problems.append(f"{name}: no source")
        if value is None:
            continue
        if name in ("merged_prs_per_engineer_month", "engineers") and value <= 0:
            problems.append(f"{name}: must be > 0")
        if name == "rework_rate" and not 0 <= value <= 1:
            problems.append(f"{name}: must be 0..1")
    problems += [f"{name}: unknown" for name in sorted(set(params) - set(PARAMETERS))]
    return problems


def cost_per_merged_pr(params: dict) -> dict:
    """Cost per merged pull request, by part, each rounded to 2 places, plus:
      total        sum of the unrounded parts, rounded to 2 places
      assumptions  number of parameters whose source starts with "assumption:"
      monthly      total x engineers x merged_prs_per_engineer_month, rounded to 0 places
    Raises ValueError listing every problem from validate() if there are any."""
    problems = validate(params)
    if problems:
        raise ValueError("; ".join(problems))
    v = {name: params[name]["value"] for name in PARAMETERS}
    rate, prs = v["loaded_cost_per_engineer_hour"], v["merged_prs_per_engineer_month"]
    parts = {"licence": v["licence_per_engineer_month"] / prs,
             "enablement": v["enablement_hours_per_engineer_month"] * rate / prs,
             "usage": v["agent_usage_per_pr"],
             "author": v["author_hours_per_pr"] * rate,
             "review": v["review_hours_per_pr"] * rate,
             "rework": v["rework_rate"] * v["rework_hours_per_reworked_pr"] * rate}
    total = sum(parts.values())
    result = {k: round(x, 2) for k, x in parts.items()}
    result["total"] = round(total, 2)
    result["assumptions"] = sum(str(params[n]["source"]).startswith("assumption:") for n in PARAMETERS)
    result["monthly"] = round(total * v["engineers"] * prs)
    return result


def merged(config: dict, arm: str, scenario: str) -> dict:
    own = config["scenarios"][scenario]
    common = {k: v for k, v in own.items() if k not in config["arms"]}
    return {**config.get("shared", {}), **config["arms"][arm], **common, **own.get(arm, {})}


def table(config: dict) -> str:
    lines = ["| Scenario | Arm | " + " | ".join(p.capitalize() for p in PARTS) + " | Total per PR | Per month | "
             "Assumptions |", "|---|---|" + "---|" * (len(PARTS) + 3)]
    problems = []
    for scenario in config["scenarios"]:
        for arm in config["arms"]:
            try:
                r = cost_per_merged_pr(merged(config, arm, scenario))
            except ValueError as exc:
                problems.append(f"{scenario}/{arm}: {exc}")
                continue
            lines.append(f"| {scenario} | {arm} | " + " | ".join(f"{r[p]:.2f}" for p in PARTS)
                         + f" | **{r['total']:.2f}** | {r['monthly']:,} | {r['assumptions']} of {len(PARAMETERS)} |")
    if problems:
        return "cost model refused to run:\n" + "\n".join(f"  {p}" for p in problems)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    path = Path(args[0]) if args else ROOT / "labs" / "s12" / "cost-scenarios.json"
    config = json.loads(path.read_text())
    print(f"Currency: {config.get('currency', 'not stated')}. {config.get('note', '')}".strip())
    out = table(config)
    print(out)
    return 1 if out.startswith("cost model refused") else 0


if __name__ == "__main__":
    sys.exit(main())
