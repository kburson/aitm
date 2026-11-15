"""Explicitly acknowledge still-current lab evidence and release only the lab hold."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

import evidence_io as io
from capture import ROOT, RECORDS, capture
from dispatch import canonical
from profiles import digest
from source.operator_recovery import NAMESPACE, instant, need, signed
from verify_recovery import DENIALS, RUN_KEYS, rows, subset, verify


ACTION = "acknowledge-and-release-disposable-hold"


def read_anchor(repo, name, target, run, workflow):
    branch = io.get(repo, "branches/trunk", target / f"branch-{name}.json")
    head = io.get(repo, f"actions/runs/{run['id']}", target / f"run-{name}.json")
    listing_path = target / f"workflow-runs-{name}.json"
    candidates = io.pages(repo, f"actions/workflows/{workflow}/runs?branch=trunk&per_page=100",
                          "workflow_runs", listing_path)
    need(branch["protected"] is True and branch["name"] == "trunk"
         and branch["commit"]["sha"] == run["head_sha"]
         and subset(head, RUN_KEYS) == run
         and len(candidates) == 1 and subset(candidates[0], RUN_KEYS) == run,
         "acknowledgment evidence superseded or target moved")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", required=True, choices=[ACTION])
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--artifact-digest", required=True)
    args = parser.parse_args()
    positive = io.read(RECORDS / "green/result.json")
    need(args.run_id == positive["run"]["id"] and args.artifact_digest == positive["artifact"]["digest"],
         "explicit acknowledgment does not name the verified proof")
    out = RECORDS / "operator-acknowledgment"
    out.mkdir()
    evidence = out / "fresh-evidence"
    capture(evidence)
    checked = verify(evidence)
    io.write(evidence / "result.json", checked)
    need({k:v for k,v in checked.items() if k != "verified_at"}
         == {k:v for k,v in positive.items() if k != "verified_at"},
         "fresh current recovery no longer matches the nominated proof")
    repo = checked["repository"]
    need(repo == "kburson/aitm-missed-slot-323", "release is only defined for the disposable target")
    actor = json.loads(io.gh("user"))
    need(subset(actor, ("id", "login")) == checked["actor"], "operator credential disagrees")
    production_branch = io.get("kburson/aitm", "branches/trunk", out / "production-read-at-acknowledgment.json")
    need(production_branch["name"] == "trunk" and production_branch["protected"] is True,
         "production scope could not be recorded read-only")
    hold = io.read(evidence / "hold-after.json")
    out_request = out / "acknowledgment.json"
    doc = {
        "schema": "aitm.rehearsal-operator-acknowledgment/v1",
        "issue": 323, "action": args.action, "operator": checked["actor"],
        "repository": repo, "producer": checked["producer"], "hold_id": hold["id"],
        "run_id": checked["run"]["id"], "attempt": checked["run"]["run_attempt"],
        "artifact_id": checked["artifact"]["id"], "artifact_digest": checked["artifact"]["digest"],
        "authorization_id": checked["authorization_id"],
        "production_sha_at_acknowledgment": production_branch["commit"]["sha"],
        "miss_sha256": checked["miss_sha256"],
        "fresh_verification_sha256": digest((evidence / "result.json").read_bytes()),
        "acknowledged_at": datetime.now(timezone.utc).isoformat(),
    }
    out_request.write_bytes(canonical(doc))
    subprocess.run(["ssh-keygen", "-Y", "sign", "-f", str(ROOT / "private/operator"), "-n", NAMESPACE,
                    str(out_request)], check=True)
    sig = out_request.with_suffix(".json.sig").read_bytes()
    need(signed(out_request.read_bytes(), sig, RECORDS / "operator.allowed_signers") == doc,
         "operator acknowledgment signature disagrees")
    read_anchor(repo, "at-release", out, checked["run"], checked["run"]["workflow_id"])
    release = {k: hold[k] for k in ("name", "target", "conditions", "bypass_actors", "rules")}
    release["enforcement"] = "disabled"
    release_path = out / "hold-release-request.json"
    io.write(release_path, release)
    release_result = io.gh(io.route(repo, f"rulesets/{hold['id']}"), method="PUT", body=release_path)
    (out / "hold-release-response.json").write_bytes(release_result)
    released = json.loads(release_result)
    need(released["id"] == hold["id"] and released["enforcement"] == "disabled", "hold release is unconfirmed")
    normal_id = io.read(RECORDS / "lab-normal-response.json")["id"]
    normal = io.get(repo, f"rulesets/{normal_id}", out / "normal-after-release.json")
    rules_after = io.get(repo, "rules/branches/trunk", out / "rules-after-release.json")
    read_anchor(repo, "after-release", out, checked["run"], checked["run"]["workflow_id"])
    need(normal["enforcement"] == "active" and normal["bypass_actors"] == []
         and {r["type"] for r in rules_after if r["ruleset_id"] == normal_id}
         == {"deletion", "non_fast_forward", "pull_request"}
         and not any(r["ruleset_id"] == hold["id"] for r in rules_after),
         "ordinary protection or final hold state disagrees")
    receipt = {
        "status": "disposable-hold-released-after-explicit-fresh-acknowledgment",
        "acknowledgment_sha256": digest(out_request.read_bytes()),
        "acknowledgment_signature_sha256": digest(sig),
        "native_hold_release_sha256": digest(release_result),
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "acknowledgment": doc,
    }
    io.write(out / "receipt.json", receipt)
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    try:
        main()
    except DENIALS + (subprocess.CalledProcessError,) as exc:
        raise SystemExit(f"HOLD or unconfirmed release: {exc}") from None
