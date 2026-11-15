#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
repo=kburson/aitm-missed-slot-323
records=$PWD/records
mkdir "$records/green-held-merge-probe"
out="$records/green-held-merge-probe"
approved="$records/green/result.json"
initial="$records/held-merge-probe/probe-pr-after.json"
pr=$(jq -r '.number' "$initial")
held=$(jq -r '.producer.sha' "$approved")
run_id=$(jq -r '.run.id' "$approved")
hand=$(jq -r '.head.sha' "$initial")
hold_id=$(jq -r '.id' "$records/lab-hold-response.json")
suite_api="repos/$repo/rulesets/rule-suites?per_page=50"
gh api "$suite_api" > "$out/suites-before.json"
gh api "repos/$repo/actions/runs/$run_id" > "$out/green-before-probe.json"
jq -e '.run_attempt == 1 and .conclusion == "success"' "$out/green-before-probe.json"
set +e
gh api --method PUT "repos/$repo/pulls/$pr/merge" -f merge_method=merge -f sha="$hand"   > "$out/refused-merge.json" 2> "$out/refused-merge.stderr"
status=$?
set -e
test "$status" -ne 0
jq -e '.status == "405" and (.message | contains("Cannot update this protected ref"))' "$out/refused-merge.json"
gh api "repos/$repo/branches/trunk" > "$out/branch-after.json"
gh api "repos/$repo/rules/branches/trunk" > "$out/rules-after.json"
jq -e --arg sha "$held" '.protected == true and .commit.sha == $sha' "$out/branch-after.json"
jq -e --argjson hold "$hold_id" 'any(.[]; .type=="update" and .ruleset_id==$hold)' "$out/rules-after.json"
gh api "repos/$repo/pulls/$pr" > "$out/probe-pr-after.json"
jq -e '.merged == false and .state == "open"' "$out/probe-pr-after.json"
for attempt in 1 2 3 4 5 6 7 8; do
  gh api "$suite_api" > "$out/suites-after.json"
  suite=$(jq --arg sha "$held" --slurpfile previous "$out/suites-before.json" -r '
    [.[] | select(.ref=="refs/heads/trunk" and .result=="fail" and .before_sha==$sha)
      | .id as $id | select(all($previous[0][]; .id!=$id))] | first.id // empty
  ' "$out/suites-after.json")
  if [[ -n "$suite" ]]; then break; fi
  sleep 1
done
test -n "$suite"
gh api "repos/$repo/rulesets/rule-suites/$suite" > "$out/rule-suite.json"
jq '.rule_evaluations[] | {rule_type,result,rule_source}' "$out/rule-suite.json"
