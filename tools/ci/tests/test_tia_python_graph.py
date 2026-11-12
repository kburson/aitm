"""Verify Python and pytest edges from exact endpoint inputs."""

import os
import shutil
import subprocess
import sys
from dataclasses import replace
from hashlib import sha256

import pytest
from tia.python_graph import (
    Edge,
    ProviderPolicy,
    PytestScope,
    UnresolvedScope,
    build_graph,
)
from tia.snapshot import Entry, LocalRequest, SnapshotUncertain, resolve


class Endpoint:
    def __init__(self, sources, modes=None):
        self.sources = sources
        modes = modes or {}
        self.entries = tuple(
            Entry(path, modes.get(path, "100644"), sha256(content).hexdigest())
            for path, content in sorted(sources.items())
        )
        self.digest = sha256(repr(self.entries).encode()).hexdigest()

    def read_content(self, path):
        return self.sources[path]


def policy(*roots, **overrides):
    return replace(ProviderPolicy(roots, (), (), (), (), ()), **overrides)


def edges(graph):
    return {(edge.consumer, edge.input, edge.kind) for edge in graph.edges}


def test_import_alias_relative_reexport_cycle():
    test = b"tests/test_example.py"
    init = b"app/pkg/__init__.py"
    worker = b"app/pkg/worker.py"
    other_init = b"lib/other/__init__.py"
    helper = b"lib/other/helper.py"
    endpoint = Endpoint(
        {
            init: b"from .worker import exported",
            worker: b"import pkg as p\nexported = 1",
            other_init: b"",
            helper: b"",
            test: (
                b"from pkg import exported as use\n"
                b"from pkg import worker as w\n"
                b"import other.helper as helper"
            ),
        }
    )
    rules = policy(b"app", b"lib", b"tests")
    graph = build_graph(endpoint, rules)

    assert edges(graph) == {
        (test, init, "package-init"),
        (test, worker, "import"),
        (test, other_init, "package-init"),
        (test, helper, "import"),
        (init, worker, "import"),
        (worker, init, "package-init"),
    }
    assert graph.unresolved == ()
    assert graph.snapshot_digest == endpoint.digest
    assert all(edge.rules == ("python-ast",) for edge in graph.edges)
    assert tuple((e.consumer, e.input, e.kind) for e in graph.edges) == tuple(
        sorted(edges(graph))
    )
    assert build_graph(endpoint, rules) == graph
    assert (
        build_graph(
            endpoint, replace(rules, external_modules=("pathlib",))
        ).policy_digest
        != graph.policy_digest
    )


def test_dynamic_scope():
    bounded = b"app/reader.py"
    unbounded = b"tests/test_example.py"
    known = b"lib/helper.py"
    uncovered = UnresolvedScope(None, "incomplete-input", "runtime-files", None)
    endpoint = Endpoint(
        {
            bounded: (
                b"import importlib as loader\n"
                b"from builtins import __import__ as load\n"
                b"f = loader.import_module\nload(computed)"
            ),
            unbounded: b"from importlib import import_module as load\nimport helper",
            known: b"",
        }
    )
    rules = policy(
        b"app",
        b"lib",
        b"tests",
        external_modules=("builtins", "importlib"),
        dynamic_import_bounds=((bounded, (b"app", b"lib/helper.py")),),
        incomplete_inputs=(uncovered,),
    )

    graph = build_graph(endpoint, rules)
    assert edges(graph) == {(unbounded, known, "import")}
    assert set(graph.unresolved) == {
        UnresolvedScope(bounded, "dynamic-import", "", (b"app", b"lib/helper.py")),
        UnresolvedScope(unbounded, "dynamic-import", "", None),
        uncovered,
    }


def test_ambiguous_owners_keep_possible_edges():
    reader = b"tests/test_owners.py"
    first = b"one/shared/worker.py"
    second = b"two/shared/worker.py"
    collision = b"one/collision.py"
    package = b"two/collision/__init__.py"
    local_external = b"one/pathlib.py"
    endpoint = Endpoint(
        {
            reader: b"import shared.worker, collision, pathlib.missing",
            first: b"",
            second: b"",
            collision: b"",
            package: b"",
            local_external: b"",
        }
    )

    graph = build_graph(
        endpoint, policy(b"one", b"two", b"tests", external_modules=("pathlib",))
    )
    assert edges(graph) == {
        (reader, first, "import"),
        (reader, second, "import"),
        (reader, collision, "import"),
        (reader, package, "package-init"),
        (reader, local_external, "import"),
    }
    assert set(graph.unresolved) == {
        UnresolvedScope(reader, "ambiguous-module", "shared", None),
        UnresolvedScope(reader, "ambiguous-module", "shared.worker", None),
        UnresolvedScope(reader, "ambiguous-module", "collision", None),
        UnresolvedScope(reader, "unresolved-import", "pathlib.missing", None),
    }


