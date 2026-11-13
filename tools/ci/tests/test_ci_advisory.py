import json
import sys
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ci_advisory as ci  # noqa: E402
from verify_pr import Hold  # noqa: E402

SHA = "a" * 40
START = "2026-11-13T09:00:00Z"
END = "2026-11-13T09:01:00Z"
RUN = {
    "id": 50,
    "run_number": 10,
    "run_attempt": 2,
    "workflow_id": ci.WORKFLOW_ID,
    "path": ci.WORKFLOW,
    "head_branch": ci.TARGET,
    "head_sha": SHA,
    "repository": {"id": ci.REPOSITORY_ID},
    "head_repository": {"id": ci.REPOSITORY_ID},
    "event": "push",
    "check_suite_id": 51,
    "created_at": START,
    "updated_at": END,
    "run_started_at": START,
    "status": "completed",
    "conclusion": "success",
}
APP = {"id": 15368, "slug": "github-actions"}
SUITE = {
    "id": 51,
    "app": APP,
    "head_sha": SHA,
    "head_branch": ci.TARGET,
    "status": "completed",
    "conclusion": "success",
}


class Provider:
    def __init__(self):
        self.latest = deepcopy(RUN)
        self.attempt = deepcopy(RUN)
        self.jobs = [
            {
                "name": name,
                "id": number,
                "run_id": 50,
                "run_attempt": 2,
                "head_sha": SHA,
                "started_at": START,
                "completed_at": END,
                "status": "completed",
                "conclusion": "success",
            }
            for number, name in enumerate(sorted(ci.REQUIRED), 101)
        ]
        self.suite = deepcopy(SUITE)
        self.branch = SHA
        self.branch_reads = 0
        self.change_on_readback = False
        self.check_overrides = {}

    def document(self, endpoint):
        if endpoint == "":
            return {"id": ci.REPOSITORY_ID, "full_name": ci.REPO}
        if endpoint == "branches/trunk":
            self.branch_reads += 1
            sha = (
                "b" * 40
                if self.change_on_readback and self.branch_reads > 1
                else self.branch
            )
            return {"name": "trunk", "protected": True, "commit": {"sha": sha}}
        if endpoint == "actions/workflows/ci.yml":
            return {"id": ci.WORKFLOW_ID, "path": ci.WORKFLOW, "state": "active"}
        if endpoint == "actions/runs/50/attempts/2":
            return self.attempt
        if endpoint == "check-suites/51":
            return self.suite
        if endpoint.startswith("check-runs/"):
            number = int(endpoint.split("/")[-1])
            job = next(job for job in self.jobs if job["id"] == number)
            return {
                **job,
                "check_suite": {"id": 51},
                "app": APP,
                **self.check_overrides.get(number, {}),
            }
        raise AssertionError(endpoint)

    def pages(self, endpoint, key):
        if key == "workflow_runs":
            assert f"head_sha={SHA}" in endpoint
            return [self.latest]
        if key == "jobs":
            return self.jobs
        if key == "artifacts":
            return []
        raise AssertionError(endpoint)


@pytest.fixture
def provider(monkeypatch):
    fake = Provider()
    monkeypatch.setattr(
        ci,
        "verify_push_artifact",
        lambda *_: {"id": 300, "digest": "sha256:" + "b" * 64},
    )
    return fake


def test_green_requires_exact_current_attempt(provider):
    actual = ci.observe(provider, expected=(50, 2))
    assert actual["status"] == "green"
    assert actual["run_id"] == 50 and actual["attempt"] == 2
    assert set(actual["jobs"]) == ci.REQUIRED
    assert actual["artifact"]["id"] == 300
    assert provider.branch_reads == 2


@pytest.mark.parametrize("expected", [(49, 2), (50, 1)])
def test_delayed_attempt_is_stale(provider, expected):
    assert ci.observe(provider, expected=expected)["status"] == "stale"


def test_moving_trunk_invalidates_green(provider):
    provider.change_on_readback = True
    assert ci.observe(provider)["status"] == "stale"


def test_pending_does_not_look_like_green(provider):
    for record in (provider.latest, provider.attempt, provider.suite):
        record.update(status="in_progress", conclusion=None)
    assert ci.observe(provider)["status"] == "pending"


def test_authenticated_failure_survives_missing_job_and_artifact(provider, monkeypatch):
    provider.jobs = [job for job in provider.jobs if job["name"] != "quality"]
    next(job for job in provider.jobs if job["name"] == "python")["conclusion"] = (
        "failure"
    )

    def missing(*_):
        raise Hold("python artifact unavailable")

    monkeypatch.setattr(ci, "verify_push_artifact", missing)
    actual = ci.observe(provider)
    assert actual["status"] == "red"
    assert actual["failures"] == ["python:failure"]
    assert "quality:missing-or-duplicate" in actual["gaps"]


