# Labelled example for Lab s07: CWE-78 (OS command injection). Scanner rules: ruff S602, S605.
# Fixed: no shell and no command string. The standard library writes the archive, so file names are
# always data. (An argument list with subprocess.run also avoids the shell; tarfile avoids the process.)
import tarfile
from pathlib import Path


def archive_handoff(folder: str, name: str, dest: str) -> None:
    """Create a gzipped tar archive at dest containing folder/name (stored as `name`)."""
    with tarfile.open(dest, "w:gz") as archive:
        archive.add(Path(folder) / name, arcname=name)
