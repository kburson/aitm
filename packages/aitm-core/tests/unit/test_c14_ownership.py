"""Ownership decisions made against the effective extension registry."""

import json
from types import SimpleNamespace

import pytest
from pydantic import BaseModel, ConfigDict

from aitm_core.events import EMPTY_LOG_DIGEST, core_reducers, fold
from aitm_core.ext.api import EventRegistration, Extension
from aitm_core.ext.ownership import ExtensionWriteAuthorizer, OwnershipError
from aitm_core.ext.registry import load_extensions
from aitm_core.models.config import ExtensionConfig
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    BlobWrite,
    EventAppend,
    ExtensionOwner,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
    story_event_path,
)
from aitm_core.services import UnavailablePort


class Recorded(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    total: int


def extension(name, *paths, events=(), namespace=None):
    return Extension(
        name=name,
        namespace=namespace if namespace is not None else name,
        version="0.1.0",
        requires_core=">=0.1,<0.2",
        owned_paths=paths,
        event_types=events,
    )


def authorizer(*declarations, enabled=None, core=None):
    if enabled is None:
        enabled = tuple(item.name for item in declarations)
    policy = SimpleNamespace(
        config=SimpleNamespace(extensions=ExtensionConfig(enabled=enabled))
    )
    return ExtensionWriteAuthorizer(load_extensions(policy, declarations), core)


def owner(name="fixture", version="0.1.0"):
    return OperationOwner(
        actor=EventActor(kind="agent"),
        extension=None if name is None else ExtensionOwner(name=name, version=version),
    )


def change(*paths, records=()):
    reads = dict.fromkeys(paths)
    for path in paths:
        if path.startswith(".aitm/stories/"):
            reads[story_event_path(int(path.split("/")[3]))] = None
    if records:
        reads[story_event_path(15)] = None
    return RelatedWriteSet(
        read_set=tuple(ReadExpectation(path=path, digest=None) for path in reads),
        writes=tuple(BlobWrite(path=path, content=b"opaque") for path in paths),
        events=(EventAppend(story=15, records=records),) if records else (),
    )


@pytest.mark.parametrize(
    ("first", "second", "overlap"),
    [
        ("fixture/a*.json", "fixture/*b.json", True),
        ("fixture/a*?.json", "fixture/a.json", False),
        ("fixture/a?.json", "fixture/ab.json", True),
        ("fixture/*.json", "fixture/nested/a.json", False),
        ("fixture/**/a?.json", "fixture/ab.json", True),
        ("fixture/**/a?.json", "fixture/nested/deep/ab.json", True),
        ("fixture/**/a?.json", "fixture/**/ab.md", False),
        ("fixture/?.*.json", "fixture/a.*.json", True),
        ("fixture/.?/file.json", "fixture/?./file.json", False),
        ("fixture/.gi?/file.json", "fixture/.?it/file.json", False),
        ("stories/*/*/fixture/*", "stories/000/15/fixture/data.json", True),
        ("stories/*/*/fixture/*", "stories/000/15/other/data.json", False),
    ],
)
def test_glob_overlap_uses_actual_path_intersections(first, second, overlap):
    declarations = (extension("fixture", first), extension("other", second))
    if overlap:
        with pytest.raises(OwnershipError, match="overlap"):
            authorizer(*declarations)
    else:
        authorizer(*declarations)


@pytest.mark.parametrize(
    "pattern",
    [
        "*/*.json",
        "store.json",
        "README.?d",
        "operations/**",
        "repairs/*.json",
        "ideas/2026-11/idea.md",
        "drafts/**",
        "stories/*/*/descriptio?.md",
        "stories/*/*/draft.md",
        "stories/*/*/story.md",
        "stories/*/*/events.jsonl",
        "stories/*/*/attach*/file.json",
        "stories/*/*/desi?n/**",
        "stories/*/*/evidence/item.json",
        "stories/*/*/plan/**",
        "stories/*/*/retro/item.json",
        "stories/*/*/operations/**",
    ],
)
def test_core_reserved_path_intersections_refuse_declaration(pattern):
    with pytest.raises(OwnershipError, match="Core"):
        authorizer(extension("fixture", pattern))


@pytest.mark.parametrize(
    "pattern",
    [
        "./fixture/**",
        "fixture/../other/**",
        "fixture//*.json",
        "fixture/",
        "/fixture/*.json",
        ".aitm/fixture/**",
        "fixture/.GIT/**",
        "fixture\\*.json",
        "fixture/[ab].json",
        "fixture/{a,b}.json",
        "fixture/ab**.json",
        "fixture/***/data.json",
    ],
)
def test_invalid_declaration_grammar_is_refused(pattern):
    with pytest.raises(OwnershipError, match="pattern"):
        authorizer(extension("fixture", pattern))


def test_extension_receipt_binds_only_declared_data_paths():
    auth = authorizer(extension("fixture", "stories/*/*/fixture/*", "fixture/**"))
    listed = ".aitm/stories/000/15/fixture/data.json"
    nested = ".aitm/fixture/nested/record.txt"
    request = owner()
    result = auth(request, change(nested, listed))
    assert result.allowed
    assert result.origin is AuthorityOrigin.REGISTERED
    assert result.extension == request.extension
    assert result.owned_paths == (nested, listed)


@pytest.mark.parametrize(
    "path",
    [
        ".aitm/other/data.json",
        ".aitm/fixture/data.py",
        ".aitm/fixture/.git/config.json",
        ".aitm/stories/000/15/fixture/nested/data.json",
        ".aitm/stories/000/15/plan/data.md",
    ],
)
def test_extension_cannot_write_undeclared_or_structurally_invalid_paths(path):
    auth = authorizer(extension("fixture", "stories/*/*/fixture/*", "fixture/**"))
    result = auth(owner(), change(path))
    assert not result.allowed
    assert result.reason


@pytest.mark.parametrize(
    ("enabled", "name", "version"),
    [
        ((), "fixture", "0.1.0"),
        (("fixture",), "other", "0.1.0"),
        (("fixture",), "fixture", "0.1.1"),
    ],
)
def test_unavailable_extension_authority_fails_closed(enabled, name, version):
    auth = authorizer(extension("fixture", "fixture/**"), enabled=enabled)
    with pytest.raises(UnavailablePort) as failure:
        auth(owner(name, version), change(".aitm/fixture/data.json"))
    assert failure.value.port == "write_authorization"


def record(kind, data, *, story=15):
    return (
        json.dumps(
            {
                "v": 1,
                "id": "one",
                "ts": "2026-11-27T13:00:00Z",
                "type": kind,
                "story": story,
                "actor": {"kind": "agent"},
                "operation_id": "fixture-write",
                "sequence": 1,
                "prior_log_digest": EMPTY_LOG_DIGEST,
                "data": data,
            }
        ).encode()
        + b" \n"
    )


def event_authorizer(*, core=None):
    return authorizer(
        extension(
            "fixture",
            "fixture/**",
            events=(
                EventRegistration(
                    id="fixture.measure.recorded", version=2, model=Recorded
                ),
                EventRegistration(
                    id="fixture.measure.created", version=1, model=Recorded
                ),
            ),
        ),
        core=core,
    )


@pytest.mark.parametrize(
    ("kind", "data"),
    [
        ("fixture.measure.recorded", {"version": 2, "total": 3}),
        ("fixture.measure.created", {"total": 4}),
    ],
)
def test_admitted_typed_event_preserves_raw_bytes_and_stays_outside_owned_paths(
    kind, data
):
    raw = record(kind, data)
    request = change(".aitm/fixture/data.json", records=(raw,))
    result = event_authorizer()(owner(), request)
    assert result.allowed
    assert result.owned_paths == (".aitm/fixture/data.json",)
    assert fold(request.events[0].records, core_reducers()).opaque_events == (raw,)


@pytest.mark.parametrize(
    "raw",
    [
        record("fixture.measure.recorded", {"total": 3}),
        record("fixture.measure.recorded", {"version": 1, "total": 3}),
        record("fixture.measure.created", {"version": True, "total": 3}),
        record("fixture.measure.recorded", {"version": 2, "total": "3"}),
        record("fixture.measure.recorded", {"version": 2, "total": 3, "extra": True}),
        record("fixture.measure.recorded", {"version": 2, "total": 3}, story=16),
        record("fixture.measure.other", {"version": 2, "total": 3}),
        record("other.measure.recorded", {"version": 2, "total": 3}),
        record("core.measure.recorded", {"version": 2, "total": 3}),
        b"not JSON\n",
    ],
)
def test_extension_rejects_foreign_unregistered_or_invalid_events(raw):
    result = event_authorizer()(owner(), change(records=(raw,)))
    assert not result.allowed
    assert result.reason


def test_core_delegates_regular_writes_without_granting_extension_access():
    core_receipt = WriteAuthorization(allowed=True, origin=AuthorityOrigin.FIXTURE)

    def core(_owner, _change):
        return core_receipt

    auth = event_authorizer(core=core)
    assert auth(owner(None), change(".aitm/README.md")) is core_receipt
    assert not auth(owner(None), change(".aitm/fixture/data.json")).allowed
    raw = record("fixture.measure.recorded", {"version": 2, "total": 3})
    assert not auth(owner(None), change(records=(raw,))).allowed


def test_manifest_name_and_event_namespace_are_distinct():
    typed = EventRegistration(id="usage.measure.recorded", version=1, model=Recorded)
    auth = authorizer(extension("fixture", events=(typed,), namespace="usage"))
    records = (record("usage.measure.recorded", {"total": 3}),)
    result = auth(owner(), change(records=records))
    assert result.allowed
    assert result.owned_paths == ()
    assert result.extension == owner().extension


def test_disabled_scope_does_not_overlap_the_effective_registry():
    active = extension("fixture", "fixture/*.json", "fixture/a*.json")
    disabled = extension("other", "fixture/a*.json")
    auth = authorizer(active, disabled, enabled=("fixture",))
    assert auth(owner(), change(".aitm/fixture/ab.json")).allowed
