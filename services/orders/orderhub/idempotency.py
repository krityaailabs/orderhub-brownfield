"""Idempotency keys for unsafe HTTP requests (docs/specs/cancellation.md).

A client that retries a request (after a timeout, say) sends the same Idempotency-Key header.
The first request runs and its response is stored; a repeat with the same key and the same
request returns the stored response without running again. Reusing a key for a different
request is an error.
"""

import hashlib  # noqa: F401  (used once the Lab s05 stubs are implemented)
import json  # noqa: F401  (used once the Lab s05 stubs are implemented)

from sqlalchemy.orm import Session

from .errors import ValidationFailed  # noqa: F401
from .models import IdempotencyRecord  # noqa: F401

MAX_KEY_LENGTH = 128


def request_fingerprint(method: str, path: str, body: dict | None) -> str:
    """Return a SHA-256 hex digest that identifies the request: method (upper-cased), path, and
    the body serialised as JSON with sorted keys and no spaces (None counts as an empty object).
    Two requests that differ only in key order or whitespace have the same fingerprint."""
    raise NotImplementedError("Lab s05: implement request_fingerprint")


def lookup(session: Session, key: str, fingerprint: str) -> tuple[int, dict] | None:
    """Return (status_code, response_body) stored for key, or None if the key is new.

    Raise ValidationFailed("idempotency key is too long") if the key is longer than MAX_KEY_LENGTH,
    ValidationFailed("idempotency key is empty") if it is blank, and
    ValidationFailed("idempotency key reused for a different request") if the stored fingerprint
    differs from fingerprint."""
    raise NotImplementedError("Lab s05: implement lookup")


def record(session: Session, key: str, fingerprint: str, status_code: int, body: dict) -> None:
    """Store the outcome for key and commit. Only successful outcomes (status 200 to 299) are
    stored; for any other status, do nothing, so a client can retry after fixing the problem."""
    raise NotImplementedError("Lab s05: implement record")
