import sys
from copy import deepcopy
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scheduled_sweep_flag as flag  # noqa: E402
from verify_pr import Hold  # noqa: E402

START = "2026-11-21T04:02:12Z"
END = "2026-11-21T04:07:11Z"
SHA = "a" * 40
BINDING = {
    "issue_number": 999,
    "issue_id": 1000,
    "activation_floor": 4,
}


def attempt(number, conclusion, *, run_id=None, sha=SHA, status="completed"):
    return {
        "id": run_id or 1100000 + number,
        "run_number": number,
        "run_attempt": 1,
        "workflow_id": flag.WORKFLOW_ID,
        "path": flag.WORKFLOW,
        "event": "schedule",
        "head_branch": "trunk",
        "head_sha": sha,
        "repository": {"id": flag.REPO_ID},
        "head_repository": {"id": flag.REPO_ID},
        "check_suite_id": 50,
        "status": status,
        "conclusion": conclusion,
        "created_at": START,
        "run_started_at": START,
        "updated_at": END,
    }


def decision(run, state):
    return {
        "schema": flag.SCHEMA,
        "state": state,
        "run": {
            "repository_id": flag.REPO_ID,
            "workflow_id": flag.WORKFLOW_ID,
            "run_id": run["id"],
            "run_number": run["run_number"],
            "run_attempt": 1,
            "head_sha": run["head_sha"],
            "conclusion": run["conclusion"],
            "result_at": END,
        },
    }


class Provider:
    def __init__(self, *runs):
        self.runs = {run["id"]: run for run in runs}
        self.listed = deepcopy(list(runs))
        self.paths = []
        self.workflow_blob = flag.WORKFLOW_BLOB
        self.job_passing = True
        self.app = {"slug": "github-actions", "id": 12}
        self.attempt_error = set()
        self.history_reads = 0
        self.job = {
            "id": 60,
            "name": "reconcile",
            "run_attempt": 1,
            "status": "completed",
            "conclusion": "success",
            "started_at": START,
            "completed_at": END,
        }

    def document(self, path):
        self.paths.append(path)
        if not path:
            return {
                "id": flag.REPO_ID,
                "full_name": flag.REPO,
                "default_branch": "trunk",
            }
        if path == f"actions/workflows/{flag.WORKFLOW_ID}":
            return {"id": flag.WORKFLOW_ID, "path": flag.WORKFLOW, "state": "active"}
        if path.endswith("per_page=1"):
            return {"total_count": len(self.listed)}
        if "/attempts/" in path:
            run_id = int(path.split("/")[2])
            if run_id in self.attempt_error:
                raise Hold("attempt unavailable")
            return deepcopy(self.runs[run_id])
        if path.startswith("contents/"):
            return {"sha": self.workflow_blob, "type": "file"}
        if path == "check-suites/50":
            return {"id": 50, "head_sha": SHA, "head_branch": "trunk", "app": self.app}
        if path == "check-runs/60":
            return dict(self.job, head_sha=SHA, app=self.app, check_suite={"id": 50})
        raise AssertionError(path)

    def optional_attempt(self, run_id):
        if run_id in self.attempt_error:
            raise Hold("cached attempt unavailable")
        return deepcopy(self.runs.get(run_id))

    def pages(self, path, key):
        self.paths.append(path)
        if key == "workflow_runs":
            self.history_reads += 1
            return deepcopy(self.listed)
        run_id = int(path.split("/")[2])
        if not self.job_passing:
            return []
        return [dict(self.job, run_id=run_id, head_sha=SHA)]


class Store:
    def __init__(self, record=None, editor_id=41898282):
        self.record = record
        self.editor_id = editor_id if record else None
        self.writes = []
        self.fail_before = False
        self.fail_after = False

    def read(self):
        return flag.Snapshot(
            flag.render_body(self.record), None, self.editor_id, self.record
        )

    def write(self, body):
        self.writes.append(body)
        if self.fail_before:
            self.fail_before = False
            raise Hold("ambiguous")
        self.record = flag.parse_body(body)
        self.editor_id = 41898282
        if self.fail_after:
            raise Hold("ambiguous")


