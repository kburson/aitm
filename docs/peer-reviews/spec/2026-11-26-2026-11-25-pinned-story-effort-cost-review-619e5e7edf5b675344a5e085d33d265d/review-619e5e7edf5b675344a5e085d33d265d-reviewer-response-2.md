<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-619e5e7edf5b675344a5e085d33d265d"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/004/458/design/2026-11-25-pinned-story-effort-cost.md"
artifact_commit: "1f66b6e322981d2eab4fcceb48cf3c010f1a65c9"
artifact_blob: "aa1cdc9940a37dff43f57d1bb7859cb9f7dad240"
artifact_digest: "sha256:9d834f6dfbcb27d1cc28c6c818e6cbcba26cb044c6963ad7ba62673c72d16a57"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-sonnet-5-5"
  model_display: "claude-sonnet-5-5"
  session_fingerprint: "sha256:d05378fe03130750b1936004faa46835ce3f83bc69d77971dde2756200e357bb"
  identity_source: "runtime"
started_at: "2026-11-26T02:06:17.062Z"
submitted_at: "2026-11-26T02:07:47.901Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-read the revised design at commit 1f66b6e3 against my five turn-1 findings and the author's disposition. Each is resolved in the design text. I did not open the linked #443, #181 or #455 documents, and I did not re-run the author's #461 receipt enumeration, so those claims remain the author's.

Turn-1 findings:

1. **Commit versus cutoff.** Resolved. The planning pin is treated as an evidence watermark. Without a reconciled coverage record through the cutoff, the report shows the observed subset and holds complete Project Cost. Older pins are named explicitly and tested.
2. **Coverage record ordering.** Resolved. The record is resolved only from matching `core.evidence.recorded` facts in the pinned story event stream. The matched fields are listed. An unregistered file is ignored. A registration with a missing file, invalid path or digest mismatch is a separate integrity gap that holds Cost. Each case appears in the acceptance scenarios.
3. **Reopen discovery.** Resolved. After readback, the report ID and artifact commit are registered in a subsequent commit. This avoids self-reference. The publisher also returns the pair before registration.
4. **Real example and fixtures.** Resolved. #461 is the real example. The `complete_cost_projection` and `partial_cost_hold` fixtures cover the eligible and held paths, and the real story may hold.
5. **Edge cases.** Resolved. The scenarios now cover the half-open window end, a turn starting at the end, a crossing interval, an observation exactly at cutoff, GPT-6.2 Sol band edges, publication conflict, and numeric read bounds.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. The coverage paragraph says twice that the record is linked through a `core.evidence.recorded` fact, once as resolution and once as linking. Merging them would remove a possible reading that there are two facts.
2. The registration commit that records the report ID and artifact commit is outside the immutable report. The design does not say what happens if registration is never completed, or if two different pairs are registered for one window and cutoff. A one-line rule, for example "multiple registered pairs hold reopen discovery", would close this.
3. The author declined numbered requirement IDs. That is acceptable, but the acceptance scenario bullets are now dense. Consider one test name per clause when the plan is written.

## Decision

accepted
