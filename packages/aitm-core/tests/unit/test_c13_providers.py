"""Provider contract tests that require neither Git nor a network client."""

import pytest
from pydantic import ValidationError

from aitm_core.models.attempts import SourceSnapshot
from aitm_core.models.common import (
    CommandResult,
    LocalOutcome,
    PublicationOutcome,
    RefObservation,
)
from aitm_core.models.config import BacklogIssuer
from aitm_core.models.operations import FinalizationIntent, ReadExpectation
from aitm_core.providers.backlog import (
    ActionKey,
    ActionResult,
    BacklogObservation,
    GraduationIntent,
    GraduationResult,
    IdentityReservation,
    IdentityResult,
    IssueRef,
    LocalGraduationAuthority,
    PublishedStory,
)
from aitm_core.providers.githost import (
    DeliveryRequest,
    DeliveryResult,
    FetchResult,
    ProtectionRules,
    ProtectResult,
    PublicationIntent,
    PublicationResult,
    RemoteRef,
    ReviewRequest,
    ReviewResult,
)
from aitm_core.store.gate import RefIdentity

HEAD = "a" * 40
TREE = "b" * 40
DIGEST = "c" * 64
ISSUER = BacklogIssuer(
    backlog="external", backlog_repository="org/project", numbering_namespace="issues"
)


def graduation_intent(*, shared: bool) -> GraduationIntent:
    return GraduationIntent(
        operation_id="graduate-1",
        source_kind="draft",
        source_id="draft-1",
        source_digest=DIGEST,
        issuer=ISSUER,
        shared=shared,
    )


def remote_target() -> RemoteRef:
    return RemoteRef(
        repository="org/planning",
        ref=RefIdentity("refs/heads/planning"),
        remote="origin",
    )


def test_uncertain_identity_cannot_be_used_as_proof_of_absence():
    reservation = IdentityReservation(
        intent=graduation_intent(shared=True), key="external-correlation"
    )
    uncertain = IdentityResult(
        reservation=reservation, status="uncertain", evidence=("request timed out",)
    )
    assert uncertain.issue is None
    assert uncertain.absence_proof is None

    with pytest.raises(ValidationError):
        IdentityResult(reservation=reservation, status="absent-with-proof")
    with pytest.raises(ValidationError):
        IdentityResult(
            reservation=reservation,
            status="uncertain",
            absence_proof="receipt:external-positive-absence",
        )

    absent = IdentityResult(
        reservation=reservation,
        status="absent-with-proof",
        absence_proof="receipt:external-positive-absence",
    )
    assert absent.absence_proof == "receipt:external-positive-absence"


@pytest.mark.parametrize("status", ["reserved", "failed", "unsupported"])
def test_nonissued_identity_statuses_cannot_expose_an_issue(status):
    reservation = IdentityReservation(intent=graduation_intent(shared=True), key="key")
    with pytest.raises(ValidationError):
        IdentityResult(
            reservation=reservation,
            status=status,
            issue=IssueRef(issuer=ISSUER, number=42),
        )
    result = IdentityResult(reservation=reservation, status=status)
    assert result.issue is None


def test_external_issuance_is_pending_finalization_and_keeps_issuer_scope():
    reservation = IdentityReservation(intent=graduation_intent(shared=True), key="key")
    wrong_issuer = BacklogIssuer(
        backlog="external",
        backlog_repository="org/unrelated",
        numbering_namespace="issues",
    )
    for issue in (None, IssueRef(issuer=wrong_issuer, number=42)):
        with pytest.raises(ValidationError):
            IdentityResult(reservation=reservation, status="issued", issue=issue)

    result = IdentityResult(
        reservation=reservation,
        status="issued",
        issue=IssueRef(issuer=ISSUER, number=42),
    )
    assert result.pending_finalization
    assert result.issue.issuer.backlog_repository == "org/project"
    assert result.issue.issuer.numbering_namespace == "issues"
    with pytest.raises(ValidationError):
        result.issue.number = 43


