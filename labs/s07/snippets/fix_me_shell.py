# Labelled example for Lab s07: CWE-78 (OS command injection). Scanner rules: ruff S602, S605.
# Not used by OrderHub. Fix it so the scanner is clean and tests/test_snippets pass.
import subprocess


def archive_handoff(folder: str, name: str, dest: str) -> None:
    """Create a gzipped tar archive at dest containing folder/name (stored as `name`)."""
    subprocess.run(f"tar -czf {dest} -C {folder} {name}", shell=True, check=True)
