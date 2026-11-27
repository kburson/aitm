"""Provider-neutral managed contract tests. The fake provider is purely local."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from aitm_core.ext.api import Extension
from aitm_core.ext.registry import load_extensions
from aitm_core.models.common import RefObservation
from aitm_core.models.config import ExtensionConfig
from aitm_core.providers.githost import RemoteRef
from aitm_core.providers.managed import (
    ManagedOperation,
    ManagedProviderRegistration,
    ManagedQualification,
    ManagedReceipt,
    ManagedRequest,
    ManagedResult,
    resolve_managed,
)
from aitm_core.store.gate import RefIdentity

SOURCE = "a" * 40
BASE = "b" * 40
LANDING = "c" * 40
REPOSITORY = "org/project"
PROVIDER = "fixture"
PR = "pull-234"
SOURCE_REF = RemoteRef(repository=REPOSITORY, ref=RefIdentity("refs/heads/story-233"))
TARGET_REF = RemoteRef(repository=REPOSITORY, ref=RefIdentity("refs/heads/trunk"))


def request(operation, **overrides):
    fields = dict(
        operation=operation,
        provider=PROVIDER,
        capability_version=1,
        operation_id="action-233",
        story=233,
        role="implementation",
        incarnation="round-1",
        source=SOURCE_REF,
        target=TARGET_REF,
        source_head=SOURCE,
        target_base=BASE,
        pull_request=None if operation == "provision" else PR,
        draft=True if operation == "readiness" else None,
    )
    return ManagedRequest(**(fields | overrides))


def qualification(intent, **overrides):
    fields = dict(
        provider=intent.provider,
        repository=intent.target.repository,
        operation=intent.operation,
        version=intent.capability_version,
        evidence=("provider-operation-qualification",),
    )
    return ManagedQualification(**(fields | overrides))


def observation(ref, revision, **overrides):
    return RefObservation(
        **(
            dict(ref=ref.ref.name, observed_commit=revision, remote=ref.repository)
            | overrides
        )
    )


def receipt(intent, **overrides):
    fields = dict(
        request=intent,
        source=observation(
            intent.source, None if intent.operation == "retire" else SOURCE
        ),
        target=observation(
            intent.target, LANDING if intent.operation == "deliver" else BASE
        ),
        pull_request=PR,
        draft=True,
        protected=True,
        landed_commit=LANDING if intent.operation == "deliver" else None,
        evidence=("provider-readback",),
    )
    return ManagedReceipt(**(fields | overrides))


def checked(intent, **overrides):
    return ManagedResult(
        request=intent, status="verified", receipt=receipt(intent, **overrides)
    )


def context(*, selected=PROVIDER, enabled=(PROVIDER,), registration=None, fenced=False):
    policy = SimpleNamespace(
        config=SimpleNamespace(
            extensions=ExtensionConfig(enabled=enabled),
            providers=SimpleNamespace(githost=selected),
        ),
        routing=SimpleNamespace(code_repository=REPOSITORY),
        writes_fenced=fenced,
    )
    extension = Extension(
        name=PROVIDER,
        namespace=PROVIDER,
        version="0.1",
        requires_core=">=0.1,<0.2",
        managed_provider=registration,
    )
    return policy, load_extensions(policy, (extension,))


@pytest.fixture
def configured():
    calls = []

    class FakeProvider:
        name = PROVIDER

        def perform_managed(self, intent, qualifier):
            assert qualifier.operation == intent.operation
            calls.append(intent.operation)
            return checked(intent)

    def factory():
        calls.append("factory")
        return FakeProvider()

    registration = ManagedProviderRegistration(
        factory=factory,
        capabilities=tuple((operation, 1) for operation in ManagedOperation),
    )
    return registration, calls


@pytest.mark.parametrize("operation", list(ManagedOperation))
def test_registered_qualified_capabilities_are_lazy_and_scoped(operation, configured):
    registration, calls = configured
    policy, registry = context(registration=registration)
    intent = request(operation)
    proof = qualification(intent)
    result = resolve_managed(policy, registry, intent, proof)
    assert result.status == "available"
    assert result.qualification is proof
    assert result.factory is registration.factory
    assert calls == []

    provider = result.factory()
    output = provider.perform_managed(intent, result.qualification)
    assert output.status == "verified" and output.request == intent
    assert calls == ["factory", intent.operation]


@pytest.mark.parametrize(
    ("selection", "enabled", "has_registration", "expected"),
    [
        ("none", (PROVIDER,), True, "not selected"),
        (PROVIDER, (), True, "disabled"),
        (PROVIDER, (PROVIDER,), False, "unsupported"),
    ],
)
def test_missing_provider_capacity_is_explained_without_running_a_factory(
    selection, enabled, has_registration, expected, configured
):
    registration, calls = configured
    policy, registry = context(
        selected=selection,
        enabled=enabled,
        registration=registration if has_registration else None,
    )
    intent = request("readiness")
    result = resolve_managed(policy, registry, intent, qualification(intent))
    assert result.status == "unavailable" and expected in result.reason
    assert result.factory is None and calls == []


@pytest.mark.parametrize(
    "wrong",
    [
        None,
        {"repository": "elsewhere"},
        {"provider": "other"},
        {"operation": "deliver"},
        {"version": 2},
    ],
    ids=(
        "absent-proof",
        "wrong-repository",
        "wrong-provider",
        "wrong-operation",
        "wrong-version",
    ),
)
def test_unqualified_operation_is_pending_and_cannot_activate_provider(
    wrong, configured
):
    registration, calls = configured
    policy, registry = context(registration=registration)
    intent = request("readiness")
    proof = qualification(intent, **wrong) if wrong is not None else None
    result = resolve_managed(policy, registry, intent, proof)
    assert result.status == "unavailable" and "qualification" in result.reason
    assert result.factory is None and result.qualification is None and calls == []


def test_requested_version_must_be_supported_even_with_scoped_evidence(configured):
    registration, _ = configured
    policy, registry = context(registration=registration)
    intent = request("readiness", capability_version=2)
    result = resolve_managed(policy, registry, intent, qualification(intent))
    assert result.status == "unavailable" and "version" in result.reason


@pytest.mark.parametrize(
    ("operation", "changes"),
    [
        ("provision", {"pull_request": PR}),
        ("readiness", {"draft": None}),
        ("deliver", {"pull_request": None}),
        ("retire", {"draft": True}),
        ("observe", {"source": TARGET_REF}),
    ],
)
def test_each_request_pins_the_required_effect_coordinates(operation, changes):
    with pytest.raises(ValidationError):
        request(operation, **changes)


@pytest.mark.parametrize(
    ("operation", "changes"),
    [
        ("provision", {"draft": False}),
        ("provision", {"protected": False}),
        ("readiness", {"draft": False}),
        ("readiness", {"pull_request": "different-pr"}),
        ("readiness", {"source": observation(SOURCE_REF, BASE)}),
        ("readiness", {"source": observation(SOURCE_REF, SOURCE, remote="foreign")}),
        ("deliver", {"landed_commit": None}),
        ("deliver", {"landed_commit": SOURCE}),
        ("retire", {"source": observation(SOURCE_REF, SOURCE)}),
        ("observe", {"target": observation(TARGET_REF, SOURCE)}),
        ("observe", {"evidence": ()}),
    ],
)
def test_verified_receipts_require_operation_specific_live_readback(operation, changes):
    with pytest.raises(ValidationError):
        checked(request(operation), **changes)


def test_a_verified_receipt_cannot_be_reused_for_another_incarnation():
    original = request("deliver")
    other = request("deliver", incarnation="replacement")
    with pytest.raises(ValidationError, match="request"):
        ManagedResult(request=other, status="verified", receipt=receipt(original))


@pytest.mark.parametrize("status", ["pending", "unsupported", "refused"])
def test_nonverified_outcomes_require_reason_and_preserve_pending_evidence(status):
    intent = request("retire")
    result = ManagedResult(
        request=intent,
        status=status,
        reason="manual provider evidence pending",
        evidence=("observed",),
    )
    assert result.request == intent and result.receipt is None
    with pytest.raises(ValidationError):
        ManagedResult(request=intent, status=status)
    with pytest.raises(ValidationError):
        ManagedResult(
            request=intent, status=status, reason="pending", receipt=receipt(intent)
        )


def test_matching_qualification_for_foreign_repository_does_not_grant_authority(
    configured,
):
    registration, calls = configured
    policy, registry = context(registration=registration)
    intent = request(
        "readiness",
        source=RemoteRef(repository="foreign", ref=SOURCE_REF.ref),
        target=RemoteRef(repository="foreign", ref=TARGET_REF.ref),
    )
    result = resolve_managed(policy, registry, intent, qualification(intent))
    assert result.status == "unavailable" and "repository" in result.reason
    assert result.factory is None and calls == []


def test_committed_routing_fence_allows_observation_but_holds_managed_mutation(
    configured,
):
    registration, calls = configured
    policy, registry = context(registration=registration, fenced=True)
    query = request("observe")
    mutation = request("readiness")
    assert (
        resolve_managed(policy, registry, query, qualification(query)).status
        == "available"
    )
    result = resolve_managed(policy, registry, mutation, qualification(mutation))
    assert result.status == "unavailable" and "routing" in result.reason
    assert result.factory is None and calls == []


def test_ready_request_requires_positive_out_of_draft_readback():
    intent = request("readiness", draft=False)
    assert checked(intent, draft=False).status == "verified"
    with pytest.raises(ValidationError):
        checked(intent, draft=True)
