"""Spec and slice checker: is this specification agent-ready, and is the plan reviewable?

Usage: python tools/spec_check.py [spec.md plan.md]   (or: make spec-check)
With no arguments, checks every docs/specs/<name>.md that has a matching <name>.plan.md.

The checks are a rubric, not a judge of quality: a spec can pass and still be wrong.
"""

import re
import sys
from pathlib import Path

REQUIRED_SECTIONS = ("Intent", "Context", "Constraints", "Acceptance criteria", "Non-goals", "Open questions")
MIN_CRITERIA = 3
MAX_SLICE_LINES = 300


def parse_sections(text: str) -> dict[str, str]:
    """Split markdown into {level-2 heading: body}. Headings keep their original case."""
    sections: dict[str, str] = {}
    current = None
    buffer: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current, buffer = m.group(1), []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def _section(sections: dict[str, str], name: str) -> str | None:
    for heading, body in sections.items():
        if heading.lower().startswith(name.lower()):
            return body
    return None


def parse_criteria(text: str) -> list[tuple[str, str]]:
    """Return [(id, text)] for each criterion in the 'Acceptance criteria' section.

    A criterion is a bullet that starts with a bold id: `- **AC-1** Given ..., when ..., then ...`.
    The text is everything after the id, stripped. Order is preserved. No section: empty list."""
    body = _section(parse_sections(text), "Acceptance criteria")
    if body is None:
        return []
    out = []
    for m in re.finditer(r"^\s*-\s+\*\*(AC-\d+)\*\*\s*(.+)$", body, flags=re.M):
        out.append((m.group(1), m.group(2).strip()))
    return out


def check_spec(text: str) -> list[str]:
    """Return a list of problems (empty means the spec passes the rubric):

    - 'missing section: <name>' for each REQUIRED_SECTIONS entry without a level-2 heading
      (prefix match, case-insensitive)
    - 'too few acceptance criteria: <n> (minimum 3)'
    - 'criteria ids must be AC-1..AC-n in order' if ids are not exactly AC-1, AC-2, ... in order
    - '<id>: needs Given, When and Then in that order' for each criterion missing them
      (case-insensitive whole words)
    - 'non-goals: list at least one' if the Non-goals section has no bullet
    - 'unresolved TODO' if the text contains TODO anywhere
    """
    problems = []
    sections = parse_sections(text)
    for name in REQUIRED_SECTIONS:
        if _section(sections, name) is None:
            problems.append(f"missing section: {name}")
    criteria = parse_criteria(text)
    if len(criteria) < MIN_CRITERIA:
        problems.append(f"too few acceptance criteria: {len(criteria)} (minimum {MIN_CRITERIA})")
    if [cid for cid, _ in criteria] != [f"AC-{i}" for i in range(1, len(criteria) + 1)]:
        problems.append("criteria ids must be AC-1..AC-n in order")
    for cid, body in criteria:
        lowered = body.lower()
        positions = [re.search(rf"\b{word}\b", lowered) for word in ("given", "when", "then")]
        if not all(positions) or not (positions[0].start() < positions[1].start() < positions[2].start()):
            problems.append(f"{cid}: needs Given, When and Then in that order")
    non_goals = _section(sections, "Non-goals")
    if non_goals is not None and not re.search(r"^\s*-\s+\S", non_goals, flags=re.M):
        problems.append("non-goals: list at least one")
    if "TODO" in text:
        problems.append("unresolved TODO")
    return problems


