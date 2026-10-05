# Labelled example: CWE-502 (deserialisation of untrusted data). Scanner rule: ruff S301.
# Read-only example for Lecture 7.6. Fix pattern: use a data format (JSON) and validate it.
import pickle


def load_cart(blob: bytes) -> dict:
    return pickle.loads(blob)
