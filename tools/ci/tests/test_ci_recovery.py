import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ci_incident as incidents  # noqa: E402
import ci_recovery as recovery  # noqa: E402
from test_ci_incident import decision  # noqa: E402

WHEN = "2026-11-13T09:01:00Z"
NOW = datetime.fromisoformat(WHEN)
REPAIR = "6" * 40


def green(sequence=4, *, sha=None, started="2026-11-13T09:02:00Z"):
    result = decision(sequence=sequence, status="green")
    result["sha"] = sha or result["sha"]
    result["started_at"] = started
    result["artifact"] = {
        "id": 1,
        "digest": "sha256:" + "a" * 64,
        "policy_result": {"passed": True},
    }
    return result


@pytest.fixture
def store(tmp_path):
    return incidents.Store(tmp_path / "incidents.db", "shadow")


def test_infrastructure_only_requires_fresh_same_sha_and_manual_ack(store):
    initial = decision(status="incomplete")
    store.observe(initial)
    recovery.confirm_infrastructure(
        store, 1, "operator", "GitHub artifact outage", now=NOW
    )
    assert recovery.reconcile(store, 1, green(sha=initial["sha"], started=WHEN)) is None
    assert store.status()["incident"]["active"]
    current = green(sequence=5, sha=initial["sha"])
    token = recovery.reconcile(store, 1, current)
    assert token and store.status()["incident"]["active"]
    recovery.acknowledge(store, 1, "operator", token, current)
    state = store.status()["incident"]
    assert not state["active"]
    assert state["acknowledgment"]["operator"] == "operator"
    assert recovery.reconcile(store, 1, current) is None
    assert not store.status()["incident"]["active"]


def test_known_failure_excludes_infrastructure_recovery(store):
    store.observe(decision())
    with pytest.raises(ValueError, match="infrastructure"):
        recovery.confirm_infrastructure(store, 1, "operator", "outage", now=NOW)


def test_nominated_repair_needs_exact_current_green_and_ack(store):
    store.observe(decision())
    store.nominate(1, "repairer", 22)
    repair = {"pr": 22, "sha": REPAIR, "landed_at": WHEN, "receipt": "a" * 64}
    token = recovery.reconcile(store, 1, green(sha=REPAIR), repair=repair)
    assert token and store.status()["incident"]["active"]
    assert recovery.acknowledge(
        store, 1, "operator", token, green(sha=REPAIR), repair=repair
    )
    assert store.status()["incident"]["acknowledgment"]["repair"]["pr"] == 22


def test_rollback_invalidates_recovery_without_acknowledging(store):
    original = decision()
    store.observe(original)
    store.nominate(1, "repairer", 22)
    repair = {"pr": 22, "sha": REPAIR, "landed_at": WHEN, "receipt": "a" * 64}
    token = recovery.reconcile(store, 1, green(sha=REPAIR), repair=repair)
    assert token
    rollback = green(5, sha=original["sha"])
    assert not recovery.acknowledge(
        store, 1, "operator", token, rollback, repair=repair
    )
    assert store.status()["incident"]["active"]
    assert store.status()["incident"]["recovery"] is None


def test_new_red_revokes_old_ack_even_when_attempt_is_repeated(store):
    store.observe(decision(status="incomplete"))
    sha = decision()["sha"]
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    token = recovery.reconcile(store, 1, green(sha=sha))
    repeated_red = decision(5)
    for _ in range(2):
        assert not recovery.acknowledge(store, 1, "operator", token, repeated_red)
    active = store.status()["incident"]
    assert active["active"] and active["recovery"] is None and active["failures"]


def test_acknowledgment_survives_later_independent_incident(store):
    starting = decision(status="incomplete")
    store.observe(starting)
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    observed = green(sha=starting["sha"])
    token = recovery.reconcile(store, 1, observed)
    assert recovery.acknowledge(store, 1, "operator", token, observed)
    assert store.observe(decision(5, status="incomplete")) == "warning"
    assert store.status()["incident"]["active"]
    with store.transaction() as db:
        assert db.execute("SELECT version FROM acknowledgments").fetchall() == [(1,)]


def test_provider_loss_revokes_proof_and_requires_new_check(store):
    initial = decision(status="incomplete")
    store.observe(initial)
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    current = green(sha=initial["sha"])
    token = recovery.reconcile(store, 1, current)
    assert token
    assert not recovery.acknowledge(store, 1, "operator", token, None)
    assert store.status()["incident"]["recovery"] is None
    assert not recovery.acknowledge(store, 1, "operator", token, current)
    assert store.status()["incident"]["active"]


def test_late_authenticated_failure_prevents_same_sha_infrastructure_recovery(store):
    initial = decision(status="incomplete")
    store.observe(initial)
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    current = green(sha=initial["sha"])
    token = recovery.reconcile(store, 1, current)
    assert token
    assert store.observe(decision(verified=False)) == "stale"
    assert not recovery.acknowledge(store, 1, "operator", token, current)
    assert store.status()["incident"]["active"]


def test_ack_does_not_restore_a_revoked_token(store):
    initial = decision(status="incomplete")
    store.observe(initial)
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    current = green(sha=initial["sha"])
    token = recovery.reconcile(store, 1, current)
    assert token
    assert not recovery.acknowledge(store, 1, "operator", token, None)
    for _ in range(2):
        assert not recovery.acknowledge(store, 1, "operator", token, current)
        assert store.status()["incident"]["recovery"] is None


def test_ack_binds_artifact_id_and_start_time(store):
    initial = decision(status="incomplete")
    store.observe(initial)
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    current = green(sha=initial["sha"])
    token = recovery.reconcile(store, 1, current)
    assert token
    current["artifact"]["id"] += 1
    assert not recovery.acknowledge(store, 1, "operator", token, current)


def test_fresh_check_after_evidence_loss_issues_new_token(store):
    initial = decision(status="incomplete")
    store.observe(initial)
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    current = green(sha=initial["sha"])
    discarded = recovery.reconcile(store, 1, current)
    assert not recovery.acknowledge(store, 1, "operator", discarded, None)
    fresh = recovery.reconcile(store, 1, current)
    assert fresh and fresh != discarded
    assert not recovery.acknowledge(store, 1, "operator", discarded, current)
    assert recovery.acknowledge(store, 1, "operator", fresh, current)


def test_unverified_newer_failure_revokes_persisted_recovery(store):
    initial = decision(status="incomplete")
    store.observe(initial)
    recovery.confirm_infrastructure(store, 1, "operator", "artifact outage", now=NOW)
    current = green(sha=initial["sha"])
    token = recovery.reconcile(store, 1, current)
    assert token
    assert store.observe(decision(sequence=5, verified=False)) == "unverified"
    assert store.status()["incident"]["recovery"] is None
    assert not recovery.acknowledge(store, 1, "operator", token, current)
