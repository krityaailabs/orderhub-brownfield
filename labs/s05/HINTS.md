# Lab s05 hints

## Q12 (5.5)
1. Reproduce first: cancel the same order twice and check stock.
2. What does `cancel_order` do when the order is already CANCELLED?
3. Return the order unchanged when it's already CANCELLED, before touching stock.

## request_fingerprint
1. `json.dumps(body or {}, sort_keys=True, separators=(",", ":"))`.
2. Combine the upper-cased method, the path and the canonical body; hash with `hashlib.sha256(...).hexdigest()`.

## lookup and record
1. Check the key (blank, too long) before reading the database.
2. `session.get(IdempotencyRecord, key)`; compare fingerprints; return `(status_code, json.loads(response_json))`.
3. `record` stores only 2xx outcomes, then commits.

## select_checks
1. Build a set of check names from the rules in the docstring, then return `[name for name in ORDER if name in wanted]`.
2. A path is under a tests directory if `"/tests/"` or `"/test/"` appears in `"/" + path`.
