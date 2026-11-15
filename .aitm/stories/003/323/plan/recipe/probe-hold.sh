#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
repo=kburson/aitm-missed-slot-323
mkdir records/held-merge-probe
evidence=$PWD/records/held-merge-probe
commit=$(cat records/lab-sha)
gh api "repos/$repo/branches/trunk" > "$evidence/branch-before.json"
gh api "repos/$repo/rules/branches/trunk" > "$evidence/rules-before.json"
jq -e 'any(.[]; .type=="update")' "$evidence/rules-before.json"
git -C lab switch --detach "$commit"
git -C lab switch -c hold-probe-323
printf '%s\n' 'This isolated change should be refused while the disposable merge hold is active.' > lab/HOLD-PROBE.md
git -C lab add HOLD-PROBE.md
git -C lab commit -m 'Probe #323 held default branch'
git -C lab push origin hold-probe-323
gh api --method POST "repos/$repo/pulls" -f title='Disposable #323 hold probe'   -f head='hold-probe-323' -f base=trunk -f body='Exercise refusal while the separate update hold is active.'   > "$evidence/probe-pr.json"
head=$(git -C lab rev-parse HEAD)
pr=$(jq -r '.number' "$evidence/probe-pr.json")
set +e
gh api --method PUT "repos/$repo/pulls/$pr/merge" -f merge_method=merge -f sha="$head"   > "$evidence/refused-merge.json" 2> "$evidence/refused-merge.stderr"
status=$?
set -e
test "$status" -ne 0
cat "$evidence/refused-merge.json" "$evidence/refused-merge.stderr"
gh api "repos/$repo/pulls/$pr" > "$evidence/probe-pr-after.json"
gh api "repos/$repo/branches/trunk" > "$evidence/branch-after.json"
gh api "repos/$repo/rules/branches/trunk" > "$evidence/rules-after.json"
jq -e --arg sha "$commit" '.protected == true and .commit.sha == $sha' "$evidence/branch-after.json"
jq -e '.merged == false and .state == "open"' "$evidence/probe-pr-after.json"
jq -e 'any(.[]; .type=="update")' "$evidence/rules-after.json"
git -C lab switch --detach "$commit"
