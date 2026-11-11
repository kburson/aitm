<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-d723b3d55991d2c3bf2c78beab9170ef"
role: "reviewer"
turn: 3
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md"
artifact_commit: "f4a6c43bcb84db94f337efd0dcb86a0a7d49bcb9"
artifact_blob: "28e712ddcd03bd07b58e8586155b5db3365fe20a"
artifact_digest: "sha256:b1a1f71f42fd39d9b03ce04b9971c5ed519275515731452f88efe00ff1698f8c"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:667c6c199bc4287411e24eebb8696c176515eb3a668a669ac8131e1c8b7796b4"
  identity_source: "runtime"
started_at: "2026-11-11T15:04:43.089Z"
submitted_at: "2026-11-11T15:12:17.376Z"
finding_ids: ["R3-F001","R3-F002","R3-F003","R3-F004","R3-F005"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the plan-phase review (turn 3) of `.aitm/stories/000/2/plan/2026-11-11-2-governed-pr-and-branch-lifecycle.md` at commit `f4a6c43bcb84db94f337efd0dcb86a0a7d49bcb9`, with artifact digest `sha256:b1a1f71f42fd39d9b03ce04b9971c5ed519275515731452f88efe00ff1698f8c` taken from this response's protected frontmatter. I reviewed it against the specification accepted in phase 1, which is design commit `d192607c426d3dc081d104f5ece8dc0d13879417` with digest `sha256:a8ebc9a9fb27ba705e63b467ed6ac3f920b75697fc01cd965aadb87f7a48d938`, as recorded in the phase-01 manifest. This review grants no hosted test, protection change, implementation or #159 pickup authority.

**The plan was not revised after the spec revision.** This plan digest is identical to the plan digest that `spr-reviewer-round-3.md` recorded against the earlier design revision (`71dae425…`). In round 1 of this review, the author response said the plan "will reflect the accepted design in its own reviewed revision". The current plan does not yet do that. Each of the five accepted design contracts added in response to R1-F001 to R1-F005 is either missing from the plan or contradicted by it. These gaps break the spec-to-plan handoff and block acceptance.

### Full-file read record

- **Ranges and EOF.** I used Read in contiguous chunks of at most 60 lines and read lines 1–60, 61–120, 121–180, 181–240, 241–300 and 301–339. The last request (offset 301, limit 60) returned 39 lines, so line 339 is EOF.
- **Truncation.** No output was truncated, so no recovery was needed. The long table rows at lines 23–29 and 329–338 came back complete.
- **Hashing.** Shell hashing is unavailable to this reviewer, so the digest above comes from the protected frontmatter and was not computed independently.
- **Spec reference.** I used the accepted design (140 lines), which I read in full in turn 2, together with the phase-01 manifest. I also used the #133 amendment, the #158 plan, core-design §Providers and §Verification/delivery, and the C76 leaf, all read in turn 1. Nothing in those references changed during this review.

### Independently verified (no finding)

- **Integration delivery.** Owner designation, the separate literal upstream, the C62 required scope, non-circular staging, the composed-source receipt bound to the literal upstream with its own Test, Review and C41, and no empty tagged commit (lines 42–86). All are consistent with the accepted design (lines 35–46) and C76.
- **Provisioning concurrency.** One semantic lifecycle slot, exclusive literal host resources, dispatch claims, positive attribution and reuse fencing (lines 103–144).
- **Ready and retarget ordering.** Separate ready/retarget qualification from the #158 merge boundary (lines 191–220). This matches #133 lines 52–66 and #158 lines 31–54.
- **Dual-role refs.** The target write policy, integration refresh and direct-owner-work constraints (lines 232–245).
- **Producer separation.** Step 3 and proof rows 336–337 keep the synthetic #158 host proof separate from the actual #133 T34/T36–T40 evidence.
- **#159 and production protections.** These remain explicitly unauthorized (lines 12 and 307–309).

## Findings

### R3-F001 — High — The plan still derives the PR base from Backlog parentage instead of the declared literal delivery target

**Location:** plan lines 23, 27, 35–36, 112–113, 284–291 and 334. Accepted design lines 29–35, 115–117 and 129.

**Problem.**
- Line 23 creates the working branch "from that parent".
- Line 27 applies "the declared parent's review, CI and exact-delivery policy".
- Lines 35–36 say "A child story uses its declared feature or epic parent branch as the PR base. A missing or unbound parent blocks provisioning."
- Line 112 freezes "the declared parent incarnation".

**Conflict with the design.** The accepted design declares the literal delivery target independently of Backlog parentage. A story under a pure aggregate epic, or with no Backlog parent, explicitly declares the default branch or another authorized literal target at graduation. A missing or unbound target leaves provisioning pending. The design also applies "the declared target's exact C39–C41 delivery policy".

**Consequence.** As written, the plan would implement the contradiction found in R1-F001: an ordinary trunk-bound story under a pure aggregate epic would be unprovisionable or would rely on an implicit fallback. Step 1 does not assign target declaration at graduation to C20/C22, and the proof matrix has no trunk-from-pure-aggregate case, although design acceptance requires one (line 129).

**Closure criteria.**
- Rewrite the create, push/refresh and merge interface rows and lines 35–36 and 112–113 in terms of the declared literal delivery target.
- State how a child of a branch-backed parent resolves that target, and how a story under a pure aggregate epic or with no parent declares it at graduation.
- Say that a missing or unbound target leaves provisioning pending, with no implicit fallback.
- Add the graduation-time target declaration to the step 1 Core refinement (C20/C22).
- Add proof-matrix cases for:
  - an explicit trunk target under a pure aggregate epic;
  - an explicit target with no parent;
  - a missing target staying pending;
  - rejection of implicit default fallback.

### R3-F002 — High — Post-delivery retirement and GitHub host-triggered deletion and retarget are not planned

**Location:** plan lines 21–29, 257–280, 292–299 and 329–338. Accepted design lines 72–84 and 130.

**Problem.** The plan's Retirement section and the interface table cover only abandonment and scrap. The accepted design requires all of the following, and none is in the plan:
- a terminal retirement action for the exact delivered incarnation after verified delivery and the required completion evidence;
- preservation of the merged PR and receipts;
- retention of the ref and worktree until dependents, outstanding actions and local source are resolved;
- the same retirement fence for ordinary and integration deliveries;
- qualification of GitHub automatic branch deletion and of host-triggered PR base changes or closures;
- retaining the ref when deletion cannot be controlled, and holding a managed merge before dispatch when deletion can occur on merge;
- reconciling external base changes as retargets that invalidate earlier admission and CI.

**Gaps in proof order and the matrix.**
- Step 1 does not assign the Core action that publishes post-delivery retirement, which ties to the C43 action journal and terminal sign-off.
- Step 2 does not own the GitHub qualification.
- Proof row 330 races retirement only for an abandoned parent.

**Closure criteria.**
- Add post-delivery retirement to the interface and Retirement sections.
- Assign its Core action to step 1 and its GitHub automatic-deletion, base-change and closure qualification to step 2.
- Add proof rows for:
  - retiring a delivered ordinary ref and a delivered integration ref while a dependent PR is open;
  - the repository's automatic head-branch deletion setting, enabled and disabled, including the merge hold when deletion cannot be controlled;
  - a host-initiated base change reconciled as a retarget, with admission and CI invalidated and a verified draft required before re-entry.

### R3-F003 — Medium — Governed read-only observation is missing from the plan

**Location:** plan lines 21–29, 169–189, 292–299, 310–314 and 332. Accepted design lines 60–63, 100–103 and 132–133.

**Problem.** The accepted design provides governed read-only observation of the authorized PR state, review threads, check results and allowed logs or artifacts. That observation is bound to the same scoped identity and capability catalog, and acceptance must show scoped CI and review observation. In the plan:
- The "Discover or inspect" row (line 29) covers operation discovery and status only.
- The isolation section (lines 178–189) removes direct routes but plans no replacement read path.
- Proof row 332 tests only denials.

**Consequence.** Under managed isolation, a planned implementation would leave agents unable to read CI failures and review feedback for their own PRs.

**Closure criteria.**
- Add governed observation operations to the interface table with scope, typed results and catalog entries.
- Assign the adapter and runtime parts to step 2 and the catalog entries to step 4.
- Add proof cases showing that a managed agent receives PR state, review threads, check results and permitted logs or artifacts for its own incarnation, and is denied them for an unauthorized resource.

### R3-F004 — Medium — Bootstrap provisioning artifact accounting is missing

**Location:** plan lines 66–86, 93–100, 112–113, 331 and 335. Accepted design lines 47–56.

**Problem.** The accepted design records the bootstrap OID, parent OID, equal tree, trusted service role and incarnation as a provisioning artifact. It pins ordinary attempt source baselines at or after the verified bootstrap and accounts for the artifact explicitly in composed-source and delivery mappings, and the bootstrap's CI provides only provisioning evidence. The plan (lines 93–100) checks only draft creation, CI behavior and absence of source changes. It also has these gaps:
- The provisioning read-set (lines 112–113) and the composed-source receipt (lines 66–86) do not mention the bootstrap artifact.
- The guard fixture (row 335) has no bootstrap case.
- Row 331 records only a "bootstrap disposition".

**Closure criteria.**
- Specify the recorded bootstrap artifact fields and pin the attempt baseline at or after it.
- Add the bootstrap artifact to the composed-source receipt's mapping and to delivery mapping.
- State that its CI is provisioning-only evidence.
- Extend proof rows 331 and 335 with:
  - a recorded bootstrap accepted as explained, content-free history;
  - an unrecorded or non-matching empty commit rejected as unexplained;
  - an attempt baseline before the bootstrap rejected.

### R3-F005 — Medium — Runtime-attested caller identity and cross-story denial are missing

**Location:** plan lines 169–176 and 332. Accepted design lines 88–92 and 133–134.

**Problem.** The plan says the service "authenticates the caller". It does not carry over the accepted contract that the principal is runtime-attested, stays outside the workspace, and cannot be selected or transferred by the agent. Proof row 332 checks unauthorized repository, ref, action and stale generation, but not cross-story access to another live incarnation, which design acceptance requires.

**Closure criteria.**
- State the runtime-attested, non-transferable caller identity in the isolation section and assign it to step 2.
- Add a proof case in which a current, valid managed session is denied push, ready, retarget, merge, abandon and observation on another story's live incarnation in the same repository.
- Add a case showing that a workspace-copied identity artifact cannot authenticate.

## Required changes

1. **R3-F001:** Replace parent-derived base and policy wording with the declared literal delivery target. Add graduation-time target declaration to step 1, and add trunk-from-pure-aggregate, no-parent, missing-target and no-fallback proof cases.
2. **R3-F002:** Plan post-delivery retirement, its Core action and the GitHub automatic-deletion, base-change and closure qualification. Add the merge hold when deletion cannot be controlled and the reconciliation of external base changes as retargets, each with proof rows.
3. **R3-F003:** Add governed read-only observation operations, their step ownership and catalog entries, and positive and negative proof.
4. **R3-F004:** Specify the recorded bootstrap artifact, baseline pinning, composed-source and delivery accounting, and provisioning-only CI, and extend proof rows 331 and 335.
5. **R3-F005:** Specify runtime-attested, non-transferable caller identity, and add cross-story and copied-identity denial proof.

## Optional suggestions

1. Tag each proof-matrix row with its owning bounded-delivery step (1–4). The proof order and Core leaf handoffs would then be checkable row by row.
2. The accepted design (lines 32–34) declares targets "at graduation". Consider planning an explicit, authorized target declaration for stories graduated before this capability exists, so they do not stay pending indefinitely.

## Decision

revisions-requested
