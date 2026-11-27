"""Exercise C08 continuity from independent observations and validation reports."""

from dataclasses import replace

import pytest

from aitm_core.models.common import LocalOutcome, RefObservation, StoreAnchor
from aitm_core.store.continuity import (
    ContinuityAnchor,
    ContinuityStatus,
    SharedFrontier,
    observe_shared,
    unavailable_shared,
)
from aitm_core.store.validation import ValidationReport

ROOT = "genesis"
OLD = "trusted-shared"
NEW = "shared-descendant"
REF = "refs/heads/records"
REMOTE = "shared-remote"


def observed(commit, *, ref=REF, remote=REMOTE):
    return RefObservation(ref=ref, remote=remote, observed_commit=commit)


def unexpected(*args):
    pytest.fail(f"unexpected authority lookup: {args}")


def content_valid(tip):
    return ValidationReport(LocalOutcome.COMPLETED, tip, valid_prefix=tip)


@pytest.fixture
def initial():
    return ContinuityAnchor(
        store=StoreAnchor(
            store_uuid="fixture",
            code_default_ref="refs/heads/trunk",
            planning_ref=REF,
            planning_remote=REMOTE,
            root_commit=ROOT,
        ),
        checkpoint=ROOT,
        previous=None,
        is_ancestor=unexpected,
        validate=unexpected,
    )


@pytest.fixture
def established(initial):
    previous = SharedFrontier(ContinuityStatus.VERIFIED, OLD, OLD, observed(OLD), True)
    return replace(initial, checkpoint=OLD, previous=previous, first_clone=False)


def test_local_only_ignores_unsolicited_remote_tip(initial):
    local = replace(
        initial, store=initial.store.model_copy(update={"planning_remote": None})
    )
    frontier = observe_shared(local, observed(NEW))
    assert frontier.status is ContinuityStatus.LOCAL_ONLY
    assert frontier.checkpoint == ROOT
    assert frontier.observation is None
    assert not frontier.first_observation_limit
    assert not frontier.fences_shared


def test_local_only_transport_diagnostic_does_not_invent_shared_route(initial):
    local = replace(
        initial, store=initial.store.model_copy(update={"planning_remote": None})
    )
    frontier = unavailable_shared(local, "transport unavailable")
    assert frontier.status is ContinuityStatus.LOCAL_ONLY
    assert frontier.valid_tip is None
    assert not frontier.fences_shared


@pytest.mark.parametrize(
    "candidate",
    [
        pytest.param(
            observed(NEW, remote="code-remote"), id="different-repository-remote"
        ),
        pytest.param(
            observed(NEW, ref="refs/heads/trunk"), id="code-default-not-planning"
        ),
        pytest.param(observed(NEW, remote=None), id="local-ref-not-remote-observation"),
    ],
)
def test_only_literal_remote_and_ref_can_admit_a_candidate(established, candidate):
    frontier = observe_shared(established, candidate)
    assert frontier.status is ContinuityStatus.ROUTE_MISMATCH
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert frontier.observation == candidate
    assert frontier.fences_shared


def test_absence_confirmed_by_configured_remote_fences_and_retains_prior_tips(
    established,
):
    deletion = observed(None)
    frontier = observe_shared(established, deletion)
    assert frontier.status is ContinuityStatus.DELETED
    assert frontier.observation == deletion
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert frontier.fences_shared


def test_transport_failure_is_stale_when_last_observation_can_be_retained(established):
    frontier = unavailable_shared(established, "remote transport failed")
    assert frontier.status is ContinuityStatus.STALE
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert frontier.observation == established.previous.observation
    assert frontier.reason == "remote transport failed"
    assert frontier.fences_shared


def test_transport_failure_is_unknown_without_prior_remote_evidence(initial):
    frontier = unavailable_shared(initial, "remote transport failed")
    assert frontier.status is ContinuityStatus.UNKNOWN
    assert frontier.checkpoint == ROOT
    assert frontier.valid_tip is None
    assert frontier.observation is None
    assert frontier.first_observation_limit
    assert frontier.fences_shared


