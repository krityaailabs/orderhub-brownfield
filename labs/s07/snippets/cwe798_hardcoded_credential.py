# Labelled example: CWE-798 (hard-coded credential). Scanner rules: ruff S105 and tools/secret_scan.py
# (assigned-secret, because the name contains "password" and the value has 16+ characters). Read-only example.
# Fix pattern: read it from the environment or a secret store; never from source.
REPORTS_DB_PASSWORD = "orderhub-reports"


def connection_string(host: str) -> str:
    return f"postgresql://reports:{REPORTS_DB_PASSWORD}@{host}/reports"
