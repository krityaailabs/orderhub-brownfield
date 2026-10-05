"""Deduplication for agent pull requests (Lecture 9.6)."""


def is_duplicate(issue: str, diff_hash: str, prs: list[dict]) -> str | None:
    """Return the id of an existing PR that makes this run a duplicate, or None.

    prs: PR records, each with "id", "issue", "diff_hash" and "status".
    A run is a duplicate if any PR that is still open (status "awaiting-human" or "approved"):
      - is for the same issue, or
      - has exactly the same diff_hash (the same change, whatever issue triggered it).
    Closed or rejected PRs ("rejected", "merged", "superseded") never make a run a duplicate.
    Return the first matching PR's id, in the order given."""
    for pr in prs:
        if pr["status"] not in ("awaiting-human", "approved"):
            continue
        if pr["issue"] == issue or (diff_hash and pr["diff_hash"] == diff_hash):
            return pr["id"]
    return None
