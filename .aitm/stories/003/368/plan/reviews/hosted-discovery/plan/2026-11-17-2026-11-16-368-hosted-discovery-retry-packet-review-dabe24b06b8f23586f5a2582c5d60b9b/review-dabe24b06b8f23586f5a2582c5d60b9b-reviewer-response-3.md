<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-dabe24b06b8f23586f5a2582c5d60b9b"
role: "reviewer"
turn: 3
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-16-368-hosted-discovery-retry-packet.md"
artifact_commit: "9a061ba4c83206c3efc2861076bff487dea4449e"
artifact_blob: "10b46bdecd81653bce3d0e2576deae1ef3cdd0db"
artifact_digest: "sha256:555615f844fe5f535016e3da41bbbe81ffca4079c5d054d62cb62050d22392ce"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:798081e6024e566a3c838afa796a5d1589eec2b43d480ae37902c4d6555493c0"
  identity_source: "runtime"
started_at: "2026-11-17T05:52:31.375Z"
submitted_at: "2026-11-17T06:03:19.964Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised packet (blob `10b46bd`, digest `sha256:555615f8…`, commit `9a061ba`) against my turn-2 response and the author's turn-2 response.

**Turn-2 required change 1 is resolved:**

- The delta command in "Exact authorization" now reads `git -C /Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk diff ffe77e3e2d8f5eac625add23b37c30f40025b4ec d06b0e7f21a447cabbcd808364377a6736d16892 -- .github/spikes/368`. Its target matches the authorized workflow head on line 38 and the four-path table. The stale `3b603c6a…` reference is gone from the packet.
- The charge now reads 2.107 agent-hours, up from 1.921. That fits the added revision, reproduction and review work. I did not recompute it.

I compared the rest of the packet line by line with the turn-2 text I reviewed. Lines 1–49 are unchanged, including the head, tree, four blob IDs and SHA-256 values, and the attachment link and digest `bd0b7a61…`. Only lines 50–51 changed. This agrees with the author's statement that the source and attachment are identical to round two. The held branch `refs/heads/codex/368-hosted-qualification` still points at `d06b0e7f21a447cabbcd808364377a6736d16892`.

My turn-1 and turn-2 assessments of the design therefore still stand:

- the metadata grant is limited to the literal admission root, and only in Stage B;
- the in-job probe requires the allowed stat, the denied listing and the denied child stat, all before calibration, and stops the job otherwise;
- the launcher's `-c`/`--rootdir`/`--confcutdir` vector is consistent with the 30 bound IDs and the calibration IDs;
- the attachment ties the profile texts, the original failure, the collected IDs, the driver and the local calibration outcomes to what actually ran.

The hosted job still has to establish the independent DTrace outcomes before any product execution, and the packet says so.

Limits of this review (unchanged): I did not run Git, compute SHA-256 or blob IDs, query GitHub, or run tests. The tree, blob and attachment digests, the launcher options at the accepted head `ffe77e3e…`, and the contents of hosted artifact `14302419973` are taken from the packet and attachment.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. The turn-2 optional suggestion still applies, and it is not blocking. Consider stating explicitly, in a later record, that the hosted launcher options at `ffe77e3e…` were exactly `-p no:cacheprovider --rootdir <PRODUCT>`, without `-c` or `--confcutdir`. The local "original" case reproduces that shape.

## Decision

accepted
