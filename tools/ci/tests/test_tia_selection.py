import json
import os
import subprocess
from dataclasses import replace
from hashlib import sha256
from pathlib import Path

import pytest
from tia.inventory import SuitePolicy, classify
from tia.python_graph import ProviderPolicy, PytestScope, UnresolvedScope
from tia.selection import (
    CollectionIdentity,
    InventoryExpectation,
    InventoryPair,
    SelectionPolicy,
    select,
)
from tia.snapshot import HostedBinding, HostedRequest, LocalRequest, resolve

_CI = Path(__file__).resolve().parents[1]
_SUITES = (_CI / "tia/suites.json").read_bytes()
_CI103 = (_CI / "policy.json").read_bytes()
_PRODUCT = "packages/aitm-usage/tests/"
_CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
_OPTIONAL = (
    _PRODUCT + "test_install.py::test_backup_refuses_store_through_physical_path_alias"
)
_REMOVABLE = (
    _PRODUCT + "test_install.py::test_restore_fences_publication_until_atomic_swap"
)
_TARGET = _PRODUCT + "test_accounting.py"
_NODE = _TARGET + "::test_use[one]"
_REPO = "example/selector"
_GRAPH = ProviderPolicy(
    (b"src", b"packages/aitm-usage", b"tools/ci"),
    (),
    (
        PytestScope(
            "product",
            (),
            (_PRODUCT.rstrip("/").encode(),),
            _PRODUCT.rstrip("/").encode(),
            (),
        ),
        PytestScope("helpers", (), (b"tools/ci/tests",), b"tools/ci/tests", ()),
    ),
    (),
    (),
    (),
)
_EMPTY = b'{"schema":"aitm.tia-edges/v1","edges":[],"path_rules":[]}'


def _encode(value):
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def _git(repo, *args, data=None):
    env = {key: val for key, val in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return (
        subprocess.run(
            ["/usr/bin/git", "-C", str(repo), *args],
            input=data,
            check=True,
            capture_output=True,
            env=env,
        )
        .stdout.decode()
        .strip()
    )


def _write(repo, name, data):
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "trunk")
    _git(tmp_path, "config", "user.name", "Fixture")
    _git(tmp_path, "config", "user.email", "fixture@example.test")
    policy = json.loads(_CI103)
    for node in [*policy["required_tests"], _CLI, _OPTIONAL, _NODE]:
        _write(tmp_path, node.split("::", 1)[0], b"")
    for helper in json.loads(_SUITES)["profiles"]["ci-helpers"]["targets"]:
        _write(tmp_path, helper, b"")
    return tmp_path


def _commit(repo):
    _git(repo, "add", "--all")
    _git(repo, "commit", "-qm", "fixture")
    return _git(repo, "rev-parse", "HEAD")


def _snapshots(repo, base, role="local-effective"):
    if role == "local-effective":
        return resolve(repo, LocalRequest(_REPO, role, base))
    head = _commit(repo)
    tree = _git(repo, "rev-parse", "HEAD^{tree}")
    if role == "pr-tested":
        tested = _git(repo, "commit-tree", tree, "-p", base, "-p", head, "-m", "PR")
        ref = "refs/pull/142/merge"
    else:
        tested, head, ref = head, None, "refs/heads/trunk"
    binding = HostedBinding(_REPO, ref, 102, 3, base, tested, tree, head)
    return resolve(
        repo, HostedRequest(_REPO, role, ref, 102, 3, base, tested, tree, head, binding)
    )


def _collection_for(snapshot):
    if snapshot.mode == "local":
        return None
    endpoint = snapshot.endpoint_identity
    if snapshot.ref_role == "baseline":
        return CollectionIdentity(
            _REPO, endpoint.commit, endpoint.tree, "refs/heads/trunk", 77, 1
        )
    binding = snapshot.provenance.binding
    return CollectionIdentity(
        _REPO,
        endpoint.commit,
        endpoint.tree,
        binding.ref,
        binding.run_id,
        binding.run_attempt,
    )


