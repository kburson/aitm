# #141 Python and package edges implementation plan

> For agentic workers, use the executing-plans and test-driven-development skills after the authorized Develop pickup. Checkboxes record implementation progress.

**Goal** Build a snapshot-bound file dependency graph with qualified Python and pytest edges and explicit uncertainty.

**Architecture** Index possible Python import owners from the snapshot and trusted search roots. Walk bound source ASTs, combine static and qualified pytest/package edges, and return a sorted immutable graph with input reach and provenance for #142.

**Tech stack** Python 3.13.9 standard library, locked uv, pytest and Ruff.

**Spec** [Accepted leaf design](../design/derive-python-package-edges-design.md), SHA-256 `0f10b0e978208480b39b304c9e513019e2f603bb1358a0b8738eff75f817d438`. [T04 parent plan](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L217-L229).

## Constraints and ownership

- Create `tools/ci/tia/python_graph.py` and `tools/ci/tests/test_tia_python_graph.py` only. Reuse `tia.snapshot` and the implicit namespace. Keep graph records independent of test node IDs and workflow authority.
- Read only `Snapshot.entries`, `Snapshot.read_content` and `Snapshot.digest`. Keep raw repository paths, bind snapshot and policy identities, and preserve incomplete inputs alongside positive edges.
- Treat a valid caller policy as reviewed authority. Candidate source may contribute AST evidence. Candidate metadata, environment, collection, Python execution and filesystem discovery cannot supply policy or graph inputs.
- Review and delivery use the [companion JIT](2026-11-11-141-jit.md). #142 owns selection, runtime declarations and witnesses. No workflow, package configuration, runner, policy or live selection change is part of T04.

## Review focus

- A known edge and a computed import or ambiguous namespace can coexist. Retain every represented candidate and the uncertainty.
- A trusted external name can be shadowed by a candidate local module or namespace. Examine local ownership first and preserve known prefix edges for an unresolved full name.
- A fixture, CLI test, or qualified Python input may sit outside the package's import root. Scan it as a reader and keep an unqualified search or config scope visible.
- A moved source may be reachable only in the old graph. Build both from the real resolver; bytes unavailable at the bound reader cause a refusal.
- Source encodings, nonregular entries and original byte paths must survive the provider boundary without guessing an owner.

## Task 1. Deliver the snapshot-bound Python graph

### Interface

Use the public frozen dataclasses and field names from the design.
`build_graph(snapshot: Snapshot, provider_policy: ProviderPolicy) -> Graph`
consumes one endpoint and exposes `Graph.snapshot_digest`,
`Graph.policy_digest`, `Graph.edges`, and `Graph.unresolved`.
Each edge carries `consumer`, `input`, `kind`, and `rules`. Each
unresolved record carries `reader`, `reason`, `detail`, and
`possible_inputs`. Use `""` for inapplicable detail and `None` for
unbounded possible inputs. Use the complete supplied policy record for
its digest, with stable JSON keys and reversible hex encoding of byte
paths. Keep declaration and input-scope prefix comparisons component-aware.

### Tests and expected observations