def parse_slices(plan_text: str) -> list[dict]:
    """Parse slices from a plan. Each slice is a level-3 heading `### S<n>: <title>` followed by
    bullet lines in any order:
      - Criteria: AC-1, AC-5
      - Size: ~150 lines
      - Depends on: S1, S2   (or 'none')
    Return [{'id': 'S1', 'title': str, 'criteria': [..], 'size': int | None, 'depends': [..]}]
    in document order. Missing lines give [] or None."""
    slices = []
    blocks = re.split(r"^###\s+", plan_text, flags=re.M)[1:]
    for block in blocks:
        head, _, rest = block.partition("\n")
        m = re.match(r"(S\d+)\s*:\s*(.+)", head.strip())
        if not m:
            continue
        crit = re.search(r"^\s*-\s*Criteria:\s*(.+)$", rest, flags=re.M | re.I)
        size = re.search(r"^\s*-\s*Size:\s*~?\s*(\d+)", rest, flags=re.M | re.I)
        deps = re.search(r"^\s*-\s*Depends on:\s*(.+)$", rest, flags=re.M | re.I)
        dep_list = []
        if deps and deps.group(1).strip().lower() != "none":
            dep_list = re.findall(r"S\d+", deps.group(1))
        slices.append({
            "id": m.group(1),
            "title": m.group(2).strip(),
            "criteria": re.findall(r"AC-\d+", crit.group(1)) if crit else [],
            "size": int(size.group(1)) if size else None,
            "depends": dep_list,
        })
    return slices


def check_slices(slices: list[dict], criteria_ids: list[str], max_lines: int = MAX_SLICE_LINES) -> list[str]:
    """Return problems with a slice plan:

    - 'no slices' if the list is empty
    - '<slice>: covers no acceptance criterion'
    - '<slice>: unknown criterion <id>' for ids not in criteria_ids
    - '<slice>: no size estimate'
    - '<slice>: ~<n> lines is over the <max> line review budget; split it'
    - '<slice>: depends on <dep>, which is not an earlier slice'
    - '<criterion>: not covered by any slice' for each criterion no slice references
    """
    if not slices:
        return ["no slices"]
    problems = []
    seen: list[str] = []
    covered: set[str] = set()
    for s in slices:
        sid = s["id"]
        if not s["criteria"]:
            problems.append(f"{sid}: covers no acceptance criterion")
        for cid in s["criteria"]:
            if cid not in criteria_ids:
                problems.append(f"{sid}: unknown criterion {cid}")
            covered.add(cid)
        if s["size"] is None:
            problems.append(f"{sid}: no size estimate")
        elif s["size"] > max_lines:
            problems.append(f"{sid}: ~{s['size']} lines is over the {max_lines} line review budget; split it")
        for dep in s["depends"]:
            if dep not in seen:
                problems.append(f"{sid}: depends on {dep}, which is not an earlier slice")
        seen.append(sid)
    for cid in criteria_ids:
        if cid not in covered:
            problems.append(f"{cid}: not covered by any slice")
    return problems


def check_pair(spec_path: Path, plan_path: Path) -> list[str]:
    spec = spec_path.read_text(encoding="utf-8")
    plan = plan_path.read_text(encoding="utf-8")
    problems = [f"spec: {p}" for p in check_spec(spec)]
    ids = [cid for cid, _ in parse_criteria(spec)]
    problems += [f"plan: {p}" for p in check_slices(parse_slices(plan), ids)]
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    root = Path(__file__).resolve().parents[1]
    if argv:
        pairs = [(Path(argv[0]), Path(argv[1]))]
    else:
        specs = sorted(p for p in (root / "docs" / "specs").glob("*.md")
                       if not p.name.endswith((".plan.md", ".progress.md"))
                       and p.name not in ("template.md", "README.md", "progress-template.md"))
        pairs = [(p, p.with_name(p.stem + ".plan.md")) for p in specs]
    if not pairs:
        print("No specs found in docs/specs.")
        return 1
    failed = 0
    for spec, plan in pairs:
        if not plan.exists():
            print(f"FAIL  {spec.name}: no plan file {plan.name}")
            failed += 1
            continue
        problems = check_pair(spec, plan)
        print(("OK    " if not problems else "FAIL  ") + f"{spec.name} + {plan.name}")
        for p in problems:
            print(f"      - {p}")
        failed += bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotImplementedError as exc:
        print(f"Not implemented yet: {exc}. See labs/s03/README.md.")
        sys.exit(2)
