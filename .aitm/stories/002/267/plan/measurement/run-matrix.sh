#!/bin/zsh
set -eu
recipe=$(cd "$(dirname "$0")" && pwd -P)
private=$1
stage=${2:-all}
base=766504a02aaeb9dda339d588172dd7d5bdbd2b3f
python="$private/venv/bin/python"
source="$private/source"
tia_source="$private/tia-source"
logs="$private/logs"
profiles=(ci-helpers product-cli)
mkdir -p "$logs" "$private/history" "$private/observer" "$private/tmontmp"
[[ -L "$source/.tmontmp" ]] || ln -s "$private/tmontmp" "$source/.tmontmp"
[[ -d "$tia_source/.git" ]] || git clone --quiet --no-hardlinks --no-checkout "$source" "$tia_source"
git -C "$tia_source" checkout --quiet --detach "$base"
cp "$recipe/measure_testmon.py" "$recipe/measure_diagnostics.py" "$private/observer/"
"$python" - "$source/tools/ci/pytest_evidence.py" "$private/observer/pytest_evidence.py" <<'PY'
import sys
from pathlib import Path
source, destination = map(Path, sys.argv[1:])
source = source.read_text()
old = 'self.deselected.extend(item.nodeid for item in items)'
assert source.count(old) == 1
destination.write_text(source.replace(old, 'self.deselected.extend(getattr(item, "nodeid", None) for item in items)'))
PY
for name in $(env | cut -d= -f1 | rg '^(PYTEST_|PYTHON|UV_|GIT_|AITM_CI_|TESTMON_|TMNET_|COVERAGE_)|^(VIRTUAL_ENV|__PYVENV_LAUNCHER__)$' || true); do
  unset "$name"
done
run_profile() {
  "$recipe/run-profile.sh" "$private" "$logs/$1/$2/$3" "$2" "$3"
}
run_tia() {
  local seed=$1
  local mode=$2
  local reference=$3
  local output="$logs/$seed/tia-$mode"
  mkdir -p "$output"
  cd "$tia_source"
  local code=0
  /usr/bin/time -p "$python" -B -m tools.ci.tia.local --base "$reference" "--$mode" > "$output/report.json" 2> "$output/stderr.log" || code=$?
  print -r -- "$code" > "$output/exit"
}
if [[ "$stage" == all ]]; then
  "$python" "$recipe/seed.py" "$source" baseline > "$logs/baseline.status"
  for profile in "${profiles[@]}"; do run_profile baseline "$profile" serial; done
fi
for profile in "${profiles[@]}"; do
  if [[ "$stage" == all || "$stage" == resume-baseline ]]; then
    mkdir -p "$logs/train/$profile"
    run_profile train "$profile" train
    test -s "$logs/train/$profile/train/testmon.sqlite"
    cp "$logs/train/$profile/train/testmon.sqlite" "$private/history/$profile.sqlite"
  fi
done
for seed in cli non-code uncertain unavailable; do
  mkdir -p "$logs/$seed"
  "$python" "$recipe/seed.py" "$source" "$seed" > "$logs/$seed/source.status"
  "$python" "$recipe/seed.py" "$tia_source" "$seed" > "$logs/$seed/tia-source.status"
  git -C "$tia_source" diff --no-ext-diff --binary > "$logs/$seed/seed.patch"
  reference="$base"
  if [[ "$seed" == unavailable ]]; then reference=refs/heads/aitm-267-missing-base; fi
  run_tia "$seed" plan "$reference"
  plan_mode=$("$python" -c 'import json,sys; print(json.load(open(sys.argv[1]))["plan"]["mode"])' "$logs/$seed/tia-plan/report.json")
  if [[ "$plan_mode" == selected || "$plan_mode" == no-tests || "$seed" == cli || "$seed" == unavailable ]]; then
    run_tia "$seed" run "$reference"
  fi
  mode=warm
  if [[ "$seed" == unavailable ]]; then mode=cold; fi
  for profile in "${profiles[@]}"; do run_profile "$seed" "$profile" "$mode"; done
  if [[ "$seed" != unavailable ]]; then
    for profile in "${profiles[@]}"; do run_profile "$seed" "$profile" serial; done
  fi
  print -r -- "$seed completed"
done
if [[ "$(readlink "$source/.tmontmp")" == "$private/tmontmp" ]]; then
  unlink "$source/.tmontmp"
fi
"$python" "$recipe/seed.py" "$source" baseline > "$logs/restored.status"
"$python" "$recipe/seed.py" "$tia_source" baseline > "$logs/tia-restored.status"