def test_failure_refresh_clear_and_replayed_notification():
    first, newer, passed = (
        attempt(5, "failure"),
        attempt(7, "timed_out"),
        attempt(8, "success"),
    )
    store = Store()
    assert flag.publish(Provider(first), store) == "active"
    assert store.record == decision(first, "active")
    assert flag.publish(Provider(first, newer), store) == "active"
    assert store.record == decision(newer, "active")
    assert flag.publish(Provider(newer, first, passed), store) == "clear"
    assert store.record == decision(passed, "clear")
    incomplete_index = Provider(first, newer, passed)
    incomplete_index.listed.pop()
    assert flag.publish(incomplete_index, store) == "unchanged"
    assert flag.publish(Provider(passed), store) == "unchanged"
    assert len(store.writes) == 3


def test_manually_rerun_failure_stays_decisive_original_attempt():
    run = attempt(5, "failure")
    github = Provider(run)
    github.listed[0].update(run_attempt=2, conclusion="success")
    store = Store()
    assert flag.publish(github, store) == "active"
    assert store.record == decision(run, "active")
    assert not any("/attempts/2" in path for path in github.paths)


@pytest.mark.parametrize(
    "status,conclusion",
    [("queued", None), ("completed", "cancelled"), ("completed", "neutral")],
)
def test_newer_nondecisive_evidence_keeps_watermark(status, conclusion):
    first = attempt(5, "failure")
    store = Store(decision(first, "active"))
    assert (
        flag.publish(Provider(attempt(8, conclusion, status=status), first), store)
        == "unchanged"
    )
    assert not store.writes


@pytest.mark.parametrize(
    "field,value",
    [
        ("event", "workflow_dispatch"),
        ("workflow_id", 123),
        ("head_branch", "staging"),
        ("head_repository", {"id": 123}),
        ("run_attempt", 2),
        ("conclusion", "unknown"),
    ],
)
def test_invalid_higher_original_attempt_preserves_warning(field, value):
    first, newer = attempt(5, "failure"), attempt(8, "success")
    github = Provider(first, newer)
    github.runs[newer["id"]][field] = value
    store = Store(decision(first, "active"))
    with pytest.raises(Hold):
        flag.publish(github, store)
    assert not store.writes


@pytest.mark.parametrize(
    "defect", ["missing-job", "wrong-blob", "missing-attempt", "wrong-check"]
)
def test_unverified_success_never_clears(defect):
    first, passed = attempt(5, "failure"), attempt(8, "success")
    github = Provider(first, passed)
    if defect == "missing-job":
        github.job_passing = False
    elif defect == "wrong-blob":
        github.workflow_blob = SHA
    elif defect == "missing-attempt":
        github.attempt_error.add(passed["id"])
    else:
        github.app = {"slug": "other", "id": 12}
    store = Store(decision(first, "active"))
    with pytest.raises(Hold):
        flag.publish(github, store)
    assert not store.writes


def test_unstable_listing_stops_before_writing(monkeypatch):
    first, later = attempt(5, "failure"), attempt(8, "success")
    github = Provider(first)
    pages = github.pages

    def changing(path, key):
        github.listed = [first] if github.history_reads % 2 == 0 else [later]
        return pages(path, key)

    monkeypatch.setattr(github, "pages", changing)
    store = Store()
    with pytest.raises(Hold):
        flag.publish(github, store)
    assert not store.writes


@pytest.mark.parametrize("editor_id", [111, 41898282])
def test_edit_cannot_supply_a_result_or_block_the_authentic_decision(editor_id):
    edited = attempt(50, "success")
    actual = attempt(7, "failure")
    store = Store(decision(edited, "clear"), editor_id=editor_id)
    assert flag.publish(Provider(actual), store) == "active"
    assert store.record == decision(actual, "active")
    assert len(store.writes) == 1


def test_authentic_attempt_repairs_a_contradictory_cached_result():
    actual = attempt(5, "failure")
    store = Store(decision(dict(actual, conclusion="success"), "clear"))
    assert flag.publish(Provider(actual), store) == "active"
    assert store.record == decision(actual, "active")


