#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")"
root="$PWD"
repo="$1"
python="$2"
sha=a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2
mkdir -p audit-source
git -C "$repo" archive "$sha" | tar -x -C audit-source
cd audit-source
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$PWD/packages/aitm-usage/src:$PWD/tools/ci"
"$python" -m pytest -c packages/aitm-usage/pyproject.toml --rootdir "$PWD" -p no:cacheprovider --collect-only -q packages/aitm-usage/tests tools/ci/tests/test_cli_evidence.py > "$root/product-collection.log" 2>&1
"$python" -m pytest -c packages/aitm-usage/pyproject.toml --rootdir "$PWD" -p no:cacheprovider --collect-only -q tools/ci/tests/{test_python_gate.py,test_pytest_evidence.py,test_verify_pr.py,test_file_checks.py} > "$root/helper-collection.log" 2>&1
"$python" -m pytest -c packages/aitm-usage/pyproject.toml --rootdir "$PWD" -p no:cacheprovider --collect-only -q tools/ci/tests > "$root/all-helper-collection.log" 2>&1