def _inventory(
    snapshot, *, suite=_SUITES, ci103=_CI103, extra=(_NODE, _OPTIONAL), skip=False
):
    collection = _collection_for(snapshot)
    if collection is None:
        binding = {
            "kind": "local_advisory",
            "repository": _REPO,
            "snapshot": {"content_digest": snapshot.digest},
        }
    else:
        binding = {
            "kind": "hosted_collection_proof",
            "repository": collection.repository,
            "snapshot": {
                "commit": collection.commit,
                "tree": collection.tree,
                "ref": collection.ref,
                "run_id": collection.run_id,
                "run_attempt": collection.run_attempt,
            },
        }

    def lane(profile, items):
        return {
            "profile": profile,
            "platform_scope": "darwin-apfs",
            "binding": binding,
            "runner": {
                "profile": "darwin-apfs",
                "name": "fixture",
                "os": "Darwin",
                "filesystem": "apfs",
            },
            "capabilities": ["native-acl", "darwin", "apfs"],
            "observer": "2" * 64,
            "controls": {"workflow": "3" * 40},
            "receipt_sha256": "5" * 64,
            "exit_code": 0,
            "complete": True,
            "deselected": [],
            "items": items,
        }

    policy = json.loads(ci103)
    helpers = json.loads(suite)["profiles"]["ci-helpers"]["targets"]
    items = [
        {"nodeid": node, "disposition": "collected"}
        for node in [*policy["required_tests"], _CLI, *extra]
    ]
    if skip:
        for item in items:
            if item["nodeid"] == _OPTIONAL:
                item.update(
                    disposition="allowed_skip",
                    reason=policy["optional_skips"][_OPTIONAL],
                )
    source = _encode(
        {
            "schema": "aitm.tia-collection/v1",
            "binding": binding,
            "scopes": [
                lane("product-cli", items),
                lane(
                    "ci-helpers",
                    [
                        {"nodeid": path + "::test_fixture", "disposition": "collected"}
                        for path in helpers
                    ],
                ),
            ],
        }
    )
    collection_doc = json.loads(source)
    if "second-apfs" in json.loads(suite)["runners"]:
        second = lane("product-cli", items)
        second["platform_scope"] = second["runner"]["profile"] = "second-apfs"
        collection_doc["scopes"].append(second)
    rules = SuitePolicy(suite, ci103, "full")
    raw = classify(_encode(collection_doc), rules)
    expected = InventoryExpectation(
        sha256(raw).hexdigest(),
        rules,
        tuple(map(_encode, json.loads(raw)["scopes"])),
        collection,
    )
    return raw, expected


def _inputs(before, after, **kwargs):
    old, old_expected = _inventory(before)
    new, new_expected = _inventory(after, **kwargs)
    return InventoryPair(old, new), SelectionPolicy(
        old_expected, new_expected, _GRAPH, _EMPTY
    )


def _key(node, owner="aitm-usage"):
    return ("pytest", owner, "darwin-apfs", node)


def _reencode_candidate(pair, policy, mutation):
    document = json.loads(pair.after)
    mutation(document)
    raw = _encode(document)
    return replace(pair, after=raw), replace(
        policy, after=replace(policy.after, inventory_sha256=sha256(raw).hexdigest())
    )


@pytest.mark.parametrize("role", ["local-effective", "pr-tested", "trunk-tested"])
def test_binds_independent_endpoint_inventories(repo, role):
    base = _commit(repo)
    _write(repo, _TARGET, b"VALUE = 1\n")
    before, after = _snapshots(repo, base, role)
    pair, policy = _inputs(before, after)
    result = select(before, after, pair, policy)
    assert result.mode == "selected"
    assert _key(_NODE) in result.selected
    assert result.provenance == (
        "local_advisory" if role == "local-effective" else "hosted"
    )
    assert result.before.snapshot_sha256 == before.digest
    assert result.after.snapshot_sha256 == after.digest
    assert result.before.inventory_sha256 == sha256(pair.before).hexdigest()
    assert result.after.inventory_sha256 == sha256(pair.after).hexdigest()