def test_newer_linked_attempt_unavailability_does_not_clear_warning():
    previous, older = attempt(8, "failure"), attempt(5, "success")
    github = Provider(older, previous)
    github.listed.pop()
    github.attempt_error.add(previous["id"])
    store = Store(decision(previous, "active"))
    with pytest.raises(Hold, match="cached attempt unavailable"):
        flag.publish(github, store)
    assert not store.writes


def test_unrelated_cached_link_cannot_block_verified_sweep():
    edited, actual = attempt(50, "success"), attempt(7, "failure")
    github = Provider(actual, dict(edited, event="workflow_dispatch"))
    github.listed.pop()
    store = Store(decision(edited, "clear"))
    assert flag.publish(github, store) == "active"
    assert store.record == decision(actual, "active")


def test_ambiguous_write_readback_and_retry():
    first = attempt(5, "failure")
    landed = Store()
    landed.fail_after = True
    assert flag.publish(Provider(first), landed) == "active"
    assert len(landed.writes) == 1
    delayed = Store()
    delayed.fail_before = True
    github = Provider(first)
    assert flag.publish(github, delayed) == "active"
    assert len(delayed.writes) == 2
    assert github.history_reads == 4


def test_changed_store_before_patch_never_overwrites(monkeypatch):
    store = Store()
    current = store.read
    competing = decision(attempt(7, "failure"), "active")
    reads = iter(
        [current(), flag.Snapshot(flag.render_body(competing), END, 222, competing)]
    )
    monkeypatch.setattr(store, "read", lambda: next(reads))
    with pytest.raises(Hold):
        flag.publish(Provider(attempt(5, "failure")), store)
    assert not store.writes


def test_body_strict_json_round_trip_and_canonical_link():
    record = decision(attempt(5, "failure"), "active")
    body = flag.render_body(record)
    assert flag.parse_body(body) == record
    assert flag.attempt_url(record["run"]) in body
    assert flag.parse_body(flag.render_body(None)) is None
    for malformed in (
        body.replace('"state": "active",', '"state": "active", "state": "active",'),
        body.replace('"run_attempt": 1', '"run_attempt": true'),
        body.replace("sweep failed", "sweep passed"),
        body + "\nextra",
    ):
        with pytest.raises(Hold):
            flag.parse_body(malformed)


def test_issue_identity_bound_and_editor_retained_as_metadata():
    record = decision(attempt(5, "failure"), "active")
    issue = {
        "number": 999,
        "databaseId": 1000,
        "state": "OPEN",
        "title": flag.TITLE,
        "body": flag.render_body(record),
        "lastEditedAt": END,
        "editor": {"__typename": "Bot", "databaseId": 222},
        "author": {"__typename": "User", "databaseId": 111},
    }
    repo = {"nameWithOwner": flag.REPO, "databaseId": flag.REPO_ID, "issue": issue}
    assert flag.validate_snapshot(repo, BINDING).record == record
    with pytest.raises(Hold):
        flag.validate_snapshot(repo, dict(BINDING, issue_id=1))
    issue["editor"] = {"__typename": "User", "databaseId": 111}
    assert flag.validate_snapshot(repo, BINDING).editor_id == 111
    issue["body"] = flag.render_body(None)
    issue.update(lastEditedAt=None, editor=None)
    assert flag.validate_snapshot(repo, BINDING).record is None
    issue["state"] = "CLOSED"
    with pytest.raises(Hold):
        flag.validate_snapshot(repo, BINDING)


def test_patch_only_sends_body_through_the_existing_github_client():
    class GitHub:
        def command(self, args, limit):
            assert args == [
                "api",
                "--hostname",
                "github.com",
                "--method",
                "PATCH",
                "repos/kburson/aitm/issues/999",
                "--raw-field",
                "body=body text",
            ]
            assert limit == 65536
            return b"{}"

    flag.IssueStore(GitHub(), BINDING).write("body text")