@pytest.mark.parametrize(
    ("shared", "publication", "exposes_identity"),
    [
        (True, PublicationOutcome.PENDING, False),
        (True, PublicationOutcome.VERIFIED, True),
        (False, PublicationOutcome.NOT_APPLICABLE, True),
    ],
)
def test_local_graduation_only_exposes_an_authoritative_number(
    shared, publication, exposes_identity
):
    intent = graduation_intent(shared=shared)
    result = CommandResult(
        operation_id="graduate-1", local=LocalOutcome.COMPLETED, publication=publication
    )
    issue = IssueRef(issuer=ISSUER, number=42) if exposes_identity else None
    assert GraduationResult(intent=intent, command=result, issue=issue).issue == issue
    invalid_issue = None if exposes_identity else IssueRef(issuer=ISSUER, number=42)
    with pytest.raises(ValidationError):
        GraduationResult(intent=intent, command=result, issue=invalid_issue)


def test_local_result_cannot_mark_shared_graduation_publication_not_applicable():
    command = CommandResult(operation_id="graduate-1", local=LocalOutcome.COMPLETED)
    with pytest.raises(ValidationError):
        GraduationResult(intent=graduation_intent(shared=True), command=command)


def test_local_graduation_uses_existing_finalization_contract():
    class FakeAuthority:
        def graduate(
            self, intent: GraduationIntent, finalization: FinalizationIntent
        ) -> GraduationResult:
            assert finalization.kind == "ordinary-graduation"
            assert finalization.related_preconditions[0].digest == DIGEST
            command = CommandResult(
                operation_id=intent.operation_id, local=LocalOutcome.COMPLETED
            )
            return GraduationResult(
                intent=intent,
                command=command,
                issue=IssueRef(issuer=intent.issuer, number=42),
            )

    authority: LocalGraduationAuthority = FakeAuthority()
    finalization = FinalizationIntent(
        kind="ordinary-graduation",
        version=1,
        related_preconditions=(
            ReadExpectation(path=".aitm/drafts/draft-1/story.md", digest=DIGEST),
        ),
        payload=b"{}",
    )
    result = authority.graduate(graduation_intent(shared=False), finalization)
    assert result.issue.number == 42
    assert result.command.publication == PublicationOutcome.NOT_APPLICABLE


def test_backlog_unobservable_issue_is_not_a_missing_issue():
    issue = IssueRef(issuer=ISSUER, number=42)
    for status in ("pending", "unsupported"):
        result = BacklogObservation(issue=issue, status=status)
        assert result.status == status
        assert result.is_present is None
    with pytest.raises(ValidationError):
        BacklogObservation(issue=issue, status="absent")
    observed = BacklogObservation(
        issue=issue, status="present", evidence=("receipt:issue-observation",)
    )
    assert observed.is_present is True


def test_projection_retains_the_published_story_and_action_identity():
    published = PublishedStory(
        issue=IssueRef(issuer=ISSUER, number=42), planning_commit=HEAD
    )
    action = ActionKey(operation_id="operation-1", action_id="provider.project/v1")
    result = ActionResult(
        publication=published,
        action=action,
        status="unsupported",
        evidence=("No board",),
    )
    assert result.publication.issue.number == 42
    assert result.action.operation_id == "operation-1"
    assert result.status == "unsupported"


def test_publication_verification_requires_the_observed_ref_and_operation_witness():
    target = remote_target()
    intent = PublicationIntent(
        operation_id="operation-1", target=target, candidate=HEAD
    )
    observed = RefObservation(
        ref=target.ref.name, observed_commit=HEAD, remote="origin"
    )
    result = PublicationResult(
        intent=intent,
        status="verified",
        observed=observed,
        contained_operation_id="operation-1",
        evidence=("receipt:operation-in-observed-history",),
    )
    assert result.observed.observed_commit == HEAD
    assert result.intent.target.repository == "org/planning"
    assert result.contained_operation_id == "operation-1"
    assert PublicationResult.model_validate_json(result.model_dump_json()) == result

    for overrides in (
        {"observed": None},
        {"observed": RefObservation(ref=target.ref.name, observed_commit=None)},
        {
            "observed": RefObservation(
                ref=target.ref.name, observed_commit="unverified-tip"
            )
        },
        {
            "observed": RefObservation(
                ref="refs/heads/other", observed_commit=HEAD, remote="origin"
            )
        },
        {
            "observed": RefObservation(
                ref=target.ref.name, observed_commit=HEAD, remote="wrong-remote"
            )
        },
        {"observed": RefObservation(ref=target.ref.name, observed_commit=HEAD)},
        {"contained_operation_id": None},
        {"contained_operation_id": "operation-2"},
        {"evidence": ()},
        {"version": 2},
    ):
        with pytest.raises(ValidationError):
            PublicationResult.model_validate({**dict(result), **overrides})


