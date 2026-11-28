"""Durable semantic reservation and publication-qualified external dispatch."""

from dataclasses import dataclass
from hashlib import sha256
from json import dumps
from pathlib import PurePosixPath
from typing import Literal, Protocol
from uuid import uuid4

from pydantic import Field

from aitm_core.entities import entity_matches
from aitm_core.models.common import LocalOutcome, PublicationOutcome
from aitm_core.models.config import BacklogIssuer, Name
from aitm_core.models.events import DIGEST, EventActor
from aitm_core.models.identity import DraftSource, IdentityFact
from aitm_core.models.operations import (
    AuthorityOrigin,
    BlobWrite,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    Positive,
    PreflightOutcome,
    PreflightResult,
    ReadExpectation,
    RelatedWriteSet,
    WriteAuthorization,
)
from aitm_core.providers.backlog import (
    GraduationIntent,
    IdentityReservation,
    IdentityResult,
    IssueRef,
)
from aitm_core.services import ServicePorts, mutate, preflight_policy
from aitm_core.store.backend import Snapshot
from aitm_core.store.continuity import ContinuityStatus
from aitm_core.store.fetch import Freshness
from aitm_core.store.installation import Installation
from aitm_core.store.objects import GitCommandError


class IdentityConflict(ValueError):
    """The semantic reservation or dispatch authority cannot be established."""


class ReservationRecord(IdentityFact):
    schema_version: Literal["aitm.identity-reservation/v1"] = (
        "aitm.identity-reservation/v1"
    )
    reservation: IdentityReservation


class DispatchObservation(IdentityFact):
    claim: Name
    result: IdentityResult
    fence_proof: Name | None = None


class DispatchClaim(IdentityFact):
    schema_version: Literal["aitm.identity-dispatch/v1"] = "aitm.identity-dispatch/v1"
    key: Name
    generation: Positive
    token: Name
    prior: DispatchObservation | None = None
    origin_digest: DIGEST | None = Field(
        default=None, exclude_if=lambda value: value is None
    )


class IssuedRecord(IdentityFact):
    schema_version: Literal["aitm.identity-issue/v1"] = "aitm.identity-issue/v1"
    claim: Name
    result: IdentityResult


class IssueOwner(IdentityFact):
    schema_version: Literal["aitm.identity-owner/v1"] = "aitm.identity-owner/v1"
    issue: IssueRef
    key: DIGEST


def _owner_path(issue: IssueRef) -> str:
    owner = sha256(
        dumps(issue.model_dump(mode="json"), sort_keys=True).encode()
    ).hexdigest()
    return f"{reservation_root(owner)}/owner.json"


class IdentityProvider(Protocol):
    issuer: BacklogIssuer

    def dispatch(
        self, reservation: IdentityReservation, claim: DispatchClaim
    ) -> IdentityResult: ...
    def observe(
        self, reservation: IdentityReservation, claim: DispatchClaim
    ) -> DispatchObservation:
        """A fence proof certifies no delayed request from this claim can issue."""
        ...


class FencedIdentityProvider(IdentityProvider, Protocol):
    def verify_sender_fence(
        self, reservation: IdentityReservation, claim: DispatchClaim, proof: str
    ) -> bool:
        """Verify an enforced provider guarantee covering requests already in flight."""
        ...


def _qualified_stopped_absence(provider, reservation, claim, observation):
    if (
        observation is None
        or observation.claim != claim.token
        or observation.result.reservation != reservation
        or observation.result.status != "absent-with-proof"
        or not observation.fence_proof
    ):
        return False
    verify = getattr(provider, "verify_sender_fence", None)
    return (
        callable(verify) and verify(reservation, claim, observation.fence_proof) is True
    )


def reservation_root(key: str) -> str:
    return f".aitm/identity/{key}"


