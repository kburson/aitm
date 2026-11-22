# #362 Scheduled sweep failure flag implementation plan

**Goal**

Give a maintainer and an agent one current advisory they can check for the last verified scheduled category full sweep result.

**Architecture**

Identify the production sweep from authenticated Actions metadata, then publish one durable advisory record and provide a read-only check. The two spikes deliver independent, reviewable contracts before the writer or reader enters development.

**Scope**

[Refined epic](../story.md), [#361 sign-off](../../361/retro/2026-11-21-361-sign-off.md) and [scheduled acceptance receipt](../../361/attachments/2026-11-21-361-scheduled-acceptance.json).

## Acceptance

- Bind the flag to `kburson/aitm`, `.github/workflows/category-full-sweep.yml` (workflow ID `425235652`), `trunk`, and the `schedule` event. The first verified execution is [run 44864075824, attempt 1](https://github.com/kburson/aitm/actions/runs/44864075824/attempts/1). It arrived 4h 39m after the expected slot. Registration lag and a missing slot are distinct from a completed failure.
- Publish one active flag with an exact attempt link, timestamp, and source identity on a qualifying failure. Clear it only on verified success from a distinct, later scheduled run. Keep the last known decision through cancellation, incomplete evidence and provider errors. Show unavailable distinctly when the check cannot read a valid record.
- Verify failure to active, later success to clear, and stale, duplicate, unrelated and missing evidence through controlled replay using the actual writer and reader. Use an isolated record for replay and verify afterward that the live advisory matches the last authentic eligible run. Confirm the deployed read path against authentic scheduled evidence at epic sign-off. Preserve the result and note which transitions used replay. Leave production tests and schedule operable during validation.
- Keep the flag advisory. Merge rules, required checks, changes to sweep cadence, workspace control and repair ownership are outside scope. The publisher operates outside the sweep workflow. Its only mutation is to the advisory record, with no permission to alter the sweep conclusion, schedule, merge checks or protection. Authenticated Actions history determines state. Completion and operator events only trigger reconciliation. #361 is delivered source evidence. The existing internal dependency graph covers the rest of this work.

## Sequence

The epic enters Dev before any child starts. The spikes can proceed independently. The story planning records carry the proposed publisher and reader interfaces and test contracts. Promote receipt-dependent decisions to JIT once the corresponding spike is accepted.

| Child | Prerequisite | Evidence to hand forward |
| --- | --- | --- |
| [#363](../../363/story.md) | Epic in Dev | Authenticated event, workflow and attempt identity, ordering key and comparison, activation floor, failure, success and ignored outcomes |
| [#364](../../364/story.md) | Epic in Dev | One durable location, atomic decision and watermark schema, write and read permissions, unavailable-state behavior |
| [#365](../../365/story.md) | Accepted and compatible #363 and #364 receipts | Idempotent writer, transitions and replay, exact-head review, deployed readback |
| [#366](../../366/story.md) | Delivered #365 | Human and agent check, validation against recorded and deployed states, exact-head review |

A receipt is accepted after its independently reviewed PR lands on planning and its evidence passes delivery verification. At #365 JIT, explicitly confirm the receipts agree on the persisted ordering key, baseline and unavailable-state behavior. The working proposal is a dedicated repository issue with one machine-readable record and a generated human summary. A small, independent listener reconciles authenticated Actions history and writes only to that issue. It polls history when it receives a completion event or an authorized operator requests reconciliation. A fixed writer concurrency group shared by both triggers and a persisted run watermark protect against replay and arrival order. The spike in #364 owns the final storage decision and #363 owns the exact run eligibility rules.

## Review and delivery

Use the [manual delivery checklist](../../../../manual-delivery-checklist.md) and declare the branch target for every child. Deliver each research receipt via a PR into `planning`, and each implementation via its own PR into `trunk`. Obtain an independent Grok PR review on every child PR before merging, including the two receipt PRs. Record the PR base, head, tree, Grok model, verdict and review link, with off-platform provenance if the repository account relays Grok's review. Resolve review findings and conversations, rerun required verification and obtain fresh Grok review when the reviewed candidate changes. If Grok is unavailable, hold the merge. Confirm applicable branch checks for the exact candidate, including canonical CI and the trusted verifier for trunk PRs.

Verify delivery, sign off and reconcile issue closure, Project status and the local ledger for each child. After all four children have cleared their own gates, record the epic acceptance evidence and sign-off before closing #362.
