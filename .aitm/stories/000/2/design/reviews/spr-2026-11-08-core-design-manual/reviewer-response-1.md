---
schema: aitm.review-response/v0
level: spr
story: 2
role: reviewer
round: 1
artifact_path: .aitm/stories/000/2/design/core-design.md
artifact_base_commit: 73210b6da93942f06a0d6616cf5df02eaf64180c
artifact_digest: sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9
agent:
  host: codex
  provider: openai
  model_id: gpt-6.1-sol
  effort: high
reviewer_session: 01a1bebb-3dd5-7422-8d7e-58de85638746
started_at: "2026-11-09T05:15:14Z"
submitted_at: "2026-11-09T05:17:44Z"
start_basis: recorded
finding_ids: [R1-F001, R1-F002, R1-F003, R1-F004, R1-F005, R1-F006, R1-F007, R1-F008, R1-F009, R1-F010]
answered_finding_ids: []
---

## Summary

The design gives M1 a plausible core-only lifecycle, portable review import and a single write boundary. I checked the complete artifact against the brainstorm decisions, architecture and M1 checkpoint, then walked races involving the store ref, workflow actions, identity creation and evidence. The required changes make the existing guarantees executable under those races and make the local and legacy installation paths unambiguous.

## Findings

### R1-F001 — Candidate ancestry does not prove published continuity

**Guarding the planning branch, lines 138–155, and Publication and reconciliation, lines 272–274.** Validation from the trusted genesis can approve two internally valid linear histories that diverge after the same genesis. If a remote is rolled back or replaced with the second history, the existing clone can validate the candidate, advance its local view and lose previously published operations from the active history. A later repair could also preserve a rewritten history if it only verifies the anchored chain and restoration tree. The design calls rewrites fenced but does not specify the continuity check that distinguishes them from ordinary divergence of unpublished work.

