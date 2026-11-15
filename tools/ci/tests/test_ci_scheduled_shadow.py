from copy import deepcopy
from datetime import datetime

import ci_scheduled_shadow as shadow
import pytest
from verify_pr import Hold

SHA = "a" * 40
START = "2026-11-14T03:18:00Z"
RUN = {
    "id": 34,
    "run_number": 4,
    "run_attempt": 2,
    "workflow_id": 12,
    "path": shadow.WORKFLOW,
    "event": "schedule",
    "head_branch": "trunk",
    "head_sha": SHA,
    "repository": {"id": shadow.REPO_ID},
    "head_repository": {"id": shadow.REPO_ID},
    "check_suite_id": 55,
    "status": "completed",
    "conclusion": "success",
    "run_started_at": START,
    "created_at": START,
}
JOB = {
    "id": 72,
    "name": shadow.JOB,
    "run_id": 34,
    "run_attempt": 2,
    "head_sha": SHA,
    "status": "completed",
    "conclusion": "success",
    "started_at": START,
    "completed_at": "2026-11-14T03:20:00Z",
}
APP = {"id": 15368, "slug": "github-actions"}


class Provider:
    def __init__(self):
        self.run = deepcopy(RUN)
        self.job = deepcopy(JOB)
        self.branch = SHA
        self.artifacts = []

    def document(self, endpoint):
        if endpoint == "":
            return {
                "id": shadow.REPO_ID,
                "full_name": shadow.REPO,
                "default_branch": "trunk",
            }
        if endpoint == "branches/trunk":
            return {"name": "trunk", "protected": True, "commit": {"sha": self.branch}}
        if endpoint == "actions/workflows/scheduled-full-shadow.yml":
            return {"id": 12, "path": shadow.WORKFLOW, "state": "active"}
        if endpoint == "actions/runs/34/attempts/2":
            return self.run
        if endpoint == "check-suites/55":
            return {
                "id": 55,
                "head_sha": SHA,
                "head_branch": "trunk",
                "app": APP,
                "status": self.run["status"],
                "conclusion": self.run["conclusion"],
            }
        if endpoint == "check-runs/72":
            return {**self.job, "check_suite": {"id": 55}, "app": APP}
        raise AssertionError(endpoint)

    def pages(self, _, key):
        return {
            "workflow_runs": [self.run],
            "jobs": [self.job],
            "artifacts": self.artifacts,
        }[key]


def test_missing_artifact_cannot_claim_green():
    assert observe(Provider())["status"] == "incomplete"


def test_authenticated_failure_survives_missing_artifact():
    provider = Provider()
    provider.run["conclusion"] = provider.job["conclusion"] = "failure"
    result = observe(provider)
    assert result["status"] == "red"
    assert result["failed_job"] == 72


def test_delayed_or_stale_attempt_does_not_claim_green():
    provider = Provider()
    assert observe(provider, expected=(34, 1))["status"] == "stale"
    provider.branch = "b" * 40
    assert observe(provider)["status"] == "stale"


def test_foreign_event_cannot_enter_schedule_route():
    provider = Provider()
    provider.run["event"] = "workflow_dispatch"
    with pytest.raises(Hold, match="scheduled run identity"):
        observe(provider)


def test_same_attempt_binding_and_green_requires_complete_receipt(monkeypatch):
    provider = Provider()
    monkeypatch.setattr(
        shadow,
        "verify_artifact",
        lambda *args: {"id": 3, "digest": "sha256:" + "a" * 64},
    )
    assert observe(provider)["status"] == "green"
    provider.job["run_attempt"] = 1
    assert observe(provider)["status"] == "incomplete"


def test_pending_run_cannot_claim_green():
    provider = Provider()
    provider.run.update(status="in_progress", conclusion=None)
    provider.job.update(status="queued", conclusion=None)
    assert observe(provider)["status"] == "pending"


def test_collection_and_phase_outcomes_must_match():
    node = "tests/test_fixture.py::test_one"
    report = {
        "schema": "aitm.pytest-evidence/v1",
        "exit_code": 0,
        "deselected": [],
        "collected": [node],
        "reports": [
            {"nodeid": node, "when": phase, "outcome": "passed", "wasxfail": False}
            for phase in ("setup", "call", "teardown")
        ],
    }
    collected = {**report, "reports": []}
    assert shadow.profile(collected, report, {}) == {node: "passed"}
    with pytest.raises(Hold, match="inventory"):
        shadow.profile({**collected, "collected": []}, report, {})
    with pytest.raises(Hold, match="outcomes"):
        shadow.profile(collected, {**report, "reports": report["reports"][:-1]}, {})


