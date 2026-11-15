"""Read native hosted custody and exact result for a reviewed shadow run."""
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZipFile

from ci_advisory import authenticate_job
from ci_fast_story_shadow import (
    CLI, PATH, REPO, REPOSITORY_ID, SCHEMA, TARGET, admission_from_planning,
    classify_diff, collection, git, phase_evidence, verify_live_subject,
)
from verify_pr import GitHub, successful, timestamp


def verify(github, root, run_id, attempt_number):
    workflow = github.document(f"actions/workflows/{Path(PATH).name}")
    route = f"actions/runs/{run_id}"
    run = github.document(route)
    attempt_route = f"{route}/attempts/{attempt_number}"
    attempt = github.document(attempt_route)
    assert workflow["state"] == "active" and workflow["path"] == PATH
    for entry in (run, attempt):
        assert entry["id"] == run_id and entry["run_attempt"] == attempt_number
        assert entry["repository"]["id"] == entry["head_repository"]["id"] == REPOSITORY_ID
        assert entry["workflow_id"] == workflow["id"] and entry["path"] == PATH
        assert entry["head_branch"] == TARGET and entry["event"] == "workflow_dispatch"
        assert successful(entry)
    assert run["head_sha"] == attempt["head_sha"] and run["check_suite_id"] == attempt["check_suite_id"]
    suite = github.document(f"check-suites/{run['check_suite_id']}")
    assert suite["head_sha"] == run["head_sha"] and suite["app"]["slug"] == "github-actions"
    assert successful(suite)
    job, = github.pages(f"{attempt_route}/jobs?per_page=100", "jobs")
    assert job["name"] == "bounded-fast-story-shadow" and successful(job)
    authenticate_job(github, job, run, suite, {job["id"]: 1})

    inventory = github.pages(f"{route}/artifacts?per_page=100", "artifacts")
    item, = (a for a in inventory if a["name"] == f"aitm-fast-shadow-a{attempt_number}")
    link = item["workflow_run"]
    assert not item["expired"] and link["id"] == run_id
    assert link["head_sha"] == run["head_sha"] and link["head_branch"] == TARGET
    assert link["repository_id"] == link["head_repository_id"] == REPOSITORY_ID
    assert timestamp(job["started_at"]) <= timestamp(item["created_at"]) <= timestamp(job["completed_at"])
    raw = github.api(f"actions/artifacts/{item['id']}/zip", limit=8 * 1024 * 1024)
    assert len(raw) == item["size_in_bytes"] and item["digest"] == "sha256:" + sha256(raw).hexdigest()
    with ZipFile(BytesIO(raw)) as archive:
        member, = archive.infolist()
        assert member.orig_filename == "receipt.json" and member.file_size < 16 * 1024 * 1024
        receipt = json.loads(archive.read(member))

    assert receipt["schema"] == SCHEMA and receipt["scope"] == "advisory"
    assert receipt["repository_id"] == REPOSITORY_ID
    assert (receipt["run_id"], receipt["attempt"]) == (run_id, attempt_number)
    subject = admission_from_planning(github, receipt["planning_commit"])
    assert subject == receipt["subject"] and subject["base"] == run["head_sha"]
    verify_live_subject(github, subject)
    assert git(root, "rev-parse", "HEAD").decode().strip() == subject["base"]
    git(root, "fetch", "--no-tags", "origin", f"refs/pull/{subject['pr']}/merge")
    assert git(root, "rev-parse", "FETCH_HEAD").decode().strip() == subject["tested"]
    assert git(root, "rev-parse", f"{subject['tested']}^{{tree}}").decode().strip() == subject["tree"]
    assert git(root, "show", "-s", "--format=%P", subject["tested"]).decode().split() == [
        subject["base"], subject["head"],
    ]
    changes = classify_diff(git(root, "diff", "--raw", "-z", "--no-renames", subject["base"], subject["tested"]))
    assert receipt["docs_paths"] == list(changes)
    result = receipt["result"]
    if changes:
        assert receipt["mode"] == "selected"
        trusted = collection(result["trusted_collection"])
        assert collection(result["tested_collection"]) == trusted
        policy = json.loads((root / "tools/ci/policy.json").read_bytes())
        mandatory = set(policy["required_tests"]) | {CLI}
        assert result["mandatory"] == sorted(mandatory)
        assigned = [node for node in trusted if node in mandatory]
        assert set(assigned) == mandatory and result["selected"] == assigned
        assert phase_evidence(result["execution"], assigned, policy["required_children"]) == result["outcomes"]
        summary = {"selected": len(assigned), "inventory": len(trusted), "children": result["execution"]["children"]}
    else:
        assert receipt["mode"] == "full-required" and result is None
        summary = {"selected": 0}
    verify_live_subject(github, subject)
    assert github.document(route)["run_attempt"] == attempt_number
    return {
        "subject": subject, "mode": receipt["mode"], "scope": receipt["scope"],
        "planning_commit": receipt["planning_commit"], "run": run_id, "attempt": attempt_number,
        "job": job["id"], "artifact": item["id"], "artifact_sha256": item["digest"],
        **summary,
    }


if __name__ == "__main__":
    root, run_id, number = sys.argv[1:4]
    print(json.dumps(verify(GitHub(REPO), Path(root), int(run_id), int(number)), indent=2, sort_keys=True))
