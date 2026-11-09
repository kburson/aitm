---
schema: "aitm.review-response/v0"
level: "sar"
story: 1
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/1/plan/master-plan.md"
artifact_base_commit: "9f56a4682488c5ea586a7c6fbefced82f15bb4e2"
artifact_digest: "sha256:b7f1a5eedd67a8faefc33bf322dbfc421f29dfa7cba4d606454c8b74f909f57b"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
reviewer_session: "01a1beff-11ec-7ea2-8049-aa8c76291a45"
session_identity_kind: "observed-session-id"
started_at: "2026-11-09T06:29:10.959Z"
submitted_at: "2026-11-09T06:31:23Z"
start_basis: "recorded"
finding_ids: [R1-F001, R1-F002, R1-F003, R1-F004, R1-F005, R1-F006]
answered_finding_ids: []
---

## Summary

**Revisions requested.** I read the full candidate at the recorded raw digest, the owner decisions, accepted architecture and core design, planning layout, and interim review procedure. The published architecture and core XPR manifest digests match their respective files. This is a manual SAR with observed Codex worker provenance. The worker thread ID matches Codex session metadata, and the worker turn records the selected model and effort. The start is that worker's per-turn context timestamp. The interval is elapsed turn time.

The milestone map preserves the core acceptance matrix and separates historical review, release, and adoption. Its execution gaps are at the transition off bootstrap, review policy and live turn ownership, hosted projection evidence, and full-install delivery.

## Findings

### R1-F001 — High — Give the GitHub section a story identity route across cutover

The M1/M2 rows and dependency text (lines 38–40 and 52) make the GitHub provider follow released core. C6 and lines 69–71 then retire manual planning writes at M1 cutover. The accepted core design (lines 545, 614 and 618) preserves aitm's GitHub-numbered namespace and makes new remote issuance unavailable until its provider is configured. The local provider serves fresh local-only stores and cannot issue replacement numbers here. If M2 still needs to graduate its own section or implementation leaves after cutover, it needs the provider that those leaves are meant to build. The owner requires each section to graduate as a child epic after its own brainstorm (draft lines 58 and 129–130).

Specify an executable order for M1 release, the bootstrap graduation of the relevant M2 work or another supported setup path, M1 adoption, and the first M2 runtime-issued identity. State which related work can proceed if the provider is unavailable after cutover. Distinguish the C5 package and migration capability from C6 production adoption so delivery of M1 does not depend circularly on M2. Preserve stable GitHub IDs, the section hierarchy, and the post-cutover core writer boundary. No early graduation, actual migration, or provider configuration change is requested by this finding.

### R1-F002 — High — Scope exact-content guards and record the policy prerequisite

Line 32 requires missing exact-content levels or an exception before a runtime transition. That applies even to transitions without a document acceptance guard and appears to forbid advisory progression. The accepted core design (lines 382–400 and 418–424) applies review requirements at the appropriate guards, reports a failed or unknown policy result in advisory mode, and requires an applicable explicit policy definition to assert verified acceptance. It also leaves the depth matrix and sequence/delta policy open. Line 79 states a conditional rule closer to that contract. C1/C6 do not identify the complete, applicable committed policy as a production adoption prerequisite or say how to proceed if the owner-open choice is still unresolved.

State that exact-content completion or an exception applies to the relevant acceptance requirement under a selected, supported committed policy. Separate enforce-mode refusal from advisory advancement with retained failed/unknown guards and no verified acceptance or delivered claim while requirements remain unsatisfied. C1/C5 can use explicitly labeled fixture policy. C6 needs an explicitly authorized, supported production policy and any exception authority it relies on, or remains pending. The current scoped review assignments alone supply historical evidence.

### R1-F003 — Medium — Define the bounded v0 exception and actual cutover blockers

