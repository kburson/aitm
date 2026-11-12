"""Select pytest obligations from exact TIA evidence, without executing them."""

import re
from collections import defaultdict, deque
from dataclasses import dataclass, fields
from hashlib import new as hash_for
from hashlib import sha256
from typing import Literal

from . import inventory as t02
from .inventory import SuitePolicy
from .python_graph import (
    Edge,
    ProviderPolicy,
    UnresolvedScope,
    _policy_digest,
    build_graph,
)
from .snapshot import (
    Entry,
    GitEndpoint,
    HostedProvenance,
    LocalProvenance,
    Snapshot,
    SnapshotUncertain,
    WorktreeEndpoint,
)
from .snapshot import (
    _canonical as _snapshot_canonical,
)

ObligationKey = tuple[str, str, str, str]
Side = Literal["before", "after"]
Mode = Literal["selected", "full", "no-tests", "unavailable"]


@dataclass(frozen=True)
class InventoryPair:
    before: bytes | None
    after: bytes | None


@dataclass(frozen=True)
class CollectionIdentity:
    repository: str
    commit: str
    tree: str
    ref: str
    run_id: int
    run_attempt: int


@dataclass(frozen=True)
class InventoryExpectation:
    inventory_sha256: str
    suite_policy: SuitePolicy
    lanes: tuple[bytes, ...]  # Canonical T02 scope identities, in policy order.
    collection: CollectionIdentity | None = None


@dataclass(frozen=True)
class SelectionPolicy:
    before: InventoryExpectation
    after: InventoryExpectation
    provider: ProviderPolicy
    manifest: bytes


@dataclass(frozen=True)
class EvidenceIdentity:
    snapshot_sha256: str
    inventory_sha256: str | None
    suite_policy_sha256: str
    ci103_policy_sha256: str


@dataclass(frozen=True)
class Witness:
    path: bytes
    key: ObligationKey
    side: Side
    hops: tuple[Edge, ...]


@dataclass(frozen=True)
class Uncertainty:
    code: str
    side: Side | None = None
    reader: bytes | None = None
    detail: str = ""
    rule: str | None = None
    endpoints: tuple[bytes, ...] = ()
    possible_inputs: tuple[bytes, ...] | None = None


@dataclass(frozen=True)
class PathDisposition:
    path: bytes
    sides: tuple[Side, ...]
    disposition: Literal["resolved", "non-test", "uncertain"]
    rules: tuple[str, ...] = ()
    uncertainties: tuple[Uncertainty, ...] = ()


@dataclass(frozen=True)
class ObligationReason:
    key: ObligationKey
    code: Literal["mandatory", "newly-collected"]


@dataclass(frozen=True)
class Selection:
    mode: Mode
    before: EvidenceIdentity
    after: EvidenceIdentity
    selected: tuple[ObligationKey, ...] = ()
    removed: tuple[ObligationKey, ...] = ()
    reasons: tuple[str, ...] = ()
    provenance: str | None = None
    manifest_sha256: str | None = None
    provider_policy_sha256: str | None = None
    paths: tuple[PathDisposition, ...] = ()
    witnesses: tuple[Witness, ...] = ()
    obligation_reasons: tuple[ObligationReason, ...] = ()
    changed_obligations: tuple[ObligationKey, ...] = ()
    missing_required: tuple[ObligationKey, ...] = ()


