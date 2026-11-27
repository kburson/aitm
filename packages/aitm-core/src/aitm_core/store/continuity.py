"""Decide admission of observed shared history from independent trust inputs."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import StrEnum

from aitm_core.models.common import LocalOutcome, RefObservation, StoreAnchor
from aitm_core.store.validation import ValidationReport


class ContinuityStatus(StrEnum):
    LOCAL_ONLY = "local-only"
    VERIFIED = "verified"
    DELETED = "deleted"
    ROLLBACK = "rollback"
    SIBLING = "sibling"
    UNPROVABLE = "unprovable"
    QUARANTINED = "quarantined"
    STALE = "stale"
    UNKNOWN = "unknown"
    ROUTE_MISMATCH = "route-mismatch"


@dataclass(frozen=True, slots=True)
class SharedFrontier:
    """Separate the observed shared checkpoint from the last valid content tip."""

    status: ContinuityStatus
    checkpoint: str
    valid_tip: str | None
    observation: RefObservation | None
    first_observation_limit: bool
    local_diverged: bool = False
    reason: str | None = None

    @property
    def fences_shared(self) -> bool:
        return self.status not in {
            ContinuityStatus.LOCAL_ONLY,
            ContinuityStatus.VERIFIED,
        }


@dataclass(frozen=True, slots=True)
class ContinuityAnchor:
    """Trusted route and independent facts for candidate admission."""

    store: StoreAnchor
    checkpoint: str
    previous: SharedFrontier | None
    is_ancestor: Callable[[str, str], bool | None]
    validate: Callable[[str], ValidationReport]
    local_tip: str | None = None
    first_clone: bool = True


def _matches_route(store: StoreAnchor, observation: RefObservation) -> bool:
    return (observation.remote, observation.ref) == (
        store.planning_remote,
        store.planning_ref,
    )


def _retain(
    anchor: ContinuityAnchor,
    status: ContinuityStatus,
    observation: RefObservation | None = None,
    reason: str | None = None,
) -> SharedFrontier:
    previous = anchor.previous
    first_clone_limit = (
        previous.first_observation_limit
        if previous is not None
        else anchor.first_clone and anchor.checkpoint == anchor.store.root_commit
    )
    return SharedFrontier(
        status=status,
        checkpoint=anchor.checkpoint,
        valid_tip=previous.valid_tip if previous is not None else None,
        observation=observation,
        first_observation_limit=anchor.store.planning_remote is not None
        and first_clone_limit,
        local_diverged=previous.local_diverged if previous is not None else False,
        reason=reason,
    )


def unavailable_shared(anchor: ContinuityAnchor, reason: str) -> SharedFrontier:
    """Retain prior remote evidence when transport cannot supply a new observation."""
    if anchor.store.planning_remote is None:
        return _retain(anchor, ContinuityStatus.LOCAL_ONLY)

    previous = anchor.previous
    observation = previous.observation if previous is not None else None
    if observation is not None and not _matches_route(anchor.store, observation):
        observation = None
    known = observation is not None or (
        previous is not None and previous.valid_tip is not None
    )
    if (
        known
        and previous is not None
        and previous.fences_shared
        and previous.status not in {ContinuityStatus.STALE, ContinuityStatus.UNKNOWN}
    ):
        return _retain(anchor, previous.status, observation, previous.reason or reason)
    status = ContinuityStatus.STALE if known else ContinuityStatus.UNKNOWN
    return _retain(anchor, status, observation, reason)


def observe_shared(
    anchor: ContinuityAnchor, observation: RefObservation
) -> SharedFrontier:
    """Admit only a content-valid observation on the exact established shared chain."""
    if anchor.store.planning_remote is None:
        return _retain(anchor, ContinuityStatus.LOCAL_ONLY)
    if not _matches_route(anchor.store, observation):
        return _retain(
            anchor,
            ContinuityStatus.ROUTE_MISMATCH,
            observation,
            "observation does not identify the anchored planning remote and ref",
        )
    candidate = observation.observed_commit
    if candidate is None:
        return _retain(
            anchor,
            ContinuityStatus.DELETED,
            observation,
            "the anchored shared planning ref is absent",
        )

    checkpoint = anchor.checkpoint
    if candidate != checkpoint:
        forward = anchor.is_ancestor(checkpoint, candidate)
        if forward is not True:
            reverse = (
                anchor.is_ancestor(candidate, checkpoint) if forward is False else None
            )
            if reverse is True:
                return _retain(
                    anchor,
                    ContinuityStatus.ROLLBACK,
                    observation,
                    "shared planning ref moved behind its trusted checkpoint",
                )
            if reverse is False:
                return _retain(
                    anchor,
                    ContinuityStatus.SIBLING,
                    observation,
                    "shared planning ref diverges from its trusted checkpoint",
                )
            return _retain(
                anchor,
                ContinuityStatus.UNPROVABLE,
                observation,
                "cannot prove shared planning ancestry against its trusted checkpoint",
            )

    validation = anchor.validate(candidate)
    if validation.tip != candidate:
        return _retain(
            anchor,
            ContinuityStatus.UNPROVABLE,
            observation,
            "validation does not name the observed shared planning commit",
        )
    if validation.outcome != LocalOutcome.COMPLETED:
        held = _retain(
            anchor,
            ContinuityStatus.QUARANTINED,
            observation,
            validation.reason or "shared planning content validation did not complete",
        )
        return replace(held, checkpoint=candidate)

    local = anchor.local_tip
    local_diverged = (
        local is not None
        and local not in {candidate, checkpoint}
        and anchor.is_ancestor(local, candidate) is not True
    )
    admitted = _retain(anchor, ContinuityStatus.VERIFIED, observation)
    return replace(
        admitted,
        checkpoint=candidate,
        valid_tip=candidate,
        local_diverged=local_diverged,
    )
