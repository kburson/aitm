#!/usr/bin/env bash
# Execute the original scheduled runner in a second exact, detached Git checkout.
set -euo pipefail
out=$1
root=$PWD
work=$(mktemp -d "$RUNNER_TEMP/aitm323-source.XXXXXXXX")
source_sha=$(python3 -c 'import json;print(json.load(open("scenario.json"))["production"]["sha"])')
source_tree=$(python3 -c 'import json;print(json.load(open("scenario.json"))["production"]["tree"])')
exec > >(tee "$out/full-run.log") 2>&1
set -x
test "$(uname -sm)" = "Darwin arm64"
git -C "$work" init --quiet
git -C "$work" fetch --no-tags --depth 1 https://github.com/kburson/aitm.git "$source_sha"
git -C "$work" checkout --quiet --detach FETCH_HEAD
test "$(git -C "$work" rev-parse HEAD)" = "$source_sha"
test "$(git -C "$work" rev-parse HEAD^{tree})" = "$source_tree"
test -z "$(git -C "$work" status --porcelain)"
cd "$work"
# These two normalized values satisfy the production source runner's explicit
# checkout/ref assertions. preflight.json records the actual GitHub producer.
env GITHUB_SHA="$source_sha" GITHUB_REF=refs/heads/trunk   bash -x tools/ci/run_scheduled_shadow.sh "$out/suite"
test -z "$(git status --porcelain)"
python3 - "$out/subject.json" "$source_sha" "$source_tree" "$root" <<'PY'
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

out, sha, tree, producer = sys.argv[1:]
paths = [
    "tools/ci/run_scheduled_shadow.sh", "tools/ci/ci_scheduled_shadow.py",
    "tools/ci/pytest_evidence.py", "tools/ci/python_gate.py", "tools/ci/policy.json",
    "packages/aitm-usage/pyproject.toml", "packages/aitm-usage/uv.lock",
]
doc = {
    "schema": "aitm.rehearsal-executed-subject/v1", "repository": "kburson/aitm",
    "sha": sha, "tree": tree, "finished_at": datetime.now(timezone.utc).isoformat(),
    "status": "clean", "controls": {
        path: hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in paths
    },
}
Path(out).write_text(json.dumps(doc, sort_keys=True, indent=2) + "\n")
PY
