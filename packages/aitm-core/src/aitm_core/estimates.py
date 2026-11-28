"""Explicit estimate observations with independent phase provenance."""

from collections.abc import Mapping

from aitm_core.models.lifecycle import Estimate, EstimatePhase, StoryKind


def observe_estimate(
    current: Mapping[EstimatePhase, Estimate],
    estimate: Estimate,
    *,
    kind: StoryKind,
    design_accepted: bool,
    source: str,
    rationale: str,
) -> dict[EstimatePhase, Estimate]:
    """Retain a new observation without promoting an earlier proposal."""
    if estimate.phase == "refine" and not design_accepted:
        raise ValueError("refine estimate requires accepted own design")
    if estimate.phase == "refine" and kind != "epic" and estimate.agent_hours > 4:
        raise ValueError("bounded story estimate exceeds four agent-hours")
    recorded = Estimate.model_validate(
        estimate.model_dump() | {"source": source, "rationale": rationale}
    )
    return {**current, estimate.phase: recorded}