def test_ambiguous_relative_context_keeps_valid_dependency():
    reader = b"src/pkg/helper.py"
    owner = b"src/pkg/worker.py"
    endpoint = Endpoint(
        {reader: b"from .worker import work", owner: b"work = lambda: None"}
    )

    graph = build_graph(endpoint, policy(b"src", b"src/pkg"))
    assert edges(graph) == {(reader, owner, "import")}
    assert set(graph.unresolved) == {
        UnresolvedScope(reader, "relative-import-context", "worker", None)
    }


def test_pytest_scope_keeps_fixture_config_and_search_evidence():
    nested = b"product/tests/nested/test_deep.py"
    sibling = b"product/tests/test_near.py"
    cli = b"tools/ci/tests/test_cli_evidence.py"
    unmapped = b"elsewhere/test_absolute.py"
    main_fixture = b"product/tests/conftest.py"
    nested_fixture = b"product/tests/nested/conftest.py"
    helper = b"deps/helper.py"
    config = b"product/pyproject.toml"
    plugin = b"tools/ci/observer.py"
    endpoint = Endpoint(
        {
            nested: b"",
            sibling: b"",
            cli: b"",
            unmapped: b"import helper",
            main_fixture: b"import helper",
            nested_fixture: b"pytest_plugins = ('extra',)",
            helper: b"",
            config: b"",
            plugin: b"",
            b"product/conftest.py": b"raise Exception('outside cutoff')",
        }
    )
    qualified = PytestScope(
        "product",
        (cli,),
        (b"product/tests",),
        b"product/tests",
        (config, plugin),
    )
    # The product CLI test is outside that fixture cutoff. A second
    # qualified profile sees the same config but a different cutoff.
    cli_scope = PytestScope("cli", (cli,), (), b"tools/ci", (config,))
    unqualified = PytestScope("unqualified", (unmapped,), (), None, None)
    missing = PytestScope("missing", (nested,), (), b"", (b"absent.ini",))
    rules = policy(
        b"product/tests",
        b"tools/ci",
        b"deps",
        pytest_scopes=(qualified, cli_scope, unqualified),
    )

    graph = build_graph(endpoint, rules)
    assert edges(graph) == {
        (nested, main_fixture, "pytest-fixture"),
        (nested, nested_fixture, "pytest-fixture"),
        (sibling, main_fixture, "pytest-fixture"),
        (main_fixture, helper, "import"),
        (unmapped, helper, "import"),
        (nested, config, "pytest-config"),
        (nested, plugin, "pytest-config"),
        (sibling, config, "pytest-config"),
        (sibling, plugin, "pytest-config"),
        (cli, config, "pytest-config"),
        (cli, plugin, "pytest-config"),
    }
    assert Edge(cli, config, "pytest-config", ("pytest:cli", "pytest:product")) in (
        graph.edges
    )
    assert {(record.reader, record.reason) for record in graph.unresolved} == {
        (cli, "pytest-fixture-scope"),
        (unmapped, "pytest-fixture-scope"),
        (unmapped, "pytest-config-scope"),
        (unmapped, "pytest-import-scope"),
        (nested_fixture, "pytest-plugin"),
    }
    assert all(record.possible_inputs is None for record in graph.unresolved)
    with_missing = build_graph(
        endpoint, replace(rules, pytest_scopes=(qualified, cli_scope, missing))
    )
    assert (nested, b"product/conftest.py", "pytest-fixture") in edges(with_missing)
    assert any(
        record.reader == nested and record.reason == "pytest-config-missing"
        for record in with_missing.unresolved
    )


