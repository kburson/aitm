"""Deterministic custody proof and operation boundaries."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from aitm_core.models.common import LocalOutcome
from aitm_core.models.config import BacklogIssuer
from aitm_core.models.events import EventActor
from aitm_core.models.evidence import ExpansionCustody
from aitm_core.models.operations import (
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    RelatedWriteSet,
)
from aitm_core.providers.backlog import IdentityReservation, IdentityResult
from aitm_core.providers.identity import (
    DispatchClaim,
    DispatchObservation,
    _qualified_stopped_absence,
)
from aitm_core.rules.expansion import _CUSTODY_OPERATION
from aitm_core.services import ServicePorts
from aitm_core.store.backend import Snapshot, evaluate_operation
from tests.integration.test_c20 import plan_entry


def test_custody_proofs_are_disjoint():
    commit = "b" * 40
    common = dict(
        attempt="first",
        generation=1,
        reservation="held",
        semantic_key="a" * 64,
        verified_at=commit,
        disposition="no-child",
    )
    local = (f"local-allocation-fenced:{commit}",)
    protocol = (f"protocol-no-send:{commit}",)
    provider = (f"ordered-provider-observation:{commit}",)
    branches = {
        "local-allocation": (local, {}),
        "protocol-no-send": (protocol, {}),
        "provider-claim": (
            provider,
            dict(claim="claim", fence="provider-fence", absence="fresh-observation"),
        ),
    }
    for authority, (expected, fields) in branches.items():
        for proof in (local, protocol, provider):
            if proof == expected:
                assert (
                    ExpansionCustody(
                        **common, authority=authority, proof_refs=proof, **fields
                    ).authority
                    == authority
                )
            else:
                with pytest.raises(ValidationError, match="authority proof disagree"):
                    ExpansionCustody(
                        **common, authority=authority, proof_refs=proof, **fields
                    )
    with pytest.raises(ValidationError, match="authority proof disagree"):
        ExpansionCustody(
            **common, authority="local-allocation", proof_refs=local, issue=42
        )


def test_absence_requires_enforceable_fence_for_exact_inflight_claim():
    issuer = BacklogIssuer(
        backlog="external", backlog_repository="fixture", numbering_namespace="issues"
    )
    intent = plan_entry("operation", issuer)
    reservation = IdentityReservation(intent=intent, key=intent.source.semantic_key)
    pinned = DispatchClaim(
        key=reservation.key, generation=1, token="claim", origin_digest="c" * 64
    )
    legacy = DispatchClaim(key=reservation.key, generation=1, token="legacy")
    assert '"origin_digest"' not in legacy.model_dump_json()
    assert (
        DispatchClaim.model_validate_json(pinned.model_dump_json()).origin_digest
        == "c" * 64
    )
    observation = DispatchObservation(
        claim=pinned.token,
        result=IdentityResult(
            reservation=reservation, status="absent-with-proof", absence_proof="fresh"
        ),
        fence_proof="enforced-provider-fence",
    )
    in_flight = []

    def finish_after_observation():
        if not in_flight:
            pytest.fail("Fixture sent no request before the observation")
        if in_flight.pop() != pinned:
            return
        raise RuntimeError("Provider rejected the delayed request under its fence")

    in_flight.append(pinned)
    assert not _qualified_stopped_absence(
        SimpleNamespace(), reservation, pinned, observation
    )
    provider = SimpleNamespace(
        verify_sender_fence=lambda r, c, p: (
            (r, c, p) == (reservation, pinned, observation.fence_proof)
        )
    )
    assert _qualified_stopped_absence(provider, reservation, pinned, observation)
    assert not _qualified_stopped_absence(provider, reservation, legacy, observation)
    with pytest.raises(RuntimeError, match="Provider rejected"):
        finish_after_observation()


def test_custody_category_grants_no_default_authority():
    operation = Operation(
        operation_id="scope",
        owner=OperationOwner(actor=EventActor(kind="tool", harness="fixture")),
        policy_digest="a" * 64,
        category=OperationCategory.STOP_RECONCILIATION,
        change=RelatedWriteSet(read_set=()),
        intent=FinalizationIntent(
            kind=_CUSTODY_OPERATION[0],
            version=1,
            related_preconditions=(),
            payload=b"{}",
        ),
    )
    snapshot = Snapshot("fixture", "a" * 40, "b" * 40)
    unregistered = evaluate_operation(
        operation, snapshot, {}, ports=ServicePorts(), categories={}
    )
    assert unregistered.outcome == LocalOutcome.REFUSED
    assert unregistered.reason == "operation-category-out-of-scope"
    registered = evaluate_operation(
        operation,
        snapshot,
        {},
        ports=ServicePorts(),
        categories={_CUSTODY_OPERATION: OperationCategory.STOP_RECONCILIATION},
    )
    assert registered.outcome == LocalOutcome.UNAVAILABLE
    assert registered.reason == "write-authorizer-unavailable"
