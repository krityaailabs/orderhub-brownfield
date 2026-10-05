# Expected output: Lab s07

## At s07-start

`make security`:
```
security: FAILED secrets
    NotImplementedError: Lab s07: implement find_secrets
security: FAILED permissions
    PROBLEM  blanket allow: Bash
    ...
    permission-check: .claude/settings.json: 12 problem(s), 1 warning(s).
security: ok     static
security: ok     dependencies
security: ok     canary
security-gate: 3 of 5 checks passed; failed: secrets, permissions
```
`make test`: Python `1 failed, 71 passed` (`test_no_credential_has_a_default`); tools `28 failed, 104 passed` (secret scanner stubs, the profile, the snippets, the hook and the workflow).
`python tools/untrusted_text.py scan`: one hit, the hidden comment in `docs/issues/Q15.md` (205 chars).

## After implementing the scanner, before triage

```
SECRET  labs/s06/prs/R3.diff:1169: aws-access-key-id (AKIA... 20 chars)
...
SECRET  services/orders/orderhub/config.py:26: env-default (whk_... 33 chars)
SECRET  tools/tests/test_context_check.py:149: aws-access-key-id (AKIA... 20 chars)
SECRET  tools/tests/test_context_check.py:150: private-key (----... 31 chars)
```
Previews show the first four characters and the length only.

## At s07

`make security`: `security-gate: 5 of 5 checks passed.` `make test`: Python `72 passed`; tools `132 passed`.
The pre-commit hook blocks a staged file containing `api_key = "<24 hex characters>"`:
```
SECRET  tmp_planted.py:1: assigned-secret (3f9a... 24 chars)
secret-scan: 1 finding(s). Remove the value, rotate it if it was real, and load it from the environment.
```