- [ ] Add tests with an in-memory snapshot fixture for the static and error cases. Use real `Snapshot` values where convenient and a fixture with the same three-read interface for synthetic paths. Test through `build_graph` and compare public records.
- [ ] Add `test_import_alias_relative_reexport_cycle` using `app/pkg/__init__.py` with `from .worker import exported`, `app/pkg/worker.py` with `import pkg as p`, `lib/other/__init__.py` and `lib/other/helper.py`, and `tests/test_example.py` with `from pkg import exported as use`, `from pkg import worker as w`, and `import other.helper as helper`. Assert exact `package-init` edges from the test to the two initializers, `import` edges from the test to worker and helper, `import` from pkg initializer to worker, and `package-init` from worker to pkg initializer. Assert no unresolved records for the fixture, stable rules and repeat graph equality.
- [ ] Add `test_dynamic_scope` with a recognized aliased module loader, an imported loader alias, and an ordinary local import. Assert the ordinary edge remains and the two loader readers have distinct `dynamic-import` records, with a bound tuple for one reader and `None` for the other. Include an uncovered runtime class from policy. Add `test_ambiguous_owners_keep_possible_edges` with multiple namespace roots, duplicate owners, a module/package collision and an approved external top-level name which has a local owner. Assert the possible edges, stable ambiguity reasons and uncertainty for the missing local submodule. Add an invalid or multiply mapped relative context case and require it to remain unresolved.
- [ ] Add `test_pytest_scope_keeps_fixture_config_and_search_evidence` with nested and sibling tests, an ancestor and a nested `conftest.py`, a fixture import across roots and an explicit CLI test in `tools/ci/tests/test_cli_evidence.py`. Compare exact fixture and config edges and assert `pytest-import-scope` for an applicable absolute-only reader with no usable module name. Assert missing/unqualified config or cutoff and plugin declarations produce unresolved records. Cover a file with two qualified scopes and require one shared edge with both rule names. Cover a reviewed `package-dependency` edge and its unresolved form with a missing endpoint.
- [ ] Add `test_graph_binds_real_snapshot_pair` with an isolated Git fixture and public `resolve`, using the supported Git executable/profile from the T03 tests. Commit a fixture with `src/old.py` and a mapped consumer; move it to `src/new.py` and update the consumer. Check distinct snapshot digests and the old vs new edge. Add `test_invalid_source_retains_uncertainty` for a valid encoded source, a raw non-UTF-8 repository path, invalid syntax and a nonregular source. Add `test_bound_read_failure_refuses_graph` to inject a `SnapshotUncertain` on a regular source read and require that exact exception to propagate. Test malformed and duplicate policy inputs as `ValueError`.
- [ ] Run the focused test before adding graph behavior. If the test needs a collection-safe interface scaffold, declare only the public records and an empty graph result for the red run. Retain a named expected edge or uncertainty assertion failure rather than an import or setup failure.

### Build

- [ ] Add the typed immutable records, validated policy fields and stable policy SHA-256. Index ordinary modules, initializers and implicit namespace directories per trusted root. Retain every candidate with its original path and the importing reader's possible package contexts. Mark an unindexable Python path unresolved while still scanning it as a reader.
- [ ] Parse regular eligible source with `ast.parse` on bound bytes. Resolve `ast.Import` and `ast.ImportFrom` along dotted prefixes and relative contexts. Distinguish `package-init` from `import`, omit self-edges, keep cycles and report unresolved or ambiguous names alongside their known edges. Apply approved external names only after local ownership checks. Scan AST references to the recognized dynamic loaders and `pytest_plugins`. Carry a reviewed dynamic reader bound only on its own dynamic-import record.
- [ ] Determine applicable pytest files by exact path or directory prefix. Attach ancestor `conftest.py` through the fixture cutoff and required config inputs. Scan attached Python inputs outside import roots and mark their unmapped names with `pytest-import-scope`. Record unknown or unsupported fixture/config and missing/unsupported package-dependency endpoints. Include reviewed incomplete input classes. Merge repeated rule names under one edge key and return ordered records.
- [ ] Run the focused collection, focused suite, related T02/T03 suites, Ruff lint and format checks below. Keep local outputs with the exact tree and runtime. Record the behavior-red assertion and the passing tests separately. Verify the two-file write set and commit scoped source locally. Send the clean head/tree and proof to the wave owner for Test, hosted checks, independent source review and delivery.

```bash
export PYTHONPATH="$PWD/tools/ci"
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest --collect-only -q tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 python -m pytest -q tools/ci/tests/test_tia_python_graph.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py
uv run --project packages/aitm-usage --locked --python 3.13.9 ruff check --config packages/aitm-usage/pyproject.toml tools/ci/tia/python_graph.py tools/ci/tests/test_tia_python_graph.py
uv run --project packages/aitm-usage --locked --python 3.13.9 ruff format --check --config packages/aitm-usage/pyproject.toml tools/ci/tia/python_graph.py tools/ci/tests/test_tia_python_graph.py
git diff --check
```

Expected local outcomes are exact collection IDs, passing focused and
related tests, successful Ruff checks and only the two owned paths
in the commit. Hosted outcomes are independently verified under #103
on the applicable base and exact PR head/tree. Hosted #103's four-helper
test list excludes the new focused file and its coverage denominator
excludes the graph module.
