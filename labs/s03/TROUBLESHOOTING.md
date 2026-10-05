# Troubleshooting: Lab s03

| Symptom | Likely cause | Fix |
|---|---|---|
| `NotImplementedError: Lab s03` | A stub is still in place | Implement the function named in the message |
| A criterion fails Given/When/Then although the words are there | Order is wrong, or the words are inside other words | Use whole-word matches and compare positions |
| `test_parse_slices` gets size `None` | The size line is `Size: 120` without the tilde, or uses another word | Accept an optional `~`; read the first number |
| `make spec-check` says "No specs found" | You named the spec `template.md` or put it elsewhere | `docs/specs/returns.md` and `docs/specs/returns.plan.md` |
| Your spec passes the rubric but a reviewer rejects it | The rubric checks structure, not truth | Check every number by hand; that's what AC-2 and AC-3 are for |
