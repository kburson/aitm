#!/bin/zsh
set -eu
private=$1
output=$2
profile=$3
mode=$4
mkdir -p "$output"
output=$(cd "$output" && pwd -P)
cd "$private/source"
case "$profile" in
  ci-helpers) targets=(tools/ci/tests/test_file_checks.py tools/ci/tests/test_pytest_evidence.py tools/ci/tests/test_python_gate.py tools/ci/tests/test_verify_pr.py) ;;
  product-cli) targets=(packages/aitm-usage/tests/ tools/ci/tests/test_cli_evidence.py) ;;
  *) exit 3 ;;
esac
plugins=()
receipt_plugin="$private/observer"
database="$output/testmon.sqlite"
case "$mode" in
  serial) ;;
  train) plugins=(-p testmon.pytest_testmon -p measure_testmon --testmon --testmon-noselect); receipt_plugin="$private/observer" ;;
  warm) plugins=(-p testmon.pytest_testmon -p measure_testmon --testmon --testmon-nocollect); receipt_plugin="$private/observer"; cp "$private/history/$profile.sqlite" "$database" ;;
  cold) plugins=(-p testmon.pytest_testmon -p measure_testmon --testmon); receipt_plugin="$private/observer"; test ! -e "$database" ;;
  *) exit 3 ;;
esac
for name in $(env | cut -d= -f1 | rg '^(PYTEST_|PYTHON|UV_|GIT_|AITM_CI_|TESTMON_|TMNET_)|^(VIRTUAL_ENV|__PYVENV_LAUNCHER__|COVERAGE_PROCESS_START)$' || true); do
  unset "$name"
done
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 AITM_CI_CHILD_EVIDENCE=1
export PYTHONPATH="$receipt_plugin:$PWD/tools/ci:$PWD/packages/aitm-usage/src"
export AITM_CI_PYTEST_EVIDENCE="$output/pytest-evidence.json"
export TESTMON_DATAFILE="$database"
export MEASURE_TESTMON_RECEIPT="$output/testmon-evidence.json"
export MEASURE_DIAGNOSTICS_RECEIPT="$output/diagnostics.jsonl"
export TMPDIR="$private/tmp"
mkdir -p "$TMPDIR"
set +e
/usr/bin/time -p "$private/venv/bin/python" -P -m pytest -ra --tb=long -p pytest_evidence -p measure_diagnostics -p no:cacheprovider -c packages/aitm-usage/pyproject.toml -o addopts= --rootdir "$PWD" --confcutdir "$PWD" --basetemp "$output/fixtures" "${plugins[@]}" -- "${targets[@]}" > "$output/stdout.log" 2> "$output/stderr.log"
code=$?
set -e
print -r -- "$code" > "$output/exit"
