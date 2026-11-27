# M2 design draft — GitHub provider and first hosted delivery

Issue [#524](https://github.com/kburson/aitm/issues/524) · Product epic #1

## Goal and boundaries

Deliver aitm-github as an independently installable provider for released Core. It supplies GitHub backlog, Projection, hosted delivery and setup capabilities through Core’s versioned interfaces. The first capability is the read-only historical source path [#525](https://github.com/kburson/aitm/issues/525), which M7 #522 can consume before the remaining M2 work ships. Core owns story state, authorized operations, evidence, attempts and dispatch admission. The provider owns exact GitHub request/response translation and scoped host verification.

M2 depends on [Core release #72](https://github.com/kburson/aitm/issues/72). The source-access child qualifies against that release and ships as a bounded adapter slice. It requires no hosted story or PR writes and no M3 runtime capability. The governed hosted mutation paths require their existing qualified broker, host and M3 runtime boundaries. Distinguish installed, enabled, and live-qualified capabilities in discovery and doctor output.

## Capability and ownership map

| Slice | Contract and acceptance boundary |
| --- | --- |
| Legacy read-only source | Inventory scoped issues and their consented evidence fields, expose source identity and pagination, and qualify one deterministic pinned fixture plus a bounded live read against the approved repository. M7 owns the full crawl, corpus capture and validation. |
| Backlog identity and hierarchy | Create permanent issue identities and reconcile separately scoped parent/dependency writes. Keep issue/Project projections subordinate to the planning record. Verify uncertain outcomes before sending another create or relationship write. |
| Project projection | Use qualified reads and writes for explicit field mappings and supported triggers. Reconcile latest published owner/version, suppress stale writes, report conflicts and reconcile lost responses. Reuse Core’s durable actions and scope. |
| Hosted PR, CI and delivery | Provision a draft at authorized Dev pickup, retain exact branch and PR identities, verify current host CI, reconcile retarget and merge, and retire exact resources only where qualified. |
| Init and protection | Discover or create the approved Project and validate configuration. Read back supported branch protections, expose authorization and host gaps, and surface an actionable manual result when enforcement cannot be proved. |
| Hosted interoperability | Prove Core-only fallback, a narrowly scoped installed provider, source access with a read-only credential, sandboxed hosted fixtures, and later separately authorized live qualification. |

## Read-only source access for M7

Expose a paged read interface with an explicit source repository, cutoff, field selection and cursor. Use the approved legacy repository kburson/ai-task-manager for live qualification. Verify canonical repository identity before collecting issue data. Return stable issue and comment IDs, timestamps, source locators, selected raw fields or streamable bytes, a digest, continuation state, and typed complete, unavailable, or incomplete results. The return value must let M7 distinguish unavailable content from empty content and reproduce its capture decisions. Start with issue bodies, approved Timing Log comments and the minimal metadata M7 needs. The initial issue payload includes repository and issue IDs, issue number and URL, state, creation/update/closure timestamps and body bytes or their explicit absence. The selected comment payload adds comment ID, issue ID, URL, creation/update timestamps and body bytes or their explicit absence. Pin M7’s approved Timing Log selection predicate and its version in the qualification configuration. Commit or adjacent evidence needs its own contract before becoming a required source.

The cutoff admits issues and comments created on or before it. An observed update after the cutoff is identified as later-edited with preserved acquired bytes and timestamps. The result cannot claim those bytes reflect the past cutoff. Exact replay reads the captured manifest and bytes. A live reread has its own acquisition time and may drift. Use documented REST endpoints where their fields suffice, bounded pagination, and read retries. Bind cursors to canonical source identity, cutoff, selected fields and expected page state. An untrusted cursor, wrong repository, unexpected page discontinuity, unsupported redirection, or denied scope produces an explicit refusal or incomplete result. Do not infer a repository-wide snapshot guarantee from a live list response. Preserve acquisition scope, cutoff, digests and pagination evidence for M7’s later immutable corpus snapshot. A complete result proves the requested bounds are exhausted. It can contain zero records. Unavailable means authority or a required capability prevented a result. Incomplete means an admitted scan returned data without proving the requested bounds. A read credential and the read-only adapter surface are separate from mutation credentials. Logs and receipts contain permitted locators and proof, with credential values excluded.

**Handoff proof.** Run a reproducible multi-page fixture including a missing page, bad cursor, rate limit and authorization failure. Against the approved legacy repository, verify an exact bounded inventory and a representative allowed evidence read without a host mutation. Show that wrong and unapproved repository scopes refuse before collection. Pin the bounded live acceptance input at JIT with an approved repository identity, issue and comment limits, cutoff, expected evidence markers, and reviewable receipt output. Publish the versioned source interface, deterministic fixture and sanitized capability receipt. The adapter registers through Core’s released extension discovery surface. The M2 provider owns the dedicated read interface. A compatible wheel with an exact version, source revision and digest must be independently installable and available to M7 before the handoff qualifies. The M7 consumer verifies the receipt and version. M7 then owns full extraction, corpus normalization, provenance and import qualification.

## Hosted delivery and projection

- Map Core’s literal declared target, attempt and resource incarnation into exact branch and draft PR associations. Separate each external effect claim. Observe uncertain effects before replay. Bootstrap drafts have provisioning evidence and require independently current implementation CI.
- Consume Core’s authorized push, observation, retarget, ready and merge contracts. Bind hosted evidence to exact PR, source, target/base and tested tree as applicable. Enforce the existing default-target receipt boundary from #158 and corresponding Core host-admission rules. Retain the reviewed handoff for non-default and composed-source delivery.
- Gate projections on the corresponding shared planning publication. Scope Project field ownership and distinguish board edits awaiting a policy disposition from permitted updates. Read back writes and their exact versions. Reconcile sparse state projections plus separately authorized later timing and Cost updates.
- Never replace missing host assurance with a local cache. Rule-set and branch protection capability must be tested against the configured repository. The historic proposal for an every-push planning audit remains a design decision until the trigger and authority constraints are proved. Production changes require separate authorization.

## Acceptance and open decisions

1. Qualify the released source-access contract and exact handoff receipt independently of all board, PR, protection and M3 work.
2. Exercise issue create/recovery, hierarchy, Project replay, and conflicting changes with deterministic fixtures. Qualify the matching host behavior on approved disposable resources.
3. Qualify backlog identity, hierarchy, Project projection and setup with Core fixtures and their own scoped provider authorization. Disposable host qualification for those capabilities can proceed separately from M3 where the selected route has its required identity and host controls. Governed agent PR writes and their live activation require the applicable M3 attestation and broker rules. Use the governed PR handoff and current Core #2 contracts for exact source/target checks, retarget, draft CI, ordered merge and retirement. Verify inability to act outside the authorized scope.
4. Select Project field ownership, permitted manual board edits, and trigger or audit design before activation. Carry the existing #181 C05 timing/Cost qualification dependencies in the Project slice.
5. Decide the issue hierarchy and landing sequence during refinement. Use focused delivery slices with four to six children where applicable and at most four implementation agent-hours per child. Do not make source-access acceptance wait for those later slices.

[Master architecture and milestone plan](../../../000/1/plan/master-plan.md) · [Core’s governed PR handoff](../../../000/2/plan/2026-11-11-2-governed-pr-lifecycle-reconciliation.md) · [Accepted configured workflow plan](../../../000/2/plan/2026-11-26-configured-workflow-implementation-plan.md).

## Delivery handoff and sequencing

[#525](https://github.com/kburson/aitm/issues/525) is the first independently landable slice. Its only native blocker is the released Core #72. It registers the read capability, qualifies an exact installable wheel, and can land on trunk and close under its own receipt while the parent M2 epic is open. Board, PR, protection, M3 and remaining M2 milestones do not gate this slice.

The handoff to [M7 #522](../../522/design/history-import-design.md) consists of the source capability and schema versions, wheel version/digest/source revision, allowed canonical repository and request bounds, cutoff semantics, validation fixture, and a sanitized live capability receipt with result, source IDs, and evidence digests. The handoff proves read eligibility for defined fields and scope. M7 owns full capture and the validated corpus it supplies to [M8 #523](../../523/design/rubric-design.md).

## Refinement estimate and rank

**Rank 250 · XL · 44.5 implementation agent-hours.** XL reflects multiple separately landable provider capabilities. The estimate includes implementation, verification and review, and counts the #525 source-access story once.

| Work | Agent-hours | Basis |
| --- | ---: | --- |
| #525 read-only source capability | 3.75 | Existing bounded estimate for the independently installable handoff. |
| Backlog identity and hierarchy | 7.5 | Issue identity/replay and hierarchy/dependency work, in two bounded slices. |
| Project projection | 3.75 | Existing C05 intake estimate, including mapping, replay, and scoped readback. |
| Governed PR, CI, and terminal work | 19.5 | Five scoped intake estimates, 4, 3.5, 4, 4 and 4 h. |
| Init and protection readback | 6.5 | Two slices for setup and qualified protection or explicit manual disposition. |
| Installed provider integration | 3.5 | Exact wheel, installed routes, and designated fixture proof. |
| **Total** | **44.5** | Estimate at Refine level. Final child estimates and eligibility are settled at JIT. |

Rank is the milestone sequence after the existing 10–240 sequence. The source-access child is the first eligible M2 delivery and can cut through independently. Remaining M2 work may proceed in parallel where its own prerequisites allow.
