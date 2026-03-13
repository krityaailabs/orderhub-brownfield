"""Idempotency keys for unsafe HTTP requests (docs/specs/cancellation.md).

A client that retries a request (after a timeout, say) sends the same Idempotency-Key header.
The first request runs and its response is stored; a repeat with the same key and the same
request returns the stored response without running again. Reusing a key for a different
request is an error.
"""

import hashlib
import json

from sqlalchemy.orm import Session

from .errors import ValidationFailed
from .models import IdempotencyRecord

MAX_KEY_LENGTH = 128


def request_fingerprint(method: str, path: str, body: dict | None) -> str:
    """Return a SHA-256 hex digest that identifies the request: method (upper-cased), path, and
    the body serialised as JSON with sorted keys and no spaces (None counts as an empty object).
    Two requests that differ only in key order or whitespace have the same fingerprint."""
    canonical = json.dumps(body or {}, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(f"{method.upper()} {path}\n{canonical}".encode("utf-8")).hexdigest()


def lookup(session: Session, key: str, fingerprint: str) -> tuple[int, dict] | None:
    """Return (status_code, response_body) stored for key, or None if the key is new.

    Raise ValidationFailed("idempotency key is too long") if the key is longer than MAX_KEY_LENGTH,
    ValidationFailed("idempotency key is empty") if it is blank, and
    ValidationFailed("idempotency key reused for a different request") if the stored fingerprint
    differs from fingerprint."""
    if not key.strip():
        raise ValidationFailed("idempotency key is empty")
    if len(key) > MAX_KEY_LENGTH:
        raise ValidationFailed("idempotency key is too long")
    record = session.get(IdempotencyRecord, key)
    if record is None:
        return None
    if record.fingerprint != fingerprint:
        raise ValidationFailed("idempotency key reused for a different request")
    return record.status_code, json.loads(record.response_json)


def record(session: Session, key: str, fingerprint: str, status_code: int, body: dict) -> None:
    """Store the outcome for key and commit. Only successful outcomes (status 200 to 299) are
    stored; for any other status, do nothing, so a client can retry after fixing the problem."""
    if not 200 <= status_code < 300:
        return
    session.add(
        IdempotencyRecord(
            key=key, fingerprint=fingerprint, status_code=status_code, response_json=json.dumps(body, sort_keys=True)
        )
    )
    session.commit()