@pytest.mark.parametrize(
    "field,value",
    [
        ("ref", "refs/pull/143/merge"),
        ("run_id", 111),
        ("run_attempt", 4),
    ],
)
def test_stale_hosted_collection_expectation_is_unavailable(repo, field, value):
    base = _commit(repo)
    _write(repo, _TARGET, b"VALUE = 1\n")
    before, after = _snapshots(repo, base, "pr-tested")
    pair, policy = _inputs(before, after)
    stale = replace(policy.after.collection, **{field: value})
    result = select(
        before,
        after,
        pair,
        replace(policy, after=replace(policy.after, collection=stale)),
    )
    assert result.mode == "unavailable"
    assert result.selected == ()
    assert "candidate-inventory" in result.reasons[0]


def test_bad_before_expectation_runs_every_candidate_lane(repo):
    base = _commit(repo)
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    result = select(
        before,
        after,
        pair,
        replace(policy, before=replace(policy.before, inventory_sha256="0" * 64)),
    )
    assert result.mode == "full"
    assert _key(_NODE) in result.selected
    assert (
        _key("tools/ci/tests/test_file_checks.py::test_fixture", "ci-tools")
        in result.selected
    )
    assert len(result.selected) == len(json.loads(pair.after)["obligations"])


@pytest.mark.parametrize(
    "fault", ["digest", "canonical", "lane", "policy", "mandatory", "row"]
)
def test_candidate_inventory_must_be_complete_and_exact(repo, fault):
    base = _commit(repo)
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    if fault == "digest":
        pair = replace(pair, after=pair.after + b"\n")
    elif fault == "canonical":
        raw = pair.after + b"\n"
        pair = replace(pair, after=raw)
        policy = replace(
            policy,
            after=replace(policy.after, inventory_sha256=sha256(raw).hexdigest()),
        )
    elif fault == "lane":
        pair, policy = _reencode_candidate(
            pair, policy, lambda doc: doc["scopes"][0]["runner"].update(name="other")
        )
    elif fault == "policy":
        pair, policy = _reencode_candidate(
            pair, policy, lambda doc: doc.update(ci103_policy_sha256="9" * 64)
        )
    elif fault == "mandatory":
        pair, policy = _reencode_candidate(
            pair,
            policy,
            lambda doc: doc["obligations"].remove(
                next(row for row in doc["obligations"] if row["nodeid"] == _REMOVABLE)
            ),
        )
    else:
        pair, policy = _reencode_candidate(
            pair, policy, lambda doc: doc["obligations"].reverse()
        )
    result = select(before, after, pair, policy)
    assert result.mode == "unavailable"
    assert result.selected == ()
    assert result.reasons
    if fault == "mandatory":
        assert "missing mandatory" in " ".join(result.reasons)
        assert result.missing_required == (_key(_REMOVABLE),)


def _manifest(*, edges=(), rules=()):
    return _encode(
        {"schema": "aitm.tia-edges/v1", "edges": list(edges), "path_rules": list(rules)}
    )


def _edge(rule, consumer, dependency, kind="runtime-file"):
    return {
        "id": rule,
        "consumer": consumer,
        "input": dependency,
        "kind": kind,
        "rationale": "fixture dependency",
    }


def _rule(rule, path, kind="non-test"):
    return {"id": rule, "path": path, "kind": kind, "rationale": "fixture rule"}


def _provider(*, incomplete=()):
    return replace(_GRAPH, incomplete_inputs=incomplete)


def _witnesses(result, path, key=_key(_NODE)):
    return {
        item.side: item
        for item in result.witnesses
        if item.path == path and item.key == key
    }


