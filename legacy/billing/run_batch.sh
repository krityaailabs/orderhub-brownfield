#!/usr/bin/env bash
# Run the nightly batch: ./run_batch.sh <handoff-dir> <out-dir> <yyyy-MM-dd>
set -euo pipefail
cd "$(dirname "$0")"
[ -d build/classes ] || ./build.sh >/dev/null
java -cp build/classes com.orderhub.billing.NightlyBatch "$@"