Require a durable last-observed published frontier for the exact store/ref, distinct from the last valid tip and the local unpublished tip. Require the next observed shared ref to equal or descend from the trusted shared frontier, with explicit treatment of deletion, quarantine and verified forward repair. A fresh clone can verify from committed trust anchors and any independently available checkpoint. It cannot claim it has detected a rollback after its latest independent checkpoint. Exercise replacement by a structurally valid sibling and rollback to an earlier valid tip, in addition to the normal divergent-unpublished replay. [Git fast-forward rules](https://git-scm.com/docs/git-push#_note_about_fast_forwards)

### R1-F002 — Ref CAS does not serialize worktree checkout

**Core enforcement, line 144, The planning backend, lines 265–270, and core-run delivery, line 386.** A worktree can switch to planning after the scan and before the ref update. The expected-old OID can still match. The same problem exists without a race when core-run local delivery moves a checked-out default branch by raw ref CAS. The master plan's normal workspace keeps trunk checked out. In both cases a ref move can leave the worktree and index based on the old tree.

Specify the actual ref/worktree exclusion for supported planning writes, including retries and migration. Scope what can be guaranteed against out-of-band Git commands. A preflight scan alone is a snapshot, so any residual race must be addressed by isolation or explicit detection and fencing with preserved checkout data. For code delivery, use a worktree-aware path or refuse core-run mutation of checked-out targets and support observing the ordinary authorized merge. Test the supported checkout boundaries without relying on optional harness hooks. [Git ref updates](https://git-scm.com/docs/git-update-ref#_description) and [Git worktrees](https://git-scm.com/docs/git-worktree#_description)

### R1-F003 — Unique dispatch per intent leaves duplicate graduation intents possible

**Graduation, lines 458–462.** Two clones can independently reserve different operation IDs for the same stable draft ID and unchanged snapshot. Both intents can publish and both senders can acquire their own dispatch claims. Both can issue a provider identity before either removes the draft during finalization. Reconciliation per operation and rejection of the second finalization happen after the duplicate external effect.

Reserve a single active graduation intent for the semantic entity, keyed by the stable draft identity and validated in the shared CAS, before dispatch. A second request must join the existing intent or receive an explicit conflict. Specify when an intent can be replaced after cancellation, preserving issued or uncertain identities. Test two distinct operations for the same draft from separate clones, as well as two senders racing on one operation.

### R1-F004 — Pending expansion issuance does not block the origin

**Develop exit, line 347, and Expansion transaction, lines 422–428.** The reservation consumes the slot before provider dispatch, but origin block and pause first appear at finalization. If issue creation stalls or succeeds with a lost acknowledgement, another command can see no initialized child, continue implementation or move the origin through Test/Review/Done. The now-unattachable issue is retained for reconciliation, but the origin worked through the intended stop boundary.

Define the unresolved reservation as a versioned origin condition in the transaction that reserves the slot. Establish when it blocks and pauses origin work, which recovery operations may still run, and what authoritative finalization or disposition clears it. Test a pending reservation against origin verification and promotion, including ambiguous issuance. This addresses reservation handling while preserving the owner's open question about continuing after a successful expansion.

### R1-F005 — The trip preflight and the work it authorizes have separate race windows

**Transition transaction and trip preflight, lines 332–334, Verification, lines 380–386, and trip enforcement, lines 426–428.** The preflight can pass while the attempt is active, then a concurrent trip commits the stop before the first process actually launches. The finish check prevents a stale result from passing, but permits work to start on the stopped generation. Likewise, a published delivery intent and target CAS prove that the target head matched. They do not prove the planning generation remained authorized after a pivot, trip or rework.

Define a launch/dispatch authorization boundary tied to the current attempt and an explicit rule for already authorized or in-flight work. The core must fence new managed starts when a stop wins, terminate managed work where supported, and retain any observed stale outcome. For external target mutation, define how invalidation and dispatch are ordered, and how unavoidable uncertainty is retained and reconciled without authorizing a second effect or closing the superseded attempt. Keep publication or result observation separate from new dispatch. Test the stop occurring between preparation and start, in addition to a result arriving after stop.

### R1-F006 — Equal before/after snapshots do not bind what ran

**Verification, line 380.** A fixture or tracked source can change while the subprocess reads it and then return to its original bytes before the after-check. Head, tree and input hashes can therefore match at both endpoints even when the test ran against different inputs. Explicit fixture lists fix omitted files but do not fix this race.

Require an execution lane that either presents captured test inputs as a stable snapshot or has equivalent evidence excluding intervening mutation. Bind the receipt to those actual inputs, effective command and policy. Keep worktree boundary checks for current applicability. Add a transient input mutation case, including relevant untracked inputs, alongside the existing persistent-move case.

### R1-F007 — Verified closure and the review clock lack effective evidence prerequisites

**Leaf guards, lines 338–349, advisory recovery, lines 353–355, and Verification, lines 382–388.** The design accepts a source-bound code review record and stops the implementation clock at a valid pass, but does not state when a pass becomes effective. Read literally, a review can be recorded in Develop before the ordinary Test and Review transitions. Separately, advisory may waive a failing Test exit and enter Review. Review exit and sign-off only list review, delivery and retro, so a later pass and successful merge can produce a delivered terminal state with the relevant test condition still waived. The delivery observation is real. The resulting workflow verification and dependency eligibility are ambiguous.

Define effective passing-review eligibility, including lifecycle position, attempt/source and applicable prerequisite evidence. Define which unresolved earlier waivers prevent verified terminal disposition and dependency satisfaction, while allowing real delivery observations to remain independently visible. State how a missing receipt is reconciled, or how the attempt re-enters verification when a rerun is necessary. Test a pre-Review pass and an advisory transition with a failed or absent required test followed by delivery and sign-off.

### R1-F008 — Multi-level policy has no completion path after a later level revises authored content

**Document acceptance, lines 368–374, and Acceptance and JIT proof, line 548.** The text correctly says an earlier level cannot approve later authored bytes. It also asks acceptance to compare required level evidence to the current digest. In the existing sequential flow, SAR exhausts on A, SPR revises to B, and XPR revises to C. The design does not say which evidence can satisfy a configured SAR/SPR/XPR policy, or how to complete that policy without inventing approvals. The genuine single-design walk and v0 migration do not exercise that case.

Define how a configured policy evaluates multiple level records and policy revisions. For a policy requiring every level on the final digest, show the retry/review path that obtains missing level evidence on that candidate and what happens if the candidate changes again. Any separately approved exception or sequence/delta policy needs explicit, verifiable coverage and scope. Keep historical records and their reviewed bytes intact and leave the review-depth decision open. Add a fixture where a later level changes authored content and an earlier-level record is demonstrably insufficient under an exact-content policy.

### R1-F009 — The timeout proof can conflate elapsed subprocess time with engaged agent time

**Activity and coverage, lines 402–410, and Timing and outcomes proof, lines 550–552.** An observed subprocess start/end is exact tool elapsed time, while the agent can be idle, disconnected or working elsewhere during the run. The current language permits “actual tool-run intervals” as core-only coverage without stating whether they establish the lower bound for a confirmed four-hour trip. A long unattended verification could then trip an otherwise little-engaged attempt.

Define eligibility for the observed engaged-time lower bound separately from tool execution duration and CLI-gap estimates. Keep running a test attributable to the attempt without assuming the agent was engaged throughout. Establish how genuinely observed engagement and overlapping tool/activity intervals contribute. Test a long unattended process alongside a supported observed overrun. Preserve Unknown time and the separate review elapsed reporting.

### R1-F010 — Bootstrap paths disagree and legacy adoption has no shared identity handoff

**Policy authority, lines 113–121, init, lines 126–134, legacy anchors, lines 149–151, core-only walk, line 513, and Migration, lines 526–536.** Line 115 says local-only init commits config on the default branch. Init step 5 says it never commits those files, and the walk instructs the caller to commit them. In the existing hand-built repo there is a planning branch and no store UUID file. Normal init refuses an unrecognized branch, while migration apply requires precommitted code policy that knows the trust anchor. The current text gives a preflight legacy root/tip declaration but no precise handoff for the legacy store's new UUID/allocation authority and the normal trusted anchor. Two preflights or a restart must not nominate different store identities for the same adoption.

Specify one fresh local bootstrap path and one legacy adoption path from the current v0 tree through committed config to valid v1. Bind the proposed genesis/legacy root, store UUID and initial authority to a stable adoption record before config publication, and define what the ordinary writer and a fresh clone can do before and after cutover. Distinguish preparation from apply. Verify interrupted init and adoption plus a second fresh clone against the same identity. Keep the owner-approved default-branch PR path for hosted installs.

## Required changes

Resolve R1-F001 through R1-F010 in the design and tie the listed counterexamples to the acceptance proof. The provider-specific mechanics can remain in their planned sections where core gives them a testable capability boundary.

## Optional suggestions

- Put the required trust anchor and review-policy references in the config example, and include the already described reconfiguration entry point in the command inventory.
- Cross-reference the origin attempt and affected child attempt explicitly in trip evidence for a child timeout so the trigger and the stopped attempts remain legible.

## Decision

revisions-requested