The general path rule (line 26), C2/C4/C6, and line 69 leave the historical root README and the exact authority of the legacy declaration implicit. Line 69 also makes any incompatible record a cutover blocker. The accepted core design (lines 168–170 and 608–624) requires the independently committed code-default declaration to bind the exact legacy root and approved tip, adapter, allowed deviations, and numbering/provider namespace before apply. It requires the final tree to be data-only, with the legacy root README preserved in provenance and removed from the active root. It allows safe unsupported optional records to remain opaque and incomplete reviews to remain unaccepted evidence.

Make the bounded legacy exception, declaration, and fresh-clone verification visible in C4/C6. A changed approved tip requires renewed validation and declaration before apply. Distinguish an incompatible required fact or missing proof that makes apply unsafe from an optional opaque record or historical review that can be preserved without conferring acceptance. Retain exact evidence for either result.

### R1-F004 — High — Assign live core review ingestion to M1 and producer automation to M4

M4's row and line 77 appear to defer live per-turn starts/completion/import to M4, while the M1 row and C4 name only import and migration. The accepted core design (lines 489–497 and 640) explicitly requires M1 to open a level before its first turn, ingest a live provisional response with its timing anchor, complete it, and demonstrate identical normalization through later import/backfill. The plan's reference to the complete acceptance matrix pulls that requirement into M1, but its operational timeline could leave the M1–M4 interim with only final-bundle recording.

Assign the live `review open`, `review turn`, `review complete`, and final import/validation route to M1 and name it in C4, including the live/import idempotency case and retained Unknown timing. Show how the interim manual and native routes use the available anchors and the core writer. Assign M4 the refactored no-precommit record producer, automatic true per-turn start capture where available, and automatic handoff of those records to the existing M1 sink.

### R1-F005 — Medium — Assign full-install completion to a milestone or explicit release gate

Line 56 correctly separates package installation from enabled extension configuration, and line 85 preserves the distribution-name choice. No milestone, checkpoint, or final release gate owns delivery and verification of the actual full-install experience. The owner requires full install to load and configure all extensions (draft lines 108–111, architecture lines 184–199). Each individual package could meet its exit criteria without a fresh installation ever getting the complete product.

Assign ownership and timing to a full-install gate after the applicable extension releases and distribution-name decision. Require a fresh installation from released packages that proves dependency resolution, entry-point discovery, and supported enablement/configuration for the complete set. Keep the name open and M1 independent of that deliverable.

### R1-F006 — Medium — Test the M2 shared projection safety contract

The M2 exit lists sparse projection and REST capability checks (line 40). It omits the hosted provider's responsibility for monotonic projections. The accepted core design (line 469) explicitly assigns M2 the endpoint-specific mechanism and proof that shared projection runs only from published operations and a retried old version cannot roll the board backward. A happy-path board update after state entry can pass the present milestone description while stale replay still corrupts the board.

Add M2 exit evidence for publication-gated projection and stale retry/ambiguous acknowledgement handling against the latest published state. Require the provider to demonstrate either safe monotonic versioning or serialized ownership/fencing with the defined pending result when takeover cannot be proved. Leave the endpoint and mechanism to M2 design.

## Required changes

Address R1-F001 through R1-F006 in the master plan. Retain the existing acceptance evidence and open owner choices. Record the prerequisites for later adoption without making those choices or expanding this SAR.

## Optional suggestions

- In the global clock summary, name the effective deliverable-review endpoint for spikes and the aggregate evidence path for epics. The core matrix already establishes the distinctions.
- In the M5 exit, name the read-only research and story design/plan-only planner permission checks. Include likely defect areas in the fixed plan output and preserve opt-in epic industry research. The accepted architecture specifies these roles and boundaries.
- At the proposed advisory-to-enforce checkpoint, identify how a second enforcing consumer can be selected and authorized. The checkpoint can stay open with ai-peer-review as the planned first candidate.

## Decision

**revisions-requested**

The next round reviews the complete revised FUR and the author's disposition of each finding. Existing owner choices can remain open while the plan states where they must be resolved.