def observe(provider, **kwargs):
    return shadow.inspect(provider, now=datetime.fromisoformat(START), **kwargs)


def test_old_rerun_cannot_supply_missed_current_slot():
    provider = Provider()
    provider.run["created_at"] = "2026-11-13T03:00:00Z"
    assert (
        shadow.inspect(provider, now=datetime.fromisoformat("2026-11-14T04:03:00Z"))[
            "status"
        ]
        == "incomplete"
    )


def test_scheduled_shadow_warning_and_explicit_infrastructure_recovery(
    tmp_path, monkeypatch
):
    from ci_incident import DirectorySink, Store
    from ci_recovery import acknowledge, confirm_infrastructure, reconcile

    provider = Provider()
    missing = shadow.incident_observation(observe(provider))
    store = Store(tmp_path / "shadow.db", "shadow")
    assert store.observe(missing) == "warning"
    sink = DirectorySink(tmp_path / "operator")
    assert store.deliver(sink) == 1
    assert "Pause ordinary trunk work" in next(sink.directory.glob("*.md")).read_text()
    confirm_infrastructure(
        store,
        1,
        "shadow-operator",
        "Timed artifact recovery",
        now=datetime.fromisoformat("2026-11-14T03:27:00Z"),
    )
    provider.run["run_attempt"] = provider.job["run_attempt"] = 3
    provider.run["run_started_at"] = provider.job["started_at"] = "2026-11-14T03:29:00Z"
    provider.job["completed_at"] = "2026-11-14T03:31:00Z"
    document = provider.document
    monkeypatch.setattr(
        provider,
        "document",
        lambda path: document(path.replace("/attempts/3", "/attempts/2")),
    )
    monkeypatch.setattr(
        shadow,
        "verify_artifact",
        lambda *args: {"id": 3, "digest": "sha256:" + "a" * 64},
    )
    green = shadow.incident_observation(observe(provider))
    token = reconcile(store, 1, green)
    assert token and store.status()["incident"]["active"]
    assert acknowledge(store, 1, "shadow-operator", token, green)
    assert not store.status()["incident"]["active"]


def test_diagnostic_dispatch_cannot_feed_scheduled_incident(monkeypatch):
    provider = Provider()
    provider.run["event"] = "workflow_dispatch"
    monkeypatch.setattr(shadow, "verify_artifact", lambda *args: {"id": 3})
    diagnostic = observe(provider, event="workflow_dispatch")
    assert diagnostic["status"] == "green"
    with pytest.raises(Hold, match="unavailable"):
        shadow.incident_observation(diagnostic)


def test_older_run_on_previous_sha_does_not_hide_missed_slot():
    provider = Provider()
    provider.branch = "b" * 40
    provider.run["created_at"] = "2026-11-13T03:18:00Z"
    after_grace = datetime.fromisoformat("2026-11-14T04:03:00Z")
    assert shadow.inspect(provider, now=after_grace)["status"] == "incomplete"


def test_unregistered_job_can_still_be_pending(monkeypatch):
    provider = Provider()
    provider.run.update(status="queued", conclusion=None)
    pages = provider.pages
    monkeypatch.setattr(
        provider,
        "pages",
        lambda endpoint, key: [] if key == "jobs" else pages(endpoint, key),
    )
    assert observe(provider)["status"] == "pending"


def test_canonical_creation_drift_during_readback_prevents_green(monkeypatch):
    provider = Provider()
    pages = provider.pages
    reads = iter(("2026-11-14T03:18:00Z", "2026-11-14T03:19:00Z"))

    def drift(endpoint, key):
        if key == "workflow_runs":
            return [{**provider.run, "created_at": next(reads)}]
        return pages(endpoint, key)

    monkeypatch.setattr(provider, "pages", drift)
    monkeypatch.setattr(shadow, "verify_artifact", lambda *args: {"id": 3})
    assert observe(provider)["status"] == "stale"