def test_renamed_module_selects_former_consumer(repo):
    _write(repo, "src/old.py", b"VALUE = 1\n")
    _write(repo, _TARGET, b"import old\n")
    base = _commit(repo)
    _git(repo, "mv", "src/old.py", "src/new.py")
    _write(repo, _TARGET, b"import new\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    result = select(before, after, pair, replace(policy, provider=_provider()))
    assert result.mode == "selected"
    former = _witnesses(result, b"src/old.py")
    assert set(former) == {"before"}
    assert [(hop.input, hop.consumer, hop.kind) for hop in former["before"].hops] == [
        (b"src/old.py", _TARGET.encode(), "import"),
    ]
    assert set(_witnesses(result, b"src/new.py")) == {"after"}
    assert {
        side: w.hops for side, w in _witnesses(result, _TARGET.encode()).items()
    } == {
        "before": (),
        "after": (),
    }


def test_direct_and_multihop_exact_witnesses(repo):
    _write(repo, "src/leaf.py", b"import a\n")
    _write(repo, "src/a.py", b"import leaf\n")
    _write(repo, "src/b.py", b"import leaf\n")
    _write(repo, _PRODUCT + "conftest.py", b"import b\n")
    _write(repo, _TARGET, b"import a\nimport b\n")
    fixture_test = _PRODUCT + "test_claude.py"
    fixture_key = _key(fixture_test + "::test_fixture[two]")
    _write(repo, fixture_test, b"")
    base = _commit(repo)
    _write(repo, "src/leaf.py", b"import a\nVALUE = 2\n")
    before, after = _snapshots(repo, base)
    old, old_expected = _inventory(before, extra=(_NODE, fixture_key[3]))
    new, new_expected = _inventory(after, extra=(_NODE, fixture_key[3]))
    pair = InventoryPair(old, new)
    policy = SelectionPolicy(old_expected, new_expected, _GRAPH, _EMPTY)
    result = select(before, after, pair, policy)
    assert result.mode == "selected"
    target = _witnesses(result, b"src/leaf.py")
    assert set(target) == {"before", "after"}
    assert target["before"].hops == target["after"].hops
    assert [edge.consumer for edge in target["after"].hops] == [
        b"src/a.py",
        _TARGET.encode(),
    ]
    fixture = _witnesses(result, b"src/leaf.py", fixture_key)
    assert [edge.kind for edge in fixture["after"].hops] == [
        "import",
        "import",
        "pytest-fixture",
    ]
    assert [edge.consumer for edge in fixture["after"].hops] == [
        b"src/b.py",
        (_PRODUCT + "conftest.py").encode(),
        fixture_test.encode(),
    ]
    assert fixture["after"].hops[-1].rules == ("pytest:product",)


def test_cross_package_declared_subprocess_path(repo):
    cli = "packages/aitm-usage/src/aitm_usage/cli.py"
    _write(repo, cli, b"VALUE = 1\n")
    base = _commit(repo)
    _write(repo, cli, b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    manifest = (_CI / "tia/edges.json").read_bytes()
    result = select(before, after, pair, replace(policy, manifest=manifest))
    assert result.mode == "selected"
    witnesses = _witnesses(result, cli.encode(), _key(_CLI))
    assert set(witnesses) == {"before", "after"}
    for witness in witnesses.values():
        (hop,) = witness.hops
        assert (hop.kind, hop.input, hop.consumer, hop.rules) == (
            "subprocess",
            cli.encode(),
            _CLI.split("::")[0].encode(),
            ("cli-help-subprocess",),
        )
    assert result.manifest_sha256 == sha256(manifest).hexdigest()
    assert result.provider_policy_sha256


def test_deleted_source_keeps_only_surviving_former_witnesses(repo):
    other = _TARGET + "::test_use[two]"
    _write(repo, "src/retired.py", b"VALUE = 1\n")
    _write(repo, _TARGET, b"import retired\n")
    base = _commit(repo)
    (repo / "src/retired.py").unlink()
    _write(repo, _TARGET, b"VALUE = 1\n")
    before, after = _snapshots(repo, base)
    old, old_expected = _inventory(before, extra=(_NODE, other))
    new, new_expected = _inventory(after, extra=(_NODE,))
    result = select(
        before,
        after,
        InventoryPair(old, new),
        SelectionPolicy(old_expected, new_expected, _provider(), _EMPTY),
    )
    assert set(_witnesses(result, b"src/retired.py")) == {"before"}
    assert not _witnesses(result, b"src/retired.py", _key(other))
    assert result.removed == (_key(other),)
    assert result.mode == "full"


def test_known_edge_plus_unbounded_reader_runs_full(repo):
    _write(repo, "src/leaf.py", b"VALUE = 1\n")
    _write(repo, _TARGET, b"import leaf\n")
    base = _commit(repo)
    _write(repo, "src/leaf.py", b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    suite = json.loads(_SUITES)
    suite["runners"]["second-apfs"] = {
        **suite["runners"]["darwin-apfs"],
        "platform_scope": "second-apfs",
    }
    suite["workloads"]["full"]["required_pairs"].append(["product-cli", "second-apfs"])
    raw_suite = _encode(suite)
    old, old_expected = _inventory(before, suite=raw_suite)
    new, new_expected = _inventory(after, suite=raw_suite)
    provider = _provider(
        incomplete=(
            UnresolvedScope(b"src/reader.py", "runtime-reader", "unknown", None),
        )
    )
    result = select(
        before,
        after,
        InventoryPair(old, new),
        SelectionPolicy(old_expected, new_expected, provider, _EMPTY),
    )
    assert result.mode == "full"
    assert _key(_NODE) in result.selected
    assert ("pytest", "aitm-usage", "second-apfs", _NODE) in result.selected
    assert (
        _key("tools/ci/tests/test_verify_pr.py::test_fixture", "ci-tools")
        in result.selected
    )
    assert len(result.selected) == len(json.loads(new)["obligations"])
    assert set(_witnesses(result, b"src/leaf.py")) == {"before", "after"}
    assert {r.code for r in result.paths[0].uncertainties} == {"runtime-reader"}


@pytest.mark.parametrize(
    "bound,mode", [(b"src/transit.py", "full"), (b"src/transit", "selected")]
)
def test_bounded_reader_matches_a_transitive_consumer_by_path_components(
    repo, bound, mode
):
    _write(repo, "src/leaf.py", b"VALUE = 1\n")
    _write(repo, "src/transit.py", b"import leaf\n")
    _write(repo, _TARGET, b"import transit\n")
    base = _commit(repo)
    _write(repo, "src/leaf.py", b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    provider = _provider(
        incomplete=(
            UnresolvedScope(b"src/reader.py", "bounded-reader", "unknown", (bound,)),
        )
    )
    result = select(before, after, pair, replace(policy, provider=provider))
    assert result.mode == mode
    assert bool(result.paths[0].uncertainties) == (mode == "full")
    assert _witnesses(result, b"src/leaf.py")


@pytest.mark.parametrize(
    "endpoint,mode", [("src/transit.py", "full"), ("other/file.py", "selected")]
)
def test_missing_declaration_only_matters_when_an_endpoint_is_reached(
    repo, endpoint, mode
):
    _write(repo, "src/leaf.py", b"VALUE = 1\n")
    _write(repo, "src/transit.py", b"import leaf\n")
    _write(repo, _TARGET, b"import transit\n")
    base = _commit(repo)
    _write(repo, "src/leaf.py", b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    manifest = _manifest(edges=[_edge("missing-runtime", endpoint, "absent/data.json")])
    result = select(
        before, after, pair, replace(policy, manifest=manifest, provider=_provider())
    )
    assert result.mode == mode
    assert _witnesses(result, b"src/leaf.py")
    assert {r.rule for r in result.paths[0].uncertainties} == (
        {"missing-runtime"} if mode == "full" else set()
    )


def test_changed_test_and_non_test_disposition(repo):
    _write(repo, "guide.md", b"old")
    base = _commit(repo)
    _write(repo, "guide.md", b"new")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(
        before, after, extra=(_NODE, _OPTIONAL, _TARGET + "::test_new")
    )
    manifest = _manifest(rules=[_rule("docs", "guide.md")])
    result = select(before, after, pair, replace(policy, manifest=manifest))
    assert result.mode == "selected"
    assert result.paths[0].disposition == "non-test"
    assert result.paths[0].rules == ("docs",)
    assert _key(_NODE) not in result.selected
    assert _key(_CLI) in result.selected
    assert _key(_TARGET + "::test_new") in result.selected
    assert {(r.key, r.code) for r in result.obligation_reasons} >= {
        (_key(_CLI), "mandatory"),
        (_key(_TARGET + "::test_new"), "newly-collected"),
    }


@pytest.mark.parametrize(
    "kind", ["unclassified", "shared-input", "conflicting-non-test"]
)
def test_unsupported_no_impact_claims_run_full(repo, kind):
    dependency = "src/test_accounting.py"
    _write(repo, dependency, b"VALUE = 1\n")
    if kind == "conflicting-non-test":
        _write(repo, _TARGET, b"import test_accounting\n")
    base = _commit(repo)
    _write(repo, dependency, b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    rule_kind = "non-test" if kind == "conflicting-non-test" else kind
    rules = (
        [] if kind == "unclassified" else [_rule("sample-rule", dependency, rule_kind)]
    )
    result = select(
        before,
        after,
        pair,
        replace(policy, provider=_GRAPH, manifest=_manifest(rules=rules)),
    )
    if kind == "conflicting-non-test":
        assert result.paths[0].disposition != "non-test"
    else:
        assert result.mode == "full"
        assert not _witnesses(result, dependency.encode())
        assert result.paths[0].disposition == "uncertain"


def test_no_tests_requires_positive_classification():
    from tia.selection import PathDisposition, _mode

    known = PathDisposition(b"guide.md", ("after",), "non-test", ("docs",))
    assert _mode((), (known,), ()) == "no-tests"
    assert _mode((), (), ()) == "full"
    assert _mode((), (replace(known, disposition="uncertain"),), ()) == "full"
    assert _mode((_key(_CLI),), (known,), ()) == "selected"


@pytest.mark.parametrize("changed_policy", [False, True])
def test_required_row_removal_retains_verified_deleted_source(repo, changed_policy):
    removed_source = _PRODUCT + "test_service_process.py"
    removed = removed_source + "::test_real_service_crash_enrollment_and_private_state"
    base = _commit(repo)
    (repo / removed_source).unlink()
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    if changed_policy:
        reviewed = json.loads(_CI103)
        reviewed["required_tests"].remove(removed)
        raw, expected = _inventory(after, ci103=_encode(reviewed))
        pair = replace(pair, after=raw)
        policy = replace(policy, after=expected)
    else:
        pair, policy = _reencode_candidate(
            pair,
            policy,
            lambda doc: doc["obligations"].remove(
                next(row for row in doc["obligations"] if row["nodeid"] == removed)
            ),
        )
    result = select(before, after, pair, policy)
    assert result.removed == (_key(removed),)
    assert result.mode == ("full" if changed_policy else "unavailable")
    assert bool(result.selected) == changed_policy
    assert any(
        ("policy-changed" if changed_policy else "missing mandatory") in r
        for r in result.reasons
    )


def test_allowed_skip_is_kept_and_same_key_disposition_change_runs_full(repo):
    _write(repo, _PRODUCT + "test_install.py", b"VALUE = 1\n")
    base = _commit(repo)
    _write(repo, _PRODUCT + "test_install.py", b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after, skip=True)
    result = select(before, after, pair, policy)
    assert result.mode == "full"
    assert result.changed_obligations == (_key(_OPTIONAL),)
    assert result.removed == ()
    assert _key(_OPTIONAL) in result.selected
    assert set(
        _witnesses(result, (_PRODUCT + "test_install.py").encode(), _key(_OPTIONAL))
    ) == {
        "before",
        "after",
    }


def test_declared_fixture_cross_package(repo):
    dependency = "runtime/fixture.json"
    fixture = _PRODUCT + "conftest.py"
    _write(repo, dependency, b"{}")
    _write(repo, fixture, b"")
    base = _commit(repo)
    _write(repo, dependency, b'{"changed":true}')
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    manifest = _manifest(
        edges=[_edge("runtime-fixture", fixture, dependency, "fixture")]
    )
    result = select(before, after, pair, replace(policy, manifest=manifest))
    assert result.mode == "selected"
    trace = _witnesses(result, dependency.encode())["after"]
    assert [(hop.kind, hop.consumer, hop.rules) for hop in trace.hops] == [
        ("fixture", fixture.encode(), ("runtime-fixture",)),
        ("pytest-fixture", _TARGET.encode(), ("pytest:product",)),
    ]


@pytest.mark.parametrize(
    "fault", ["duplicate-change", "missing-change", "different-changes"]
)
def test_contradictory_pair_cannot_supply_before_witnesses(repo, fault):
    _write(repo, "src/leaf.py", b"VALUE = 1\n")
    _write(repo, _TARGET, b"import leaf\n")
    base = _commit(repo)
    _write(repo, "src/leaf.py", b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    if fault == "duplicate-change":
        before = replace(before, changes=before.changes * 2)
        after = replace(after, changes=after.changes * 2)
    elif fault == "missing-change":
        before, after = replace(before, changes=()), replace(after, changes=())
    else:
        before = replace(before, changes=())
    pair, policy = _inputs(before, after)
    result = select(before, after, pair, policy)
    assert result.mode == "full"
    assert not result.witnesses
    assert any(r.startswith("snapshot-pair:") for r in result.reasons)


def test_raw_hosted_path_never_matches_a_display_spelling(repo):
    base = _commit(repo)
    path = b"guide-\xff.md"
    blob = _git(repo, "hash-object", "-w", "--stdin", data=b"new")
    _git(
        repo,
        "update-index",
        "-z",
        "--index-info",
        data=f"100644 {blob}\t".encode() + path + b"\0",
    )
    tree = _git(repo, "write-tree")
    head = _git(repo, "commit-tree", tree, "-p", base, "-m", "raw path")
    ref = "refs/heads/trunk"
    binding = HostedBinding(_REPO, ref, 102, 3, base, head, tree)
    before, after = resolve(
        repo,
        HostedRequest(
            _REPO, "trunk-tested", ref, 102, 3, base, head, tree, None, binding
        ),
    )
    pair, policy = _inputs(before, after)
    manifest = _manifest(rules=[_rule("display-lookalike", "guide-\ufffd.md")])
    result = select(before, after, pair, replace(policy, manifest=manifest))
    assert result.mode == "full"
    assert [item.path for item in result.paths] == [path]
    assert not result.paths[0].rules


@pytest.mark.parametrize(
    "manifest",
    [
        _manifest(edges=[_edge("one", _TARGET, "src/../leaf.py")]),
        _manifest(edges=[_edge("one", _TARGET, "src/*.py")]),
        _manifest(rules=[_rule("same", "src/leaf.py"), _rule("same", "other.md")]),
        _manifest(
            rules=[
                _rule("one", "src/leaf.py"),
                _rule("two", "src/leaf.py", "shared-input"),
            ]
        ),
        b'{"schema":"aitm.tia-edges/v1","edges":[],"edges":[],"path_rules":[]}',
    ],
)
def test_invalid_manifest_cannot_narrow_selection(repo, manifest):
    _write(repo, "src/leaf.py", b"VALUE = 1\n")
    _write(repo, _TARGET, b"import leaf\n")
    base = _commit(repo)
    _write(repo, "src/leaf.py", b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    result = select(before, after, pair, replace(policy, manifest=manifest))
    assert result.mode == "full"
    assert _witnesses(result, b"src/leaf.py")
    assert any(r.startswith("declaration-manifest:") for r in result.reasons)


def test_inventory_test_outside_all_qualified_pytest_scopes_forces_full(repo):
    _write(repo, "src/leaf.py", b"VALUE = 1\n")
    _write(repo, _TARGET, b"import leaf\n")
    base = _commit(repo)
    _write(repo, "src/leaf.py", b"VALUE = 2\n")
    before, after = _snapshots(repo, base)
    pair, policy = _inputs(before, after)
    product, _ = _GRAPH.pytest_scopes
    result = select(
        before,
        after,
        pair,
        replace(policy, provider=replace(_GRAPH, pytest_scopes=(product,))),
    )
    assert result.mode == "full"
    assert _witnesses(result, b"src/leaf.py")
    assert any(
        r.code == "pytest-collection-scope-missing"
        for r in result.paths[0].uncertainties
    )
