"""Bind gate-control changes and inventory replay to trusted evidence."""

import base64
import json
import re
from dataclasses import asdict, dataclass, is_dataclass, replace
from hashlib import sha256

from tia.inventory import Inventory, _git_ref, _node
from tia.snapshot import Entry, GitEndpoint, HostedBinding, HostedProvenance, Snapshot
from verify_pr import CI_CONFIG_NAMES, gate_controls

_CONTROL_RULES = "aitm.tia-control-rules/v1"
_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
_PR_REF = re.compile(r"refs/pull/[1-9][0-9]*/merge")
_MODES = {"100644": "blob", "100755": "blob", "120000": "blob", "160000": "commit"}


@dataclass(frozen=True)
class Lane:
    profile: str
    owner: str
    platform_scope: str
    runner: tuple[tuple[str, str], ...]
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class Scope:
    workload: str
    lanes: tuple[Lane, ...]
    suite_policy_sha256: str
    ci103_policy_sha256: str


@dataclass(frozen=True)
class ControlCandidate:
    snapshot: Snapshot
    target_ref: str
    workflow_id: int
    scope: Scope


@dataclass(frozen=True)
class ControlBinding:
    repository: str
    target_ref: str
    source_ref: str
    base: GitEndpoint
    tested: GitEndpoint
    pr_head: str | None
    scope: Scope
    base_controls_sha256: str
    candidate_controls_sha256: str
    delta_sha256: str


@dataclass(frozen=True)
class ControlDecision:
    actor: str
    record_id: str
    binding: ControlBinding


@dataclass(frozen=True)
class ControlApprovals:
    owner: ControlDecision | None = None
    reviewer: ControlDecision | None = None


@dataclass(frozen=True)
class ControlEntry:
    path: bytes
    mode: str
    object_type: str
    object_id: str


@dataclass(frozen=True)
class ControlChange:
    status: str
    old: ControlEntry | None
    new: ControlEntry | None


@dataclass(frozen=True)
class ControlDisposition:
    full_required: bool
    hold_reason: str | None = None
    binding: ControlBinding | None = None
    changes: tuple[ControlChange, ...] = ()
    workflow_id: int | None = None
    run_id: int | None = None
    run_attempt: int | None = None
    approval_refs: tuple[str, ...] = ()


def _json_default(value):
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if is_dataclass(value):
        return asdict(value)
    raise TypeError(f"cannot encode {type(value).__name__}")


