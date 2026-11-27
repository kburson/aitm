<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-da800297e0b0c147b91cbdf5f1aad338"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/005/522/design/history-import-design.md"
artifact_commit: "24b64a383b3acce48f502ff391f777bc0ed0fffd"
artifact_blob: "5cac02dcdf9249ee8dc9628490f9690b11cf7947"
artifact_digest: "sha256:5d414016baf1d3c68360808d831cdc95d7198f25856c44230ee5b183394a5109"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:95893d0f86ac4fe1742705c376e1ca0f6d6c9a5fed1c21c230c0310a96695d6b"
  identity_source: "runtime"
started_at: "2026-11-27T06:13:32.030Z"
submitted_at: "2026-11-27T06:17:45.205Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This round re-reviews `history-import-design.md` at blob `5cac02dc`. I checked it against author response 1 and against the current M2 `github-extension-design.md` § Read-only source access for M7 (lines 24–28). I also re-checked the M8 handoff, which is unchanged.

Status of the round-one findings:

1. **Replay vs. live drift: resolved.** Import step 2 requires exact hash and count equality only when replaying the same captured manifest and bytes, including on a fresh checkout. A live re-extraction is a separate capture. It reports changed, added and missing records, or unknown coverage, against the earlier pin. This matches M2's statement that "A live reread … may drift."
2. **Identity revision: resolved.** The identity key now includes the source item ID and an acquired revision. The acquired revision is the returned update timestamp plus #525's acquired-record digest. M2 now defines that digest exactly (canonical JSON, body presence/digest, SHA-256). A post-cutoff update gives a chronology-unproved disposition unless independent evidence proves the pre-work revision. This is the conservative reading. It also fits M2's revised cutoff wording ("Neither proves a content edit or establishes the bytes present at cutoff").
3. **Commit/approval evidence: resolved.** Commit history, unselected comments and outside approval evidence are now optional, with a source-unsupported disposition. Their absence does not invalidate the #525 handoff. The Handoff receipts coverage check validates only the required initial fields and records unsupported optional sources. M2 now lists the same kinds as outside the initial adapter contract and reports covered and unsupported kinds in the handoff.
4. **Predicate ordering: resolved with an alternate approach.** I accept it. #525 now takes comment selection as an explicit, versioned request input. It qualifies that mechanism with its own fixture and an approved live predicate, and the receipt records the predicate ID and version. M7 pins its own predicate after #525 qualifies and before capture. This removes the reverse prerequisite and keeps #525 independently landable. M7 and M2 describe it the same way.
5. **Restricted replay: resolved.** An authorized second reader re-normalizes the restricted captured replay bundle inside the retention boundary. The publishable view is checked by manifest and digests. This also gives the M8 receipt's "independent replay" a clear meaning.

The two round-one optional suggestions were also taken: the decomposition label now reads "pinned intake and source inventory", and "complete pair" is now spelled out. The estimate still sums to 18.5 with every row at or under 4 h, and rank 260 is unchanged.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Which evidence can prove pre-work estimate chronology.** M2 puts edit history outside the initial adapter, so an issue body's current bytes can't show that a phase estimate predates work. This holds even for issues with no post-cutoff activity, because an edit before the cutoff but after work started is invisible. The draft's "unproved estimate chronology stay visible" rule (line 29) handles this safely. The trusted-Timing-Log-format decision (line 44) could add one sentence naming which admitted evidence can prove chronology, for example an estimate in a selected comment whose `created_at` equals its `updated_at` and precedes the first work interval. Without that, the qualified-label yield could fall to zero for an avoidable reason rather than a real data gap. M8 already handles a low yield correctly.
2. **Revision churn on issue records.** An issue's `updated_at` and acquired-record digest change with non-body activity: new comments, label or state changes. Each such change creates a new acquired revision of the same issue across captures. It may help to say that live-drift reports separate body or estimate changes from metadata-only activity, so reviewers aren't flooded with no-op corrections.

## Decision

accepted
