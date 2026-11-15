"""Authenticate the bounded #323 lab proof from fresh or retained GitHub facts."""

from base64 import b64decode
from datetime import datetime, timezone
from hashlib import sha1
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import BadZipFile, ZipFile

import evidence_io as io
from capture import ROOT, RECORDS, CONTROL_FILES, MAX_ARCHIVE, capture
from profiles import STEP, AUTH_STEP, TOLERANCE, digest, subset, full_evidence
from source.operator_recovery import instant, need, signed, WORKFLOW
from verify_pr import Hold

RUN_KEYS = ("id", "run_number", "run_attempt", "workflow_id", "check_suite_id",
            "display_title", "path", "event", "head_branch", "head_sha", "created_at",
            "run_started_at", "status", "conclusion")
DENIALS = (ValueError, Hold, KeyError, TypeError, OSError, BadZipFile)


def rows(document, field):
    output = [row for page in document for row in page[field]]
    need(document and all(page["total_count"] == len(output) for page in document),
         "truncated native metadata")
    return output


def proved_miss(dispatch, scenario, auth):
    miss_path = dispatch / "miss.json"
    miss = io.read(miss_path)
    slot_list = dispatch / "pre-dispatch-scheduled-runs.json"
    anchor = dispatch / "pre-dispatch-branch.json"
    need(auth["miss_record_sha256"] == digest(miss_path.read_bytes()) and miss["status"] == "missed"
         and miss["scope"] == "disposable-only" and miss["repository"] == scenario["lab"]
         and miss["slot"] == auth["slot"] == scenario["slot"]
         and miss["deadline"] == auth["deadline"] == scenario["deadline"]
         and miss["sha"] == auth["producer"]["sha"]
         and miss["server_run_list_sha256"] == digest(slot_list.read_bytes())
         and miss["server_branch_sha256"] == digest(anchor.read_bytes())
         and rows(io.read(slot_list), "workflow_runs") == [] and miss["scheduled_run_ids"] == []
         and instant(scenario["declared_at"]) < instant(miss["slot"]) < instant(miss["deadline"])
         <= instant(miss["captured_at"]) <= instant(auth["issued_at"]), "missed-slot authorization disagrees")
    for path in ("protected-production-at-issuance.json", "protected-production-pre-dispatch.json"):
        prod = io.read(dispatch / path)
        need(prod["name"] == "trunk" and prod["protected"] is True
             and prod["commit"]["sha"] == scenario["production"]["sha"],
             "production source was not current at admission and dispatch")


def held_target(docs, scenario, auth):
    bind = auth["producer"]
    repo = docs["repository"]
    need(repo["id"] == scenario["lab"]["id"] == bind["repository_id"]
         and repo["full_name"] == bind["repository"] == scenario["lab"]["repository"]
         and repo["default_branch"] == "trunk", "foreign protected default target")
    hold_id = io.read(RECORDS / "lab-hold-response.json")["id"]
    normal_id = io.read(RECORDS / "lab-normal-response.json")["id"]
    for phase in ("before", "after"):
        branch = docs[f"branch-{phase}"]
        need(branch["name"] == "trunk" and branch["protected"] is True
             and branch["commit"]["sha"] == bind["sha"], "stale or moved protected default target")
        rules = docs[f"rules-{phase}"]
        hold = docs[f"hold-{phase}"]
        need({r["type"] for r in rules if r["ruleset_id"] == normal_id}
             == {"deletion", "non_fast_forward", "pull_request"}, "normal target protection missing")
        need(hold["id"] == hold_id and hold["enforcement"] == "active"
             and hold["bypass_actors"] == []
             and hold["conditions"]["ref_name"] == {"include": ["refs/heads/trunk"], "exclude": []}
             and any(r["type"] == "update" and r["ruleset_id"] == hold_id for r in rules),
             "explicit hold is missing or bypassable")


def attempt_identity(docs, run, identifier, auth):
    producer = auth["producer"]
    workflow = docs["workflow"]
    need(workflow["state"] == "active" and workflow["path"] == WORKFLOW
         and workflow["id"] == io.read(RECORDS / "lab-workflow.json")["id"],
         "wrong or unavailable protected producer workflow")
    need(run["event"] == "workflow_dispatch", "wrong recovery event")
    need(run["id"] == identifier and run["run_attempt"] == 1, "replayed or different dispatch attempt")
    need(run["workflow_id"] == workflow["id"] and run["path"] == WORKFLOW
         and run["head_branch"] == "trunk" and run["head_sha"] == producer["sha"]
         and run["repository"]["id"] == run["head_repository"]["id"] == producer["repository_id"]
         and run["repository"]["full_name"] == run["head_repository"]["full_name"] == producer["repository"]
         and subset(run["actor"], ("id", "login")) == auth["operator"]
         and subset(run["triggering_actor"], ("id", "login")) == auth["operator"]
         and run["display_title"] == "recovery/" + auth["id"],
         "producer, dispatch authorization or actor identity disagrees")
    for phase in ("before", "after"):
        listing = rows(docs[f"workflow-runs-{phase}"], "workflow_runs")
        current = max(listing, key=lambda row: row["run_number"], default=None)
        related = [row for row in listing if row["display_title"] == run["display_title"]]
        need(current and len(related) == 1 and current["id"] == run["id"]
             and current["run_attempt"] == run["run_attempt"], "dispatch superseded or replayed")
        need(subset(current, RUN_KEYS) == subset(run, RUN_KEYS)
             and subset(docs[f"run-{phase}"], RUN_KEYS) == subset(run, RUN_KEYS),
             "run changed during verification")