def _canonical(value) -> bytes:
    return json.dumps(
        value,
        default=_json_default,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _hash(value) -> str:
    return sha256(_canonical(value)).hexdigest()


def _text(value) -> bool:
    return isinstance(value, str) and value.isprintable() and value.strip() == value


def _digest(value, *lengths) -> bool:
    return (
        isinstance(value, str)
        and len(value) in lengths
        and re.fullmatch(r"[0-9a-f]+", value) is not None
    )


def _endpoint(value) -> bool:
    return (
        isinstance(value, GitEndpoint)
        and _digest(value.commit, 40, 64)
        and _digest(value.tree, len(value.commit))
    )


def _lanes(lanes: tuple[Lane, ...]) -> tuple[Lane, ...]:
    if not isinstance(lanes, tuple) or not lanes:
        raise ValueError("invalid lane set")
    normalized = {}
    for lane in lanes:
        if (
            not isinstance(lane, Lane)
            or not all(map(_text, (lane.profile, lane.owner, lane.platform_scope)))
            or not isinstance(lane.runner, tuple)
            or not all(
                isinstance(pair, tuple) and len(pair) == 2 and all(map(_text, pair))
                for pair in lane.runner
            )
            or not isinstance(lane.capabilities, tuple)
            or not all(map(_text, lane.capabilities))
        ):
            raise ValueError("invalid lane")
        key = (lane.profile, lane.platform_scope)
        runner = dict(lane.runner)
        if (
            key in normalized
            or {"profile", "name"} - runner.keys()
            or len(runner) != len(lane.runner)
            or len(set(lane.capabilities)) != len(lane.capabilities)
        ):
            raise ValueError("duplicate or incomplete lane")
        normalized[key] = replace(
            lane,
            runner=tuple(sorted(runner.items())),
            capabilities=tuple(sorted(lane.capabilities)),
        )
    return tuple(normalized[key] for key in sorted(normalized))


def _control_entry(entry: Entry) -> ControlEntry:
    return ControlEntry(entry.path, entry.mode, _MODES[entry.mode], entry.content_id)


def _controls(entries: dict[bytes, Entry]) -> dict[bytes, ControlEntry]:
    decoded = {
        path.decode("utf-8", "surrogateescape"): entry
        for path, entry in entries.items()
    }
    legacy = gate_controls(
        {
            path: {
                "mode": entry.mode,
                "type": _MODES[entry.mode],
                "sha": entry.content_id,
            }
            for path, entry in decoded.items()
        }
    )
    return {
        entry.path: _control_entry(entry)
        for path, entry in decoded.items()
        if path in legacy or ("/" in path and path.rsplit("/", 1)[1] in CI_CONFIG_NAMES)
    }


def _controls_hash(projection: dict[bytes, ControlEntry]) -> str:
    return _hash(
        {
            "rules": _CONTROL_RULES,
            "entries": [projection[path] for path in sorted(projection)],
        }
    )


def _control_delta(
    base: Snapshot, after: Snapshot
) -> tuple[str, str, tuple[ControlChange, ...]]:
    old_entries = {entry.path: entry for entry in base.entries}
    new_entries = {entry.path: entry for entry in after.entries}
    old_controls, new_controls = _controls(old_entries), _controls(new_entries)
    unmatched = {
        (side, path)
        for side, projection, other in (
            ("old", old_controls, new_controls),
            ("new", new_controls, old_controls),
        )
        for path, entry in projection.items()
        if other.get(path) != entry
    }
    changes = []
    for change in after.changes:
        if not (
            (change.old and change.old.path in old_controls)
            or (change.new and change.new.path in new_controls)
        ):
            continue
        for side, entry, entries, projection in (
            ("old", change.old, old_entries, old_controls),
            ("new", change.new, new_entries, new_controls),
        ):
            if entry is None:
                continue
            if entries.get(entry.path) != entry:
                raise ValueError("inexact control change endpoint")
            if entry.path in projection:
                unmatched.remove((side, entry.path))
        changes.append(
            ControlChange(
                change.status,
                _control_entry(change.old) if change.old else None,
                _control_entry(change.new) if change.new else None,
            )
        )
    if unmatched:
        raise ValueError("inconsistent projected changes")
    return _controls_hash(old_controls), _controls_hash(new_controls), tuple(changes)


def _valid_pair(base: Snapshot, candidate: ControlCandidate) -> bool:
    if not isinstance(base, Snapshot) or not isinstance(candidate, ControlCandidate):
        return False
    after = candidate.snapshot
    if (
        not isinstance(after, Snapshot)
        or base.mode != "hosted"
        or after.mode != "hosted"
        or base.ref_role != "baseline"
        or not isinstance(base.provenance, HostedProvenance)
        or base.provenance != after.provenance
        or base.changes != after.changes
        or not _endpoint(base.endpoint_identity)
        or not _endpoint(after.endpoint_identity)
        or base.endpoint_identity != base.baseline_identity
        or base.endpoint_identity != after.baseline_identity
    ):
        return False
    hosted = base.provenance.binding
    if (
        not isinstance(hosted, HostedBinding)
        or not isinstance(hosted.repository, str)
        or not _REPOSITORY.fullmatch(hosted.repository)
        or base.repository != hosted.repository
        or after.repository != hosted.repository
        or base.endpoint_identity.commit != hosted.base_commit
        or after.endpoint_identity
        != GitEndpoint(hosted.tested_commit, hosted.tested_tree)
        or not isinstance(hosted.ref, str)
        or not all(
            type(number) is int and number > 0
            for number in (hosted.run_id, hosted.run_attempt, candidate.workflow_id)
        )
        or not _git_ref(candidate.target_ref)
        or not candidate.target_ref.startswith("refs/heads/")
    ):
        return False
    if after.ref_role == "pr-tested":
        return _PR_REF.fullmatch(hosted.ref) is not None and _digest(
            hosted.pr_head, len(hosted.tested_commit)
        )
    return (
        after.ref_role == "trunk-tested"
        and hosted.ref == candidate.target_ref == "refs/heads/trunk"
        and hosted.pr_head is None
    )


def _approval_hold(approvals: ControlApprovals, binding: ControlBinding) -> str | None:
    if not isinstance(approvals, ControlApprovals):
        return "malformed_approval"
    owner, reviewer = approvals.owner, approvals.reviewer
    if owner is None or reviewer is None:
        return "missing_approval"
    if not all(
        isinstance(record, ControlDecision)
        and _text(record.actor)
        and _text(record.record_id)
        and isinstance(record.binding, ControlBinding)
        and isinstance(record.binding.scope, Scope)
        for record in (owner, reviewer)
    ):
        return "malformed_approval"
    if owner.actor == reviewer.actor or owner.record_id == reviewer.record_id:
        return "approval_conflict"
    for decision in (owner, reviewer):
        scope = decision.binding.scope
        try:
            scope = replace(scope, lanes=_lanes(scope.lanes))
        except ValueError:
            return "malformed_approval"
        if replace(decision.binding, scope=scope) != binding:
            return "approval_mismatch"
    return None


def qualify_controls(
    base: Snapshot, candidate: ControlCandidate, approvals: ControlApprovals
) -> ControlDisposition:
    """Bind exact source approval and retain full validation for changed controls.

    Snapshots, workflow metadata, scope and decisions come from a trusted
    caller. The result carries the execution attempt independently of the
    source decisions and confers no runtime or merge authority.
    """
    if not _valid_pair(base, candidate):
        return ControlDisposition(True, "invalid_snapshot_pair")
    scope = candidate.scope
    if (
        not isinstance(scope, Scope)
        or not _text(scope.workload)
        or not _digest(scope.suite_policy_sha256, 64)
        or not _digest(scope.ci103_policy_sha256, 64)
    ):
        return ControlDisposition(True, "invalid_scope")
    try:
        scope = replace(scope, lanes=_lanes(scope.lanes))
    except ValueError:
        return ControlDisposition(True, "invalid_scope")
    after = candidate.snapshot
    try:
        old_controls, new_controls, changes = _control_delta(base, after)
    except (KeyError, ValueError):
        return ControlDisposition(True, "invalid_snapshot_pair")
    hosted = after.provenance.binding
    binding = ControlBinding(
        repository=after.repository,
        target_ref=candidate.target_ref,
        source_ref=hosted.ref,
        base=base.endpoint_identity,
        tested=after.endpoint_identity,
        pr_head=hosted.pr_head,
        scope=scope,
        base_controls_sha256=old_controls,
        candidate_controls_sha256=new_controls,
        delta_sha256=_hash({"rules": _CONTROL_RULES, "changes": changes}),
    )
    hold = _approval_hold(approvals, binding) if changes else None
    refs = ()
    if changes and hold is None:
        refs = (approvals.owner.record_id, approvals.reviewer.record_id)
    return ControlDisposition(
        full_required=bool(changes),
        hold_reason=hold,
        binding=binding,
        changes=changes,
        workflow_id=candidate.workflow_id,
        run_id=hosted.run_id,
        run_attempt=hosted.run_attempt,
        approval_refs=refs,
    )


@dataclass(frozen=True)
class InventoryPoint:
    """Exact revision and SHA-256 of the T02-ordered canonical row array."""

    endpoint: GitEndpoint
    suite_policy_sha256: str
    ci103_policy_sha256: str
    obligations_sha256: str


@dataclass(frozen=True)
class QualifiedReference:
    inventory: bytes
    expected_sha256: str
    receipt_id: str
    anchor: InventoryPoint
    lanes: tuple[Lane, ...]


@dataclass(frozen=True)
class InventoryTarget:
    repository: str
    target_ref: str
    workload: str
    lanes: tuple[Lane, ...]
    point: InventoryPoint
    path: tuple[InventoryPoint, ...]


@dataclass(frozen=True)
class InventoryDelta:
    """Canonical UTF-8 JSON for each full row, with None for absence."""

    before: bytes | None
    after: bytes | None


@dataclass(frozen=True)
class InventoryStepBinding:
    """Bind authority to both points, complete lanes, and the exact delta.

    The delta digest covers canonical JSON with schema
    ``aitm.tia-inventory-delta/v1`` and a changes array of ordered
    ``{"before": row_or_null, "after": row_or_null}`` records.
    """

    repository: str
    target_ref: str
    workload: str
    lanes: tuple[Lane, ...]
    before: InventoryPoint
    after: InventoryPoint
    delta_sha256: str


@dataclass(frozen=True)
class InventoryEvidence:
    record_id: str
    binding: InventoryStepBinding


@dataclass(frozen=True)
class InventoryStep:
    before: InventoryPoint
    after: InventoryPoint
    deltas: tuple[InventoryDelta, ...]
    delivery: InventoryEvidence
    review: InventoryEvidence | None = None


class InventoryHold(ValueError):
    """A specific inventory comparison requirement did not verify."""


_FULL_PROFILES = {"ci-helpers": "ci-tools", "product-cli": "aitm-usage"}
_KEY_FIELDS = ("provider", "owner", "platform_scope", "nodeid")
_ROW_FIELDS = {
    *_KEY_FIELDS,
    "profile",
    "suite",
    "isolation_group",
    "required_capabilities",
    "mandatory",
    "optional_skip_reason",
    "required_children",
    "disposition",
}
_INVENTORY_FIELDS = {
    "schema",
    "binding",
    "workload",
    "scope_status",
    "suite_policy_sha256",
    "ci103_policy_sha256",
    "scopes",
    "obligations",
}
_PRODUCT_TESTS = "packages/aitm-usage/tests/"
_CLI_CASE = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"


def _require(condition, reason):
    if not condition:
        raise InventoryHold(reason)


def _record(raw: bytes, reason: str) -> dict:
    _require(isinstance(raw, bytes), reason)
    try:
        decoded = json.loads(raw)
        canonical = _canonical(decoded)
    except (ValueError, RecursionError) as error:
        raise InventoryHold(reason) from error
    _require(isinstance(decoded, dict) and canonical == raw, reason)
    return decoded


def _valid_point(point) -> bool:
    return (
        isinstance(point, InventoryPoint)
        and _endpoint(point.endpoint)
        and all(
            _digest(digest, 64)
            for digest in (
                point.suite_policy_sha256,
                point.ci103_policy_sha256,
                point.obligations_sha256,
            )
        )
    )


def _inventory_lanes(lanes: tuple[Lane, ...]) -> tuple[Lane, ...]:
    try:
        normalized = _lanes(lanes)
    except ValueError as error:
        raise InventoryHold("invalid_lane_set") from error
    _require(
        {lane.profile: lane.owner for lane in normalized} == _FULL_PROFILES
        and all(_FULL_PROFILES.get(lane.profile) == lane.owner for lane in normalized),
        "incomplete_full_workload",
    )
    return normalized


def _lane_key(item):
    return (item["profile"], item["platform_scope"])


def _row_key(row):
    return tuple(row[field] for field in _KEY_FIELDS)


def _valid_names(names) -> bool:
    return (
        isinstance(names, list)
        and all(map(_text, names))
        and names == sorted(set(names))
    )


def _validate_row(row: dict, lanes: dict[tuple[str, str], Lane]) -> None:
    error = "invalid_obligation_row"
    _require(isinstance(row, dict) and row.keys() == _ROW_FIELDS, error)
    _require(all(_text(row[field]) for field in (*_KEY_FIELDS, "profile")), error)
    try:
        source, _ = _node(row["nodeid"], error)
    except ValueError as exc:
        raise InventoryHold(error) from exc
    lane = lanes.get(_lane_key(row))
    skip = row["optional_skip_reason"]
    _require(
        lane is not None
        and row["provider"] == "pytest"
        and row["owner"] == lane.owner
        and row["suite"] in ("unit", "integration", "system")
        and _text(row["isolation_group"])
        and type(row["mandatory"]) is bool
        and _valid_names(row["required_children"])
        and _valid_names(row["required_capabilities"])
        and set(row["required_capabilities"]) <= set(lane.capabilities)
        and (skip is None or _text(skip))
        and (
            row["disposition"] == "collected"
            or (
                row["disposition"] == "allowed_skip"
                and skip is not None
                and not row["mandatory"]
            )
        ),
        error,
    )
    if lane.profile == "product-cli":
        _require(source.startswith(_PRODUCT_TESTS) or row["nodeid"] == _CLI_CASE, error)
    else:
        _require(re.fullmatch(r"tools/ci/tests/test_[A-Za-z0-9_]+\.py", source), error)


def _ordered_rows(rows: dict) -> list[dict]:
    return [rows[key] for key in sorted(rows)]


def _helper_sources(rows) -> set[tuple[str, str, str]]:
    return {
        (*_lane_key(row), row["nodeid"].partition("::")[0])
        for row in rows
        if row["profile"] == "ci-helpers"
    }


def _validate_reference(
    reference: QualifiedReference,
    target: InventoryTarget,
    lanes: dict[tuple[str, str], Lane],
) -> tuple[dict, dict]:
    error = "unqualified_reference"
    _require(
        isinstance(reference.inventory, bytes)
        and sha256(reference.inventory).hexdigest() == reference.expected_sha256
        and _text(reference.receipt_id),
        error,
    )
    document = _record(reference.inventory, error)
    _require(
        document.keys() == _INVENTORY_FIELDS
        and document["schema"] == "aitm.tia-inventory/v1"
        and document["workload"] == "full"
        and document["scope_status"] == "complete_workload"
        and document["suite_policy_sha256"] == reference.anchor.suite_policy_sha256
        and document["ci103_policy_sha256"] == reference.anchor.ci103_policy_sha256,
        error,
    )
    binding = document["binding"]
    _require(
        isinstance(binding, dict)
        and binding.keys() == {"kind", "repository", "snapshot"}
        and binding["kind"] == "hosted_collection_proof"
        and binding["repository"] == target.repository,
        error,
    )
    snapshot = binding["snapshot"]
    _require(
        isinstance(snapshot, dict)
        and snapshot.keys() == {"commit", "tree", "ref", "run_id", "run_attempt"}
        and snapshot["commit"] == reference.anchor.endpoint.commit
        and snapshot["tree"] == reference.anchor.endpoint.tree
        and snapshot["ref"] == target.target_ref
        and all(
            type(snapshot[field]) is int and snapshot[field] > 0
            for field in ("run_id", "run_attempt")
        ),
        error,
    )

    seen = set()
    _require(isinstance(document["scopes"], list), "reference_lane_mismatch")
    for scope in document["scopes"]:
        _require(
            isinstance(scope, dict)
            and scope.keys()
            == {
                "profile",
                "platform_scope",
                "runner",
                "capabilities",
                "observer",
                "controls",
                "receipt_sha256",
            }
            and _text(scope["profile"])
            and _text(scope["platform_scope"]),
            "reference_lane_mismatch",
        )
        key = _lane_key(scope)
        lane = lanes.get(key)
        _require(
            lane is not None
            and key not in seen
            and scope["runner"] == dict(lane.runner)
            and scope["capabilities"] == list(lane.capabilities),
            "reference_lane_mismatch",
        )
        seen.add(key)
    _require(seen == lanes.keys(), "reference_lane_mismatch")

    rows = {}
    _require(isinstance(document["obligations"], list), error)
    for row in document["obligations"]:
        _validate_row(row, lanes)
        key = _row_key(row)
        _require(key not in rows, "duplicate_obligation")
        rows[key] = row
    _require(
        {_lane_key(row) for row in rows.values()} == lanes.keys(),
        "reference_lane_mismatch",
    )
    _require(
        document["obligations"] == _ordered_rows(rows)
        and _hash(document["obligations"]) == reference.anchor.obligations_sha256,
        "reference_row_digest_mismatch",
    )
    return document, rows


def _decode_deltas(
    deltas: tuple[InventoryDelta, ...], lanes: dict[tuple[str, str], Lane]
) -> list[dict]:
    changes = []
    last = None
    _require(isinstance(deltas, tuple), "invalid_delta")
    for delta in deltas:
        _require(isinstance(delta, InventoryDelta), "invalid_delta")
        before = (
            _record(delta.before, "invalid_delta") if delta.before is not None else None
        )
        after = (
            _record(delta.after, "invalid_delta") if delta.after is not None else None
        )
        _require(before != after, "invalid_delta")
        for row in (before, after):
            if row is not None:
                _validate_row(row, lanes)
        key = _row_key(before if before is not None else after)
        _require(
            (last is None or key > last) and (after is None or _row_key(after) == key),
            "invalid_delta_order_or_key",
        )
        changes.append({"before": before, "after": after})
        last = key
    return changes


def _match_step_evidence(
    evidence: InventoryEvidence,
    expected: InventoryStepBinding,
    seen_ids: set[str],
    reason: str,
) -> None:
    _require(
        isinstance(evidence, InventoryEvidence)
        and _text(evidence.record_id)
        and evidence.record_id not in seen_ids
        and isinstance(evidence.binding, InventoryStepBinding),
        reason,
    )
    try:
        normalized = replace(evidence.binding, lanes=_lanes(evidence.binding.lanes))
    except ValueError as error:
        raise InventoryHold(reason) from error
    _require(normalized == expected, reason)
    seen_ids.add(evidence.record_id)


def _preserve_required_row(before, after) -> None:
    if before is None:
        protected = after["optional_skip_reason"] is None
    elif after is None:
        protected = not (
            before["mandatory"]
            or before["required_children"]
            or before["required_capabilities"]
        )
    else:
        protected = (
            (not before["mandatory"] or after["mandatory"])
            and set(before["required_children"]) <= set(after["required_children"])
            and set(before["required_capabilities"])
            <= set(after["required_capabilities"])
            and (
                after["optional_skip_reason"] is None
                or before["optional_skip_reason"] == after["optional_skip_reason"]
            )
            and (
                after["disposition"] == "collected"
                or before["disposition"] == "allowed_skip"
            )
        )
    _require(protected, "weakened_required_obligation")


def _apply_deltas(rows: dict, changes: list[dict], allow_policy_change: bool) -> None:
    for change in changes:
        before, after = change["before"], change["after"]
        key = _row_key(before if before is not None else after)
        _require(rows.get(key) == before, "delta_predecessor_mismatch")
        _preserve_required_row(before, after)
        if before is not None and after is not None and not allow_policy_change:
            _require(
                all(
                    before[field] == after[field]
                    for field in _ROW_FIELDS - {"disposition"}
                ),
                "unbound_obligation_policy_change",
            )
        if after is None:
            del rows[key]
        else:
            rows[key] = after


def applicable_inventory(
    reference: QualifiedReference,
    target: InventoryTarget,
    dispositions: tuple[InventoryStep, ...],
) -> Inventory:
    """Replay exact reviewed history over a qualified full collection.

    The caller verifies the independent anchor, protected-target path, and
    delivery and review evidence. This checks their exact binding and preserves
    original collection provenance. A hold returns no partial inventory.
    """
    _require(
        isinstance(reference, QualifiedReference)
        and isinstance(target, InventoryTarget)
        and isinstance(target.repository, str)
        and _REPOSITORY.fullmatch(target.repository)
        and _git_ref(target.target_ref)
        and target.target_ref.startswith("refs/heads/")
        and target.workload == "full",
        "invalid_inventory_target",
    )
    canonical_lanes = _inventory_lanes(target.lanes)
    _require(
        _inventory_lanes(reference.lanes) == canonical_lanes, "reference_lane_mismatch"
    )
    lanes = {(lane.profile, lane.platform_scope): lane for lane in canonical_lanes}
    _require(
        isinstance(target.path, tuple)
        and bool(target.path)
        and all(_valid_point(point) for point in target.path)
        and target.path[0] == reference.anchor
        and target.path[-1] == target.point
        and len({point.endpoint.commit for point in target.path}) == len(target.path)
        and len({len(point.endpoint.commit) for point in target.path}) == 1
        and isinstance(dispositions, tuple)
        and len(dispositions) == len(target.path) - 1,
        "unverified_history_path",
    )
    document, rows = _validate_reference(reference, target, lanes)
    required_helpers = _helper_sources(rows.values())
    history = []
    seen_evidence = set()
    for before, after, step in zip(
        target.path[:-1], target.path[1:], dispositions, strict=True
    ):
        _require(
            isinstance(step, InventoryStep)
            and step.before == before
            and step.after == after,
            "unexpected_history_step",
        )
        changes = _decode_deltas(step.deltas, lanes)
        binding = InventoryStepBinding(
            target.repository,
            target.target_ref,
            target.workload,
            canonical_lanes,
            before,
            after,
            _hash({"schema": "aitm.tia-inventory-delta/v1", "changes": changes}),
        )
        _match_step_evidence(
            step.delivery, binding, seen_evidence, "unverified_delivery"
        )
        policy_changed = (
            before.suite_policy_sha256 != after.suite_policy_sha256
            or before.ci103_policy_sha256 != after.ci103_policy_sha256
        )
        if changes or policy_changed or step.review is not None:
            _match_step_evidence(
                step.review, binding, seen_evidence, "unverified_inventory_review"
            )
        _apply_deltas(rows, changes, policy_changed)
        helper_sources = _helper_sources(rows.values())
        _require(required_helpers <= helper_sources, "missing_required_helper")
        _require(
            policy_changed or required_helpers == helper_sources,
            "unbound_helper_policy_change",
        )
        required_helpers = helper_sources
        _require(
            {_lane_key(row) for row in rows.values()} == lanes.keys(),
            "missing_required_lane",
        )
        _require(
            _hash(_ordered_rows(rows)) == after.obligations_sha256,
            "successor_row_digest_mismatch",
        )
        history.append(
            {
                "binding": binding,
                "changes": changes,
                "delivery_id": step.delivery.record_id,
                "review_id": step.review.record_id if step.review is not None else None,
            }
        )
    return _canonical(
        {
            "schema": "aitm.tia-applicable-inventory/v1",
            "reference": {
                "inventory": document,
                "raw_sha256": reference.expected_sha256,
                "receipt_id": reference.receipt_id,
            },
            "target": {
                "repository": target.repository,
                "target_ref": target.target_ref,
                "workload": target.workload,
                "lanes": canonical_lanes,
                "point": target.point,
            },
            "history": history,
            "obligations": _ordered_rows(rows),
        }
    )
