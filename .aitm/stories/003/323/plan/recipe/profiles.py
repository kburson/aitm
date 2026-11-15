"""Reconcile production pytest output independently of the hosted job conclusion."""

from datetime import timedelta
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import evidence_io as io
from source.operator_recovery import instant, need, validate_admission, WORKFLOW

ROOT = Path(__file__).resolve().parent
SUBJECT = ROOT / "subject"
RECORDS = ROOT / "records"
sys.path.insert(0, str(SUBJECT / "tools/ci"))
from ci_scheduled_shadow import profile
from verify_pr import decode_json

SOURCE_FILES = (
    "tools/ci/run_scheduled_shadow.sh", "tools/ci/ci_scheduled_shadow.py",
    "tools/ci/pytest_evidence.py", "tools/ci/python_gate.py", "tools/ci/policy.json",
    "packages/aitm-usage/pyproject.toml", "packages/aitm-usage/uv.lock",
)
STEP = "Execute unchanged full suite from pinned production source"
AUTH_STEP = "Authenticate separate operator authorization"

TOLERANCE = timedelta(seconds=3)


def digest(buf):
    return sha256(buf).hexdigest()


def subset(mapping, fields):
    return {field: mapping[field] for field in fields}


def full_evidence(members, run, scenario, steps, auth, auth_raw, sig_raw):
    producer = auth["producer"]
    preflight = decode_json(members["preflight.json"])
    subject = decode_json(members["subject.json"])
    src = scenario["production"]
    head_and_tree = subprocess.check_output(
        ["git", "-C", str(SUBJECT), "rev-parse", "HEAD", "HEAD^{tree}"], text=True
    ).splitlines()
    need(head_and_tree == [src["sha"], src["tree"]]
         and subprocess.check_output(["git", "-C", str(SUBJECT), "status", "--porcelain"]) == b"",
         "independent verifier source checkout disagrees")
    expected_producer = {
        "repository": producer["repository"], "repository_id": producer["repository_id"],
        "ref": producer["ref"], "sha": producer["sha"], "event": run["event"],
        "workflow_ref": f"{producer['repository']}/{WORKFLOW}@{producer['ref']}",
        "workflow_sha": producer["sha"], "run_id": run["id"], "attempt": 1,
        "actor": auth["operator"]["login"], "actor_id": auth["operator"]["id"],
        "triggering_actor": auth["operator"]["login"],
    }
    need(preflight["schema"] == "aitm.rehearsal-operator-preflight/v1"
         and preflight["producer"] == expected_producer and preflight["production"] == src
         and preflight["authorization_sha256"] == digest(auth_raw)
         and preflight["admission_id"] == auth["id"]
         and members["authorization.json"] == auth_raw and members["authorization.sig"] == sig_raw,
         "runner producer or signed authorization disagrees")
    authorized = instant(preflight["authorized_at"])
    validate_admission(auth, scenario, expected_producer, authorized)
    need(instant(steps[AUTH_STEP]["started_at"]) <= authorized
         <= instant(steps[AUTH_STEP]["completed_at"]) + TOLERANCE, "runner authorization timing disagrees")
    need(subject["schema"] == "aitm.rehearsal-executed-subject/v1"
         and subset(subject, ("repository", "sha", "tree")) == subset(src, ("repository", "sha", "tree"))
         and subject["status"] == "clean"
         and subject["controls"] == {path: digest((SUBJECT / path).read_bytes()) for path in SOURCE_FILES}
         and instant(steps[STEP]["started_at"]) <= instant(subject["finished_at"])
         <= instant(steps[STEP]["completed_at"]) + TOLERANCE, "executed production source or timing disagrees")
    doc = decode_json(members["suite/receipt.json"])
    need(doc["schema"] == "aitm.ci-scheduled-shadow/v1" and doc["binding"] == {
         "repository_id": producer["repository_id"], "event": "workflow_dispatch",
         "sha": src["sha"], "run_id": run["id"], "attempt": 1, "ref": "refs/heads/trunk",
    } and set(doc["profiles"]) == {"product", "helpers"}, "production runner evidence binding disagrees")
    policy = io.read(SUBJECT / "tools/ci/policy.json")
    summary, seen, children = {}, {}, []
    for label, root in (("product", "packages/aitm-usage/tests/"), ("helpers", "tools/ci/tests/")):
        pair = doc["profiles"][label]
        need(set(pair) == {"collection", "execution"}
             and all(decode_json(members[f"suite/{label}-{phase}.json"]) == pair[phase]
                     for phase in pair), "raw and combined pytest outcomes disagree")
        reference = io.read(RECORDS / f"reference-{label}.json")
        coll, execution = pair["collection"], pair["execution"]
        need(reference == coll and reference["children"] == [], "independent ordered collection disagrees")
        outcomes = profile(coll, execution, policy["optional_skips"])
        need(set(outcomes) == set(coll["collected"])
             and all(node.startswith(root) and node not in seen for node in outcomes),
             "full inventory missing, overlapping or outside profile")
        seen.update(outcomes)
        children.extend(execution["children"])
        summary[label] = {
            "collected": len(outcomes), "passed": list(outcomes.values()).count("passed"),
            "skipped": [node for node, outcome in outcomes.items() if outcome == "skipped"],
            "phase_reports": len(execution["reports"]),
            "ordered_inventory_sha256": digest(json.dumps(coll["collected"], separators=(",", ":")).encode()),
        }
    need(all(seen.get(name) == "passed" for name in policy["required_tests"]),
         "required production test missing or failed")
    need(sorted(c["label"] for c in children) == sorted(policy["required_children"])
         and len({c["pid"] for c in children}) == len(children)
         and all(type(c["returncode"]) is int and c["returncode"] == 0
                 and type(c["pid"]) is int and c["pid"] > 0 for c in children),
         "required native subprocess evidence missing or failed")
    return summary, children, subject, preflight
