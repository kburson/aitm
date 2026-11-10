---
schema: "aitm.review-response/v0"
level: "xpr"
story: 181
role: "reviewer"
round: 2
artifact_path: ".aitm/stories/001/181/design/story-timing-dashboard-design.md"
artifact_base_commit: "307c2577e2848331f29bbd16402d82e5d95a3403"
artifact_digest: "sha256:ed54c65d42aad04bde7a4f942894beb6a2280016d5fc2ff0b6411297ce5f46a5"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:349b0f6682b403a7d39e3a413ed147008f5b5220a8e947a14d1ba9881a0c1098"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-10T20:43:55.857Z"
submitted_at: "2026-11-10T20:44:28.446Z"
start_basis: "prior-submit"
start_source: "author-response-1.md"
finding_ids: []
answered_finding_ids: []
native_source: "native/spec/2026-11-10-story-timing-dashboard-design-review-4971bb10bf0cd947510cc8f5c48ebbf4/review-4971bb10bf0cd947510cc8f5c48ebbf4-reviewer-response-2.md"
native_source_digest: "sha256:5f92376f1b514abc25e057a84c2ddd476fb951f5e906caf46329ec353ee02fef"
---

Mode: `normal`

## Summary

Re-reviewed the complete revised artifact `.aitm/stories/001/181/design/story-timing-dashboard-design.md`, lines 1–55 (full file), at blob `e5443575d6b93d2dd35165ef7cf9264628fd460e`, against reviewer response 1 and author response 1.

Turn 1, Finding 1 (single usage receipt versus per-story usage receipts) is resolved:

- Line 25 now defines an optional usage report selector. The selector binds the project, the fixed sequence or fenced report identity, the UTC window and cutoff, and the rate-card identity and pricing basis. It resolves to that report's registered per-story receipts in the pinned tree.
- Receipts from other reports are ignored for the view. A story with no receipt from the selected report shows Unknown Cost. Exactly one effective receipt per story is required. An explicit supersession chooses the evidenced revision. Conflicting candidates stay Unknown pending reconciliation. A change of cutoff or rate defines a new selector.
- Line 13 now shows the selected report identity, its cutoff and its pricing basis. It stores the selector and the sorted digests of the resolved receipts in canonical JSON, so the determinism key is now complete.
- Acceptance 1 (line 49) keys determinism on the selector. It adds the two-reports-in-one-commit case and asserts that only the selected report's receipts are used, with a single common cutoff. That matches the requested check.

All three turn-1 optional suggestions were also adopted:

- The fixture (line 35) now names three distinct agents. I re-checked the arithmetic: elapsed is 2h 45m, wall time is 2h 15m, and Actual is 3.25 agent-hours.
- Byte determinism is now scoped to the normalized JSON (line 49).
- A future-dated record is excluded at the earlier as-of, with a coverage reason (line 13).

I found no new material defect in the revised text.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Two phrases still use the old singular "usage receipt" term:
   - Line 25: "Refresh means rerun the command with the desired commit, cutoff and optional usage receipt".
   - Line 43: "existing Cost only where the chosen usage receipt supports it".

   Both still read correctly once the selector definition is in place: the line 43 phrase means the story's resolved receipt under the selector. Still, consider rewording them to "optional usage report selector" and "the story's receipt resolved by the selected usage report", so that only one term is used.

## Decision

accepted
