# Troubleshooting: Lab s02

| Symptom | Likely cause | Fix |
|---|---|---|
| `NotImplementedError: Lab s02` | A stub is still in place | Implement that function; the test name tells you which |
| `make context-check` reports `'make it' is not a Makefile target` | Your `check_commands` matches prose | Only count commands written in backticks |
| `test_root_claude_md_also_stops_nested_agents_md` fails | Nested AGENTS.md added even when a CLAUDE.md exists above | AGENTS.md reading is off for the whole session in the default mode once any CLAUDE file exists in cwd or above |
| `test_cloud_agent_reads_*` order differs | Files appended in a different order | Order: copilot-instructions, matching .instructions.md, AGENTS.md root to leaf, then CLAUDE.md |
| Your tool doesn't load AGENTS.md although the simulator says it should | Tool version, setting or surface differs from the documented rules | Check the tool's version and settings; the simulator encodes the documentation as of 5 Oct 2026 |
