import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ci_advisory as ci  # noqa: E402
import ci_incident as incident  # noqa: E402


def decision(sequence=3, attempt=1, status="red", failures=None, verified=True):
    return {
        "schema": "aitm.ci-advisory/v1",
        "repository_id": ci.REPOSITORY_ID,
        "workflow_id": ci.WORKFLOW_ID,
        "target": ci.TARGET,
        "provenance": "shadow",
        "sha": f"{sequence:040x}",
        "status": status,
        "current_verified": verified,
        "run_id": 100 + sequence,
        "run_number": sequence,
        "attempt": attempt,
        "started_at": "2026-11-13T09:00:00Z",
        "failures": ["python:failure"]
        if failures is None and status == "red"
        else failures or [],
        "gaps": [] if verified else ["readback unavailable"],
    }


def test_readback_failure_is_retained_until_confirmed(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    assert store.observe(decision(verified=False)) == "unverified"
    assert store.status()["incident"] is None
    assert store.observe(decision(status="incomplete")) == "warning"
    state = store.status()["incident"]
    assert state["active"] and state["failures"] == ["python:failure"]


def test_restart_after_write_and_before_acknowledgment(tmp_path):
    database = tmp_path / "warnings.db"
    store = incident.Store(database, "shadow")
    store.observe(decision())
    sink = incident.DirectorySink(tmp_path / "operator")

    def lose_response(name, content):
        sink(name, content)
        raise OSError("lost acknowledgment")

    with pytest.raises(OSError, match="lost acknowledgment"):
        store.deliver(lose_response, directory=sink.directory)
    [path] = sink.directory.glob("*.md")
    written = path.read_bytes()
    assert b"Pause ordinary trunk work" in written
    assert b"nominate one repair owner" in written

    restarted = incident.Store(database, "shadow")
    assert restarted.deliver(sink) == 1
    assert restarted.deliver(sink) == 0
    assert list(sink.directory.glob("*.md")) == [path]
    assert path.read_bytes() == written


def test_same_attempt_preserves_all_failures_without_duplicate_warning(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    sink = incident.DirectorySink(tmp_path / "operator")
    assert store.observe(decision()) == "warning"
    assert store.deliver(sink) == 1
    assert store.observe(decision(failures=["file-checks:failure"])) == "updated"
    assert store.observe(decision(status="incomplete")) == "duplicate"
    assert store.deliver(sink) == 1
    [path] = sink.directory.glob("*.md")
    assert "file-checks:failure, python:failure" in path.read_text()


def test_newer_pending_revokes_nomination_and_rejects_old_green(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    store.observe(decision())
    v = store.status()["incident"]["version"]
    store.nominate(v, "repairer", 12)
    assert store.observe(decision(sequence=4, status="pending")) == "pending"
    active = store.status()["incident"]
    assert active["version"] > v and active["nomination"] is None
    assert store.observe(decision(status="green")) == "stale"
    with pytest.raises(ValueError, match="version"):
        store.nominate(v, "repairer", 12)


def test_competing_nominations_keep_exactly_one(tmp_path):
    db = tmp_path / "warnings.db"
    store = incident.Store(db, "shadow")
    store.observe(decision())
    version = store.status()["incident"]["version"]

    def nominate(owner):
        try:
            incident.Store(db, "shadow").nominate(version, owner, None)
        except ValueError:
            return False
        return True

    with ThreadPoolExecutor(max_workers=2) as workers:
        assert sorted(workers.map(nominate, ["one", "two"])) == [False, True]
    assert store.status()["incident"]["nomination"]["owner"] in {"one", "two"}


def test_shadow_cannot_enter_live_store(tmp_path):
    db = tmp_path / "warnings.db"
    store = incident.Store(db, "live")
    with pytest.raises(ValueError, match="provenance"):
        store.observe(decision())
    with pytest.raises(ValueError, match="provenance"):
        incident.Store(db, "shadow")


def test_repeated_pending_does_not_change_incident_version(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    store.observe(decision())
    pending = decision(sequence=4, status="pending")
    assert store.observe(pending) == "pending"
    first = store.status()
    assert store.observe(pending) == "duplicate"
    assert store.status() == first


def test_incorrect_delivery_ack_remains_pending(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    store.observe(decision())
    with pytest.raises(ValueError, match="digest agrees|digest disagrees"):
        store.deliver(lambda *_: "wrong", directory=tmp_path / "operator")
    [warning] = store.status()["warnings"]
    assert warning["delivered"] is None


def test_verified_pending_target_without_a_run_revokes_nomination(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    store.observe(decision())
    version = store.status()["incident"]["version"]
    store.nominate(version, "repairer", 12)
    pending = decision(sequence=4, status="pending")
    del pending["run_id"]
    assert store.observe(pending) == "pending"
    state = store.status()
    assert state["pending_sha"] == pending["sha"]
    assert state["incident"]["nomination"] is None
    assert store.observe(decision()) == "stale"


def test_stale_failures_are_retained_without_reopening_incident(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    assert store.observe(decision(sequence=4, status="green")) == "green"
    assert store.observe(decision(sequence=3)) == "stale"
    with store.transaction() as db:
        [row] = db.execute("SELECT body FROM attempts WHERE run_number=3").fetchone()
    assert "python:failure" in row
    assert store.status()["incident"] is None


def test_bound_sink_revalidates_and_has_separate_provenance(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    store.observe(decision())
    sink = incident.DirectorySink(tmp_path / "operator")
    assert store.deliver(sink) == 1
    [path] = sink.directory.glob("shadow-*.md")
    path.unlink()
    assert store.deliver(sink) == 1
    assert path.is_file()
    with pytest.raises(ValueError, match="bound operator surface"):
        store.deliver(incident.DirectorySink(tmp_path / "elsewhere"))
    live = incident.Store(tmp_path / "live.db", "live")
    live.observe({**decision(), "provenance": "live"})
    assert live.deliver(sink) == 1
    assert len(list(sink.directory.glob("*.md"))) == 2


def test_flush_only_current_warning_with_explicit_prior_failure(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    sink = incident.DirectorySink(tmp_path / "operator")
    store.observe(decision())
    store.observe(decision(sequence=4, status="incomplete"))
    assert store.deliver(sink) == 1
    [warning] = sink.directory.glob("*.md")
    assert "Run 104" in warning.read_text()
    assert "Prior authenticated failures: python:failure" in warning.read_text()


def test_existing_public_directory_is_rejected(tmp_path):
    store = incident.Store(tmp_path / "warnings.db", "shadow")
    store.observe(decision())
    path = tmp_path / "public"
    path.mkdir()
    path.chmod(0o755)
    with pytest.raises(ValueError, match="private owned directory"):
        store.deliver(incident.DirectorySink(path))
