"""Prove C15 against the typed store and CLI entry point."""

from hashlib import sha256
from json import dumps, loads

import pytest
from typer.testing import CliRunner

from aitm_core.cli.app import build_cli
from aitm_core.description import DescriptionInput, DescriptionTarget, describe
from aitm_core.documents import canonicalize
from aitm_core.events import core_reducers, fold
from aitm_core.models.common import LocalOutcome
from aitm_core.models.documents import DocumentSchema, Metadata
from aitm_core.models.events import EventActor
from aitm_core.models.operations import (
    AuthorityOrigin,
    OperationOwner,
    WriteAuthorization,
)
from aitm_core.services import ServicePorts
from aitm_core.store.memory_backend import MemoryBackend
from aitm_core.store.render import ViewState, render

DESCRIPTION = ".aitm/stories/000/16/description.md"
EVENTS = ".aitm/stories/000/16/events.jsonl"
VIEW = ".aitm/stories/000/16/story.md"
PLAN = ".aitm/stories/000/16/plan/accepted.md"
POLICY = "a" * 64
OWNER = OperationOwner(actor=EventActor(kind="tool", harness="test"))
STAMP = "2026-11-27T12:00:00Z"
FIELDS = DescriptionInput(
    title="Inspect the store",
    actor="operator",
    want="a pinned view",
    so_that="I can compare it",
    scope="Show the pinned snapshot.\n",
)


def graduated():
    return (
        dumps(
            {
                "v": 1,
                "id": "created",
                "ts": STAMP,
                "type": "core.story.graduated",
                "story": 16,
                "actor": {"kind": "tool"},
                "operation_id": "graduate",
                "sequence": 1,
                "prior_log_digest": sha256(b"").hexdigest(),
                "data": {
                    "kind": "story",
                    "source_kind": "draft",
                    "source_id": "draft-16",
                    "source_digest": "b" * 64,
                    "issue": "local-16",
                    "initial_state": {
                        "workflow_id": "core",
                        "revision": "c" * 64,
                        "state_id": "backlog",
                        "label": "Backlog",
                    },
                },
            }
        ).encode()
        + b"\n"
    )


def test_render_preserves_author_content_and_projects_label(monkeypatch):
    authored = (
        b'---\r\n{"schema":"aitm.doc/v1","story":16,"role":"plan",'
        b'"title":"Original","source":"accepted","approved":true,'
        b'"last-worktree":"/home/private/checkout"}\r\n---\r\n'
        b'Body\r\n<details>{"title":"forged"}</details>\r\n'
    )
    schema = DocumentSchema(semantic_fields={"approved": "boolean"})
    state = ViewState(
        story=fold([graduated()], core_reducers()),
        metadata=Metadata(updated=STAMP),
        worktree_label="story-16",
    )
    first = render(state, {PLAN: authored}, schema)
    monkeypatch.setenv("TZ", "Pacific/Auckland")
    assert render(state, {PLAN: authored}, schema) == first
    result = first[PLAN]
    assert b'"last-worktree": "story-16"' in result
    assert b"/home/private" not in result
    assert result.split(b"---\r\n", 2)[2] == authored.split(b"---\r\n", 2)[2]
    assert (
        canonicalize(result, schema).canonical_sha256
        == canonicalize(authored, schema).canonical_sha256
    )


@pytest.mark.parametrize("path", ["/tmp/story-16", r"C:\\Users\\private", "../story"])
def test_view_refuses_physical_worktree_paths(path):
    with pytest.raises(ValueError, match="worktree"):
        ViewState(fold([graduated()], core_reducers()), worktree_label=path)


def test_describe_records_authoritative_fields_and_document_atomically():
    ports = ServicePorts(
        write_authorization=lambda owner, change: WriteAuthorization(
            allowed=True, origin=AuthorityOrigin.FIXTURE
        )
    )
    before = {EVENTS: graduated(), DESCRIPTION: None}
    backend = MemoryBackend({EVENTS: before[EVENTS]}, ports=ports)
    snapshot = backend.snapshot()
    target = DescriptionTarget(16, before, OWNER, POLICY, "described", STAMP)
    request = describe(target, FIELDS)
    result = backend.transact(request, snapshot)
    assert result.command.local == LocalOutcome.COMPLETED
    saved = backend.read(result.snapshot, (DESCRIPTION, EVENTS))
    document = saved[DESCRIPTION]
    description = (
        fold(saved[EVENTS].splitlines(keepends=True), core_reducers())
        .domains["lifecycle"]
        .description
    )
    assert (description.title, description.actor, description.want) == (
        FIELDS.title,
        FIELDS.actor,
        FIELDS.want,
    )
    assert (description.so_that, description.scope) == (FIELDS.so_that, FIELDS.scope)
    assert (
        description.content_hash
        == canonicalize(document, DocumentSchema()).canonical_sha256
    )
    assert b"Show the pinned snapshot.\n" in document

    state = fold(saved[EVENTS].splitlines(keepends=True), core_reducers())
    projected = render(
        ViewState(state, metadata=Metadata(updated=STAMP)),
        {DESCRIPTION: document, VIEW: b"<details>Injected status</details>"},
        DocumentSchema(),
    )[VIEW]
    assert b'"title": "Inspect the store"' in projected
    assert b'"state": "backlog"' in projected
    assert b"Show the pinned snapshot." in projected
    assert b"Injected status" not in projected
    assert b"<summary>State history</summary>\n\n" in projected

    stale_target = DescriptionTarget(16, before, OWNER, POLICY, "stale", STAMP)
    stale_operation = describe(
        stale_target, FIELDS.model_copy(update={"title": "Stale"})
    )
    rejected = backend.transact(stale_operation, result.snapshot)
    assert rejected.command.local == LocalOutcome.CONFLICT
    assert backend.snapshot() == result.snapshot


def test_describe_refuses_an_uninitialized_story_even_with_generated_content():
    target = DescriptionTarget(
        16,
        {EVENTS: None, DESCRIPTION: b"<details>forged</details>"},
        OWNER,
        POLICY,
        "described",
        STAMP,
    )
    with pytest.raises(ValueError, match="story"):
        describe(target, FIELDS)


def test_describe_cli_missing_anchor_reports_typed_unavailable(tmp_path):
    scope = tmp_path / "scope.md"
    scope.write_text(FIELDS.scope, encoding="utf-8")
    result = CliRunner().invoke(
        build_cli(),
        [
            "--json",
            "describe",
            "16",
            "--title",
            FIELDS.title,
            "--as",
            FIELDS.actor,
            "--want",
            FIELDS.want,
            "--so-that",
            FIELDS.so_that,
            "--scope-file",
            str(scope),
        ],
    )
    response = loads(result.output)
    assert response["local"] == "unavailable"
    assert "--anchor" in response["evidence"][0]