_REGULAR = {"100644", "100755"}
_ENTRY_MODES = _REGULAR | {"120000"}


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _endpoint(snapshot, *, baseline):
    _require(
        isinstance(snapshot.baseline_identity, GitEndpoint)
        and bool(snapshot.repository)
        and (not baseline or snapshot.endpoint_identity == snapshot.baseline_identity)
        and (
            (snapshot.ref_role == "baseline")
            if baseline
            else snapshot.ref_role != "baseline"
        ),
        "snapshot role or baseline identity does not match",
    )
    endpoint = snapshot.endpoint_identity
    provenance = snapshot.provenance
    if snapshot.mode == "local":
        _require(
            isinstance(provenance, LocalProvenance)
            and (
                baseline
                or (
                    snapshot.ref_role == "local-effective"
                    and isinstance(endpoint, WorktreeEndpoint)
                    and snapshot.entries == provenance.observation.effective_entries
                    and endpoint.worktree_digest
                    == sha256(
                        _snapshot_canonical(
                            {"version": 1, "observation": provenance.observation}
                        )
                    ).hexdigest()
                )
            ),
            "local snapshot provenance does not match",
        )
    elif snapshot.mode == "hosted":
        _require(isinstance(provenance, HostedProvenance), "missing hosted binding")
        binding = provenance.binding
        _require(
            snapshot.repository == binding.repository
            and binding.base_commit == snapshot.baseline_identity.commit
            and type(binding.run_id) is int
            and binding.run_id > 0
            and type(binding.run_attempt) is int
            and binding.run_attempt > 0,
            "hosted binding does not match baseline",
        )
        if not baseline:
            _require(
                endpoint == GitEndpoint(binding.tested_commit, binding.tested_tree)
                and (
                    (
                        snapshot.ref_role == "pr-tested"
                        and bool(binding.pr_head)
                        and re.fullmatch(r"refs/pull/[1-9][0-9]*/merge", binding.ref)
                        is not None
                    )
                    or (
                        snapshot.ref_role == "trunk-tested"
                        and binding.pr_head is None
                        and binding.ref == "refs/heads/trunk"
                    )
                ),
                "hosted binding does not match tested endpoint",
            )
    else:
        raise ValueError("unrecognized snapshot mode")


def _entries(snapshot):
    result = {}
    previous = b""
    for entry in snapshot.entries:
        _require(
            isinstance(entry, Entry)
            and isinstance(entry.path, bytes)
            and entry.path > previous
            and b"\0" not in entry.path
            and not any(part in {b"", b".", b".."} for part in entry.path.split(b"/"))
            and entry.mode in _ENTRY_MODES,
            "invalid or repeated snapshot entry",
        )
        result[entry.path] = entry
        previous = entry.path
    return result


def _pair_changes(before, after, old, new):
    _require(
        before.repository == after.repository
        and before.mode == after.mode
        and before.baseline_identity == after.baseline_identity
        and before.provenance == after.provenance
        and before.changes == after.changes,
        "snapshot pair disagrees on provenance or change records",
    )
    prior_paths, current_paths = set(), set()
    for change in after.changes:
        left, right = change.old, change.new
        status = change.status
        _require(
            (
                status == "A"
                and left is None
                and right is not None
                and right.path not in old
            )
            or (
                status == "D"
                and right is None
                and left is not None
                and left.path not in new
            )
            or (
                left is not None
                and right is not None
                and (
                    (
                        status == "R"
                        and left.path not in new
                        and right.path not in old
                        and left.mode[:3] == right.mode[:3]
                    )
                    or (
                        left.path == right.path
                        and status == ("M" if left.mode[:3] == right.mode[:3] else "T")
                    )
                )
            ),
            "contradictory snapshot change",
        )
        for entry, catalog, visited in (
            (left, old, prior_paths),
            (right, new, current_paths),
        ):
            if entry is not None:
                _require(
                    catalog.get(entry.path) == entry and entry.path not in visited,
                    "snapshot change does not identify a unique endpoint entry",
                )
                visited.add(entry.path)
    _require(
        old.keys() - prior_paths == new.keys() - current_paths,
        "incomplete change membership",
    )

    def changed(path):
        if old[path].mode != new[path].mode:
            return True
        if after.mode == "hosted":
            return old[path].content_id != new[path].content_id
        data = after.read_content(path)
        digest = hash_for(after.provenance.git.object_format)
        digest.update(f"blob {len(data)}\0".encode("ascii"))
        digest.update(data)
        _require(
            sha256(data).hexdigest() == new[path].content_id,
            "local entry content differs",
        )
        return old[path].content_id != digest.hexdigest()

    for path in sorted(old.keys() & new.keys()):
        _require(
            changed(path) == (path in prior_paths and path in current_paths),
            "change records do not match endpoint content",
        )


