# Plan: Idempotent order cancellation

Spec: `docs/specs/cancellation.md`. One slice per pull request; failing tests first.

### S1: Reproduce Q12 and make cancel a no-op on a cancelled order
- Criteria: AC-1, AC-5
- Size: ~40 lines
- Depends on: none
- Change: failing test that cancels twice and checks stock; early return in `cancel_order`.

### S2: Idempotency store
- Criteria: AC-2, AC-3
- Size: ~120 lines
- Depends on: S1
- Change: `IdempotencyRecord` model; `orderhub/idempotency.py` (fingerprint, lookup, record) with unit tests.

### S3: Wire the key into the cancel endpoint
- Criteria: AC-2, AC-3, AC-4
- Size: ~60 lines
- Depends on: S2
- Change: optional `Idempotency-Key` header in `api.py`; store only successful outcomes.

### S4: Commit hooks for the team
- Criteria: AC-5
- Size: ~120 lines
- Depends on: none
- Change: `tools/precommit.py` choosing checks by changed files; `make install-hooks`; agent hook examples.

## Progress notes

Keep `docs/specs/cancellation.progress.md` updated at the end of each session (template in `docs/specs/progress-template.md`).
