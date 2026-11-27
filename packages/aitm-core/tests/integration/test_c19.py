"""Exercise pre-story intake through installed routes and real Git."""

from datetime import UTC, datetime
from hashlib import sha256
from json import dumps, loads
from pathlib import Path, PurePosixPath
from shutil import which
from subprocess import run

from aitm_core.drafts import CreateEntity, Intake
from aitm_core.models.events import EventActor
from aitm_core.models.operations import OperationOwner
from aitm_core.services import preflight_policy
from aitm_core.store.publication import Publisher
from tests.integration.test_c08 import PLANNING, PLANNING_REMOTE, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import describe_args
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

    def session():
        preflight = preflight_policy(installation)
        assert preflight.policy is not None
        snapshot = installation.repository.tip()
        return Intake(
            installation,
            snapshot,
            preflight.policy.source.digest,
            OperationOwner(actor=EventActor(kind="tool", harness="test")),
            datetime(2026, 11, 27, 14, 55, tzinfo=UTC),
        )

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

    attachment = str(PurePosixPath(second.document).parent / "attachments/input.txt")
    advance(attachment, b"retained input\n")
    # Pick a separate source with the same title so the tombstone stem collides.
    first_result = session().discard_draft(first.identity, "Superseded")
    assert first_result.command.publication == "verified"
    before = session().snapshot
    second_result = session().discard_draft(second.identity, "Superseded")
    assert second_result.command.publication == "verified"
    after = second_result.snapshot
    assert installation.repository.parent(after) == before.revision
    retained = installation.repository.read_blobs(before.tree, (attachment,))
    assert retained[attachment] == b"retained input\n"
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
    assert saved["attachments"] == {attachment: sha256(b"retained input\n").hexdigest()}
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

    third = session().create_draft(CreateEntity("Graduated"))
    event = loads(graduated())
    event["data"]["source_id"] = third.identity
    advance(EVENTS, (dumps(event) + "\n").encode())
    before_refusal = session().snapshot
    rejected = invoke("draft", "discard", third.identity, "--reason", "Too late")
    assert rejected["local"] == "refused"
    assert "graduated" in str(rejected["evidence"]).lower()
    assert session().snapshot == before_refusal
    remote = Path(git(topology.local, "remote", "get-url", PLANNING_REMOTE))
    assert git(remote, "rev-parse", PLANNING) == before_refusal.revision

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
        == 2
    )