def _expected_binding(snapshot, expected, digest):
    if snapshot.mode == "local":
        _require(
            expected.collection is None,
            "local inventory cannot bind a hosted collection",
        )
        return {
            "kind": "local_advisory",
            "repository": snapshot.repository,
            "snapshot": {"content_digest": digest},
        }

    collection = expected.collection
    endpoint = snapshot.endpoint_identity
    binding = snapshot.provenance.binding
    _require(
        isinstance(collection, CollectionIdentity)
        and collection.repository == snapshot.repository
        and (collection.commit, collection.tree) == (endpoint.commit, endpoint.tree)
        and type(collection.run_id) is int
        and collection.run_id > 0
        and type(collection.run_attempt) is int
        and collection.run_attempt > 0,
        "hosted collection does not match the endpoint",
    )
    if snapshot.ref_role == "baseline":
        _require(
            collection.ref == "refs/heads/trunk",
            "base collection is not from protected trunk",
        )
    else:
        _require(
            (collection.ref, collection.run_id, collection.run_attempt)
            == (binding.ref, binding.run_id, binding.run_attempt),
            "candidate collection does not match the hosted ref, run and attempt",
        )
    return {
        "kind": "hosted_collection_proof",
        "repository": collection.repository,
        "snapshot": {
            field.name: getattr(collection, field.name)
            for field in fields(collection)
            if field.name != "repository"
        },
    }


def _evidence(snapshot, raw, expected):
    return EvidenceIdentity(
        snapshot.digest,
        None if raw is None else sha256(raw).hexdigest(),
        sha256(expected.suite_policy.suites).hexdigest(),
        sha256(expected.suite_policy.ci103).hexdigest(),
    )


def _key(row):
    return row["provider"], row["owner"], row["platform_scope"], row["nodeid"]


def _source(key):
    return key[3].partition("::")[0].encode("utf-8")


class _MissingMandatory(ValueError):
    def __init__(self, keys):
        super().__init__("collection: missing mandatory node ID")
        self.keys = tuple(sorted(keys))


def _mandatory_gaps(collection, suite):
    rules = t02._policy(suite)
    scopes = t02._scopes(
        collection["scopes"], collection["binding"], rules.workloads["full"]
    )
    missing = []
    for (name, platform), scope in scopes.items():
        profile = rules.profiles[name]
        t02._scope_identity(scope, profile, rules.runners)
        observed = {item["nodeid"] for item in scope["items"]}
        missing.extend(
            ("pytest", profile["owner"], platform, node)
            for node in rules.mandatory[name] - observed
        )
    return missing


def _inventory_rows(snapshot, entries, raw, expected, evidence):
    _require(
        raw is not None and evidence.inventory_sha256 == expected.inventory_sha256,
        "original inventory digest does not match",
    )
    document = t02._read(raw, "aitm.tia-inventory/v1")
    _require(raw == t02._canonical(document), "inventory bytes are not canonical")
    binding = _expected_binding(snapshot, expected, evidence.snapshot_sha256)
    _require(
        document.get("binding") == binding,
        "inventory binding does not match independently expected collection",
    )
    _require(
        (document.get("suite_policy_sha256"), document.get("ci103_policy_sha256"))
        == (evidence.suite_policy_sha256, evidence.ci103_policy_sha256),
        "inventory policy digests do not match",
    )
    _require(
        expected.suite_policy.workload == document.get("workload") == "full"
        and document.get("scope_status") == "complete_workload",
        "inventory does not cover the full workload",
    )
    scopes = document.get("scopes")
    rows = document.get("obligations")
    _require(
        isinstance(scopes, list)
        and isinstance(rows, list)
        and tuple(map(t02._canonical, scopes)) == expected.lanes,
        "inventory lane identities do not match",
    )

    # Reproject the complete rows using T02 instead of replicating its scope,
    # capability, mandatory, ordering or metadata rules in the selector.
    lanes = {}
    for scope in scopes:
        pair = (scope["profile"], scope["platform_scope"])
        _require(pair not in lanes, "repeated inventory lane")
        lanes[pair] = dict(
            scope, binding=binding, exit_code=0, complete=True, deselected=[], items=[]
        )
    obligations = {}
    for row in rows:
        key = _key(row)
        _require(key not in obligations, "duplicate inventory obligation")
        obligations[key] = row
        node = row["nodeid"]
        item = {"nodeid": node, "disposition": row["disposition"]}
        if item["disposition"] == "allowed_skip":
            item["reason"] = row["optional_skip_reason"]
        lanes[(row["profile"], row["platform_scope"])]["items"].append(item)

    collection = {
        "schema": "aitm.tia-collection/v1",
        "binding": binding,
        "scopes": list(lanes.values()),
    }
    try:
        projected = t02.classify(t02._canonical(collection), expected.suite_policy)
    except ValueError as error:
        if str(error) in (
            "collection: missing mandatory node ID",
            "collection: unsuccessful, incomplete, empty or deselected",
        ) and (gaps := _mandatory_gaps(collection, expected.suite_policy)):
            raise _MissingMandatory(gaps) from error
        raise
    _require(raw == projected, "inventory rows differ from the exact T02 projection")
    for key in obligations:
        entry = entries.get(_source(key))
        _require(
            entry is not None and entry.mode in _REGULAR,
            "inventory test source is not a regular endpoint entry",
        )
    return obligations


