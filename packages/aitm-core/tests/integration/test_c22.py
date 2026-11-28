"""Exercise atomic graduation and relationship operations against real Git."""

from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from json import loads
from pathlib import PurePosixPath

import pytest

from aitm_core.drafts import CreateEntity, Intake
from aitm_core.entities import open_entity
from aitm_core.graduation import (
    FinalizerRegistry,
    GraduationService,
    ordinary_finalization,
)
from aitm_core.models.binding import EntityRef
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.events import EventActor
from aitm_core.models.identity import (
    DeliveryTarget,
    FrozenFinalization,
    PlanEntrySource,
    SourceDescription,
)
from aitm_core.models.operations import (
    FinalizationIntent,
    OperationOwner,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from aitm_core.providers.backlog import GraduationIntent, IssueRef
from aitm_core.providers.identity import IdentityAuthority
from aitm_core.relationships import GraphConflict, LinkRequest, read_graph
from aitm_core.services import preflight_policy
from aitm_core.store.workspace import Workspace
from tests.integration.test_c08 import DEFAULT, WORKFLOW, commit_file, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c20 import Issuer
from tests.unit.test_c15 import graduated
from tests.unit.test_c90_profile import WORKFLOW as PROFILE

STAMP = "2026-11-27T12:00:00Z"
OWNER = OperationOwner(actor=EventActor(kind="tool", harness="fixture"))


def install_profile(topology):
    commit_file(
        topology.code, WORKFLOW, PROFILE.replace('"plan"', '"backlog"').encode()
    )
    git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")


def create_draft(installation, title):
    repo = installation.repository
    policy = preflight_policy(installation).policy
    assert policy is not None
    created = Intake(
        installation,
        repo.tip(),
        policy.source.digest,
        OWNER,
        datetime(2026, 11, 27, tzinfo=UTC),
    ).create_draft(CreateEntity(title, "Original draft body\n"))
    assert created.command.publication == "verified"
    return EntityRef(identity=created.identity, document=created.document)


def test_graduate_links(topology):
    from json import dumps

    install_profile(topology)
    install = topology.policy.installation
    repo = install.repository
    epic = loads(graduated())
    epic["data"]["kind"] = "epic"
    topology.advance_planning(story_event_path(16), (dumps(epic) + "\n").encode())
    draft = create_draft(install, "Promote me")
    attachment = str(PurePosixPath(draft.document).parent / "attachments/a.txt")
    git(topology.planning, "pull", "--ff-only", "-q")
    topology.advance_planning(attachment, b"Attached fixture")
    provider = Issuer(install.issuer)
    provider.fenced = True
    provider.issue = None
    authority = IdentityAuthority(install, provider)
    service = GraduationService(install, OWNER, stamp=STAMP)
    intent = service.prepare_draft(
        draft.identity,
        "semantic-op",
        DeliveryTarget(repository=install.code_repository, ref=DEFAULT),
        parent=16,
    )
    assert intent.parent == 16
    lease = open_entity(Workspace(install), draft, "writer")
    local = repo.root / draft.document
    frozen = local.read_bytes()
    local.write_bytes(frozen + b"Unpublished edit\n")
    before = repo.tip()
    reservation = authority.reserve_identity(intent)
    issued = authority.dispatch_or_observe(reservation)
    assert issued.issue is not None and issued.issue.number == 43
    pre_finalization = repo.tip()
    result = service.finalize_external_identity(
        authority, reservation, ordinary_finalization()
    )
    assert result.command.local == LocalOutcome.COMPLETED
    assert result.command.publication == PublicationOutcome.VERIFIED
    assert repo.parent(repo.tip()) == pre_finalization.revision
    graph = read_graph(repo, repo.tip())
    assert graph.stories[43].relationships.parent == 16
    assert graph.stories[16].relationships.children == (43,)
    assert graph.stories[43].graduation.kind == "story"
    assert graph.stories[43].graduation.delivery_target == intent.delivery_target
    assert graph.stories[43].workflow_state.state_id == "backlog"
    root = ".aitm/stories/000/43"
    actual = repo.read_blobs(
        repo.tip().tree,
        (draft.document, f"{root}/draft.md", f"{root}/attachments/a.txt"),
    )
    assert actual == {
        draft.document: None,
        f"{root}/draft.md": frozen,
        f"{root}/attachments/a.txt": b"Attached fixture",
    }
    assert local.read_bytes() == frozen + b"Unpublished edit\n"
    assert not Workspace(install).lookup(draft).active
    assert lease.scope == draft
    assert before != repo.tip()
    assert (
        service.finalize_external_identity(
            authority, reservation, ordinary_finalization()
        ).command.local
        == LocalOutcome.COMPLETED
    )

    assert (
        service.link(
            LinkRequest(story=43, other=16, relation="blocked-by")
        ).command.local
        == LocalOutcome.COMPLETED
    )
    pinned = repo.tip()
    with pytest.raises(GraphConflict, match="cycle"):
        service.link(LinkRequest(story=16, other=43, relation="blocked-by"))
    assert repo.tip() == pinned
    assert len(provider.sent) == 1

    finalization = FinalizationIntent(
        kind="fixture.parent-proof",
        version=1,
        payload=b"typed fixture",
        related_preconditions=(
            ReadExpectation(
                path=".aitm/README.md", digest=sha256(b"Expected").hexdigest()
            ),
        ),
    )
    registry = FinalizerRegistry().register_finalizer(
        finalization.kind,
        finalization.version,
        lambda _request, _child, _snapshot: RelatedWriteSet(read_set=()),
    )
    pinned_service = replace(service, registry=registry)
    source = PlanEntrySource(
        parent=16,
        entry_key="bounded",
        design_digest="a" * 64,
        plan_digest="b" * 64,
        entry_digest="c" * 64,
        descriptor=SourceDescription(
            title="Plan entry",
            scope="Accepted scope",
            actor="maintainer",
            want="a generated child",
            so_that="it can be tracked",
        ),
    )
    entry_intent = GraduationIntent(
        operation_id="plan-entry",
        issuer=install.issuer,
        shared=True,
        source=source,
        delivery_target=intent.delivery_target,
        finalization=FrozenFinalization.from_intent(finalization),
    )
    provider.fenced = False
    provider.issue = IssueRef(issuer=install.issuer, number=44)
    entry = authority.reserve_identity(entry_intent)
    held = pinned_service.finalize_external_identity(authority, entry, finalization)
    assert held.command.local == LocalOutcome.CONFLICT
    assert held.command.publication == PublicationOutcome.PENDING
    assert authority.dispatch_or_observe(entry).issue == provider.issue
    assert 44 not in read_graph(repo, repo.tip()).stories
    git(topology.planning, "pull", "--ff-only", "-q")
    topology.advance_planning(".aitm/README.md", b"Expected")
    result = pinned_service.finalize_external_identity(authority, entry, finalization)
    assert result.command.local == LocalOutcome.COMPLETED
    child = read_graph(repo, repo.tip()).stories[44]
    assert child.graduation.source_kind == "plan-entry"
    assert child.description.title == "Plan entry"
    path = ".aitm/stories/000/44/draft.md"
    assert repo.read_blobs(repo.tip().tree, (path,))[path] is None
    assert len(provider.sent) == 2
    assert (
        git(repo.root, "for-each-ref", "--format=%(refname)", "refs/heads")
        == "refs/heads/records\nrefs/heads/trunk"
    )

    drifted = create_draft(install, "Workflow drift")
    candidate_intent = service.prepare_draft(
        drifted.identity, "workflow-drift", intent.delivery_target
    )
    pinned_policy = service.policy()
    old_tip = service.snapshot(pinned_policy)
    workspace = Workspace(install)
    with workspace.lock():
        candidate = service.build(
            candidate_intent,
            IssueRef(issuer=install.issuer, number=45),
            old_tip,
            pinned_policy,
            ordinary_finalization(),
            workspace,
            operation="workflow-drift",
        )
        changed_profile = PROFILE.replace('"plan"', '"backlog"').replace(
            "Ready to implement", "New Backlog"
        )
        commit_file(topology.code, WORKFLOW, changed_profile.encode())
        git(topology.code, "push", "-q", "origin", f"HEAD:{DEFAULT}")
        rejected = service.commit(candidate, old_tip)
    assert rejected.command.local == LocalOutcome.CONFLICT
    assert "workflow changed" in " ".join(rejected.command.evidence)
    assert repo.tip() == old_tip
