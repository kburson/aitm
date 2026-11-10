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
  pytest inside the worker. T07/T08/T10 qualify actual independent
  observation, including negative results.
- A deletion and rename can remove an edge or a required case from the
  new tree. T03/T05/T10 preserve former consumers and inventory
  dispositions across the two snapshots.
- A passing repair against a broken base needs a qualified independent
  runner and correctly attributed inventory. T19/T20 rehearse the
  exception without weakening the candidate.
- A request can time out after GitHub receives it. T17/T18 retain
  pending intent, fence additional writes and reconcile host state.
- A disconnected worker and a conflict can make an ancestral repair
  ineffective. T21–T23/T27 fence admission, prove the effective state
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
| `Inventory` | Snapshot and runner-policy identities, ordered unique obligation IDs, package, suite, platform, isolation group, mandatory flag and collection disposition |
| `Selection` | Two snapshot identities, inventory and policy digests, mode, affected obligation IDs, per-path witness chains or declared dispositions, fallback reason |
| `ShardPlan` | Selection digest, full assignment and required scope, workflow run/attempt, controller identity and lock; assignment digest |
| `ShardReceipt` | Plan, shard, tested tree, actual observed obligations and outcome, coverage and child-proof digests, qualified runner and authenticated observation source |
| `FullProof` | Exact repository/ref, commit/tree, applicable base/head, run/attempt, current policy and required gates, verified outcomes, trust/freshness and complete baseline or labeled repair reference |
| `Incident` | Repository and trunk ref, monotonic version and stop epoch, failure evidence IDs and causes, held state, repair intent, current full proof, stop roster |
| `WorkspaceReceipt` | Repository, workspace ID/generation, incident version, repaired revision and verified effective snapshot, incident regression results and pickup validation |

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
`classify(observed, suite_policy) -> Inventory`.

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
  channel under a separate principal. Document what arbitrary
  candidate code in a pytest process can still influence. Passing
  fixture output or artifact provenance alone cannot prove actual
  test execution. If the boundary cannot resist the cases, stop
  T08 and its descendants. Keep #103 and local advisory available
  and return the boundary to design review.

### T08. Implement the qualified observer — 4h, P1, T07

**Owns** `tools/ci/tia/observe.py`, `test_tia_observe.py`, and the
qualified T07 execution adapter. **Interface**
`observe(candidate, expected_ids, runner_identity) -> Observations`.

- [ ] Port the qualifying attack fixtures to
  `test_candidate_cannot_supply_authoritative_outcomes` and
  `test_failure_observed_if_worker_exits_before_finalize`.
- [ ] Implement only the T07-qualified mechanism, with no candidate
  access to observer controls, credentials or authenticated output.
  V(observe) passes and native qualification repeats on the exact
  implementation. If the qualified mechanism needs more than four
  hours or new trust assumptions, split or replan before Develop.

### T09. Assign isolated test shards — 3h, P2, T02

**Owns** `tools/ci/tia/shards.py`, `test_tia_shards.py`.
**Interface** `assign(inventory, selection, durations, limits) -> ShardPlan`.

- [ ] `test_balancing_keeps_isolation_group` keeps APFS and process
  groups intact, deterministically places ties, and verifies a
  disjoint exact union by package, lane and platform.
- [ ] Assign only compatible groups; an absent required runner holds
  the gate. Start with a maximum of two independent jobs per package
  and lane, then tune with observed queue and setup costs. V(shards)
  passes for unknown durations, zero selection and reruns.

### T10. Verify shard receipts and inventories — 4h, P1, T08/T09

**Owns** `tools/ci/tia/receipts.py`, `test_tia_receipts.py`.
**Interface** `verify_receipts(plan, receipts, trusted_base) -> Results`.

- [ ] `test_exact_attempt_union_rejects_forgery_or_duplicate` and
  `test_negative_receipt_survives_missing_shard` separate gate
  completeness from an independently verified failure.
- [ ] Reconcile assignments, inventory, policy scopes, required
  outcomes, and same-run/attempt authenticated artifacts. Record
  candidate removals or runtime degradation against applicable base
  obligations. V(receipts) passes with partial rerun, stale base,
  absent mandatory ID, unexpected skip and extra ID.

### T11. Combine coverage and timing — 3.5h, P1, T10

