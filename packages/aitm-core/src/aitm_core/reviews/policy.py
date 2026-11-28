"""Validate the closure and topology of one reconstructed review."""

import re
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from aitm_core.documents import DocumentError, _Document, _parse
from aitm_core.models.config import DocumentAssurance
from aitm_core.models.evidence import ReviewLevel
from aitm_core.models.lifecycle import Positive, Text
from aitm_core.reviews.portable import (
    PortableManifest,
    PortableResponse,
    ReconstructedReview,
    ReviewError,
)
from aitm_core.reviews.topology import (
    IdentityBinding,
    IdentityMapping,
    IdentityRelation,
    Participant,
    resolve_participant,
)

Role = Literal["author", "reviewer"]
_DECISION_HEADING = re.compile(r" {0,3}## Decision[ \t]*")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})(.*)")
_DECISION_VALUE = re.compile(
    r" {0,3}(\*\*)?(accepted|revisions-requested)(?(1)\*\*)[ \t]*"
)


class ReviewRefusal(ReviewError):
    """Reconstructed evidence cannot satisfy the review level under this policy."""


@dataclass(frozen=True, slots=True)
class ReviewPolicy:
    assurances: tuple[DocumentAssurance, ...]
    identities: IdentityMapping
    allow_participant_replacements: bool = False


@dataclass(frozen=True, slots=True)
class ValidatedReview:
    record: ReconstructedReview
    level: ReviewLevel
    assurance: DocumentAssurance


