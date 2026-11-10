# Test impact analysis and Stop the Line implementation plan

> **For agentic workers** Use `subagent-driven-development` or
> `executing-plans` after implementation authorization. Each checkbox
> describes future work on the named leaf.

**Goal** Deliver explainable Python test selection, verified sharded
full-suite execution, and a qualified Stop the Line recovery path.

**Architecture** A trusted planner binds Git snapshots and pytest
obligations to a test plan. A trusted controller and collector prove
execution on named hosted runners. A separate authority governs
scheduled trunk health, conditional merges, repair, and the workspace
restart barrier. Qualify control changes in isolation before adoption.

**Tech stack** Python 3.13, the repository's locked uv, pytest, coverage.py
and Ruff, GitHub Actions, Git, and standard-library SQLite on a single
trusted authority host. The current #103 workflow uses Python 3.13.9,
uv 0.10.6 and qualified macOS/APFS. Re-pin the live qualified versions
at JIT. Additional isolation primitives require the T07 evidence.

**Spec** [Accepted #133 design](../design/test-impact-analysis-design.md)
at planning commit `2ff1b49ed3a3f91c8164d6c7b0e1dbe4c15cd3f9`,
SHA-256 `2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928`.
[Design acceptance and review evidence](../design/reviews/README.md).

**Source baseline** Trunk `dc037364ba617b97244c93670d12358d0b5cbba7`
was inspected for refinement. [#103 CI contract](../../103/design/github-ci-quality-gates-design.md)
and [manual delivery checklist](../../../../manual-delivery-checklist.md)
apply. Recheck the real source, protected target and runner evidence
at JIT.

## Global constraints

- Each leaf has a four implementation-agent-hour limit, its own accepted
  requirements, JIT, isolated branch, red/green verification, exact
  source review and delivery evidence. Split at refinement or JIT if
  the required work exceeds the estimate. Estimates are planning
  assumptions, with external approval and queue time separate.
- Retain full #103 PR validation as authority through shadow and
  qualification. TIA-first gating, live health enforcement and
  workspace enrollment require separate owner-approved activation.
  Work after plan acceptance requires separate implementation authority.
- Record exact repository, source and tree, applicable base/head, lock,
  controller/policy, platform, workflow run and attempt. Keep planned,
  observed and missing evidence distinct. A candidate cannot mint
  authority, credentials, assignments, or authoritative outcomes.
- Preserve full fallback across every applicable package and runner
  lane, unrounded 90% product and existing CI-helper coverage, required
  child-process evidence, installed-wheel smoke, file checks, and
  #103 full exact-base comparison. Full fallback cannot rescue
  unverifiable evidence or an observed test failure.
- Targets are under 3 minutes unit, under 6 integration, and under 10
  full, measured from first relevant job start to last required test
  result. Track queue, setup, execution, collector latency, total
  feedback and runner minutes separately.
- A PR-only failure holds that PR. A verified scheduled trunk test
  failure stops ordinary trunk merges and ordinary governed work.
  Verified non-test regressions or unavailable evidence hold merges.
  One repair addresses the incident's current causes and passes the
  exact full gate. A fresh full run on current repaired trunk precedes
  workspace updates. All stop-roster acknowledgments must verify.
- Keep private workspace paths, candidate-controlled logs, credentials,
  and work-in-progress out of public proof. Publish sanitized bound
  receipts. Preserve locks, untracked work and attempt evidence.
- The new gate is Python-first. Keep scope on #133 and existing AITM CI.
  Other language providers, a generic health service, and release
  policy changes are outside this plan.

## Review focus

- Candidate Python can forge a correct-looking artifact and may poison
  pytest inside the worker. T07–T09/T12 qualify actual independent
  observation, including negative results.
- A deletion and rename can remove an edge or a required case from the
  new tree. T03/T05/T12 preserve former consumers and inventory
  dispositions across the two snapshots.
- A passing repair against a broken base needs a qualified independent
  runner and correctly attributed inventory. T23–T25 rehearse the
  exception without weakening the candidate.
- A request can time out after GitHub receives it. T17/T21/T22 retain
  pending intent, fence additional writes and reconcile host state.
- A disconnected worker and a conflict can make an ancestral repair
  ineffective. T26–T33/T39 fence admission, prove the effective state
  and keep an outstanding roster member at the restart barrier.

## Interfaces, sequencing and verification

Paths below are relative to the repository. New modules live under
`tools/ci/tia/`; focused tests live at `tools/ci/tests/test_tia_<module>.py`
unless named otherwise. Each leaf owns only the paths stated. An
interface or file-ownership change requires reviewing its downstream
consumers before pickup. Existing workflow and verifier edits are
serialized by dependencies where shared.

Use versioned canonical JSON at process and trust boundaries. Domain
records in this plan have the following minimum fields. Hash content
with SHA-256 and normalize repo-relative paths without losing Git's
path identity. Reject duplicate keys, unsupported schema and path
escape before using receipts.

| Record | Required binding |
| --- | --- |
| `Snapshot` | Repository identity, ref role, commit/tree for hosted work or content digest for local work, sorted path changes including rename endpoints, baseline identity |
| `CollectionProof` | Exact tree, qualified collection observer, control and runner identities, independently established complete ID set and deviations |
| `Inventory` | Snapshot and runner-policy identities, ordered unique obligation IDs, package, suite, platform, isolation group, mandatory flag and collection disposition |
| `Selection` | Two snapshot identities, inventory and policy digests, mode, affected obligation IDs, per-path witness chains or declared dispositions, fallback reason |
| `ShardPlan` | Selection digest, full assignment and required scope, workflow run/attempt, controller identity and lock; assignment digest |
| `ShardReceipt` | Plan, shard, tested tree, actual observed obligations and outcome, coverage and child-proof digests, qualified runner and authenticated observation source |
| `FullProof` | Exact repository/ref, commit/tree, applicable base/head, run/attempt, current policy and required gates, verified outcomes, trust/freshness and complete baseline or labeled repair reference |
| `ContinuityWitness` | Independent monotonic repository and authority epoch, ordered decision/event tail, pending mutation and frozen roster commitment |
| `Incident` | Repository and trunk ref, monotonic version and stop epoch, failure evidence IDs and causes, held state, appointed incident owner, eligible exact repair PR, repair intent, current full proof, stop roster |
| `IncidentProbe` | Authority approval, incident version, repaired revision, verified failure IDs, selection and fallback policy digest |
| `WorkspaceReceipt` | Probe digest, repository, workspace ID/generation, incident version, repaired revision and verified effective snapshot, incident regression results and pickup validation |

Verification convention **V(module)** runs
`uv run --project packages/aitm-usage --locked pytest -q tools/ci/tests/test_tia_<module>.py`
from the repository root. A focused assertion must fail for the
specified missing behavior before implementation and pass after it.
Run related tests and the current required workflow checks before
closing each code leaf. For a spike, verify the pinned report and
observed outputs without treating an unsupported route as a pass.
Retain red/green or controlled proof, then commit scoped work through
the story's normal delivery route. All hosted qualification uses an
explicitly approved disposable repository or isolated target. A
simulated test cannot satisfy a real host or harness acceptance claim.

The plan keys below are stable identifiers. Native issues and direct
dependency edges are indexed separately from these reviewed bytes.
Keep leaves in Backlog until their own pickup gates apply.

## Pinned timing and candidate recipe

Use two consecutive, non-overlapping seven-day windows. Before the
first window, pin the immutable fixture candidates and run order.
For each window collect 20 comparable candidate cohorts: two per
candidate class per cache profile. Each cohort runs serial full,
sharded full, and actual selected (including mandated fallback)
against the same exact candidate on matched qualified capabilities.

| Candidate class | Required selection evidence |
| --- | --- |
| Single-package unit change | Known direct/multi-hop unit consumers and exact IDs |
| Multi-package integration change | Cross-package fixture/subprocess and integration consumers |
| Gate-defining control change | Full fallback and trusted independent disposition |
| Test-only change | Changed test self witness and other affected IDs where applicable |
| Positively classified non-test change | Trusted named disposition and exact required or empty selection |

A cold run has no restored dependency cache. A warm run uses the
same approved lock, runner image and primed cache key. Record actual
hit or miss. Use a proposed ceiling of 900 hosted runner-minutes
per window across the three modes, subject to owner approval before
spending. Incomplete cohorts, exceeded budget, capability drift or
missing evidence leave the window unqualified. Altering the pinned
recipe requires plan review before new measurement.

For each mode and window report p50 and p95 for unit (under 3m),
integration (under 6m), and the complete workload (under 10m).
Show the latter as full-suite elapsed only for complete runs.
For selected mode label its selected or fallback workload explicitly.
For a lane with no obligations show N/A and count, without counting
it as a zero-time observation. Report queue, total PR feedback, base
cost, cache profile, runner minutes, and matched cohort counts.
Propose affected-first cutover only with all reports complete, two
consecutive sharded-full windows at p95 of 10m or more despite
reasonable sharding, and at least 20% better p95 PR feedback in
comparable nonfallback cohorts. Cutover still requires the remaining
qualification and separate owner approval.

## Implementation stories

### T01. Pin the serial baseline — 2.5h, P1, no predecessor

**Owns** `tools/ci/tia/baseline.py`, `test_tia_baseline.py`, and the
sanitized baseline report. **Interface**
`build_baseline(verified_ci103, timings) -> Baseline`.

- [ ] Pin a green exact #103 trunk and PR candidate, package/CI helper
  inventories, coverage and child evidence, lock and toolchain. Use
  existing #103 verification and outcome custody. This comparison
  baseline cannot authorize the future gate. Retain
  cold and warm runs, with time and runner scope recorded separately.
- [ ] Make `test_baseline_rejects_mixed_attempts` fail first, then
  verify with V(baseline). A base/shard from another attempt cannot
  qualify; both timing samples retain actual measurements or Unknown.

### T02. Classify the pytest inventory — 3.5h, P1, T01

**Owns** `tools/ci/tia/inventory.py`, `tools/ci/tia/suites.json`,
`test_tia_inventory.py`. **Interface**
`classify(collection, suite_policy) -> Inventory`. Its input is a
local advisory observation or a hosted `CollectionProof`; preserve
that distinction in the inventory identity.

- [ ] Add `test_classification_preserves_parametrized_platform_ids`
  and `test_unclassified_or_duplicate_fails`. A parameterized test
  stays unique per required platform, and APFS/ACL and shared process
  groups keep explicit obligations.
- [ ] Encode approved unit, integration and system rules and preserve
  #103 required tests, optional skips, CLI subprocesses and CI helper
  ownership. V(inventory) passes and the full classified inventory
  reconciles with the serial baseline.

### T03. Resolve exact Git changes — 3h, P1, no predecessor

**Owns** `tools/ci/tia/snapshot.py`, `test_tia_snapshot.py`.
**Interface** `resolve(repo, request) -> tuple[Snapshot, Snapshot]`.

- [ ] `test_hosted_diff_matches_tested_tree` refuses a mismatched base
  or head, and `test_local_staged_untracked_rename_and_deleted_paths`
  binds both endpoints and content before and after reading.
- [ ] Use Git trees and NUL-delimited paths for hosted mode. Hash the
  effective local tracked and relevant untracked contents and return
  uncertainty if they change mid-read. V(snapshot) passes with
  missing objects, path escape and non-ASCII path fixtures.

### T04. Derive Python and package edges — 3.5h, P1, T02/T03

**Owns** `tools/ci/tia/python_graph.py`, `test_tia_python_graph.py`.
**Interface** `build_graph(snapshot, provider_policy) -> Graph` with
directed consumer/input edges and unresolved scope records.

- [ ] `test_import_alias_relative_reexport_cycle` preserves exact
  edges through initializers and module owners. `test_dynamic_scope`
  records unknown readers and package reachability.
- [ ] Resolve static imports with Python AST and trusted package-root
  mapping. Include pytest fixture and configuration scopes from
  qualified inputs. V(python_graph) passes. Neither a cycle nor an
  ambiguous namespace package silently drops a potential edge.

### T05. Select and explain test impact — 4h, P1, T02/T04

**Owns** `tools/ci/tia/selection.py`, `tools/ci/tia/edges.json`,
`test_tia_selection.py`. **Interface**
`select(before, after, inventory, policy) -> Selection`.

- [ ] `test_renamed_module_selects_former_consumer`,
  `test_cross_package_declared_subprocess_path`, and
  `test_known_edge_plus_unbounded_reader_runs_full` assert exact
  witnesses, qualified IDs and the full inventory on uncertainty.
- [ ] `test_direct_and_multihop_exact_witnesses` asserts
  `engine.py → test_engine.py::test_run` and
  `leaf.py → engine.py → test_engine.py::test_run` with the exact
  obligation ID and edge kinds. `test_declared_fixture_cross_package`
  asserts the fixture, cross-package consumer and exact test ID.
  `test_changed_test_and_non_test_disposition` asserts the changed
  test's self witness and exact ID, and an empty optional set with
  the named trusted non-test rule on a docs-only fixture.
- [ ] Union old/new reverse consumers, mandatory and changed IDs.
  Resolve declarations against trusted policy and record provenance
  for each path. A no-test result requires positive policy for every
  change and no mandatory obligation. V(selection) passes, including
  missing endpoints, deleted required case and arbitrary filename
  resemblance.

### T06. Deliver local advisory feedback — 3h, P2, T05

**Owns** `tools/ci/tia/local.py`, `test_tia_local.py`.
**Interface** `python -m tools.ci.tia.local --base <ref> --plan|--run`.

- [ ] `test_local_dirty_snapshot_never_mints_hosted_proof` and
  `test_selection_failure_runs_entire_applicable_suite` check output
  scope, deduped IDs, actual exit status and full escalation.
- [ ] Render summary plus a machine-readable plan and runner result.
  Stop on post-snapshot drift or unsupported required capability.
  V(local) passes and a controlled local fixture runs both modes.

### T07. Qualify trusted pytest observation — 3.5h, P1, T02

**Owns** spike report and disposable fixtures, with no production
observer. **Interface** a pinned host/runner capability receipt,
attack cases, and a bounded controller design or an explicit refusal.

- [ ] In an isolated qualified macOS/APFS runner, distinguish
  candidate-writable output from an externally observed runner.
  Exercise forged same-shape receipt, removed test during collection,
  fake pass through in-process hooks, and authenticated failure with
  a missing sibling shard. Include native child-process coverage.
- [ ] Prototype an independently controlled observer and receipt
  channel under a separate principal. Qualify complete collection
  before assignment and actual execution afterward. In particular,
  hide a newly collected ID before assignment and substitute a pass
  after assignment. Require a trusted completeness check or refusal
  in both full and selected modes. Document what arbitrary
  candidate code in a pytest process can still influence. Passing
  fixture output or artifact provenance alone cannot prove actual
  test execution. If the boundary cannot resist the cases, stop
  T08/T09 and their descendants. Keep #103 and local advisory available
  and return the boundary to design review.

### T08. Implement qualified complete collection — 4h, P1, T07

**Owns** `tools/ci/tia/collect.py`, `test_tia_collect.py` and the
qualified T07 collection adapter.
**Interface** `collect(candidate, control_identity, runner_identity) -> CollectionProof`.

- [ ] `test_new_candidate_id_cannot_be_hidden_before_assignment`
  exercises deletion of a newly discovered case even when the base
  inventory still matches. Reject when completeness is unprovable.
- [ ] Establish the complete collection before creating assignments.
  Use T07's isolated mechanism. Bind exact candidate, qualified
  observer, controls and platform. V(collect) and the hosted attack
  fixture pass independently of how many IDs later execute.

### T09. Implement qualified execution observation — 4h, P1, T07/T08

**Owns** `tools/ci/tia/observe.py`, `test_tia_observe.py` and the
qualified T07 execution adapter.
**Interface** `observe(candidate, collection, assigned_ids, runner_identity) -> Observations`.

- [ ] `test_candidate_cannot_supply_authoritative_outcomes` and
  `test_failure_observed_if_worker_exits_before_finalize` verify
  positive and negative evidence for the assigned subset.
- [ ] Keep controller, credentials and evidence channel outside
  candidate code. Match runtime observation to the prior complete
  collection and exact assignment. V(observe) and native qualification
  repeat on the exact implementation. Split or replan before Develop
  if the approved mechanism exceeds four hours.

### T10. Bind gate changes and inventory dispositions — 3.5h, P1, T02/T03

**Owns** `tools/ci/tia/controls.py`, `test_tia_controls.py`.
**Interface** `qualify_controls(base, candidate, approvals) -> ControlDisposition`
and `applicable_inventory(reference, target, dispositions) -> Inventory`.

- [ ] `test_control_edit_requires_full_and_independent_disposition`
  holds a gate-defining diff until the trusted approval binds exact
  source, control and scope. A candidate cannot amend its own rules.
- [ ] `test_reference_inventory_requires_intervening_dispositions`
  compares current exact scope to an older qualified reference
  only through verified ordered dispositions. Reject stale, missing
  or wrong-scope approval. V(controls) passes. T12/T14/T15/T24/T34
  consume these same rules for ordinary, scheduled, repair and selected
  paths, without inventing a new approval source.

### T11. Assign isolated test shards — 3h, P2, T02/T08

**Owns** `tools/ci/tia/shards.py`, `test_tia_shards.py`.
**Interface** `assign(collection, inventory, selection, durations, limits) -> ShardPlan`.

- [ ] `test_balancing_keeps_isolation_group` keeps APFS and process
  groups intact, deterministically places ties, and verifies a
  disjoint exact union by package, lane and platform.
- [ ] Assign only compatible groups; an absent required runner holds
  the gate. Start with a maximum of two independent jobs per package
  and lane as an experimental setting. T35 owns retuning from
  observed queue and setup costs. V(shards)
  passes for unknown durations, zero selection and reruns.

### T12. Verify shard receipts and inventories — 4h, P1, T09/T10/T11

**Owns** `tools/ci/tia/receipts.py`, `test_tia_receipts.py`.
**Interface** `verify_receipts(plan, collection, receipts, trusted_base, dispositions) -> Results`.

- [ ] `test_exact_attempt_union_rejects_forgery_or_duplicate` and
  `test_negative_receipt_survives_missing_shard` separate gate
  completeness from an independently verified failure.
- [ ] Reconcile assignments, inventory, policy scopes, required
  outcomes, independently qualified complete collection, and
  same-run/attempt authenticated artifacts. Refuse truncated or
  unverifiable collection in full or selected mode. Record
  candidate removals or runtime degradation against applicable base
  obligations. V(receipts) passes with partial rerun, stale base,
  absent mandatory ID, unexpected skip and extra ID.

### T13. Combine coverage and timing — 3.5h, P1, T12

**Owns** `tools/ci/tia/aggregate.py`, `test_tia_aggregate.py`.
**Interface** `aggregate(results, coverage, spans) -> GateReport`.

- [ ] `test_coverage_union_preserves_line_branch_and_child` rejects
  a wrong-tree child receipt and distinguishes 89.5% from 90%.
  `test_elapsed_envelope_is_not_sum` tests overlapping shards.
- [ ] Reuse #103 product/helper and wheel checks with exact compatible
  source and the unrounded 90% floor per active product package. Keep
  all three elapsed envelopes and separate queue,
  setup, execution and collector spans. V(aggregate) passes against
  the baseline and deliberately mismatched coverage.

### T14. Run the full and TIA shadow workflow — 4h, P1, T05/T13

**Owns** `.github/workflows/tia-shadow.yml`,
`tools/ci/tia/hosted.py`, `test_tia_hosted.py`.
**Interface** `shadow(candidate, policy) -> AdvisoryReport`.

- [ ] `test_shadow_cannot_publish_merge_authority` and
  `test_sharded_comparison_requires_identical_candidate` assert
  equal serial/shard node, outcome, line/branch and child proof.
- [ ] Expose package/lane/shard as separate hosted jobs. Keep #103
  as required, publish read-only summaries and exact witness paths.
  Derive hosted assignments only from qualified collection. Force
  full on T10 gate changes and show unresolved approvals hold.
  V(hosted) and an isolated hosted serial versus sharded run pass.
  Do not move the required gate in this story.

### T15. Schedule full trunk validation and ingest evidence — 3.5h, P1, T13

**Owns** `.github/workflows/tia-full.yml`,
`tools/ci/tia/scheduled.py`, `test_tia_scheduled.py`.
**Interface** `ingest(run, trusted_expectation, now) -> HealthEvent`.

- [ ] `test_failed_test_precedes_incomplete_run` and
  `test_overdue_schedule_holds_merges` authenticate negative evidence
  independently of final success. Unknown is never healthy.
- [ ] Use nightly full validation in the isolated target, with an
  immediate incident-bound dispatch for recovery. Proposed default
  freshness is 30 hours since the last qualifying completion,
  with missed-dispatch detection independent of that workflow.
  Reconcile all outcomes against the last trusted full trunk baseline
  using T10's ordered intervening inventory dispositions.
  V(scheduled) and a hosted skipped/missing shard drill pass.

### T16. Define the line incident reducer — 3.5h, P1, T15

**Owns** `tools/ci/tia/incident.py`, `test_tia_incident.py`.
**Interface** `reduce_incident(state, event) -> Incident` with typed owner appointment,
repair-candidate binding and external-cause disposition.

- [ ] `test_pr_failure_is_local`, `test_second_failure_advances_stop_version`,
  and `test_verified_skip_or_floor_miss_holds_merges_only` distinguish
  false, missing and complete outcomes.
- [ ] Fold ordered facts idempotently, with verified test failure
  taking precedence over merge-only holds. Version distinct unresolved
  causes and fence stale repair, recovery and workspace evidence.
  Persist the appointed owner and exactly one eligible repair PR
  identity, head, base, tree and incident version. Bind a source
  repair under a merge-only hold only after that owner substantiates
  the trunk-source/control cause. Reject unauthorized appointments,
  old assignments and a second full-passing PR.
  V(incident) passes for late pass, duplicate and wrong repository.

### T17. Persist authority and merge intents — 3.5h, P1, T16

**Owns** `tools/ci/tia/authority_store.py`, `test_tia_authority_store.py`.
**Interface** `apply(expected_version, operation) -> Decision` and
`get_pending(repository) -> Intent | None`.

- [ ] `test_stale_version_and_crash_hold_pending_intent` races two
  writes and restarts between intent reservation and reconciliation.
- [ ] Use one protected SQLite store on the trusted host and durable
  compare-and-swap updates. Deduplicate authenticated event IDs.
  Persist pending host mutation and its exact authorization before
  dispatch, with no ordinary retry during uncertain state. Deliver
  T17 as a closed storage seam with fixture-only state transitions.
  The store exposes facts and intents, with no live Healthy or
  authority issuance. T18 adds continuity verification before any
  live admission. Missing, restored or inconsistent state stays held.
  V(authority_store) passes without discarding locks or evidence.

### T18. Fence authority restore with independent continuity — 3.5h, P1, T17

**Owns** `tools/ci/tia/continuity.py`, `test_tia_continuity.py`.
**Interface** `verify_continuity(local, witness) -> Current | RecoveryHold`
and `record_tail(event, expected_tail) -> ContinuityWitness`.

- [ ] `test_restore_pre_stop_snapshot_with_green_host_stays_held`
  restores old SQLite while a workspace is disconnected and an
  intent unresolved. Verify canonical incident, roster and intent
  survive or ordinary work and merges stay held.
- [ ] Publish the critical ordered event/intent tail with compare-
  and-swap to a separately protected append-only audit ref using a
  distinct trusted identity. Bind the roster and pending mutation
  commitment before emitting an allowance or dispatch. Reconcile
  local/witness disagreement from the retained canonical sequence.
  No receipt or dispatch is issued while the witness is unavailable
  or history is incomplete. V(continuity) passes, including lost
  witness, stale restore and interrupted checkpoint.

### T19. Connect trusted scheduled evidence and freshness — 3h, P1, T18

**Owns** `tools/ci/tia/health_ingress.py`,
`test_tia_health_ingress.py`, and the disposable host's evidence
read identity. **Interface**
`refresh_host_evidence(expected, provider, now) -> HealthEvent`.

- [ ] `test_read_identity_and_missed_dispatch_hold` rejects candidate
  ingestion and records missed schedule under a scoped read-only
  hosting API identity. Refuse replay, wrong workflow or revision,
  and expired evidence.
- [ ] On the trusted host, run the independent freshness check and
  feed only T15's verified facts to the continuity-bound authority.
  V(health_ingress) and the isolated delayed/missing dispatch proof
  pass without granting merge or workspace credentials.

### T20. Authenticate workspace and incident authority — 3.5h, P1, T19

**Owns** `tools/ci/tia/authority_io.py`, `test_tia_authority_io.py`,
and disposable host transport configuration.
**Interface** `handle(actor, request, store) -> Decision` and
`require_current_authority(repository, expected_version) -> Current | Hold`.

- [ ] `test_candidate_cannot_request_repair_or_bypass_continuity`
  checks impersonation, authorized appointment and singular repair
  binding, stale version, and unavailable or inconsistent witness.
- [ ] Qualify a restricted authenticated workspace command endpoint,
  initially SSH forced-command on the disposable host, binding
  identity and generation to credentials and operation allowlists.
  Keep workspace, health-read, candidate and merge roles separate.
  Authenticate the appointing operator and verify the appointed
  owner's exact repair binding or external-interruption diagnosis.
  Pin T18 continuity and require it on all live grants and dispatch.
  Return delivery deferral for ordinary validation against stopped
  trunk. V(authority_io) and a cross-clone request pass. Prove the
  normal entry point issues no grant and dispatches nothing with only
  T17 storage or an inconsistent witness.

### T21. Qualify the GitHub merge fence — 3.5h, P1, no predecessor

**Owns** spike report and disposable repository rules evidence.
**Interface** receipt for one qualified GitHub merge method or refusal.

- [ ] In an owner-authorized disposable repo, test a dedicated
  trusted actor, host-enforced exclusive target updates, and a
  head-conditional PR merge. Require proof that the tested tree
  is the exact result of the permitted merge method.
- [ ] Exercise direct push, web/API, other automation, queue,
  head/base movement at mutation, stop between reservation and
  dispatch, and ambiguous in-flight ordinary merge concurrent with a
  stop. Prove the host commit and stop can be ordered. An unsent
  superseded request cannot dispatch. An ambiguous request fences all
  further mutations until readback establishes whether it committed
  before the stop or cannot commit. Reject any route where an ordinary
  update can still commit after the stop. A read followed by an
  unrestricted write, status cache or local epoch alone is insufficient.
  If the host cannot enforce the boundary, hold T22 and its
  descendants. Do not change AITM's production protection.

### T22. Implement conditional merge and reconciliation — 4h, P1, T20/T21

**Owns** `tools/ci/tia/merge.py`, `test_tia_merge.py`.
**Interface** `authorize_merge(request, incident, full_or_pr_proof) -> Intent`
and `reconcile(intent, provider_readback) -> MergeResult`.

- [ ] `test_head_or_base_moved_at_mutation_refuses`,
  `test_stop_between_intent_and_dispatch_and_during_uncertain_merge`, and
  `test_timeout_reconciles_without_duplicate_merge` assert exactness.
- [ ] Apply only T21's qualified method. Validate review, protection,
  base/head, tree, incident version and actor separation. Serialize
  reservation, final admission and dispatch with stop recording. Use
  T20's live continuity gate and admit only the bound exact repair in
  the current version. Test that an unauthorized or second full-pass
  candidate is refused. Cancel
  unsent stale intents. Keep an in-flight unknown intent and the stop
  fence durable. Admit no subsequent merge while ordering remains
  unknown. A conclusively earlier host commit becomes incident
  baseline evidence. Hold on
  drift or unexpected tree. V(merge) and the disposable host
  replay pass before any use as authority.

### T23. Qualify full repair outside broken base controls — 3.5h, P1, T15/T20

**Owns** disposable repair-route fixtures and capability report.
**Interface** a pinned trust/control route and full evidence receipt
or explicit refusal.

- [ ] In an approved isolated target, run a base with broken lock or
  workflow/setup and a fully passing exact repair candidate. Bootstrap
  the trusted controller from a separately pinned qualified source,
  install the exact candidate with its approved lock, and verify
  candidate coverage, native and child evidence, wheel and file checks.
- [ ] Refuse a red candidate and missing, mislabeled or unapproved
  reference inventory. Demonstrate normal independent review and
  gate-control disposition. Without this proof, hold T24 and its
  descendants. T07/T09 alone do not qualify this alternate route.

### T24. Validate repair on a broken base — 4h, P1, T22/T23

**Owns** `tools/ci/tia/repair.py`, `.github/workflows/tia-repair.yml`,
`test_tia_repair.py`.
**Interface** `verify_repair(candidate, incident, reference) -> FullProof`.

- [ ] `test_broken_base_setup_and_full_candidate` pins the base
  failure, records reference inventory at its actual revision,
  and refuses a selected-only or partial two-failure repair.
- [ ] Run an independently qualified trusted full candidate route
  when base controls cannot run, using T23's qualified route and
  T10's ordered reference dispositions. Permit only incident-accounted
  base-side gaps, preserve candidate floors and independent
  disposition for gate changes. V(repair) and the isolated broken
  lock/setup case pass.

### T25. Bind repair delivery to current trunk — 3.5h, P1, T24

**Owns** `tools/ci/tia/recovery.py`, `test_tia_recovery.py`.
**Interface** `accept_recovery(incident, delivered, full_proof, live) -> Decision`.

- [ ] `test_old_scheduled_failure_can_recognize_exact_landed_fix`
  requires full PR evidence and actual causal proof.
  `test_stale_full_pass_cannot_open_rollout` exercises wrong tree,
  older incident and protection drift.
- [ ] Dispatch full validation on the confirmed repair result;
  update on current trunk only. A verified external/scheduling
  interruption requires diagnosis plus fresh full pass. A repaired
  failing-test incident still requires workspace delivery. V(recovery) passes.

### T26. Bind incident probes to the repaired revision — 3h, P1, T05/T25

**Owns** `tools/ci/tia/incident_probe.py`, `test_tia_incident_probe.py`.
**Interface** `bind_probe(incident, full_proof, approved_policy) -> IncidentProbe`.

- [ ] `test_probe_includes_all_failures_and_fences_version_change`
  rejects a stale, unsigned or client-chosen probe. Bind approval,
  current incident/version, exact repaired trunk and every verified
  failing test ID. An unresolved or missing required probe holds.
- [ ] For each challenged effective workspace, union the incident
  probe with selection over relevant local changes and conflict
  resolutions. Use trustworthy full fallback on uncertainty.
  V(incident_probe) passes for a local change that restores the bug.
  T31 and T32 consume only current authority-bound probes.

### T27. Enroll workspaces and issue bounded decisions — 4h, P1, T17

**Owns** `tools/ci/tia/workspaces.py`, `test_tia_workspaces.py`.
**Interface** `enroll(identity, generation) -> Workspace` and
`admit(workspace, operation, now) -> Lease | Denial`.

- [ ] `test_disconnect_or_withdrawal_retains_roster_obligation` and
  `test_expired_or_wrong_generation_lease_refuses` exercise identity
  reuse, late enrollment and a disconnected runner.
- [ ] Snapshot the roster at stop. Allow only scoped diagnosis,
  repair, review, and later update under the appropriate phase.
  Proposed bound is a fresh decision per mutation batch with a
  60-second maximum lease and an earlier safe interruption point
  where supported. V(workspaces) passes. Unavailable authority
  refuses fresh ordinary mutations. T27 tests a local decision
  function only. T33 calls it in the live entry point after T20's
  current continuity proof and T32's applicable fix check.

### T28. Qualify native workspace controls — 3.5h, P1, T20/T27

**Owns** disposable native harness fixtures and capability report.
**Interface** a pinned registration, guarded operation, notification
and observation route per harness or explicit refusal.

- [ ] Probe actual Codex Desktop and Claude Code builds and scoped
  native PreToolUse/pickup and resume routes for an enrolled identity.
  Test safe interruption, a command or edit with no fresh lease, and
  missed notification. Confirm no unguarded mutation surface is admitted.
- [ ] Prove a trusted local observer under a separate identity can
  take a challenged effective snapshot and run an authority-bound
  fixture probe
  without accepting candidate-authored truth. Establish how a live
  admitted session receives stop via trusted notification and how a
  disconnected session is fenced at its next guarded boundary. A
  failed capability blocks that adapter or the observation leaf.

### T29. Bridge governed Codex operations — 4h, P1, T28

**Owns** `tools/ci/tia/harness.py`, `test_tia_harness.py`, and the
isolated Codex qualification carrier.
**Interface** `guard(request, authority_client) -> Permit | Hold`.

- [ ] `test_running_agent_loses_authority_before_notification` and
  `test_read_only_and_incident_roles` cover pickup, resume and
  bounded mutation. Preserve local changes and locks.
- [ ] Wire the T28-qualified Codex Desktop entry points and trusted
  stop-notification path to the authenticated enrollment. Prove a
  connected stop, missed notification, and fresh denial on
  disconnected mutation. V(harness) plus native Codex evidence pass.

### T30. Bridge governed Claude operations — 3.5h, P1, T29

**Owns** `tools/ci/tia/harness_claude.py`, `test_tia_harness_claude.py`
and the isolated Claude qualification carrier.
**Interface** `adapt_claude(event, enrollment) -> GuardRequest`.

- [ ] `test_claude_enrolled_hooks_deny_expired_lease` exercises
  pickup, resume, stop notification and governed mutations on the
  T28-qualified Claude Code surface, reusing T29's decision contract.
- [ ] Rehearse connected and disconnected Claude sessions and
  verify read-only and authorized incident actions. V(harness_claude)
  and native Claude evidence pass. Further admitted harnesses require
  separate equivalent qualification before enrollment.

### T31. Produce trusted workspace update observations — 4h, P1, T09/T26/T28

**Owns** `tools/ci/tia/workspace_observe.py`,
`test_tia_workspace_observe.py`.
**Interface** `observe_workspace(challenge, workspace, probe) -> WorkspaceReceipt`.

- [ ] `test_forged_or_replayed_fix_claim_is_denied` binds a fresh
  authority challenge, identity, generation, incident, repaired
  base, effective working-state digest and incident regression result.
- [ ] Measure tracked and relevant local changes and run the
  current T26 authority-bound probe through the qualified
  observation route. Refuse a stale or client-supplied probe or
  observation, and rebind on an incident version change. Qualify a real
  enrolled workspace, including an effective-state change during
  measurement. V(workspace_observe) and the native proof pass.

### T32. Verify workspace updates and release barrier — 4h, P1, T25/T30/T31

**Owns** `tools/ci/tia/restart.py`, `test_tia_restart.py`.
**Interface** `acknowledge(incident, effective_snapshot, fix_proof) -> WorkspaceReceipt`
and `release(incident, current_receipts) -> Decision`. Export
`check_effective(workspace, fresh_receipt, incident) -> Current | Hold`
for T33 to call before live lease issuance.

- [ ] `test_repaired_ancestry_with_bad_conflict_stays_held` and
  `test_final_workspace_receipt_reopens_only_current_stop` verify
  relevant working changes, disconnected workspace, and new failure
  between update and release.
- [ ] Use the incident regression probe on effective state as well
  as ancestry. Verify the T26 probe version and digest, bind workspace
  and generation, and recheck every
  current receipt before release and at next admission. Preserve
  user changes and never clear the roster by enrollment withdrawal.
  Consume the challenged receipt from T31 and re-observe effective
  state at release and next admission. A change after acknowledgment
  invalidates eligibility until the new proof verifies.
  V(restart) passes.

### T33. Enforce current workspace proof on live admission — 3.5h, P1, T32

**Owns** the workspace admission composition in
`tools/ci/tia/authority_io.py`, the T29/T30 native entry-point adapters'
admission wiring, and `test_tia_live_admission.py`.
**Interface** `admit_live(request, continuity, fix_observer) -> Lease | Denial`.

- [ ] `test_live_entry_denies_store_only_or_stale_workspace` proves
  the real lease entry point requires T20 continuity, then T32's
  fresh applicable proof, then T27's operation policy.
- [ ] Run an ordinary native mutation after a valid acknowledgment
  followed by a reverted effective state. Refuse the mutation.
  Refuse a newly enrolled or reopened workspace with stale base and
  admit the same operation only after its fix proof verifies.
  V(live_admission) and the enrolled native smoke pass.

### T34. Implement selected-mode gate in shadow — 4h, P1, T14

**Owns** `tools/ci/tia/selected_gate.py`, `test_tia_selected_gate.py`,
and the selected-only advisory job in `.github/workflows/tia-shadow.yml`.
**Interface** `evaluate_selected(plan, candidate, exact_base) -> GateReport`.

- [ ] `test_full_exact_base_and_changed_line_floor` checks 89.5%
  fails, 90% passes, executable deletion with zero denominator
  chooses full, and unobserved runtime outcomes remain unknown.
- [ ] Apply proposed complete inventories and selected runtime
  comparison with full exact-base evidence; keep mandated helpers,
  child/wheel/file checks. A measured deficit fails, unverifiable
  scope chooses full if trustworthy, and a failed test blocks.
  Run an actual selected and a forced-fallback candidate in the
  read-only hosted shadow, with compatible trusted exact-base proof.
  V(selected_gate) and the hosted receipts pass without publishing
  required PR authority.

### T35. Measure selection and sharding qualification — 3h, P2, T06/T34

**Owns** `tools/ci/tia/qualification.py`, `test_tia_qualification.py`,
and a sanitized timing and selector report.
**Interface** `summarize(episodes, profile) -> QualificationReport`.

- [ ] `test_report_requires_each_mode_window_and_lane` checks 3/6/10
  envelopes, p50/p95, no-test N/A and excluded queue, and rejects
  mixing unrelated runners or attempts.
- [ ] Apply the pinned recipe. Use T01 to forecast runner minutes before
  dispatch and return an over-cap recipe for review. Seed off-path
  defects, local drift
  and full fallback on the representative candidates. Report co-run
  contention, missed impacts and retuning separately. V(qualification)
  passes and each accepted sample has a bound run receipt.

### T36. Rehearse PR isolation and escaped-defect fencing — 3.5h, P1, T25/T33/T34

**Owns** isolated PR and escaped-defect fixture and bound host trace.
**Interface** a verified test-stop scenario for T38.

- [ ] Validate and actually merge an independent PR and observe
  its agent continue while a separate failed PR remains blocked.
- [ ] Prove verified scheduled test failure and a second verified
  cause hold already-green, queued and alternate update routes.
  Record ordinary delivery deferral and exact stopped state.
  Retain scoped host and agent receipts for both scenarios.

### T37. Rehearse merge-only holds — 4h, P1, T25/T33/T34

**Owns** isolated coverage, skip and unavailable-evidence fixtures
and their separate receipts.
**Interface** verified merge-only hold results for T41.

- [ ] After passing selected validation in the isolated fixture,
  observe scheduled coverage-floor miss and, in a distinct run,
  an undisposed skip of an unselected test. For each, retain
  denied ordinary merge and fresh allowed ordinary work.
- [ ] Inject broken scheduled setup with no outcomes and retain
  evidence of the merge hold and permitted work. Neither a missing
  report nor a skipped case can impersonate a verified failing test.

### T38. Rehearse conditional repair and fresh trunk proof — 4h, P1, T36

**Owns** disposable broken-base repair fixture and bound host trace.
**Interface** incident, admitted exact repair, actual host outcome
and current-trunk full proof for T39.

- [ ] Reuse T23's qualified broken-base fixture. Require full pass
  on the exact combined repair candidate. Reconcile an ambiguous
  mutation and replay the conditional head/base race fixtures from
  T21. A partial repair and an unapproved resulting tree are refused.
- [ ] Run the full suite on the confirmed current trunk. Retain
  the verified transition to workspace update, with ordinary
  merges and code work still stopped for the test incident.

### T39. Rehearse workspace pause and restart — 4h, P1, T33/T38

**Owns** three-clone rehearsal fixtures, restart qualification
receipt and operator runbook under `tools/ci/tia/`.
**Interface** an authenticated trace joining the T38 incident and
trunk proof to every workspace acknowledgment and release.

- [ ] Enroll Codex Desktop on the affected base, Claude Code on an
  earlier base, and a third native session on a separate clone that
  disconnects before notification. Preserve locks and changes.
  Exercise invalid conflict result, stale generation, withdrawal and
  older incident receipt on that roster. Release must refuse while
  any current acknowledgment is missing or invalid.
- [ ] Verify the disconnected workspace can return with the fix
  effective and provide the final acknowledgment before reopening.
  Retain the positive release trace and a separate bound stopped
  fixture with one outstanding receipt as input to T41. T41 owns
  rollback evidence. Keep this rehearsal isolated from live protection,
  schedule and authority mode.

### T40. Rehearse exact repair of a merge-only hold — 3.5h, P1, T37/T38

**Owns** the isolated broken-scheduled-setup repair and release trace.
**Interface** bound merge-only recovery proof for T41.

- [ ] Use T37's broken scheduled setup, with no verified failing test.
  Record the appointed owner's substantiation of the trunk control
  cause. Bind the single exact repair PR to the current hold version,
  with independent gate-change disposition.
- [ ] Require T24's full candidate proof and T22's conditional host
  mutation. Run a fresh full suite on confirmed current trunk. Retain
  refusal while another recorded cause is unresolved, then the
  verified merge-only release with no workspace-update phase.

### T41. Rehearse rollback with a live stop — 3h, P1, T35/T39/T40

**Owns** `tools/ci/tia/rollback.py`, `test_tia_rollback.py` and the
disposable rollback report.
**Interface** `change_validation_mode(mode, incident, proof) -> Decision`.

- [ ] `test_full_fallback_preserves_live_stop_and_roster` switches
  simulated selected validation to full with a verified test stop
  and an outstanding workspace receipt. Prove the stop persists,
  ordinary merges and work remain fenced, and the roster is intact.
- [ ] Exercise the policy transition in the isolated rehearsal.
  Restoring selected validation requires fresh control qualification
  and separate authorization. V(rollback) and the bound trace pass.

## Coverage and delivery boundary

| Accepted design area | Owning leaves |
| --- | --- |
| §§2–3 exact candidates, graph witness, conservative fallback | T02–T06, T10, T34 |
| §4 trusted observation, shards, test inventory and coverage | T01–T02, T07–T14, T34 |
| §5 timing, staged adoption, shadow, delayed schedule and rollback | T13–T15, T19, T34–T41 |
| §6 isolated failures, negative evidence, merge, repair and health | T15–T26, T36–T38, T40 |
| §6 workspace pause and verified all-workspace restart | T18–T20, T26–T33, T39 |
| §7 acceptance, real-host and failure-injection proofs | Exact T04/T05 witness assertions plus T35–T41 traces |

At JIT verify the direct dependency result, exact accepted leaf inputs,
four-hour estimate, supported route and the current base. A completed
negative spike records a deliverable but does not satisfy a capability
dependency. A leaf can land only with its own authorized scope, tests,
and review. Keep new controls inert or isolated until qualified.
Stop and replan a blocked capability rather than relabel it as available.

Acceptance of this plan binds its exact bytes. It does not open Develop,
approve disposable-host mutations, install credentials or enroll agents.
A later cutover proposal must present verified T07/T21/T23/T28 capability,
full versus sharded parity, the T35 timing and coverage tradeoff, the
T36–T41 traces, explicit changed-outcome/coverage policy, and a rollback to
full PR validation that preserves any live incident. If owner approval
or authority qualification is absent, keep the existing full PR gate.
