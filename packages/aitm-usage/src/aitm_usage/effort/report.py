"""Story, epic and unattached views over one fixed effort snapshot."""

from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, fields
from datetime import timedelta

from ..types import SourceRef
from .export import REPORT_SCHEMA, LegacySnapshot
from .rollup import EffortTotals, RollupTarget, WorkflowWindow, rollup
from .store import EffortError, Snapshot


def _totals(totals: EffortTotals) -> dict:
    result = {}
    for field in fields(totals):
        value = getattr(totals, field.name)
        if field.name in ("engaged", "working_wall", "workflow_elapsed"):
            result[f"{field.name}_us"] = (
                None if value is None else value // timedelta(microseconds=1)
            )
        elif field.name != "grok_cost_usd_ticks":
            result[field.name] = value
    return {
        **result,
        "provider_reported_grok_usd_ticks": totals.grok_cost_usd_ticks,
        "estimated_usd": None,
        "rate_basis": None,
        "verified_billed_usd": None,
    }


def build_report(
    snapshot: Snapshot,
    target: RollupTarget,
    *,
    clocks: Mapping[str, SourceRef] | None = None,
    workflow: WorkflowWindow | None = None,
    legacy: LegacySnapshot | None = None,
) -> dict:
    """Expose portable totals and provenance without mixing accounting sources."""
    if legacy is not None and legacy.project_id != target.project_id:
        raise EffortError("Legacy snapshot belongs to another project")
    summary = rollup(snapshot, target, clocks=clocks, workflow=workflow)
    selected = {
        enrollment.attempt_id: enrollment
        for enrollment in snapshot.enrollments
        if target.selects(enrollment.story, enrollment.epic)
    }
    rows = {}
    for row in snapshot.attributed:
        attempt = row.enrollment.attempt_id
        if target.contains(row):
            selected[attempt] = row.enrollment
        if attempt in selected:
            rows[attempt] = row
    pending = Counter(receipt.attempt_id for receipt in snapshot.pending)
    conflicts = Counter(conflict.receipt.attempt_id for conflict in snapshot.conflicts)

    attempts = []
    for attempt, enrollment in sorted(selected.items()):
        row = rows.get(attempt)
        receipt = None if row is None else row.receipt
        attempts.append(
            {
                "attempt_id": str(attempt),
                "role": enrollment.role.value,
                "story": enrollment.story if row is None else row.story,
                "epic": enrollment.epic if row is None else row.epic,
                "included_in_view": row is not None and target.contains(row),
                "provider": None if receipt is None else receipt.turn.provider,
                "observation_id": None if receipt is None else receipt.observation_id,
                "revision": None if receipt is None else receipt.revision,
                "outcome": "unknown" if receipt is None else receipt.outcome.value,
                "coverage": "unknown" if receipt is None else receipt.coverage.value,
                "usage_scope": "unknown" if receipt is None else receipt.scope.value,
                "pending_receipts": pending[attempt],
                "conflicting_receipts": conflicts[attempt],
            }
        )

    legacy_view = None
    if legacy is not None:
        legacy_view = {
            "schema": legacy.schema,
            "project_id": str(legacy.project_id),
            "cutoff": legacy.cutoff,
            "rate_basis": legacy.rate_basis,
            "sha256": legacy.sha256,
            "rows": [asdict(row) for row in legacy.rows],
        }
    return {
        "schema": REPORT_SCHEMA,
        "project_id": str(snapshot.project_id),
        "generation": snapshot.generation,
        "target": {"epic": target.epic, "story": target.story},
        "total": _totals(summary.total),
        "by_role": {
            role.value: _totals(totals) for role, totals in summary.by_role.items()
        },
        "by_provider": {
            provider: _totals(totals)
            for provider, totals in summary.by_provider.items()
        },
        "unassigned_observations": summary.unassigned_observations,
        "unsettled_attempts": summary.unsettled_attempts,
        "attempts": attempts,
        "legacy": legacy_view,
        "combined_coverage": "unresolved-overlap" if legacy and legacy.rows else None,
    }


def _display(value: str | int | None) -> str:
    return "unknown" if value is None else str(value)


def _duration(value: int | None) -> str:
    if value is None:
        return "unknown"
    whole, fraction = divmod(value, 1_000_000)
    return f"{whole}.{fraction:06d} s"


def _provider_usd(ticks: int | None) -> str:
    if ticks is None:
        return "unknown"
    whole, fraction = divmod(ticks, 10_000_000_000)
    return f"{whole}.{fraction:010d}"


def render_text(report: dict) -> str:
    """Render known amounts and gaps for a person inspecting a report."""
    target = report["target"]
    if target["story"] is not None:
        label = f"Story #{target['story']}"
    elif target["epic"] is not None:
        label = f"Epic #{target['epic']}"
    else:
        label = "Unattached work"
    total = report["total"]
    lines = [
        f"{label} | project {report['project_id']} | generation {report['generation']}",
        f"Observed tokens: {_display(total['observed_tokens'])} ({total['usage_gaps']} usage gaps)",
        f"Agent engagement: {_duration(total['engaged_us'])}",
        f"Working wall time: {_duration(total['working_wall_us'])}",
        f"Workflow elapsed: {_duration(total['workflow_elapsed_us'])}",
        f"Clock gaps: {total['clock_gaps']} | boundary gaps: {total['boundary_gaps']}",
        f"Provider-reported Grok USD: {_provider_usd(total['provider_reported_grok_usd_ticks'])}",
        f"API-equivalent estimated USD: {_display(total['estimated_usd'])}",
        f"Verified billed USD: {_display(total['verified_billed_usd'])}",
        f"Unassigned observations: {report['unassigned_observations']}",
        f"Unsettled attempts: {report['unsettled_attempts']}",
    ]
    for group, title in (("by_role", "Role"), ("by_provider", "Provider")):
        for name, subtotal in report[group].items():
            lines.append(
                f"{title} {name}: {_display(subtotal['observed_tokens'])} observed tokens, "
                f"{_duration(subtotal['engaged_us'])} engagement, "
                f"{subtotal['usage_gaps']} usage gaps"
            )
    for attempt in report["attempts"]:
        provider = _display(attempt["provider"])
        lines.append(
            f"Attempt {attempt['attempt_id']} ({attempt['role']}, {provider}): "
            f"{attempt['outcome']} outcome, {attempt['coverage']} coverage"
        )
    legacy = report["legacy"]
    if legacy is not None:
        lines.append(
            f"Legacy usage snapshot at sequence {legacy['cutoff']} "
            f"({len(legacy['rows'])} project rows, rate basis {legacy['rate_basis']})"
        )
        if report["combined_coverage"] == "unresolved-overlap":
            lines.append("Combined coverage: unknown (unresolved source overlap)")
        for row in legacy["rows"]:
            lines.append(
                f"Legacy {row['source']} revision {row['observation_revision']}: "
                f"{_display(row['observed_tokens'])} observed tokens, "
                f"{_display(row['estimated_usd'])} estimated USD"
            )
    return "\n".join(lines) + "\n"
