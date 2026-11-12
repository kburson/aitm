"""Build Python file dependencies from one bound TIA snapshot."""

import ast
import json
from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from hashlib import sha256

from .snapshot import Snapshot

_REGULAR = {"100644", "100755"}
_DYNAMIC_LOADERS = {
    "builtins": ("__import__",),
    "importlib": ("__import__", "import_module"),
}


@dataclass(frozen=True)
class PytestScope:
    """Repository inputs for one independently qualified invocation."""

    name: str
    test_paths: tuple[bytes, ...]
    test_roots: tuple[bytes, ...]
    fixture_root: bytes | None
    config_paths: tuple[bytes, ...] | None


@dataclass(frozen=True)
class UnresolvedScope:
    reader: bytes | None
    reason: str
    detail: str
    possible_inputs: tuple[bytes, ...] | None


@dataclass(frozen=True)
class ProviderPolicy:
    """The caller supplies reviewed search paths, input scopes and declarations."""

    import_roots: tuple[bytes, ...]
    external_modules: tuple[str, ...]
    pytest_scopes: tuple[PytestScope, ...]
    package_dependencies: tuple[tuple[bytes, bytes, str], ...]
    dynamic_import_bounds: tuple[tuple[bytes, tuple[bytes, ...]], ...]
    incomplete_inputs: tuple[UnresolvedScope, ...]


@dataclass(frozen=True)
class Edge:
    consumer: bytes
    input: bytes
    kind: str
    rules: tuple[str, ...]


@dataclass(frozen=True)
class Graph:
    snapshot_digest: str
    policy_digest: str
    edges: tuple[Edge, ...]
    unresolved: tuple[UnresolvedScope, ...]


@dataclass(frozen=True)
class _ModuleOwner:
    path: bytes
    kind: str


def _require_path(path, *, allow_root=False):
    if not isinstance(path, bytes) or b"\x00" in path:
        raise ValueError("provider policy requires repository byte paths")
    if allow_root and not path:
        return
    if any(part in {b"", b".", b".."} for part in path.split(b"/")):
        raise ValueError("provider policy path is not repository-relative")


def _policy_tuple(values, *, arity=None):
    if not isinstance(values, tuple) or (arity is not None and len(values) != arity):
        raise ValueError("provider policy requires a tuple of the declared shape")
    return values


def _require_prefixes(prefixes):
    if not _policy_tuple(prefixes):
        raise ValueError("provider policy input bound is empty")
    for prefix in prefixes:
        _require_path(prefix)


def _require_rule(rule):
    if not isinstance(rule, str) or not rule:
        raise ValueError("provider policy requires a nonempty rule name")


