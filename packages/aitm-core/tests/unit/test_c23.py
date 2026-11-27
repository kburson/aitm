"""C23 implementation engagement is a pure fold over pinned clock facts."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest

from aitm_core.activity import ActivityObservation, ingest_activity
from aitm_core.ext.api import ActivityProducerRegistration, Extension
from aitm_core.ext.registry import load_extensions
from aitm_core.models.attempts import AttemptRecord, AttemptStarted, ClockChanged
from aitm_core.models.config import ExtensionConfig
from aitm_core.rules.timing import engagement

ORIGIN = datetime(2026, 1, 5, tzinfo=UTC)
HOUR = 3_600_000
MINUTE = 60_000


def time_at(hours):
    return ORIGIN + timedelta(hours=hours)


def clock(*boundaries, allowance=4 * HOUR):
    if not boundaries:
        boundaries = ((0, "active"),)
    previous = None
    clocks = []
    for index, (when, mode) in enumerate(boundaries):
        clocks.append(
            ClockChanged(
                attempt="implementation",
                generation=1,
                cause_event_id=f"event-{index}",
                observed_at=time_at(when),
                used_millis=0,
                **{"from": previous, "to": mode},
            )
        )
        previous = mode
    return AttemptRecord(
        started=AttemptStarted(
            attempt="implementation",
            generation=1,
            plan_generation=1,
            source=None,
            binding="managed-binding",
            allowance_millis=allowance,
        ),
        generation=1,
        binding="managed-binding",
        allowance_millis=allowance,
        clocks=tuple(clocks),
    )


def activity(contract, *specs):
    kind = {
        "engaged-interval/v1": "measured-engagement",
        "tool-interval/v1": "tool-duration",
        "cli-gap/v1": "gap-estimate",
    }[contract]
    declaration = ActivityProducerRegistration(
        id="fixture.activity",
        version=1,
        measurement_contract=contract,
        coverage_class=kind,
    )
    manifest = Extension(
        name="fixture",
        namespace="fixture",
        version="0.1",
        requires_core=">=0.1,<0.2",
        activity_producers=(declaration,),
    )
    policy = SimpleNamespace(
        config=SimpleNamespace(extensions=ExtensionConfig(enabled=("fixture",)))
    )
    producer = load_extensions(policy, (manifest,)).register_activity(declaration)
    observations = []
    for index, (start, end, overrides) in enumerate(specs):
        fields = dict(
            source_id=f"{contract}:{index}",
            actor="fixture-agent",
            actor_kind="agent",
            session="session-a",
            attempt="implementation",
            generation=1,
            binding="managed-binding",
            observed_at=time_at(start),
            ended_at=time_at(end) if end is not None else None,
            recorded_at=time_at(end if end is not None else start),
            evidence=("fixture source proof",),
        )
        observations.append(ActivityObservation(**(fields | overrides)))
    return ingest_activity(producer, observations).records


def test_five_hour_unattended_tool_never_establishes_engaged_overrun():
    records = activity("tool-interval/v1", (0, 5, {"actor_kind": "tool"}))
    report = engagement(clock(), records, as_of=time_at(5))
    assert report.tool_millis == 5 * HOUR
    assert report.measured_millis is None
    assert not report.confirmed_overrun
    assert any("measured" in reason for reason in report.unknown)


def test_exact_registered_fixture_confirms_engagement_beyond_allowance():
    records = activity("engaged-interval/v1", (0, 5, {}))
    report = engagement(clock(), records, as_of=time_at(5))
    assert report.measured_millis == 5 * HOUR
    assert report.confirmed_overrun
    assert report.tool_millis is None
    assert report.estimated_millis is None


def test_union_overlapping_observations_per_actor_and_sum_distinct_actors():
    records = activity(
        "engaged-interval/v1",
        (0, 2, {}),
        (1, 3, {"session": "session-b"}),
        (2, 4, {"actor": "second-agent"}),
    )
    report = engagement(clock(), records, as_of=time_at(4))
    assert report.measured_millis == 5 * HOUR
    assert report.confirmed_overrun


def test_only_active_windows_count_and_exact_allowance_is_not_an_overrun():
    state = clock(
        (1, "active"), (3, "expansion-paused"), (4, "active"), (6, "review-stopped")
    )
    records = activity("engaged-interval/v1", (0, 7, {}))
    report = engagement(state, records, as_of=time_at(7))
    assert report.measured_millis == 4 * HOUR
    assert not report.confirmed_overrun


def test_review_rework_resumes_same_allowance_without_counting_review():
    state = clock((0, "active"), (2, "review-stopped"), (3, "active"))
    records = activity("engaged-interval/v1", (0, 6, {}))
    report = engagement(state, records, as_of=time_at(6))
    assert report.measured_millis == 5 * HOUR
    assert report.confirmed_overrun


def test_late_evidence_cannot_authorize_an_earlier_as_of_decision():
    records = activity("engaged-interval/v1", (0, 5, {"recorded_at": time_at(6)}))
    old_report = engagement(clock(), records, as_of=time_at(5))
    assert old_report.measured_millis is None
    assert not old_report.confirmed_overrun
    assert any("recorded after" in reason for reason in old_report.unknown)
    now_report = engagement(clock(), records, as_of=time_at(6))
    assert now_report.measured_millis == 5 * HOUR
    assert now_report.confirmed_overrun


def test_phase_binding_attempt_and_generation_do_not_lend_coverage():
    records = activity(
        "engaged-interval/v1",
        (0, 5, {"binding": "planning"}),
        (0, 5, {"attempt": "other-attempt"}),
        (0, 5, {"generation": 2}),
        (0, 5, {"actor_kind": "human"}),
    )
    report = engagement(clock(), records, as_of=time_at(5))
    assert report.measured_millis is None
    assert not report.confirmed_overrun
    assert len(report.unknown) >= 4


def test_estimate_needs_two_same_session_points_and_preserves_oversized_gap():
    records = activity(
        "cli-gap/v1",
        (0, None, {}),
        (0.25, None, {}),
        (0.5, None, {"session": "session-b"}),
        (1, None, {}),
    )
    report = engagement(clock(), records, as_of=time_at(1))
    assert report.estimated_millis == 15 * MINUTE
    assert report.measured_millis is None
    assert not report.confirmed_overrun
    assert any("gap" in reason for reason in report.unknown)


def test_tool_duration_overlapping_engagement_is_reported_separately():
    records = activity("engaged-interval/v1", (0, 3, {})) + activity(
        "tool-interval/v1", (1, 3, {"actor_kind": "tool"})
    )
    report = engagement(clock(), records, as_of=time_at(3))
    assert report.measured_millis == 3 * HOUR
    assert report.tool_millis == 2 * HOUR
    assert not report.confirmed_overrun


def test_closed_and_paused_windows_cannot_add_later_elapsed_time():
    state = clock((0, "active"), (1, "terminal-closed"))
    records = activity("engaged-interval/v1", (2, 7, {}))
    report = engagement(state, records, as_of=time_at(7))
    assert report.measured_millis is None
    assert not report.confirmed_overrun


def test_later_conflicting_source_only_fences_after_it_is_recorded():
    first = activity("engaged-interval/v1", (0, 5, {}))
    divergent = activity("engaged-interval/v1", (0, 6, {"recorded_at": time_at(7)}))
    prior = engagement(clock(), first + divergent, as_of=time_at(5))
    assert prior.measured_millis == 5 * HOUR
    with pytest.raises(ValueError, match="conflicting activity source"):
        engagement(clock(), first + divergent, as_of=time_at(7))


def test_duplicate_retained_facts_across_ingestions_do_not_double_measurement():
    records = activity("engaged-interval/v1", (0, 3, {}))
    report = engagement(clock(), records + records, as_of=time_at(3))
    assert report.measured_millis == 3 * HOUR
    assert not report.confirmed_overrun


@pytest.mark.parametrize(
    "malformed",
    [{"source_id": []}, {"recorded_at": "unknown"}, {"generation": True}],
    ids=("unhashable-source", "unavailable-recording-time", "boolean-generation"),
)
def test_ineligible_activity_remains_unknown_in_the_report(malformed):
    records = activity("engaged-interval/v1", (0, 5, malformed))
    report = engagement(clock(), records, as_of=time_at(5))
    assert report.measured_millis is None
    assert records[0].reason in report.unknown[0]
    assert not report.confirmed_overrun
