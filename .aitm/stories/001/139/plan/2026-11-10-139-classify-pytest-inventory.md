# #139 Classify the pytest inventory Implementation Plan

> **For agentic workers** Use Superpowers subagent-driven development or executing-plans after separate implementation authorization. Checkboxes describe the authorized attempt.

**Goal** Classify complete pytest collections into deterministic, scoped obligations and reconcile the full result against the delivered #138 comparison.

**Architecture** An offline classifier validates the complete policy-selected workload domain and combines bound collection components using reviewed test rules and supplied #103 policy. A private comparison harness exercises the same classifier against retained exact inputs with evidence kind preserved.

**Tech stack** Python 3.13.9, uv 0.10.6, locked pytest and Ruff, standard-library JSON and SHA-256.

**Spec** [Own #139 design](../design/2026-11-10-139-classify-pytest-inventory-design.md) · [Accepted #133 T02](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L187) · [JIT inputs](2026-11-10-139-jit.md)

## Global constraints

- Keep #103 authoritative. Work in an isolated branch after separate implementation authority. Preserve existing Python job targets, unrounded product and helper floors, optional skips, required child evidence, installed-wheel smoke, and exact PR-base comparison.
- Own `tools/ci/tia/inventory.py`, `tools/ci/tia/suites.json` and `tools/ci/tests/test_tia_inventory.py` only. Keep the implicit `tia` namespace and use the existing package toolchain. No workflow, observer, verifier, baseline, snapshot, package, protection or #158 changes.
- Retain private raw evidence in custody. Publish only sanitized provenance, counts and digests. The inventory is an offline projection, and its hosted source label only describes the verified input supplied by the trusted caller.

## Review focus

- A parameter may contain a slash, brackets, or platform name. The exact ID survives and capability still comes from the observed runner scope.
- A previously unseen file, missing required profile, duplicate node, wrong capability, incompatible role or incomplete collection holds the result. Full scope is determined by reviewed workload policy, independent of the rows observed.
- The console smoke node lives under CI tooling but runs with product and emits `cli-help`. Helper IDs remain separately owned, with hosted per-node results unavailable in the comparison.
- A valid optional capability skip retains its ID and exact reason. A deselection, unexpected skip, xfail, or omitted mandatory node cannot masquerade as complete collection.
- Local advisory and caller-verified hosted provenance cannot collapse to one identity even for equal rows. Focused hosted inputs are synthetic projection fixtures. Historical #103 evidence remains comparison input.

## Task 1 · Implement the classifier and approved policy

**Interface.** Export `classify(collection: bytes, suite_policy: SuitePolicy) -> Inventory`. `SuitePolicy` is a frozen record with `suites: bytes`, `ci103: bytes` and `workload: str`. The trusted caller selects the intended workload separately from collection bytes. `Inventory` is the canonical UTF-8 JSON bytes for `aitm.tia-inventory/v1`. Raise `ValueError` with a stable category for malformed input, scope or capability, collection, or policy mismatch.

| Record | Required fields |
| --- | --- |
| Normalized collection `aitm.tia-collection/v1` | `schema`, `binding`, `scopes`. Binding is `kind` (`local_advisory` or `hosted_collection_proof`), `repository` and `snapshot`. Local snapshot carries `content_digest`. Hosted snapshot carries `commit`, `tree`, `ref`, `run_id` and `run_attempt`. Validate the exact field shape for the kind. |
| Scope row | `profile`, `platform_scope`, `binding`, `runner`, `capabilities`, `observer`, `controls`, `receipt_sha256`, `exit_code`, `complete`, `deselected`, `items`, optional `source_reference`. The binding must equal the envelope binding. Comparison-only references carry original evidence kind, exact tree and receipt digest, plus run and attempt when present. Items carry `nodeid`, `disposition` (`collected` or `allowed_skip`) and `reason` only for the latter. Qualifying `hosted_collection_proof` is a T07/T08 responsibility. |
| Suite rules `aitm.tia-suite-policy/v1` | `schema`, `workloads`, `profiles`, `runners`, `modules`, `overrides`. Each workload defines `scope_status` and unique `required_pairs` of `[profile, platform_scope]`. Encode the four design workloads, with `full` alone marked `complete_workload`. Profiles `product-base`, `product-cli` and `ci-helpers` constrain applicable owner/targets, required capabilities and #103 obligations. Runner profiles name supported scope and required capabilities. Module rows carry owner, suite and isolation. Overrides are exact module/function selectors with suite, isolation, extra capabilities, mandatory CLI flag or child labels as applicable. |
| Inventory `aitm.tia-inventory/v1` | `schema`, `binding`, `workload`, `scope_status`, `suite_policy_sha256`, `ci103_policy_sha256`, ordered `scopes`, ordered `obligations`. Scope identities retain profile, platform scope, runner, capabilities, observer, controls, receipt and any source reference. Each obligation contains `provider`, `owner`, `profile`, `platform_scope`, `nodeid`, `suite`, `isolation_group`, `required_capabilities`, `mandatory`, `optional_skip_reason`, `required_children`, `disposition`. Its digest is SHA-256 of the full output bytes. |

- [ ] Add a valid small fixture in `test_tia_inventory.py` and the contract cases below. Import the public function as `from tia.inventory import classify`. Run the cases and retain red evidence at that public call before implementing the projection.

  | Test | Assertion |
  | --- | --- |
  | `test_classification_preserves_parametrized_platform_ids` | The same complete opaque parameterized ID under two explicit allowed scopes yields two sorted keys. A second parameter value stays distinct. Native APFS/ACL and process group labels come from reviewed rules. Changing receipt/provenance while retaining IDs changes the canonical digest. Reordering the input scope/item lists leaves the projected output stable when receipt identities are unchanged. |
  | `test_unclassified_or_duplicate_fails` | Parameterize one mutation at a time for an unknown module, duplicate node, repeated/missing/extra scope, missing required capability or node, malformed source path, overlap in policy, duplicate JSON key, nonzero exit, incomplete collection, deselection and unexpected skip/xfail. Each fails closed with a reason category. |
  | `test_ci103_scope_and_child_mapping` | Assert all six mandatory product IDs, the optional firmlink allowance and reason, exactly two required child labels in product-plus-CLI, product ownership of the installed CLI and helper ownership of all four helper targets. Base scope expects product only. An exact allowed skip retains its obligation. |
  | `test_full_inventory_requires_all_policy_pairs` | Under `full` the exact product/CLI and helper union is `complete_workload`. Removing the helper component fails even when the collection declares no missing data. A different-tree, other-attempt, advisory or comparison-replay component cannot fill a hosted full pair. Each reviewed comparison workload succeeds only as `comparison_component`. |
  | `test_hosted_and_advisory_preserve_distinct_provenance` | Equal obligations under a valid local advisory and a synthetic caller-verified hosted envelope yield distinct identity. Assert the exact hosted commit, tree, ref, run, attempt, observer, controls, runner and receipt survive. Missing hosted fields, advisory fields under hosted kind, unknown kind and conflicting component binding each fail without downgrade. This tests projection only. |

- [ ] Implement the strict parser and projection. Validate source path segments before matching exact module paths and the unparameterized function-qualified selector. Split the source at the first `::`, then find the parameter suffix in the opaque remainder for matching only. Refuse duplicate keys, unsupported schemas and non-finite JSON. Look up the workload in the supplied policy and require exact equality of its required pairs with the observed pairs after rejecting duplicates. Validate each component binding and profile before forming the union. Hash the actual supplied policy bytes. Serialize sorted object keys, compact separators, UTF-8, no ASCII escape conversion or trailing newline. Sort obligations by their complete tuple, scope rows by `(profile, platform_scope)`, and unordered metadata sets consistently. Keep the transformation free of filesystem reads and network calls.
- [ ] Encode the exact rules in the design in `suites.json`. Read the #103 required product IDs and optional allowance from the supplied existing policy. Cross-check the required child labels and their mapped tests, profile applicability, and capability declarations. Run the same focused tests to green.

## Task 2 · Reconcile evidence and verify delivery

- [ ] Validate the canonical #138 bytes against the JIT digest. Replay the 592 historical base IDs, both separate 630 product-plus-CLI roles and the 182 advisory helper IDs against their respective comparison workloads using exact IDs, roles and capabilities. Use the historical archived policy when applicable. Use local fixture observations for the three verified product roles with explicit `source_reference` kind `ci103_historical_replay`. Preserve the helper receipt separately with original `local_collect_only` reference and advisory binding. Never pass a #103 replay as a qualified hosted TIA collection. Compare exact row key sets back to each input, confirm equal PR/push IDs with distinct provenance, and check outcomes, mandatory cases, skip allowances and child labels against the original receipts. No hosted helper per-node outcomes are established.
- [ ] Reconcile the current 748 product-plus-CLI IDs from the pinned push using `compare-product-cli` with a local `ci103_current_replay` reference. Verify the four helper test source blobs and collection controls against the historical ones. In the clean exact pickup snapshot, run the two collect-only commands in JIT and call `classify` with workload `full` and both observed components under the same local snapshot binding. Compare the exact product/CLI and helper node sets separately with the pinned references and record the full local union. Treat any drift as a scoped discrepancy requiring a verified explanation. Save private raw outputs and a sanitized reconciliation of workload, scope, counts, hashes, ownership, suite totals and capability groups. Keep #103 hosted outcomes and coverage digests in the comparison evidence. The advisory full union carries no runtime outcomes or coverage.
- [ ] Run V(inventory), neighboring tests and Ruff from the physical source root. Run the current full local suite and documented required CI for exact delivery.

  ```sh
  PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked \
    pytest -q tools/ci/tests/test_tia_inventory.py
  PYTHONPATH="$PWD/tools/ci" uv run --project packages/aitm-usage --locked \
    pytest -q tools/ci/tests/test_tia_baseline.py tools/ci/tests/test_tia_snapshot.py
  uv run --project packages/aitm-usage --locked ruff check \
    --config packages/aitm-usage/pyproject.toml tools/ci
  uv run --project packages/aitm-usage --locked ruff format --check \
    --config packages/aitm-usage/pyproject.toml tools/ci
  ```

- [ ] Commit the three owned files only. Retain exact-head local Test, independent source review and same-attempt #103 hosted proof. The verifier treats additions under `tools/ci/` as changed controls. Obtain the applicable exact tested-tree disposition through the existing authority before the trusted-target verifier, then follow the normal delivery and Close requirements when authorized.

Estimate **3.5 implementation agent-hours**. Classifier, policy and focused red/green 2h. Exact reconciliation and local checks 1h. Evidence packaging and handoff 0.5h. Review, approvals and hosted queue are separate. Return to refinement if work would exceed four implementation agent-hours or if the baseline comparison cannot be reconstructed from verified evidence.
