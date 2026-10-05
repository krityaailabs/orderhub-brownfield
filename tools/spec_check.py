"""Spec and slice checker: is this specification agent-ready, and is the plan reviewable?

Usage: python tools/spec_check.py [spec.md plan.md]   (or: make spec-check)
With no arguments, checks every docs/specs/<name>.md that has a matching <name>.plan.md.

The checks are a rubric, not a judge of quality: a spec can pass and still be wrong.
"""

import re  # noqa: F401  (used once the Lab s03 stubs are implemented)
import sys
from pathlib import Path

REQUIRED_SECTIONS = ("Intent", "Context", "Constraints", "Acceptance criteria", "Non-goals", "Open questions")
MIN_CRITERIA = 3
MAX_SLICE_LINES = 300


def parse_sections(text: str) -> dict[str, str]:
    """Split markdown into {level-2 heading: body}. Headings keep their original case."""
    raise NotImplementedError("Lab s03: implement parse_sections")


def _section(sections: dict[str, str], name: str) -> str | None:
    for heading, body in sections.items():
        if heading.lower().startswith(name.lower()):
            return body
    return None


def parse_criteria(text: str) -> list[tuple[str, str]]:
    """Return [(id, text)] for each criterion in the 'Acceptance criteria' section.

    A criterion is a bullet that starts with a bold id: `- **AC-1** Given ..., when ..., then ...`.
    The text is everything after the id, stripped. Order is preserved. No section: empty list."""
    raise NotImplementedError("Lab s03: implement parse_criteria")


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
    raise NotImplementedError("Lab s03: implement check_spec")


def parse_slices(plan_text: str) -> list[dict]:
    """Parse slices from a plan. Each slice is a level-3 heading `### S<n>: <title>` followed by
    bullet lines in any order:
      - Criteria: AC-1, AC-5
      - Size: ~150 lines
      - Depends on: S1, S2   (or 'none')
    Return [{'id': 'S1', 'title': str, 'criteria': [..], 'size': int | None, 'depends': [..]}]
    in document order. Missing lines give [] or None."""
    raise NotImplementedError("Lab s03: implement parse_slices")


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
    raise NotImplementedError("Lab s03: implement check_slices")


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
                       if not p.name.endswith(".plan.md") and p.name not in ("template.md", "README.md"))
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