**Owns** `tools/ci/tia/aggregate.py`, `test_tia_aggregate.py`.
**Interface** `aggregate(results, coverage, spans) -> GateReport`.

- [ ] `test_coverage_union_preserves_line_branch_and_child` rejects
  a wrong-tree child receipt and distinguishes 89.5% from 90%.
  `test_elapsed_envelope_is_not_sum` tests overlapping shards.
- [ ] Reuse #103 product/helper and wheel checks with exact compatible
  source. Keep all three elapsed envelopes and separate queue,
  setup, execution and collector spans. V(aggregate) passes against
  the baseline and deliberately mismatched coverage.

### T12. Run the full and TIA shadow workflow — 4h, P1, T05/T11

**Owns** `.github/workflows/tia-shadow.yml`,
`tools/ci/tia/hosted.py`, `test_tia_hosted.py`.
**Interface** `shadow(candidate, policy) -> AdvisoryReport`.

- [ ] `test_shadow_cannot_publish_merge_authority` and
  `test_sharded_comparison_requires_identical_candidate` assert
  equal serial/shard node, outcome, line/branch and child proof.
- [ ] Expose package/lane/shard as separate hosted jobs. Keep #103
  as required, publish read-only summaries and exact witness paths.
  V(hosted) and an isolated hosted serial versus sharded run pass.
  Do not move the required gate in this story.

### T13. Schedule full trunk validation and ingest evidence — 3.5h, P1, T11

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
  Reconcile all outcomes against the last trusted full trunk baseline.
  V(scheduled) and a hosted skipped/missing shard drill pass.

### T14. Define the line incident reducer — 3.5h, P1, T13

**Owns** `tools/ci/tia/incident.py`, `test_tia_incident.py`.
**Interface** `reduce_incident(state, event) -> Incident`.

- [ ] `test_pr_failure_is_local`, `test_second_failure_refences_stop`,
  and `test_verified_skip_or_floor_miss_holds_merges_only` distinguish
  false, missing and complete outcomes.
- [ ] Fold ordered facts idempotently, with verified test failure
  taking precedence over merge-only holds. Version distinct unresolved
  causes and fence stale repair, recovery and workspace evidence.
  V(incident) passes for late pass, duplicate and wrong repository.

### T15. Persist authority and merge intents — 3.5h, P1, T14

**Owns** `tools/ci/tia/authority_store.py`, `test_tia_authority_store.py`.
**Interface** `apply(expected_version, operation) -> Decision` and
`get_pending(repository) -> Intent | None`.

- [ ] `test_stale_version_and_crash_hold_pending_intent` races two
  writes and restarts between intent reservation and reconciliation.
- [ ] Use one protected SQLite store on the trusted host and durable
  compare-and-swap updates. Deduplicate authenticated event IDs.
  Persist pending host mutation and its exact authorization before
  dispatch, with no ordinary retry during uncertain state. Missing,
  restored or inconsistent authority state cannot initialize Healthy
  without verified reconciliation of pending mutations and evidence.
  V(authority_store) passes without discarding locks or evidence.

### T16. Connect the trusted authority boundary — 3.5h, P1, T15

**Owns** `tools/ci/tia/authority_io.py`, `test_tia_authority_io.py`,
and disposable host transport configuration.
**Interface** `handle(actor, request, store) -> Decision` and
`refresh_host_evidence(expected, provider, now) -> HealthEvent`.

- [ ] `test_candidate_cannot_ingest_health_or_request_repair` and
  `test_missing_freshness_and_replayed_request_fail_closed` exercise
  impersonation, role separation, stale version and unavailable state.
- [ ] Read scheduled evidence from the hosting API with a scoped
  read-only trusted identity. Run the independent freshness check
  on the authority host. For workspace requests qualify a restricted
  authenticated command endpoint, initially SSH forced-command on
  the disposable host, with workspace identity and generation bound
  to credentials and operation allowlists. Hold on unavailable or
  unqualified transport. V(authority_io) and an authenticated
  cross-clone request pass. Separate the merge identity from the
  endpoint and candidate runners.

### T17. Qualify the GitHub merge fence — 3.5h, P1, no predecessor

**Owns** spike report and disposable repository rules evidence.
**Interface** receipt for one qualified GitHub merge method or refusal.

