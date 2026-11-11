<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-d723b3d55991d2c3bf2c78beab9170ef"
role: "reviewer"
turn: 4
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md"
artifact_commit: "2304562f53bbf47448d77ec9f07178d73036fffd"
artifact_blob: "cd1d14285b8272dad0acbbdb19e5928dc8471c89"
artifact_digest: "sha256:e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:667c6c199bc4287411e24eebb8696c176515eb3a668a669ac8131e1c8b7796b4"
  identity_source: "runtime"
started_at: "2026-11-11T15:04:43.089Z"
submitted_at: "2026-11-11T15:14:10.285Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the plan-phase follow-up review (turn 4) of `.aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` at commit `2304562f53bbf47448d77ec9f07178d73036fffd`, with artifact digest `sha256:e4245997416a6e39188aacbab246a1fbb41d9ccc8c50e1a2971d85f52b033db3` taken from this response's protected frontmatter. I checked the dispositions in `review-d723b3d55991d2c3bf2c78beab9170ef-author-response-3.md` against a fresh read of the whole revised plan. The reference is the specification accepted in phase 1 (design commit `d192607c426d3dc081d104f5ece8dc0d13879417`, digest `sha256:a8ebc9a9…d938`). All five turn 3 findings are resolved, and both optional suggestions were adopted. This review grants no hosted test, protection change, credential, implementation or #159 pickup authority.

### Full-file reread

- **Ranges and EOF.** I used Read in contiguous chunks of at most 60 lines and read lines 1–60, 61–120, 121–180, 181–240, 241–300, 301–360 and 361–397. The last request (offset 361, limit 60) returned 37 lines, so line 397 is EOF.
- **Truncation.** No output was truncated, so no recovery was needed. The long table rows at lines 23–31 and 386–396 and the long line 133 came back complete.
- **Hashing.** Shell hashing is unavailable to this reviewer, so the digest above comes from the protected frontmatter and was not computed independently.
- **Line count note.** The author response says the turn 3 read covered "338 exact physical plan lines". The Read tool showed 339 numbered lines for that revision, which is probably a trailing-newline counting difference. Either way, the turn 3 read reached EOF, and this does not affect any disposition.

### Disposition verification

| Finding | Verdict | Evidence in the revised plan |
| --- | --- | --- |
| R3-F001 | Resolved | **Interface rows.** Line 23 resolves "the explicitly declared literal delivery target", line 25 refreshes against "its actual declared target", and line 27 applies "the declared target's review, CI and exact-delivery policy". **Target declaration.** Line 40 says the declared target determines each PR base. Lines 42–50 cover branch-backed parent resolution, explicit default or other literal target declaration for a pure aggregate or no-parent story at graduation, and an authorized backfill declaration for existing stories; a missing or unbound target stays pending, and a pure aggregate supplies no implied target. **Read-set and Core work.** Lines 133–135 freeze the declared target. Lines 338–339 assign graduation-time publication and backfill to C20/C22. **Proof.** Row 388 covers the default-targeted story under a pure aggregate, the no-parent explicit target, a bound non-default parent, missing or unbound targets staying pending, and denial of substitution and implicit default fallback. |
| R3-F002 | Resolved | **Interface and retirement.** Line 29 adds "Retire delivered work". Lines 287–303 add a post-delivery terminal retirement claim after verified delivery and C79 completion evidence. They preserve the merged PR and source mapping, state that a pending retirement does not invalidate delivery, and apply the same fence. Dependent PRs must be terminal, or moved through a governed retarget, before a delivered or abandoned parent ref is deleted. **GitHub host behavior.** Lines 305–317 qualify automatic, manual and API deletion and host-driven base change and closure. They hold managed merge when automatic deletion could bypass the fence and reconcile external retarget or closure, invalidating ready, CI and merge evidence and requiring a verified draft and fresh admission. **Ownership and proof.** Lines 339–341 extend C43/C79, and line 352 assigns qualification to step 2. Row 389 covers delivered ordinary and integration refs with dependent PRs, automatic deletion enabled and disabled, the merge hold and host-triggered reconciliation. |
| R3-F003 | Resolved | **Interface.** Line 30 adds "Observe PR and CI" with exact check, run and head identities and redaction. **Scoping.** Lines 202–206 bind observation to the same authenticated scope, resolve resources from the binding, filter logs and artifacts, and confer no target-action admission. **Ownership.** Line 353 assigns it to step 2, and lines 367–368 assign catalog entries to step 4. **Proof.** Row 390 requires positive reads for the session's own resources and rejection of another story's scoped data. |
| R3-F004 | Resolved | **Bootstrap artifact.** Lines 107–118 record the typed bootstrap artifact: OID, parent OID, unchanged tree, actor or service role, incarnation and host receipt. They also verify the initial working ref at the bootstrap OID and keep bootstrap CI distinct. **Baselines and mappings.** Ordinary baselines are pinned at or after the bootstrap, and the upstream baseline is kept separately for composed-source proof. The bootstrap, or its verified rewrite or omission, is mapped as content-free in composed-source and delivery evidence, and an empty unrecorded commit does not qualify. **Proof.** Row 388 verifies bootstrap identity and tree. Row 393 accepts recorded bootstrap history and rejects unrecorded or mismatching empty history and a pre-bootstrap baseline. |
| R3-F005 | Resolved | **Identity.** Lines 196–199 make the runtime attest session identity outside the workspace, and broker admission derives story and scope from that non-transferable identity. **Ownership.** Line 353 assigns this to step 2. **Proof.** Row 390 rejects push, readiness, retarget, merge and abandonment from another current story session, a workspace-copied identity artifact, and cross-story observation. |

The adopted optional suggestions are:
- every proof-matrix row now names its owning step (column at lines 384–396);
- the plan includes an explicit authorized target backfill for already-graduated stories (lines 46–48 and 338–339).

### Regression and handoff check

- **Unchanged sections.** The integration delivery, composed-source receipt, provisioning concurrency, ready/retarget ordering, dual-role refs and producer separation sections are unchanged in substance from turn 3, where I verified them.
- **#133 and #158 handoffs.** These still match: a separate step 2 readiness capability; #158 synthetic host proof in step 3 (row 394) separate from actual #133 T34/T36–T40 end-to-end evidence (row 395); non-default parents outside the hold; #159, #103 and production protections unauthorized (lines 356–365).
- **Proof order.** The order is coherent:
  - Core contracts and the guard are in step 1 (rows 386, 387 and 393).
  - Hosted adapter, isolation, observation, deletion and readiness qualification are in step 2.
  - #158 and #133 integration are in step 3.
  - Catalog and interface parity are in step 4.
- **Core/provider boundary.** This is consistent with core-design §Providers.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Row 388 reads "an explicitly default-targeted ordinary story under a pure aggregate for a story with no Backlog parent and an explicit target". A comma is missing after "pure aggregate", so two cases read as one. Consider "…under a pure aggregate, for a story with no Backlog parent and an explicit target, and for a bound non-default parent".
2. Some wording still refers to a "parent" where the accepted contract is now the declared target. Line 104 has "starts at the same commit as its parent", line 141 "Record the exact parent binding" and line 344 "exact parent". Consider "declared target" or "target binding" during leaf refinement.
3. Row 386 (step 1, deterministic Core) could also exercise the C20/C22 graduation-time target publication and the authorized backfill for an existing story, including denial of an unauthorized backfill. Hosted row 388 would then not be the first proof of that Core contract.

## Decision

accepted
