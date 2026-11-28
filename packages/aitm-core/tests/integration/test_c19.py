"""Exercise pre-story intake through installed routes and real Git."""

from datetime import UTC, datetime
from hashlib import sha256
from json import dumps, loads
from pathlib import Path, PurePosixPath
from shutil import which
from subprocess import run

from aitm_core.drafts import CreateEntity, Intake
from aitm_core.models.events import EventActor
from aitm_core.models.operations import OperationOwner, story_event_path
from aitm_core.services import preflight_policy
from aitm_core.store.objects import Repository
from aitm_core.store.publication import Publisher
from tests.integration.test_c08 import PLANNING, PLANNING_REMOTE, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned, describe_args
from tests.unit.test_c15 import EVENTS, graduated


def test_draft_identity(topology, tmp_path, monkeypatch):
    installation = topology.policy.installation
    config = describe_args(topology, tmp_path)[-4:]

    def invoke(group, action, *args):
        cli = which("aitm")
        assert cli is not None
        process = run(
            [cli, "--json", group, action, *args, *config],
            cwd=topology.local,
            capture_output=True,
            text=True,
            check=False,
        )
        assert process.stdout, process.stderr
        return loads(process.stdout)

    def session(anchor=installation):
        preflight = preflight_policy(anchor)
        assert preflight.policy is not None
        snapshot = anchor.repository.tip()
        return Intake(
            anchor,
            snapshot,
            preflight.policy.source.digest,
            OperationOwner(actor=EventActor(kind="tool", harness="test")),
            datetime(2026, 11, 27, 14, 55, tzinfo=UTC),
        )

    recoverable = session().create_draft(CreateEntity("Retry after losing CAS"))
    compare_and_swap = Repository.compare_and_swap

    def lose_discard_cas(repo, new, expected):
        assert "AITM operation draft-discard-" in git(
            repo.root, "show", "-s", "--format=%s", new
        )
        monkeypatch.setattr(Repository, "compare_and_swap", compare_and_swap)
        contender = repo.create_commit(
            repo.read_tree(expected),
            {".aitm/README.md": b"Concurrent change\n"},
            "contender",
        )
        assert compare_and_swap(repo, contender.revision, expected)
        return False

    monkeypatch.setattr(Repository, "compare_and_swap", lose_discard_cas)
    failed = session().discard_draft(recoverable.identity, "Replaced")
    assert failed.command.local == "conflict"
    restarted = session().discard_draft(recoverable.identity, "Replaced")
    assert restarted.command.local == "completed"
    assert restarted.command.publication == "verified"
    assert restarted.command.operation_id != failed.command.operation_id

    idea = invoke("idea", "add", "Sketch", "--tag", "intake")
    assert idea["publication"] == "verified"
    entity = idea["entity"]
    assert invoke("idea", "list")["entities"] == [entity]

    first = session().create_draft(CreateEntity("One idea", "First body\n"))
    second = session().create_draft(CreateEntity("One idea"))
    assert first.identity != second.identity
    assert "/20261127-1455-one-idea/" in first.document
    assert "/20261127-1455-one-idea-2/" in second.document

    ambiguous = invoke("draft", "discard", "one-idea", "--reason", "Superseded")
    assert ambiguous["local"] == "conflict"
    assert all(ref.identity in str(ambiguous["evidence"]) for ref in (first, second))

    def advance(path, contents):
        git(topology.planning, "pull", "--ff-only", "-q")
        return topology.advance_planning(path, contents)

    attachment = str(PurePosixPath(second.document).parent / "attachments/draft.md")
    second_tree = session().snapshot.tree
    attached = installation.repository.read_blobs(second_tree, (second.document,))[
        second.document
    ]
    assert attached is not None
    advance(attachment, attached)
    # Pick a separate source with the same title so the tombstone stem collides.
    first_result = session().discard_draft(first.identity, "Superseded")
    assert first_result.command.publication == "verified"
    before = session().snapshot
    second_result = session().discard_draft(second.identity, "Superseded")
    assert second_result.command.publication == "verified"
    after = second_result.snapshot
    assert installation.repository.parent(after) == before.revision
    retained = installation.repository.read_blobs(before.tree, (attachment,))
    assert retained[attachment] == attached
    files = git(topology.local, "ls-tree", "-r", "--name-only", after.tree).splitlines()
    assert second.document not in files and attachment not in files
    tombstone = ".aitm/drafts/discarded/20261127-1455-one-idea-2.json"
    saved = loads(
        installation.repository.read_blobs(after.tree, (tombstone,))[tombstone]
    )
    assert (saved["entity"]["identity"], saved["prior_tree"]) == (
        second.identity,
        before.tree,
    )
    assert saved["attachments"] == {attachment: sha256(attached).hexdigest()}
    assert (
        invoke("draft", "discard", "one-idea", "--reason", "Superseded")["local"]
        == "refused"
    )
    retry = invoke("draft", "discard", second.identity, "--reason", "Superseded")
    assert (retry["local"], retry["publication"], retry["operation_id"]) == (
        "completed",
        "verified",
        second_result.command.operation_id,
    )
    assert session().snapshot == after

    retry_by_operation = session().discard_draft(
        second_result.command.operation_id, "Superseded"
    )
    assert retry_by_operation.command.operation_id == retry["operation_id"]

    other = cloned(topology, tmp_path).policy.installation
    recovered = session(other).discard_draft(second.identity, "Superseded")
    assert recovered.command.publication == "verified"
    assert recovered.command.operation_id == retry["operation_id"]
    assert other.repository.tip().revision == after.revision
    replacement = session().create_draft(CreateEntity("One idea"))
    assert "/20261127-1455-one-idea-3/" in replacement.document
    before_stale_handle = session().snapshot
    stale = session().discard_draft(first.document, "Superseded")
    assert stale.command.operation_id == first_result.command.operation_id
    assert stale.command.local == "completed"
    assert session().snapshot == before_stale_handle

    third = session().create_draft(CreateEntity("Graduated"))
    event = loads(graduated())
    before_event = {
        **event,
        "id": "c19-prior-evidence",
        "type": "core.idea.created",
        "operation_id": "c19-prior-evidence",
        "data": {"path": entity["document"]},
    }
    earlier = (dumps(before_event) + "\n").encode()
    advance(EVENTS, earlier)
    event["data"]["source_id"] = third.identity
    event["sequence"] = 2
    event["prior_log_digest"] = sha256(earlier).hexdigest()
    advance(EVENTS, earlier + (dumps(event) + "\n").encode())
    before_refusal = session().snapshot
    rejected = invoke("draft", "discard", third.identity, "--reason", "Too late")
    assert rejected["local"] == "refused"
    assert "graduated" in str(rejected["evidence"]).lower()
    assert session().snapshot == before_refusal
    remote = Path(git(topology.local, "remote", "get-url", PLANNING_REMOTE))
    assert git(remote, "rev-parse", PLANNING) == before_refusal.revision

    already_discarded = loads(graduated())
    already_discarded["story"] = 17
    already_discarded["data"]["source_id"] = second.identity
    advance(story_event_path(17), (dumps(already_discarded) + "\n").encode())
    before_retry = session().snapshot
    assert (
        session().discard_draft(second.identity, "Superseded").command.operation_id
        == retry["operation_id"]
    )
    changed_reason = session().discard_draft(second.identity, "Changed")
    assert changed_reason.command.local == "conflict"
    assert changed_reason.command.operation_id == retry["operation_id"]
    assert session().snapshot == before_retry

    raced = session().create_draft(CreateEntity("Attachment race"))
    raced_attachment = str(
        PurePosixPath(raced.document).parent / "attachments/raced.txt"
    )
    push = Publisher._push

    def competing_push(self, tip, expected_shared):
        monkeypatch.setattr(Publisher, "_push", push)
        advance(raced_attachment, b"concurrent attachment")
        push(self, tip, expected_shared)

    monkeypatch.setattr(Publisher, "_push", competing_push)
    result = session().discard_draft(raced.identity, "Race")
    assert result.command.local == "completed"
    assert result.command.publication == "pending"
    assert result.command.recovery
    remote_tip = git(remote, "rev-parse", PLANNING)
    assert (
        git(remote, "show", f"{remote_tip}:{raced_attachment}")
        == "concurrent attachment"
    )
    assert git(remote, "show", f"{remote_tip}:{raced.document}")
    assert (
        git(remote, "ls-tree", "-r", remote_tip, ".aitm/drafts/discarded").count(
            ".json"
        )
        == 3
    )
