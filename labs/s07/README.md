# Lab s07: a security gate for agent-assisted development (Section 7)

**Start tag:** `s07-start` · **Solved tag:** `s07` · **Time:** 2–3 hours · **Agent usage:** recommended for the scanner; the permission profile and the decisions are yours

Everything in this lab is defensive. The flawed-code examples are short, labelled snippets of well-known weakness classes (CWE), shown with the scanner finding and the fix. The only "injected instruction" is a harmless canary.

At `s07-start`:
- `.claude/settings.json` allows everything (`Bash`, `Edit`, `WebFetch`) and accepts edits automatically: an agent's convenience setup.
- An agent change added a default value for the warehouse token in `services/orders/orderhub/config.py`, "so the webhook works out of the box". (The value is synthetic, but treat it as if it were real.)
- `tools/secret_scan.py` has two stubs: `is_placeholder` and `find_secrets`.
- The pre-commit hook doesn't run the secret scanner, and CI has no security workflow.
- `labs/s07/snippets/fix_me_sql.py` and `fix_me_shell.py` have scanner findings.
- `docs/issues/Q15.md` contains a hidden instruction for agents (the canary).

`make security` fails at the start: 3 of 5 checks pass (secrets, permissions fail).

| Lecture | Task | Done when |
|---|---|---|
| 7.1 | Draw the threat model for an agent working on OrderHub (start from `docs/course/agent-threat-model.md`) | Assets, actors, boundaries, controls written |
| 7.2 | Replace the permission profile in `.claude/settings.json`: allow tests and lint; deny network tools, pushes, installs, `.env` reads, edits to `instructor/` and `.claude/` | `python tools/permission_check.py` reports 0 problems; `tools/tests/test_permission_profile.py` passes |
| 7.3 | Implement `is_placeholder` and `find_secrets`; add the scanner to `tools/hooks/pre-commit`; prove it blocks a planted fake key; remove the token default | `tools/tests/test_secret_scan.py` and `tests/test_config.py` pass; a commit with a fake key is blocked |
| 7.4 | Audit three suggested packages with `docs/course/dependency-audit.md` | Worksheet filled; compare with `ANSWERS.md` |
| 7.5 | Run an agent on Q15 with and without the defence; the canary must not reach product code | `python tools/untrusted_text.py canary` passes; one context-file line added |
| 7.6 | Run the scanner on `labs/s07/snippets`; fix the two `fix_me_*` snippets | `tools/tests/test_security_snippets.py` passes |
| 7.7 | Fill `docs/course/mcp-vetting-checklist.md` for one MCP server you might install | Checklist filled |
| 7.8 | Add `.github/workflows/security.yml` running `tools/security_gate.py`; make it a required check | `make security` passes: 5 of 5; the gate fails if you re-plant the token |

```bash
git switch -c my-s07 s07-start
make security                                   # 3 of 5 checks pass
.venv/bin/python -m pytest -q tools/tests/test_secret_scan.py
```

## Prove the hook blocks a planted fake key (7.3)

After `make install-hooks`, create a file with a key-shaped value (build it in your shell so you never paste a real one), stage it and commit. The hook must block the commit and show only a redacted preview. Then delete the file.

```bash
printf 'api_key = "%s"\n' "$(python3 -c 'import secrets; print(secrets.token_hex(12))')" > tmp_planted.py
git add tmp_planted.py && git commit -m "planted key test"     # blocked
git restore --staged tmp_planted.py && rm tmp_planted.py
```

## Rules

1. Never paste a real credential anywhere in this lab, including into an agent session.
2. If a check reports a false positive, fix it with the narrowest tool: an inline `# secret-scan: allow <reason>`, or one glob in `.secret-scan-ignore` with a reason. Say why in the commit message.
3. Don't weaken a check to make the gate pass. If you think a rule is wrong, write down why and ask.
