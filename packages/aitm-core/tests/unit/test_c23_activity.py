"""Pure tests for provider-bound activity ingestion."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from aitm_core.activity import (
    ActivityEvidence,
    ActivityObservation,
    EventBatch,
    ingest_activity,
)
from aitm_core.ext.api import ActivityProducerRegistration, Extension
from aitm_core.ext.registry import load_extensions
from aitm_core.models.config import ExtensionConfig

START = datetime(2026, 11, 27, 12, tzinfo=UTC)
END = START + timedelta(hours=1)


@pytest.fixture
def producer():
    declarations = tuple(
        ActivityProducerRegistration(
            id=f"fixture.{name}",
            version=3,
            measurement_contract=contract,
            coverage_class=coverage,
        )
        for name, contract, coverage in (
            ("measured", "engaged-interval/v1", "measured-engagement"),
            ("tool", "tool-interval/v1", "tool-duration"),
            ("gap", "cli-gap/v1", "gap-estimate"),
        )
    )
    manifest = Extension(
        name="fixture",
        namespace="fixture",
        version="0.1.0",
        requires_core=">=0.1,<0.2",
        activity_producers=declarations,
    )
    policy = SimpleNamespace(
        config=SimpleNamespace(extensions=ExtensionConfig(enabled=("fixture",)))
    )
    registry = load_extensions(policy, (manifest,))
    return {
        declaration.id.removeprefix("fixture."): registry.register_activity(declaration)
        for declaration in declarations
    }


@pytest.fixture
def observation():
    return ActivityObservation(
        source_id="observed-first",
        actor="fixture-agent",
        actor_kind="agent",
        session="session-1",
        attempt="attempt-1",
        generation=2,
        binding="binding-1",
        observed_at=START,
        recorded_at=END,
        ended_at=END,
        evidence=("fixture:observed-active-agent",),
    )


def test_ingest_keeps_provider_and_observation_in_recorded_order(producer, observation):
    late = replace(
        observation,
        source_id="arrived-later",
        observed_at=START - timedelta(hours=2),
        recorded_at=END + timedelta(days=1),
    )

    batch = ingest_activity(producer["measured"], iter((observation, late)))

    assert isinstance(batch, EventBatch)
    assert batch.records == (
        ActivityEvidence(producer["measured"], observation, True, None),
        ActivityEvidence(producer["measured"], late, True, None),
    )
    pinned = batch.records[0].producer
    assert (
        pinned.id,
        pinned.version,
        pinned.measurement_contract,
        pinned.coverage_class,
    ) == (
        "fixture.measured",
        3,
        "engaged-interval/v1",
        "measured-engagement",
    )


def test_exact_observation_duplicates_collapse_by_source_id(producer, observation):
    distinct = replace(observation, source_id="distinct-id")
    batch = ingest_activity(
        producer["measured"], (observation, distinct, replace(observation))
    )

    assert tuple(record.observation.source_id for record in batch.records) == (
        "observed-first",
        "distinct-id",
    )


@pytest.mark.parametrize(
    "change",
    [
        {"recorded_at": END + timedelta(minutes=1)},
        {"observed_at": START.astimezone(timezone(timedelta(hours=1)))},
        {"generation": 2.0},
        {"evidence": ("different-proof",)},
    ],
)
def test_conflicting_duplicate_source_id_raises(producer, observation, change):
    with pytest.raises(ValueError, match="observed-first"):
        ingest_activity(
            producer["measured"], (observation, replace(observation, **change))
        )


@pytest.mark.parametrize(
    "change",
    [
        {"source_id": ""},
        {"actor": " "},
        {"actor_kind": "human"},
        {"session": ""},
        {"attempt": ""},
        {"generation": 0},
        {"generation": True},
        {"binding": ""},
        {"observed_at": START.replace(tzinfo=None)},
        {"recorded_at": START - timedelta(seconds=1)},
        {"recorded_at": START},
        {"ended_at": START - timedelta(seconds=1)},
        {"ended_at": START},
        {"ended_at": None},
        {"evidence": ()},
        {"evidence": (" ",)},
    ],
)
def test_ineligible_measured_observation_is_retained_with_reason(
    producer, observation, change
):
    candidate = replace(observation, **change)
    (record,) = ingest_activity(producer["measured"], (candidate,)).records

    assert record.observation is candidate
    assert not record.qualified
    assert record.reason


@pytest.mark.parametrize(
    ("name", "actor_kind", "end", "eligible"),
    [
        ("tool", "tool", END, True),
        ("tool", "agent", END, False),
        ("tool", "tool", None, False),
        ("gap", "agent", None, True),
        ("gap", "human", None, False),
        ("gap", "agent", END, False),
    ],
)
def test_nonmeasured_observation_requires_its_contract_shape(
    producer, observation, name, actor_kind, end, eligible
):
    candidate = replace(observation, actor_kind=actor_kind, ended_at=end, evidence=())
    (record,) = ingest_activity(producer[name], (candidate,)).records

    assert record.observation is candidate
    assert record.qualified is eligible
    assert (record.reason is None) is eligible


def test_unknown_measurement_contract_remains_ineligible(producer, observation):
    obsolete = producer["measured"].model_copy(
        update={"measurement_contract": "engaged-interval/v2"}
    )
    (record,) = ingest_activity(obsolete, (observation,)).records

    assert record.observation is observation
    assert not record.qualified
    assert record.reason