def test_green_jobs_without_artifact_is_incomplete(provider, monkeypatch):
    def missing(*_):
        raise Hold("python artifact unavailable")

    monkeypatch.setattr(ci, "verify_push_artifact", missing)
    actual = ci.observe(provider)
    assert actual["status"] == "incomplete"
    assert actual["gaps"] == ["python artifact unavailable"]


def test_unbound_check_cannot_supply_failure(provider):
    job = provider.jobs[0]
    job["conclusion"] = "failure"
    provider.check_overrides[job["id"]] = {"check_suite": {"id": 999}}
    actual = ci.observe(provider)
    assert actual["status"] == "incomplete"
    assert actual["failures"] == []


@pytest.mark.parametrize(
    "field,value", [("head_branch", "planning"), ("workflow_id", 999)]
)
def test_wrong_run_identity_holds(provider, field, value):
    provider.latest[field] = value
    with pytest.raises(Hold, match="canonical run"):
        ci.observe(provider)


def archive(members):
    data = BytesIO()
    with ZipFile(data, "w") as output:
        for name, content in members.items():
            output.writestr(name, content)
    return data.getvalue()


def test_archive_reader_requires_exact_members():
    members = {name: json.dumps({"value": name}) for name in ci.ARTIFACT_MEMBERS}
    data = archive(members)
    assert set(ci.read_push_archive(data)) == ci.ARTIFACT_MEMBERS - {
        "product-junit.xml"
    }
    members["../extra.json"] = "{}"
    with pytest.raises(Hold, match="archive members"):
        ci.read_push_archive(archive(members))


def test_artifact_digest_and_attempt_binding(monkeypatch):
    provider = Provider()
    payload = b"wrong"
    name = "aitm-ci-python-a2"
    item = {
        "name": name,
        "id": 7,
        "expired": False,
        "size_in_bytes": len(payload),
        "digest": "sha256:" + sha256(b"other").hexdigest(),
        "created_at": END,
        "workflow_run": {
            "id": 50,
            "repository_id": ci.REPOSITORY_ID,
            "head_repository_id": ci.REPOSITORY_ID,
            "head_branch": ci.TARGET,
            "head_sha": SHA,
        },
    }
    monkeypatch.setattr(provider, "pages", lambda *_: [item])
    monkeypatch.setattr(provider, "api", lambda *_args, **_kw: payload, raising=False)
    jobs = {"python": {"started_at": START}, "collect-evidence": {"completed_at": END}}
    with pytest.raises(Hold, match="archive digest"):
        ci.verify_push_artifact(provider, RUN, jobs)
    item["name"] = "aitm-ci-python-a1"
    with pytest.raises(Hold, match="current attempt"):
        ci.verify_push_artifact(provider, RUN, jobs)


@pytest.mark.parametrize("failed", [True, False])
def test_readback_failure_retains_authenticated_observation(provider, failed):
    if failed:
        provider.jobs[0]["conclusion"] = "failure"
    document = provider.document

    def lost_readback(endpoint):
        if endpoint == "branches/trunk" and provider.branch_reads == 1:
            raise Hold("branch read unavailable")
        return document(endpoint)

    provider.document = lost_readback
    actual = ci.observe(provider)
    assert actual["status"] == ("red" if failed else "incomplete")
    assert actual["current_verified"] is False
    assert actual["failures"] == (
        [f"{provider.jobs[0]['name']}:failure"] if failed else []
    )
    assert actual["jobs"][provider.jobs[0]["name"]] == provider.jobs[0]["id"]


def test_exact_attempt_endpoint_change_prevents_green(provider):
    document = provider.document

    def changed_attempt(endpoint):
        row = document(endpoint)
        if endpoint == "actions/runs/50/attempts/2" and provider.branch_reads == 2:
            return {**row, "status": "in_progress", "conclusion": None}
        return row

    provider.document = changed_attempt
    actual = ci.observe(provider)
    assert actual["status"] == "stale"
    assert actual["current_verified"] is False


def test_malformed_sibling_keeps_red(provider):
    provider.jobs[0]["conclusion"] = "failure"
    provider.jobs += [None, {"name": "quality", "id": [5]}]
    actual = ci.observe(provider, shadow=True)
    assert actual["provenance"] == "shadow"
    assert actual["status"] == "red"
    assert actual["failures"] == [f"{provider.jobs[0]['name']}:failure"]
    assert "invalid push job record" in actual["gaps"]


def test_rerun_record_can_be_created_after_its_start(provider):
    provider.attempt["created_at"] = "2026-11-13T09:00:01Z"
    assert ci.observe(provider)["status"] == "green"
