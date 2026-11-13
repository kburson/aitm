#!/bin/zsh
set -eu
private=$1
node='packages/aitm-usage/tests/test_monitor_journal.py::test_pair_preserves_frontiers_when_one_native_completion_is_invalid[repeated-counter-rival]'
for name in $(env | cut -d= -f1 | rg '^(PYTEST_|PYTHON|UV_|GIT_|AITM_CI_|TESTMON_|TMNET_|COVERAGE_)|^(VIRTUAL_ENV|__PYVENV_LAUNCHER__)$' || true); do
  unset "$name"
done
cd "$private/source"
[[ -z "$(git diff --name-only HEAD)" ]]
for iteration in 1 2 3; do
  output="$private/logs/baseline/recheck-$iteration"
  mkdir -p "$output"
  code=0
  PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="$private/observer:$PWD/tools/ci:$PWD/packages/aitm-usage/src" \
    AITM_CI_CHILD_EVIDENCE=1 AITM_CI_PYTEST_EVIDENCE="$output/pytest-evidence.json" \
    MEASURE_DIAGNOSTICS_RECEIPT="$output/diagnostics.jsonl" TMPDIR="$private/tmp" \
    /usr/bin/time -p "$private/venv/bin/python" -P -m pytest -ra --tb=long \
    -p pytest_evidence -p measure_diagnostics -p no:cacheprovider \
    -c packages/aitm-usage/pyproject.toml -o addopts= --rootdir "$PWD" \
    --confcutdir "$PWD" --basetemp "$output/fixtures" -- "$node" \
    > "$output/stdout.log" 2> "$output/stderr.log" || code=$?
  print -r -- "$code" > "$output/exit"
done
