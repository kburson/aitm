#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
out="$PWD/records"
cd subject
set -x
test "$(git rev-parse HEAD)" = 9de9dbbec4053b95cfab5e005cd876c667f71e10
test -z "$(git status --porcelain)"
uv --version
uv sync --project packages/aitm-usage --locked --python 3.13.9
PY="$PWD/packages/aitm-usage/.venv/bin/python"
"$PY" --version
export PYTHONPATH="$PWD/tools/ci" PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 AITM_CI_CHILD_EVIDENCE=1
args=(-c packages/aitm-usage/pyproject.toml --rootdir "$PWD" -p no:cacheprovider -p pytest_evidence --collect-only -q)
AITM_CI_PYTEST_EVIDENCE="$out/reference-product.json" "$PY" -m pytest "${args[@]}" packages/aitm-usage/tests
AITM_CI_PYTEST_EVIDENCE="$out/reference-helpers.json" "$PY" -m pytest "${args[@]}" tools/ci/tests
test -z "$(git status --porcelain)"
