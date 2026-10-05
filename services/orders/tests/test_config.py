"""Lab s07 (Lecture 7.3): credentials come from the environment only."""

import json

import httpx

from orderhub import notify
from orderhub.config import load_settings


def clear_orderhub_env(monkeypatch):
    import os
    for name in list(os.environ):
        if name.startswith("ORDERHUB_"):
            monkeypatch.delenv(name)


def test_no_credential_has_a_default(monkeypatch):
    clear_orderhub_env(monkeypatch)
    assert load_settings().warehouse_token is None


def test_token_is_read_from_the_environment(monkeypatch):
    clear_orderhub_env(monkeypatch)
    monkeypatch.setenv("ORDERHUB_WAREHOUSE_TOKEN", "value-from-the-secret-store")
    assert load_settings().warehouse_token == "value-from-the-secret-store"


def test_token_is_sent_as_a_bearer_header_and_never_in_the_body():
    seen = []

    def handler(request):
        seen.append((request.headers.get("authorization"), json.loads(request.content)))
        return httpx.Response(204)

    notify.order_cancelled("https://warehouse.example/hook", 1, [], transport=httpx.MockTransport(handler),
                           token="t0k3n-from-env")
    assert seen == [("Bearer t0k3n-from-env", {"event": "order.cancelled", "order_id": 1, "lines": []})]
