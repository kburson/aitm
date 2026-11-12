# #141 leaf design · Derive Python and package edges

[Story #141](../story.md) · [Refined acceptance and sizing](../plan/2026-11-11-141-refinement.md) · [Accepted parent design §3](https://github.com/kburson/aitm/blob/2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9/.aitm/stories/001/133/design/test-impact-analysis-design.md#L70) · [Accepted T04](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L217-L229)

#142 needs a reproducible file-level dependency graph for each side of
an exact comparison. This leaf supplies Python import, package and
qualified pytest edges and exposes gaps in that graph. It adds
`tools/ci/tia/python_graph.py` and `tools/ci/tests/test_tia_python_graph.py`
in the existing implicit `tia` namespace. #142 owns runtime declarations,
inventory joins, graph traversal, test witnesses and selection or full
fallback. Qualified runner policy and its activation remain with the
owning caller and later leaves.

## Interface and authority

`build_graph(snapshot: Snapshot, provider_policy: ProviderPolicy) -> Graph`
consumes the delivered #140 snapshot. The caller constructs the same
independently reviewed policy for both snapshots. Inputs come from
`Snapshot.entries`, `Snapshot.read_content(path)`, and `Snapshot.digest`.
The builder reads bound source bytes and uses the standard-library AST
with Python's source encoding detection. It does not import or execute
candidate modules, evaluate candidate manifests, run collection, use
checkout contents, or inspect ambient module search paths. A failed
bound read propagates `SnapshotUncertain`. Unparseable or nonregular
Python entries yield unresolved records. Git modes `100644` and
`100755` are regular. A link's payload cannot establish its target's
dependencies.

| Value | Public fields and interpretation |
| --- | --- |
| `ProviderPolicy` | `import_roots` (tuple of repository directory byte paths, with `b""` for the root); `external_modules` (reviewed top-level module names); `pytest_scopes` (tuple of qualified scopes); `package_dependencies` (explicit `(consumer_path, input_path, rule)` tuples); `dynamic_import_bounds` (tuple of exact reader path and nonempty input-prefix tuple pairs); `incomplete_inputs` (tuple of `UnresolvedScope` records supplied by the reviewed policy for input classes the invocation cannot cover). The caller must supply the incomplete-input field explicitly. |
| `PytestScope` | `name` (stable rule name); `test_paths` (exact module paths); `test_roots` (directory prefixes for Python files in the invocation); `fixture_root` (inclusive cutoff directory, `b""` for repo root, `None` for unqualified); `config_paths` (tuple of required shared inputs, empty for a qualified empty set, `None` for unqualified). |
| `Graph` | `snapshot_digest`, `policy_digest`, `edges`, `unresolved`. Use immutable records and tuples. Bind the complete supplied policy values by SHA-256 over stable JSON with repository byte paths encoded reversibly. Bind snapshot identity to `Snapshot.digest`. |
| `Edge` | `consumer` and `input` as original repository byte paths; `kind` in `import`, `package-init`, `pytest-fixture`, `pytest-config`, `package-dependency`; `rules` (sorted distinct provenance IDs). Sort and deduplicate by `(consumer, input, kind)`. Static rules identify Python AST, fixture and config rules identify the invocation scope, and explicit package edges retain the reviewed rule. |
| `UnresolvedScope` | `reader` (repository byte path or `None` for a policy-wide input class); `reason` (stable code); `detail` (module, scope name or input class when applicable); `possible_inputs` (sorted distinct raw repository path prefixes or `None` for all applicable packages). Prefix matches require a whole path component. Sort and deduplicate records deterministically. |

Invalid or contradictory policy values refuse graph construction with
a `ValueError`. For example, an escaping prefix, empty bound, duplicate
scope name or multiple bounds for one reader cannot provide authority.
Scope bounds describe reachable **inputs** across package boundaries.
The graph uses a trusted bound only for a recognized dynamic import
from its exact reader. Ambiguity and unsupported syntax, source modes,
or fixture/plugin behavior remain unbounded unless their input class
has an independently reviewed policy record. Policy authors account
for runtime file I/O, subprocesses, external plugins, and other
unmodeled mechanisms when they supply incomplete-input records. #142
can interpret those classes with reviewed runtime declarations. The
graph does not establish completeness from a known edge.

## Python and package resolution

1. Index `.py` source entries under trusted import roots by relative
   dotted module name. A package initializer owns its package name.
   Use valid UTF-8 Python identifier components for indexing, and
   retain the original bytes in graph records. A Python path under a
   mapped root that cannot be indexed this way remains a scanned
   reader and records uncertainty. Represent initialized packages
   and implicit namespace directory candidates separately from
   ordinary modules. Resolve each import against the full candidate
   set. Multiple roots for a namespace or module and collisions
   between a module and package produce uncertainty, with all
   represented possible edges retained. A unique implicit namespace
   carries no synthetic file edge.
2. For `import a.b.c as alias`, add edges to applicable package
   initializers and the target source module. For
   `from a.b import item`, retain the base dependency and any local
   submodule named `a.b.item`. A missing from-list child may be a
   symbol, so the base dependency suffices when the base resolves.
   Resolve relative imports using the importer's mapped package
   context, including an initializer's own package. Unmapped,
   invalid or ambiguous relative context produces uncertainty.
   Resolve possible valid contexts to preserve their edges.
   Imports in initializers create ordinary downstream edges to
   re-export owners. Skip self-edges and preserve cycles across files.
   If an absolute target remains unresolved, a trusted external
   classification applies only where there is no local top-level
   candidate. Known prefix edges coexist with an unresolved target.
3. Walk all AST imports, including branches and function bodies.
   Conservatively flag references to `__import__` and the
   `importlib.import_module` or `builtins.__import__` loaders,
   including module aliases and `from` imports of the loader.
   Recognized dynamic imports produce `dynamic-import` records
   even when the argument is a literal. Recognizing loader
   references also covers simple assignment or passing the loader
   through another call. The provider does not infer arbitrary data
   flow, import hooks or dynamically modified paths. Reviewed
   incomplete-input records cover those mechanisms.
4. A trusted package dependency adds an explicit file-to-file edge
   when both named endpoints exist as regular entries. A missing
   or unsupported endpoint creates an unresolved record with
   its rule, even when another edge reaches the consumer. Static
   imports can cross roots without a separate declaration. Package
   input mapping comes from qualified policy, including any reviewed
   manifest dependency. This provider does not infer a dependency
   from a candidate's package metadata or a filename.

## Pytest fixture and configuration scopes

A scope applies by exact file membership or component-aware directory
membership. Treat its directory members at Python file granularity.
The inventory determines which node IDs actually belong to those
files. For each applicable test source, add edges to existing
`conftest.py` entries in ancestors from its directory through the
inclusive `fixture_root`. A cutoff that is unknown or outside that
test's ancestors creates fixture-scope uncertainty. A nested fixture
cannot apply to siblings. Scan attached fixtures, test modules and
qualified Python config inputs as readers even outside the import
roots. Their imports use the same resolver. When an applicable Python
reader has no usable module name under the trusted roots, record
unbounded `pytest-import-scope` uncertainty for that reader, including
when it has no relative imports. The invocation may have an unmapped
search directory. A nonregular fixture remains an observed input with
unresolved behavior.

Add one edge to each qualified `config_paths` input that exists in
the endpoint. The field covers shared invocation inputs such as
an explicitly supplied repo plugin. Missing or nonregular config,
an unqualified config set, or explicit `pytest_plugins` declarations
create unresolved records. Scope derives from the reviewed invocation,
including where it can load fixtures and configuration. Candidate
configuration and plugin declarations cannot qualify the invocation.
Qualified scopes for the same file accumulate edges and retain scope
provenance. Other runtime loading is outside this static provider and
is accounted for through the caller's incomplete-input records.

The pinned repository uses `packages/aitm-usage/src` for `aitm_usage`,
`tools/ci` for `tia` and top-level CI helpers, and reviewed pytest
import roots for test helpers. The product invocation includes
`packages/aitm-usage/tests/` and `tools/ci/tests/test_cli_evidence.py`,
with the product project configuration and the explicitly loaded
`pytest_evidence` plugin. Helper scope uses its own qualified
invocation. The file-lint project declares `package = false`.
These are baseline inputs for caller qualification and fixture design.
#141 supplies no active policy file or automatic invocation profile.
Known product tests already use `importlib.import_module`. Full-mode
fallback remains possible after the graph module is delivered.

## Acceptance evidence

- `test_import_alias_relative_reexport_cycle` asserts exact directed
  kinds through aliased imports, initializers, local from-list
  submodules, relative re-exports, and a cycle. It includes a
  cross-root dependency and verifies provenance and determinism.
- `test_dynamic_scope` asserts a known edge alongside bounded and
  unbounded dynamic readers, including module aliases and a
  from-import alias. Additional assertions cover ambiguous namespace
  roots, duplicate module ownership and a conflicting local candidate
  with a reviewed external name.
- Verify ancestor and nested fixture reachability, fixture helper
  imports, qualified config input, missing or unqualified config,
  an unmapped pytest reader with only absolute imports, plugin
  uncertainty, and the CLI test outside the product directory.
  Verify a reviewed package edge and missing endpoint disposition.
- Build a before/after graph with the real #140 resolver and a
  rename or deletion. Verify old and new edge sets and bound digest.
  Cover nonregular Python entries, source encoding, raw byte path
  identity, invalid syntax and propagated bound-read failure.
- Run focused behavior red/green and the related #139/#140 tests with
  the locked Python environment. Retain distinct #103 hosted proof for
  the exact candidate. The additions under `tools/ci/` are gate-defining
  at the inspected baseline. #103's four helper files define its
  coverage denominator and its hosted test list excludes this new file.
  Recheck the route and obtain exact-tree owner disposition and
  independent review through the existing delivery contract.

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_python_graph.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_python_graph.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py
```
