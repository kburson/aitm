"""Reject incoherent graph facts before constructing a relationship transaction."""

import pytest

from aitm_core.graduation import (
    FinalizerRegistry,
    GraduationConflict,
    ordinary_finalization,
)
from aitm_core.models.identity import FrozenFinalization
from aitm_core.models.lifecycle import Relationships
from aitm_core.models.operations import FinalizationIntent, RelatedWriteSet
from aitm_core.relationships import GraphConflict, validate_graph


@pytest.mark.parametrize(
    ("graph", "kinds", "replacements", "message"),
    [
        ({1: Relationships(parent=1)}, {1: "epic"}, {}, "itself"),
        ({1: Relationships(blocking=(1,))}, {1: "story"}, {}, "itself"),
        ({1: Relationships()}, {1: "story"}, {1: 1}, "itself"),
        ({1: Relationships(children=(2,))}, {1: "epic"}, {}, "initialized"),
        ({1: Relationships(blocked_by=(2,))}, {1: "story"}, {}, "initialized"),
        ({1: Relationships()}, {1: "story"}, {1: 2}, "replacement"),
        (
            {1: Relationships(children=(2,)), 2: Relationships(parent=1)},
            {1: "story", 2: "story"},
            {},
            "epic parent",
        ),
        (
            {1: Relationships(), 2: Relationships(parent=1)},
            {1: "epic", 2: "story"},
            {},
            "reciprocal child",
        ),
        (
            {1: Relationships(children=(2,)), 2: Relationships()},
            {1: "epic", 2: "story"},
            {},
            "reciprocal parent",
        ),
        (
            {1: Relationships(blocked_by=(2,)), 2: Relationships()},
            {1: "story", 2: "story"},
            {},
            "reciprocal",
        ),
        (
            {
                1: Relationships(parent=2, children=(2,)),
                2: Relationships(parent=1, children=(1,)),
            },
            {1: "epic", 2: "epic"},
            {},
            "parent graph",
        ),
        (
            {
                1: Relationships(blocked_by=(2,), blocking=(2,)),
                2: Relationships(blocked_by=(1,), blocking=(1,)),
            },
            {1: "story", 2: "story"},
            {},
            "dependency",
        ),
        (
            {1: Relationships(), 2: Relationships()},
            {1: "story", 2: "story"},
            {1: 2, 2: 1},
            "replacement",
        ),
        (
            {1: Relationships(blocked_by=(2,)), 2: Relationships(blocking=(1,))},
            {1: "story", 2: "story"},
            {2: 1},
            "replacement",
        ),
    ],
)
def test_relationship_graph_rejects_conflicts(graph, kinds, replacements, message):
    with pytest.raises(GraphConflict, match=message):
        validate_graph(graph, kinds, replacements)


def test_finalizer_dispatch_is_versioned_and_receives_the_chosen_candidate():
    request = FinalizationIntent(
        kind="core.related", version=2, related_preconditions=(), payload=b"\x00binary"
    )
    frozen = FrozenFinalization.from_intent(request)
    assert (
        FrozenFinalization.model_validate_json(frozen.model_dump_json()).to_intent()
        == request
    )
    observed = []
    registry = FinalizerRegistry().register_finalizer(
        request.kind,
        request.version,
        lambda intent, child, snapshot: (
            observed.append((intent, child, snapshot)) or RelatedWriteSet(read_set=())
        ),
    )
    registry.materialize_finalization(request, 42, "pin")
    assert observed == [(request, 42, "pin")]
    assert registry.materialize_finalization(
        ordinary_finalization(), 43, "pin"
    ) == RelatedWriteSet(read_set=())
    with pytest.raises(GraduationConflict, match="unregistered"):
        registry.materialize_finalization(
            request.model_copy(update={"version": 1}), 42, "pin"
        )
