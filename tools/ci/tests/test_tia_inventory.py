import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import pytest
from tia.inventory import SuitePolicy, classify

_CI = Path(__file__).resolve().parents[1]
_SUITES = _CI / "tia" / "suites.json"
_CI103 = _CI / "policy.json"
_PRODUCT = "packages/aitm-usage/tests/"
_HELPERS = [
    "tools/ci/tests/test_file_checks.py",
    "tools/ci/tests/test_pytest_evidence.py",
    "tools/ci/tests/test_python_gate.py",
    "tools/ci/tests/test_verify_pr.py",
]
_CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
_ACL = _PRODUCT + "test_install.py::test_backup_and_restore_reject_inherited_acl"
_OPTIONAL = (
    _PRODUCT + "test_install.py::test_backup_refuses_store_through_physical_path_alias"
)
_SKIP_REASON = "The host does not expose the matching APFS firmlink path"
_ONE_SHOT = (
    _PRODUCT + "test_service.py::test_one_shot_status_uses_collecting_subprocess_pid"
)
_SERVICE = (
    _PRODUCT
    + "test_service_process.py::test_real_service_crash_enrollment_and_private_state"
)
_REQUIRED = {
    _ACL,
    _ONE_SHOT,
    _SERVICE,
    _PRODUCT + "test_install.py::test_restore_fences_publication_until_atomic_swap",
    _PRODUCT + "test_ledger.py::test_atomic_cursor_and_revisions",
    _PRODUCT
    + "test_ledger.py::test_writer_refusal_read_snapshot_and_release_on_process_exit",
}
_FIRMLINKS = {
    _OPTIONAL,
    _PRODUCT
    + "test_ledger.py::test_apfs_firmlink_overlap_refused_before_private_creation",
    _PRODUCT + "test_ledger.py::test_distinct_apfs_alias_cannot_admit_a_second_writer",
}
_PRICING = _PRODUCT + "test_grok_pricing.py::"
_UNIT = {
    _PRICING + "test_grok_rate_classes_do_not_use_claude_defaults",
    _PRICING + "test_unknown_grok_rate_and_provider_ticks_remain_separate",
    _PRICING + "test_grok_card_rejects_unproven_rate_classes_and_models",
    _PRICING + "test_legacy_v1_revision_refuses_grok_provider",
}
_FIXED_EXPORT = _PRICING + "test_grok_preserves_legacy_rate_digest_and_fixed_export"
_PRODUCT_IDS = sorted(_REQUIRED | _FIRMLINKS | _UNIT | {_FIXED_EXPORT})
_LOCAL = {
    "kind": "local_advisory",
    "repository": "kburson/aitm",
    "snapshot": {"content_digest": "a" * 64},
}
_HOSTED = {
    "kind": "hosted_collection_proof",
    "repository": "kburson/aitm",
    "snapshot": {
        "commit": "b" * 40,
        "tree": "c" * 40,
        "ref": "refs/pull/139/merge",
        "run_id": 42,
        "run_attempt": 2,
    },
}
_REPLAY = {
    "kind": "ci103_historical_replay",
    "tree": "e" * 40,
    "receipt_sha256": "f" * 64,
    "run_id": 17,
    "run_attempt": 1,
    "role": "pr_candidate",
}


def _encode(value):
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _scope(profile, binding):
    nodes = {
        "product-base": _PRODUCT_IDS,
        "product-cli": [*_PRODUCT_IDS, _CLI],
        "ci-helpers": [path + "::test_fixture" for path in _HELPERS],
    }[profile]
    return {
        "profile": profile,
        "platform_scope": "darwin-apfs",
        "binding": deepcopy(binding),
        "runner": {
            "profile": "darwin-apfs",
            "name": "macos-26",
            "os": "Darwin",
            "filesystem": "apfs",
            "image": "macos26:fixture",
        },
        "capabilities": ["native-acl", "darwin", "apfs"],
        "observer": "2" * 64,
        "controls": {"workflow": "3" * 40, "lock": "4" * 64},
        "receipt_sha256": {"product-base": "5", "product-cli": "6", "ci-helpers": "7"}[
            profile
        ]
        * 64,
        "exit_code": 0,
        "complete": True,
        "deselected": [],
        "items": [{"nodeid": node, "disposition": "collected"} for node in nodes],
    }


def _collection(*profiles, binding=_LOCAL):
    return {
        "schema": "aitm.tia-collection/v1",
        "binding": deepcopy(binding),
        "scopes": [_scope(profile, binding) for profile in profiles],
    }


