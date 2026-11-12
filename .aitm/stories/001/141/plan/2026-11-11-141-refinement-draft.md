# #141 Derive Python and package edges

**Refinement draft · Wave 3, Rank 30 · P1 · 3.5 implementation agent-hours.**
The draft is for leaf design review. Accepted requirements, the leaf plan,
JIT and implementation authorization are separate pickup gates.
[Story #141](../story.md) · [Accepted T04 at publication](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L217-L229) · [Accepted #133 design, §3](https://github.com/kburson/aitm/blob/2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9/.aitm/stories/001/133/design/test-impact-analysis-design.md#L70)

Given one exact source snapshot, build the Python and pytest dependency
edges and report what the provider could not resolve. This gives #142
the inputs to explain impact on exact tests across the before and after
snapshots, including cases where it must use the full suite.

## Delivered inputs

Source inspection pinned `trunk` at
`56266ed30bbc572b7e56bc64777e802be264c23f`. The T04 section matches
the story's recorded SHA-256
`8834c6ab0466869c48e118e34b3064ff1ef86a362aaecc5e4db66a6f6c0b6165`.

| Predecessor | Delivered contract and proof |
| --- | --- |
| #139 · T02 | `classify(collection: bytes, suite_policy: SuitePolicy) -> Inventory` emits canonical `aitm.tia-inventory/v1` bytes. Obligations retain `(provider, owner, platform_scope, nodeid)`, collection source, workload and policy digests. The CLI obligation is product-owned despite its location in `tools/ci/tests`. #141 uses the reviewed ownership and scope as policy inputs. #142 joins graph source paths to the full obligation identities. PR #197 delivered at the pinned revision with exact-tree workflow and 47 focused tests. [Source](https://github.com/kburson/aitm/blob/56266ed30bbc572b7e56bc64777e802be264c23f/tools/ci/tia/inventory.py#L631) · [Delivery](../../139/plan/delivery-receipt.json) · [Close](../../139/plan/closure-receipt.json) |
| #140 · T03 | `resolve(repo, request) -> tuple[Snapshot, Snapshot]` supplies before and after snapshots or raises `SnapshotUncertain`. Use each snapshot's complete `entries`, `read_content(path: bytes) -> bytes`, and `digest`. `changes` preserves old and new endpoints for #142. Hosted reads come from bound Git objects and effective local content is advisory. PR #184 delivered at `a495d60a87ac4ca764f019dc266e579f13f1787e`, an ancestor of the pinned revision. [Source](https://github.com/kburson/aitm/blob/56266ed30bbc572b7e56bc64777e802be264c23f/tools/ci/tia/snapshot.py#L164-L200) · [Delivery](../../140/plan/delivery-receipt.json) · [Close](../../140/plan/closure-receipt.json) |

## Contract to refine

Keep the accepted `build_graph(snapshot, provider_policy) -> Graph`
interface. The proposed result binds the snapshot digest and reviewed
policy digest and contains deterministically ordered, deduplicated
`(consumer_path, input_path, kind)` edges and unresolved scope records.
Keep repository paths as raw bytes and use reversible encoding if a
later boundary serializes them. Stable edge kinds distinguish imports,
package initialization, pytest fixtures, configuration and any explicit
package dependency represented by approved mapping. Retain the
scope rule or source of the edge so #142 can cite it. Cycles remain
in the graph. Reverse traversal, witness choice and deduplication of
test obligations belong to #142.

- Read source by exact snapshot entry. Parse regular Python bytes with
  the standard-library AST, preserving Python source encoding handling.
  Build both endpoint graphs separately. Propagate failed bound reads
  as `SnapshotUncertain` so an unavailable graph cannot appear complete.
  Record unsupported source modes, parse failures and ambiguous
  module ownership as unresolved. A symlink's recorded bytes do not
  establish its target's import behavior.
- Resolve absolute, aliased and relative imports against an explicit
  import-root and ownership map from the trusted caller. Preserve
  package initializers along an import chain. For
  `from package import name`, retain the package edge and a local
  submodule edge when applicable. Imports inside initializers create
  ordinary source edges to re-export owners. Keep ambiguous namespace
  roots and module/package collisions explicit. A reviewed external
  classification applies only after checking for possible local
  ownership. Current mapping inputs include
  `packages/aitm-usage/src` for `aitm_usage`, `tools/ci` for the
  implicit `tia` namespace and top-level CI helpers, and the approved
  test roots. Resolve cross-package imports wherever the trusted map
  establishes ownership. The pinned `tools/ci/file-lint` project
  declares `package = false`.
- Map applicable test files to ancestor `conftest.py` and trusted
  pytest configuration paths under the qualified invocation scope.
  Include imports made by fixture and helper files. Keep nested
  fixture reachability scoped to applicable tests and use the
  reviewed profile for shared configuration. Candidate file contents
  can supply evidence of dependencies. Scope and completeness come
  from the caller's trusted policy, including any fixture or config
  cutoffs. Candidate configuration, plugin discovery and collection
  do not establish that policy.
- An unresolved record identifies the reader or input class, the
  reason, and possible input reach across packages. An unbounded
  scope means all applicable packages. The initial provider should
  record recognized dynamic imports and unsupported fixture/plugin
  loading conservatively. Uncovered runtime input classes stay
  visible even if the scanner found a definite edge from another
  reader. The pinned tree already uses `importlib.import_module` in
  product tests, so a correct graph may still require full fallback.
  #142 applies reviewed runtime declarations and decides whether
  unresolved scope intersects a changed input.

## Ownership and integration

- Own `tools/ci/tia/python_graph.py` and
  `tools/ci/tests/test_tia_python_graph.py`. Use the existing implicit
  `tia` namespace. The proposed policy type lives with the graph
  provider and takes qualified inputs from the caller. Confirm its
  minimum fields, the approved import/config scope and the handoff
  to #142 in leaf design review.
- #142 owns `selection.py`, `edges.json`, declarations for subprocesses
  and other runtime inputs, inventory joins, old/new reverse traversal,
  witnesses and fallback. #144 owns trusted-observation qualification.
  #147 owns control and inventory dispositions. #158's bounded
  merge-route refusal belongs to #159's dependency path. The three
  Rank 30 drafts can proceed with their own predecessor evidence.
- Keep scope within the two owned files. Current #103 executes four
  named helper test files and computes gated helper coverage from the
  policy's four targets. Retain a separate focused run for the graph
  module, and preserve required #103 validation, exact-base comparison
  and evidence. The pinned verifier classifies additions under
  `tools/ci/` as gate-defining. Recheck at JIT and obtain the applicable
  exact-tree owner disposition and independent review through the
  existing delivery route. [Verifier](https://github.com/kburson/aitm/blob/56266ed30bbc572b7e56bc64777e802be264c23f/tools/ci/verify_pr.py#L495-L511) · [Workflow](https://github.com/kburson/aitm/blob/56266ed30bbc572b7e56bc64777e802be264c23f/.github/workflows/ci.yml#L194-L202) · [Delivery checklist](../../../../manual-delivery-checklist.md)

## Proposed acceptance and verification

| Check | Required observation |
| --- | --- |
| `test_import_alias_relative_reexport_cycle` | A test imports a package symbol with an alias, an initializer imports its implementation with a relative import, and the implementation imports back through the package. Assert the exact directed edges and kinds, including the initializer and actual module owner. Include a fixture import from another mapped package or CI root. Assert deterministic results and preservation of the cycle. |
| `test_dynamic_scope` | Keep a known static edge while an aliased `import_module` or `__import__` uses a computed name. Assert the unknown reader, reason and cross-package reach. Exercise both a policy-bounded and an unbounded scope. An ambiguous namespace or duplicate module owner must retain uncertainty even with another known edge. |
| Qualified pytest scope | A test inside a nested fixture scope has edges to its applicable ancestor fixtures and configuration. A sibling outside the nested scope keeps only its own applicable edges. An unqualified or ambiguous config scope records uncertainty. A fixture helper remains reachable through the fixture's import edge. Include the product-owned CLI test location when checking the CI/product ownership boundary. |
| Snapshot binding and unavailable inputs | Build two graphs through #140's real public `resolve` API. A rename or deletion leaves the former importer edge visible on the old graph and uses the new endpoint's bytes for the new graph. Assert distinct endpoint digests. Exercise a syntax error, a non-regular Python entry and a failed bound read. The first two produce scoped uncertainty and the failed read makes the graph unavailable. |

Run V(python_graph) from the physical root with the namespace on the
module path. Capture expected behavior failures before implementing,
then retain passing focused, related and normal exact-candidate
validation. An import or collection failure provides no red case.

```bash
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_python_graph.py
PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked python -m pytest -q tools/ci/tests/test_tia_python_graph.py tools/ci/tests/test_tia_inventory.py tools/ci/tests/test_tia_snapshot.py
```

## Estimate

The 3.5-hour implementation estimate is credible but tight for the two
owned files with a fixed, reviewed policy and conservative uncertainty.
Allow 1.5 hours for exact source reads, module indexing and AST edges,
0.75 hours for pytest and unknown scopes, 0.75 hours for focused fixtures
and red/green, and 0.5 hours for integration and evidence. External
approval and queue time are separate. Recheck at JIT. If supporting the
required pytest scope needs new collection or policy machinery, or
implementing the accepted behavior exceeds four agent-hours, return
the leaf for decomposition before Develop.
