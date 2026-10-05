# Lab s03 hints

## parse_criteria
1. Get the Acceptance criteria body with `_section(parse_sections(text), "Acceptance criteria")`.
2. Each criterion is a bullet `- **AC-n** text`; use one regex with `re.M`.
3. Return tuples `(id, text.strip())` in order; return `[]` when the section is missing.

## check_spec
1. Build the problem list in the order the docstring gives.
2. For Given, When, Then use `re.search(rf"\b{word}\b", lowered)` so "forgiven" doesn't count, and compare the match positions.
3. A non-goals bullet is a line starting with `- ` followed by text.

## parse_slices and check_slices
1. Split the plan on lines starting with `### `; the first chunk is the preamble.
2. "Depends on: none" means an empty list; otherwise collect every `S<n>`.
3. Track the ids you've seen so far to check that dependencies point backwards, and a set of covered criteria for the final check.