def _project(collection, workload, *, suites=None, ci103=None):
    policy = SuitePolicy(
        suites=_SUITES.read_bytes() if suites is None else _encode(suites),
        ci103=_CI103.read_bytes() if ci103 is None else _encode(ci103),
        workload=workload,
    )
    raw = collection if isinstance(collection, bytes) else _encode(collection)
    return classify(raw, policy)


def test_classification_preserves_parametrized_platform_ids():
    policy = json.loads(_SUITES.read_bytes())
    runner = deepcopy(policy["runners"]["darwin-apfs"])
    runner["platform_scope"] = "darwin-apfs-secondary"
    policy["runners"]["secondary"] = runner
    policy["workloads"]["compare-product-cli"]["required_pairs"].append(
        ["product-cli", "darwin-apfs-secondary"]
    )

    collection = _collection("product-cli", "product-cli")
    primary, secondary = collection["scopes"]
    secondary["platform_scope"] = "darwin-apfs-secondary"
    secondary["runner"]["profile"] = "secondary"
    prefix = _PRODUCT + "test_service.py::TestPlatform::test_example"
    first = prefix + "[Linux/a::b[é]]"
    second = prefix + "[FreeBSD/x[y]::z]"
    primary["items"].extend(
        {"nodeid": node, "disposition": "collected"} for node in (first, second)
    )
    secondary["items"].append({"nodeid": first, "disposition": "collected"})

    raw = _project(collection, "compare-product-cli", suites=policy)
    inventory = json.loads(raw)
    assert raw == _encode(inventory)
    assert b"\xc3\xa9" in raw
    obligations = inventory["obligations"]
    keys = [
        tuple(row[key] for key in ("provider", "owner", "platform_scope", "nodeid"))
        for row in obligations
    ]
    assert keys == sorted(set(keys))
    assert [(row[2], row[3]) for row in keys if row[3].startswith(prefix)] == [
        ("darwin-apfs", second),
        ("darwin-apfs", first),
        ("darwin-apfs-secondary", first),
    ]
    by_id = {
        row["nodeid"]: row
        for row in obligations
        if row["platform_scope"] == "darwin-apfs"
    }
    assert by_id[_ACL]["required_capabilities"] == ["native-acl"]
    assert by_id[_ONE_SHOT]["isolation_group"] == "system-process"
    assert by_id[first]["isolation_group"] == "native-process-state"
    for node in _FIRMLINKS:
        assert by_id[node]["required_capabilities"] == ["apfs"]

    collection["scopes"].reverse()
    for scope in collection["scopes"]:
        scope["items"].reverse()
        scope["capabilities"].reverse()
    assert _project(collection, "compare-product-cli", suites=policy) == raw
    primary["receipt_sha256"] = "8" * 64
    changed = _project(collection, "compare-product-cli", suites=policy)
    assert sha256(changed).digest() != sha256(raw).digest()


