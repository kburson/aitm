<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-d723b3d55991d2c3bf2c78beab9170ef"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md"
artifact_commit: "d192607c426d3dc081d104f5ece8dc0d13879417"
artifact_blob: "dfbf240cd8754be0974a6c6657033d98441009eb"
artifact_digest: "sha256:a8ebc9a9fb27ba705e63b467ed6ac3f920b75697fc01cd965aadb87f7a48d938"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:667c6c199bc4287411e24eebb8696c176515eb3a668a669ac8131e1c8b7796b4"
  identity_source: "runtime"
started_at: "2026-11-11T15:04:43.089Z"
submitted_at: "2026-11-11T15:10:21.861Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the round 2 follow-up review of `.aitm/stories/000/2/design/2026-11-11-2-governed-pr-and-branch-lifecycle-design.md` at commit `d192607c426d3dc081d104f5ece8dc0d13879417` (artifact digest `sha256:a8ebc9a9fb27ba705e63b467ed6ac3f920b75697fc01cd965aadb87f7a48d938`, taken from this response's protected frontmatter). I checked each disposition in `review-d723b3d55991d2c3bf2c78beab9170ef-author-response-1.md` against a fresh read of the whole revised specification. All five round 1 findings are resolved at the spec level, and all three optional suggestions were adopted. This review grants no hosted test, protection change, implementation or #159 pickup authority.

### Full-file reread

- **Ranges and EOF.** I used Read in contiguous chunks of at most 60 lines and read lines 1–60, 61–120 and 121–140. The last request (offset 121, limit 60) returned only 20 lines, so line 140 is EOF.
- **Truncation.** No output was truncated, so no recovery was needed.
- **Hashing.** Shell hashing is unavailable to this reviewer, so the digest above comes from the protected frontmatter and was not computed independently.
- **Line count note.** The author response says the round 1 reviewer read "107 exact specification lines". In round 1 the Read tool reported the prior revision as 108 lines (offset 121 returned "file has 108 lines"), and I read lines 1–60 and 61–108. The difference is probably how a trailing newline is counted. It does not affect any disposition.

### Disposition verification

| Finding | Verdict | Evidence in the revised design |
| --- | --- | --- |
| R1-F001 | Resolved | Lines 29–35 make the literal delivery target independent of Backlog parentage. A child of a branch-backed parent resolves that parent's exact ref. A story under a pure aggregate, or with no parent, explicitly declares the default branch or another authorized literal target at graduation. A missing or unbound target leaves provisioning pending, with no implicit fallback. Acceptance at line 129 now covers "correct explicit targets including trunk from a pure aggregate". |
| R1-F002 | Resolved | Lines 72–84 add post-delivery terminal retirement for the exact delivered incarnation. That retirement preserves the merged PR and receipts and retains the ref and worktree until dependents, outstanding actions and local source are resolved. It uses the same fence for ordinary and integration deliveries. GitHub automatic deletion and host-triggered base changes or closures must be qualified. The ref is retained, or the merge held before dispatch, when deletion cannot be controlled. External base changes are reconciled as retargets that invalidate admission and CI and require a verified draft and fresh evidence. Acceptance at line 130 covers cleanup after delivery. |
| R1-F003 | Resolved | Lines 60–63 add governed read-only observation of PR state, review threads, check results and allowed logs or artifacts, bound to the same scoped identity and catalog. Lines 100–101 state that governed observation preserves the isolation boundary. Acceptance at lines 132–133 requires scoped CI and review observation. |
| R1-F004 | Resolved | Lines 49–56 record the bootstrap OID, parent OID, equal tree, trusted service role and incarnation as a provisioning artifact. Attempt baselines are pinned at or after the verified bootstrap, the artifact is accounted for explicitly in composed-source and delivery mappings, and its CI is limited to provisioning evidence. The existing rule that rejects unexplained source still covers unrecorded commits. |
| R1-F005 | Resolved | Lines 88–92 require a runtime-attested principal whose identity stays outside the workspace and cannot be selected or transferred by the agent. Acceptance at lines 133–134 requires denial of cross-story access to another live incarnation. |

The adopted optional suggestions are:
- line 116 now says "Apply the declared target's exact C39–C41 delivery policy";
- lines 131–132 add the composed-source guard and durable scrap source recovery to Acceptance;
- lines 100–101 state the purpose of governed observation.

### Regression check

I re-checked the revised text against the #133 amendment (one shared flag, repair-only hold, per-PR recovery and retarget allowance loss) and the #158 plan (exact flag, head, base and tree host boundary, with the PR association proof obligation). Both handoffs are unchanged:
- **Default-branch merges** still need the #158 boundary (lines 117–119).
- **Managed readiness** still uses broker ordering (lines 107–112).
- **Non-default delivery** stays outside the hold (lines 114–117).

The new post-delivery retirement rule is consistent with the abandonment fence (lines 64–71) and with Core's rule that cleanup cannot create delivered status. I found no new contradiction with the Core/provider boundary in core-design §Providers.

The plan is the next sealed phase. Its proof matrix must reflect these contracts there, including the cases listed in the round 1 closure criteria.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Lines 32–34 require the literal target to be declared "at graduation". Stories graduated before this capability exists have no declared target, so under line 34 they would stay pending. Consider allowing an explicit, authorized target declaration for an already-graduated story before provisioning. The plan phase could carry this instead.
2. Line 32 says "a pure aggregate". Consider "a pure aggregate epic" to match line 45 and plan terminology.

## Decision

accepted
