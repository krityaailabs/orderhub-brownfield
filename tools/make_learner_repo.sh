#!/usr/bin/env bash
# Build the public learner repository from this (private) instructor repository.
# Each course tag is exported with `git archive`, which honours export-ignore, so
# instructor/ never enters the learner history. Usage: tools/make_learner_repo.sh <out-dir>
set -euo pipefail
OUT=${1:?usage: tools/make_learner_repo.sh <out-dir>}
SRC=$(cd "$(dirname "$0")/.." && pwd)
rm -rf "$OUT" && mkdir -p "$OUT" && git -C "$OUT" init -q -b main
for tag in $(git -C "$SRC" tag --list 's[0-9][0-9]*' --sort=creatordate); do
  find "$OUT" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  git -C "$SRC" archive "$tag" | tar -x -C "$OUT"
  git -C "$OUT" add -A
  git -C "$OUT" -c user.name="Kritya AI Labs" -c user.email="course@kritya.example" \
      commit -q -m "Course tag $tag" --allow-empty
  git -C "$OUT" tag "$tag"
done
if [ -e "$OUT/instructor" ]; then echo "ERROR: instructor/ leaked into learner repo" >&2; exit 1; fi
echo "learner repo at $OUT with tags: $(git -C "$OUT" tag | tr '\n' ' ')"
