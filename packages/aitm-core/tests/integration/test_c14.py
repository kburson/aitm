"""Exercise extension ownership at the normal mutation entry in real Git."""

import json
import subprocess
from hashlib import sha256

import pytest
from pydantic import BaseModel, ConfigDict

from aitm_core.events import core_reducers, fold
from aitm_core.ext.api import EventRegistration, Extension
from aitm_core.models.common import LocalOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.evidence import GuardEvaluated
from aitm_core.models.operations import (
    BlobWrite,
    EventAppend,
    ExtensionOwner,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
)
from aitm_core.services import ServicePorts, mutate, policy
from aitm_core.store.objects import Repository
from aitm_core.store.validation import validate_history
from tests.integration.test_c06 import candidate_with_mode
from tests.integration.test_c07 import commit_policy
from tests.integration.test_c08 import empty_planning_root, git, identify
from tests.support.c07 import PLANNING, installation, settings_at

OWNED = ".aitm/stories/000/9/fixture/record.json"
STREAM = ".aitm/stories/000/9/events.jsonl"
OPAQUE = b" \r\n\xff\x00plugin format 1\r\n"


class FixtureData(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    value: int


def manifest(name="fixture", *, paths=("stories/*/*/fixture/**",)):
    return Extension(
        name=name,
        namespace=name,
        version="1.0",
        requires_core=">=0.1,<0.2",
        owned_paths=paths,
        event_types=(
            EventRegistration(
                id=f"{name}.record.written", version=1, model=FixtureData
            ),
        ),
    )


@pytest.fixture
def installed(tmp_path):
    git(tmp_path, "init", "-q", "-b", "trunk")
    identify(tmp_path)
    genesis = empty_planning_root(tmp_path)
    git(tmp_path, "update-ref", PLANNING, genesis)
    return installation(Repository(tmp_path, PLANNING), genesis)


def enable(installed, *names):
    settings = settings_at(installed.store.root_commit).replace(
        "enabled = []", f"enabled = {json.dumps(names)}"
    )
    revision = commit_policy(installed.repository.root, settings)
    return policy(installed, revision).source.digest


def event(operation_id, event_type):
    return (
        b" "
        + json.dumps(
            {
                "v": 1,
                "id": f"{operation_id}-event",
                "ts": "2026-11-27T08:00:00Z",
                "type": event_type,
                "story": 9,
                "actor": {"kind": "agent", "harness": "fixture"},
                "operation_id": operation_id,
                "sequence": 1,
                "prior_log_digest": sha256(b"").hexdigest(),
                "data": {"value": 27},
            }
        ).encode()
        + b"\n"
    )


def operation(
    policy_digest,
    operation_id,
    write,
    *,
    current=None,
    stream=None,
    record=None,
):
    return Operation(
        operation_id=operation_id,
        owner=OperationOwner(
            actor=EventActor(kind="agent", harness="fixture"),
            extension=ExtensionOwner(name="fixture", version="1.0"),
        ),
        policy_digest=policy_digest,
        category=OperationCategory.NORMAL,
        intent=FinalizationIntent(
            kind="fixture.record", version=1, related_preconditions=(), payload=b"{}"
        ),
        change=RelatedWriteSet(
            read_set=(
                ReadExpectation(
                    path=write.path,
                    digest=sha256(current).hexdigest() if current is not None else None,
                ),
                ReadExpectation(
                    path=STREAM,
                    digest=sha256(stream).hexdigest() if stream is not None else None,
                ),
            ),
            writes=(write,),
            events=(EventAppend(story=9, records=(record,)),) if record else (),
        ),
    )


def blob(repo, path):
    return subprocess.check_output(
        ("git", "-C", str(repo.root), "cat-file", "blob", f"{PLANNING}:{path}"),
        stderr=subprocess.PIPE,
    )


def assert_unchanged(repo, before, result):
    assert result.snapshot == before
    assert git(repo.root, "rev-parse", PLANNING) == before.revision
    assert git(repo.root, "rev-parse", f"{PLANNING}^{{tree}}") == before.tree


def test_registered_write_and_event_survive_disabling_the_extension(installed):
    digest = enable(installed, "fixture")
    repo = installed.repository
    before = repo.tip()
    ports = ServicePorts(extension_declarations=(manifest(),))
    event_bytes = event("write-fixture", "fixture.record.written")
    request = operation(
        digest,
        "write-fixture",
        BlobWrite(path=OWNED, content=OPAQUE),
        record=event_bytes,
    )

    written = mutate(installed, request, before, ports=ports)

    assert written.command.local is LocalOutcome.COMPLETED, written.reason
    assert written.snapshot == repo.tip()
    assert repo.parent(written.snapshot) == before.revision
    assert blob(repo, OWNED) == OPAQUE
    assert blob(repo, STREAM) == event_bytes
    key = sha256(b"write-fixture").hexdigest()
    receipt_path = f".aitm/operations/{key}.json"
    receipt_bytes = blob(repo, receipt_path)
    receipt = json.loads(receipt_bytes)
    assert set(
        git(
            repo.root, "diff-tree", "-r", "--no-commit-id", "--name-only", PLANNING
        ).splitlines()
    ) == {OWNED, STREAM, receipt_path}
    assert receipt["base"] == before.revision
    assert receipt["authorization"] == {
        "allowed": True,
        "origin": "registered",
        "reason": None,
        "extension": {"name": "fixture", "version": "1.0"},
        "owned_paths": [OWNED],
    }

    disabled = enable(installed)
    retained = validate_history(
        installed.store, written.snapshot.revision, repository=repo
    )
    assert retained.outcome is LocalOutcome.COMPLETED, retained.reason
    opaque = fold(blob(repo, STREAM).splitlines(keepends=True), core_reducers())
    assert opaque.opaque_events == (event_bytes,)

    attempt = operation(
        disabled,
        "write-disabled",
        BlobWrite(path=OWNED, content=b"replacement"),
        current=OPAQUE,
        stream=event_bytes,
    )
    refused = mutate(installed, attempt, written.snapshot, ports=ports)
    assert refused.command.local is LocalOutcome.UNAVAILABLE, refused.reason
    assert_unchanged(repo, written.snapshot, refused)
    assert blob(repo, OWNED) == OPAQUE
    assert blob(repo, receipt_path) == receipt_bytes

    bypass = repo.create_commit(written.snapshot, {OWNED: b"unreceipted"}, "bypass")
    rejected = validate_history(installed.store, bypass.revision, repository=repo)
    assert rejected.outcome is LocalOutcome.INTEGRITY_ERROR, rejected.reason
    assert rejected.first_invalid == bypass.revision
    assert rejected.valid_prefix == written.snapshot.revision


@pytest.mark.parametrize(
    ("other_paths", "overlapping_owner"),
    [
        pytest.param(
            ("stories/*/*/fixture/record.json",), "fixture", id="extension-overlap"
        ),
        pytest.param(("stories/*/*/plan/**",), "Core", id="core-overlap"),
    ],
)
def test_overlapping_enabled_declarations_refuse_mutation(
    installed, other_paths, overlapping_owner
):
    digest = enable(installed, "fixture", "other")
    repo = installed.repository
    before = repo.tip()
    ports = ServicePorts(
        extension_declarations=(manifest(), manifest("other", paths=other_paths))
    )
    request = operation(
        digest, "declared-overlap", BlobWrite(path=OWNED, content=OPAQUE)
    )

    result = mutate(installed, request, before, ports=ports)

    assert result.command.local is LocalOutcome.REFUSED, result.reason
    assert f"overlaps {overlapping_owner}" in result.reason
    assert_unchanged(repo, before, result)


def test_foreign_registered_event_refuses_the_whole_operation(installed):
    digest = enable(installed, "fixture", "other")
    repo = installed.repository
    before = repo.tip()
    ports = ServicePorts(
        extension_declarations=(
            manifest(),
            manifest("other", paths=("stories/*/*/other/**",)),
        )
    )
    request = operation(
        digest,
        "foreign-event",
        BlobWrite(path=OWNED, content=OPAQUE),
        record=event("foreign-event", "other.record.written"),
    )

    result = mutate(installed, request, before, ports=ports)

    assert result.command.local is LocalOutcome.REFUSED, result.reason
    assert "other.record.written" in result.reason
    assert_unchanged(repo, before, result)


def test_guard_refusal_records_outcome_without_extension_write_receipt(installed):
    digest = enable(installed, "fixture")
    repo = installed.repository
    before = repo.tip()
    ports = ServicePorts(extension_declarations=(manifest(),))
    request = operation(digest, "guard-refused", BlobWrite(path=OWNED, content=OPAQUE))
    guard = GuardEvaluated(
        operation=request.operation_id,
        read_set_digest=request.change.read_set_digest,
        policy_digest=digest,
        workflow={
            "workflow_id": "fixture",
            "revision": digest,
            "state_id": "refine",
            "label": "Refine",
        },
        slot="source-exit",
        guard="fixture.readiness",
        guard_version="1",
        ok=False,
        code="missing",
        mode="enforce",
    )
    request = request.model_copy(update={"guards": (guard,)})

    result = mutate(installed, request, before, ports=ports)

    assert result.command.local is LocalOutcome.REFUSED, result.reason
    assert repo.tip() == result.snapshot
    assert repo.parent(result.snapshot) == before.revision
    key = sha256(b"guard-refused").hexdigest()
    receipt_path = f".aitm/operations/{key}.json"
    assert (
        git(repo.root, "diff-tree", "-r", "--no-commit-id", "--name-only", PLANNING)
        == receipt_path
    )
    receipt = json.loads(blob(repo, receipt_path))
    assert receipt["command"]["local"] == "refused"
    assert receipt["authorization"] == {
        "allowed": True,
        "origin": "registered",
        "reason": None,
    }


@pytest.mark.parametrize(
    ("existing", "target"),
    [(OWNED, f"{OWNED}/leaf.txt"), (f"{OWNED}/leaf.txt", OWNED)],
    ids=("blob-as-parent", "directory-as-blob"),
)
def test_extension_cannot_change_git_path_type(installed, existing, target):
    digest = enable(installed, "fixture")
    repo = installed.repository
    ports = ServicePorts(extension_declarations=(manifest(),))
    initial = operation(digest, "seed", BlobWrite(path=existing, content=OPAQUE))
    seeded = mutate(installed, initial, repo.tip(), ports=ports)
    assert seeded.command.local is LocalOutcome.COMPLETED, seeded.reason
    request = operation(digest, "collision", BlobWrite(path=target, content=b"blocked"))
    objects = git(repo.root, "count-objects")

    result = mutate(installed, request, seeded.snapshot, ports=ports)

    assert result.command.local is LocalOutcome.REFUSED, result.reason
    assert "path type" in result.reason
    assert_unchanged(repo, seeded.snapshot, result)
    assert git(repo.root, "count-objects") == objects
    assert blob(repo, existing) == OPAQUE


def test_extension_cannot_write_through_tree_symlink(installed):
    digest = enable(installed, "fixture")
    repo = installed.repository
    link = ".aitm/stories/000/9/fixture/link"
    revision = candidate_with_mode(repo, repo.tip(), "120000", link)
    git(repo.root, "update-ref", PLANNING, revision)
    before = repo.tip()
    ports = ServicePorts(extension_declarations=(manifest(),))
    request = operation(
        digest, "symlink", BlobWrite(path=f"{link}/leaf.txt", content=OPAQUE)
    )

    result = mutate(installed, request, before, ports=ports)

    assert result.command.local in (LocalOutcome.REFUSED, LocalOutcome.INTEGRITY_ERROR)
    assert "regular" in result.reason or "symlink" in result.reason
    assert_unchanged(repo, before, result)
    assert git(repo.root, "ls-tree", PLANNING, link).startswith("120000 blob ")