def _policy_digest(policy):
    if not isinstance(policy, ProviderPolicy):
        raise ValueError("expected a Python provider policy")
    for root in _policy_tuple(policy.import_roots):
        _require_path(root, allow_root=True)
    for module in _policy_tuple(policy.external_modules):
        if not isinstance(module, str) or not module.isidentifier():
            raise ValueError("external module approval requires a top-level name")

    scope_names = set()
    for scope in _policy_tuple(policy.pytest_scopes):
        if not isinstance(scope, PytestScope):
            raise ValueError("expected a pytest scope record")
        _require_rule(scope.name)
        if scope.name in scope_names:
            raise ValueError("duplicate pytest scope name")
        scope_names.add(scope.name)
        for path in _policy_tuple(scope.test_paths):
            _require_path(path)
            if not path.endswith(b".py"):
                raise ValueError("pytest scope requires Python test paths")
        for root in _policy_tuple(scope.test_roots):
            _require_path(root, allow_root=True)
        if scope.fixture_root is not None:
            _require_path(scope.fixture_root, allow_root=True)
        if scope.config_paths is not None:
            for path in _policy_tuple(scope.config_paths):
                _require_path(path)

    for declaration in _policy_tuple(policy.package_dependencies):
        consumer, dependency, rule = _policy_tuple(declaration, arity=3)
        _require_path(consumer)
        _require_path(dependency)
        _require_rule(rule)

    bounded_readers = set()
    for bound in _policy_tuple(policy.dynamic_import_bounds):
        reader, prefixes = _policy_tuple(bound, arity=2)
        _require_path(reader)
        _require_prefixes(prefixes)
        if reader in bounded_readers:
            raise ValueError("multiple dynamic import bounds for the same reader")
        bounded_readers.add(reader)

    for record in _policy_tuple(policy.incomplete_inputs):
        if not isinstance(record, UnresolvedScope):
            raise ValueError("expected an unresolved input scope record")
        if record.reader is not None:
            _require_path(record.reader)
        _require_rule(record.reason)
        if not isinstance(record.detail, str):
            raise ValueError("unresolved input detail must be text")
        if record.possible_inputs is not None:
            _require_prefixes(record.possible_inputs)

    raw = json.dumps(
        asdict(policy), sort_keys=True, separators=(",", ":"), default=bytes.hex
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def _under(path, directory):
    return not directory or path.startswith(directory + b"/")


def _module_parts(raw_path):
    try:
        parts = tuple(raw_path.decode("utf-8").split("/"))
    except UnicodeDecodeError:
        return ()
    if all(part.isidentifier() for part in parts):
        return parts
    return ()


def _unresolved_key(record):
    return (
        record.reader is not None,
        record.reader or b"",
        record.reason,
        record.detail,
        record.possible_inputs is None,
        record.possible_inputs or (),
    )


def _dynamic_import_present(nodes):
    module_aliases = {module: {module} for module in _DYNAMIC_LOADERS}
    for node in nodes:
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.partition(".")[0]
                if module in module_aliases and (
                    alias.name == module or not alias.asname
                ):
                    module_aliases[module].add(alias.asname or module)
        elif isinstance(node, ast.ImportFrom) and not node.level:
            loaders = _DYNAMIC_LOADERS.get(node.module)
            if loaders and any(
                alias.name == "*" or alias.name in loaders for alias in node.names
            ):
                return True

    for node in nodes:
        if isinstance(node, ast.Name) and node.id == "__import__":
            return True
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if any(
                node.attr in loaders and node.value.id in module_aliases[module]
                for module, loaders in _DYNAMIC_LOADERS.items()
            ):
                return True
    return False


def _declares_pytest_plugins(nodes):
    return any(
        isinstance(node, ast.Name)
        and node.id == "pytest_plugins"
        and isinstance(node.ctx, ast.Store)
        or isinstance(node, ast.alias)
        and (node.asname or node.name) == "pytest_plugins"
        for node in nodes
    )


class _GraphBuilder:
    def __init__(self, snapshot, policy):
        self.snapshot = snapshot
        self.policy = policy
        self.entries = {entry.path: entry.mode for entry in snapshot.entries}
        self.sources = set()
        self.contexts = defaultdict(set)
        self.owners = defaultdict(set)
        self.edges = defaultdict(set)
        self.unresolved = set()
        self.dynamic_bounds = {
            reader: tuple(sorted(set(prefixes)))
            for reader, prefixes in policy.dynamic_import_bounds
        }

    def _edge(self, reader, dependency, kind, rule):
        if reader != dependency:
            self.edges[reader, dependency, kind].add(rule)

    def _unknown(self, reader, reason, detail="", prefixes=None):
        self.unresolved.add(UnresolvedScope(reader, reason, detail, prefixes))

    def _index_sources(self):
        for root in self.policy.import_roots:
            offset = len(root) + 1 if root else 0
            directories = set()
            for path in self.entries:
                if not _under(path, root):
                    continue
                relative = path[offset:]
                directory = relative.rpartition(b"/")[0]
                while directory and directory not in directories:
                    directories.add(directory)
                    directory = directory.rpartition(b"/")[0]
                if not relative.endswith(b".py"):
                    continue
                self.sources.add(path)
                parts = _module_parts(relative[:-3])
                if not parts:
                    self._unknown(path, "unindexable-source")
                    continue
                initializer = len(parts) > 1 and parts[-1] == "__init__"
                if initializer:
                    parts = parts[:-1]
                name = ".".join(parts)
                kind = "package-init" if initializer else "import"
                self.owners[name].add(_ModuleOwner(path, kind))
                self.contexts[path].add(parts if initializer else parts[:-1])

            for directory in directories:
                parts = _module_parts(directory)
                path = root + b"/" + directory if root else directory
                if parts and path + b"/__init__.py" not in self.entries:
                    self.owners[".".join(parts)].add(_ModuleOwner(path, "namespace"))

    def _resolve_import(self, reader, name):
        parts = name.split(".")
        for stop in range(1, len(parts) + 1):
            prefix = ".".join(parts[:stop])
            candidates = self.owners.get(prefix, ())
            if len(candidates) > 1:
                self._unknown(reader, "ambiguous-module", prefix)
            for owner in candidates:
                if owner.kind != "namespace":
                    self._edge(reader, owner.path, owner.kind, "python-ast")
        if name not in self.owners and (
            parts[0] in self.owners or parts[0] not in self.policy.external_modules
        ):
            self._unknown(reader, "unresolved-import", name)

    def _from_import(self, reader, node):
        if node.level:
            contexts = self.contexts.get(reader, ())
            valid = [context for context in contexts if len(context) >= node.level]
            if len(contexts) != 1 or not valid:
                self._unknown(reader, "relative-import-context", node.module or "")
            module_parts = tuple(node.module.split(".")) if node.module else ()
            names = {
                ".".join(context[: len(context) - node.level + 1] + module_parts)
                for context in valid
            }
        else:
            names = {node.module}
        for name in names:
            self._resolve_import(reader, name)
            owners = self.owners.get(name, ())
            namespace_only = bool(owners) and all(
                owner.kind == "namespace" for owner in owners
            )
            for alias in node.names:
                if alias.name == "*":
                    # A package's __all__ can trigger child imports at runtime.
                    if any(
                        owner.kind in {"package-init", "namespace"} for owner in owners
                    ):
                        self._unknown(reader, "wildcard-import", name)
                    continue
                child = f"{name}.{alias.name}"
                # A namespace has no initializer to account for a missing symbol.
                if child in self.owners or namespace_only:
                    self._resolve_import(reader, child)

    def _scan_source(self, path):
        if self.entries[path] not in _REGULAR:
            self._unknown(path, "unsupported-python-mode")
            return
        content = self.snapshot.read_content(path)
        try:
            nodes = tuple(ast.walk(ast.parse(content)))
        except (SyntaxError, ValueError, RecursionError):
            self._unknown(path, "python-parse")
            return
        for node in nodes:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._resolve_import(path, alias.name)
            elif isinstance(node, ast.ImportFrom):
                self._from_import(path, node)
        if _dynamic_import_present(nodes):
            self._unknown(
                path, "dynamic-import", prefixes=self.dynamic_bounds.get(path)
            )
        if _declares_pytest_plugins(nodes):
            self._unknown(path, "pytest-plugin")

    def _pytest_reader(self, path):
        if path.endswith(b".py"):
            self.sources.add(path)
            if path not in self.contexts:
                self._unknown(path, "pytest-import-scope")

    def _pytest_fixtures(self, path, scope, rule):
        cutoff = scope.fixture_root
        if cutoff is None or not _under(path, cutoff):
            self._unknown(path, "pytest-fixture-scope", scope.name)
            return
        ancestor = path.rpartition(b"/")[0]
        while True:
            fixture = ancestor + b"/conftest.py" if ancestor else b"conftest.py"
            if fixture in self.entries:
                self._edge(path, fixture, "pytest-fixture", rule)
                self._pytest_reader(fixture)
            if ancestor == cutoff:
                return
            ancestor = ancestor.rpartition(b"/")[0]

    def _pytest_config(self, path, scope, rule):
        if scope.config_paths is None:
            self._unknown(path, "pytest-config-scope", scope.name)
            return
        for config in scope.config_paths:
            mode = self.entries.get(config)
            detail = f"{scope.name}:{config.hex()}"
            if mode is None:
                self._unknown(path, "pytest-config-missing", detail)
                continue
            self._edge(path, config, "pytest-config", rule)
            self._pytest_reader(config)
            if mode not in _REGULAR:
                self._unknown(path, "pytest-config-mode", detail)

    def _pytest_inputs(self):
        for scope in self.policy.pytest_scopes:
            for path in self.entries:
                if not path.endswith(b".py"):
                    continue
                if path not in scope.test_paths and (
                    path.rpartition(b"/")[2] == b"conftest.py"
                    or not any(_under(path, root) for root in scope.test_roots)
                ):
                    continue
                rule = f"pytest:{scope.name}"
                self._pytest_reader(path)
                self._pytest_fixtures(path, scope, rule)
                self._pytest_config(path, scope, rule)

    def _package_dependencies(self):
        for consumer, dependency, rule in self.policy.package_dependencies:
            if (
                self.entries.get(consumer) not in _REGULAR
                or self.entries.get(dependency) not in _REGULAR
            ):
                self._unknown(consumer, "package-dependency-endpoint", rule)
                continue
            self._edge(consumer, dependency, "package-dependency", rule)

    def build(self, digest):
        self._index_sources()
        self._pytest_inputs()
        self._package_dependencies()
        for path in sorted(self.sources):
            self._scan_source(path)
        for record in self.policy.incomplete_inputs:
            if record.possible_inputs is not None:
                record = replace(
                    record, possible_inputs=tuple(sorted(set(record.possible_inputs)))
                )
            self.unresolved.add(record)
        return Graph(
            snapshot_digest=self.snapshot.digest,
            policy_digest=digest,
            edges=tuple(
                Edge(consumer, dependency, kind, tuple(sorted(rules)))
                for (consumer, dependency, kind), rules in sorted(self.edges.items())
            ),
            unresolved=tuple(sorted(self.unresolved, key=_unresolved_key)),
        )


def build_graph(snapshot: Snapshot, provider_policy: ProviderPolicy) -> Graph:
    """Return exact endpoint dependencies and the inputs they could not establish."""
    digest = _policy_digest(provider_policy)
    return _GraphBuilder(snapshot, provider_policy).build(digest)
