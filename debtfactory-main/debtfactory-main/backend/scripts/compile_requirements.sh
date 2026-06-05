#!/usr/bin/env bash
# Compile all requirements fragments into pinned lockfiles with pip-compile.
#
# Each team edits only its own .in fragment; this script recompiles every
# fragment so day-to-day changes stay conflict-free. Run after editing any
# requirements/*.in or requirements/services/*.in file.
set -euo pipefail

cd "$(dirname "$0")/.."

PIP_COMPILE="${PIP_COMPILE:-pip-compile}"
COMPILE_ARGS="--resolver=backtracking --strip-extras --quiet"

echo ">> Compiling base + dev"
"$PIP_COMPILE" $COMPILE_ARGS requirements/base.in -o requirements/base.txt
"$PIP_COMPILE" $COMPILE_ARGS requirements/dev.in -o requirements/dev.txt

echo ">> Compiling per-service fragments"
for fragment in requirements/services/*.in; do
  [ -e "$fragment" ] || continue
  out="${fragment%.in}.txt"
  echo "   - $fragment -> $out"
  "$PIP_COMPILE" $COMPILE_ARGS "$fragment" -o "$out"
done

echo ">> Done. Review the diff and commit the updated .txt lockfiles."
