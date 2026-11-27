"""Check C02 through the same envelope and fold APIs that reducers consume."""

import hashlib
import json
from dataclasses import replace

import pytest

from aitm_core.events import (
    FoldIntegrityError,
    ReducerRegistry,
    UnavailableReducer,
    fold,
)
from aitm_core.models.events import EnvelopeError, validate_envelope

EMPTY_DIGEST = hashlib.sha256(b"").hexdigest()


def raw_event(sequence=1, prior=EMPTY_DIGEST, **fields):
    event = {
        "v": 1,
        "id": f"event-{sequence}",
        "ts": "2026-11-27T08:00:00.000Z",
        "type": "core.fixture.set",
        "story": 4,
        "actor": {"kind": "agent", "harness": "test"},
        "operation_id": "op-fixture",
        "sequence": sequence,
        "prior_log_digest": prior,
        "data": {"value": sequence},
    }
    event.update(fields)
    return json.dumps(event, separators=(",", ":")).encode()


def digest(*events):
    return hashlib.sha256(
        b"".join(event.removesuffix(b"\n") + b"\n" for event in events)
    ).hexdigest()


def test_causal_envelope():
    first = raw_event()
    same_time = raw_event(2, digest(first))
    late = raw_event(3, digest(first, same_time), ts="2026-11-26T23:59:59Z")
    calls = []

    def remember(state, envelope):
        calls.append(envelope.id)
        assert state.story_id == 4
        return replace(state, domains={"latest": envelope.data["value"]})

    reducers = ReducerRegistry()
    reducers.register("core.fixture.set", remember)
    result = fold([first, same_time, first, validate_envelope(late)], reducers)
    assert calls == ["event-1", "event-2", "event-3"]
    assert result.next_sequence == 4
    assert result.prior_log_digest == digest(first, same_time, late)
    assert result.domains["latest"] == 3


@pytest.mark.parametrize(
    ("second", "message"),
    [
        (raw_event(3), "sequence"),
        (raw_event(2), "prior log digest"),
        (raw_event(2, digest(raw_event()), story=5), "story"),
        (raw_event(2, digest(raw_event()), id="event-1"), "identity"),
    ],
)
def test_refuses_inconsistent_lineage(second, message):
    reducers = ReducerRegistry()
    reducers.register("core.fixture.set", lambda state, event: state)
    with pytest.raises(FoldIntegrityError, match=message):
        fold([raw_event(), second], reducers)


def test_opaque_extension_preserves_raw_record():
    event = (
        b" "
        + raw_event(type="vendor.extra.observed", data={"visible": [True, None]})
        + b"\n"
    )
    result = fold([event], ReducerRegistry())
    assert result.opaque_events == (event,)
    assert result.prior_log_digest == digest(event)


def test_missing_required_reducers_are_unavailable():
    with pytest.raises(UnavailableReducer, match="core.fixture.set"):
        fold([raw_event()], ReducerRegistry())
    required = ReducerRegistry(required_namespaces={"vendor"})
    with pytest.raises(UnavailableReducer, match="vendor.extra.observed"):
        fold([raw_event(type="vendor.extra.observed")], required)


def test_duplicate_reducer_registration_is_refused():
    reducers = ReducerRegistry()
    reducers.register("core.fixture.set", lambda state, event: state)
    with pytest.raises(ValueError, match="already registered"):
        reducers.register("core.fixture.set", lambda state, event: state)


@pytest.mark.parametrize(
    "raw",
    [
        raw_event(v=True),
        raw_event(sequence=0),
        raw_event(ts="2026-11-27"),
        raw_event(ts="2026-11-27T08:00:00+03:00"),
        raw_event(type="core.fixture"),
        raw_event(actor={"kind": "unknown"}),
        raw_event(read_set_digest="bad"),
        raw_event()[:-1] + b',"id":"shadow"}',
        raw_event().replace(b'"value":1', b'"value":1e999'),
        raw_event() + b"\n" + raw_event(),
        raw_event(
            backfill={
                "recorded_at": "2026-11-27T09:00:00Z",
                "by": {"kind": "agent"},
                "source": "../outside",
                "source_digest": EMPTY_DIGEST,
            }
        ),
    ],
)
def test_malformed_envelope_refuses(raw):
    with pytest.raises(EnvelopeError):
        validate_envelope(raw)
