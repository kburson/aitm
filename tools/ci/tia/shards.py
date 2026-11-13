"""Deterministic advisory assignments over an expected T02 inventory."""

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Literal

from . import inventory as t02

ObligationKey = tuple[str, str, str, str]
Lane = tuple[str, str, str, str]
_MAX_SHARDS = 2
_DEFAULT_ESTIMATE_MS = 1000


@dataclass(frozen=True)
class InventoryExpectation:
    """Independent expected T02 policy, digest, binding, and canonical lanes."""

    policy: t02.SuitePolicy
    inventory_sha256: str
    binding: bytes
    lanes: tuple[bytes, ...]


@dataclass(frozen=True)
class Shard:
    """One advisory placement in a provider, owner, profile, platform lane."""

    lane: Lane
    slot: int
    obligations: tuple[ObligationKey, ...]
    estimate_ms: int
    unknown_count: int


@dataclass(frozen=True)
class ShardPlan:
    collection_sha256: str
    inventory_sha256: str
    suite_policy_sha256: str
    ci103_policy_sha256: str
    max_shards: int
    shards: tuple[Shard, ...]
    scope: Literal["advisory"] = field(default="advisory", init=False)


@dataclass
class _Bin:
    obligations: list[ObligationKey] = field(default_factory=list)
    estimate_ms: int = 0
    unknown_count: int = 0
    groups: int = 0


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _verified_inventory(collection, inventory, expected):
    _require(expected.policy.workload == "full", "expected full workload policy")
    _require(isinstance(inventory, bytes), "expected T02 inventory bytes")
    _require(
        sha256(inventory).hexdigest() == expected.inventory_sha256,
        "inventory digest differs from expectation",
    )
    projected = t02.classify(collection, expected.policy)
    _require(inventory == projected, "inventory differs from exact T02 projection")
    document = t02._read(projected, "aitm.tia-inventory/v1")
    _require(
        document["scope_status"] == "complete_workload",
        "inventory must describe the full workload",
    )
    _require(
        t02._canonical(document["binding"]) == expected.binding,
        "inventory binding differs from expectation",
    )
    _require(
        tuple(map(t02._canonical, document["scopes"])) == expected.lanes,
        "inventory lanes differ from expectation",
    )
    return document


def _placements(lane, groups, timings, max_shards):
    known = sorted(
        timings[key] for keys in groups.values() for key in keys if key in timings
    )
    fallback = known[len(known) // 2] if known else _DEFAULT_ESTIMATE_MS
    estimates = {
        name: sum(timings.get(key, fallback) for key in keys)
        for name, keys in groups.items()
    }
    bins = [_Bin() for _ in range(min(max_shards, len(groups)))]
    for name in sorted(groups, key=lambda name: (-estimates[name], name)):
        slot = min(
            range(len(bins)),
            key=lambda slot: (bins[slot].estimate_ms, bins[slot].groups, slot),
        )
        placement = bins[slot]
        keys = groups[name]
        placement.obligations.extend(keys)
        placement.estimate_ms += estimates[name]
        placement.unknown_count += sum(key not in timings for key in keys)
        placement.groups += 1
    return tuple(
        Shard(
            lane,
            slot,
            tuple(sorted(bin.obligations)),
            bin.estimate_ms,
            bin.unknown_count,
        )
        for slot, bin in enumerate(bins)
    )


def assign(
    collection: bytes,
    inventory: bytes,
    expected: InventoryExpectation,
    requested: Sequence[ObligationKey],
    durations_ms: Mapping[ObligationKey, int],
    *,
    max_shards: int = _MAX_SHARDS,
) -> ShardPlan:
    """Assign exact requested obligations without dispatch or evidence authority.

    Timing hints are keyed by inventory obligation. Omit unknown durations.
    Slots are zero-based within a lane. A placement includes allowed-skip
    obligations when requested, retaining their metadata in the bound inventory.
    """
    _require(
        type(max_shards) is int and 1 <= max_shards <= _MAX_SHARDS, "invalid shard cap"
    )
    document = _verified_inventory(collection, inventory, expected)
    rows = {
        (row["provider"], row["owner"], row["platform_scope"], row["nodeid"]): row
        for row in document["obligations"]
    }
    keys = tuple(requested)
    _require(
        all(
            type(key) is tuple
            and len(key) == 4
            and all(type(part) is str for part in key)
            for key in keys
        ),
        "invalid requested obligation key",
    )
    _require(len(keys) == len(set(keys)), "duplicate requested obligation")
    _require(set(keys) <= rows.keys(), "unknown requested obligation")
    timings = dict(durations_ms)
    _require(
        timings.keys() <= rows.keys()
        and all(type(ms) is int and ms >= 0 for ms in timings.values()),
        "invalid timing hint",
    )

    lanes = defaultdict(lambda: defaultdict(list))
    for key in keys:
        row = rows[key]
        lane = row["provider"], row["owner"], row["profile"], row["platform_scope"]
        lanes[lane][row["isolation_group"]].append(key)
    shards = tuple(
        shard
        for lane, groups in sorted(lanes.items())
        for shard in _placements(lane, groups, timings, max_shards)
    )
    return ShardPlan(
        sha256(collection).hexdigest(),
        expected.inventory_sha256,
        document["suite_policy_sha256"],
        document["ci103_policy_sha256"],
        max_shards,
        shards,
    )
