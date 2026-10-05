# Expected output: Lab s02 (at the solved tag)

`make context-check`
```
Instruction files: .github/copilot-instructions.md, AGENTS.md, legacy/billing/AGENTS.md, web/AGENTS.md
OK     AGENTS.md
OK     legacy/billing/AGENTS.md
OK     web/AGENTS.md

Simulated loading (documented rules, 5 Oct 2026):
  Claude Code, start at root           : ['AGENTS.md']
  Claude Code, after opening legacy file: ['AGENTS.md', 'legacy/billing/AGENTS.md']
  Copilot cloud agent, legacy file     : ['.github/copilot-instructions.md', 'AGENTS.md', 'legacy/billing/AGENTS.md']
  Copilot GitHub.com chat              : ['.github/copilot-instructions.md']
  Cursor, legacy file                  : ['AGENTS.md', 'legacy/billing/AGENTS.md']

Context check passed.
```

`make test` (summary lines): Python `27 passed`; tools `44 passed`; legacy `all checks passed`.

At `s02-start`, `python -m pytest tools/tests -q` shows `32 failed, 12 passed`, and `make context-check` prints `Not implemented yet: Lab s02: implement find_instruction_files.`
