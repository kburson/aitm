"""Replay exact disposable GitHub results through the existing shadow store."""
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import ci_advisory
from ci_incident import Store
from ci_recovery import acknowledge, reconcile
from simulate_operator import OPERATOR, REPO, REPO_ID, ROOT, api

PREFIX = f"repos/{REPO}"


def fixture_run(run_id, sha, conclusion):
    run = api(f"{PREFIX}/actions/runs/{run_id}")
    jobs = api(f"{PREFIX}/actions/runs/{run_id}/attempts/{run['run_attempt']}/jobs")["jobs"]
    assert run["repository"]["id"] == run["head_repository"]["id"] == REPO_ID
    assert run["event"] == "push" and run["head_branch"] == "trunk" and run["head_sha"] == sha
    assert run["status"] == "completed" and run["conclusion"] == conclusion
    job, = jobs
    assert job["name"] == "fixture-ci" and job["conclusion"] == conclusion
    return {k: run[k] for k in ("id", "run_number", "run_attempt", "workflow_id", "head_sha", "run_started_at", "conclusion")}


def projected(run):
    success = run["conclusion"] == "success"
    return {
        "schema": "aitm.ci-advisory/v1", "provenance": "shadow",
        "repository_id": REPO_ID, "workflow_id": run["workflow_id"], "target": "trunk",
        "run_id": run["id"], "run_number": run["run_number"], "attempt": run["run_attempt"],
        "status": "green" if success else "red", "current_verified": True,
        "sha": run["head_sha"], "started_at": run["run_started_at"],
        "failures": [] if success else ["python:failure"],
        "artifact": {
            "id": run["id"],
            "digest": "sha256:" + sha256(json.dumps(run, sort_keys=True).encode()).hexdigest(),
            "policy_result": {"passed": True},
        } if success else None,
    }


def main(current_run):
    delivery = json.loads((ROOT / "verified-repair.json").read_bytes())
    plan = delivery["nomination"]
    stale = fixture_run(43718360953, (ROOT / "old-green-sha").read_text().strip(), "success")
    red = fixture_run(43718383807, plan["base"], "failure")
    latest = fixture_run(current_run, delivery["merge"], "success")
    assert stale["workflow_id"] == red["workflow_id"] == latest["workflow_id"]
    assert api(f"{PREFIX}/branches/trunk")["commit"]["sha"] == latest["head_sha"]
    assert api(f"{PREFIX}/rulesets/{plan['hold_ruleset']}")["enforcement"] == "active"
    ci_advisory.REPOSITORY_ID = REPO_ID
    ci_advisory.WORKFLOW_ID = latest["workflow_id"]
    repair = {"pr": plan["pr"], "sha": delivery["merge"], "landed_at": delivery["merged_at"], "receipt": delivery["repair_review_sha256"]}
    with TemporaryDirectory() as name:
        store = Store(Path(name) / "hold-shadow.sqlite", "shadow")
        assert store.observe(projected(stale)) == "green"
        assert store.observe(projected(red)) == "warning"
        store.nominate(1, "rehearsal-repair-owner", plan["pr"])
        assert reconcile(store, 1, projected(stale), repair=repair) is None
        assert store.status()["incident"]["active"]
        token = reconcile(store, 1, projected(latest), repair=repair)
        assert token and store.status()["incident"]["active"]
        assert acknowledge(store, 1, "rehearsal-operator", token, projected(latest), repair=repair)
        assert not store.status()["incident"]["active"]
        assert store.status()["incident"]["acknowledgment"]["repair"]["sha"] == latest["head_sha"]
    print(json.dumps({
        "scope": "disposable shadow replay with provider fixture outcomes as inputs",
        "fixture_attestation": "local projection of exact disposable GitHub run metadata",
        "old_green": stale, "red": red, "repaired_green": latest,
        "repaired_sha": delivery["merge"], "nomination_pr": plan["pr"], "operator_id": OPERATOR,
        "old_green_rejected": True, "fresh_green_left_hold_active": True,
        "explicit_operator_simulation_acknowledged": True,
        "branch_protection_mutation": None,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main(int(sys.argv[1]))
