"""Exercise T10 through exact Git snapshots and independent evidence inputs."""

import json
from dataclasses import replace
from hashlib import sha256

import pytest
from test_tia_inventory import _CI103, _SUITES, _collection, _project
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
from tia.inventory import SuitePolicy
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
    runner = (
        ("filesystem", "apfs"),
        ("name", "macos-26"),
        ("os", "Darwin"),
        ("profile", "darwin-apfs"),
    )
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
    policy = SuitePolicy(_SUITES.read_bytes(), _CI103.read_bytes(), "full")
    scope = Scope(
        "full",
        full_lanes(),
        sha256(policy.suites).hexdigest(),
        sha256(policy.ci103).hexdigest(),
    )
    return old, ControlCandidate(new, _TARGET, 12, scope, policy)


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
    stale = replace(
        approved,
        reviewer=replace(
            approved.reviewer, binding=replace(result.binding, scope=wrong_policy)
        ),
    )
    assert qualify_controls(base, candidate, stale).hold_reason == "approval_mismatch"
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
    collection = _collection("product-cli", "ci-helpers", binding=collection_binding)
    inventory = _project(collection, "full")
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
    nodeid = ordinary["nodeid"].partition("::")[0] + "::test_new_case"
    product_scope = next(
        scope for scope in collection["scopes"] if scope["profile"] == "product-cli"
    )
    product_scope["items"].append({"nodeid": nodeid, "disposition": "collected"})
    resulting = json.loads(_project(collection, "full"))["obligations"]
    added = next(row for row in resulting if row["nodeid"] == nodeid)
    final = point_for("c" * 40, "2" * 40, resulting, suite_policy, ci_policy)
    reference = QualifiedReference(
        inventory, sha256(inventory).hexdigest(), "collector-A", first, lanes
    )
    target = InventoryTarget(
        "kburson/aitm",
        _TARGET,
        "full",
        lanes,
        final,
        (first, unchanged, final),
        (SuitePolicy(_SUITES.read_bytes(), _CI103.read_bytes(), "full"),),
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


@pytest.mark.parametrize("gap", ["missing-helper", "wrong-platform", "wrong-owner"])
def test_exact_approvals_cannot_clear_invalid_full_control_scope(repo, gap):
    base, candidate = control_pair(
        repo,
        {_NESTED_CONTROL: ("100644", b"old")},
        {_NESTED_CONTROL: ("100644", b"new")},
    )
    scope = candidate.scope
    helper, product = scope.lanes
    if gap == "missing-helper":
        wrong = (product,)
    elif gap == "wrong-platform":
        wrong = (replace(helper, platform_scope="elsewhere"), product)
    else:
        wrong = (replace(helper, owner="other"), product)
    proposal = qualify_controls(base, candidate, ControlApprovals())
    wrong_scope = replace(scope, lanes=wrong)
    wrong_binding = replace(proposal.binding, scope=wrong_scope)
    result = qualify_controls(
        base, replace(candidate, scope=wrong_scope), approvals_for(wrong_binding)
    )
    assert result.full_required
    assert result.hold_reason == "invalid_scope"
    assert result.approval_refs == ()


@pytest.mark.parametrize(
    ("field", "bad_value"),
    [
        ("observer", None),
        ("observer", "a" * 40),
        ("receipt_sha256", None),
        ("receipt_sha256", "a" * 40),
        ("controls", None),
        ("controls", {}),
        ("controls", {"": "b" * 40}),
        ("controls", {"workflow": "not-an-object-id"}),
    ],
)
def test_inventory_refuses_malformed_scope_provenance_with_exact_hash(
    lineage, field, bad_value
):
    reference, target, steps, _ = lineage
    document = json.loads(reference.inventory)
    document["scopes"][0][field] = bad_value
    raw = canonical(document)
    reference = replace(
        reference, inventory=raw, expected_sha256=sha256(raw).hexdigest()
    )
    with pytest.raises(InventoryHold, match="reference_scope_provenance"):
        applicable_inventory(reference, target, steps)


def test_control_qualification_requires_the_reviewed_policy_bytes(repo):
    base, candidate = control_pair(
        repo,
        {_NESTED_CONTROL: ("100644", b"old")},
        {_NESTED_CONTROL: ("100644", b"new")},
    )
    binding = qualify_controls(base, candidate, ControlApprovals()).binding
    approval = approvals_for(binding)
    proof = candidate.suite_policy
    for invalid in (None, replace(proof, suites=proof.suites + b"\n")):
        result = qualify_controls(
            base, replace(candidate, suite_policy=invalid), approval
        )
        assert result.full_required and result.hold_reason == "invalid_scope"
        assert result.approval_refs == ()


def test_named_comparison_scope_keeps_control_changes_full(repo):
    base, candidate = control_pair(
        repo,
        {_NESTED_CONTROL: ("100644", b"old")},
        {_NESTED_CONTROL: ("100644", b"new")},
    )
    scope = candidate.scope
    name = "compare-product-cli"
    comparison = replace(
        candidate,
        scope=replace(scope, workload=name, lanes=(scope.lanes[1],)),
        suite_policy=replace(candidate.suite_policy, workload=name),
    )
    proposed = qualify_controls(base, comparison, ControlApprovals())
    assert proposed.full_required and proposed.hold_reason == "missing_approval"
    approvals = approvals_for(proposed.binding)
    qualified = qualify_controls(base, comparison, approvals)
    assert qualified.full_required and qualified.hold_reason is None
    assert qualified.binding.scope.workload == name
    assert (
        qualify_controls(base, candidate, approvals).hold_reason == "approval_mismatch"
    )


def test_full_control_scope_checks_every_reviewed_profile_platform_pair(repo):
    base, candidate = control_pair(
        repo,
        {_NESTED_CONTROL: ("100644", b"old")},
        {_NESTED_CONTROL: ("100644", b"new")},
    )
    document = json.loads(candidate.suite_policy.suites)
    secondary = "darwin-apfs-secondary"
    document["runners"][secondary] = {
        **document["runners"]["darwin-apfs"],
        "platform_scope": secondary,
    }
    document["workloads"]["full"]["required_pairs"].append(["product-cli", secondary])
    raw = canonical(document)
    scope = replace(candidate.scope, suite_policy_sha256=sha256(raw).hexdigest())
    proof = replace(candidate.suite_policy, suites=raw)
    candidate = replace(candidate, scope=scope, suite_policy=proof)
    incomplete = qualify_controls(base, candidate, ControlApprovals())
    assert incomplete.full_required and incomplete.hold_reason == "invalid_scope"

    product = scope.lanes[1]
    second = replace(
        product,
        platform_scope=secondary,
        runner=tuple(
            (key, secondary if key == "profile" else value)
            for key, value in product.runner
        ),
    )
    complete = replace(candidate, scope=replace(scope, lanes=(*scope.lanes, second)))
    disposition = qualify_controls(base, complete, ControlApprovals())
    assert disposition.full_required and disposition.hold_reason == "missing_approval"
    qualified = qualify_controls(base, complete, approvals_for(disposition.binding))
    assert qualified.full_required and qualified.hold_reason is None


@pytest.mark.parametrize("kind", ["unregistered-module", "suite", "isolation-group"])
def test_reviewed_addition_must_match_successor_policy(lineage, kind):
    reference, target, steps, rows = lineage
    step = steps[1]
    original = json.loads(step.deltas[0].after)
    if kind == "unregistered-module":
        forged = {
            **original,
            "nodeid": "packages/aitm-usage/tests/test_unregistered.py::test_new_case",
        }
    elif kind == "suite":
        wrong_suite = "unit" if original["suite"] != "unit" else "system"
        forged = {**original, "suite": wrong_suite}
    else:
        forged = {**original, "isolation_group": "unapproved-group"}
    successor = replace(
        step.after,
        obligations_sha256=sha256(
            canonical(order_rows([row for row in rows if row != original] + [forged]))
        ).hexdigest(),
    )
    target = replace(target, point=successor, path=(*target.path[:-1], successor))
    reviewed = step_for(
        target, step.before, successor, (delta_for(None, forged),), review=True
    )
    with pytest.raises(InventoryHold, match="policy_obligation_mismatch"):
        applicable_inventory(reference, target, (steps[0], reviewed))


def test_anchor_requires_every_policy_helper_target_even_without_replay(lineage):
    reference, target, _, _ = lineage
    document = json.loads(reference.inventory)
    missing = next(
        row for row in document["obligations"] if row["profile"] == "ci-helpers"
    )
    document["obligations"].remove(missing)
    raw = canonical(document)
    anchor = replace(
        reference.anchor,
        obligations_sha256=sha256(canonical(document["obligations"])).hexdigest(),
    )
    reference = replace(
        reference, inventory=raw, expected_sha256=sha256(raw).hexdigest(), anchor=anchor
    )
    target = replace(target, point=anchor, path=(anchor,))
    with pytest.raises(InventoryHold, match="policy_obligation_mismatch"):
        applicable_inventory(reference, target, ())


@pytest.mark.parametrize("policy_gap", ["absent", "wrong-bytes", "wrong-workload"])
def test_replay_holds_when_exact_point_policy_is_unavailable(lineage, policy_gap):
    reference, target, steps, _ = lineage
    policy = target.policies[0]
    if policy_gap == "absent":
        policies = ()
    elif policy_gap == "wrong-bytes":
        policies = (replace(policy, ci103=policy.ci103 + b"\n"),)
    else:
        policies = (replace(policy, workload="compare-product-cli"),)
    with pytest.raises(InventoryHold, match="unbound_replay_policy"):
        applicable_inventory(reference, replace(target, policies=policies), steps)


def test_successor_reconciles_policy_metadata_at_each_reviewed_revision(lineage):
    reference, target, steps, _ = lineage
    policy = target.policies[0]
    reference_document = json.loads(reference.inventory)
    original = reference_document["obligations"]
    before = next(
        row
        for row in original
        if row["profile"] == "product-cli" and not row["mandatory"]
    )
    policy_document = json.loads(policy.suites)
    override = next(
        (
            row
            for row in policy_document["overrides"]
            if row["selector"] == before["nodeid"]
        ),
        None,
    )
    if override is None:
        override = {"selector": before["nodeid"]}
        policy_document["overrides"].append(override)
    override["isolation_group"] = "reviewed-replacement"
    raw = canonical(policy_document)
    successor_policy = replace(policy, suites=raw)
    projected = json.loads(
        _project(
            _collection(
                "product-cli", "ci-helpers", binding=reference_document["binding"]
            ),
            "full",
            suites=policy_document,
        )
    )
    after = next(
        row for row in projected["obligations"] if row_key(row) == row_key(before)
    )
    assert after["isolation_group"] == "reviewed-replacement"
    target = replace(target, policies=(policy, successor_policy))
    for candidate_row, accepted in (
        (after, True),
        ({**after, "isolation_group": "forged"}, False),
    ):
        rows = order_rows(
            [row for row in original if row_key(row) != row_key(before)]
            + [candidate_row]
        )
        point = replace(
            target.point,
            suite_policy_sha256=sha256(raw).hexdigest(),
            obligations_sha256=sha256(canonical(rows)).hexdigest(),
        )
        candidate = replace(target, point=point, path=(*target.path[:-1], point))
        reviewed = step_for(
            candidate,
            steps[1].before,
            point,
            (delta_for(before, candidate_row),),
            review=True,
        )
        if accepted:
            result = json.loads(
                applicable_inventory(reference, candidate, (steps[0], reviewed))
            )
            assert result["obligations"] == projected["obligations"]
        else:
            with pytest.raises(InventoryHold, match="policy_obligation_mismatch"):
                applicable_inventory(reference, candidate, (steps[0], reviewed))
