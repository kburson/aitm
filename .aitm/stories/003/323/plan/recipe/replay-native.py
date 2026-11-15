"""Exercise old authorization replay on native GitHub after acknowledged lab release."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import evidence_io as io
from capture import RECORDS
from source.operator_recovery import need, signed
from verify_recovery import DENIALS, attempt_identity, rows


OUT = RECORDS / "native-replay"


def anchor():
    ack_file = RECORDS / "operator-acknowledgment/acknowledgment.json"
    ack = signed(ack_file.read_bytes(), ack_file.with_suffix(".json.sig").read_bytes(),
                 RECORDS / "operator.allowed_signers")
    receipt = io.read(ack_file.parent / "receipt.json")
    need(receipt["acknowledgment"] == ack
         and receipt["status"] == "disposable-hold-released-after-explicit-fresh-acknowledgment"
         and ack["repository"] == "kburson/aitm-missed-slot-323",
         "separate acknowledged disposable release required before replay")
    return ack, ack["repository"], ack["run_id"]


def start():
    ack, repo, run_id = anchor()
    OUT.mkdir()
    path = f"actions/runs/{run_id}"
    original = io.get(repo, path, OUT / "pre-rerun-latest.json")
    hold = io.get(repo, f"rulesets/{ack['hold_id']}", OUT / "pre-rerun-hold.json")
    need(original["run_attempt"] == 1 and original["conclusion"] == "success"
         and hold["enforcement"] == "disabled", "native replay precondition disagrees")
    request_start = datetime.now(timezone.utc).isoformat()
    response = io.gh("--include", io.route(repo, path + "/rerun"), method="POST")
    (OUT / "rerun-response.txt").write_bytes(response)
    io.write(OUT / "rerun-request.json", {"requested_at": request_start, "run_id": run_id, "action": "rerun"})
    io.get(repo, path, OUT / "post-rerun-first-read.json")


def finish():
    ack, repo, run_id = anchor()
    path = f"actions/runs/{run_id}"
    latest = io.get(repo, path, OUT / "post-rerun-latest.json")
    need(latest["run_attempt"] == 2 and latest["status"] == "completed" and latest["conclusion"] == "failure",
         "native replay has not completed red")
    attempt = io.get(repo, f"{path}/attempts/2", OUT / "second-attempt.json")
    first = io.get(repo, f"{path}/attempts/1", OUT / "first-attempt-historical.json")
    jobs = io.pages(repo, f"{path}/attempts/2/jobs?per_page=100", "jobs", OUT / "second-attempt-jobs.json")
    artifacts = io.pages(repo, f"{path}/artifacts?per_page=100", "artifacts", OUT / "artifacts-after-rerun.json")
    need(len(jobs) == 1 and first["conclusion"] == "success" and attempt["conclusion"] == "failure"
         and attempt["id"] == run_id and attempt["run_attempt"] == 2
         and jobs[0]["run_attempt"] == 2 and jobs[0]["run_id"] == run_id
         and jobs[0]["conclusion"] == "failure", "native rerun custody disagrees")
    steps = {step["name"]: step["conclusion"] for step in jobs[0]["steps"]}
    need(steps["Authenticate separate operator authorization"] == "failure"
         and steps["Execute unchanged full suite from pinned production source"] == "skipped"
         and all(art["name"] != "aitm-recovery-a2" for art in artifacts), "replay reached execution or published evidence")
    logs = OUT / "rerun-logs.zip"
    logs.write_bytes(io.raw(repo, f"{path}/attempts/2/logs"))
    with ZipFile(logs) as zip:
        need(any(b"wrong event or replayed attempt" in zip.read(name) for name in zip.namelist() if not name.endswith("/")),
             "native replay refusal missing from Actions logs")
    workflow = io.get(repo, f"actions/workflows/{latest['workflow_id']}", OUT / "workflow.json")
    authorization = io.read(RECORDS / "dispatch/authorization.json")
    denial = None
    try:
        attempt_identity({"workflow": workflow}, latest, run_id, authorization)
    except DENIALS as exc:
        denial = str(exc)
    need(denial == "replayed or different dispatch attempt", "native collector accepted superseding rerun")
    output = {"run_id": run_id, "attempt": 2, "native_conclusion": latest["conclusion"],
              "authorization_step": steps["Authenticate separate operator authorization"],
              "full_suite_step": steps["Execute unchanged full suite from pinned production source"],
              "collector_denial": denial, "timing": "after separate disposable hold acknowledgment"}
    io.write(OUT / "result.json", output)
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    {"start": start, "finish": finish}[sys.argv[1]]()
