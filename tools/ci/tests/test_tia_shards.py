import json
from collections import Counter
from dataclasses import replace
from hashlib import sha256

import pytest
from test_tia_inventory import _CI103, _HOSTED, _LOCAL, _SUITES, _collection, _encode
from tia.inventory import SuitePolicy, classify
from tia.shards import InventoryExpectation, assign


def key(row):
    return tuple(
        row[name] for name in ("provider", "owner", "platform_scope", "nodeid")
    )


@pytest.fixture(params=[_LOCAL, _HOSTED], ids=["local", "hosted"])
def source(request):
    policy = SuitePolicy(_SUITES.read_bytes(), _CI103.read_bytes(), "full")
    collection = _encode(
        _collection("product-cli", "ci-helpers", binding=request.param)
    )
    inventory = classify(collection, policy)
    doc = json.loads(inventory)
    expected = InventoryExpectation(
        policy,
        sha256(inventory).hexdigest(),
        _encode(request.param),
        tuple(map(_encode, doc["scopes"])),
    )
    return collection, inventory, expected, doc


def test_exact_union_balanced_and_no_isolation_group_split(source):
    collection, inventory, expected, doc = source
    rows = {key(row): row for row in doc["obligations"]}
    selected = tuple(rows)
    timings = {node: (index + 1) * 130 for index, node in enumerate(selected[::2])}
    plan = assign(collection, inventory, expected, selected, timings)
    assert plan == assign(collection, inventory, expected, selected[::-1], timings)
    assert plan.scope == "advisory"
    assert plan.inventory_sha256 == expected.inventory_sha256
    assert plan.collection_sha256 == sha256(collection).hexdigest()
    assert Counter(
        node for shard in plan.shards for node in shard.obligations
    ) == Counter(selected)
    assert all(
        count <= 2 for count in Counter(shard.lane for shard in plan.shards).values()
    )
    placements = {}
    for shard in plan.shards:
        for node in shard.obligations:
            group = shard.lane, rows[node]["isolation_group"]
            assert placements.setdefault(group, shard.slot) == shard.slot
    assert sum(shard.unknown_count for shard in plan.shards) == len(selected) - len(
        timings
    )


def test_empty_selection_ties_and_reassignment(source):
    collection, inventory, expected, doc = source
    rows = [row for row in doc["obligations"] if row["owner"] == "aitm-usage"]
    nodes = tuple(map(key, rows))
    assert assign(collection, inventory, expected, (), {}).shards == ()
    plan = assign(collection, inventory, expected, nodes, {})
    assert len(plan.shards) == 2
    assert all(shard.estimate_ms >= 1000 for shard in plan.shards)
    assert plan == assign(collection, inventory, expected, nodes[::-1], {})
    serial = assign(collection, inventory, expected, nodes, {}, max_shards=1)
    assert len(serial.shards) == 1
    assert serial.shards[0].obligations == tuple(sorted(nodes))


def test_rejects_bad_digest_binding_lanes_and_comparison(source):
    collection, inventory, expected, doc = source
    for amended, match in (
        (replace(expected, inventory_sha256="0" * 64), "digest"),
        (replace(expected, binding=b"{}"), "binding"),
        (replace(expected, lanes=expected.lanes[:1]), "lane"),
        (
            replace(
                expected,
                policy=replace(expected.policy, workload="compare-product-cli"),
            ),
            "full workload",
        ),
    ):
        with pytest.raises(ValueError, match=match):
            assign(collection, inventory, amended, (), {})
    del doc["obligations"][-1]
    truncated = _encode(doc)
    with pytest.raises(ValueError, match="projection"):
        assign(
            collection,
            truncated,
            replace(expected, inventory_sha256=sha256(truncated).hexdigest()),
            (),
            {},
        )


def test_rejects_missing_required_or_requested_and_invalid_timing(source):
    collection, inventory, expected, doc = source
    node = key(doc["obligations"][0])
    requested = (*node[:3], "tests/unknown.py::test_unknown")
    raw = json.loads(collection)
    required = next(row for row in doc["obligations"] if row["mandatory"])
    scope = next(row for row in raw["scopes"] if row["profile"] == required["profile"])
    scope["items"] = [
        row for row in scope["items"] if row["nodeid"] != required["nodeid"]
    ]
    with pytest.raises(ValueError, match="mandatory"):
        assign(_encode(raw), inventory, expected, (), {})
    for nodes, timings, limit, match in (
        ((requested,), {}, 2, "unknown"),
        ((node, node), {}, 2, "duplicate"),
        ((node,), {node: -1}, 2, "timing"),
        ((node,), {node: True}, 2, "timing"),
        ((node,), {}, 3, "cap"),
    ):
        with pytest.raises(ValueError, match=match):
            assign(collection, inventory, expected, nodes, timings, max_shards=limit)


def test_rejects_actual_incompatible_runner(source):
    collection, inventory, expected, _ = source
    raw = json.loads(collection)
    raw["scopes"][0]["runner"]["filesystem"] = "ext4"
    with pytest.raises(ValueError, match="incompatible runner"):
        assign(_encode(raw), inventory, expected, (), {})


def test_largest_first_tie_and_upper_median(source):
    collection, inventory, expected, doc = source
    groups = {}
    for row in doc["obligations"]:
        if row["owner"] == "aitm-usage":
            groups.setdefault(row["isolation_group"], key(row))
    first, second, third = [groups[group] for group in sorted(groups)[:3]]
    plan = assign(
        collection, inventory, expected, (third, second, first), {first: 1, second: 9}
    )
    assert plan.shards[0].obligations == tuple(sorted((first, second)))
    assert plan.shards[1].obligations == (third,)
    assert [shard.estimate_ms for shard in plan.shards] == [10, 9]
