"""Exercise semantic identity and dispatch authority on a shared Git store."""

from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import PurePosixPath

import pytest

from aitm_core.drafts import CreateEntity, Intake
from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.binding import EntityRef
from aitm_core.models.events import EventActor
from aitm_core.models.identity import (
    DeliveryTarget,
    DraftSource,
    PlanEntrySource,
    SourceDescription,
)
from aitm_core.models.operations import OperationOwner
from aitm_core.providers.backlog import GraduationIntent, IdentityResult, IssueRef
from aitm_core.providers.identity import (
    DispatchObservation,
    IdentityAuthority,
    IdentityConflict,
)
from aitm_core.services import preflight_policy
from tests.integration.test_c08 import PLANNING, git
from tests.integration.test_c08 import topology as topology
from tests.integration.test_c09 import cloned


class Issuer:
    def __init__(self, issuer):
        self.issuer = issuer
        self.sent = []
        self.observed = []
        self.issue = None
        self.compete = None
        self.fenced = False
        self.lose_reply = False
        self.unsupported = False

    def dispatch(self, reservation, claim):
        self.sent.append(claim)
        if self.lose_reply:
            self.issue = IssueRef(issuer=self.issuer, number=42)
            if self.compete is not None:
                self.compete()
            raise TimeoutError("response lost")
        if self.fenced:
            self.issue = IssueRef(issuer=self.issuer, number=43)
        return IdentityResult(
            reservation=reservation,
            status="issued" if self.issue is not None else "uncertain",
            issue=self.issue,
            evidence=("provider-readback",),
        )

    def observe(self, reservation, claim):
        self.observed.append(claim)
        return DispatchObservation(
            claim=claim.token,
            result=IdentityResult(
                reservation=reservation,
                status="unsupported"
                if self.unsupported
                else "issued"
                if self.issue is not None
                else "absent-with-proof",
                issue=self.issue,
                absence_proof="provider-definitive-absence"
                if self.issue is None and not self.unsupported
                else None,
                evidence=("provider-observation",),
            ),
            fence_proof="prior-sender-terminated" if self.fenced else None,
        )


def plan_entry(operation, issuer, *, key="same-entry", entry_digest="c" * 64):
    return GraduationIntent(
        operation_id=operation,
        shared=True,
        issuer=issuer,
        source=PlanEntrySource(
            parent=16,
            entry_key=key,
            design_digest="a" * 64,
            plan_digest="b" * 64,
            entry_digest=entry_digest,
            descriptor=SourceDescription(title="Build it", scope="One bounded change"),
        ),
        delivery_target=DeliveryTarget(
            repository="example/code", ref="refs/heads/trunk"
        ),
    )


def test_identity_once(topology, tmp_path):
    installation = topology.policy.installation
    other = cloned(topology, tmp_path).policy.installation
    issuer = Issuer(installation.issuer)
    left = IdentityAuthority(installation, issuer)
    right = IdentityAuthority(other, issuer)
    intent = plan_entry("original", installation.issuer)
    reservation = left.reserve_identity(intent)
    joined = right.reserve_identity(
        plan_entry("different-request", installation.issuer)
    )
    assert joined == reservation
    with pytest.raises(IdentityConflict, match="frozen"):
        right.reserve_identity(
            plan_entry("changed", installation.issuer, entry_digest="d" * 64)
        )

    issuer.lose_reply = True
    issuer.compete = lambda: (
        right.dispatch_or_observe(joined).issue.number == 42
        or pytest.fail("the second sender did not reconcile the first issue")
    )
    uncertain = left.dispatch_or_observe(reservation)
    assert uncertain.status in {"uncertain", "issued"}
    issuer.lose_reply = False
    issuer.compete = None
    assert left.dispatch_or_observe(reservation).issue.number == 42
    assert right.dispatch_or_observe(joined).issue.number == 42
    assert len(issuer.sent) == 1

    another = left.reserve_identity(
        plan_entry("second", installation.issuer, key="other")
    )
    issuer.issue = None
    issuer.unsupported = True
    assert left.dispatch_or_observe(another).status == "uncertain"
    assert right.cancel(another).status == "uncertain"
    assert len(issuer.sent) == 2
    issuer.unsupported = False
    assert right.dispatch_or_observe(another).status == "uncertain"
    assert len(issuer.sent) == 2
    issuer.fenced = True
    assert right.dispatch_or_observe(another).issue.number == 43
    assert len(issuer.sent) == 3
    assert issuer.sent[-1].generation == 2
    assert right.dispatch_or_observe(another).issue.number == 43

    with pytest.raises(IdentityConflict, match="prepared"):
        left.reserve_identity(
            GraduationIntent(
                operation_id="legacy",
                source_kind="draft",
                source_id="legacy",
                source_digest="a" * 64,
                issuer=installation.issuer,
                shared=True,
            )
        )
    foreign = replace(
        installation,
        issuer=installation.issuer.model_copy(update={"backlog_repository": "foreign"}),
    )
    with pytest.raises(IdentityConflict, match="issuer"):
        IdentityAuthority(foreign, issuer).reserve_identity(intent)
    policy = preflight_policy(installation).policy
    assert policy is not None
    repo = installation.repository
    draft = Intake(
        installation,
        repo.tip(),
        policy.source.digest,
        OperationOwner(actor=EventActor(kind="tool")),
        datetime(2026, 11, 27, tzinfo=UTC),
    ).create_draft(CreateEntity("Frozen draft"))
    snapshot = repo.tip()
    raw = repo.read_blobs(snapshot.tree, (draft.document,))[draft.document]
    assert raw is not None
    directory = PurePosixPath(draft.document).parent
    prepared = DraftSource(
        entity=EntityRef(identity=draft.identity, document=draft.document),
        snapshot=SourceSnapshot(commit=snapshot.revision, tree=snapshot.tree),
        draft_tree=git(repo.root, "rev-parse", f"{snapshot.tree}:{directory}"),
        document_digest=sha256(raw).hexdigest(),
    )
    draft_intent = GraduationIntent(
        operation_id="draft-intent",
        issuer=installation.issuer,
        shared=True,
        source=prepared,
        delivery_target=intent.delivery_target,
    )
    retained = left.reserve_identity(draft_intent)
    git(topology.planning, "pull", "--ff-only", "-q")
    topology.advance_planning(draft.document, raw + b"Edited after reservation\n")
    with pytest.raises(IdentityConflict, match="frozen source"):
        right.dispatch_or_observe(retained)
    assert len(issuer.sent) == 3

    foreign_issue = left.reserve_identity(
        plan_entry("foreign-issue", installation.issuer, key="unrelated")
    )
    with pytest.raises(IdentityConflict, match="another semantic reservation"):
        left.dispatch_or_observe(foreign_issue)
    assert right.dispatch_or_observe(another).issue.number == 43

    assert (
        git(topology.local, "for-each-ref", "--format=%(refname)", "refs/heads")
        == f"{PLANNING}\nrefs/heads/trunk"
    )
