"""Runtime settings, read from environment variables.

Copy .env.example to .env for local overrides. Never put secrets in this file.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    currency: str
    billing_handoff_dir: str
    warehouse_webhook_url: str | None = None


def load_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("ORDERHUB_DATABASE_URL", "sqlite:///./orderhub.db"),
        currency=os.environ.get("ORDERHUB_CURRENCY", "USD"),
        billing_handoff_dir=os.environ.get("ORDERHUB_BILLING_HANDOFF_DIR", "./handoff"),
        warehouse_webhook_url=os.environ.get("ORDERHUB_WAREHOUSE_WEBHOOK_URL") or None,
    )
