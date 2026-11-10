# AITM test impact analysis, CI sharding, and Stop the Line

Candidate for design review under [#133](https://github.com/kburson/aitm/issues/133).
Follow-on to the [#103 CI quality gates](../../103/story.md).

## 1. Outcome and scope

Give authors fast feedback on the tests a story can affect. A reviewer
can start at any changed file, follow the dependency chain to each
selected test, and see the result of that test on the exact candidate.
If the selector cannot establish impact, run the full applicable suite.
Distribute independent tests as named jobs on separate GitHub-hosted
runners without losing test inventory, capability, or coverage evidence.

The first provider covers AITM's Python packages and pytest-based CI
tooling. Package ownership and test type are separate, so one package
can have unit, integration, and system tests. The planning and evidence
formats can later accept another runner. Additional language providers,
historical ranking, shared result caching, release-policy changes, and
a general-purpose project health service are outside this design.

The original ai-task-manager used reverse imports, naming matches, and
declared dependencies. It reported direct and transitive matches but
discarded intermediate nodes, and it could classify an unmatched path
as having no impact. Its CI used separate jobs for lanes and verified
the union of shard receipts. AITM carries forward the graph and receipt
patterns, records the intermediate edges, and requires a positive
disposition for paths that can skip tests. [Legacy selector](https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/test-impact-selector.mjs#L120) · [Legacy workflow](https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/.github/workflows/ci.yml#L103) · [Nx affected](https://nx.dev/docs/features/ci-features/affected)

The current #103 gate runs a full candidate Python suite on qualified
macOS, checks trusted base inventory and outcomes, verifies expected
subprocess coverage and the installed wheel, and retains exact PR
evidence. One representative PR completed in 3m 31s. A recent trunk
push took 9m 07s end to end, with roughly 5m 12s before the Python job
started and 3m 43s in that job. These are observations, without separate
unit and integration timing. Establish a comparable baseline before
choosing shard counts or treating runtime as a reason to change the gate.
[Existing CI design](../../103/design/github-ci-quality-gates-design.md#coverage-and-test-scaling) · [PR run](https://github.com/kburson/aitm/actions/runs/42841994451) · [Trunk run](https://github.com/kburson/aitm/actions/runs/42843355312)

## 2. Validation modes and authority

| Mode | Inputs | Passing evidence |
| --- | --- | --- |
| Local story feedback | Declared story base and inspected working snapshot | Selected or full local outcomes tied to the inspected snapshot |
| PR during qualification | Applicable base, PR head, and tested merge candidate | Full required candidate suite and existing #103 evidence. TIA selection is advisory. |
| PR after approved cutover | Same exact candidate identity and trusted policy | Verified selected set, or the full suite if required, plus applicable review and quality gates |
| Scheduled trunk | Exact trunk snapshot pinned for the run | Complete repository inventory, full outcomes, qualified runners, and full coverage |
| Incident repair PR | Active incident, current trunk base, and exact proposed repair candidate | Full candidate suite and ordinary required review and checks |
| Incident recovery run | Active incident and exact current trunk after the repair merges | Complete trunk evidence authorizing the workspace update |

Keep candidate identity distinct from branch names. A PR plan and its
results bind the repository, base, head, tested commit and tree, workflow
run and attempt, and control revisions. Base or head movement requires
fresh applicable evidence. A local run includes committed story changes,
staged and unstaged changes, and relevant untracked files. It cannot
authorize a hosted gate. If a committed candidate or its applicable
base cannot be established, no hosted test result can pass the gate.

Select and qualify using reviewed policy and trusted controls outside
the candidate's authority. Treat proposed changes to the selector,
classification, test discovery controls, coverage controls, workflow,
verifier, or merge policy as gate-defining changes. Run the full suite,
record the changes explicitly, and require existing independent
disposition of gate changes. If trusted collection or verification
cannot establish outcomes, block. Candidate jobs have read-only
credentials and cannot publish authoritative health or merge decisions.
Preserve #103's exact-attempt artifact custody and signed or independently
verified binding for the final PR result. [Existing CI evidence rules](../../103/design/github-ci-quality-gates-design.md#workflow-and-evidence)

## 3. Dependency graph and selection

### Inputs and resolution

Use Git objects for hosted inputs. Diff the applicable base tree against
the tree actually tested. Record additions, modifications, removals,
and both sides of renames or moves. Use the base graph for former
consumers and the candidate graph for current consumers. A surviving
test affected by either graph must run. A deleted test cannot run.
Record it and require the same inventory disposition as any other
removed test. If the removed input's consumers or inventory change
cannot be resolved, fall back or block when the evidence is unfit.

For each snapshot, derive repository-local import and package ownership
edges from supported Python source and workspace inputs. Include
package initializers and re-exports, test helpers, pytest fixture and
configuration scope, and dependencies between packages. Add reviewed
declarations for subprocess or console entry points, dynamically loaded
modules, schemas, templates, test fixtures, and other runtime files that
imports cannot express. A declaration specifies source scope, consumers,
edge kind, and rationale. A matched declaration with missing or
ambiguous endpoints makes selection uncertain. A name match may help
locate a dependency for review. It cannot be the sole basis for
excluding other tests.

Resolve edges from consumer to input and traverse in reverse from each
changed file. Deduplicate tests while keeping a deterministic witness
path for each changed-file and affected-test pair. Cycles terminate
without losing reachable consumers. Retain the source of declared edges
and distinguish paths observed on the base, the candidate, or both.
File-level analysis may select every collected ID in a test module.
Use finer IDs only when the dependency can be established. Include
changed and newly collected test IDs, and record any policy-mandatory
test or suite with its policy reason.

For example, a data fixture can affect a loader, the CLI entry point
that invokes it, and an integration test that launches that CLI. The
record shows those three edges and their kinds, including the declared
subprocess edge. An evidence chain may contain package or fixture nodes
when they represent a real dependency. Keep the original changed file
and exact test ID at the endpoints.

### Classification and fallback

Every changed path gets one or more evidenced dispositions. A resolved
path lists affected tests, a positively classified non-test input
names its policy rule, and an uncertain path names the reason for
fallback. A changed file with no known consumers, an unsupported
production input, an unresolved dynamic edge in relevant scope, a
global or unclassified configuration change, incompatible inventory,
or an unavailable graph is uncertain. A reviewed shared input can
directly select the whole applicable inventory. A no-test selection is
allowed only when trusted policy positively establishes no test impact
for every changed path and no required test is due. Other PR checks
still run. A broad fallback covers the whole configured applicable
suite, including all qualified lanes. It is never downgraded to the
package where the first uncertainty appeared.

Coverage observations and shadow results can identify gaps in the graph
and add candidate edges for review. A previous test's lack of coverage
cannot exclude it. A timeout, parse error, or selector crash falls back
if the exact candidate and full execution remain available. Failure to
run or verify that fallback fails validation. A failing selected test
blocks the candidate, even if another run passes.

## 4. Inventory, shards, and test evidence

Discover a complete applicable test inventory through the qualified
runner before assigning shards. Normalize each item to a stable
provider, package, runner scope, and exact test ID, preserving
parameterization. Use an explicit reviewed inventory rule for suite
classification. Each required item belongs to exactly one execution
lane for a given environment. A test that intentionally runs on more
than one platform has a distinct obligation in each required scope.
Fail closed for unclassified items, duplicate IDs, unavailable runner
capabilities, or collection that cannot be reconciled with policy.

| Dimension | Use |
| --- | --- |
| Owning package or CI tooling | Select and report work independently of test type |
| Unit, integration, system or slow | Group fast feedback and identify expensive required work |
| Platform and capability | Keep required APFS, ACL, and native behavior on qualified runners |
| Isolation group | Keep shared fixtures, process lifecycle, lease, or shared-state tests together until isolation is proven |

Each independently executable shard runs as a named job on a separate
instance. Name jobs by package or package group, test type, and shard.
Retain an immutable assignment for the run attempt. Use recorded
durations to balance independent groups with deterministic ties. Keep
groups that share environment or state intact. The implementation plan
chooses shard counts and concurrency from measured setup cost, capacity,
and total hosted runner time. No fixed shard count or more in-process
parallelism is required. [GitHub Actions job matrices](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/run-job-variations)

An independently trusted collector verifies every expected shard
artifact by identity and digest. Check repository, source tree, tested
candidate, policy, platform scope, assignment, run and attempt.
The union of outcomes must equal the planned test IDs, with every
expected outcome classified and every ID accounted for once per
required scope. Reject extra, missing, duplicate, cancelled, stale,
or unexpectedly skipped results. Policy-scoped capability skips retain
the existing evidence requirement. A rerun uses a complete matching
attempt. Artifacts from earlier attempts cannot fill gaps. Compare
complete candidate collection with trusted exact-base inventory and
surface removal, deselection, new skips, and new xfails. A missing
required case or an undisposed inventory change blocks the gate.
Selected mode records which remaining outcomes were not observed.

Full PR mode retains the existing #103 requirement to compare complete
candidate outcomes with trusted exact-base outcomes. The proposed
selected gate still requires a full exact-base result. Compare the
complete inventories, and compare runtime outcomes for every selected
test against that base result. Establish a trusted full trunk baseline
before cutover. The scheduled gate compares complete outcomes with
the last trusted full trunk baseline, applying any intervening reviewed
inventory dispositions. This moves detection of runtime changes in
unselected tests to the full gate and requires explicit cutover
approval. Any reuse of a retained base run must match its source,
controls, lock, runner scope, and provenance. Measure the base lane's
time when evaluating whether selection shortens PR feedback.

Combine compatible coverage from the same tested source, policy, and
attempt, including required child-process evidence. Compare serial and
sharded coverage at the line and branch set level on the same candidate
during qualification. Preserve #103's unrounded 90% line floor per
active product package for every full gate. Keep the wheel smoke and
other required checks separate from the test subset. For an eventual
selected PR gate, the proposed replacement for full-package coverage
on that candidate is 90% of changed executable lines per affected
product package, measured on the candidate. This is a separate gate
policy decision at cutover. Use full mode when the selected result
cannot establish its required coverage scope, when the denominator
cannot be trusted, or when full coverage is independently required.
A measured coverage deficit fails the selected gate. Report full and
selected coverage scopes explicitly. [Coverage aggregation](https://coverage.readthedocs.io/en/latest/commands/cmd_combine.html) · [Subprocess coverage](https://coverage.readthedocs.io/en/latest/subprocess.html)

The plan records source and policy identity, changed paths and their
dispositions, full inventory digest, mode, exact selected IDs and
witness paths, fallback reason, and shard assignments. Outcomes link
back to that plan and identify the same source, scope, and run attempt.
Publish a short summary with selected and executed counts by package
and type, elapsed time, result and reason for escalation. Put detailed
per-file paths, per-test outcomes, and artifact identities in the
linked evidence. Retain enough to reproduce or dispute a decision.
Keep local working-snapshot evidence local, and keep secrets,
environment values, and machine-private paths out of hosted records.

## 5. Runtime budgets and adoption

| Suite | Target elapsed time |
| --- | ---: |
| Unit | Under 3 minutes |
| Integration, across all required integration shards | Under 6 minutes |
| Full, across all required test lanes | Under 10 minutes |

Measure each envelope from the first applicable job start to the last
required test outcome. This includes setup and gaps between shards
after the first job starts. Measure planning, initial queue, test
execution, evidence collection, and total PR feedback separately.
Report cache state, runner scope, shard count, and hosted runner
minutes. Compare like-for-like cold and warm samples. Targets apply to
elapsed time across parallel jobs, rather than their sum.

1. Establish a serial inventory and timing baseline. Introduce sharded
   full execution only after inventory, outcomes, capabilities and
   coverage agree with the serial reference on the same candidate.
2. Run TIA in shadow while the full PR gate remains required. Compare
   selections with actual outcomes and known dependency obligations.
   Include seeded failures outside the obvious direct-import path,
   representative multi-package changes, and fault cases for unknown
   inputs. A full green run without seeded or observed failures cannot
   establish selection safety.
3. Make selected feedback available during story development. Keep
   complete hosted PR evidence until a separate gate change is
   accepted. An affected-only cutover requires sustained misses of the
   10-minute budget after reasonable sharding, useful selection on
   representative changes, successful fallback drills, and an
   end-to-end Stop the Line rehearsal. The plan sets the sample window
   and representative test set before taking measurements.
4. Before cutover, qualify an independent scheduled full trunk run and
   its health authority. Proposed default is nightly plus an immediate
   recovery run after a repair merge. Bind runs to an exact trunk SHA.
   Observe delayed, dropped, incomplete, and overdue runs through
   trusted state or a separate freshness check. The plan specifies
   cadence and freshness limits for review. The schedule never
   substitutes for a PR's required full fallback.
5. On selector or evidence regression, route ordinary PRs through full
   validation. If an incident is active, preserve its state and
   recovery requirements during rollback. Restore selected validation
   only after the failing control has been qualified again.

## 6. Failure boundary and Stop the Line

A failed isolated PR blocks that PR from its parent. Its author fixes
the candidate and obtains fresh passing evidence. Unrelated PRs and
agents on isolated work continue. A failed candidate alone cannot
change shared trunk health.

A failing test in a qualifying scheduled full run on shared trunk is
an escaped defect. Stop ordinary trunk merges and ordinary agent code
work across the repository's governed workspaces. A branch based on
an earlier revision participates in the pause and update. An
infrastructure interruption or overdue full result blocks ordinary
trunk merges while evidence is restored. Use the workspace-wide stop
when a failing test is observed. If test failure and infrastructure
failure coexist, the failing-test incident takes precedence.

| State or event | Required action |
| --- | --- |
| Healthy | Admit ordinary work under the current PR policy. Record the latest verified full trunk result. |
| Trusted scheduled evidence reports a failing test | Open a durable incident for the failed trunk SHA and run attempt. Block ordinary trunk merges and pause ordinary governed code work. |
| Authorized repair candidate passes the full suite | Permit only the exact authorized repair to merge, after normal review and other gates. Keep the line stopped. |
| Repair merges | Trigger a full run immediately on the resulting trunk SHA. Record the merge, repaired revision, and incident binding. |
| Full recovery run passes on current repaired trunk | Record trunk as recovered. Start workspace updates while ordinary merges and code work stay stopped. |
| All governed workspaces verify the fix | Reopen ordinary merges and code work. Require refreshed PR evidence for the applicable base. |
| Recovery fails or evidence is missing | Keep the incident open. Continue diagnosis and repair or CI recovery. |

### Incident and merge authority

Retain the incident identity, repository and ref, observed failed
revision and run attempt, failure classification, repair owner and
eligible PR, state version, recorded merge and trunk recovery proof,
workspace roster, acknowledgments, and timestamps. State changes are
durable and ordered. Duplicate or out-of-order events are idempotent.
Late passes for another revision or incident cannot clear the stop.
A verified infrastructure-only failure may recover without a source
PR after an authorized operator records the diagnosis and resolution
and a new full run passes on current trunk. This exception cannot
clear an incident with a recorded failing test.

Bind one active repair candidate to the incident at a time. Its scope
is the failure and its cause. Require the full suite on its exact
proposed merge against current trunk. Recheck the candidate, base,
controls, review, and active repair authority at merge. A head or base
change invalidates the old proof. A repair merge is one allowed
operation, with provider readback before retrying an ambiguous merge
response. A passing repair PR is insufficient to reopen the line.
Retain the stop if the resulting trunk revision fails, its proof is
incomplete, or it differs from the recovery run's pinned revision.

If the failed scheduled revision is older than live trunk, still
record the stop. The proposed recovery rule permits the incident owner
to recognize an already-landed repair PR only with exact full-suite PR
evidence, proof that the delivered change fixes the recorded defect,
and proof that current trunk contains it. The same incident-bound
full trunk run and workspace update remain required. Otherwise keep
the stop and use the ordinary incident repair path.

Authorize ordinary merges at the actual merge boundary. Serialize the
recording of a trusted stop, merge eligibility, repair admission, and
restart through one authority. A cached green PR or pre-stop queue
entry has no authority to merge after a stop is recorded. A merge
already committed before detection is part of the shared baseline
that recovery must account for. During a stop, defer ordinary delivery
validation against stopped trunk. Candidate jobs and their credentials
cannot alter the stop or its release conditions. Preserve review and
required check enforcement on the authorized merge path.

The live trunk rules at design time require PRs and prohibit deletion
and force pushes. They do not require a health check. The proposed
enforcement shape is one trusted merge actor behind branch protection,
or another host-enforced route that proves the same semantics. A
commit status set once at PR creation cannot prove current eligibility.
Prove the enabled merge paths, including API, web, direct push,
automation and any configured merge queue, in an isolated repository
before cutover. Detect protection drift and hold the gate on
unverifiable authority or state. Keep full PR validation if the
enforcement cannot be qualified. [GitHub ruleset options](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) · [Scheduled workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

### Agent pause and workspace delivery

Capture the roster of enrolled governed workspaces for the repository
when the stop is recorded. Use the shared incident decision at pickup,
resume, and governed execution boundaries. Notify running sessions.
At the first safe interruption point, agents preserve working trees,
locks, pending operations, and evidence. Allow read-only diagnosis,
incident repair and its review and validation, and the later workspace
update. Ordinary code work remains paused. Qualification must show the
required behavior across the supported harnesses and across clones.
Unmanaged processes cannot acknowledge a governed update.

After trunk recovery, each workspace fetches and integrates the fixed
upstream through its normal workflow. Preserve local changes and
resolve conflicts without discarding work. Record evidence that the
workspace's updated base contains the fix, that the update was made
for this incident, and that its pickup and applicable validation are
fresh. Use the roster and these acknowledgments as a restart barrier.
A disconnected workspace or unresolved update holds the barrier.
A missed notification is handled at the next governed boundary.
A new or reopened workspace can enter ordinary work only after its
base contains the fix. Stop or restart state alone never counts as
evidence of a workspace update.

## 7. Required acceptance evidence

| Area | Proof to retain |
| --- | --- |
| Selection | A direct import, a multi-hop witness, a cross-package path, a fixture or subprocess declaration, a changed test, and a positively classified non-test change. Verify the reported path and exact selected ID for each case. |
| Unknown impact | Renames or deletions across snapshots, missing Git inputs, unresolved runtime dependencies, changed CI controls, and selector failure. Show exact full fallback or a blocked result when full evidence cannot be established. |
| Shard correctness | Serial and parallel runs on the same candidate. Show separate runners, complete disjoint assignments, matching outcomes and coverage, and refusal of missing, duplicated, stale, mismatched, or unexpectedly skipped outcomes. |
| Timing | Cold and warm timing, queue, setup, test and evidence timings for the three budgets, runner cost, and observed savings for selected feedback. |
| PR isolation | A failing isolated PR cannot merge. An independent PR can validate and merge and its agent can continue work. |
| Escaped defect | Inject a scheduled trunk failure missed by PR validation. Prove an already-green PR, a queued PR, and direct or alternate update paths are blocked. Show active agents on both affected and earlier bases pause. |
| Repair and restart | Reject TIA-only and stale full repair proofs. Allow the exact full-passing repair through normal review. Prove a failed, stale, incomplete, or wrong-revision recovery does not reopen the line. Prove repaired trunk passing allows workspace updates and a disconnected workspace holds restart until its fix receipt is verified. |
| Failure of controls | Exercise duplicate and out-of-order events, a repair merge with ambiguous acknowledgment, an already-landed repair for a failing older revision, protection drift, stale health, and infrastructure-only recovery. Show no ordinary merge through an active stop and no infrastructure exception for an observed failing test. |

## 8. Decisions reserved for the implementation plan

Choose the Python resolver and test classification encoding, the exact
artifact schema, shard balancing method, health storage, workspace
enrollment mechanism, and provider enforcement design. Document
compatibility with #103, test limits and costs, and the exact
qualification sequence. Propose the sample window, schedule and
freshness limits, and any replacement PR coverage requirement for
cutover review. Gate activation requires separate reviewed evidence and
owner authorization. This specification is the input to that plan once
the team accepts its exact revision.
