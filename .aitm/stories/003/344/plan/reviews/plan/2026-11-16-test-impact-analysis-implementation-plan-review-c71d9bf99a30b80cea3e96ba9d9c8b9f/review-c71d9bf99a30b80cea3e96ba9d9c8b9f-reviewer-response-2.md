<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-c71d9bf99a30b80cea3e96ba9d9c8b9f"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/344/plan/test-impact-analysis-implementation-plan.md"
artifact_commit: "e3bc34118e735a1ca80e772a8d9379d7191918c2"
artifact_blob: "4d7a8692b8acdd011c784ef8957b37f6d2b6b88e"
artifact_digest: "sha256:a6f7ef90668153eeb063d34b33162424409526021475eeed97dbf342b289c109"
agent:
  host: "grok"
  provider: "xai"
  model_id: "grok-4.7"
  model_display: "grok-4.7"
  session_fingerprint: "sha256:0c26620ccf192459c096abf761f4125c0e239c36725cd214d71437bf7a857592"
  identity_source: "declared"
started_at: "2026-11-16T12:55:58.895Z"
submitted_at: "2026-11-16T13:10:35.548Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent round-2 review of the revised plan at blob `4d7a8692b8acdd011c784ef8957b37f6d2b6b88e`, commit `e3bc34118e735a1ca80e772a8d9379d7191918c2`. I read the whole revised plan, lines 1–69, and compared it with reviewer response 1 and author response 1. No new product source was read. The prior trunk reading remains the baseline for the claims the author rechecked.

**Dispositions.** R1-F001 and R1-F002 are fixed in the normative task text, not only in the author's summary. Both optional suggestions are incorporated. The author's correction of the stamp-restore observation is also right: a step `if` that does not call `success()`, `failure()`, `always()`, or `cancelled()` is still gated on previous-step success, so the current post-test restore would not record a hit after the mapped step fails.

**R1-F001.** Line 51 now pins full mode for an unclassified path alone or mixed with any other path, checks-only for explicitly classified no-impact paths, and mapped mode for explicit no-impact plus a mapped source path. Line 52 states the same rule: checks-only only when every changed path has an explicit positive no-impact match; a mapped path mixed only with those paths keeps the mapped tests; any unclassified path, including a lone non-executable path, requires full. Fail-closed remains for shared setup, controls, and incomplete input, and line 53 still fails the check when a trusted full run cannot be established. The old "implicit no-impact" pin and the "if alongside a known mapping" wording are gone. Line 45 still withholds the documentation disposition from unclassified inputs.

**R1-F002.** The conditional stamp change is gone. Line 53 replaces the current PR-and-selection key with a versioned exact key that adds the applicable base SHA and a policy digest of the trusted selector and map blobs. The selection digest stays mode plus the sorted selected modules. A new namespace stops pre-cutover stamps from counting. `test_cache_key_is_exact_and_rejects_unsafe_values` and the workflow key assertion must pin a miss when base, policy, PR, or selection changes. Save stays behind successful validation. A content-only change with the same base, policy, and selected tests repeats the short check and does not start another full run. That matches constraint line 13.

**Optional items and the proof change.** Line 27 labels the Ledger commands as a reproduction of the known mismatch and leaves consumer inventory to the following reverse-import step, which already includes fixture, shared-setup, and subprocess declarations. Line 54 requires per-path evidence only once the delivered selector and map are the trusted base, and it keeps the control-changing PR on the old selector with full validation and legacy receipts readable. Line 66 moves stamp restore to after selection and before candidate tests, so the red head can record the cache hit, and it forbids that failed candidate from saving a stamp or publishing passing evidence. The separate exact-tree full comparison stays outside that skipped full-once step. Line 67 adds the direct-source proper-subset proof to the live set. That case was already in the Task 1 table and in #344's acceptance criteria.

**Scope.** Goal, approach, inputs, constraints, and review focus are unchanged. Scheduled backstop, Stop the Line, new runners, and a general selector remain out of scope. The edits are the two required rules, the two optional clarifications, the restore-before-test proof order, and the direct-source live proof. No unrelated task was removed or widened.

## Findings

None.

## Required changes

None.

## Optional suggestions

None.

## Decision

accepted
