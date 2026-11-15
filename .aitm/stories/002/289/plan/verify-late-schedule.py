"""Verify one genuine late scheduled attempt for historical evidence only."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZipFile

from ci_scheduled_shadow import (
    MAX_ARCHIVE,
    REPO,
    TARGET,
    current_target,
    exact_job,
    incident_observation,
    inspect,
    run_key,
    validate_run,
    verify_artifact,
)
from verify_pr import GitHub, Hold, successful, timestamp


def read_late(run_id, attempt_number, export):
    github = GitHub(REPO)
    target_sha, workflow = current_target(github)
    route = f"actions/runs/{run_id}"
    attempt_route = f"{route}/attempts/{attempt_number}"
    run = github.document(route)
    attempt = github.document(attempt_route)
    for entry in (run, attempt):
        validate_run(entry, workflow, "schedule")
        assert entry["id"] == run_id and entry["run_attempt"] == attempt_number
    assert run_key(attempt) == run_key(run)
    assert run["head_sha"] == target_sha == (export / "source-sha").read_text().strip()
    job, suite = exact_job(github, attempt_route, run)
    assert all(map(successful, (run, attempt, job, suite)))
    artifact = verify_artifact(github, run, job)
    raw = github.api(f"actions/artifacts/{artifact['id']}/zip", limit=MAX_ARCHIVE)
    assert "sha256:" + sha256(raw).hexdigest() == artifact["digest"]
    with ZipFile(BytesIO(raw)) as zipped:
        receipt = json.loads(zipped.read("receipt.json"))

    inventory = {}
    for profile, path in (("product", "packages/aitm-usage/tests/"), ("helpers", "tools/ci/tests/")):
        expected = [
            line for line in (export / f"{profile}.log").read_text().splitlines()
            if line.startswith(path) and "::" in line
        ]
        native = receipt["profiles"][profile]
        assert native["collection"]["collected"] == native["execution"]["collected"] == expected
        assert len(expected) == len(set(expected)) == artifact["counts"][profile]
        assert not native["collection"]["deselected"] and not native["execution"]["deselected"]
        inventory[profile] = {
            "count": len(expected),
            "ordered_ids_sha256": sha256(("\n".join(expected) + "\n").encode()).hexdigest(),
        }

    freshness = inspect(github, expected=(run_id, attempt_number))
    assert freshness["status"] == "incomplete" and not freshness["current_verified"]
    assert freshness["artifact"] is None and freshness["observed_run"]["id"] == run_id
    try:
        incident_observation(freshness)
    except Hold as exc:
        handoff = str(exc)
    else:
        raise AssertionError("Unverified late run entered the incident handoff")
    slot_delay = (timestamp(run["created_at"]) - timestamp(freshness["slot"])).total_seconds()
    assert slot_delay > 45 * 60
    assert current_target(github) == (target_sha, workflow)
    assert run_key(github.document(route)) == run_key(github.document(attempt_route)) == run_key(run)

    return {
        "scope": "historical scheduled execution",
        "result": "success",
        "qualifies_as_current_green": False,
        "repository": REPO,
        "target": TARGET,
        "sha": target_sha,
        "workflow_id": workflow,
        "run_id": run_id,
        "attempt": attempt_number,
        "event": run["event"],
        "created_at": run["created_at"],
        "slot_delay_seconds": int(slot_delay),
        "job_id": job["id"],
        "job_started_at": job["started_at"],
        "job_completed_at": job["completed_at"],
        "artifact": artifact,
        "inventory": inventory,
        "children": {
            name: rows["execution"]["children"] for name, rows in receipt["profiles"].items()
        },
        "freshness_handoff": handoff,
        "current_slot": freshness,
    }


if __name__ == "__main__":
    archive_root = Path(sys.argv[3])
    result = read_late(int(sys.argv[1]), int(sys.argv[2]), archive_root)
    print(json.dumps(result, indent=2, sort_keys=True))