@dataclass(frozen=True)
class _PathRule:
    rule: str
    kind: str


def _manifest_path(value):
    _require(
        isinstance(value, str)
        and not any(part in {"", ".", ".."} for part in value.split("/"))
        and not re.search(r"[\\*?\[\]\x00-\x1f\x7f]", value)
        and not re.match(r"^[A-Za-z]:", value),
        "manifest path must be an exact repository-relative UTF-8 path",
    )
    return value.encode("utf-8")


def _declarations(raw):
    doc = t02._read(raw, "aitm.tia-edges/v1")
    _require(
        set(doc) == {"schema", "edges", "path_rules"}
        and isinstance(doc["edges"], list)
        and isinstance(doc["path_rules"], list),
        "invalid declaration manifest shape",
    )
    identifiers = set()

    def row_id(row, keys):
        _require(
            isinstance(row, dict) and row.keys() == keys,
            "invalid declaration row shape",
        )
        rule, rationale = row["id"], row["rationale"]
        _require(
            isinstance(rule, str)
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", rule)
            and rule not in identifiers
            and isinstance(rationale, str)
            and rationale.strip(),
            "invalid or repeated declaration identifier or missing rationale",
        )
        identifiers.add(rule)
        return rule

    edges = {}
    for row in doc["edges"]:
        rule = row_id(row, {"id", "consumer", "input", "kind", "rationale"})
        consumer, dependency = (
            _manifest_path(row["consumer"]),
            _manifest_path(row["input"]),
        )
        kind = row["kind"]
        _require(
            kind in ("runtime-file", "subprocess", "fixture"),
            "invalid declared edge kind",
        )
        key = consumer, dependency, kind
        _require(
            consumer != dependency and key not in edges,
            "self or repeated declared edge",
        )
        edges[key] = Edge(*key, (rule,))
    rules = {}
    for row in doc["path_rules"]:
        rule = row_id(row, {"id", "path", "kind", "rationale"})
        path, kind = _manifest_path(row["path"]), row["kind"]
        _require(
            kind in ("non-test", "shared-input") and path not in rules,
            "invalid or conflicting path rule",
        )
        rules[path] = _PathRule(rule, kind)
    return tuple(edges[key] for key in sorted(edges)), rules


def _changed_paths(changes):
    paths = defaultdict(list)
    for change in changes:
        if change.old is not None:
            paths[change.old.path].append("before")
        if change.new is not None:
            paths[change.new.path].append("after")
    return {
        path: tuple(side for side in ("before", "after") if side in paths[path])
        for path in sorted(paths)
    }


def _unknown_paths(paths, code):
    return tuple(
        PathDisposition(path, sides, "uncertain", uncertainties=(Uncertainty(code),))
        for path, sides in paths.items()
    )


@dataclass
class _SideGraph:
    reverse: dict
    unresolved: tuple
    missing: dict
    declarations: set
    tests: dict