def validate_identity_record(path: str, content: bytes) -> None:
    key, name = path.split("/")[-2:]
    if name == "reservation.json":
        reservation = ReservationRecord.model_validate_json(content).reservation
        source = reservation.intent.source
        if source is None or source.semantic_key != key or reservation.key != key:
            raise ValueError("reservation is outside its prepared semantic source")
    elif name == "owner.json":
        owner = IssueOwner.model_validate_json(content)
        if path != _owner_path(owner.issue):
            raise ValueError("issuer identity is outside its immutable ownership key")
    elif name == "issue.json":
        record = IssuedRecord.model_validate_json(content)
        if record.result.status != "issued" or record.result.reservation.key != key:
            raise ValueError("issued evidence is outside its reservation")
    else:
        claim = DispatchClaim.model_validate_json(content)
        if (
            claim.key != key
            or name != f"claim-{claim.generation}.json"
            or (claim.generation > 1) != (claim.prior is not None)
            or (
                claim.prior is not None
                and (
                    claim.prior.result.reservation.key != key
                    or claim.prior.result.status != "absent-with-proof"
                    or not claim.prior.fence_proof
                )
            )
        ):
            raise ValueError("invalid dispatch claim or predecessor proof")


@dataclass(frozen=True, slots=True)
class _View:
    snapshot: Snapshot
    policy: str


@dataclass(frozen=True, slots=True)
class _State:
    reservation: IdentityReservation | None
    claim: DispatchClaim | None
    issue: IssuedRecord | None


@dataclass(frozen=True, slots=True)
class StoppedIdentityObservation:
    snapshot: Snapshot
    reads: tuple[str, ...]
    claim: DispatchClaim | None = None
    issue: IssueRef | None = None
    absence: DispatchObservation | None = None