def test_reviewed_package_dependencies_require_exact_endpoints():
    reader = b"app/pkg/__init__.py"
    config = b"lib/pyproject.toml"
    endpoint = Endpoint({reader: b"", config: b""})
    rules = policy(
        b"app",
        package_dependencies=(
            (reader, config, "workspace-install"),
            (reader, b"lib/absent.toml", "missing-input"),
        ),
    )

    graph = build_graph(endpoint, rules)
    assert graph.edges == (
        Edge(reader, config, "package-dependency", ("workspace-install",)),
    )
    assert graph.unresolved == (
        UnresolvedScope(reader, "package-dependency-endpoint", "missing-input", None),
    )


def test_graph_binds_real_snapshot_pair(tmp_path):
    executable = "/usr/bin/git" if sys.platform == "darwin" else shutil.which("git")
    assert executable is not None
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)

    def git(*args):
        return subprocess.run(
            [executable, "-C", str(tmp_path), *args],
            check=True,
            capture_output=True,
            env=env,
        ).stdout

    git("init", "-q", "-b", "trunk")
    git("config", "user.name", "Fixture")
    git("config", "user.email", "fixture@example.test")
    (tmp_path / "src").mkdir()
    (tmp_path / "src/old.py").write_text("VALUE = 1\n", encoding="utf-8")
    consumer = tmp_path / "src/consumer.py"
    consumer.write_text("import old\n", encoding="utf-8")
    git("add", "--all")
    git("commit", "-q", "-m", "fixture")
    base = git("rev-parse", "HEAD").decode().strip()
    git("mv", "src/old.py", "src/new.py")
    consumer.write_text("import new\n", encoding="utf-8")

    before, after = resolve(
        tmp_path, LocalRequest("owner/project", "local-effective", base)
    )
    rules = policy(b"src")
    old = build_graph(before, rules)
    new = build_graph(after, rules)
    assert edges(old) == {(b"src/consumer.py", b"src/old.py", "import")}
    assert edges(new) == {(b"src/consumer.py", b"src/new.py", "import")}
    assert (old.snapshot_digest, new.snapshot_digest) == (before.digest, after.digest)
    assert old.snapshot_digest != new.snapshot_digest
    assert old.policy_digest == new.policy_digest


def test_invalid_source_retains_uncertainty():
    encoded = b"src/encoded.py"
    raw = b"src/raw-\xff.py"
    syntax = b"src/syntax.py"
    symlink = b"src/symlink.py"
    dependency = b"src/helper.py"
    endpoint = Endpoint(
        {
            encoded: b"# coding: latin-1\nlabel = '\xff'\nimport helper",
            raw: b"import helper",
            syntax: b"def no(): invalid :",
            symlink: b"helper.py",
            dependency: b"",
        },
        modes={symlink: "120000"},
    )

    graph = build_graph(endpoint, policy(b"src"))
    assert edges(graph) == {
        (encoded, dependency, "import"),
        (raw, dependency, "import"),
    }
    assert {(record.reader, record.reason) for record in graph.unresolved} == {
        (raw, "unindexable-source"),
        (syntax, "python-parse"),
        (symlink, "unsupported-python-mode"),
    }


def test_bound_read_failure_refuses_graph():
    failure = SnapshotUncertain("hosted", "blob_unavailable")

    class UnavailableEndpoint(Endpoint):
        def read_content(self, path):
            raise failure

    endpoint = UnavailableEndpoint({b"src/module.py": b""})
    with pytest.raises(SnapshotUncertain) as caught:
        build_graph(endpoint, policy(b"src"))
    assert caught.value is failure


@pytest.mark.parametrize(
    "rules",
    [
        policy(b"../src"),
        policy(b"src", external_modules=["os"]),
        policy(b"src", pytest_scopes=(None,)),
        policy(b"src", package_dependencies=((b"src/reader.py",),)),
        policy(b"src", dynamic_import_bounds=((b"src/reader.py", [b"src"]),)),
        policy(b"src", dynamic_import_bounds=((b"src/reader.py", ()),)),
        policy(
            b"src",
            dynamic_import_bounds=(
                (b"src/reader.py", (b"src",)),
                (b"src/reader.py", (b"lib",)),
            ),
        ),
        policy(
            b"src",
            pytest_scopes=(
                PytestScope("same", (), (), b"", ()),
                PytestScope("same", (), (), b"", ()),
            ),
        ),
    ],
)
def test_invalid_policy_cannot_authorize_a_graph(rules):
    with pytest.raises(ValueError):
        build_graph(Endpoint({}), rules)
