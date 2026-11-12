"""Exercise T10 through exact Git snapshots and independent evidence inputs."""

import json
from dataclasses import replace
from hashlib import sha256

import pytest
from test_tia_inventory import _collection, _project
from test_tia_snapshot import blob, commit, git, hosted_request, tree
from tia.controls import (
    ControlApprovals,
    ControlCandidate,
    ControlDecision,
    InventoryDelta,
    InventoryEvidence,
    InventoryHold,
    InventoryPoint,
    InventoryStep,
    InventoryStepBinding,
    InventoryTarget,
    Lane,
    QualifiedReference,
    Scope,
    applicable_inventory,
    qualify_controls,
)
from tia.snapshot import GitEndpoint, resolve
from verify_pr import gate_controls

_CONFIG_DIR = b"packages/aitm-usage/src/aitm_usage"
_PRODUCT = _CONFIG_DIR + b"/render.py"
_NESTED_CONTROL = _CONFIG_DIR + b"/conftest.py"
_TARGET = "refs/heads/trunk"


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "trunk")
    git(repo, "config", "user.name", "Fixture")
    git(repo, "config", "user.email", "fixture@example.test")
    return repo


def git_tree(repo, files):
    def entries(files):
        direct = []
        directories = {}
        for path, (mode, content) in files.items():
            name, slash, tail = path.partition(b"/")
            if slash:
                directories.setdefault(name, {})[tail] = (mode, content)
            else:
                direct.append((name, mode, "blob", blob(repo, content)))
        for name, children in directories.items():
            direct.append((name, "040000", "tree", entries(children)))
        return tree(repo, direct)

    return entries(files)


def full_lanes():
    runner = (("filesystem", "apfs"), ("name", "macos-26"), ("profile", "darwin-apfs"))
    capabilities = ("apfs", "darwin", "native-acl")
    return (
        Lane("ci-helpers", "ci-tools", "darwin-apfs", runner, capabilities),
        Lane("product-cli", "aitm-usage", "darwin-apfs", runner, capabilities),
    )


def control_pair(repo, before, after):
    base_tree = git_tree(repo, before)
    tested_tree = git_tree(repo, after)
    base = commit(repo, base_tree, message="trusted base")
    head = commit(repo, tested_tree, base, message="proposed head")
    tested = commit(repo, tested_tree, base, head, message="hosted merge")
    old, new = resolve(repo, hosted_request(base, tested, tested_tree, head))
    scope = Scope("full", full_lanes(), "1" * 64, "2" * 64)
    return old, ControlCandidate(new, _TARGET, 12, scope)


def approvals_for(binding):
    return ControlApprovals(
        ControlDecision("owner", "decision-1", binding),
        ControlDecision("reviewer", "review-1", binding),
    )


@pytest.mark.parametrize(
    "path",
    [
        b".github/workflows/ci.yml",
        b"tools/ci/policy.json",
        b"tools/ci/verify_pr.py",
        b"tools/ci/tia/selection.py",
        _NESTED_CONTROL,
    ],
)
def test_control_edit_requires_full_and_independent_disposition(repo, path):
    before = {_PRODUCT: ("100644", b"old"), path: ("100644", b"old rule")}
    ordinary = {**before, _PRODUCT: ("100644", b"new")}
    base, candidate = control_pair(repo, before, ordinary)
    result = qualify_controls(base, candidate, ControlApprovals())
    assert not result.full_required
    assert result.hold_reason is None
    assert result.changes == ()

    changed = {**before, path: ("100644", b"new rule")}
    base, candidate = control_pair(repo, before, changed)
    result = qualify_controls(base, candidate, ControlApprovals())
    assert result.full_required, "an exact gate-defining edit requires full validation"
    assert result.hold_reason == "missing_approval"
    assert (
        result.binding.base_controls_sha256 != result.binding.candidate_controls_sha256
    )
    assert result.changes[0].old.path == result.changes[0].new.path == path

    approvals = approvals_for(result.binding)
    for incomplete in (
        replace(approvals, owner=None),
        replace(approvals, reviewer=None),
    ):
        assert (
            qualify_controls(base, candidate, incomplete).hold_reason
            == "missing_approval"
        )
    qualified = qualify_controls(base, candidate, approvals)
    assert qualified.full_required and qualified.hold_reason is None
    assert qualified.approval_refs == ("decision-1", "review-1")
    assert (qualified.workflow_id, qualified.run_id, qualified.run_attempt) == (
        12,
        987,
        2,
    )