class IdentityAuthority:
    def __init__(self, installation: Installation, provider: IdentityProvider):
        self.installation = installation
        self.provider = provider
        self.repo = installation.repository

    def _view(self, intent: GraduationIntent) -> _View:
        if (
            intent.issuer != self.installation.issuer
            or intent.issuer != self.provider.issuer
        ):
            raise IdentityConflict(
                "The selected issuer differs from the anchored provider."
            )
        if intent.shared != (self.installation.store.planning_remote is not None):
            raise IdentityConflict(
                "The intent does not match the anchored sharing mode."
            )
        prepared = preflight_policy(self.installation)
        if (
            prepared.outcome != LocalOutcome.COMPLETED
            or prepared.policy is None
            or prepared.views.code_freshness
            not in {Freshness.FRESH, Freshness.LOCAL_ONLY}
        ):
            raise IdentityConflict("Current committed authority is unavailable.")
        revision = prepared.views.planning.observed_commit
        if intent.shared:
            shared = prepared.views.shared
            if shared is None or shared.status != ContinuityStatus.VERIFIED:
                raise IdentityConflict(
                    "Verified shared identity authority is unavailable."
                )
            revision = shared.valid_tip
        if revision is None:
            raise IdentityConflict("The authoritative planning tip is unavailable.")
        return _View(self.repo.read_tree(revision), prepared.policy.source.digest)

    def _state(self, view: _View, key: str) -> _State:
        root = reservation_root(key)
        names = self.repo._git(
            "ls-tree", "-r", "--name-only", "-z", view.snapshot.tree, root
        )
        paths = tuple(part.decode() for part in names.split(b"\0") if part)
        blobs = self.repo.read_blobs(view.snapshot.tree, paths)
        reservation = None
        claims = {}
        issue = None
        for path, raw in blobs.items():
            if path in {f"{root}/graduated.json", f"{root}/projection.json"}:
                continue
            assert raw is not None
            validate_identity_record(path, raw)
            if path == f"{root}/reservation.json":
                reservation = ReservationRecord.model_validate_json(raw).reservation
            elif path == f"{root}/issue.json":
                issue = IssuedRecord.model_validate_json(raw)
            else:
                claim = DispatchClaim.model_validate_json(raw)
                claims[claim.generation] = claim
        predecessor = None
        for generation, claim in sorted(claims.items()):
            if generation == 1:
                predecessor = claim
                continue
            if (
                predecessor is None
                or generation != predecessor.generation + 1
                or claim.prior is None
                or claim.prior.claim != predecessor.token
                or claim.prior.result.reservation != reservation
            ):
                raise IdentityConflict(
                    "The retained dispatch claim sequence is inconsistent."
                )
            predecessor = claim
        if (predecessor is not None and reservation is None) or (
            issue is not None
            and (
                predecessor is None
                or issue.claim != predecessor.token
                or issue.result.reservation != reservation
            )
        ):
            raise IdentityConflict("The retained identity evidence is inconsistent.")
        if issue is not None:
            assert issue.result.issue is not None
            owner = self._issue_owner(view, issue.result.issue)
            if owner is None or owner.key != key:
                raise IdentityConflict(
                    "Issued evidence lacks its matching ownership claim."
                )
        return _State(reservation, predecessor, issue)

    def _issue_owner(self, view: _View, issue: IssueRef) -> IssueOwner | None:
        path = _owner_path(issue)
        raw = self.repo.read_blobs(view.snapshot.tree, (path,))[path]
        if raw is None:
            return None
        validate_identity_record(path, raw)
        return IssueOwner.model_validate_json(raw)

    def _check_source(self, view: _View, intent: GraduationIntent) -> None:
        source = intent.source
        if source is None or intent.delivery_target is None:
            raise IdentityConflict(
                "Graduation requires a prepared source and delivery target."
            )
        self.repo._git("check-ref-format", intent.delivery_target.ref)
        if isinstance(source, DraftSource):
            folder = str(PurePosixPath(source.entity.document).parent)
            original = self.repo.read_tree(source.snapshot.commit)
            if (
                original.tree != source.snapshot.tree
                or self.repo._run(
                    "merge-base",
                    "--is-ancestor",
                    original.revision,
                    view.snapshot.revision,
                ).returncode
                != 0
            ):
                raise IdentityConflict(
                    "The frozen draft snapshot is outside the planning history."
                )
            for tree in (original.tree, view.snapshot.tree):
                raw = self.repo.read_blobs(tree, (source.entity.document,))[
                    source.entity.document
                ]
                found = self.repo._run("rev-parse", "--verify", f"{tree}:{folder}")
                if (
                    raw is None
                    or not entity_matches(source.entity, raw)
                    or sha256(raw).hexdigest() != source.document_digest
                    or found.returncode != 0
                    or found.stdout.decode().strip() != source.draft_tree
                ):
                    raise IdentityConflict(
                        "The current draft differs from its frozen source."
                    )

    def _write(
        self,
        view: _View,
        path: str,
        value: IdentityFact,
        identity: str,
        pin: tuple[str, ...] = (),
        *,
        ownership: IssueOwner | None = None,
        origin_pin: ReadExpectation | None = None,
        claim_intent: GraduationIntent | None = None,
    ) -> bool:
        payload = value.model_dump_json().encode()
        writes = {path: payload}
        if ownership is not None:
            writes[_owner_path(ownership.issue)] = ownership.model_dump_json().encode()
        origin = (origin_pin.path,) if origin_pin is not None else ()
        bodies = self.repo.read_blobs(view.snapshot.tree, (*writes, *pin, *origin))
        if any(bodies[destination] is not None for destination in writes):
            return False
        reads = tuple(
            ReadExpectation(
                path=key, digest=sha256(raw).hexdigest() if raw is not None else None
            )
            for key, raw in bodies.items()
        )
        if origin_pin is not None and origin_pin not in reads:
            return False
        change = RelatedWriteSet(
            read_set=reads,
            writes=tuple(
                BlobWrite(path=destination, content=raw)
                for destination, raw in writes.items()
            ),
        )
        owner = OperationOwner(actor=EventActor(kind="tool", harness="core-identity"))
        operation = Operation(
            operation_id=identity,
            owner=owner,
            policy_digest=view.policy,
            category=OperationCategory.NORMAL,
            intent=FinalizationIntent(
                kind="core.identity.record",
                version=1,
                related_preconditions=reads,
                payload=payload,
            ),
            change=change,
        )

        def authorize(candidate, writes):
            return WriteAuthorization(
                allowed=candidate == owner and writes == change,
                origin=AuthorityOrigin.REGISTERED,
            )

        def preflight(context):
            from aitm_core.rules.expansion import expansion_claim_pin

            allowed = (
                isinstance(value, DispatchClaim)
                and origin_pin is not None
                and value.origin_digest == origin_pin.digest
                and claim_intent is not None
                and context.operation == operation
                and expansion_claim_pin(self.repo, context.snapshot, claim_intent)
                == origin_pin
            )
            return PreflightResult(
                outcome=PreflightOutcome.PASSED
                if allowed
                else PreflightOutcome.BLOCKED,
                origin=AuthorityOrigin.REGISTERED,
            )

        result = mutate(
            self.installation,
            operation,
            view.snapshot,
            ports=ServicePorts(
                write_authorization=authorize,
                attempt_preflight=preflight if origin_pin is not None else None,
            ),
        ).command
        expected = (
            PublicationOutcome.VERIFIED
            if self.installation.store.planning_remote
            else PublicationOutcome.NOT_APPLICABLE
        )
        return result.local == LocalOutcome.COMPLETED and result.publication == expected

    def reserve_identity(self, intent: GraduationIntent) -> IdentityReservation:
        if intent.source is None or intent.delivery_target is None:
            raise IdentityConflict(
                "Graduation requires a prepared source and delivery target."
            )
        key = intent.source.semantic_key
        path = f"{reservation_root(key)}/reservation.json"
        view = self._view(intent)
        graduated = f"{reservation_root(key)}/graduated.json"
        existing = self._state(view, key).reservation
        if existing is None:
            if (
                self.repo.read_blobs(view.snapshot.tree, (graduated,))[graduated]
                is not None
            ):
                raise IdentityConflict(
                    "The prepared source already has a permanent story."
                )
            self._check_source(view, intent)
            proposal = IdentityReservation(intent=intent, key=key)
            self._write(
                view,
                path,
                ReservationRecord(reservation=proposal),
                uuid4().hex,
                (graduated,),
            )
            existing = self._state(self._view(intent), key).reservation
        if existing is None:
            raise IdentityConflict("The semantic reservation has not been verified.")
        if existing.intent.model_dump(exclude={"operation_id"}) != intent.model_dump(
            exclude={"operation_id"}
        ):
            raise IdentityConflict(
                "The entity is already reserved against another frozen intent."
            )
        return existing

    def _pending(self, reservation: IdentityReservation, reason: str) -> IdentityResult:
        return IdentityResult(
            reservation=reservation, status="uncertain", evidence=(reason,)
        )

    def _observe(
        self, reservation: IdentityReservation, claim: DispatchClaim
    ) -> DispatchObservation:
        try:
            evidence = self.provider.observe(reservation, claim)
        except OSError:
            return DispatchObservation(
                claim=claim.token,
                result=self._pending(
                    reservation, "Provider observation was unavailable."
                ),
            )
        if (
            not isinstance(evidence, DispatchObservation)
            or evidence.claim != claim.token
            or evidence.result.reservation != reservation
        ):
            raise IdentityConflict(
                "Provider observation does not match the retained claim."
            )
        return evidence

    def _observation_ref(
        self, reservation: IdentityReservation, claim: DispatchClaim
    ) -> str:
        scope = sha256(
            f"{self.installation.store.store_uuid}\0{reservation.key}\0{claim.token}".encode()
        ).hexdigest()
        return f"refs/aitm/issuer-observations/{scope}"

    def _retained_observation(
        self, reservation: IdentityReservation, claim: DispatchClaim
    ) -> IssuedRecord | None:
        reference = self._observation_ref(reservation, claim)
        observed = self.repo._run("rev-parse", "--verify", "--quiet", reference)
        if observed.returncode == 1:
            return None
        if observed.returncode:
            raise GitCommandError("rev-parse", observed.stderr)
        raw = self.repo._git("cat-file", "blob", observed.stdout.decode().strip())
        record = IssuedRecord.model_validate_json(raw)
        if (
            record.claim != claim.token
            or record.result.reservation != reservation
            or record.result.status != "issued"
        ):
            raise IdentityConflict(
                "Local issuance evidence disagrees with the retained claim."
            )
        return record

    def _retain_issue(
        self, result: IdentityResult, claim: DispatchClaim
    ) -> IdentityResult:
        reservation = result.reservation
        if not result.evidence:
            raise IdentityConflict("An issued identity requires provider evidence.")
        record = IssuedRecord(claim=claim.token, result=result)
        retained = self._retained_observation(reservation, claim)
        if retained is None:
            oid = self.repo._git(
                "hash-object", "-w", "--stdin", data=record.model_dump_json().encode()
            )
            reference = self._observation_ref(reservation, claim)
            created = self.repo._run(
                "update-ref",
                "--no-deref",
                reference,
                oid.decode().strip(),
                "0" * self.repo.oid_length,
            )
            if created.returncode:
                retained = self._retained_observation(reservation, claim)
                if retained is None:
                    raise GitCommandError("update-ref", created.stderr)
        if retained is not None:
            if retained.result.issue != result.issue:
                raise IdentityConflict(
                    "The issuer returned conflicting permanent identities."
                )
            record = retained
        root = reservation_root(reservation.key)
        view = self._view(reservation.intent)
        path = f"{root}/issue.json"
        assert result.issue is not None
        owner = self._issue_owner(view, result.issue)
        if owner is not None and owner.key != reservation.key:
            raise IdentityConflict(
                "The provider issue belongs to another semantic reservation."
            )
        state = self._state(view, reservation.key)
        if state.claim != claim or state.reservation != reservation:
            raise IdentityConflict(
                "Issuance does not match the current reservation and claim."
            )
        if state.issue is None:
            self._write(
                view,
                path,
                record,
                uuid4().hex,
                (
                    f"{root}/reservation.json",
                    f"{root}/claim-{claim.generation}.json",
                    f"{root}/claim-{claim.generation + 1}.json",
                ),
                ownership=IssueOwner(issue=result.issue, key=reservation.key),
            )
        current = self._view(reservation.intent)
        owner = self._issue_owner(current, result.issue)
        if owner is not None and owner.key != reservation.key:
            raise IdentityConflict(
                "The provider issue belongs to another semantic reservation."
            )
        durable = self._state(current, reservation.key).issue
        if durable is None:
            return self._pending(
                reservation, "Issuance was observed. Durable publication is pending."
            )
        if durable.result.issue != result.issue:
            raise IdentityConflict(
                "The issuer returned conflicting permanent identities."
            )
        return durable.result

    def issued_reads(
        self, snapshot: Snapshot, reservation: IdentityReservation, issue: IssueRef
    ) -> tuple[str, ...]:
        root = reservation_root(reservation.key)
        paths = (f"{root}/reservation.json", f"{root}/issue.json", _owner_path(issue))
        state = self._state(_View(snapshot, ""), reservation.key)
        if (
            state.reservation != reservation
            or state.issue is None
            or state.issue.result.issue != issue
        ):
            raise IdentityConflict(
                "The pinned finalization source lacks authoritative issuance."
            )
        return paths

    def observe_stopped(self, intent: GraduationIntent) -> StoppedIdentityObservation:
        """Observe the exact stopped reservation without ever acquiring send authority."""
        from aitm_core.rules.expansion import stopped_expansion_claim

        view = self._view(intent)
        stopped_expansion_claim(self.repo, view.snapshot, intent)
        assert intent.source is not None
        key = intent.source.semantic_key
        root = reservation_root(key)
        state = self._state(view, key)
        reservation = state.reservation
        claim = state.claim
        found = StoppedIdentityObservation(
            view.snapshot,
            (f"{root}/reservation.json", f"{root}/issue.json", f"{root}/claim-1.json"),
        )
        if reservation is None:
            return found
        if reservation.intent != intent:
            raise IdentityConflict(
                "The stopped intent differs from the retained issuer reservation."
            )
        if claim is None:
            return found
        reads = (
            *found.reads[:2],
            f"{root}/claim-{claim.generation}.json",
            f"{root}/claim-{claim.generation + 1}.json",
        )
        if state.issue is not None:
            assert state.issue.result.issue is not None
            issue = state.issue.result.issue
            return StoppedIdentityObservation(
                view.snapshot, (*reads, _owner_path(issue)), claim, issue
            )

        retained = self._retained_observation(reservation, claim)
        observation = retained.result if retained is not None else None
        observed = self._observe(reservation, claim) if observation is None else None
        if observed is not None:
            observation = observed.result
        assert observation is not None
        if observation.status == "issued":
            result = self._retain_issue(observation, claim)
            if result.issue is None:
                return StoppedIdentityObservation(view.snapshot, reads, claim)
            current = self._view(intent)
            paths = self.issued_reads(current.snapshot, reservation, result.issue)
            return StoppedIdentityObservation(
                current.snapshot,
                tuple(dict.fromkeys((*reads, *paths))),
                claim,
                result.issue,
            )
        qualified = _qualified_stopped_absence(
            self.provider, reservation, claim, observed
        )
        return StoppedIdentityObservation(
            view.snapshot, reads, claim, absence=observed if qualified else None
        )

    def dispatch_or_observe(self, reservation: IdentityReservation) -> IdentityResult:
        return self._advance(reservation, send=True)

    def cancel(self, reservation: IdentityReservation) -> IdentityResult:
        """Observe only. Uncertain cancellation retains its semantic reservation."""
        return self._advance(reservation, send=False)

    def _advance(
        self, reservation: IdentityReservation, *, send: bool
    ) -> IdentityResult:
        intent = reservation.intent
        if intent.source is None or reservation.key != intent.source.semantic_key:
            raise IdentityConflict(
                "The reservation does not match its prepared semantic source."
            )
        view = self._view(intent)
        state = self._state(view, reservation.key)
        if state.reservation != reservation:
            raise IdentityConflict(
                "The reservation is not the verified semantic holder."
            )
        if state.issue is not None:
            return state.issue.result
        prior = None
        claim = state.claim
        if claim is not None:
            retained = self._retained_observation(reservation, claim)
            if retained is not None:
                return self._retain_issue(retained.result, claim)
            prior = self._observe(reservation, claim)
            if prior.result.status == "issued":
                return self._retain_issue(prior.result, claim)
            if prior.result.status != "absent-with-proof" or not prior.fence_proof:
                return self._pending(
                    reservation, "The previous dispatcher or issuance remains unproven."
                )
        if not send:
            return self._pending(
                reservation, "Cancellation requires a recorded terminal disposition."
            )
        from aitm_core.rules.expansion import expansion_claim_pin

        try:
            self._check_source(view, intent)
            origin_pin = expansion_claim_pin(self.repo, view.snapshot, intent)
        except GitCommandError as error:
            raise IdentityConflict("The prepared source cannot be verified.") from error
        if origin_pin is not None and claim is not None and claim.origin_digest is None:
            return self._pending(
                reservation, "Historical expansion claims are observe-only."
            )
        root = reservation_root(reservation.key)
        generation = claim.generation + 1 if claim is not None else 1
        token = uuid4().hex
        proposed = DispatchClaim(
            key=reservation.key,
            generation=generation,
            token=token,
            prior=prior,
            origin_digest=origin_pin.digest if origin_pin is not None else None,
        )
        pins = (f"{root}/reservation.json", f"{root}/issue.json")
        if claim is not None:
            pins += (f"{root}/claim-{claim.generation}.json",)
        if not self._write(
            view,
            f"{root}/claim-{generation}.json",
            proposed,
            token,
            pins,
            origin_pin=origin_pin,
            claim_intent=intent,
        ):
            return self._pending(
                reservation, "Dispatch authority was not verified for this sender."
            )
        current = self._view(intent)
        if current.policy != view.policy or self._state(
            current, reservation.key
        ) != _State(reservation, proposed, None):
            return self._pending(reservation, "Dispatch authority changed before send.")
        self._check_source(current, intent)
        if origin_pin is not None:
            try:
                rechecked = expansion_claim_pin(self.repo, current.snapshot, intent)
            except IdentityConflict:
                rechecked = None
            if rechecked != origin_pin or proposed.origin_digest != origin_pin.digest:
                return self._pending(
                    reservation,
                    "Expansion fenced before send. Custody remains unknown.",
                )
        try:
            result = self.provider.dispatch(reservation, proposed)
        except OSError:
            return self._pending(reservation, "The send acknowledgement was lost.")
        if not isinstance(result, IdentityResult) or result.reservation != reservation:
            raise IdentityConflict("Provider result does not match the retained claim.")
        if result.status == "issued":
            return self._retain_issue(result, proposed)
        return self._pending(
            reservation, "Dispatch is incomplete. Observe before retrying."
        )
