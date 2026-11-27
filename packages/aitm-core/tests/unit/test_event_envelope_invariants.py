"""Cover lossless event provenance and dispatch at the wire boundary."""

from dataclasses import replace

import pytest

from aitm_core.events import FoldIntegrityError, ReducerRegistry, fold
from aitm_core.models.events import EnvelopeError, validate_envelope
from tests.unit.test_c02 import EMPTY_DIGEST, digest, raw_event


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        pytest.param(
            raw_event(v=2), "invalid event envelope", id="unsupported-version"
        ),
        pytest.param(
            raw_event(story=True), "invalid event envelope", id="boolean-story"
        ),
        pytest.param(
            raw_event(operation_id=""), "invalid event envelope", id="empty-operation"
        ),
        pytest.param(
            raw_event(data=["unexpected"]),
            "invalid event envelope",
            id="non-object-data",
        ),
        pytest.param(
            raw_event(recorded_at="2026-11-27"),
            "explicit UTC",
            id="date-only-recording",
        ),
        pytest.param(
            raw_event(ts="2026-02-30T08:00:00Z"),
            "invalid event timestamp",
            id="nonexistent-date",
        ),
        pytest.param(
            raw_event() + b"\r\n", "one LF-delimited", id="wrong-wire-newline"
        ),
        pytest.param(
            raw_event().replace(b'"value":1', b'"value":NaN'),
            "nonfinite",
            id="non-json-nan",
        ),
        pytest.param(
            raw_event().replace(b'"value":1', b'"nested":{"proof":1,"proof":2}'),
            "duplicate event key: proof",
            id="shadowed-nested-proof",
        ),
    ],
)
def test_envelope_refuses_ambiguous_wire_records(raw, reason):
    with pytest.raises(EnvelopeError, match=reason):
        validate_envelope(raw)


def test_backfill_retains_distinct_observation_and_recording_roles():
    actor = {"kind": "human", "on_behalf_of": "fixture-owner"}
    recorder = {"kind": "tool", "harness": "importer", "session": "import-1"}
    raw = (
        raw_event(
            actor=actor,
            recorded_at="2026-11-27T09:00:01Z",
            backfill={
                "recorded_at": "2026-11-27T09:00:00Z",
                "by": recorder,
                "source": "evidence/import.json",
                "source_digest": EMPTY_DIGEST,
            },
        )
        + b"\n"
    )
    event = validate_envelope(raw)
    assert event.raw_record == raw
    assert event.ts < event.backfill.recorded_at < event.recorded_at
    assert event.actor.on_behalf_of == "fixture-owner" and event.actor.kind == "human"
    assert event.backfill.by.session == "import-1" and event.backfill.by.kind == "tool"
    assert event.backfill.source_digest == EMPTY_DIGEST


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        pytest.param(
            {"source": "/tmp/evidence"}, "repository-relative", id="absolute-source"
        ),
        pytest.param(
            {"recorded_at": "2026-11-27T08:00:00-06:00"},
            "explicit UTC",
            id="local-backfill-time",
        ),
        pytest.param(
            {"source_digest": "A" * 64},
            "invalid event envelope",
            id="noncanonical-backfill-digest",
        ),
    ],
)
def test_backfill_requires_replayable_evidence_coordinates(change, reason):
    backfill = {
        "recorded_at": "2026-11-27T09:00:00Z",
        "by": {"kind": "tool"},
        "source": "evidence/input.json",
        "source_digest": EMPTY_DIGEST,
    }
    with pytest.raises(EnvelopeError, match=reason):
        validate_envelope(raw_event(backfill=backfill | change))


def test_byte_distinct_duplicate_is_a_conflict_even_when_json_values_match():
    original = raw_event()
    whitespace_variant = b" " + original
    reducers = ReducerRegistry().register("core.fixture.set", lambda state, _: state)
    with pytest.raises(FoldIntegrityError, match="different bytes"):
        fold([original, whitespace_variant], reducers)


def test_replay_revalidates_wire_bytes_from_a_preparsed_envelope():
    envelope = validate_envelope(raw_event())
    substituted = envelope.model_copy(update={"data": {"value": "not-on-wire"}})
    reducers = ReducerRegistry().register(
        "core.fixture.set", lambda state, event: replace(state, domains=event.data)
    )
    assert fold([substituted], reducers).domains == {"value": 1}


def test_reducer_cannot_replace_wire_sequence_story_or_digest():
    raw = raw_event()
    reducers = ReducerRegistry().register(
        "core.fixture.set",
        lambda state, _: replace(
            state,
            story_id=12,
            next_sequence=8,
            prior_log_digest="bogus",
            domains={"owned": "projection"},
        ),
    )
    result = fold([raw], reducers)
    assert result.story_id == 4 and result.next_sequence == 2
    assert result.prior_log_digest == digest(raw)
    assert result.domains == {"owned": "projection"}


def test_batch_refusal_precedes_even_the_first_domain_write():
    first = raw_event()
    second = raw_event(2, digest(first))
    reduced = []

    def validate(events):
        assert [event.sequence for event in events] == [1, 2]
        raise ValueError("causal evidence is missing")

    def apply(state, event):
        reduced.append(event.id)
        return state

    reducers = ReducerRegistry(batch_validator=validate).register(
        "core.fixture.set", apply
    )
    with pytest.raises(ValueError, match="causal evidence"):
        fold([first, second], reducers)
    assert reduced == []