@pytest.mark.parametrize(
    ("case", "category"),
    [
        ("unknown-module", "collection"),
        ("duplicate-node", "collection"),
        ("repeated-scope", "scope"),
        ("missing-scope", "scope"),
        ("extra-scope", "scope"),
        ("missing-apfs", "capability"),
        ("missing-native-acl", "capability"),
        ("inconsistent-runner", "capability"),
        ("missing-mandatory", "collection"),
        ("unsafe-path", "collection"),
        ("duplicate-override", "policy"),
        ("outside-module-override", "policy"),
        ("duplicate-policy-pair", "policy"),
        ("duplicate-json-key", "malformed input"),
        ("nonfinite-json", "malformed input"),
        ("nonzero-exit", "collection"),
        ("incomplete", "collection"),
        ("deselected", "collection"),
        ("unexpected-skip", "collection"),
        ("unexpected-xfail", "collection"),
        ("wrong-skip-reason", "collection"),
        ("unexpected-child", "policy"),
        ("unknown-capability", "policy"),
    ],
)
def test_unclassified_or_duplicate_fails(case, category):
    collection = _collection("product-cli")
    scope = collection["scopes"][0]
    items = scope["items"]
    suites = json.loads(_SUITES.read_bytes())
    ci103 = json.loads(_CI103.read_bytes())
    if case == "unknown-module":
        items[0]["nodeid"] = _PRODUCT + "test_unreviewed.py::test_fixture"
    elif case == "duplicate-node":
        items.append(deepcopy(items[0]))
    elif case == "repeated-scope":
        collection["scopes"].append(deepcopy(scope))
    elif case == "missing-scope":
        collection["scopes"].clear()
    elif case == "extra-scope":
        collection["scopes"].append(_scope("ci-helpers", _LOCAL))
    elif case == "missing-apfs":
        scope["capabilities"].remove("apfs")
    elif case == "missing-native-acl":
        scope["capabilities"].remove("native-acl")
    elif case == "inconsistent-runner":
        scope["runner"]["filesystem"] = "ext4"
    elif case == "missing-mandatory":
        items.remove(next(row for row in items if row["nodeid"] == _ACL))
    elif case == "unsafe-path":
        items[0]["nodeid"] = _PRODUCT + "sub/../test_service.py::test_fixture"
    elif case == "duplicate-override":
        suites["overrides"].append(suites["overrides"][0])
    elif case == "outside-module-override":
        suites["overrides"][0]["selector"] = (
            _PRODUCT + "test_unreviewed.py::test_fixture"
        )
    elif case == "duplicate-policy-pair":
        suites["workloads"]["full"]["required_pairs"].append(
            ["product-cli", "darwin-apfs"]
        )
    elif case == "duplicate-json-key":
        collection = _encode(collection).replace(
            b'{"binding":', b'{"schema":"x","binding":', 1
        )
    elif case == "nonfinite-json":
        collection = _encode(collection).replace(b'"exit_code":0', b'"exit_code":1e999')
    elif case == "nonzero-exit":
        scope["exit_code"] = 5
    elif case == "incomplete":
        scope["complete"] = False
    elif case == "deselected":
        scope["deselected"] = [_OPTIONAL]
    elif case == "unexpected-skip":
        items[0].update(disposition="allowed_skip", reason=_SKIP_REASON)
    elif case == "unexpected-xfail":
        items[0]["disposition"] = "xfail"
    elif case == "wrong-skip-reason":
        next(row for row in items if row["nodeid"] == _OPTIONAL).update(
            disposition="allowed_skip", reason="wrong reason"
        )
    elif case == "unexpected-child":
        ci103["required_children"].append("unmapped")
    elif case == "unknown-capability":
        suites["overrides"][0]["required_capabilities"] = ["not-declared"]
    with pytest.raises(ValueError, match=f"^{category}:"):
        _project(
            collection,
            "compare-product-cli",
            suites=suites,
            ci103=ci103,
        )


def test_ci103_scope_and_child_mapping():
    collection = _collection("product-cli")
    next(
        row for row in collection["scopes"][0]["items"] if row["nodeid"] == _OPTIONAL
    ).update(disposition="allowed_skip", reason=_SKIP_REASON)
    product = json.loads(_project(collection, "compare-product-cli"))
    rows = {row["nodeid"]: row for row in product["obligations"]}
    assert {node for node, row in rows.items() if row["mandatory"]} == _REQUIRED | {
        _CLI
    }
    assert {
        node: row["required_children"]
        for node, row in rows.items()
        if row["required_children"]
    } == {_CLI: ["cli-help"], _ONE_SHOT: ["service-one-shot"]}
    assert rows[_OPTIONAL]["optional_skip_reason"] == _SKIP_REASON
    assert rows[_OPTIONAL]["disposition"] == "allowed_skip"
    assert rows[_CLI]["owner"] == "aitm-usage"
    assert {node for node, row in rows.items() if row["suite"] == "system"} == {
        _CLI,
        _ONE_SHOT,
        _SERVICE,
    }
    assert {rows[node]["isolation_group"] for node in (_CLI, _ONE_SHOT, _SERVICE)} == {
        "system-process"
    }
    assert {node for node, row in rows.items() if row["suite"] == "unit"} == _UNIT
    assert rows[_FIXED_EXPORT]["suite"] == "integration"
    assert rows[_FIXED_EXPORT]["isolation_group"] != rows[min(_UNIT)]["isolation_group"]

    base = json.loads(_project(_collection("product-base"), "compare-product-base"))
    assert {
        row["nodeid"] for row in base["obligations"] if row["mandatory"]
    } == _REQUIRED
    assert all(row["owner"] == "aitm-usage" for row in base["obligations"])
    assert all(not row["required_children"] for row in base["obligations"])
    assert _CLI not in {row["nodeid"] for row in base["obligations"]}

    helpers = _collection("ci-helpers")
    projected = json.loads(_project(helpers, "compare-ci-helpers"))
    assert {
        row["nodeid"].partition("::")[0] for row in projected["obligations"]
    } == set(_HELPERS)
    assert {row["owner"] for row in projected["obligations"]} == {"ci-tools"}
    assert {row["isolation_group"] for row in projected["obligations"]} == {
        "ci-helper-serial"
    }
    helpers["scopes"][0]["items"].pop()
    with pytest.raises(ValueError, match="^collection:"):
        _project(helpers, "compare-ci-helpers")

    collection["scopes"][0]["items"].pop()
    with pytest.raises(ValueError, match="^collection:"):
        _project(collection, "compare-product-cli")


