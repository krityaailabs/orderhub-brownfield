# Labelled example: CWE-328 (weak hash for passwords). Scanner rule: ruff S324.
# Read-only example for Lecture 7.6. Fix pattern: a password-hashing function (hashlib.scrypt or a
# reviewed library), with a per-user salt.
import hashlib


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()