def _side_graph(snapshot, entries, inventory, surviving, provider, declarations):
    graph = build_graph(snapshot, provider)
    reverse = defaultdict(list)
    missing = defaultdict(list)
    declared_endpoints = set()
    for edge in graph.edges:
        reverse[edge.input].append(edge)
    for edge in declarations:
        endpoints = (edge.input, edge.consumer)
        invalid = tuple(
            path
            for path in endpoints
            if entries.get(path) is None or entries[path].mode not in _REGULAR
        )
        if invalid:
            for path in endpoints:
                missing[path].append((edge.rules[0], invalid))
        else:
            reverse[edge.input].append(edge)
            declared_endpoints.update(endpoints)
    for edges in reverse.values():
        edges.sort(key=lambda e: (e.consumer, e.kind, e.rules))

    tests = defaultdict(list)
    for key in inventory:
        if key in surviving:
            tests[_source(key)].append(key)
    unresolved = list(graph.unresolved)
    for path in sorted({_source(key) for key in inventory}):
        # Use the T04 scope membership rule, including the distinction
        # between explicit test paths and conftest files beneath test roots.
        if not any(
            path in scope.test_paths
            or (
                path.endswith(b".py")
                and path.rpartition(b"/")[2] != b"conftest.py"
                and any(
                    not root or path.startswith(root + b"/")
                    for root in scope.test_roots
                )
            )
            for scope in provider.pytest_scopes
        ):
            unresolved.append(
                UnresolvedScope(
                    path,
                    "pytest-collection-scope-missing",
                    "no qualified pytest scope",
                    None,
                )
            )
    return _SideGraph(reverse, tuple(unresolved), missing, declared_endpoints, tests)


def _walk(seed, reverse):
    queue = deque([seed])
    parent = {seed: None}
    while queue:
        path = queue.popleft()
        for edge in reverse.get(path, ()):
            if edge.consumer not in parent:
                parent[edge.consumer] = edge
                queue.append(edge.consumer)
    return parent


def _hops(path, parent):
    result = []
    while (edge := parent[path]) is not None:
        result.append(edge)
        path = edge.input
    return tuple(reversed(result))


def _trace(path, sides, graphs, rule):
    uncertainties = []
    witnesses = []
    graph_evidence = False
    for side in sides:
        graph = graphs.get(side)
        if graph is None:
            uncertainties.append(Uncertainty("graph-unavailable", side))
            continue
        reached = _walk(path, graph.reverse)
        graph_evidence |= len(reached) > 1 or path in graph.declarations
        for consumer in reached:
            if keys := graph.tests.get(consumer):
                hops = _hops(consumer, reached)
                witnesses.extend(Witness(path, key, side, hops) for key in keys)
        for record in graph.unresolved:
            bounds = record.possible_inputs
            if bounds is None or any(
                candidate == prefix or candidate.startswith(prefix + b"/")
                for candidate in reached
                for prefix in bounds
            ):
                uncertainties.append(
                    Uncertainty(
                        record.reason,
                        side,
                        record.reader,
                        record.detail,
                        possible_inputs=bounds,
                    )
                )
        invalid_declarations = {
            item for candidate in reached for item in graph.missing.get(candidate, ())
        }
        uncertainties.extend(
            Uncertainty(
                "declaration-endpoint-unavailable",
                side,
                rule=identifier,
                endpoints=endpoints,
            )
            for identifier, endpoints in sorted(invalid_declarations)
        )

    if rule and rule.kind == "shared-input":
        uncertainties.append(Uncertainty("shared-input", rule=rule.rule))
    if uncertainties:
        disposition = "uncertain"
    elif witnesses:
        disposition = "resolved"
    elif rule and rule.kind == "non-test" and not graph_evidence:
        disposition = "non-test"
    else:
        disposition = "uncertain"
        uncertainties.append(Uncertainty("unclassified-change"))
    return (
        PathDisposition(
            path, sides, disposition, (rule.rule,) if rule else (), tuple(uncertainties)
        ),
        witnesses,
    )


def _mode(selected, paths, reasons) -> Mode:
    if reasons or any(path.disposition == "uncertain" for path in paths):
        return "full"
    if selected:
        return "selected"
    if paths and all(path.disposition == "non-test" for path in paths):
        return "no-tests"
    return "full"


