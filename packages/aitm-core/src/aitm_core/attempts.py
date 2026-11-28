"""Attach current planning evidence to the retained provisional attempt."""

from aitm_core.models.attempts import AttemptReconciled, AttemptRecord, SourceSnapshot


def attach_attempt_evidence(
    record: AttemptRecord,
    *,
    attempt: str,
    generation: int,
    plan_generation: int,
    source: SourceSnapshot,
    binding: str,
) -> AttemptRecord:
    fact = AttemptReconciled(
        attempt=attempt,
        generation=generation,
        plan_generation=plan_generation,
        source=source,
        binding=binding,
    )
    if record.started.attempt != fact.attempt or record.generation != fact.generation:
        raise ValueError("attempt identity or generation is stale")
    if record.closed or record.recovery is not None or record.clock_mode != "active":
        raise ValueError("attempt requires its active implementation clock")
    if not record.started.provisional:
        raise ValueError("only a provisional attempt can attach planning evidence")
    if (
        record.source not in (None, fact.source)
        or record.plan_generation not in (None, fact.plan_generation)
        or record.binding not in (None, fact.binding)
    ):
        raise ValueError("planning evidence contradicts the retained attempt")
    return record.model_copy(update={"reconciliation": fact, "binding": fact.binding})
