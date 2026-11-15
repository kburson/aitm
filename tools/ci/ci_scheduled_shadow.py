"""Read and replay a default-trunk scheduled full-suite shadow observation."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from ci_advisory import (
    EVIDENCE_ERRORS,
    FAILURES,
    REPO,
    TARGET,
    authenticate_job,
)
from ci_advisory import (
    REPOSITORY_ID as REPO_ID,
)
from ci_advisory import (
    WORKFLOW_ID as PUSH_WORKFLOW_ID,
)
from python_gate import _outcomes
from verify_pr import (
    GitHub,
    Hold,
    blob,
    commit,
    decode_json,
    digest,
    positive,
    regular_blob,
    require,
    successful,
    timestamp,
    tree_entries,
)

WORKFLOW = ".github/workflows/scheduled-full-shadow.yml"
JOB = "full-suite-shadow"
PROFILES = ("product", "helpers")
SCHEMA = "aitm.ci-scheduled-shadow/v1"
CONTROLS = (
    WORKFLOW,
    "tools/ci/run_scheduled_shadow.sh",
    "tools/ci/ci_scheduled_shadow.py",
    "tools/ci/pytest_evidence.py",
    "tools/ci/policy.json",
    "packages/aitm-usage/uv.lock",
)
MAX_ARCHIVE = 8 * 1024 * 1024
MAX_RECEIPT = 16 * 1024 * 1024


def current_target(github):
    repo = github.document("")
    branch = github.document(f"branches/{TARGET}")
    require(
        repo["id"] == REPO_ID
        and repo["full_name"] == REPO
        and repo["default_branch"] == branch["name"] == TARGET
        and branch["protected"] is True
        and digest(branch["commit"]["sha"]),
        "scheduled source is not the protected default branch",
    )
    workflow = github.document(f"actions/workflows/{Path(WORKFLOW).name}")
    require(
        workflow["path"] == WORKFLOW
        and workflow["state"] == "active"
        and positive(workflow["id"]),
        "scheduled workflow identity disagrees",
    )
    return branch["commit"]["sha"], workflow["id"]


def latest(github, workflow, event, since):
    starting = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    records = github.pages(
        f"actions/workflows/{workflow}/runs?branch={TARGET}&event={event}&created=%3E%3D{starting}&per_page=100",
        "workflow_runs",
    )
    require(len(records) < 1000, "scheduled run search is truncated")
    for row in records:
        validate_run(row, workflow, event)
    return max(records, key=lambda row: row["run_number"], default=None)


def validate_run(row, workflow, event):
    require(
        row["repository"]["id"] == row["head_repository"]["id"] == REPO_ID
        and row["workflow_id"] == workflow
        and row["path"] == WORKFLOW
        and row["head_branch"] == TARGET
        and row["event"] == event
        and digest(row["head_sha"])
        and all(
            positive(row[k])
            for k in ("id", "run_number", "run_attempt", "check_suite_id")
        ),
        "scheduled run identity disagrees",
    )


def run_key(row):
    return tuple(
        row[name]
        for name in (
            "id",
            "run_number",
            "run_attempt",
            "check_suite_id",
            "head_sha",
            "status",
            "conclusion",
            "run_started_at",
        )
    )


def schedule_slot(now):
    slot = now.replace(hour=3, minute=17, second=0, microsecond=0)
    return slot if now >= slot else slot - timedelta(days=1)


def profile(collected, executed, optional):
    require(
        collected["schema"] == "aitm.pytest-evidence/v1"
        and collected["exit_code"] == 0
        and collected["deselected"] == []
        and collected["reports"] == []
        and collected["collected"] == executed["collected"],
        "full collection inventory disagrees with execution",
    )
    outcomes, failures = _outcomes(executed, optional)
    require(not failures, "incomplete full test outcomes")
    return outcomes


def verify_document(receipt, run, policy):
    require(
        receipt["schema"] == SCHEMA
        and receipt["binding"]
        == {
            "repository_id": REPO_ID,
            "event": run["event"],
            "sha": run["head_sha"],
            "run_id": run["id"],
            "attempt": run["run_attempt"],
            "ref": f"refs/heads/{TARGET}",
        }
        and set(receipt["profiles"]) == set(PROFILES),
        "scheduled evidence binding disagrees",
    )
    combined = set()
    counts = {}
    for label in PROFILES:
        pair = receipt["profiles"][label]
        outcomes = profile(
            pair["collection"], pair["execution"], policy["optional_skips"]
        )
        require(not combined.intersection(outcomes), "overlapping scheduled profiles")
        root = "packages/aitm-usage/tests/" if label == "product" else "tools/ci/tests/"
        require(
            all(node.startswith(root) for node in outcomes),
            "scheduled profile escaped its root",
        )
        counts[label] = len(outcomes)
        combined.update(outcomes)
    require(
        set(policy["required_tests"]) <= combined, "missing required scheduled test"
    )
    children = [
        child
        for label in PROFILES
        for child in receipt["profiles"][label]["execution"]["children"]
    ]
    expected = set(policy["required_children"])
    require(
        len(children) == len(expected)
        and {child["label"] for child in children} == expected
        and all(
            type(child["returncode"]) is int and child["returncode"] == 0
            for child in children
        ),
        "missing or failed scheduled native child",
    )
    return counts


def verify_artifact(github, run, job):
    artifacts = github.pages(
        f"actions/runs/{run['id']}/artifacts?per_page=100", "artifacts"
    )
    name = f"aitm-scheduled-shadow-a{run['run_attempt']}"
    found = [item for item in artifacts if item["name"] == name]
    require(len(found) == 1, "scheduled artifact missing or duplicated")
    item = found[0]
    link = item["workflow_run"]
    require(
        positive(item["id"])
        and item["expired"] is False
        and link["id"] == run["id"]
        and link["head_branch"] == TARGET
        and link["head_sha"] == run["head_sha"]
        and link["repository_id"] == link["head_repository_id"] == REPO_ID
        and timestamp(job["started_at"])
        <= timestamp(item["created_at"])
        <= timestamp(job["completed_at"])
        and positive(item["size_in_bytes"])
        and item["size_in_bytes"] <= MAX_ARCHIVE,
        "scheduled artifact custody disagrees",
    )
    raw = github.api(f"actions/artifacts/{item['id']}/zip", limit=MAX_ARCHIVE)
    require(
        len(raw) == item["size_in_bytes"]
        and item["digest"] == "sha256:" + sha256(raw).hexdigest(),
        "scheduled artifact digest disagrees",
    )
    try:
        with ZipFile(BytesIO(raw)) as archive:
            rows = archive.infolist()
            require(
                len(rows) == 1
                and rows[0].orig_filename == "receipt.json"
                and 0 < rows[0].file_size <= MAX_RECEIPT,
                "invalid scheduled archive members",
            )
            with archive.open(rows[0]) as stream:
                receipt = decode_json(stream.read(MAX_RECEIPT + 1))
    except (BadZipFile, RuntimeError, EOFError, NotImplementedError):
        raise Hold("invalid scheduled evidence archive") from None
    tree = commit(github, run["head_sha"])["tree"]["sha"]
    entries = tree_entries(github, tree)
    checkout = Path(__file__).resolve().parents[2]
    controls = {}
    for path in CONTROLS:
        controls[path] = regular_blob(entries, path)
        require(
            blob(github, controls[path]) == (checkout / path).read_bytes(),
            "scheduled control disagrees with trusted checkout",
        )
    policy = decode_json((checkout / "tools/ci/policy.json").read_bytes())
    return {
        "id": item["id"],
        "digest": item["digest"],
        "tree": tree,
        "controls": controls,
        "counts": verify_document(receipt, run, policy),
    }


def exact_job(github, route, run):
    suite = github.document(f"check-suites/{run['check_suite_id']}")
    require(
        suite["id"] == run["check_suite_id"]
        and suite["head_sha"] == run["head_sha"]
        and suite["head_branch"] == TARGET
        and suite["app"]["slug"] == "github-actions"
        and positive(suite["app"]["id"]),
        "scheduled Actions suite disagrees",
    )
    jobs = github.pages(f"{route}/jobs?per_page=100", "jobs")
    require(
        len(jobs) == 1 and jobs[0]["name"] == JOB, "scheduled job missing or unexpected"
    )
    [job] = jobs
    authenticate_job(github, job, run, suite, {job["id"]: 1})
    return job, suite


def inspect(github, *, expected=None, event="schedule", now=None):
    require(event in {"schedule", "workflow_dispatch"}, "invalid shadow event")
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    slot = schedule_slot(now)
    sha, workflow = current_target(github)
    since = slot - timedelta(days=1)
    run = latest(github, workflow, event, since)
    result = {
        "schema": SCHEMA,
        "provenance": "shadow",
        "repository_id": REPO_ID,
        "workflow_id": workflow,
        "event": event,
        "sha": sha,
        "target": TARGET,
        "slot": slot.isoformat() if event == "schedule" else None,
        "status": "pending",
        "artifact": None,
        "failed_job": None,
        "current_verified": False,
        "gaps": [],
    }
    deadline = slot + timedelta(minutes=45)
    if expected and (not run or expected != (run["id"], run["run_attempt"])):
        result["status"] = "stale"
        return result
    if run is None or (
        event == "schedule"
        and not slot <= timestamp(run["created_at"]) <= min(now, deadline)
    ):
        result["gaps"].append(
            "no run for the current schedule slot"
            if event == "schedule"
            else "no diagnostic run"
        )
        if event == "schedule" and now >= deadline:
            result["status"] = "incomplete"
        return result
    if run["head_sha"] != sha:
        result["status"] = "stale"
        return result
    result.update(
        run_id=run["id"],
        run_number=run["run_number"],
        attempt=run["run_attempt"],
        started_at=run["run_started_at"],
    )
    route = f"actions/runs/{run['id']}/attempts/{run['run_attempt']}"
    try:
        attempt = github.document(route)
        validate_run(attempt, workflow, event)
        require(run_key(attempt) == run_key(run), "scheduled attempt changed")
        job, suite = exact_job(github, route, run)
        if job["status"] == "completed" and job["conclusion"] in FAILURES:
            result.update(status="red", failed_job=job["id"])
        elif successful(job) and successful(run) and successful(suite):
            result.update(status="green", artifact=verify_artifact(github, run, job))
        elif run["status"] == "completed" or (event == "schedule" and now >= deadline):
            result.update(status="incomplete")
            result["gaps"].append("scheduled completion unavailable")
    except EVIDENCE_ERRORS as exc:
        if run["status"] == "completed" or (event == "schedule" and now >= deadline):
            result["status"] = "incomplete"
        result["gaps"].append(
            str(exc) if isinstance(exc, Hold) else "invalid scheduled evidence"
        )
    try:
        same_target = current_target(github) == (sha, workflow)
        final = latest(github, workflow, event, since) if same_target else None
        same_attempt = (
            final is not None
            and run_key(final) == run_key(run)
            and final["created_at"] == run["created_at"]
        )
        if same_attempt:
            final_attempt = github.document(route)
            validate_run(final_attempt, workflow, event)
            same_attempt = run_key(final_attempt) == run_key(run)
    except EVIDENCE_ERRORS:
        result["gaps"].append("current scheduled attempt could not be reverified")
        if result["status"] != "red":
            result.update(status="incomplete", artifact=None)
    else:
        if not same_attempt:
            result.update(status="stale", artifact=None)
        else:
            result["current_verified"] = True
    return result


def incident_observation(decision):
    """Translate verified scheduled evidence for a separate shadow-only store."""
    require(
        decision["schema"] == SCHEMA
        and decision["provenance"] == "shadow"
        and decision["event"] == "schedule"
        and decision["current_verified"] is True
        and decision["status"] in {"red", "green", "incomplete"},
        "scheduled result unavailable for shadow incident replay",
    )
    receipt = {
        **decision,
        "schema": "aitm.ci-advisory/v1",
        "workflow_id": PUSH_WORKFLOW_ID,
        "scheduled_source": {
            "workflow_id": decision["workflow_id"],
            "slot": decision["slot"],
        },
        "failures": ["python:failure"] if decision["status"] == "red" else [],
    }
    if decision["status"] == "green":
        receipt["artifact"] = {
            **decision["artifact"],
            "policy_result": {"passed": True},
        }
    return receipt


def emit(directory):
    binding = {
        "repository_id": int(os.environ["GITHUB_REPOSITORY_ID"]),
        "event": os.environ["GITHUB_EVENT_NAME"],
        "sha": os.environ["GITHUB_SHA"],
        "run_id": int(os.environ["GITHUB_RUN_ID"]),
        "attempt": int(os.environ["GITHUB_RUN_ATTEMPT"]),
        "ref": os.environ["GITHUB_REF"],
    }
    profiles = {
        label: {
            phase: decode_json((directory / f"{label}-{phase}.json").read_bytes())
            for phase in ("collection", "execution")
        }
        for label in PROFILES
    }
    (directory / "receipt.json").write_text(
        json.dumps(
            {"schema": SCHEMA, "binding": binding, "profiles": profiles},
            separators=(",", ":"),
        )
        + "\n"
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--dispatch-diagnostic", action="store_true")
    parser.add_argument("--expect", nargs=2, type=int, metavar=("RUN", "ATTEMPT"))
    args = parser.parse_args(argv)
    try:
        if args.emit:
            emit(args.emit)
        else:
            event = "workflow_dispatch" if args.dispatch_diagnostic else "schedule"
            result = inspect(
                GitHub(REPO),
                event=event,
                expected=tuple(args.expect) if args.expect else None,
            )
            print(json.dumps(result, sort_keys=True, indent=2))
    except EVIDENCE_ERRORS as exc:
        print(f"scheduled shadow: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