class _Replacement(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    role: Role
    round: Positive


class _ManifestClaims(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="ignore")

    authority_assurance: Text | None = None
    commit_mode: Text | None = None
    native_status: Text | None = None
    execution: Text | None = None
    author_session: Text | None = None
    reviewer_session: Text | None = None
    session_identity_kind: Text | None = None
    participant_replacements: list[_Replacement] = []


class _TurnClaims(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="ignore")

    session_identity_kind: Text = "recorded-session"
    reviewer_decision: Literal["accepted", "revisions-requested"] | None = None


def _original(
    originals: dict[str, bytes],
    name: str,
    expected: PortableManifest | PortableResponse,
) -> _Document:
    try:
        document = _parse(originals[name])
        if type(expected).model_validate(document.header) != expected:
            raise ReviewRefusal(f"{name} disagrees with the reconstructed record")
        return document
    except (KeyError, DocumentError, ValidationError) as error:
        raise ReviewRefusal(f"invalid retained original {name}") from error


def _assurance(claims: _ManifestClaims, policy: ReviewPolicy) -> DocumentAssurance:
    if claims.commit_mode not in (None, "normal"):
        raise ReviewRefusal("review commit mode must be normal")
    if claims.authority_assurance == "declared-manual" and claims.native_status is None:
        assurance = "declared-manual"
    elif (
        claims.authority_assurance
        in ("unavailable", "native-consensus-authority-unavailable")
        and claims.native_status == "accepted"
        and claims.commit_mode == "normal"
        and claims.execution not in ("manual", "declared-manual")
    ):
        assurance = "native-consensus-authority-unavailable"
    else:
        raise ReviewRefusal("review assurance is unsupported or lacks evidence")
    if assurance not in policy.assurances:
        raise ReviewRefusal(f"review assurance {assurance} is disallowed")
    return assurance


def _decision(document: _Document, claims: _TurnClaims) -> str | None:
    # Historical portable responses use a standalone value under ## Decision.
    # Ignore headings inside fenced examples and require agreement with typed claims.
    markdown_decision = None
    pending = False
    fence = ""
    for line in document.body.decode("utf-8").splitlines():
        fence_line = _FENCE.fullmatch(line)
        if fence:
            if (
                fence_line
                and fence_line[1].startswith(fence)
                and not fence_line[2].strip()
            ):
                fence = ""
            continue
        # Raw HTML blocks can hide a line shaped like a decision. Their scope
        # is outside the portable decision grammar.
        if line.lstrip().startswith("<"):
            raise ReviewRefusal("unsupported HTML in reviewer decision record")
        if pending and line.strip():
            value = _DECISION_VALUE.fullmatch(line)
            if value is None:
                raise ReviewRefusal("unsupported reviewer decision")
            markdown_decision = value[2]
            pending = False
            continue
        if fence_line:
            fence = fence_line[1]
        elif _DECISION_HEADING.fullmatch(line):
            if markdown_decision is not None:
                raise ReviewRefusal("duplicate reviewer decision")
            pending = True
    if pending or (
        claims.reviewer_decision is not None
        and markdown_decision is not None
        and claims.reviewer_decision != markdown_decision
    ):
        raise ReviewRefusal("incomplete or contradictory reviewer decision")
    return claims.reviewer_decision or markdown_decision


def _participant(
    response: PortableResponse, claims: _TurnClaims, mapping: IdentityMapping
) -> IdentityBinding:
    session = (
        response.reviewer_session
        if response.role == "reviewer"
        else response.author_session
    )
    if session is None or response.agent is None:
        raise ReviewRefusal(f"{response.role} identity is unknown")
    result = resolve_participant(
        Participant(claims.session_identity_kind, session, response.agent.provider),
        mapping,
    )
    if isinstance(result, IdentityRelation):
        raise ReviewRefusal(f"{response.role} identity is {result}")
    return result


def _topology(
    level: ReviewLevel, author: IdentityBinding, reviewer: IdentityBinding
) -> None:
    same_family = author.provider_family == reviewer.provider_family
    same_session = author.session_id == reviewer.session_id
    if level == "sar" and not same_family:
        raise ReviewRefusal("SAR requires the author's provider family")
    if level == "spr" and (not same_family or same_session):
        raise ReviewRefusal(
            "SPR requires distinct sessions in the same provider family"
        )
    if level == "xpr" and (same_family or same_session):
        raise ReviewRefusal("XPR requires distinct sessions and provider families")


def _findings(reviewer: PortableResponse, author: PortableResponse, index: int) -> None:
    opened = set(reviewer.finding_ids)
    answered = set(author.answered_finding_ids)
    if (
        len(opened) != len(reviewer.finding_ids)
        or len(answered) != len(author.answered_finding_ids)
        or reviewer.answered_finding_ids
        or author.finding_ids
        or opened != answered
    ):
        raise ReviewRefusal(
            f"round {index} findings require exactly one disposition each"
        )


def _check_manifest_participant(
    role: Role, claims: _ManifestClaims, binding: IdentityBinding
) -> None:
    session = claims.author_session if role == "author" else claims.reviewer_session
    if (session is not None and session != binding.participant.session) or (
        claims.session_identity_kind is not None
        and claims.session_identity_kind != binding.participant.namespace
    ):
        raise ReviewRefusal(f"{role} identity conflicts with the manifest")


def validate_review(
    record: ReconstructedReview, policy: ReviewPolicy
) -> ValidatedReview:
    """Apply explicit policy to C24-verified bytes and preserve their provenance."""
    manifest = record.manifest
    if manifest.outcome != "exhausted":
        raise ReviewRefusal(
            f"review outcome {manifest.outcome!r} does not prove exhaustion"
        )
    if len(record.rounds) != manifest.rounds:
        raise ReviewRefusal("review round count conflicts with the manifest")
    originals = {item.name: item.raw for item in record.originals}
    if len(originals) != len(record.originals):
        raise ReviewRefusal("duplicate retained review original")
    manifest_doc = _original(originals, "review-manifest.md", manifest)
    try:
        claims = _ManifestClaims.model_validate(manifest_doc.header)
        assurance = _assurance(claims, policy)
        replacements = {
            (item.role, item.round) for item in claims.participant_replacements
        }
        if len(replacements) != len(claims.participant_replacements) or (
            replacements and not policy.allow_participant_replacements
        ):
            raise ReviewRefusal(
                "participant continuity requires policy-permitted replacements"
            )
        previous: dict[Role, IdentityBinding] = {}
        for index, turn in enumerate(record.rounds, 1):
            reviewer, author = turn.reviewer, turn.author
            if reviewer.round != index or author.round != index:
                raise ReviewRefusal(f"round order conflicts at round {index}")
            _findings(reviewer, author, index)
            for role, response in (("reviewer", reviewer), ("author", author)):
                if response.role != role:
                    raise ReviewRefusal(f"unexpected {response.role} in {role} turn")
                document = _original(originals, f"{role}-response-{index}.md", response)
                turn_claims = _TurnClaims.model_validate(document.header)
                binding = _participant(response, turn_claims, policy.identities)
                prior = previous.get(role)
                if prior is None:
                    _check_manifest_participant(role, claims, binding)
                elif prior.session_id != binding.session_id:
                    replacement = (role, index)
                    if replacement not in replacements:
                        raise ReviewRefusal(
                            f"{role} continuity breaks at round {index}"
                        )
                    replacements.remove(replacement)
                previous[role] = binding
                if role == "reviewer":
                    decision = _decision(document, turn_claims)
            _topology(manifest.level, previous["author"], previous["reviewer"])
            if index < manifest.rounds and decision == "accepted":
                raise ReviewRefusal("reviewer decision accepted before the final round")
            if index == manifest.rounds:
                if decision != "accepted" or reviewer.finding_ids:
                    raise ReviewRefusal(
                        "final reviewer decision does not establish exhaustion"
                    )
                if (
                    turn.input_bytes != turn.output_bytes
                    or turn.input_bytes != record.final_bytes
                ):
                    raise ReviewRefusal(
                        "final bytes differ from the reviewer's accepted input"
                    )
        if replacements:
            raise ReviewRefusal(
                "participant continuity declaration has no matching replacement"
            )
    except (ValidationError, UnicodeError) as error:
        raise ReviewRefusal("invalid retained policy or topology claims") from error
    return ValidatedReview(record, manifest.level, assurance)