def test_control_changes_keep_raw_rename_and_mode_type_identity(repo):
    old_path, new_path = b"tools/ci/\xff.py", _CONFIG_DIR + b"/\xff.py"
    before = {
        old_path: ("100644", b"renamed"),
        b"tools/ci/old.py": ("100644", b"deleted"),
        b"tools/ci/mode.py": ("100644", b"executable"),
        b"tools/ci/link.py": ("100644", b"target.py"),
    }
    after = {
        new_path: ("100644", b"renamed"),
        b"tools/ci/new.py": ("100644", b"added"),
        b"tools/ci/mode.py": ("100755", b"executable"),
        b"tools/ci/link.py": ("120000", b"target.py"),
    }
    base, candidate = control_pair(repo, before, after)
    result = qualify_controls(base, candidate, ControlApprovals())
    observed = {(change.old or change.new).path: change for change in result.changes}
    assert set(observed) == {
        old_path,
        b"tools/ci/old.py",
        b"tools/ci/new.py",
        b"tools/ci/mode.py",
        b"tools/ci/link.py",
    }
    rename = observed[old_path]
    assert (rename.status, rename.old.path, rename.new.path) == (
        "R",
        old_path,
        new_path,
    )
    assert rename.old.object_id == rename.new.object_id
    assert observed[b"tools/ci/old.py"].new is None
    assert observed[b"tools/ci/new.py"].old is None
    assert observed[b"tools/ci/mode.py"].new.mode == "100755"
    assert observed[b"tools/ci/link.py"].status == "T"
    assert observed[b"tools/ci/link.py"].new.object_type == "blob"
    assert observed[b"tools/ci/link.py"].new.mode == "120000"

    expected_legacy = gate_controls(
        {
            path.decode("utf-8", "surrogateescape"): {
                "mode": mode,
                "type": "blob",
                "sha": blob(repo, content),
            }
            for path, (mode, content) in before.items()
        }
    )
    assert {path.encode("utf-8", "surrogateescape") for path in expected_legacy} <= set(
        observed
    )


def test_disposition_refuses_conflicting_or_replayed_exact_binding(repo):
    path = b"tools/ci/tia/suites.json"
    before = {path: ("100644", b'{"ignore":[]}'), _NESTED_CONTROL: ("100644", b"old")}
    after = {
        path: ("100644", b'{"ignore":["conftest.py"]}'),
        _NESTED_CONTROL: ("100644", b"new"),
    }
    base, candidate = control_pair(repo, before, after)
    result = qualify_controls(base, candidate, ControlApprovals())
    assert {change.new.path for change in result.changes} == {path, _NESTED_CONTROL}

    approved = approvals_for(result.binding)
    scope = result.binding.scope
    changed_lanes = (replace(scope.lanes[0], platform_scope="other"), scope.lanes[1])
    mismatches = {
        "repository": "other/project",
        "target_ref": "refs/heads/other",
        "source_ref": "refs/pull/99/merge",
        "base": GitEndpoint("4" * 40, "5" * 40),
        "tested": GitEndpoint(result.binding.tested.commit, "6" * 40),
        "pr_head": "7" * 40,
        "base_controls_sha256": "8" * 64,
        "candidate_controls_sha256": "9" * 64,
        "delta_sha256": "a" * 64,
        "scope": replace(scope, lanes=changed_lanes),
    }
    for field, wrong_value in mismatches.items():
        replay = replace(result.binding, **{field: wrong_value})
        attempted = replace(
            approved, reviewer=replace(approved.reviewer, binding=replay)
        )
        assert (
            qualify_controls(base, candidate, attempted).hold_reason
            == "approval_mismatch"
        ), field
    wrong_policy = replace(scope, ci103_policy_sha256="3" * 64)
    policy_candidate = replace(candidate, scope=wrong_policy)
    assert (
        qualify_controls(base, policy_candidate, approved).hold_reason
        == "approval_mismatch"
    )
    for attempted in (
        replace(
            approved, reviewer=replace(approved.reviewer, actor=approved.owner.actor)
        ),
        replace(
            approved,
            reviewer=replace(approved.reviewer, record_id=approved.owner.record_id),
        ),
    ):
        assert (
            qualify_controls(base, candidate, attempted).hold_reason
            == "approval_conflict"
        )

    assert (
        qualify_controls(replace(base, mode="local"), candidate, approved).hold_reason
        == "invalid_snapshot_pair"
    )
    assert (
        qualify_controls(replace(base, changes=()), candidate, approved).hold_reason
        == "invalid_snapshot_pair"
    )
    second_binding = replace(candidate.snapshot.provenance.binding, run_attempt=3)
    provenance = replace(candidate.snapshot.provenance, binding=second_binding)
    retry = replace(
        candidate, snapshot=replace(candidate.snapshot, provenance=provenance)
    )
    renewed = qualify_controls(replace(base, provenance=provenance), retry, approved)
    assert (
        renewed.full_required
        and renewed.hold_reason is None
        and renewed.run_attempt == 3
    )


