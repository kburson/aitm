---
kind: draft
slug: test-impact-analysis
title: AITM test impact analysis, CI sharding, and Stop the Line
created: 2026-11-10T15:15:29Z
updated: 2026-11-10T15:20:17Z
---

**Status:** Draft for owner review.

## Purpose

Give a story's author and reviewer fast test feedback with enough evidence to
understand why each test ran. Preserve a complete regression check as the
repository grows. Start with AITM's own Python and pytest suites. Keep the
execution-plan and evidence formats independent of pytest so later package
providers can add their own dependency discovery and test collection.

The original ai-task-manager combined a reverse import graph with filename
matches and declared dependencies. It selected both direct and transitive
consumers but reported only the endpoints and the type of match. An unmatched
path could be treated as having no verification impact. Its CI ran separate
unit, integration, and slow jobs and verified the union of shard receipts.
Carry forward the graph and receipt patterns. Require a traceable dependency
chain and a full-suite fallback for uncertainty.
[Legacy selector](https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/test-impact-selector.mjs#L120) ·
[Legacy CI workflow](https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/.github/workflows/ci.yml#L103)

The current [AITM CI design](../103/design/github-ci-quality-gates-design.md#coverage-and-test-scaling)
requires full candidate validation. In [one hosted PR run](https://github.com/kburson/aitm/actions/runs/42837579428),
746 tests passed in the candidate Python job and required CI finished in
3 minutes 40 seconds. That run predates the proposed suite classification and
provides a single baseline observation.

## Select the story's tests

- Resolve the complete change set. For hosted validation, use the exact
  applicable base and tested candidate, including the validated PR head and
  synthetic merge identity where relevant. For local feedback, include
  committed changes from the story base, staged and unstaged edits, and
  relevant untracked files. Include both sides of renames and use the base
  graph to identify former consumers of removed or moved paths. Local results
  describe the inspected working snapshot. Hosted evidence is required for
  the applicable PR gate.
- Resolve Python imports and package dependencies against repository inputs.
  Add reviewed relationships for shared fixtures, pytest configuration,
  subprocess and installed CLI entry points, data files, and runtime
  dependencies the import graph cannot see. Follow reverse dependencies
  across package boundaries. Select new and changed tests directly. Begin
  with test-file granularity where a finer dependency cannot be established
  and expand selected files to the exact pytest IDs in the plan.
- Give every changed path a recorded disposition. For each changed file and
  selected test it affects, retain at least one deterministic path through
  the dependency graph, with edge kinds and the source of declared edges.
  Label directly changed tests and policy-mandatory tests with their own
  reasons. Report a known non-test input only when the trusted policy can
  positively classify it. A missing match or a filename convention cannot
  justify skipping a test.
- Any uncertainty about impact triggers the full applicable suite on the
  same candidate. Examples include missing Git inputs, an unresolved
  dynamic dependency, an unclassified file or test, missing inventory, or
  a change to trusted selection controls. Broad inputs may select every
  test even when the graph is sound. If CI cannot establish the exact
  candidate or run the required full suite, validation fails. A test
  failure in the selected set remains a failure.
- The story and CI summary show the exact base and candidate, selection or
  fallback mode, and planned and executed counts by package and test type.
  The detailed artifact records selected IDs, their paths and reasons,
  per-file dispositions, fallback reasons, inventory and policy identities,
  job assignments, actual outcomes, and timings. Use trusted selection
  policy from outside the candidate's control. A PR cannot loosen its own
  selection, inventory, or merge rules.

## Classify and distribute the suite

Package ownership and test type are independent. Start with unit,
integration, and system or slow tests. Mark required runner capabilities and
isolation constraints separately. Every collected test has a known owner,
type, and execution lane. One inventory drives local commands, selected
runs, full runs, and the CI collector.

Run independently executable shards as individually named GitHub Actions
jobs on separate hosted instances. A job name identifies its package or
package group, test type, and shard number. Keep tests with shared state or
host-specific requirements together until isolation is demonstrated. Keep
required Darwin and APFS coverage on qualified runners. Use observed
durations to balance eligible shards, with a stable assignment for the
same inputs. Let the builder choose shard counts, test markers or paths,
and concurrency caps using measured runner startup costs and availability.

For the exact candidate and run attempt, compare the union of shard
outcomes against the intended inventory. Reject missing, duplicate,
mismatched, or unexpectedly skipped work. Keep the existing comparison
with trusted base inventory and outcome evidence so a PR cannot silently
remove or disable required cases. Combine only compatible evidence from
the same candidate and run attempt. A full run includes required subprocess
coverage and applies the existing 90% per-product-package line floor.
Report partial-run coverage with its actual scope. Wheel validation,
file checks, and other required checks follow their own policy.

| Suite | Target elapsed time |
| --- | ---: |
| Unit | Under 3 minutes |
| Integration, all shards combined | Under 6 minutes |
| Full, all required test lanes combined | Under 10 minutes |

Measure wall-clock time across jobs, from first shard start through the
last required shard outcome. Track queue, setup, test execution, evidence
collection, and total PR feedback latency separately so shard startup and
runner contention remain visible. Compare cold and warm samples. Treat
the targets as operating budgets and surface sustained misses.

## Introduce selection without losing the full check

1. Classify and time the full suite. Verify that the sharded inventory,
   outcomes, required platform coverage, and combined coverage agree with
   the serial baseline.
2. Run TIA in shadow on representative changes while full PR validation
   remains authoritative. Compare the selected IDs with full-run outcomes
   and use seeded regressions and known dependency paths to exercise
   omission detection. A green full run alone cannot show whether a
   skipped test would have caught a regression.
3. Enable affected-test feedback during story development. Make ordinary
   PR validation affected-first only after evidence supports selection,
   sharding alone can no longer reliably keep the full suite under
   10 minutes, and the owner approves the new gate policy. That policy
   must define coverage evidence for selected runs and when full
   validation is mandatory. Uncertain candidates still run the full
   suite before their PR can merge.
4. Before switching the PR gate, establish an independent scheduled full
   run of the configured suite on a pinned trunk revision. Qualify Stop
   the Line end to end, including an immediate full run after a repair
   merges. The builder proposes schedule cadence, freshness policy, and
   the sample window for sustained budget misses.

## PR failures and Stop the Line

A failure confined to a PR blocks that PR through its ordinary required
checks. The author repairs the candidate and reruns validation before
it can merge into its parent branch. Record the failure against that
candidate. Leave other PRs and agents on unaffected bases free to
continue. A candidate failure alone does not put the shared line into
a stopped state.

Stop the Line applies when the scheduled full run finds a failing test
on shared trunk. A defect escaped the PR gates and entered the shared
baseline. Block ordinary trunk merges and pause ordinary agent code work
across the repository's governed workspaces while the fix is delivered.
A workspace on an earlier base also takes the fix before ordinary work
resumes.

| Event | Effect |
| --- | --- |
| A test fails on an isolated PR | Block that PR. Other isolated PRs and workers continue. |
| Scheduled full suite finds a failing test on trunk | Block ordinary trunk merges and pause ordinary code work across the repository's governed workspaces. Record the failed trunk SHA and run attempt. |
| Authorized repair PR passes the full suite | Permit that exact repair candidate to merge after its required review and other gates pass. Keep ordinary trunk merges blocked. |
| Repair merges | Immediately run the full suite on the resulting trunk SHA. Keep the line stopped. |
| Full run passes on current repaired trunk | Record trunk as recovered and distribute the fix. Ordinary work stays paused during the workspace update. |
| All governed workspaces verify receipt of the fix | Restart ordinary merges and code work. |
| Full run on repaired trunk fails or its evidence is incomplete | Keep the line stopped. Continue repair or CI recovery. |
| Verified CI-only incident is resolved and current trunk passes a fresh full run | Restart the line without a source repair PR. |

Record the affected repository and ref, source SHA, workflow run and
attempt, incident identity, repair owner, and current disposition.
An unavailable or unverifiable scheduled result requires recovery and
cannot authorize ordinary trunk merges once the expected evidence is
overdue. The scheduler can delay or drop runs, so absence must be
detectable. [GitHub Actions schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

Bind the repair PR to the active incident and limit it to diagnosing and
correcting the failing test or its cause. Require the full suite on the
exact proposed merge candidate against current trunk. Revalidate if the
head, base, or validation controls change. For a failing test, clear the
stop only after an authorized repair merges and trusted full-suite
evidence passes on the live repaired trunk SHA for the active incident.
Proposed recovery default for CI-only incidents such as a lost runner:
an authorized operator records the infrastructure diagnosis and
resolution, then a fresh trusted full pass on current trunk clears that
incident. This exception requires evidence that the incident contained
no failing test.

Enforce the stop at the governed trunk merge boundary. Suppress ordinary
delivery validation that would test a merge against the stopped trunk.
An already running check may finish, but its result cannot authorize a
merge during the stop. Reject stale green checks and queued merges.
Serialize stop, repair admission, merge, and restart decisions so
cached checks and concurrent updates cannot bypass the stop. At the
design baseline, the live trunk rules require a PR but do not require a
health check. The merge authority and its credentials must sit outside
candidate-controlled jobs. Prove that GitHub's enabled merge paths
honor the stop, including direct updates and queued merges where
applicable. If an ordinary merge can still get through while stopped,
keep the current full PR gate.
[GitHub ruleset configuration](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository)

Record the governed workspace inventory for the incident and notify
agents of the stop and the failed trunk SHA. Agents pause at the first
safe interruption point and preserve their working trees,
locks, and evidence. Incident diagnosis, repair, review, and validation
can proceed. An infrastructure-only interruption blocks ordinary trunk
merges while CI recovers. Apply the repository-wide code pause when the
scheduled run reports a failing test.

After repaired trunk passes, agents fetch and integrate the repaired
upstream into their local branches through the normal workflow,
preserve in-flight changes, resolve conflicts, and refresh pickup and
validation against the repaired base. Record evidence per workspace that
its updated base contains the fix. Restart ordinary work after every
governed workspace in the incident inventory has acknowledged the
update. A disconnected workspace or a workspace with unresolved
conflicts holds the restart until its update can be verified. Check
the incident on pickup and resume as well as at the merge boundary.
A new or reopened workspace joins ordinary work only on a base that
contains the fix. Ordinary PRs targeting trunk need fresh validation
against the applicable base.

## Acceptance evidence

- Show a real changed file with direct and transitive test consumers and
  one declared non-import dependency. Verify every reported edge and
  exact selected ID. Show a package crossing and a new or changed test.
- Exercise deletion or rename, an unresolved runtime dependency, a
  shared configuration change, missing analysis inputs, and a positively
  classified non-test change. Verify that unknown impact runs the full
  suite and records the reason. An unexecutable fallback fails the gate.
- Compare serial and sharded full results on one pinned candidate. Show
  separate named jobs, every expected ID exactly once, and matching
  coverage. Demonstrate rejection of missing, duplicate, and stale
  shard evidence. Report timings against all three targets.
- Rehearse a failure confined to a PR. Show that PR cannot merge while
  an unrelated PR can validate and merge and its agent can continue.
- Rehearse a scheduled full run that exposes a defect missed at PR
  validation. Prove already-green and queued ordinary PRs cannot merge
  into trunk and ordinary agent code work pauses across active
  workspaces, including one based on an earlier revision. Prove a
  passing TIA-only repair and stale full-suite repair evidence cannot
  authorize a merge. Merge the authorized, exact full-suite-passing
  repair and prove that a green trunk run opens workspace updates.
  Show ordinary work stays paused until every governed workspace has
  integrated the fix, including a disconnected workspace that returns,
  updates its branch, and refreshes its evidence.
- Demonstrate that a late success for a different revision or an older
  incident cannot restart the line. Show that a failed or incomplete
  post-repair run leaves it stopped. Exercise an infrastructure-only
  recovery and verify that its exception cannot clear a failing-test
  incident.

## Scope decisions

The proposed first release covers AITM's Python suite and existing hosted
CI. Defer extra language providers, historical ranking, a generalized
project-health service, and release-policy changes. Keep test selection
deterministic and auditable. The implementation plan can choose the graph
representation, receipt encoding, shard allocator, and health storage,
provided they satisfy the evidence and enforcement requirements above.
