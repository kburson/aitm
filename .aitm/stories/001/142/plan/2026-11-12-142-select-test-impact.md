# #142 selector implementation plan

> For agentic workers. Use `executing-plans` and `test-driven-development` after the exact Plan and JIT are accepted and the owner-authorized Develop attempt is recorded.

**Goal.** Use exact source and inventory evidence to select affected tests, explain each changed path, and choose the complete applicable inventory when impact is uncertain.

**Architecture.** Bind delivered T02 inventory and T03 snapshot evidence, derive the two T04 graphs, add the reviewed declarations, traverse each graph in reverse, and join exact keys across before and after. Publish deterministic selections, witnesses and fallback reasons. Use locked Python 3.13.9, uv 0.10.6 and the existing TIA namespace.

**Spec.** [Accepted leaf design](../design/2026-11-12-142-select-test-impact-design.md) and [refinement](2026-11-12-142-refinement.md). The [parent T05 plan](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L231) defines the leaf and its downstream boundaries.

## Scope and checkpoints

Create `tools/ci/tia/selection.py`, `tools/ci/tia/edges.json`, and `tools/ci/tests/test_tia_selection.py`. Use the upstream modules without changing them. The 4-hour implementation estimate includes focused verification. At 2.75 implementation agent-hours require passing input and traversal slices with fallback tests underway. Return to refinement if the work needs a new authority or collection route, an additional provider or changes outside the owned files. Keep external review and CI waits separate.

## 1. Bind inputs and expose the result

- [ ] Define `InventoryPair(before: bytes | None, after: bytes | None)`, an `InventoryExpectation` for each endpoint's expected original inventory digest, full T02 `SuitePolicy`, exact lane identities and optional hosted collection tuple, and `SelectionPolicy` containing both expectations, reviewed provider policy and manifest bytes. Expose `select(before, after, inventory, policy) -> Selection`, with immutable exact obligation keys, source identities, dispositions, witnesses, removed keys and result mode.
- [ ] Write behavior tests with independently bound base and candidate collections. Reject stale candidate ref/run/attempt, wrong raw inventory digest, policy/runner drift and incomplete mandatory rows with `unavailable` and no executable keys. A valid candidate paired with a bad before expectation yields `full` with every candidate key. Use distinct local snapshot digests and assert advisory provenance. Exercise both hosted T03 roles.
- [ ] Run the tests red against a collection-safe scaffold. Implement candidate-only validation first, then pair validation. Use the delivered T02 canonical parser and policy/obligation projection to validate scope and all complete rows, and the T03 roles, endpoint membership and original change tuples. Derive no custody from caller-shaped data. Retain verified deletion evidence even when a required candidate key is missing. Verify green.

## 2. Add reviewed declarations and trace both graphs

- [ ] Add a strict `aitm.tia-edges/v1` JSON document with `edges` and `path_rules` arrays. Edge rows carry `id`, `consumer`, `input`, `kind`, and `rationale`. Rule rows carry `id`, exact `path`, `kind` (`non-test` or `shared-input`), and `rationale`. Require exact relative UTF-8 paths and unambiguous IDs, endpoint and rule combinations. Leave the production non-test rules empty until reviewed evidence supports a path.
- [ ] Declare two traced relationships. Use `runtime-file` from `packages/aitm-usage/src/aitm_usage/pricing.py` to `packages/aitm-usage/src/aitm_usage/rates/monitor/2026-11-10.json` because the default monitor loader reads it. Use `subprocess` from `tools/ci/tests/test_cli_evidence.py` to `packages/aitm-usage/src/aitm_usage/cli.py` because the smoke test launches the console entry point pinned in `packages/aitm-usage/pyproject.toml`.
- [ ] Write `test_renamed_module_selects_former_consumer`, `test_direct_and_multihop_exact_witnesses`, and `test_cross_package_declared_subprocess_path`. Assert byte-exact original paths, stable key and edge kinds, old and new sides, deduplication through cycles, stable shortest-path ties, fixture hops, and before-only keys that cannot become surviving witnesses. Run red, then derive T04 graphs and append validated per-side declared edges. Reverse-walk in stable order and join that side's inventory. Verify green.

## 3. Decide mode and record the reasons

- [ ] Write `test_known_edge_plus_unbounded_reader_runs_full` and `test_changed_test_and_non_test_disposition`. Assert all-lane fallback with an existing witness, a bounded unknown or missing declaration endpoint reached after a valid hop, and no fallback for an unrelated bounded unknown. Verify changed/new/mandatory keys, shared inputs, arbitrary name matches, and exact positive non-test classification. For a genuine docs-only projection keep mandatory keys. Exercise `no-tests` through the focused decision fixture with no mandatory or new keys.
- [ ] Test an unchanged-policy missing required row, a verified removal under different endpoint policies, and a same-key metadata or allowed-skip disposition change. Expect unavailable on the first case, and full with exact removed or changed keys on the latter two. Preserve allowed-skip obligations and leave runtime evidence and inventory disposition to the downstream gate.
- [ ] Run red, then implement per-path dispositions, full fallback and unavailable handling. Keep the ordinary dependency witnesses and the applicable scope reasons, and record the exact suite and graph inputs in the result. Verify green.

## 4. Verify the three-file candidate

- [ ] Run the locked focused and related pytest commands in the [JIT](2026-11-12-142-jit.md). Use genuine T02/T03/T04 records in representative integration tests. Run Ruff lint and format, verify manifest parsing and diff whitespace, then record exact tree, focused IDs and observed counts.
- [ ] Hand off to the [manual delivery checklist](../../../../manual-delivery-checklist.md). The focused tests and three-file source diff are separate from the current hosted helper suite. Require the exact six-job #103 run, authenticated evidence, owner-delegated disposition, trusted verifier and independent PR SAR or XPR before delivery.