def canonical(value):
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def row_key(row):
    return tuple(row[key] for key in ("provider", "owner", "platform_scope", "nodeid"))


def order_rows(rows):
    return sorted(rows, key=row_key)


def point_for(commit, tree, rows, suite_policy, ci_policy):
    return InventoryPoint(
        GitEndpoint(commit, tree),
        suite_policy,
        ci_policy,
        sha256(canonical(order_rows(rows))).hexdigest(),
    )


def delta_for(before, after):
    return InventoryDelta(
        canonical(before) if before is not None else None,
        canonical(after) if after is not None else None,
    )


def step_for(target, before, after, deltas, *, review):
    wire_changes = [
        {
            "before": json.loads(change.before) if change.before else None,
            "after": json.loads(change.after) if change.after else None,
        }
        for change in deltas
    ]
    digest = sha256(
        canonical({"schema": "aitm.tia-inventory-delta/v1", "changes": wire_changes})
    ).hexdigest()
    binding = InventoryStepBinding(
        target.repository,
        target.target_ref,
        target.workload,
        target.lanes,
        before,
        after,
        digest,
    )
    suffix = after.endpoint.commit[:4]
    return InventoryStep(
        before,
        after,
        tuple(deltas),
        InventoryEvidence("delivery-" + suffix, binding),
        InventoryEvidence("review-" + suffix, binding) if review else None,
    )


@pytest.fixture
def lineage():
    collection_binding = {
        "kind": "hosted_collection_proof",
        "repository": "kburson/aitm",
        "snapshot": {
            "commit": "a" * 40,
            "tree": "0" * 40,
            "ref": _TARGET,
            "run_id": 12,
            "run_attempt": 1,
        },
    }
    inventory = _project(
        _collection("product-cli", "ci-helpers", binding=collection_binding), "full"
    )
    document = json.loads(inventory)
    scopes = document["scopes"]
    owners = {"ci-helpers": "ci-tools", "product-cli": "aitm-usage"}
    lanes = tuple(
        Lane(
            scope["profile"],
            owners[scope["profile"]],
            scope["platform_scope"],
            tuple(sorted(scope["runner"].items())),
            tuple(scope["capabilities"]),
        )
        for scope in scopes
    )
    original = document["obligations"]
    suite_policy, ci_policy = (
        document["suite_policy_sha256"],
        document["ci103_policy_sha256"],
    )
    first = point_for("a" * 40, "0" * 40, original, suite_policy, ci_policy)
    unchanged = point_for("b" * 40, "1" * 40, original, suite_policy, ci_policy)
    ordinary = next(
        row
        for row in original
        if row["profile"] == "product-cli"
        and not row["mandatory"]
        and not row["required_capabilities"]
        and row["optional_skip_reason"] is None
    )
    added = {
        **ordinary,
        "nodeid": ordinary["nodeid"].partition("::")[0] + "::test_new_case",
    }
    resulting = order_rows([*original, added])
    final = point_for("c" * 40, "2" * 40, resulting, suite_policy, ci_policy)
    reference = QualifiedReference(
        inventory, sha256(inventory).hexdigest(), "collector-A", first, lanes
    )
    target = InventoryTarget(
        "kburson/aitm", _TARGET, "full", lanes, final, (first, unchanged, final)
    )
    steps = (
        step_for(target, first, unchanged, (), review=False),
        step_for(target, unchanged, final, (delta_for(None, added),), review=True),
    )
    return reference, target, steps, resulting