def test_full_inventory_requires_all_policy_pairs():
    collection = _collection("ci-helpers", "product-cli", binding=_HOSTED)
    inventory = json.loads(_project(collection, "full"))
    assert inventory["scope_status"] == "complete_workload"
    assert [scope["profile"] for scope in inventory["scopes"]] == [
        "ci-helpers",
        "product-cli",
    ]
    assert {row["nodeid"] for row in inventory["obligations"]} == {
        *_PRODUCT_IDS,
        _CLI,
        *(path + "::test_fixture" for path in _HELPERS),
    }

    for profile in ("product-base", "product-cli", "ci-helpers"):
        component = _collection(profile)
        projected = json.loads(_project(component, "compare-" + profile))
        assert projected["scope_status"] == "comparison_component"
        with pytest.raises(ValueError, match="^scope:"):
            _project(component, "full")

    helper = collection["scopes"][0]
    for change in ({"tree": "d" * 40}, {"run_attempt": 3}):
        helper["binding"]["snapshot"].update(change)
        with pytest.raises(ValueError, match="^scope:"):
            _project(collection, "full")
        helper["binding"] = deepcopy(_HOSTED)
    helper["binding"] = deepcopy(_LOCAL)
    with pytest.raises(ValueError, match="^scope:"):
        _project(collection, "full")
    helper["binding"] = deepcopy(_HOSTED)
    helper["source_reference"] = deepcopy(_REPLAY)
    with pytest.raises(ValueError, match="^scope:"):
        _project(collection, "full")
    helper["binding"] = deepcopy(_LOCAL)
    collection["binding"] = deepcopy(_LOCAL)
    collection["scopes"][1]["binding"] = deepcopy(_LOCAL)
    with pytest.raises(ValueError, match="^scope:"):
        _project(collection, "full")


def test_hosted_and_advisory_preserve_distinct_provenance():
    local = _collection("product-cli")
    local["scopes"][0]["source_reference"] = deepcopy(_REPLAY)
    hosted = _collection("product-cli", binding=_HOSTED)
    advisory_raw = _project(local, "compare-product-cli")
    hosted_raw = _project(hosted, "compare-product-cli")
    advisory, proof = map(json.loads, (advisory_raw, hosted_raw))
    assert advisory["obligations"] == proof["obligations"]
    assert sha256(advisory_raw).digest() != sha256(hosted_raw).digest()
    assert advisory["binding"] == _LOCAL
    assert advisory["scopes"][0]["source_reference"] == _REPLAY
    assert proof["binding"] == _HOSTED
    scope = hosted["scopes"][0]
    assert proof["scopes"] == [
        {
            "profile": scope["profile"],
            "platform_scope": scope["platform_scope"],
            "runner": scope["runner"],
            "capabilities": sorted(scope["capabilities"]),
            "observer": scope["observer"],
            "controls": scope["controls"],
            "receipt_sha256": scope["receipt_sha256"],
        }
    ]
    assert proof["suite_policy_sha256"] == sha256(_SUITES.read_bytes()).hexdigest()
    assert proof["ci103_policy_sha256"] == sha256(_CI103.read_bytes()).hexdigest()

    for change in (
        {"kind": "unknown"},
        {"snapshot": _LOCAL["snapshot"]},
        {"snapshot": {"commit": "b" * 40}},
    ):
        invalid = deepcopy(hosted)
        invalid["binding"].update(change)
        with pytest.raises(ValueError, match="^malformed input:"):
            _project(invalid, "compare-product-cli")
    scope["binding"] = deepcopy(_LOCAL)
    with pytest.raises(ValueError, match="^scope:"):
        _project(hosted, "compare-product-cli")


@pytest.mark.parametrize(
    "nodeid",
    [
        _PRODUCT
        + "test_scope_admission.py::test_scope_cli_refuses_uninitialized_admission_without_creating_state",
        _PRODUCT
        + "test_scope_legacy.py::test_adopted_replay_keeps_the_pending_legacy_receipt_without_monitor_state",
    ],
)
def test_refreshed_scope_modules_share_native_process_isolation(nodeid):
    collection = _collection("product-cli")
    collection["scopes"][0]["items"].append(
        {"nodeid": nodeid, "disposition": "collected"}
    )
    inventory = json.loads(_project(collection, "compare-product-cli"))
    row = next(row for row in inventory["obligations"] if row["nodeid"] == nodeid)
    assert (row["owner"], row["suite"], row["isolation_group"]) == (
        "aitm-usage",
        "integration",
        "native-process-state",
    )
