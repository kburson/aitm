"""C14 ownership wiring, compatible receipts, and lossless opaque replay."""

from hashlib import sha256
from json import dumps
from types import SimpleNamespace

import pytest

from aitm_core import services
from aitm_core.ext.adapters import resolve_adapter
from aitm_core.ext.api import CapabilitySlot, Extension
from aitm_core.ext.registry import RegistryStatus, load_extensions
from aitm_core.models.common import (
    CommandResult,
    LocalOutcome,
    PublicationOutcome,
    StoreAnchor,
)
from aitm_core.models.config import ExtensionConfig
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    EventAppend,
    ExtensionOwner,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.services import ServicePorts
from aitm_core.store.backend import OperationResult, Snapshot, evaluate_operation

OPAQUE = b'{"schema":"fixture/old","unknown":[2,1]}\r\n\xff'
ACTOR = EventActor(kind="agent", harness="codex")


def operation(owner=None):
    return Operation(
        operation_id="c14-old-request",
        owner=owner or OperationOwner(actor=ACTOR),
        policy_digest="a" * 64,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind="fixture.action", version=1, related_preconditions=(), payload=b""
        ),
        change=RelatedWriteSet(read_set=()),
    )


def registry(*, enabled=("fixture",), installed=True):
    policy = SimpleNamespace(
        config=SimpleNamespace(extensions=ExtensionConfig(enabled=enabled))
    )
    manifest = Extension(
        name="fixture",
        namespace="fixture",
        version="1.2.0",
        requires_core=">=0.1,<0.2",
        owned_paths=("stories/*/*/fixture/**",),
        capabilities=(
            CapabilitySlot(
                id="fixture.write.guard",
                version=1,
                kind="guard",
                placements=("onExit",),
            ),
        ),
    )
    return load_extensions(policy, (manifest,) if installed else ())


def test_legacy_core_request_digest_and_receipt_wire_are_unchanged():
    before = operation()
    assert (
        before.request_digest
        == "19fd48856466ee92b8d2aaf5f5fabe85b94956c519a03265a068d8b25f36b686"
    )
    assert "extension" not in before.owner.model_dump()
    assert WriteAuthorization(
        allowed=True, origin=AuthorityOrigin.REGISTERED
    ).model_dump_json() == ('{"allowed":true,"origin":"registered","reason":null}')


def test_an_existing_core_authorizer_does_not_qualify_an_extension_operation():
    prepared = operation(
        OperationOwner(
            actor=ACTOR, extension=ExtensionOwner(name="fixture", version="1.2.0")
        )
    )
    result = evaluate_operation(
        prepared,
        Snapshot("store", "a" * 40, "b" * 40),
        {},
        ports=ServicePorts(
            write_authorization=lambda *_: WriteAuthorization(
                allowed=True, origin=AuthorityOrigin.REGISTERED
            )
        ),
        categories={},
    )
    assert result.outcome == LocalOutcome.UNAVAILABLE
    assert result.reason == "extension-write-authority-unqualified"
    assert not result.record


@pytest.mark.parametrize(
    ("enabled", "installed", "version", "status"),
    [
        ((), True, "1.2.0", RegistryStatus.DISABLED),
        (("fixture",), False, "1.2.0", RegistryStatus.MISSING),
        (("fixture",), True, "1.1.0", RegistryStatus.INCOMPATIBLE),
    ],
    ids=("disabled-owner", "uninstalled-owner", "older-version"),
)
def test_unavailable_adapter_preserves_original_record_bytes(
    enabled, installed, version, status
):
    installed_registry = registry(enabled=enabled, installed=installed)
    result = resolve_adapter(installed_registry, "fixture", version, OPAQUE)
    assert result.status is status
    assert result.owner == "fixture" and result.version == version
    assert result.raw is OPAQUE
    assert result.registration is None and result.reason


def test_compatible_adapter_reports_exact_owner_and_keeps_record_bytes():
    result = resolve_adapter(registry(), "fixture", "1.2.0", OPAQUE)
    assert result.status is RegistryStatus.ENABLED
    assert result.registration.name == result.owner == "fixture"
    assert result.registration.version == result.version == "1.2.0"
    assert result.raw is OPAQUE


def test_opaque_storage_does_not_make_missing_guard_available():
    disabled_registry = registry(enabled=())
    retained = resolve_adapter(disabled_registry, "fixture", "1.2.0", OPAQUE)
    guard = disabled_registry.resolve(
        "fixture.write.guard", version=1, placement="onExit"
    )
    assert retained.raw == OPAQUE
    assert guard.status is RegistryStatus.DISABLED and guard.registration is None


def test_normal_ingress_uses_owned_authority_even_with_no_extension_declarations(
    monkeypatch,
):
    before = Snapshot("store", "a" * 40, "b" * 40)
    stream = story_event_path(9)
    request = operation()
    foreign = dumps(
        {
            "v": 1,
            "id": "foreign-event",
            "ts": "2026-01-01T00:00:00Z",
            "type": "foreign.record.written",
            "story": 9,
            "actor": ACTOR.model_dump(mode="json"),
            "operation_id": request.operation_id,
            "sequence": 1,
            "prior_log_digest": sha256(b"").hexdigest(),
            "data": {},
        }
    ).encode()
    request = request.model_copy(
        update={
            "change": RelatedWriteSet(
                read_set=(ReadExpectation(path=stream, digest=None),),
                events=(EventAppend(story=9, records=(foreign,)),),
            )
        }
    )
    store = StoreAnchor(
        store_uuid="store",
        code_default_ref="refs/heads/trunk",
        planning_ref="refs/heads/planning",
        planning_remote=None,
        root_commit=before.revision,
    )
    installation = SimpleNamespace(
        repository=object(), store=store, policy_ref=lambda _: store.code_default_ref
    )
    policy = SimpleNamespace(
        config=SimpleNamespace(extensions=ExtensionConfig(enabled=()))
    )
    prepared = SimpleNamespace(
        views=SimpleNamespace(local=SimpleNamespace(observed_commit="c" * 40)),
        outcome=LocalOutcome.COMPLETED,
        publication=PublicationOutcome.NOT_APPLICABLE,
        evidence=(),
        policy=policy,
    )
    monkeypatch.setattr(
        services, "prepare_mutation", lambda *_args, **_kwargs: prepared
    )

    def compose(_repository, _store, *, ports, **_options):
        def transact(received, expected):
            evaluation = evaluate_operation(
                received, expected, {stream: None}, ports=ports, categories={}
            )
            assert evaluation.outcome is LocalOutcome.REFUSED
            assert "foreign.record.written" in evaluation.reason
            assert not evaluation.record and not evaluation.writes
            return OperationResult(
                CommandResult(
                    operation_id=received.operation_id, local=evaluation.outcome
                ),
                expected,
                evaluation.reason,
            )

        return SimpleNamespace(transact=transact)

    monkeypatch.setattr(services, "backend", compose)

    def legacy(*_):
        raise AssertionError("an unowned event cannot reach the legacy Core authorizer")

    result = services.mutate(
        installation, request, before, ports=ServicePorts(write_authorization=legacy)
    )
    assert result.command.local is LocalOutcome.REFUSED
    assert result.snapshot == before