def test_wrong_route_receipt_does_not_create_known_remote_evidence(initial):
    mismatch = observe_shared(initial, observed(NEW, remote="other"))
    frontier = unavailable_shared(
        replace(initial, previous=mismatch), "remote transport failed"
    )
    assert frontier.status is ContinuityStatus.UNKNOWN
    assert frontier.valid_tip is None
    assert frontier.observation is None


def test_matching_frontier_does_not_need_ancestry_lookup(established):
    frontier = observe_shared(
        replace(established, validate=content_valid), observed(OLD)
    )
    assert frontier.status is ContinuityStatus.VERIFIED
    assert frontier.valid_tip == OLD
    assert frontier.checkpoint == OLD
    assert not frontier.fences_shared


def test_first_observation_validates_from_trusted_genesis(initial):
    pairs = []

    def ancestry(ancestor, descendant):
        pairs.append((ancestor, descendant))
        return True

    result = observe_shared(
        replace(initial, is_ancestor=ancestry, validate=content_valid), observed(NEW)
    )
    assert pairs == [(ROOT, NEW)]
    assert result.status is ContinuityStatus.VERIFIED
    assert result.checkpoint == NEW
    assert result.valid_tip == NEW
    assert result.first_observation_limit


def test_independently_supplied_later_checkpoint_closes_genesis_only_limit(initial):
    seeded = replace(initial, checkpoint=OLD, validate=content_valid)
    result = observe_shared(seeded, observed(OLD))
    assert result.status is ContinuityStatus.VERIFIED
    assert not result.first_observation_limit


@pytest.mark.parametrize(
    ("edges", "expected"),
    [
        pytest.param(
            {(OLD, NEW): False, (NEW, OLD): True},
            ContinuityStatus.ROLLBACK,
            id="strict-ancestor-rollback",
        ),
        pytest.param(
            {(OLD, NEW): False, (NEW, OLD): False},
            ContinuityStatus.SIBLING,
            id="unrelated-sibling",
        ),
        pytest.param(
            {(OLD, NEW): None},
            ContinuityStatus.UNPROVABLE,
            id="forward-ancestry-unavailable",
        ),
        pytest.param(
            {(OLD, NEW): False, (NEW, OLD): None},
            ContinuityStatus.UNPROVABLE,
            id="reverse-ancestry-unavailable",
        ),
    ],
)
def test_non_descending_observations_never_run_content_admission(
    established, edges, expected
):
    frontier = observe_shared(
        replace(established, is_ancestor=lambda a, b: edges[a, b]), observed(NEW)
    )
    assert frontier.status is expected
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert frontier.fences_shared


@pytest.mark.parametrize(
    ("local_tip", "local_edge", "diverged"),
    [
        pytest.param(NEW, {}, False, id="local-already-at-shared-tip"),
        pytest.param(OLD, {}, False, id="local-at-shared-checkpoint"),
        pytest.param(
            "older-local",
            {("older-local", NEW): True},
            False,
            id="other-proven-local-ancestor",
        ),
        pytest.param(
            "unpublished-local",
            {("unpublished-local", NEW): False},
            True,
            id="unpublished-branch-diverged",
        ),
        pytest.param(
            "unchecked-local",
            {("unchecked-local", NEW): None},
            True,
            id="local-fast-forward-cannot-be-proven",
        ),
    ],
)
def test_content_valid_remote_tip_does_not_force_local_writer_advance(
    established, local_tip, local_edge, diverged
):
    facts = {(OLD, NEW): True, **local_edge}
    frontier = observe_shared(
        replace(
            established,
            local_tip=local_tip,
            is_ancestor=lambda a, b: facts[a, b],
            validate=content_valid,
        ),
        observed(NEW),
    )
    assert frontier.status is ContinuityStatus.VERIFIED
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip == NEW
    assert frontier.local_diverged is diverged
    assert not frontier.fences_shared


def invalid_content(tip):
    return ValidationReport(
        LocalOutcome.INTEGRITY_ERROR,
        tip,
        "invalid planning data",
        valid_prefix="unobserved-intermediate",
    )


def test_proven_invalid_descendant_becomes_checkpoint_but_not_content_tip(established):
    frontier = observe_shared(
        replace(established, is_ancestor=lambda _a, _b: True, validate=invalid_content),
        observed(NEW),
    )
    assert frontier.status is ContinuityStatus.QUARANTINED
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip == OLD
    assert frontier.reason == "invalid planning data"
    assert frontier.fences_shared


