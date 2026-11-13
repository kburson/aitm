"""Fetch read-only exact trunk CI evidence and run benign advisory controls."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from advisory import Incident, REPO, REQUIRED, TARGET, WORKFLOW, assess

HERE = Path(__file__).resolve().parent


def read(endpoint, *args, decode=True):
    cmd = ["gh", "api", "/".join(part for part in ("repos", REPO, endpoint) if part), *args]
    response = subprocess.check_output(cmd)
    return json.loads(response) if decode else response


def artifact_check(run, source, directory):
    root = f"actions/runs/{run['id']}"
    [artifact] = [
        item for item in read(f"{root}/artifacts")["artifacts"]
        if item["name"] == f"aitm-ci-python-a{run['run_attempt']}"
    ]
    exact = artifact["workflow_run"]
    assert (exact["id"], exact["repository_id"], exact["head_repository_id"],
            exact["head_sha"], exact["head_branch"]) == (
                run["id"], run["repository"]["id"], run["head_repository"]["id"],
                run["head_sha"], TARGET,
            )
    assert artifact["expired"] is False
    archive = read(f"actions/artifacts/{artifact['id']}/zip", decode=False)
    calculated = sha256(archive).hexdigest()
    assert artifact["digest"] == f"sha256:{calculated}"
    path = directory / "artifact.zip"
    path.write_bytes(archive)
    fields = {
        "inventory": "pytest.json",
        "outcomes": "pytest.json",
        "coverage": "product-coverage.json",
        "product-inventory": "product-inventory.json",
        "helpers": "helper-coverage.json",
        "child-evidence": "children.json",
        "capability": "capability.json",
    }
    gate_cmd = [sys.executable]
    file_ids = {}
    for filename in (".github/workflows/ci.yml", "tools/ci/python_gate.py", "tools/ci/policy.json"):
        data = subprocess.check_output(["git", "-C", str(source), "show", f"{run['head_sha']}:{filename}"])
        file_ids[filename] = sha256(data).hexdigest()
        (directory / Path(filename).name).write_bytes(data)
    gate_cmd.extend([str(directory / "python_gate.py"), "--mode", "push", "--policy",
                     str(directory / "policy.json")])
    with ZipFile(path) as bundle:
        assert len(bundle.namelist()) == len(set(bundle.namelist()))
        for key, name in fields.items():
            entry = directory / name
            entry.write_bytes(bundle.read(name))
            gate_cmd.extend([f"--{key}", str(entry)])
    outcome = subprocess.run(gate_cmd, capture_output=True, check=True, text=True)
    gate = json.loads(outcome.stdout)
    assert gate["passed"] is True
    return {"id": artifact["id"], "sha256": calculated, "passed": gate["passed"],
            "tracked_inputs": file_ids, "gate_disposition": gate}


def latest_for(sha):
    response = read(f"actions/workflows/{WORKFLOW}/runs", "--method", "GET", "-f", f"branch={TARGET}",
                    "-f", "event=push", "-f", f"head_sha={sha}", "-f", "per_page=100")
    assert 0 < response["total_count"] <= len(response["workflow_runs"])
    return max(response["workflow_runs"], key=lambda row: (row["run_number"], row["run_attempt"]))


def live(source):
    trunk = read(f"branches/{TARGET}")["commit"]["sha"]
    repo = read("")
    workflow = read("actions/workflows/ci.yml")
    assert repo["default_branch"] == TARGET and workflow["id"] == WORKFLOW
    latest = latest_for(trunk)
    run_path = f"actions/runs/{latest['id']}"
    attempt_path = f"{run_path}/attempts/{latest['run_attempt']}"
    run = read(attempt_path)
    jobs = read(f"{attempt_path}/jobs", "--method", "GET", "-f", "per_page=100")
    assert jobs["total_count"] <= len(jobs["jobs"])
    with TemporaryDirectory() as temp:
        artifact = artifact_check(run, source, Path(temp))
    assert read(f"branches/{TARGET}")["commit"]["sha"] == trunk
    fresh = latest_for(trunk)
    assert (fresh["id"], fresh["run_attempt"], fresh["status"], fresh["conclusion"]) == (
        run["id"], run["run_attempt"], run["status"], run["conclusion"],
    )
    observed = assess(run, jobs["jobs"], trunk, (latest["id"], latest["run_attempt"]), artifact["passed"])
    assert observed.status == "green"
    historical = read("actions/runs/43250904624/attempts/1")
    historical_jobs = read("actions/runs/43250904624/attempts/1/jobs")["jobs"]
    try:
        assess(historical, historical_jobs, trunk, (latest["id"], latest["run_attempt"]), False)
    except ValueError as exc:
        old_rejected = str(exc)
    else:
        raise AssertionError("historical red was accepted for live trunk")
    return run, jobs["jobs"], {"trunk_sha": trunk, "tree": read(f"git/commits/{trunk}")["tree"]["sha"],
                              "observation": observed.__dict__, "artifact": artifact,
                              "jobs": {job["name"]: job["conclusion"] for job in jobs["jobs"]},
                              "historical_run": historical["id"],
                              "historical_conclusion": historical["conclusion"],
                              "historical_jobs": {job["name"]: job["conclusion"] for job in historical_jobs},
                              "historical_rejected": old_rejected}


def controls(run, jobs):
    incident = Incident()
    checks = {}

    def envelope(seq, *, attempt=1, sha=None, conclusion="success", status="completed", started="2026-11-12T18:00:00Z"):
        result = deepcopy(run)
        result.update(id=90000000000 + seq, run_attempt=attempt, run_number=100 + seq,
                      head_sha=sha or run["head_sha"], conclusion=conclusion, status=status, run_started_at=started)
        required_jobs = [
            {**job, "run_id": result["id"], "run_attempt": attempt, "head_sha": result["head_sha"]}
            for job in jobs if job["name"] in REQUIRED
        ]
        return result, required_jobs

    def verdict(envelope, *, verified=True, latest=None):
        event, lanes = envelope
        return assess(event, lanes, event["head_sha"], latest or (event["id"], event["run_attempt"]), verified)

    def verify(label, wanted, actual):
        assert wanted == actual, (label, wanted, actual)
        checks[label] = actual

    def refuses(label, action):
        try:
            action()
        except ValueError as exc:
            checks[label] = str(exc)
        else:
            raise AssertionError(f"{label} accepted")

    attempt = envelope(1, status="in_progress", conclusion=None)
    verify("ordinary-pending-does-not-warn", "pending", incident.observe(verdict(attempt)))
    active_run, lanes = attempt
    lanes = [job for job in lanes if job["name"] != "file-checks"]
    [python] = [job for job in lanes if job["name"] == "python"]
    python["conclusion"] = "failure"
    red = verdict((active_run, lanes), verified=False)
    verify("retains-failed-lane", ("python:failure",), red.failures)
    verify("retains-missing-sibling", ("file-checks:missing-or-duplicate",), red.gaps)
    verify("red-requests-manual-stop", "manual-stop-requested", incident.observe(red))
    verify("duplicate-red-suppressed", "duplicate", incident.observe(red))
    terminal_lanes = deepcopy(lanes)
    terminal_lanes.append({**python, "name": "file-checks", "conclusion": "success"})
    terminal_red = verdict(({**active_run, "status": "completed", "conclusion": "failure"}, terminal_lanes))
    verify("later-evidence-updates-same-warning", "same-attempt-evidence-updated", incident.observe(terminal_red))
    verify("one-incident-version-per-warning", 1, incident.version)
    verify("same-attempt-detail-retains-known-failure", ("python:failure",), incident.failing.failures)
    verify("red-cannot-be-reclassified-green-in-same-attempt", "red-evidence-retained",
           incident.observe(verdict(envelope(1))))
    verify("old-run-cannot-overwrite", "stale", incident.observe(verdict(envelope(0))))
    refuses("prior-attempt-rejected-at-intake", lambda: verdict(envelope(1), latest=(active_run["id"], 2)))

    incomplete = verdict(envelope(2), verified=False)
    verify("success-with-missing-artifact-is-evidence-gap", "incomplete", incomplete.status)
    verify("evidence-gap-requests-manual-stop", "manual-stop-requested", incident.observe(incomplete))
    verify("green-without-repair-is-advisory-only", "green-without-repair", incident.observe(verdict(envelope(3))))

    repair_sha = "a" * 40
    landed_at = "2026-11-12T18:10:00Z"
    refuses("wrong-repair-sha", lambda: incident.record_landed_repair("agent", 99, repair_sha, landed_at, "b" * 40))
    incident.record_landed_repair("agent", 99, repair_sha, landed_at, repair_sha)
    refuses("second-repair-rejected", lambda: incident.record_landed_repair("other-agent", 100, repair_sha, landed_at, repair_sha))
    verify("run-admitted-before-repair-cannot-recover", "recovery-not-fresh",
           incident.observe(verdict(envelope(4, sha=repair_sha, started="2026-11-12T18:09:00Z"))))
    green = verdict(envelope(5, sha=repair_sha, started="2026-11-12T18:11:00Z"))
    verify("fresh-current-trunk-green-offers-manual-resume", "manual-resume-available", incident.observe(green))
    verify("remains-active-before-acknowledgment", True, incident.active)
    refuses("stale-incident-version", lambda: incident.acknowledge_resume(incident.version - 1, green.key, repair_sha))
    refuses("trunk-drift-before-resume", lambda: incident.acknowledge_resume(incident.version, green.key, "b" * 40))
    verify("manual-resume-with-current-readback", "manually-resumed",
           incident.acknowledge_resume(incident.version, green.key, repair_sha))

    separate = Incident()
    separate.observe(red)
    separate.record_landed_repair("agent", 99, repair_sha, landed_at, repair_sha)
    separate.observe(green)
    pending = verdict(envelope(6, sha=repair_sha, status="in_progress", conclusion=None))
    separate.observe(pending)
    refuses("newer-run-invalidates-recovery", lambda: separate.acknowledge_resume(separate.version, green.key, repair_sha))
    red_again = verdict(envelope(6, sha=repair_sha, conclusion="failure"))
    verify("new-failure-advances-incident", "manual-stop-requested", separate.observe(red_again))
    verify("new-failure-invalidates-repair", None, separate.repair)
    infrastructure = Incident()
    infrastructure.observe(incomplete)
    ready_at = "2026-11-12T18:12:00Z"
    infrastructure.confirm_infrastructure_recovered(infrastructure.version, incomplete.sha, ready_at)
    same_sha_green = verdict(envelope(7, started="2026-11-12T18:13:00Z"))
    verify("infrastructure-recovery-may-use-fresh-run-on-same-sha", "manual-resume-available",
           infrastructure.observe(same_sha_green))
    verify("infrastructure-recovery-still-requires-owner", True, infrastructure.active)
    refuses("verified-red-cannot-be-dismissed-as-evidence-gap",
            lambda: separate.confirm_infrastructure_recovered(separate.version, repair_sha, ready_at))
    late_red = Incident()
    late_red.observe(incomplete)
    late_red.confirm_infrastructure_recovered(late_red.version, incomplete.sha, ready_at)
    verify("late-same-attempt-failure-updates-warning", "same-attempt-evidence-updated",
           late_red.observe(verdict(envelope(2, conclusion="failure"))))
    verify("late-same-attempt-failure-revokes-infrastructure-recovery", "green-without-repair",
           late_red.observe(same_sha_green))
    refuses("late-same-attempt-failure-prevents-resume",
            lambda: late_red.acknowledge_resume(late_red.version, same_sha_green.key, incomplete.sha))
    return checks


def main():
    source = Path(sys.argv[1]).resolve()
    run, jobs, readback = live(source)
    report = {"spike": 275, "mode": "read-only prototype", "live_control": readback,
              "synthetic_controls": controls(run, jobs)}
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    (HERE / "readback.json").write_text(output)
    print(output, end="")


if __name__ == "__main__":
    main()
