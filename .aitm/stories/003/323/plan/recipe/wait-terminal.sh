#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
run_id=$(jq -r .workflow_run_id records/dispatch/dispatch-response.json)
end=$((SECONDS + 2400))
while ((SECONDS < end)); do
  gh api "repos/kburson/aitm-missed-slot-323/actions/runs/$run_id" > records/current-poll.json
  jq -c '{run_attempt,status,conclusion,updated_at}' records/current-poll.json
  if jq -e '.status=="completed"' records/current-poll.json > /dev/null; then
    python3 capture.py green --logs
    python3 verify_recovery.py verify green
    exit 0
  fi
  sleep 20
done
exit 2
