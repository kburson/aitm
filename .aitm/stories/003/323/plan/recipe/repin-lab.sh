#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
prod_source=$1
lab=kburson/aitm-missed-slot-323
record=$PWD/records
mkdir "$record/abandoned-setup" "$record/repin"
cp "$record"/lab-before-* "$record/lab-sha" "$record/scenario.json" "$record/lab-setup-completed-at" "$record/abandoned-setup/"
hold_id=$(jq -r '.id' "$record/lab-hold-response.json")
normal_id=$(jq -r '.id' "$record/lab-normal-response.json")
jq '.enforcement="disabled"' "$record/lab-hold-request.json" > "$record/repin/hold-disable-request.json"
gh api --method PUT "repos/$lab/rulesets/$hold_id" --input "$record/repin/hold-disable-request.json" > "$record/repin/hold-disable.json"
gh api "repos/$lab/rulesets/$normal_id" > "$record/repin/normal-during-repin.json"
jq -e '.enforcement=="active"' "$record/repin/normal-during-repin.json"
gh api "repos/$lab/actions/runs" > "$record/repin/actions-before-repin.json"
jq -e '.total_count==0' "$record/repin/actions-before-repin.json"
git -C lab switch -c repin-before-rehearsal
tree=$(git -C subject rev-parse "$prod_source^{tree}")
python3 - "$prod_source" "$tree" <<'PY'
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys

path = Path("lab/scenario.json")
doc = json.loads(path.read_bytes())
now = datetime.now(timezone.utc)
slot = now.replace(second=0, microsecond=0) + timedelta(minutes=2)
doc.update(declared_at=now.isoformat(), slot=slot.isoformat(), deadline=(slot+timedelta(minutes=2)).isoformat())
doc["production"].update(sha=sys.argv[1], tree=sys.argv[2])
path.write_text(json.dumps(doc, sort_keys=True, indent=2) + "\n")
PY
git -C lab add scenario.json
git -C lab commit -m 'Repin #323 before dispatch after production trunk advance'
git -C lab push origin repin-before-rehearsal
gh api --method POST "repos/$lab/pulls" -f title='Repin rehearsal before activation'   -f head='repin-before-rehearsal' -f base=trunk   -f body='Retain first setup. Pin refreshed protected production source and predeclare a fresh rehearsal window.'   > "$record/repin/pr.json"
pr=$(jq -r '.number' "$record/repin/pr.json")
head=$(git -C lab rev-parse HEAD)
gh api --method PUT "repos/$lab/pulls/$pr/merge" -f merge_method=merge -f sha="$head" > "$record/repin/merge.json"
jq -e '.merged == true' "$record/repin/merge.json"
gh api --method PUT "repos/$lab/rulesets/$hold_id" --input "$record/lab-hold-request.json" > "$record/repin/hold-reactivated.json"
git -C lab fetch origin trunk
git -C lab switch --detach origin/trunk
git -C lab rev-parse HEAD > "$record/lab-sha"
cp lab/scenario.json "$record/scenario.json"
gh api "repos/$lab/branches/trunk" > "$record/lab-before-branch.json"
gh api "repos/$lab/rules/branches/trunk" > "$record/lab-before-rules.json"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$record/lab-setup-completed-at"
jq -e 'any(.[]; .type=="update") and any(.[]; .type=="pull_request")' "$record/lab-before-rules.json"
cat "$record/scenario.json"