def require_green(docs, run):
    need(run["status"] == "completed", "pending recovery")
    need(run["conclusion"] == "success", "red or unsuccessful recovery")
    attempt = docs["attempt"]
    suite = docs["suite"]
    jobs = rows(docs["jobs"], "jobs")
    need(subset(attempt, RUN_KEYS) == subset(run, RUN_KEYS)
         and suite["id"] == run["check_suite_id"] and suite["head_sha"] == run["head_sha"]
         and suite["head_branch"] == "trunk" and suite["app"]["slug"] == "github-actions"
         and suite["app"]["id"] == 15368
         and suite["status"] == "completed" and suite["conclusion"] == "success"
         and len(jobs) == 1, "exact GitHub Actions attempt or suite evidence disagrees")
    [job] = jobs
    check = docs[f"check-{job['id']}"]
    fields = ("name", "status", "conclusion", "started_at", "completed_at")
    need(job["name"] == "recovery" and job["head_branch"] == "trunk"
         and job["head_sha"] == run["head_sha"] and job["run_id"] == run["id"]
         and job["run_attempt"] == run["run_attempt"] and job["status"] == "completed"
         and job["conclusion"] == "success" and "macos-26" in job["labels"]
         and job["runner_group_name"] == "GitHub Actions"
         and check["id"] == job["id"] and check["app"] == suite["app"]
         and check["check_suite"]["id"] == suite["id"]
         and subset(check, fields) == subset(job, fields),
         "attempt job and native GitHub check disagree")
    steps = {row["name"]: row for row in job["steps"] if row["name"] in {AUTH_STEP, STEP}}
    need(set(steps) == {AUTH_STEP, STEP}
         and all(s["status"] == "completed" and s["conclusion"] == "success" for s in steps.values()),
         "authorization or exact source execution step did not pass")
    return job, steps


def artifact(docs, raw, run, job):
    items = rows(docs["artifacts"], "artifacts")
    matches = [a for a in items if a["name"] == "aitm-recovery-a1"]
    need(len(matches) == 1 and raw is not None, "missing or duplicate recovery archive")
    [item] = matches
    need(type(item["id"]) is int and item["id"] > 0 and item["expired"] is False
         and item["workflow_run"] == {
             "id": run["id"], "repository_id": run["repository"]["id"],
             "head_repository_id": run["head_repository"]["id"],
             "head_branch": run["head_branch"], "head_sha": run["head_sha"],
         }
         and instant(job["started_at"]) <= instant(item["created_at"]) <= instant(job["completed_at"])
         and item["size_in_bytes"] == len(raw) and 0 < len(raw) <= MAX_ARCHIVE
         and item["digest"] == "sha256:" + digest(raw), "foreign or invalid recovery archive custody")
    expected = {"preflight.json", "authorization.json", "authorization.sig", "subject.json", "full-run.log",
                "suite/receipt.json"} | {
                    f"suite/{label}-{part}.json"
                    for label in ("product", "helpers") for part in ("collection", "execution")
                }
    with ZipFile(BytesIO(raw)) as archive:
        members = archive.infolist()
        files = [row for row in members if not row.is_dir()]
        directories = [row.orig_filename for row in members if row.is_dir()]
        need({row.orig_filename for row in files} == expected and len(files) == len(expected)
             and set(directories) <= {"suite/"}
             and all(0 < row.file_size <= 16 * 1024 * 1024 for row in files)
             and archive.testzip() is None, "invalid recovery archive members")
        return item, {row.orig_filename: archive.read(row) for row in files}


