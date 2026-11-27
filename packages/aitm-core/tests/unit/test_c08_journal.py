"""Verify durable C08 evidence against fixed ref facts without Git or disk."""

import json
from dataclasses import replace

import pytest

from aitm_core.models.common import RefObservation
from aitm_core.store import fetch
from aitm_core.store.continuity import ContinuityStatus, SharedFrontier
from aitm_core.store.fetch import RefreshPolicy, _ContinuityStore, _JournalEntry
from aitm_core.store.objects import Repository
from tests.support.c07 import PLANNING, installation

ROOT = "1" * 40
CODE = "2" * 40
FIRST = "3" * 40
NEXT = "4" * 40
OTHER = "5" * 40
REMOTE = "planning-remote"


class RepositoryFacts:
    ref = PLANNING
    oid_length = 40
    _oid = Repository._oid

    def _git(self, *args):
        if args[0] == "check-ref-format":
            return b""
        assert args == ("rev-parse", "--path-format=absolute", "--git-common-dir")
        return b"/fixture/git-common\n"


class JournalBytes:
    def __init__(self, payload):
        self.payload = payload

    def read_bytes(self):
        if self.payload is None:
            raise FileNotFoundError
        return self.payload


@pytest.fixture
def store():
    anchor = installation(RepositoryFacts(), ROOT)
    anchor = replace(
        anchor, store=anchor.store.model_copy(update={"planning_remote": REMOTE})
    )
    return _ContinuityStore(RefreshPolicy(anchor))


def entry(store, *, previous=None, before=ROOT, after=FIRST):
    observation = RefObservation(ref=PLANNING, remote=REMOTE, observed_commit=after)
    return _JournalEntry(
        route=store.route,
        previous=previous,
        frontier=SharedFrontier(
            ContinuityStatus.VERIFIED, after, after, observation, True
        ),
        writer_before=before,
        writer_after=after,
        code=CODE,
    )


def encoded(entry):
    return entry.model_dump_json().encode() + b"\n"


@pytest.fixture
def persisted(store, monkeypatch):
    def load(payload, *, marker=None, checkpoint=None, valid=None):
        refs = {
            store.marker_ref: marker,
            store.checkpoint_ref: checkpoint,
            store.valid_ref: valid,
        }

        def read_ref(repo, name):
            assert repo is store.repository
            return refs[name]

        monkeypatch.setattr(store, "journal", JournalBytes(payload))
        monkeypatch.setattr(fetch, "_direct_ref", read_ref)
        return store.read()

    return load


def test_confirmed_marker_and_both_refs_identify_accepted_entry(store, persisted):
    accepted = entry(store)
    raw = encoded(accepted)
    marker = store._oid(raw)
    journal = persisted(raw, marker=marker, checkpoint=FIRST, valid=FIRST)
    assert journal.accepted == accepted
    assert journal.marker == marker
    assert journal.pending is None
    assert journal.pending_marker is None


def test_first_uncommitted_record_does_not_establish_shared_history(store, persisted):
    pending = entry(store)
    raw = encoded(pending)
    journal = persisted(raw)
    assert journal.accepted is None
    assert journal.marker is None
    assert journal.pending == pending
    assert journal.pending_marker == store._oid(raw)


def test_one_uncommitted_tail_preserves_last_accepted_entry(store, persisted):
    accepted = entry(store)
    first = encoded(accepted)
    marker = store._oid(first)
    pending = entry(store, previous=marker, before=FIRST, after=NEXT)
    second = encoded(pending)
    journal = persisted(first + second, marker=marker, checkpoint=FIRST, valid=FIRST)
    assert journal.accepted == accepted
    assert journal.marker == marker
    assert journal.pending == pending
    assert journal.pending_marker == store._oid(second)


def test_two_uncommitted_records_cannot_be_inferred_as_recovery(store, persisted):
    first = encoded(entry(store))
    marker = store._oid(first)
    second = encoded(entry(store, previous=marker, before=FIRST, after=NEXT))
    third = encoded(entry(store, previous=store._oid(second), before=NEXT, after=OTHER))
    with pytest.raises(ValueError, match="marker disagrees with its append history"):
        persisted(first + second + third, marker=marker, checkpoint=FIRST, valid=FIRST)


def test_retained_checkpoint_with_missing_journal_is_integrity_hold(persisted):
    with pytest.raises(
        ValueError, match="journal is missing while retained refs exist"
    ):
        persisted(None, checkpoint=FIRST)


def test_partial_tail_cannot_be_discarded_to_reuse_last_confirmed_entry(
    store, persisted
):
    first = encoded(entry(store))
    marker = store._oid(first)
    with pytest.raises(ValueError, match="partial record"):
        persisted(first + b'{"route":', marker=marker, checkpoint=FIRST, valid=FIRST)


@pytest.mark.parametrize(
    ("overrides", "diagnostic"),
    [
        pytest.param(
            {"checkpoint": OTHER},
            "retained frontier refs disagree",
            id="different-checkpoint-pin",
        ),
        pytest.param(
            {"valid": OTHER},
            "retained frontier refs disagree",
            id="different-valid-content-pin",
        ),
    ],
)
def test_marker_confirmation_cannot_substitute_for_retained_ref_evidence(
    store, persisted, overrides, diagnostic
):
    raw = encoded(entry(store))
    trusted = {"marker": store._oid(raw), "checkpoint": FIRST, "valid": FIRST}
    with pytest.raises(ValueError, match=diagnostic):
        persisted(raw, **(trusted | overrides))


def test_journal_entry_cannot_claim_another_installation_route(store):
    foreign = entry(store).model_copy(update={"route": "wrong-route"})
    with pytest.raises(ValueError, match="journal identity or append order disagrees"):
        store._entry(encoded(foreign), None)


