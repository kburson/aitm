# Legacy resident actions and evidence

C108 [#495][story] records action, recovery and evidence facts for the legacy
qualification slice. The source is commit
`c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905` and Git tree
`844ae26bb169e8618e45fc3b1aedb57f44896fe0`. The [guard inventory][guards]
records the separate entry and exit checks. The [C110 decision fixture][decision]
owns policy dispositions and proof vectors for the configured workflow.

## Registered actions

| State | Registration | Serialization | Completion evidence |
| --- | --- | --- | --- |
| Develop | [`developVerificationAction`][develop] | Issue lock | Current, structurally valid Develop-final receipt for the issue and HEAD with every required command classification passing |
| Test | [`testQuickCiAction`][test] | Correlation intent | Complete provider observation for exact HEAD, or matching parsed Test receipt on the compatibility read path |
| Review | [`reviewAgentValidationAction`][review] | Issue lock | Applicable current Plan approval, complete review evidence, and a passing validation timestamp at or after the current Review visit |

**Develop.** The action checks its optional receipt reader before parsing the
issue body. `run` pauses when finalization or persistence capability is absent,
fails on unsuccessful finalization or a missing receipt, and persists a
successful receipt before returning it. The shared runner rehydrates and
verifies the persisted result before resolving its action event. Repository
finalization and its receipt are separate from the state move. [Develop
action][develop] · [Develop action tests][develop-test].

**Test.** With a provider observer, completion requires its `complete` result
and the same HEAD as the hydrated snapshot. Without that capability, the
compatibility verifier requires a parsed Test receipt and a string HEAD that
matches its commit. `startOrObserve` can produce completion, waiting,
infrastructure waiting, source failure, or an indeterminate pause. Waiting
retains deadline and correlation. Source failure carries a rework reason.
Missing start capability pauses the action. [Test action][test] ·
[Test action tests][test-test].

**Review.** The action revalidates any applicable Plan approval against
current source and scope. It then assesses the hydrated issue body, comments
and changed paths. Failure and pass use explicit persistence ports. A failed
current Plan approval can stamp a failure through its configured port.
An authorized semantic waiver has its own outcome and evidence. A fresh
validation pass must belong to the current Review visit. A retained failing
carrier or stale pass requires further work. [Review action][review] ·
[Current approval tests][approval-test] · [Review action tests][review-test].

## State entry and recovery

The [State Cursor][cursor] records the target state and visit, then resumes
its registered actions from the hydrated snapshot. An invocation for the
same state can resume the current visit. The transition and the subsequent
action outcome have distinct identities and reporting. Tests cover
interruption around state and resident effects. [Cursor interruption tests][cursor-test].

The [shared runner][runner] applies the following order.

1. Hydrate the action ledger for the specific issue, state visit, action ID
   and definition. An unavailable ledger pauses. Verify current proof first.
   Current proof can resolve an open intent or wait when writes are authorized.
   The resolution distinguishes matching correlation from independently
   observed proof. A waiver needs a durable matching waiver event.
2. An existing waiting event requires a usable correlation and valid
   deadline. A live wait returns the same correlation and deadline. An
   expired wait returns an expired observation on a read-only invocation.
   An authorized writer appends failure at the deadline.
3. Before a new effect, require write authorization. An open intent can reuse
   its correlation. Otherwise obtain the repository's correlation and take
   the issue lock or correlation intent according to the action. Contention
   pauses. Append intent, rehydrate the visit, and stop on visit drift before
   submitting. Managed actions evaluate the relevant provider boundary at
   the effect point.
4. After submission, rehydrate and verify. A reported completion needs
   current observable proof. A waiting result is returned as durable only
   after the written wait reads back with matching correlation and deadline.
   Failure and waiver are recorded with distinct phases. Missing proof,
   invalid results or a missing capability remain paused.

The action ledger codec uses `aitm.resident-action-event/v1` and
`aitm.resident-action-head/v1`. Event phases are `intent`, `waiting`,
`resolved`, `failed` and `waived`. An event retains issue, state visit,
action ID, attempt ordinal, time and correlation. Global and action-specific
predecessors pair comment IDs with hashes. A head can live inline in the issue
body or point at a spilled protected comment. Readback validates the head and
event chain. A clean ledger is a precondition to runner recovery. Tests cover
exact retry no-op, stale expected head, altered events, ambiguous orphan
recovery, fresh attempts after failure and revalidation before submission.
[Ledger codec][ledger-codec] · [Ledger reader][ledger-read] ·
[Recovery tests][resume-test] · [Runner contract tests][conformance-test].

## Evidence and migration

### Verification and historical formats

The receipt schema is `aitm.verification-receipt/v1`. It carries the issue,
stage, commit, receipt ID and command results. The fuller validator also
checks required command authority and applicable source and artifact
fingerprints. Preserve the distinction between a parsed issue marker,
a structurally valid record and proof applicable to the current inputs.
Develop-final defaults to successful full lint and format. A project provider
can supply its required Develop classifications. The default Test receipt
adds unit, integration and slow test classifications. A Test provider can
supply its own required classifications. A proven docs-only lane skip in
the default profile can drop eligible Test lanes while retaining lint and
format.
[Receipt schema and verification][receipts] · [Lane-skip proof tests][lane-tests].

The proof-marker reader accepts consolidated verifier fields and historical
`verified-at` values, including the older packed commit and timestamp form.
It normalizes old keys while retaining the legacy data needed for reading
history. An authored verification declaration and an executed result have
distinct meanings. A body field, checkmark or copied receipt supplies a
projection or a claim until the applicable source and authority checks
qualify it. [Proof-marker parser][proof] · [Reviewed scope checks][scope].

### Review, source and closeout

Separate Test evidence, the Review resident action's semantic validation
and independently approved source. The Review action receives current source
HEAD and planned scope inputs. The GitHub lifecycle evidence schema
distinguishes agent Test and Review passes from human or full-auto approval.
Acceptance checks the retained record ID, expected commit, contract epoch,
authority grant and authority epoch. The reviewed-scope reader resolves the
authorized issue and artifact context, rejects stale or ambiguously copied
proof, and retains typed blockers when evidence cannot be read or verified.
Closing then checks its own marker and lifecycle-chain inputs, issue
cleanliness and positive delivery to the resolved lineage target. A child
can be delivered to the parent branch. An epic's surviving source branch
and its later upward delivery are distinct. A verified lineage target remains
applicable across unrelated trunk movement.
[Review evidence][review] · [Lifecycle evidence][lifecycle-evidence] ·
[Reviewed-scope authority][scope] ·
[Close gates][close] · [Close-lineage tests][close-test].

Where evidence cannot establish a source, time, candidate, outcome or
required scope, carry the uncertainty forward with the originating record.
The action-ledger phase or a body projection alone cannot establish the
execution result. The tests below establish the named scenarios in the
pinned checkout. Provider-specific production authorization remains in
[C109][authority].

### Kind differences

- Code uses its applicable commit-bearing verification and source-delivery
  evidence.
- The docs-only kind remains commit-bearing. A current receipt with a proven
  docs-only change and every permitted dropped lane can qualify the reduced
  Test suite.
- Audit, research and spike work can use an approved non-commit deliverable.
  The kind marker alone supplies no delivery proof.
- Coordination epics share the no-commit verification path for their own work.
  Their children's required deliveries and the upward delivery of an applicable
  integration source still have separate lineage checks.

[Kind predicates][kind] · [Code Complete kind evidence][kind-code] ·
[Lineage close][close].

## Verified legacy scenarios

Eight pinned Node test files reported **137 passing cases** with the repository
lockfile on Node 26.8.1. These cover the three resident actions, same-visit
resume, interrupted state entry, exact-head evidence, current Plan approval,
runner conformance and close lineage. The linked source files describe the
other historical formats and applicability rules at the same commit.
[Develop tests][develop-test] · [Test tests][test-test] ·
[Review tests][review-test] · [Conformance][conformance-test] ·
[Resume][resume-test] · [Cursor interruption][cursor-test] ·
[Current Plan approval][approval-test] · [Close lineage][close-test].

[story]: https://github.com/kburson/aitm/issues/495
[guards]: guard-facts.md
[decision]: https://github.com/kburson/aitm/issues/497
[authority]: https://github.com/kburson/aitm/issues/496
[develop]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/resident-actions/develop-verification.mjs#L34
[test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/resident-actions/test-quick-ci.mjs#L9
[review]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/resident-actions/review-agent-validation.mjs#L142
[cursor]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/state-cursor.mjs#L373
[runner]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/resident-action-runner.mjs#L127
[ledger-codec]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/resident-action-ledger-codec.mjs#L5
[ledger-read]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/resident-action-ledger-read.mjs#L85
[receipts]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/verification-receipt.mjs#L20
[proof]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/proof-marker.mjs#L91
[scope]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/reviewed-scope/readiness.mjs#L71
[lifecycle-evidence]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/github-records/lifecycle-gate-source.mjs#L12
[close]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/close-gates.mjs#L271
[kind]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/issue-kind.mjs#L25
[kind-code]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/task-tracker/lib/develop-exit-code-complete-guard.mjs#L54
[lane-tests]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/core/docs-only-lane-skip-completeness.test.mjs#L103
[develop-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/verbs/develop-state-action.test.mjs
[test-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/verbs/test-state-action.test.mjs
[review-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/verbs/review-state-action.test.mjs
[conformance-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/state-action-conformance.test.mjs
[resume-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/state-action-resume.test.mjs
[cursor-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/state-cursor-interruption.test.mjs
[approval-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/verbs/review-current-plan-approval.test.mjs
[close-test]: https://github.com/kburson/ai-task-manager/blob/c8b64b6b2d0e404cbae9a1d5eced7d94c36b4905/scripts/tests/unit/task-tracker/lib/close-gates-lineage.test.mjs