def test_capped_history_subdivides_and_deduplicates_boundary(monkeypatch):
    from datetime import timedelta
    from urllib.parse import parse_qs, urlsplit

    start = flag.SCHEDULE_DEPLOYED
    runs = [
        dict(
            attempt(5 + offset, "failure"),
            created_at=flag.utc_string(start + timedelta(seconds=offset)),
        )
        for offset in (1, 2, 3)
    ]

    def in_range(path):
        lower, upper = parse_qs(urlsplit(path).query)["created"][0].split("..")
        return [run for run in runs if lower <= run["created_at"] <= upper]

    class CappedProvider:
        def document(self, path):
            return {"total_count": len(in_range(path))}

        def pages(self, path, key):
            assert key == "workflow_runs"
            return in_range(path)

    monkeypatch.setattr(flag, "HISTORY_CAP", 3)
    actual = flag.history(CappedProvider(), start + timedelta(seconds=4))
    assert list(sorted(actual)) == [6, 7, 8]


def test_same_count_paging_rejects_duplicate_run_identity():
    first = attempt(5, "failure")
    github = Provider(first)
    github.listed = [first, first]
    store = Store()
    with pytest.raises(Hold, match="duplicate or contradictory"):
        flag.publish(github, store)
    assert not store.writes


def test_missing_history_preserves_existing_but_cannot_initialize():
    stored = decision(attempt(5, "failure"), "active")
    store = Store(stored)
    with pytest.raises(Hold, match="no verified sweep result"):
        flag.publish(Provider(), store)
    assert store.record == stored and not store.writes
    with pytest.raises(Hold, match="no verified sweep result"):
        flag.publish(Provider(), Store())


def test_equal_result_after_ambiguous_patch_does_not_retry_a_different_update(
    monkeypatch,
):
    store = Store()
    different = decision(attempt(7, "failure"), "active")

    def write(body):
        store.writes.append(body)
        store.record = different
        raise Hold("ambiguous")

    monkeypatch.setattr(store, "write", write)
    with pytest.raises(Hold, match="changed during publication"):
        flag.publish(Provider(attempt(5, "failure")), store)
    assert store.record == different and len(store.writes) == 1


def test_replacement_binding_cannot_bootstrap_from_pre_recovery_result():
    older = attempt(5, "failure")
    qualifying = attempt(7, "failure")
    store = Store()
    with pytest.raises(Hold, match="no verified sweep result"):
        flag.publish(Provider(older), store, activation_floor=7)
    assert not store.writes
    assert (
        flag.publish(Provider(older, qualifying), store, activation_floor=7) == "active"
    )
    assert store.record == decision(qualifying, "active")


def test_unverified_newer_candidate_preserves_existing_clear_over_older_failure():
    saved = attempt(5, "success")
    failure = attempt(7, "failure")
    unverified = attempt(8, "success")
    store = Store(decision(saved, "clear"))
    github = Provider(saved, failure, unverified)
    github.job_passing = False
    with pytest.raises(Hold, match="lacks one exact reconcile"):
        flag.publish(github, store)
    assert store.record == decision(saved, "clear") and not store.writes


def test_baseline_cannot_be_reinterpreted_as_a_failure():
    floor = attempt(
        4, "failure", run_id=44864075824, sha="8ab84ba0590286d4655ea94e4d9de99f25ea1f2e"
    )
    store = Store()
    with pytest.raises(Hold):
        flag.publish(Provider(floor), store)
    assert not store.writes


@pytest.mark.parametrize(
    "code,body,expected",
    [
        (200, '{"id": 42}', {"id": 42}),
        (404, '{"message": "Not Found"}', None),
        (403, '{"message": "Forbidden"}', "hold"),
    ],
)
def test_cached_attempt_lookup_distinguishes_missing_from_unavailable(
    monkeypatch, code, body, expected
):
    from subprocess import CompletedProcess

    def response(args, **kwargs):
        assert args[-1] == "repos/kburson/aitm/actions/runs/42/attempts/1"
        return CompletedProcess(
            args, int(code != 200), f"HTTP/2.0 {code} Status\n\n{body}"
        )

    monkeypatch.setattr(flag.subprocess, "run", response)
    github = flag.SweepGitHub(flag.REPO)
    if expected == "hold":
        with pytest.raises(Hold, match="cached attempt unavailable"):
            github.optional_attempt(42)
    else:
        assert github.optional_attempt(42) == expected
