# Lab s07 hints

## Permission profile (7.2)
1. Start from deny: `Bash(git push *)`, `Bash(curl *)`, `Bash(wget *)`, `Bash(ssh *)`, `Bash(scp *)`, `Bash(pip install *)`, `Bash(npm install *)`, `Read(./.env)`, `Edit(./instructor/**)`. Add `Edit(./.claude/**)` so the agent can't loosen its own profile.
2. Allow only the project's commands: `Bash(make test)`, `Bash(make lint)`, … and read-only git (`Bash(git diff *)`, `Bash(git log *)`).
3. Put commits and branch changes under `ask`, so you see each one.
4. Remove `defaultMode: acceptEdits` unless you've decided edits should never prompt.
5. Keep the `hooks` section.

## is_placeholder and find_secrets (7.3)
1. `is_placeholder`: lower-case the value; any placeholder word → True; `len(set(value)) == 1` → True.
2. `find_secrets`: handle `.env` files first and return early.
3. For each line: skip it if `ALLOW_MARKER in line`; then for each `(rule, pattern, group)` in `RULES`, look through `pattern.finditer(line)` for the first match whose value isn't a placeholder; append one `Finding` and `break`.
4. The preview is `redact(value)`.

## Running the gate after the scanner works
The scanner will report 8 findings. Fake keys that are test fixtures in `tools/tests/test_context_check.py`, the recorded diff `labs/s06/prs/R3.diff`, and the labelled CWE-798 example in `labs/s07/snippets/` are deliberate. Mark the test lines with `# secret-scan: allow <reason>` and add the recorded diffs and labelled examples to `.secret-scan-ignore` with a reason. The token in `config.py` is not a fixture: remove the default.

## Snippets (7.6)
1. SQL: pass the value as a parameter: `conn.execute("... WHERE country = ? ...", (country,))`.
2. Shell: don't build a command string. The standard library's `tarfile` does it without a shell: `tarfile.open(dest, "w:gz")` and `archive.add(path, arcname=name)`.

## The CI workflow (7.8)
Copy the setup steps from `ci.yml` and run `python tools/security_gate.py`. Then, in the repository settings, add the job as a required status check for `main`.