def test_first_invalid_observation_does_not_promote_unobserved_prefix(initial):
    frontier = observe_shared(
        replace(initial, is_ancestor=lambda _a, _b: True, validate=invalid_content),
        observed(NEW),
    )
    assert frontier.status is ContinuityStatus.QUARANTINED
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip is None
    assert frontier.first_observation_limit


def test_validation_for_another_commit_cannot_qualify_this_tip(established):
    frontier = observe_shared(
        replace(
            established,
            is_ancestor=lambda _a, _b: True,
            validate=lambda _tip: content_valid(OLD),
        ),
        observed(NEW),
    )
    assert frontier.status is ContinuityStatus.UNPROVABLE
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert frontier.fences_shared


def test_content_evidence_unavailable_does_not_make_proven_descendant_writable(
    established,
):
    def missing_content(tip):
        return ValidationReport(
            LocalOutcome.UNAVAILABLE, tip, "required validator unavailable"
        )

    frontier = observe_shared(
        replace(established, is_ancestor=lambda _a, _b: True, validate=missing_content),
        observed(NEW),
    )
    assert frontier.status is ContinuityStatus.QUARANTINED
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip == OLD
    assert frontier.reason == "required validator unavailable"


@pytest.fixture
def quarantined(established):
    previous = observe_shared(
        replace(established, is_ancestor=lambda _a, _b: True, validate=invalid_content),
        observed(NEW),
    )
    return replace(established, checkpoint=NEW, previous=previous)


def test_cannot_roll_back_to_content_valid_tip_after_invalid_shared_advance(
    quarantined,
):
    facts = {(NEW, OLD): False, (OLD, NEW): True}
    frontier = observe_shared(
        replace(quarantined, is_ancestor=lambda a, b: facts[a, b]), observed(OLD)
    )
    assert frontier.status is ContinuityStatus.ROLLBACK
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip == OLD


def test_repair_on_sibling_of_quarantine_does_not_run_verifier(quarantined):
    repair = "repair-on-sibling"
    facts = {(NEW, repair): False, (repair, NEW): False}
    frontier = observe_shared(
        replace(quarantined, is_ancestor=lambda a, b: facts[a, b]), observed(repair)
    )
    assert frontier.status is ContinuityStatus.SIBLING
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip == OLD


def test_verified_repair_extends_the_quarantined_checkpoint(quarantined):
    repair = "repair-after-quarantine"
    pairs = []

    def ancestry(ancestor, descendant):
        pairs.append((ancestor, descendant))
        return True

    frontier = observe_shared(
        replace(quarantined, is_ancestor=ancestry, validate=content_valid),
        observed(repair),
    )
    assert pairs == [(NEW, repair)]
    assert frontier.status is ContinuityStatus.VERIFIED
    assert frontier.checkpoint == repair
    assert frontier.valid_tip == repair
    assert frontier.first_observation_limit


def test_first_success_after_offline_starts_from_same_independent_checkpoint(initial):
    offline = unavailable_shared(initial, "offline before first observation")

    def ancestry(ancestor, descendant):
        assert (ancestor, descendant) == (ROOT, NEW)
        return True

    frontier = observe_shared(
        replace(
            initial, previous=offline, is_ancestor=ancestry, validate=content_valid
        ),
        observed(NEW),
    )
    assert frontier.status is ContinuityStatus.VERIFIED
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip == NEW
    assert frontier.first_observation_limit


def test_rollback_after_stale_transport_still_uses_last_shared_checkpoint(established):
    stale = unavailable_shared(established, "temporary transport failure")
    facts = {(OLD, ROOT): False, (ROOT, OLD): True}
    frontier = observe_shared(
        replace(established, previous=stale, is_ancestor=lambda a, b: facts[a, b]),
        observed(ROOT),
    )
    assert frontier.status is ContinuityStatus.ROLLBACK
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert frontier.fences_shared


