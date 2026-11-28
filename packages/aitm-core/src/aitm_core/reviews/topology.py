"""Compare review participants through explicitly documented identity bindings."""

from dataclasses import dataclass
from enum import StrEnum


class IdentityRelation(StrEnum):
    SAME = "same"
    DISTINCT = "distinct"
    UNKNOWN = "unknown"
    CONTRADICTORY = "contradictory"


@dataclass(frozen=True, slots=True)
class Participant:
    namespace: str
    session: str
    provider: str


@dataclass(frozen=True, slots=True)
class IdentityBinding:
    participant: Participant
    session_id: str
    provider_family: str


@dataclass(frozen=True, slots=True)
class IdentityMapping:
    """Map recorded claims to canonical session IDs and provider families.

    The evidence identifies the documented source of the mapping. Raw claims
    in different namespaces may alias only through an explicit binding.
    """

    evidence: str
    bindings: tuple[IdentityBinding, ...]


def resolve_participant(
    participant: Participant, mapping: IdentityMapping
) -> IdentityBinding | IdentityRelation:
    """Resolve one raw claim, preserving missing and conflicting provenance."""
    if not mapping.evidence.strip() or not all(
        value.strip()
        for value in (participant.namespace, participant.session, participant.provider)
    ):
        return IdentityRelation.UNKNOWN
    candidates = tuple(
        binding
        for binding in mapping.bindings
        if (binding.participant.namespace, binding.participant.session)
        == (participant.namespace, participant.session)
    )
    if not candidates:
        return IdentityRelation.UNKNOWN
    if not any(binding.participant == participant for binding in candidates):
        return IdentityRelation.CONTRADICTORY
    identities = {
        (binding.session_id, binding.provider_family) for binding in candidates
    }
    if len(identities) != 1:
        return IdentityRelation.CONTRADICTORY
    session_id, provider_family = next(iter(identities))
    if not session_id.strip() or not provider_family.strip():
        return IdentityRelation.UNKNOWN
    if any(
        binding.session_id == session_id and binding.provider_family != provider_family
        for binding in mapping.bindings
    ):
        return IdentityRelation.CONTRADICTORY
    return next(binding for binding in candidates if binding.participant == participant)


def compare_participants(
    left: Participant, right: Participant, mapping: IdentityMapping
) -> IdentityRelation:
    """Compare documented sessions without inferring identity from raw strings."""
    first = resolve_participant(left, mapping)
    second = resolve_participant(right, mapping)
    if IdentityRelation.CONTRADICTORY in (first, second):
        return IdentityRelation.CONTRADICTORY
    if isinstance(first, IdentityBinding) and isinstance(second, IdentityBinding):
        if first.session_id == second.session_id:
            return IdentityRelation.SAME
        return IdentityRelation.DISTINCT
    return IdentityRelation.UNKNOWN