def test_reference_inventory_requires_intervening_dispositions(lineage):
    reference, target, steps, expected = lineage
    raw = applicable_inventory(reference, target, steps)
    result = json.loads(raw)
    assert result.get("schema") == "aitm.tia-applicable-inventory/v1"
    assert result["obligations"] == expected
    assert result["reference"] == {
        "inventory": json.loads(reference.inventory),
        "raw_sha256": reference.expected_sha256,
        "receipt_id": "collector-A",
    }
    assert result["target"]["point"]["endpoint"] == {
        "commit": "c" * 40,
        "tree": "2" * 40,
    }
    assert [entry["delivery_id"] for entry in result["history"]] == [
        "delivery-bbbb",
        "delivery-cccc",
    ]
    assert [entry["review_id"] for entry in result["history"]] == [None, "review-cccc"]
    assert canonical(result) == raw

    at_reference = replace(target, point=reference.anchor, path=(reference.anchor,))
    direct = json.loads(applicable_inventory(reference, at_reference, ()))
    assert direct["history"] == []
    assert direct["obligations"] == json.loads(reference.inventory)["obligations"]


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "extra",
        "reordered",
        "duplicate-point",
        "wrong-delivery",
        "missing-review",
        "same-evidence",
        "policy-drift",
        "wrong-before-row",
        "wrong-result-digest",
        "review-lane",
        "delivery-lane",
        "delivery-runner",
        "reference-lane",
        "anchor-lane",
        "net-zero",
        "different-target",
    ],
)
def test_inventory_holds_on_unverified_or_mismatched_replay(lineage, case):
    reference, target, steps, _ = lineage
    first, second = steps
    if case == "missing":
        steps = (second,)
    elif case == "extra":
        steps = (first, second, second)
    elif case == "reordered":
        steps = (second, first)
    elif case == "duplicate-point":
        target = replace(
            target, path=(reference.anchor, reference.anchor, target.point)
        )
    elif case == "wrong-delivery":
        steps = (replace(first, delivery=second.delivery), second)
    elif case == "missing-review":
        steps = (first, replace(second, review=None))
    elif case == "same-evidence":
        steps = (first, replace(second, review=second.delivery))
    elif case in {"policy-drift", "wrong-result-digest"}:
        field = (
            "suite_policy_sha256" if case == "policy-drift" else "obligations_sha256"
        )
        changed = replace(target.point, **{field: "9" * 64})
        target = replace(target, point=changed, path=(*target.path[:-1], changed))
        if case == "wrong-result-digest":
            steps = (
                first,
                step_for(target, second.before, changed, second.deltas, review=True),
            )
    elif case == "wrong-before-row":
        added = json.loads(second.deltas[0].after)
        wrong = (delta_for({**added, "suite": "system"}, added),)
        steps = (
            first,
            step_for(target, second.before, second.after, wrong, review=True),
        )
    elif case == "review-lane":
        review = replace(
            second.review,
            binding=replace(second.review.binding, lanes=(target.lanes[1],)),
        )
        steps = (first, replace(second, review=review))
    elif case in {"delivery-lane", "delivery-runner"}:
        wrong = (
            (target.lanes[1],)
            if case == "delivery-lane"
            else (
                replace(
                    target.lanes[0],
                    runner=(("name", "other"), ("profile", "darwin-apfs")),
                ),
                target.lanes[1],
            )
        )
        delivery = replace(
            first.delivery, binding=replace(first.delivery.binding, lanes=wrong)
        )
        steps = (replace(first, delivery=delivery), second)
    elif case == "reference-lane":
        document = json.loads(reference.inventory)
        document["scopes"].pop(0)
        raw = canonical(document)
        reference = replace(
            reference, inventory=raw, expected_sha256=sha256(raw).hexdigest()
        )
    elif case == "anchor-lane":
        reference = replace(reference, lanes=(reference.lanes[1],))
    elif case == "net-zero":
        final = replace(
            target.point, obligations_sha256=reference.anchor.obligations_sha256
        )
        target = replace(target, point=final, path=(*target.path[:-1], final))
        steps = (step_for(target, reference.anchor, final, (), review=False),)
    elif case == "different-target":
        target = replace(target, repository="other/project")

    with pytest.raises(InventoryHold):
        applicable_inventory(reference, target, steps)