@pytest.mark.parametrize("status", ["pending", "unsupported"])
def test_unverified_publication_has_no_containment_claim(status):
    target = remote_target()
    intent = PublicationIntent(
        operation_id="operation-1", target=target, candidate=HEAD
    )
    observed = RefObservation(
        ref=target.ref.name, observed_commit=HEAD, remote="origin"
    )
    pending = PublicationResult(intent=intent, status=status, observed=observed)
    assert pending.contained_operation_id is None
    with pytest.raises(ValidationError):
        PublicationResult(
            intent=intent,
            status=status,
            observed=observed,
            contained_operation_id="operation-1",
        )


def test_missing_git_host_ref_requires_a_positive_observation():
    target = remote_target()
    missing = RefObservation(ref=target.ref.name, observed_commit=None, remote="origin")
    with pytest.raises(ValidationError):
        FetchResult(target=target, status="observed", observation=missing)
    result = FetchResult(
        target=target,
        status="observed",
        observation=missing,
        evidence=("receipt:authenticated-ref-is-absent",),
    )
    assert result.observation.observed_commit is None
    assert FetchResult(target=target, status="pending").observation is None


def test_git_host_fetch_preserves_observed_ref_coordinates():
    target = remote_target()
    result = FetchResult(
        target=target,
        status="observed",
        observation=RefObservation(
            ref=target.ref.name, observed_commit=HEAD, remote="origin"
        ),
    )
    assert result.observation.observed_commit == HEAD
    with pytest.raises(ValidationError):
        FetchResult(
            target=target,
            status="observed",
            observation=RefObservation(
                ref="refs/heads/other", observed_commit=HEAD, remote="origin"
            ),
        )
    with pytest.raises(ValidationError):
        FetchResult(target=target, status="observed")
    for status in ("pending", "unsupported"):
        assert FetchResult(target=target, status=status).observation is None


@pytest.mark.parametrize("capability", ["delivery", "review"])
def test_git_host_observations_preserve_pins_and_require_positive_evidence(capability):
    request_type, result_type = {
        "delivery": (DeliveryRequest, DeliveryResult),
        "review": (ReviewRequest, ReviewResult),
    }[capability]
    request = request_type(
        attempt="attempt-1",
        source=SourceSnapshot(commit=HEAD, tree=TREE),
        target=remote_target(),
        target_commit=HEAD,
        policy_digest=DIGEST,
    )
    for status in ("pending", "rejected", "unsupported"):
        result = result_type(
            request=request, status=status, evidence=("receipt:observation",)
        )
        assert result.status == status
        with pytest.raises(ValidationError):
            result_type(request=request, status=status)
    with pytest.raises(ValidationError):
        result_type(request=request, status="verified")
    verified = result_type(
        request=request, status="verified", evidence=("receipt:qualified-observation",)
    )
    assert verified.request.source.tree == TREE
    assert verified.request.target.ref.name == "refs/heads/planning"


def test_protection_manual_outcome_requires_instructions():
    rules = ProtectionRules()
    target = remote_target()
    with pytest.raises(ValidationError):
        ProtectResult(target=target, rules=rules, status="manual")
    manual = ProtectResult(
        target=target,
        rules=rules,
        status="manual",
        instructions=("Require a linear history and disallow deletion.",),
        settings_url="https://example.invalid/settings",
    )
    assert manual.instructions
    assert manual.settings_url == "https://example.invalid/settings"
    for status in ("applied", "already-protected"):
        with pytest.raises(ValidationError):
            ProtectResult(target=target, rules=rules, status=status)
        observed = ProtectResult(
            target=target,
            rules=rules,
            status=status,
            evidence=("receipt:branch-settings",),
        )
        assert observed.status == status
