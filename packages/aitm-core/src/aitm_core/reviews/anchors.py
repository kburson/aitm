"""Derive safe elapsed-time anchors from public native response evidence."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

from aitm_core.models.evidence import UtcText
from aitm_core.models.lifecycle import Positive, Text
from aitm_core.reviews.portable import RawDigest

Role = Literal["author", "reviewer"]


class PublicClaim(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="ignore")

    claim_id: Text
    claimed_at: UtcText
    role: Role
    host: Text
    session_fingerprint: RawDigest
    turn: Positive | None = None


@dataclass(frozen=True, slots=True)
class SourceReference:
    path: str
    digest: str


@dataclass(frozen=True, slots=True)
class TimingAnchor:
    basis: Literal["claim", "prior-submit", "unknown"]
    started_at: str | None
    source: SourceReference | None
    claim_id: str | None = None


@dataclass(frozen=True, slots=True)
class SubmittedTurn:
    round: int
    role: Role
    host: str
    fingerprint: str
    submitted_at: str
    source: SourceReference


def _instant(value: str) -> datetime:
    return datetime.fromisoformat(value)


def derive_anchor(
    response: SubmittedTurn,
    predecessor: SubmittedTurn | None,
    claims: tuple[PublicClaim, ...],
    manifest: SourceReference,
) -> TimingAnchor:
    """Use exact-turn claims and bounded predecessor proxies, ignoring registrations."""
    end = _instant(response.submitted_at)
    previous = _instant(predecessor.submitted_at) if predecessor else None
    if previous is not None and previous > end:
        return TimingAnchor("unknown", None, None)
    matches = tuple(
        claim
        for claim in claims
        if claim.role == response.role
        and claim.host == response.host
        and claim.session_fingerprint == response.fingerprint
        and (
            claim.turn == response.round or (claim.turn is None and response.round == 1)
        )
        and _instant(claim.claimed_at) <= end
        and (previous is None or previous <= _instant(claim.claimed_at))
    )
    if len(matches) == 1:
        claim = matches[0]
        return TimingAnchor("claim", claim.claimed_at, manifest, claim.claim_id)
    if predecessor is not None:
        return TimingAnchor(
            "prior-submit", predecessor.submitted_at, predecessor.source
        )
    return TimingAnchor("unknown", None, None)