def test_journal_entry_must_bind_exact_predecessor_marker(store):
    old = encoded(entry(store))
    next_entry = entry(store, previous=OTHER, before=FIRST, after=NEXT)
    with pytest.raises(ValueError, match="journal identity or append order disagrees"):
        store._entry(encoded(next_entry), store._oid(old))


@pytest.mark.parametrize(
    "route_change",
    [
        pytest.param({"remote": "code-remote"}, id="other-configured-remote"),
        pytest.param({"ref": "refs/heads/trunk"}, id="other-literal-ref"),
    ],
)
def test_matching_journal_route_does_not_qualify_foreign_remote_observation(
    store, route_change
):
    current = entry(store)
    observation = current.frontier.observation.model_copy(update=route_change)
    foreign = current.model_copy(
        update={"frontier": replace(current.frontier, observation=observation)}
    )
    with pytest.raises(ValueError, match="observation is outside the anchored route"):
        store._entry(encoded(foreign), None)


@pytest.mark.parametrize(
    "field_path",
    [
        pytest.param(("writer_before",), id="prior-local-cas-input"),
        pytest.param(("writer_after",), id="proposed-writer-tip"),
        pytest.param(("code",), id="independent-code-authority"),
        pytest.param(("frontier", "checkpoint"), id="shared-ancestry-checkpoint"),
        pytest.param(("frontier", "valid_tip"), id="prior-content-valid-tip"),
        pytest.param(
            ("frontier", "observation", "observed_commit"),
            id="observed-remote-identity",
        ),
    ],
)
def test_durable_oid_fields_require_full_repository_object_ids(store, field_path):
    current = entry(store, before=FIRST)
    rollback = replace(
        current.frontier,
        status=ContinuityStatus.ROLLBACK,
        valid_tip=ROOT,
        observation=current.frontier.observation.model_copy(
            update={"observed_commit": ROOT}
        ),
    )
    payload = json.loads(encoded(current.model_copy(update={"frontier": rollback})))
    container = payload
    for field in field_path[:-1]:
        container = container[field]
    container[field_path[-1]] = "4" * 39
    with pytest.raises(ValueError, match="expected a full Git object identity"):
        store._entry(json.dumps(payload).encode(), None)


def test_journal_cannot_move_writer_while_shared_continuity_is_fenced(store):
    current = entry(store)
    fenced = replace(
        current.frontier, status=ContinuityStatus.QUARANTINED, valid_tip=ROOT
    )
    attempted = current.model_copy(
        update={"frontier": fenced, "writer_before": OTHER, "writer_after": ROOT}
    )
    with pytest.raises(ValueError, match="unapproved writer transition"):
        store._entry(encoded(attempted), None)


def test_journal_cannot_move_writer_away_from_unpublished_divergence(store):
    current = entry(store)
    diverged = replace(current.frontier, local_diverged=True)
    attempted = current.model_copy(update={"frontier": diverged})
    with pytest.raises(ValueError, match="unapproved writer transition"):
        store._entry(encoded(attempted), None)


def test_verified_entry_cannot_move_writer_to_other_content_tip(store):
    current = entry(store)
    attempted = current.model_copy(update={"writer_after": OTHER})
    with pytest.raises(ValueError, match="unapproved writer transition"):
        store._entry(encoded(attempted), None)


@pytest.mark.parametrize(
    ("status", "witnessed", "checkpoint", "valid_tip"),
    [
        pytest.param(
            ContinuityStatus.VERIFIED,
            NEXT,
            FIRST,
            FIRST,
            id="verified-checkpoint-was-not-observed",
        ),
        pytest.param(
            ContinuityStatus.VERIFIED,
            FIRST,
            FIRST,
            ROOT,
            id="verified-content-tip-does-not-match",
        ),
        pytest.param(
            ContinuityStatus.QUARANTINED,
            NEXT,
            FIRST,
            ROOT,
            id="quarantine-checkpoint-was-not-observed",
        ),
        pytest.param(
            ContinuityStatus.DELETED,
            FIRST,
            FIRST,
            ROOT,
            id="deletion-cannot-name-present-commit",
        ),
        pytest.param(
            ContinuityStatus.STALE,
            FIRST,
            FIRST,
            ROOT,
            id="transport-failure-is-not-durable-remote-observation",
        ),
    ],
)
def test_durable_frontier_requires_a_witness_for_its_claimed_status(
    store, status, witnessed, checkpoint, valid_tip
):
    current = entry(store, before=FIRST)
    frontier = replace(
        current.frontier,
        status=status,
        checkpoint=checkpoint,
        valid_tip=valid_tip,
        observation=RefObservation(
            ref=PLANNING, remote=REMOTE, observed_commit=witnessed
        ),
    )
    with pytest.raises(ValueError, match="continuity journal"):
        store._entry(encoded(current.model_copy(update={"frontier": frontier})), None)


def test_observed_commit_cannot_bind_public_writer_as_private_transport_ref(store):
    observed = entry(store).model_copy(update={"transport_ref": PLANNING})
    with pytest.raises(
        ValueError, match="does not name a private planning candidate ref"
    ):
        store._entry(encoded(observed), None)


def test_confirmed_deletion_cannot_bind_any_transport_object_ref(store):
    current = entry(store, before=FIRST)
    deleted = replace(
        current.frontier,
        status=ContinuityStatus.DELETED,
        observation=current.frontier.observation.model_copy(
            update={"observed_commit": None}
        ),
    )
    forged = current.model_copy(
        update={
            "frontier": deleted,
            "transport_ref": "refs/aitm/candidates/planning-" + "a" * 32,
        }
    )
    with pytest.raises(
        ValueError, match="does not name a private planning candidate ref"
    ):
        store._entry(encoded(forged), None)
