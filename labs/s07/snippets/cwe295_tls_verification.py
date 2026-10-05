# Labelled example: CWE-295 (improper certificate validation). Scanner rule: ruff S501.
# Read-only example for Lecture 7.6. Fix pattern: keep verification on; trust a private CA with
# verify="/path/to/ca.pem" rather than turning checks off.
import httpx


def fetch_rates(url: str) -> dict:
    return httpx.get(url, verify=False, timeout=5).json()
