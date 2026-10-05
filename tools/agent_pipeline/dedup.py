"""Deduplication for agent pull requests (Lecture 9.6)."""


def is_duplicate(issue: str, diff_hash: str, prs: list[dict]) -> str | None:
    """Return the id of an existing PR that makes this run a duplicate, or None.

    prs: PR records, each with "id", "issue", "diff_hash" and "status".
    A run is a duplicate if any PR that is still open (status "awaiting-human" or "approved"):
      - is for the same issue, or
      - has exactly the same diff_hash (the same change, whatever issue triggered it).
    Closed or rejected PRs ("rejected", "merged", "superseded") never make a run a duplicate.
    Return the first matching PR's id, in the order given."""
    raise NotImplementedError("Lab s09: implement is_duplicate")
