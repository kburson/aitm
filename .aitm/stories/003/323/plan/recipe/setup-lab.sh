#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
lab=kburson/aitm-missed-slot-323
prod=e9b92172aee21eaab728e1a313d94f0bea38279b
record=$PWD/records
private=$PWD/private
mkdir -m 700 "$private"
ssh-keygen -q -t ed25519 -f "$private/operator" -N '' -C 'ephemeral rehearsal authority #323'
git init --initial-branch trunk lab
mkdir -p lab/.github/workflows
cp source/operator-recovery.yml lab/.github/workflows/operator-recovery.yml
cp source/operator_recovery.py source/run-recovery.sh lab/
chmod +x lab/run-recovery.sh
printf 'rehearsal-operator %s\n' "$(cut -d' ' -f1,2 "$private/operator.pub")" > lab/operator.allowed_signers
tree=$(git -C ../planning rev-parse "$prod^{tree}")
python3 - "$record/lab-repository-created.json" "$prod" "$tree" > lab/scenario.json <<'PY'
import json
import sys
from datetime import datetime, timedelta, timezone

repo = json.load(open(sys.argv[1]))
now = datetime.now(timezone.utc)
slot = now.replace(second=0, microsecond=0) + timedelta(minutes=2)
deadline = slot + timedelta(minutes=2)
doc = {
    "schema": "aitm.rehearsal-scenario/v1",
    "lab": {"repository": repo["full_name"], "id": repo["id"], "ref": "refs/heads/trunk"},
    "production": {
        "repository": "kburson/aitm", "id": 1450406435, "ref": "refs/heads/trunk",
        "sha": sys.argv[2], "tree": sys.argv[3],
    },
    "mode": "predeclared deliberately unconfigured rehearsal schedule",
    "declared_at": now.isoformat(), "slot": slot.isoformat(), "deadline": deadline.isoformat(),
}
print(json.dumps(doc, indent=2, sort_keys=True))
PY
git -C lab add .
git -C lab commit -m 'Configure disposable #323 recovery control and intentional schedule gap'
git -C lab remote add origin "git@github.com:$lab.git"
git -C lab push --set-upstream origin trunk
git -C lab rev-parse HEAD > "$record/lab-sha"
cp lab/scenario.json lab/operator.allowed_signers "$record/"
gh api "repos/$lab" > "$record/lab-repository.json"
jq -e '.default_branch == "trunk"' "$record/lab-repository.json"
cp ../delivery-293-v2/lab-rules-request.json "$record/lab-normal-template.json"
jq '.name = "Disposable #323 normal target protection" | .conditions.ref_name.include = ["refs/heads/trunk"]' "$record/lab-normal-template.json" > "$record/lab-normal-request.json"
gh api --method POST "repos/$lab/rulesets" --input "$record/lab-normal-request.json" > "$record/lab-normal-response.json"
cat > "$record/lab-hold-request.json" <<'JSON'
{
  "name": "Disposable #323 missed-slot hold",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [],
  "conditions": {"ref_name": {"include": ["refs/heads/trunk"], "exclude": []}},
  "rules": [{"type": "update", "parameters": {"update_allows_fetch_and_merge": false}}]
}
JSON
gh api --method POST "repos/$lab/rulesets" --input "$record/lab-hold-request.json" > "$record/lab-hold-response.json"
gh api "repos/$lab/branches/trunk" > "$record/lab-before-branch.json"
gh api "repos/$lab/rules/branches/trunk" > "$record/lab-before-rules.json"
gh api "repos/$lab/actions/workflows/operator-recovery.yml" > "$record/lab-workflow.json"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$record/lab-setup-completed-at"
cat "$record/scenario.json"
jq -e 'any(.[]; .type=="update") and any(.[]; .type=="pull_request")' "$record/lab-before-rules.json"
jq '{id,path,state}' "$record/lab-workflow.json"
