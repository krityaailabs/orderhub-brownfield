"""Unit tests for orderhub/idempotency.py (Lab s05)."""

import pytest

from orderhub import idempotency
from orderhub.errors import ValidationFailed


def test_fingerprint_ignores_key_order_and_whitespace():
    a = idempotency.request_fingerprint("post", "/orders/1/cancel", {"a": 1, "b": [1, 2]})
    b = idempotency.request_fingerprint("POST", "/orders/1/cancel", {"b": [1, 2], "a": 1})
    assert a == b and len(a) == 64


def test_fingerprint_differs_by_path_method_and_body():
    base = idempotency.request_fingerprint("POST", "/orders/1/cancel", None)
    assert base == idempotency.request_fingerprint("POST", "/orders/1/cancel", {})
    assert base != idempotency.request_fingerprint("POST", "/orders/2/cancel", None)
    assert base != idempotency.request_fingerprint("PUT", "/orders/1/cancel", None)
    assert base != idempotency.request_fingerprint("POST", "/orders/1/cancel", {"x": 1})


def test_lookup_of_new_key_is_none_then_returns_the_recorded_outcome(session):
    fp = idempotency.request_fingerprint("POST", "/x", None)
    assert idempotency.lookup(session, "k1", fp) is None
    idempotency.record(session, "k1", fp, 200, {"ok": True})
    assert idempotency.lookup(session, "k1", fp) == (200, {"ok": True})


def test_failed_outcomes_are_not_recorded(session):
    fp = idempotency.request_fingerprint("POST", "/x", None)
    idempotency.record(session, "k2", fp, 409, {"error": "no"})
    assert idempotency.lookup(session, "k2", fp) is None


def test_reused_key_with_different_fingerprint_is_rejected(session):
    idempotency.record(session, "k3", idempotency.request_fingerprint("POST", "/a", None), 200, {})
    with pytest.raises(ValidationFailed, match="reused for a different request"):
        idempotency.lookup(session, "k3", idempotency.request_fingerprint("POST", "/b", None))


@pytest.mark.parametrize("key,message", [("   ", "empty"), ("k" * 129, "too long")])
def test_bad_keys_are_rejected(session, key, message):
    with pytest.raises(ValidationFailed, match=message):
        idempotency.lookup(session, key, "f")
