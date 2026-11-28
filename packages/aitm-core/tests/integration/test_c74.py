"""Exercise installed entity authoring against a real local and shared planning store."""

from hashlib import sha256
from json import loads
from pathlib import Path, PurePosixPath

from aitm_core.models.binding import EntityRef
from aitm_core.services import preflight_policy
from aitm_core.setup.init import _record_installation
from aitm_core.store.workspace import Workspace
from tests.integration.test_c08 import git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import describe_args
from tests.integration.test_c16 import cli


def test_entity_authoring(topology, tmp_path):
    installation = topology.policy.installation
    policy = preflight_policy(installation).policy
    assert policy is not None
    _record_installation(installation, policy.revision)
    options = describe_args(topology, tmp_path)[-4:]
    root = topology.local
    repo = installation.repository

    idea = cli(root, "idea", "add", "Sketch", *options)["entity"]
    draft = cli(root, "draft", "new", "Build", *options)["entity"]
    opened = cli(root, "idea", "open", idea["identity"], "--session", "writer")
    assert opened["local"] == "completed", opened
    idea_binding = loads(opened["evidence"][0])
    attachment = str(PurePosixPath(draft["document"]).parent / "attachments/note.txt")
    opened_draft = cli(
        root,
        "draft",
        "open",
        draft["document"],
        "--session",
        "writer",
        "--path",
        attachment,
    )
    assert opened_draft["local"] == "completed", opened_draft
    draft_binding = loads(opened_draft["evidence"][0])
    assert idea_binding["scope"] == idea
    assert draft_binding["scope"] == draft
    assert draft_binding["branch"] is None

    def coordinates(entity, binding, *, holder="writer", generation=None):
        return (
            "--entity",
            entity["identity"],
            "--binding",
            binding["identity"],
            "--session",
            holder,
            "--generation",
            str(binding["generation"] if generation is None else generation),
        )

    idea_args = coordinates(idea, idea_binding)
    document = root / idea["document"]
    original = document.read_bytes()
    for body in (b"First edit\n", b"Second edit\n"):
        document.write_bytes(original + body)
        saved = cli(root, "sync", *idea_args)
        assert saved["publication"] == "verified", saved
        assert (
            repo.read_blobs(repo.tip().tree, (idea["document"],))[idea["document"]]
            == original + body
        )
    assert (
        cli(root, "sync", *coordinates(idea, idea_binding, holder="foreign"))["local"]
        == "conflict"
    )
    assert (
        cli(root, "sync", *coordinates(idea, idea_binding, generation=2))["local"]
        == "conflict"
    )
    assert (
        cli(root, "sync", *idea_args, "--path", "../escape.md")["local"]
        == "integrity-error"
    )
    document.write_bytes(
        original.replace(idea["identity"].encode(), b"forged") + b"Tampered\n"
    )
    assert cli(root, "sync", *idea_args)["local"] == "integrity-error"
    outside = tmp_path / "outside.md"
    outside.write_bytes(original + b"Outside\n")
    document.unlink()
    document.symlink_to(outside)
    assert cli(root, "sync", *idea_args)["local"] == "conflict"
    document.unlink()

    local_change = original + b"Unsynced idea\n"
    shared_change = original + b"Concurrent idea\n"
    document.write_bytes(local_change)
    git(topology.planning, "pull", "--ff-only", "-q")
    topology.advance_planning(idea["document"], shared_change)
    unbound = cli(root, "unbind", *idea_args)
    assert unbound["local"] == "conflict", unbound
    recovery = Path(unbound["recovery"])
    assert (recovery / "local" / idea["document"]).read_bytes() == local_change
    assert (recovery / "shared" / idea["document"]).read_bytes() == shared_change
    workspace = Workspace(installation)
    assert workspace.lookup(EntityRef.model_validate(idea)).active
    document.write_bytes(shared_change)
    assert cli(root, "unbind", *idea_args)["local"] == "completed"
    assert not workspace.lookup(EntityRef.model_validate(idea)).active

    from aitm_core.entities import finalize_entity_binding

    draft_ref = EntityRef.model_validate(draft)
    draft_args = coordinates(draft, draft_binding)
    draft_path = root / draft["document"]
    original_draft = draft_path.read_bytes() + b"Committed draft edit\n"
    draft_path.write_bytes(original_draft)
    attachment_path = root / attachment
    attachment_path.parent.mkdir()
    attachment_path.write_bytes(b"Committed attachment\n")
    assert cli(root, "sync", *draft_args)["publication"] == "verified"
    before = repo.tip()
    assert repo.read_blobs(before.tree, (draft["document"], attachment)) == {
        draft["document"]: original_draft,
        attachment: b"Committed attachment\n",
    }
    with workspace.lock():
        disposition = finalize_entity_binding(workspace, draft_ref, "graduated", before)
    assert disposition.binding == draft_binding["identity"]
    assert disposition.generation == draft_binding["generation"]
    assert disposition.source_digest == sha256(original_draft).hexdigest()
    assert repo.tip() == before
    assert workspace.lookup(draft_ref).active

    draft_path.write_bytes(original_draft + b"Unsynced draft\n")
    attachment_path.write_bytes(b"Unsynced attachment\n")
    result = cli(
        root, "draft", "discard", draft["identity"], "--reason", "Replaced", *options
    )
    assert result["local"] == "completed", result
    assert result["publication"] == "verified", result
    after = repo.tip()
    assert repo.parent(after) == before.revision
    (tombstone,) = git(
        root, "ls-tree", "-r", "--name-only", after.tree, ".aitm/drafts/discarded"
    ).splitlines()
    record = loads(repo.read_blobs(after.tree, (tombstone,))[tombstone])
    assert record["binding_disposition"]["binding"] == draft_binding["identity"]
    assert record["binding_disposition"]["generation"] == draft_binding["generation"]
    assert record["binding_disposition"]["outcome"] == "discarded"
    conflict = (
        workspace.state
        / "sync-recovery"
        / draft_binding["identity"]
        / result["operation_id"]
    )
    assert (
        conflict / "local" / draft["document"]
    ).read_bytes() == original_draft + b"Unsynced draft\n"
    assert (conflict / "shared" / draft["document"]).read_bytes() == original_draft
    assert (conflict / "local" / attachment).read_bytes() == b"Unsynced attachment\n"
    assert (conflict / "shared" / attachment).read_bytes() == b"Committed attachment\n"
    assert not workspace.lookup(draft_ref).active
    assert cli(root, "sync", *draft_args)["local"] == "conflict"
    assert draft_path.read_bytes() == original_draft + b"Unsynced draft\n"
    assert not git(root, "ls-tree", "-r", "--name-only", after.tree, ".aitm/stories")
