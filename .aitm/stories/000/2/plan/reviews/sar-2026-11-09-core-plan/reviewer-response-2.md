---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "f86dd7c1954215585dcbdbcc9bac0e7e490a1956"
artifact_digest: "sha256:07c9ec8e1f51c5c7b78bf4e7390fc50d6d461872f1a027bae884305e235f4765"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
reviewer_session: "01a1bf0f-9ac0-7603-911d-3fb4bd37d3e7"
session_identity_kind: "observed-session-id"
started_at: "2026-11-09T07:00:11.655Z"
submitted_at: "2026-11-09T07:01:59.367Z"
start_basis: "recorded"
finding_ids: [R2-F001, R2-F002, R2-F003, R2-F004, R2-F005]
answered_finding_ids: []
---

## Summary

**Revisions requested.** I read all 1,128 lines of the revised FUR and the complete round 1 author disposition. I verified the raw digest at revision 90b8a05c1ce54e285cf2a109a5eed774a816dcb0, 62 leaves, a 194.5 h sum, a 4 h maximum and a topological table order. The same observed Codex worker session recorded gpt-6.1-sol/high and a new round 2 turn start. Timing is an elapsed turn span.

The local graduation transaction, explicit recovery paths, contained executor wiring and decomposition changes address R1-F002 and R1-F004–R1-F006. The CLI/qualification and production composition additions address much of R1-F001, R1-F003 and R1-F007. R1-F008's receipt validation and adoption handoff are now explicit, and R1-F009's release-source circularity is resolved. The remaining findings concern prerequisites and runtime call sites exposed by the more specific proofs, parity of migration output, and isolation of the release side effect from the verification suite.

## Findings

### R2-F001 — High — Match qualification prerequisites to the commands the leaf will exercise

C49's prerequisite closure lacks C21 even though the nominal installed local walk must graduate a draft. The external finalizer in C22 does not provide that local authority. C49 also audits every mapped route while its closure lacks C10 repair, C41 managed delivery and C48 migration apply. C51 requires an actual index rebuild and query parity but has no dependency path to C18. The table order does not supply a prerequisite in parallel execution (lines 90, 183–187, 939–945, 991–1003 and 1113–1126).

Add C21 to the nominal walk's prerequisites and C18 to migration/index qualification. For the broader CLI audit, specify which assertions are registration/option checks and which require operational positive proof. Either add the owning dependencies or assign and collect the operational cases in the qualification suites that already depend on them, with one gate covering the whole map. Preserve the requirement that the nominal walk and operational assertions invoke installed commands.

### R2-F002 — High — Carry the local authority contract through expansion

C21 and C22 now correctly keep local graduation allocation and initialization in one authority transaction. C30's prerequisites still end at C20/C22 for identity work, and its contract/tests name the external pending-identity path without an owner for actual local expansion issuance (lines 153–166, 515–541 and 697–709). C22's public pure constructor consumes a draft, candidate and graduation intent, while C30 must link a reserved origin attempt, child identity and expansion block. The local provider cannot issue a permanent number using C20's external protocol. The design applies both the reservation rule and the local atomic number/initialization rule to expansions (lines 499, 541–545).

Assign the integration with C21 and the exact construction seam by which C30's live origin reservation and its child story/relations enter the local authority transaction. Preserve the earlier allowance/pause commit. Test actual local-only and shared local expansion with no published child or permanent number before the applicable authority point, no gap in the origin block at finalization, and one child under a lost acknowledgement or competing clone. Keep uncertain external issuance separate.

### R2-F003 — High — Assign the remaining shared runtime hooks to the owning leaves

The new composition paragraph (line 95) resolves many earlier seams. Three guarantees still have only a producer/helper and no explicit owner for wiring their normal call sites. C09 defines publish/reconcile and lists only its two store modules. The accepted default requires ordinary mutating commands to attempt bounded publication, not just explicit sync or specialized admission calls (design lines 576–580). C31 names preflight_attempt and tests ordering but lists only its own trips/pivot files, while preflight must precede ordinary sync and work and run again on CAS retry and completion before effective pass (design lines 324–326 and 360–368). C44 defines record_outcome after C42, but C42 never declares a join point for Close outcome and C44 has neither a signoff update nor an operation ingress seam. Signoff must append its outcome, closure, session end and applicable related changes together (design lines 461, 507). A helper-level test can pass while the default command does something different.

Name the responsible composition leaves and allowed shared paths or earlier ports for default publication, trip preflight and atomic Close outcomes. Prove an ordinary state mutation without --push attempts publication and distinguishes pending from local completion. Prove a trip wins before authored sync or managed dispatch, with same-attempt CAS retry and completion ordering. Prove real signoff appends its Close outcome with the same operation ID and leaves no half-close on refusal/crash. Preserve explicit pending behavior during implementation and normal operation eligibility rules.

### R2-F004 — Medium — Bind dry-run output to the same migration construction used by apply

C46 is assigned a complete dry-run input/output manifest before C47's declaration and C48's accepted-snapshot binding, metadata/view regeneration and payload-tree construction exist. C51 proves immutability and compares hashes without stating that the dry-run prediction for the same pinned declaration agrees with the tree C48 actually builds (lines 893–945 and 1122). Separate implementations can truthfully report different output hashes while passing those tests. The master C4 checkpoint requires an input/output hash manifest; the core design requires a read-only dry-run and deterministic apply under the exact declaration (lines 608–624).

Identify one construction/preview contract and give it an executable prerequisite order. Early dry-run can report inventory, planned transformations and explicitly unbound values before a declaration exists. With the same pinned inputs and exact declaration, require read-only preview and apply to agree on mapped facts, accepted snapshots, and the deterministic receipt-excluded payload digest. Assert the agreement in the real fixture and retain no-mutation checks.

### R2-F005 — Medium — Keep the publication action outside the post-release test

C53 now delivers its candidate workflow before C60, resolving the artifact dependency cycle. C60's **Test first** step still tells test_published_release to publish the delivered revision, while the shared cycle calls for a failing test before implementation and the last paragraph makes the suite part of the publication job (lines 68–78, 1047–1059 and 1128). If read as executable, the failure/retry of a pytest check can trigger a second live publication, or the publication job can depend on a test that dispatches itself.

Describe the authorized publication as an explicit once-per-release operation outside pytest. Use fixture tests for checker failures before the live action; the post-publication suite only observes and installs the exact already-published release. On a lost result, query the exact version/artifact and compare provenance before any retry. Keep C5 pending until the read-only dual-platform evidence succeeds. The correction does not change the later release authority boundary.

## Required changes

Address R2-F001 through R2-F005 and synchronize the affected table, leaf details, composition and qualification assertions. Preserve the revised bounded decomposition, original Refine record and all open owner choices.

## Optional suggestions

None.

## Decision

**revisions-requested**

The next round reviews the full candidate and the dispositions for these five findings.