def verify_controls(evidence, git_doc, tree_doc, producer):
    need(git_doc["sha"] == producer["sha"]
         and tree_doc["sha"] == git_doc["tree"]["sha"] and tree_doc["truncated"] is False,
         "foreign protected producer commit or incomplete tree")
    entries = {row["path"]: row for row in tree_doc["tree"]}
    controls = {}
    for path in CONTROL_FILES:
        name = Path(path).name
        raw = (evidence / "controls" / name).read_bytes()
        remote = io.read(evidence / "controls" / (name + ".provider.json"))
        expected = {
            WORKFLOW: ROOT / "source/operator-recovery.yml",
            "operator_recovery.py": ROOT / "source/operator_recovery.py",
            "run-recovery.sh": ROOT / "source/run-recovery.sh",
            "scenario.json": RECORDS / "scenario.json",
            "operator.allowed_signers": RECORDS / "operator.allowed_signers",
        }[path]
        need(b64decode(remote["content"]) == raw == expected.read_bytes()
             and remote["path"] == path and entries[path]["type"] == "blob"
             and entries[path]["mode"] in {"100644", "100755"}
             and sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == remote["sha"] == entries[path]["sha"],
             "protected producer controller or local recipe differs")
        controls[path] = {"blob": remote["sha"], "sha256": digest(raw)}
    return controls


def load_docs(evidence):
    return {path.stem: io.read(path) for path in evidence.glob("*.json") if path.name != "result.json"}


def verify(evidence, *, docs=None, archive_raw=..., now=None):
    docs = docs if docs is not None else load_docs(evidence)
    dispatch = RECORDS / "dispatch"
    scenario = io.read(RECORDS / "scenario.json")
    auth_raw = (dispatch / "authorization.json").read_bytes()
    sig_raw = (dispatch / "authorization.json.sig").read_bytes()
    auth = signed(auth_raw, sig_raw, RECORDS / "operator.allowed_signers")
    proved_miss(dispatch, scenario, auth)
    held_target(docs, scenario, auth)
    dispatch_response = io.read(dispatch / "dispatch-response.json")
    identifier = dispatch_response["workflow_run_id"]
    request = io.read(dispatch / "dispatch-request.json")
    producer = auth["producer"]
    need(request["ref"] == "trunk" and request["inputs"]["admission_id"] == auth["id"]
         and b64decode(request["inputs"]["authorization"], validate=True) == auth_raw
         and b64decode(request["inputs"]["signature"], validate=True) == sig_raw
         and dispatch_response["html_url"] == f"https://github.com/{producer['repository']}/actions/runs/{identifier}"
         and dispatch_response["run_url"] == f"https://api.github.com/repos/{producer['repository']}/actions/runs/{identifier}",
         "retained signed admission differs from dispatch")
    run = docs["run-before"]
    attempt_identity(docs, run, identifier, auth)
    now = now or datetime.now(timezone.utc)
    interval = io.read(dispatch / "dispatch-interval.json")
    issued = instant(auth["issued_at"])
    requested = instant(interval["requested_at"])
    returned = instant(interval["returned_at"])
    created = instant(run["created_at"])
    need(issued <= requested <= returned <= now <= instant(auth["expires_at"])
         and requested - TOLERANCE <= created <= returned + TOLERANCE,
         "run outside the signed dispatch interval or authorization expired")
    job, steps = require_green(docs, run)
    started, job_started, job_completed = map(
        instant, (run["run_started_at"], job["started_at"], job["completed_at"])
    )
    need(created <= started <= job_started <= job_completed <= now, "run or job timing disagrees")
    if archive_raw is ...:
        path = evidence / "artifact.zip"
        archive_raw = path.read_bytes() if path.is_file() else None
    item, members = artifact(docs, archive_raw, run, job)
    summary, children, subject, preflight = full_evidence(
        members, run, scenario, steps, auth, auth_raw, sig_raw
    )
    git_doc = docs["lab-git-commit"]
    return {
        "status": "eligible-current-full-recovery", "repository": producer["repository"],
        "producer": producer, "producer_tree": git_doc["tree"]["sha"],
        "controls": verify_controls(evidence, git_doc, docs["lab-git-tree"], producer),
        "production": scenario["production"], "run": subset(run, RUN_KEYS),
        "actor": auth["operator"], "authorization_id": auth["id"],
        "authorization_sha256": digest(auth_raw), "miss_sha256": auth["miss_record_sha256"],
        "rehearsal_slot": auth["slot"], "rehearsal_deadline": auth["deadline"],
        "artifact": subset(item, ("id", "name", "digest", "size_in_bytes", "created_at")),
        "job_id": job["id"], "job_started_at": job["started_at"], "job_completed_at": job["completed_at"],
        "queue_to_job_seconds": (job_started - created).total_seconds(),
        "job_elapsed_seconds": (job_completed - job_started).total_seconds(),
        "full_execution_step": steps[STEP], "reference_profiles": summary, "child_witnesses": children,
        "preflight": preflight, "subject": subject, "hold_at_verification": "active", "verified_at": now.isoformat(),
    }


if __name__ == "__main__":
    evidence = RECORDS / sys.argv[2]
    try:
        if sys.argv[1] == "capture":
            capture(evidence, include_logs="--logs" in sys.argv)
        result = verify(evidence)
    except DENIALS as exc:
        print(f"HOLD: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
    io.write(evidence / "result.json", result)
    print(json.dumps(result, sort_keys=True, indent=2))
