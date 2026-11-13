#!/bin/zsh
set -eu
recipe=$(cd "$(dirname "$0")" && pwd -P)
repo=$1
base=766504a02aaeb9dda339d588172dd7d5bdbd2b3f
wheel="$recipe/pytest_testmon-2.3.0-py3-none-any.whl"
wheel_url=https://files.pythonhosted.org/packages/1b/f1/0312fca79f6695ce17426e8d30df0c4c2f6efa297094ea6fd81fe7a257b4/pytest_testmon-2.3.0-py3-none-any.whl
[[ "$(uv --version | cut -d' ' -f2)" == 0.10.6 ]]
if [[ ! -f "$wheel" ]]; then curl --fail --location --output "$wheel" "$wheel_url" >&2; fi
[[ "$(shasum -a 256 "$wheel" | cut -d' ' -f1)" == fd541506efa483e5a217e6cc5c07c73b382619c218d1ed4ffa80584c34defd77 ]]
private=$(mktemp -d "$HOME/Library/Caches/aitm-267.XXXXXXXX")
for name in $(env | cut -d= -f1 | rg '^(PYTEST_|PYTHON|UV_|GIT_|AITM_CI_|TESTMON_|TMNET_|COVERAGE_)|^(VIRTUAL_ENV|__PYVENV_LAUNCHER__)$' || true); do
  unset "$name"
done
git clone --quiet --no-hardlinks --no-checkout "$repo" "$private/source"
git -C "$private/source" checkout --quiet --detach "$base"
[[ "$(shasum -a 256 "$private/source/packages/aitm-usage/uv.lock" | cut -d' ' -f1)" == 949aa576be20d2b4f2516313fde8426304b0aeda3874751927243f8ff979ae73 ]]
UV_PROJECT_ENVIRONMENT="$private/venv" uv sync --locked --no-config --python 3.13.9 --project "$private/source/packages/aitm-usage" >&2
uv pip install --python "$private/venv/bin/python" --no-deps "$wheel" >&2
print -r -- "$private"
