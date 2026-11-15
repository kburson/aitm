#!/usr/bin/env bash
# Run both full profiles with fresh fixtures in an advisory-only workflow.
set -euo pipefail

: "${GITHUB_SHA:?}" "${GITHUB_REF:?}" "${GITHUB_EVENT_NAME:?}" "${RUNNER_TEMP:?}"
test "$GITHUB_REF" = refs/heads/trunk
case "$GITHUB_EVENT_NAME" in
  schedule|workflow_dispatch) ;;
  *) exit 2 ;;
esac
test "$(git rev-parse HEAD)" = "$GITHUB_SHA"
test "$(uname -s)" = Darwin
device=$(df -P "$RUNNER_TEMP" | awk 'NR==2 {print $1}')
test "$(diskutil info -plist "$device" | plutil -extract FilesystemType raw -)" = apfs

root=$(pwd -P)
out=$1
mkdir "$out"
fixtures=$(mktemp -d "$RUNNER_TEMP/aitm-shadow-fixtures.XXXXXXXX")
export PYTHONPATH="$root/tools/ci"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export AITM_CI_CHILD_EVIDENCE=1
uv sync --project packages/aitm-usage --locked --python 3.13.9
python="$root/packages/aitm-usage/.venv/bin/python"
args=(-c packages/aitm-usage/pyproject.toml --rootdir "$root" -p no:cacheprovider -p pytest_evidence)

status=0
run_profile() {
  local name=$1
  local targets=$2
  AITM_CI_PYTEST_EVIDENCE="$out/$name-collection.json"     "$python" -m pytest "${args[@]}" --collect-only -q "$targets" || status=1
  AITM_CI_PYTEST_EVIDENCE="$out/$name-execution.json"     "$python" -m pytest "${args[@]}" --basetemp "$fixtures/$name" --durations=15 -q "$targets" || status=1
}
run_profile product packages/aitm-usage/tests
run_profile helpers tools/ci/tests
test "$status" = 0
"$python" tools/ci/ci_scheduled_shadow.py --emit "$out"
git diff --quiet --exit-code HEAD
