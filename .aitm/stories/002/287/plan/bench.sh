#!/bin/zsh
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$1"
python="$2"
candidate="$3"
pinned='a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2'
scratch=$(mktemp -d "$HOME/Library/Caches/aitm-287-bench.XXXXXXXX")
mkdir "$scratch/parent" "$scratch/candidate"
git -C "$repo" archive "$pinned" | tar -x -C "$scratch/parent"
git -C "$repo" archive "$candidate" | tar -x -C "$scratch/candidate"
node=packages/aitm-usage/tests/test_monitor_journal.py::test_pair_settles_two_frontiers_and_preserves_first_ownership
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1
for i in {1..5}; do
  for version in parent candidate; do
    cd "$scratch/$version"
    export PYTHONPATH="$PWD/packages/aitm-usage/src:$PWD/tools/ci:$here"
    "$python" -m pytest -p measure_journal -p no:cacheprovider --basetemp "$scratch/$version-$i" -q -s "$node" >> "$scratch/$version-paired.log" 2>&1
  done
done
printf "%s\n" "$scratch"
