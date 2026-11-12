# #147 gate changes and inventory dispositions implementation plan

> **For agentic workers** The Wave 30 owning agent uses `executing-plans` and behavior red/green after independent acceptance of this plan and its [JIT](2026-11-11-147-jit.md), followed by live Develop authority.

**Goal** Bind a full-validation requirement to exact changed controls and reconstruct the applicable obligation inventory through reviewed protected-target transitions.

**Architecture** Reuse the hosted Git snapshot and #103 gate path logic. Match independently authenticated records to exact source, policy and lane identities. Replay scoped deltas over canonical T02 inventory and retain a distinct comparison envelope.

**Tech stack** Python 3.13.9, uv 0.10.6, standard library, pytest, and the existing #103 CI delivery route.

**Spec** [Accepted leaf design](../design/2026-11-11-147-bind-gate-changes-design.md), [refinement](2026-11-11-147-refinement.md), [accepted T10](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L320).

## Constraints and files

- Create `tools/ci/tia/controls.py` for the two offline functions and their immutable evidence records. Create `tools/ci/tests/test_tia_controls.py` for focused tests. Use the existing implicit namespace and leave T02, T03, #103 and live workflow or policy files as input only.
- Qualified caller inputs come from reviewed code outside candidate execution. Every known changed control needs full validation and exact owner disposition and independent review. Full execution, observation custody, eligibility and merge decisions stay with the existing or downstream gate owners.
- Retain 3.5 implementation agent-hours, including local validation. At 2.5h require working and focused passing core control and complete-lane replay, with the refusal and regression checks underway. Return to refinement if delivery requires a new authority feed, durable store, CI integration, a change outside the two-file write set, or more than four implementation agent-hours.

## Review focus

- A raw-byte control path or a move across the classifier boundary preserves both exact identities. An ordinary module alongside a nested configuration file does not qualify as a control. Task 1 tests both.
- A matching tested tree string from one approver cannot substitute for either actor's exact decision. Wrong source, policy or lane data cannot be reused. Task 1 tests missing, same-actor and replayed dispositions.
- A valid review or unchanged assertion for one lane cannot cover the full workload. Task 2 tests wrong delivery and review coverage with an otherwise correct row digest.
- A net-zero replay still requires an independent path and one proof per delivered step. Task 2 tests omitted, reordered, repeated and wrong-step evidence.
- The last row from a fixed CI-helper target is a required obligation even if its individual row has `mandatory: false`. Task 2 tests this along with mandatory, child, capability and skip protections.

## Task 1 — Qualify the exact control diff

**Consumes** Two corresponding hosted `Snapshot` instances from `tia.snapshot.resolve`, trusted target and workflow metadata, and existing accepted owner and review records. Reuse `verify_pr.gate_controls` from the trusted version.

**Produces** `qualify_controls(base: Snapshot, candidate: ControlCandidate, approvals: ControlApprovals) -> ControlDisposition`.

- `Lane` carries profile, owner, platform, immutable runner key/value pairs and capabilities. `Scope` binds the workload, canonically ordered lanes, suite policy SHA-256 and CI policy SHA-256. Require unique lane profile/platform keys and canonical equality independent of input ordering.
- `ControlCandidate` carries the after snapshot, trusted target ref, canonical workflow ID and `Scope`. The `ControlBinding` contains repository, target and source refs, base and tested Git endpoints, PR head if applicable, scope, control projection digests and control delta digest. The canonical PR merge ref encodes the PR number. The decision records carry actor identity, evidence identity and that exact binding. `ControlApprovals` has separate owner and reviewer fields. The caller establishes actor authority, independence from the author, and current status. Distinct owner and review identities are required when both approvals are needed.
- `ControlDisposition` exposes binding, the immutable exact change records, full requirement and hold reason. Keep workflow ID and exact run/attempt plus applicable approval references with the result. If the source and scope stay fixed across a rerun, the same applicable source dispositions may be recognized. The result carries the new run attempt and independently qualified execution still has to match it.

- [ ] Add `test_control_edit_requires_full_and_independent_disposition` using a temporary Git history and actual hosted T03 resolver. Assert a product-only change is clear. Assert a workflow, policy, verifier, selector or nested `conftest.py` change holds and requires full without either approval. Assert exact distinct decisions clear the hold and retain full. Exercise a same-directory ordinary product file as the negative nested classifier case.
- [ ] Add parameterized assertions for old/new raw-byte rename across the control boundary, addition, removal, executable mode and type change, and candidate edit of the classification policy. Verify both change endpoints and distinct fingerprints. Exercise wrong repository, target, baseline, PR/head, tested endpoint, policy/scope and diff digests, same actor or record, missing decision, contradictory pair, and advisory snapshot. Keep the classification policy's existing effect for the candidate comparison.
- [ ] Run the focused assertions red. A missing module or symbol establishes absent implementation initially. Use the specific behavior assertions to check subsequent slices, including approval holds and the classifier boundary, before writing their behavior.
- [ ] Implement the trusted pair check and finite projection in `controls.py`. Match hosted provenance, endpoint roles, repository, exact base/tested endpoint, changes, and provider source ref. Feed surrogate-escaped paths to the legacy predicate and recover original bytes for identity. Include the design's exact non-root basenames using the trusted `CI_CONFIG_NAMES` set at the pinned verifier. Bind versioned, sorted projection and delta records with reversible path bytes and file modes, types and object IDs. Match approvals against the computed binding. A valid empty diff adds no T10 full requirement. An invalid comparison holds.
- [ ] Run the focused control cases green.