def select(
    before: Snapshot, after: Snapshot, inventory: InventoryPair, policy: SelectionPolicy
) -> Selection:
    """Return an exact selection or a conservative fallback without executing tests."""
    prior = _evidence(before, inventory.before, policy.before)
    current = _evidence(after, inventory.after, policy.after)
    provenance = "local_advisory" if after.mode == "local" else after.mode
    manifest_digest = sha256(policy.manifest).hexdigest()
    provider_digest = None
    old, new = None, None
    old_entries, new_entries = None, None
    reasons = []
    missing_required = ()

    try:
        _endpoint(after, baseline=False)
        new_entries = _entries(after)
        new = _inventory_rows(
            after, new_entries, inventory.after, policy.after, current
        )
    except (ValueError, TypeError, KeyError) as error:
        reasons.append(f"candidate-inventory: {error}")
        if isinstance(error, _MissingMandatory):
            missing_required = error.keys
    try:
        _endpoint(before, baseline=True)
        old_entries = _entries(before)
        old = _inventory_rows(
            before, old_entries, inventory.before, policy.before, prior
        )
    except (ValueError, TypeError, KeyError) as error:
        reasons.append(f"baseline-inventory: {error}")
    exact_pair = False
    if old_entries is not None and new_entries is not None:
        try:
            _pair_changes(before, after, old_entries, new_entries)
            exact_pair = True
        except (ValueError, SnapshotUncertain) as error:
            reasons.append(f"snapshot-pair: {error}")

    try:
        provider_digest = _policy_digest(policy.provider)
    except ValueError as error:
        reasons.append(f"provider-policy: {error}")
    try:
        declared, rules = _declarations(policy.manifest)
    except ValueError as error:
        declared, rules = (), {}
        reasons.append(f"declaration-manifest: {error}")

    paths = _changed_paths(after.changes) if exact_pair else {}
    common = {
        "before": prior,
        "after": current,
        "provenance": provenance,
        "manifest_sha256": manifest_digest,
        "provider_policy_sha256": provider_digest,
    }
    if new is None:
        removed = ()
        if exact_pair and old is not None:
            deleted = {
                change.old.path for change in before.changes if change.status == "D"
            }
            removed = tuple(key for key in old if _source(key) in deleted)
        return Selection(
            "unavailable",
            removed=removed,
            missing_required=missing_required,
            reasons=tuple(reasons),
            paths=_unknown_paths(paths, "candidate-inventory-unavailable"),
            **common,
        )

    obligations = [
        ObligationReason(key, "mandatory")
        for key, row in new.items()
        if row["mandatory"]
    ]
    if (prior.suite_policy_sha256, prior.ci103_policy_sha256) != (
        current.suite_policy_sha256,
        current.ci103_policy_sha256,
    ):
        reasons.append("inventory-policy-changed")
    if not exact_pair:
        return Selection(
            "full",
            selected=tuple(new),
            reasons=tuple(reasons),
            obligation_reasons=tuple(obligations),
            **common,
        )

    removed = changed = ()
    if old is not None:
        removed = tuple(sorted(old.keys() - new.keys()))
        changed = tuple(key for key in new if key in old and old[key] != new[key])
        obligations.extend(
            ObligationReason(key, "newly-collected")
            for key in sorted(new.keys() - old.keys())
        )
        if removed:
            reasons.append(
                "obligations-removed: downstream inventory disposition required"
            )
        if changed:
            reasons.append("obligation-rows-changed")
    graphs = {}
    if provider_digest is not None:
        for side, snapshot, entries, rows in (
            ("before", before, old_entries, old),
            ("after", after, new_entries, new),
        ):
            if rows is None:
                continue
            try:
                graphs[side] = _side_graph(
                    snapshot, entries, rows, new, policy.provider, declared
                )
            except (ValueError, SnapshotUncertain) as error:
                reasons.append(f"{side}-graph: {error}")

    dispositions, witnesses = [], []
    for path, sides in paths.items():
        disposition, matched = _trace(path, sides, graphs, rules.get(path))
        dispositions.append(disposition)
        witnesses.extend(matched)
    selected_keys = {item.key for item in witnesses} | {
        item.key for item in obligations
    }
    selected = tuple(key for key in new if key in selected_keys)
    mode = _mode(selected, dispositions, reasons)
    return Selection(
        mode,
        selected=tuple(new) if mode == "full" else selected,
        removed=removed,
        reasons=tuple(reasons),
        paths=tuple(dispositions),
        witnesses=tuple(
            sorted(witnesses, key=lambda w: (w.path, w.key, w.side != "before"))
        ),
        obligation_reasons=tuple(sorted(obligations, key=lambda o: (o.key, o.code))),
        changed_obligations=changed,
        **common,
    )
