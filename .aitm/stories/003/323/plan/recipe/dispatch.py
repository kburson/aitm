"""Establish the disposable missed slot, sign one explicit admission and dispatch."""

from base64 import b64encode
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
from secrets import token_hex
import subprocess

import evidence_io as io
from source.operator_recovery import instant, NAMESPACE, need


ROOT = Path(__file__).resolve().parent
RECORDS = ROOT / "records"


def utcnow():
    return datetime.now(timezone.utc)


def canonical(document):
    return (json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n").encode()


def payload_data(scenario, miss_raw, actor, sha, when):
    return {
        "schema": "aitm.rehearsal-operator-authorization/v1", "issue": 323,
        "id": token_hex(16), "operator": actor, "slot": scenario["slot"], "deadline": scenario["deadline"],
        "miss_record_sha256": sha256(miss_raw).hexdigest(),
        "producer": {"repository": scenario["lab"]["repository"], "repository_id": scenario["lab"]["id"],
                     "ref": scenario["lab"]["ref"], "sha": sha,
                     "workflow": ".github/workflows/operator-recovery.yml"},
        "production": scenario["production"], "action": "recover-full-suite-after-missed-slot",
        "issued_at": when.isoformat(), "expires_at": (when + timedelta(minutes=70)).isoformat(),
    }


def main():
    scenario = io.read(RECORDS / "scenario.json")
    repo = scenario["lab"]["repository"]
    sha = (RECORDS / "lab-sha").read_text().strip()
    when = utcnow()
    need(instant(scenario["declared_at"])
         <= instant((RECORDS / "lab-setup-completed-at").read_text().strip()) < instant(scenario["deadline"])
         <= when, "lab missing-slot deadline has not elapsed or was not predeclared")
    output = RECORDS / "dispatch"
    output.mkdir()
    branch = io.get(repo, "branches/trunk", output / "pre-dispatch-branch.json")
    rules = io.get(repo, "rules/branches/trunk", output / "pre-dispatch-rules.json")
    need(branch["name"] == "trunk" and branch["protected"] and branch["commit"]["sha"] == sha
         and any(rule["type"] == "update" for rule in rules), "lab target or hold is stale")
    lab_workflow = io.read(RECORDS / "lab-workflow.json")
    workflow = lab_workflow["id"]
    rows = io.pages(repo, f"actions/runs?branch=trunk&event=schedule&per_page=100",
                    "workflow_runs", output / "pre-dispatch-scheduled-runs.json")
    all_runs = io.pages(repo, f"actions/workflows/{workflow}/runs?per_page=100",
                        "workflow_runs", output / "pre-dispatch-workflow-runs.json")
    need(rows == [] and all_runs == [], "rehearsal requires an observed empty scheduled window and recovery history")
    production = io.get("kburson/aitm", "branches/trunk", output / "protected-production-at-issuance.json")
    need(production["protected"] and production["name"] == "trunk"
         and production["commit"]["sha"] == scenario["production"]["sha"],
         "production advanced before lab admission; repin before issuing")
    miss = {
        "schema": "aitm.rehearsal-missed-slot/v1", "status": "missed", "scope": "disposable-only",
        "captured_at": utcnow().isoformat(), "slot": scenario["slot"], "deadline": scenario["deadline"],
        "repository": scenario["lab"], "sha": sha, "scheduled_run_ids": [],
        "server_branch_sha256": sha256((output / "pre-dispatch-branch.json").read_bytes()).hexdigest(),
        "server_run_list_sha256": sha256((output / "pre-dispatch-scheduled-runs.json").read_bytes()).hexdigest(),
    }
    io.write(output / "miss.json", miss)
    actor = json.loads(io.gh("user"))
    identity = {"id": actor["id"], "login": actor["login"]}
    need(identity == {"id": 1082467, "login": "kburson"}, "simulated operator actor disagrees")
    authorization = payload_data(scenario, (output / "miss.json").read_bytes(), identity, sha, utcnow())
    auth_path = output / "authorization.json"
    auth_path.write_bytes(canonical(authorization))
    subprocess.run(["ssh-keygen", "-Y", "sign", "-f", str(ROOT / "private/operator"),
                    "-n", NAMESPACE, str(auth_path)], check=True)
    request = {"ref": "trunk", "inputs": {
        "admission_id": authorization["id"],
        "authorization": b64encode(auth_path.read_bytes()).decode(),
        "signature": b64encode(auth_path.with_suffix(".json.sig").read_bytes()).decode(),
    }}
    request_path = output / "dispatch-request.json"
    io.write(request_path, request)
    production = io.get("kburson/aitm", "branches/trunk", output / "protected-production-pre-dispatch.json")
    need(production["protected"] and production["commit"]["sha"] == scenario["production"]["sha"],
         "production advanced before dispatch; repin before dispatch")
    before = utcnow()
    response_file = output / "dispatch-response.json"
    response_file.write_bytes(io.gh("-H", "X-GitHub-Api-Version: 2026-03-10",
                                    io.route(repo, f"actions/workflows/{workflow}/dispatches"),
                                    method="POST", body=request_path))
    after = utcnow()
    response = io.read(response_file)
    identifier = response["workflow_run_id"]
    need(type(identifier) is int and identifier > 0, "native dispatch receipt omitted its run ID")
    io.write(output / "dispatch-interval.json", {"requested_at": before.isoformat(), "returned_at": after.isoformat()})
    initial = io.get(repo, f"actions/runs/{identifier}", output / "initial-run.json")
    need(initial["head_sha"] == sha and initial["event"] == "workflow_dispatch"
         and initial["actor"]["id"] == identity["id"] and initial["run_attempt"] == 1,
         "native dispatch returned a foreign run")
    print(json.dumps({"response": response, "status": initial["status"]}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
