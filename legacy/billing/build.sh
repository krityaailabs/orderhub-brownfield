#!/usr/bin/env bash
# Legacy build: compiles for Java 8 with plain javac and runs the self-test.
# (No Maven here yet. Moving this module to a modern build is part of Section 8.)
set -euo pipefail
cd "$(dirname "$0")"
rm -rf build && mkdir -p build/classes
javac -nowarn -Xlint:-options --release 8 -encoding UTF-8 -d build/classes \
  $(find src test -name '*.java')
java -cp build/classes com.orderhub.billing.BillingSelfTest