@pytest.mark.parametrize("kind", ["local", "partial", "derived", "wrong-hash"])
def test_inventory_requires_qualified_hosted_full_reference(lineage, kind):
    reference, target, steps, _ = lineage
    document = json.loads(reference.inventory)
    if kind == "local":
        document["binding"]["kind"] = "local_advisory"
    elif kind == "partial":
        document["scope_status"] = "comparison_component"
    elif kind == "derived":
        document["schema"] = "aitm.tia-applicable-inventory/v1"
    raw = canonical(document)
    digest = "9" * 64 if kind == "wrong-hash" else sha256(raw).hexdigest()
    with pytest.raises(InventoryHold):
        applicable_inventory(
            replace(reference, inventory=raw, expected_sha256=digest), target, steps
        )


@pytest.mark.parametrize(
    "change",
    [
        "mandatory",
        "child",
        "capability",
        "helper",
        "skip-permission",
        "allowed-skip",
        "unexpected-xfail",
        "deselected",
        "wrong-owner",
        "wrong-key",
    ],
)
def test_even_reviewed_delta_cannot_weaken_required_inventory(lineage, change):
    reference, target, steps, _ = lineage
    rows = json.loads(reference.inventory)["obligations"]
    old = next(row for row in rows if row["mandatory"])
    if change == "child":
        old = next(row for row in rows if row["required_children"])
        new = {**old, "required_children": []}
    elif change == "capability":
        old = next(row for row in rows if row["required_capabilities"])
        new = {**old, "required_capabilities": []}
    elif change == "helper":
        old = next(row for row in rows if row["profile"] == "ci-helpers")
        new = None
    elif change == "mandatory":
        new = None
    elif change == "skip-permission":
        new = {**old, "optional_skip_reason": "new reason"}
    elif change == "allowed-skip":
        old = next(row for row in rows if row["optional_skip_reason"] is not None)
        new = {**old, "disposition": "allowed_skip"}
    elif change in {"unexpected-xfail", "deselected"}:
        new = {**old, "disposition": change}
    elif change == "wrong-owner":
        new = {**old, "owner": "ci-tools"}
    else:
        new = {**old, "nodeid": "../escape.py::test_bad"}

    remaining = [row for row in rows if row != old]
    if new is not None:
        remaining.append(new)
    final = point_for(
        "c" * 40,
        "2" * 40,
        remaining,
        target.point.suite_policy_sha256,
        target.point.ci103_policy_sha256,
    )
    target = replace(target, point=final, path=(*target.path[:-1], final))
    changed = step_for(
        target, steps[1].before, final, (delta_for(old, new),), review=True
    )
    with pytest.raises(InventoryHold):
        applicable_inventory(reference, target, (steps[0], changed))


def test_control_qualification_refuses_inexact_change_endpoint_and_target(repo):
    before = {_NESTED_CONTROL: ("100644", b"old")}
    after = {_NESTED_CONTROL: ("100644", b"new")}
    base, candidate = control_pair(repo, before, after)
    change = base.changes[0]
    forged = replace(change, new=replace(change.new, content_id="7" * 40))
    wrong_base = replace(base, changes=(forged,))
    wrong_candidate = replace(
        candidate, snapshot=replace(candidate.snapshot, changes=(forged,))
    )
    result = qualify_controls(wrong_base, wrong_candidate, ControlApprovals())
    assert result.hold_reason == "invalid_snapshot_pair"

    malformed = replace(candidate, target_ref="refs/heads/trunk..")
    result = qualify_controls(base, malformed, ControlApprovals())
    assert result.hold_reason == "invalid_snapshot_pair"


def test_control_approval_compares_canonical_lane_sets(repo):
    before = {_NESTED_CONTROL: ("100644", b"old")}
    after = {_NESTED_CONTROL: ("100644", b"new")}
    base, candidate = control_pair(repo, before, after)
    result = qualify_controls(base, candidate, ControlApprovals())
    scope = result.binding.scope
    reordered = replace(scope, lanes=tuple(reversed(scope.lanes)))
    approved = approvals_for(replace(result.binding, scope=reordered))
    qualified = qualify_controls(base, candidate, approved)
    assert qualified.full_required
    assert qualified.hold_reason is None