- [ ] In an owner-authorized disposable repo, test a dedicated
  trusted actor, host-enforced exclusive target updates, and a
  head-conditional PR merge. Require proof that the tested tree
  is the exact result of the permitted merge method.
- [ ] Exercise direct push, web/API, other automation, queue,
  head/base movement at mutation, and ambiguous response. A read
  then unrestricted write or a cached status is insufficient.
  If the host cannot enforce the boundary, hold T18 and its
  descendants. Do not change AITM's production protection.

### T18. Implement conditional merge and reconciliation — 4h, P1, T16/T17

**Owns** `tools/ci/tia/merge.py`, `test_tia_merge.py`.
**Interface** `authorize_merge(request, incident, full_or_pr_proof) -> Intent`
and `reconcile(intent, provider_readback) -> MergeResult`.

- [ ] `test_head_or_base_moved_at_mutation_refuses`,
  `test_stop_fences_old_green_and_queue`, and
  `test_timeout_reconciles_without_duplicate_merge` assert exactness.
- [ ] Apply only T17's qualified method. Validate review, protection,
  base/head, tree, incident version and actor separation. Hold on
  drift or unexpected tree. V(merge) and the disposable host
  replay pass before any use as authority.

### T19. Validate repair on a broken base — 4h, P1, T18/T13

**Owns** `tools/ci/tia/repair.py`, `.github/workflows/tia-repair.yml`,
`test_tia_repair.py`.
**Interface** `verify_repair(candidate, incident, reference) -> FullProof`.

- [ ] `test_broken_base_setup_and_full_candidate` pins the base
  failure, records reference inventory at its actual revision,
  and refuses a selected-only or partial two-failure repair.
- [ ] Run an independently qualified trusted full candidate route
  when base controls cannot run. Permit only incident-accounted
  base-side gaps, preserve candidate floors and independent
  disposition for gate changes. V(repair) and the isolated broken
  lock/setup case pass.

### T20. Bind repair delivery to current trunk — 3.5h, P1, T19

**Owns** `tools/ci/tia/recovery.py`, `test_tia_recovery.py`.
**Interface** `accept_recovery(incident, delivered, full_proof, live) -> Decision`.

- [ ] `test_old_scheduled_failure_can_recognize_exact_landed_fix`
  requires full PR evidence and actual causal proof.
  `test_stale_full_pass_cannot_open_rollout` exercises wrong tree,
  older incident and protection drift.
- [ ] Dispatch full validation on the confirmed repair result;
  update on current trunk only. A verified external/scheduling
  interruption requires diagnosis plus fresh full pass. Failing
  tests still enter workspace delivery. V(recovery) passes.

### T21. Enroll workspaces and issue bounded decisions — 4h, P1, T15

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
  refuses fresh ordinary mutations.

### T22. Bridge governed harness boundaries — 4h, P1, T16/T21

**Owns** `tools/ci/tia/harness.py`, `test_tia_harness.py`, and isolated
Codex and Claude qualification fixtures.
**Interface** `guard(request, authority_client) -> Permit | Hold`.

- [ ] `test_running_agent_loses_authority_before_notification` and
  `test_read_only_and_incident_roles` exercise pickup, resume and
  governed mutation boundaries without destroying local changes.
- [ ] Bind only actual supported native hooks or governed command
  entry points to the scoped authority. Use authenticated transport,
  with no candidate-owned secrets. Prove Codex and Claude on real
  enrolled sessions and two clones. Any additional admitted harness
  must pass the same proof before enrollment. If a supported surface
  cannot fence ordinary work, exclude it from readiness and block
  cutover pending an approved split or design resolution.
  V(harness) proves logic; native evidence is separate.

### T23. Verify workspace updates and release barrier — 4h, P1, T20/T22

**Owns** `tools/ci/tia/restart.py`, `test_tia_restart.py`.
**Interface** `acknowledge(incident, effective_snapshot, fix_proof) -> WorkspaceReceipt`
and `release(incident, current_receipts) -> Decision`.

- [ ] `test_repaired_ancestry_with_bad_conflict_stays_held` and
  `test_final_workspace_receipt_reopens_only_current_stop` verify
  relevant working changes, disconnected workspace, and new failure
  between update and release.
