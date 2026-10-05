#!/usr/bin/env bash
# Headless agent job (Lecture 9.1): fix lint errors, then prove it. Exits non-zero if lint still fails.
# Inputs: the repository at HEAD. Output: a working-tree change (or none). Exit criteria: `make lint` passes.
# Requires Claude Code and ANTHROPIC_API_KEY; without them, it falls back to ruff's own fixer so the
# job's shape (inputs, bounded run, verification, exit code) can be seen offline.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=${PY:-.venv/bin/python}
if command -v claude >/dev/null 2>&1 && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  timeout 600 claude --bare -p "Fix every error reported by 'make lint'. Change only what the errors require. Do not edit tests. Then run 'make lint' and report the result." \
    --max-turns 15 --output-format json \
    --allowedTools "Read,Edit,Bash(make lint),Bash(git diff *)" > out-headless.json
  echo "agent exit: $?  cost: $($PY -c 'import json;print(json.load(open("out-headless.json")).get("total_cost_usd"))' 2>/dev/null)"
else
  echo "claude not available: using ruff --fix as the stand-in agent"
  $PY -m ruff check --fix --quiet services/orders tools || true
fi
# The job's exit criterion is checked by the job, not taken from the agent's word.
make lint PY="$PY"