def test_confirmed_deletion_does_not_let_recreated_sibling_start_new_chain(established):
    deleted = observe_shared(established, observed(None))
    sibling = "new-branch-on-different-history"
    facts = {(OLD, sibling): False, (sibling, OLD): False}
    frontier = observe_shared(
        replace(established, previous=deleted, is_ancestor=lambda a, b: facts[a, b]),
        observed(sibling),
    )
    assert frontier.status is ContinuityStatus.SIBLING
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert frontier.fences_shared


def test_restoring_deleted_ref_to_previous_tip_requires_fresh_content_proof(
    established,
):
    deleted = observe_shared(established, observed(None))
    inspected = []

    def validate(tip):
        inspected.append(tip)
        return content_valid(tip)

    frontier = observe_shared(
        replace(established, previous=deleted, validate=validate), observed(OLD)
    )
    assert inspected == [OLD]
    assert frontier.status is ContinuityStatus.VERIFIED
    assert frontier.checkpoint == OLD
    assert frontier.valid_tip == OLD
    assert not frontier.fences_shared


def test_repeated_observation_of_quarantined_checkpoint_does_not_upgrade_its_content(
    quarantined,
):
    frontier = observe_shared(
        replace(quarantined, validate=invalid_content), observed(NEW)
    )
    assert frontier.status is ContinuityStatus.QUARANTINED
    assert frontier.checkpoint == NEW
    assert frontier.valid_tip == OLD
    assert frontier.fences_shared


def test_stale_transport_retains_local_divergence_until_an_accepted_observation_can_recheck_it(
    established,
):
    local = "unpublished-branch"
    facts = {(OLD, NEW): True, (local, NEW): False}
    verified = observe_shared(
        replace(
            established,
            local_tip=local,
            is_ancestor=lambda a, b: facts[a, b],
            validate=content_valid,
        ),
        observed(NEW),
    )
    # The local ref may have changed independently while the remote was unavailable.
    refreshed_anchor = replace(
        established, checkpoint=NEW, previous=verified, local_tip=NEW
    )
    stale = unavailable_shared(refreshed_anchor, "remote was not observed")
    assert stale.status is ContinuityStatus.STALE
    assert stale.local_diverged
    readmitted = observe_shared(
        replace(refreshed_anchor, previous=stale, validate=content_valid), observed(NEW)
    )
    assert readmitted.status is ContinuityStatus.VERIFIED
    assert not readmitted.local_diverged


def test_repair_acceptance_moves_continuity_past_both_old_tips(quarantined):
    repair = "repair-of-quarantined-history"
    repaired = observe_shared(
        replace(
            quarantined,
            is_ancestor=lambda a, b: (a, b) == (NEW, repair),
            validate=content_valid,
        ),
        observed(repair),
    )
    facts = {(repair, NEW): False, (NEW, repair): True}
    frontier = observe_shared(
        replace(
            quarantined,
            checkpoint=repair,
            previous=repaired,
            is_ancestor=lambda a, b: facts[a, b],
        ),
        observed(NEW),
    )
    assert frontier.status is ContinuityStatus.ROLLBACK
    assert frontier.checkpoint == repair
    assert frontier.valid_tip == repair
    assert frontier.fences_shared


def test_transport_failure_does_not_clear_established_rollback(established):
    rewrite = observed(ROOT)
    facts = {(OLD, ROOT): False, (ROOT, OLD): True}
    refused = observe_shared(
        replace(established, is_ancestor=lambda a, b: facts[a, b]), rewrite
    )
    offline = unavailable_shared(replace(established, previous=refused), "offline")
    assert offline.status is ContinuityStatus.ROLLBACK
    assert offline.checkpoint == OLD
    assert offline.valid_tip == OLD
    assert offline.observation == rewrite
    assert offline.reason == refused.reason
    assert offline.fences_shared


def test_repeated_offline_refresh_keeps_quarantine_and_bounded_diagnosis(quarantined):
    first = unavailable_shared(quarantined, "network unavailable")
    retry = unavailable_shared(replace(quarantined, previous=first), "timeout")
    assert retry == first == quarantined.previous
    assert retry.status is ContinuityStatus.QUARANTINED
    assert retry.checkpoint == NEW
    assert retry.valid_tip == OLD
    assert retry.fences_shared