- [ ] Use the incident regression probe on effective state as well
  as ancestry, bind workspace and generation, and recheck every
  current receipt before release and at next admission. Preserve
  user changes and never clear the roster by enrollment withdrawal.
  V(restart) passes.

### T24. Implement selected-mode gate in shadow — 4h, P1, T12

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

### T25. Measure selection and sharding qualification — 3h, P2, T06/T24

**Owns** `tools/ci/tia/qualification.py`, `test_tia_qualification.py`,
and a sanitized timing and selector report.
**Interface** `summarize(episodes, profile) -> QualificationReport`.

- [ ] `test_queue_not_counted_as_full_suite_budget` checks all three
  envelopes and rejects mixing unrelated runners or attempts.
  Seed off-path defects, local snapshot drift, cross-package reads,
  and full fallback on representative fixture candidates.
- [ ] Collect a proposed minimum 20 comparable runs per window,
  reporting cold/warm separately, base lane cost, missed-impact
  evidence, and total feedback versus serial. Compare equivalent
  full/sharded and selected executions on the same candidate with
  matched capabilities and cache profile. Record any co-run
  contention separately. Propose cutover only
  after two consecutive windows miss the full target at p95 despite
  reasonable sharding and TIA improves feedback without losing
  required proof. Otherwise keep full PR authority. V(qualification)
  and the pinned shadow reports pass.

### T26. Rehearse hosted holds and exact repair — 4h, P1, T20/T24

**Owns** disposable hosted failure and repair fixtures and the
bound host trace under `tools/ci/tia/`.
**Interface** authenticated incident, authority and current-trunk proof
for the workspace rehearsal.

- [ ] Prove isolated PR failure leaves other PRs eligible. Rehearse
  verified escaped failure, a second verified cause, and merge-only
  coverage, inventory and evidence holds. Refuse already-green,
  queued and alternate update routes. Replay the component race
  fixtures and reconcile an ambiguous merge.
- [ ] Rehearse broken-base full validation, the exact full-passing
  combined repair and conditional host mutation. Require a full
  current-trunk proof before emitting the workspace-update phase.
  Retain each failure and control result in the hosted trace.

### T27. Rehearse workspace pause and restart — 4h, P1, T23/T25/T26

**Owns** two-clone rehearsal fixtures, the restart qualification
receipt, and the operator runbook under `tools/ci/tia/`.
**Interface** an authenticated trace joining the T26 incident and
trunk proof to every workspace acknowledgment and release.

- [ ] Exercise real enrolled native sessions, including an earlier
  base and an active workspace disconnected before notification.
  Preserve locks and changes and refuse an invalid conflict result,
  stale generation, withdrawal, and an older incident receipt.
- [ ] Verify the disconnected workspace can return with the fix
  effective and provide the final acknowledgment before reopening.
  Retain the positive release trace. Record the combined qualification
  and rollback evidence, without changing live protection, schedule
  or authority mode.

## Coverage and delivery boundary

| Accepted design area | Owning leaves |
| --- | --- |
| §§2–3 exact candidates, graph witness, conservative fallback | T02–T06, T24 |
| §4 trusted observation, shards, test inventory and coverage | T01–T02, T07–T12, T24 |
| §5 timing, staged adoption, shadow, delayed schedule and rollback | T11–T13, T24–T27 |
| §6 isolated failures, negative evidence, merge, repair and health | T13–T20, T26 |
| §6 workspace pause and verified all-workspace restart | T16, T21–T23, T27 |
| §7 acceptance, real-host and failure-injection proofs | The owning leaf assertions plus T25–T27 |

At JIT verify the direct dependency result, exact accepted leaf inputs,
four-hour estimate, supported route and the current base. A completed
negative spike records a deliverable but does not satisfy a capability
dependency. A leaf can land only with its own authorized scope, tests,
and review. Keep new controls inert or isolated until qualified.
Stop and replan a blocked capability rather than relabel it as available.

Acceptance of this plan binds its exact bytes. It does not open Develop,
approve disposable-host mutations, install credentials or enroll agents.
A later cutover proposal must present verified T07/T17 capability,
full versus sharded parity, the T25 timing and coverage tradeoff, the
T26 and T27 traces, explicit changed-outcome/coverage policy, and a rollback to
full PR validation that preserves any live incident. If owner approval
or authority qualification is absent, keep the existing full PR gate.
