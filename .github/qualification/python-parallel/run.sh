#!/usr/bin/env bash
set -euo pipefail
source_root=$1
mode=$2
workers=$3
out=$4
harness=$(cd "$(dirname "$0")" && pwd -P)
started=$(date +%s)
mkdir -p "$out/evidence" "$out/product"
fixtures=$(mktemp -d "$RUNNER_TEMP/aitm-qualification-fixtures.XXXXXXXX")
cd "$source_root"
test "$(git rev-parse HEAD)" = "$QUALIFICATION_SOURCE"
test "$(git rev-parse 'HEAD^{tree}')" = "$QUALIFICATION_TREE"
test "$(uname -s)" = Darwin
device=$(df -P "$RUNNER_TEMP" | awk 'NR==2 {print $1}')
test "$(diskutil info -plist "$device" | plutil -extract FilesystemType raw -)" = apfs

export PYTHONPATH="$source_root/tools/ci:$harness"
export AITM_CI_XDIST_DIR="$out/product"
export AITM_CI_CHILD_EVIDENCE=1 COVERAGE_FILE="$out/product/.product"
cd packages/aitm-usage
uv sync --locked --python "$PYTHON_VERSION"
python="$PWD/.venv/bin/python"
uv pip install --python "$python" --no-deps pytest-xdist==3.8.0 execnet==2.1.2
uv pip check --python "$python"
ready=$(date +%s)
case "$mode" in
  full) tests=(tests) ;;
  selected)
    tests=(
      tests/test_accounting.py
      tests/test_export.py
      tests/test_grok_pricing.py
      tests/test_service.py::test_one_shot_status_uses_collecting_subprocess_pid
    )
    ;;
  *) exit 2 ;;
esac
printf '%s\n' "${tests[@]}" > "$out/evidence/scope.txt"
"$python" -m coverage run -m pytest -p worker_receipts -p pytest_evidence \
  -n "$workers" --dist worksteal --rootdir "$source_root" -q -p no:cacheprovider \
  --basetemp "$fixtures/pytest" --junitxml "$out/evidence/product-junit.xml" \
  --durations=15 "${tests[@]}" "$source_root/tools/ci/tests/test_cli_evidence.py"
"$python" "$harness/reconcile.py" "$out/product" "$workers" "$source_root/tools/ci/policy.json"
cp "$out/product/reconciled.json" "$out/evidence/pytest.json"
cp "$out/product/children.json" "$out/evidence/children.json"
"$python" -m coverage combine --keep
"$python" -m coverage json -o "$out/evidence/product-coverage.json"
product_done=$(date +%s)

cd "$source_root"
unset AITM_CI_CHILD_EVIDENCE AITM_CI_PYTEST_EVIDENCE
gh_asset=gh_2.97.0_macOS_arm64.zip
curl --fail --silent --show-error --location --retry 3 \
  "https://github.com/cli/cli/releases/download/v2.97.0/$gh_asset" -o "$out/$gh_asset"
(cd "$out" && printf '%s\n' a58b8fd77b417a38f47a0b54d1370c59b0fcdb324ccc9ca002b0998f7c4c999e "$gh_asset" | shasum -a 256 -c -)
unzip -q "$out/$gh_asset" -d "$out"
export PATH="$out/gh_2.97.0_macOS_arm64/bin:$PATH"
printf '%s\n' '[run]' 'branch = True' 'relative_files = True' 'source = tools/ci' \
  'omit = tools/ci/tests/*' 'patch = subprocess' > "$out/helper.coveragerc"
COVERAGE_FILE="$out/.helpers" "$python" -m pytest -q \
  --junitxml "$out/evidence/helpers-junit.xml" --cov=tools/ci \
  --cov-config="$out/helper.coveragerc" --cov-report=json:"$out/evidence/helper-coverage.json" \
  tools/ci/tests/test_python_gate.py tools/ci/tests/test_pytest_evidence.py \
  tools/ci/tests/test_verify_pr.py tools/ci/tests/test_file_checks.py
helpers_done=$(date +%s)

cd packages/aitm-usage
uv build --wheel --no-sources --out-dir "$out/wheel"
wheels=("$out"/wheel/*.whl)
test "${#wheels[@]}" -eq 1
wheel="${wheels[0]}"
shasum -a 256 "$wheel" > "$out/wheel.sha256"
uv export --locked --no-dev --no-emit-project --format requirements.txt > "$out/runtime.txt"
uv venv --python "$PYTHON_VERSION" "$out/install"
uv pip sync --python "$out/install/bin/python" "$out/runtime.txt"
shasum -a 256 -c "$out/wheel.sha256"
uv pip install --python "$out/install/bin/python" --no-deps "$wheel"
"$out/install/bin/python" -I -c 'from pathlib import Path; import sys, aitm_usage; assert Path(aitm_usage.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())'
"$out/install/bin/aitm-usage" --help > "$out/help"
grep -q 'usage: aitm-usage' "$out/help"
jq -n --arg digest "$(cut -d' ' -f1 "$out/wheel.sha256")" '{digest:$digest}' > "$out/evidence/wheel.json"
end=$(date +%s)
jq -n --arg source "$QUALIFICATION_SOURCE" --arg tree "$QUALIFICATION_TREE" \
  --arg mode "$mode" --arg image "${ImageVersion:-local}" \
  --argjson workers "$workers" --argjson cpu "$("$python" -c 'import os; print(os.process_cpu_count() or 1)')" \
  --argjson setup "$((ready - started))" --argjson product "$((product_done - ready))" \
  --argjson helpers "$((helpers_done - product_done))" --argjson wheel "$((end - helpers_done))" \
  --argjson total "$((end - started))" \
  '{source:$source,tree:$tree,mode:$mode,image:$image,workers:$workers,available_cpus:$cpu,
    setup_seconds:$setup,product_seconds:$product,helper_seconds:$helpers,wheel_seconds:$wheel,
    script_seconds:$total}' > "$out/evidence/timings.json"
cat "$out/evidence/timings.json"