## Task 2 — Replay complete inventory dispositions

**Consumes** A trusted reference receipt, original T02 inventory, independently enumerated protected-target lineage and reviewed row deltas. The caller acquires exact approval and delivery records from the existing trusted procedure.

**Produces** `applicable_inventory(reference: QualifiedReference, target: InventoryTarget, dispositions: tuple[InventoryStep, ...]) -> Inventory`. Failures raise `InventoryHold` with a stable reason and no partial output.

- `QualifiedReference` carries original bytes, expected raw digest, verified receipt identity, expected anchor and complete lanes. `InventoryPoint` carries a Git endpoint, suite/CI policy digests and complete canonical obligation digest. `InventoryTarget` carries repository/ref, workload, target point, complete lanes and independently ordered points including anchor and target. A single-point path is valid at the exact anchor.
- `InventoryStep` carries before and after points, an ordered tuple of complete canonical before/after rows with absence explicit, verified delivery evidence and applicable independent review evidence. Each evidence record identifies its authority record and carries the exact binding with repository, ref, workload, complete lanes, both points and the row-delta digest. The caller verifies the reviewed-source to actual-target mapping and checks that an unchanged statement was positively established. Equal row and policy digests and an explicit empty delta are required to use that unchanged route.
- Read T02's original canonical v1 bytes and keep the full reference intact. Use its row identity order `(provider, owner, platform_scope, nodeid)`. Keep the complete, independently expected full-workload lane set across anchor, target, replay records and both evidence types. Match v1 scope pairs, runner identity and capabilities, and ensure each obligation's profile/platform and owner correspond to exactly one expected lane. Apply sorted, unique full-row deltas, check the complete prior and resulting row digest at each point, and compare the final result to the independently expected target. Require one step per adjacent expected revision and reject repeats, gaps and unbound or wrong delivery. Policy changes require reviewed coverage even if rows are equal.
- Preserve mandatory rows, child proof and capability requirements, existing skip constraints, and at least one case in each required CI-helper source target of the qualified reference. The T02 full projection already verifies its helper target set. Compare replacement fields on the full stable row. Permit no newly skipped, deselected or xfailed row, newly granted skip permission, or relaxed existing permission. Keep an unchanged preapproved collection skip as data with no implication for runtime outcomes. Treat any unsupported row state or missing lane as a hold.

- [ ] Add `test_reference_inventory_requires_intervening_dispositions` with the actual T02 classifier, reviewed policy and synthetic trusted hosted full collection. Start A with product and helper lanes, replay an explicitly unchanged A → B and an exactly reviewed B → C optional addition or policy-consistent semantic replacement. Assert the complete C obligations, A's actual collection and receipt, canonical derived schema and order, and C's separate target identity. Exercise the exact same-anchor comparison.
- [ ] Add parameterized refusals for missing, reordered, duplicate or conflicting steps, wrong delivery, missing independent review, net-zero omitted history, mismatched points/digests/policy, wrong predecessor row, incomplete or wrong-scope lane evidence, missing reference lane, advisory/partial/derived reference, wrong reference digest, invalid key or disposition, new skip permission or weakening a mandatory, child, capability or required helper obligation.
- [ ] Run the inventory assertions red. Implement the minimum deterministic replay in `controls.py` and emit canonical `aitm.tia-applicable-inventory/v1` bytes, with original reference content and raw digest, custody identity, exact target and replay evidence. Verify green. The output supplies applicable comparison rows only. Later qualification still independently establishes actual collection and required outcomes.

## Task 3 — Verify and hand off the exact candidate

- [ ] Run the focused file in locked Python 3.13.9 and collect its node IDs. Run the related T02, T03 and #103 verifier tests, then Ruff check and format check using the locked package config. Keep the red results, final counts, environment and source identity attributable to this attempt. Use the approved commands in the [JIT](2026-11-11-147-jit.md).
- [ ] Confirm that the diff adds only the owned files, check whitespace, and commit locally as `[#147] Bind gate changes and inventory dispositions`. Report the exact local commit and tree to the delivery coordinator. Repeat exact verification if the effective source changes.
- [ ] The delivery coordinator runs the [manual delivery checklist](../../../../manual-delivery-checklist.md). The current gate treats both additions as control changes. The coordinator obtains the existing owner's disposition for the exact tested tree, all required hosted checks, the trusted verifier receipt, and an independent exact-source verdict before normal merge. Keep current candidate evidence, verified delivery mapping and implementer retrospective distinct.
