<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a4a8291ce43671588b36a83b461ad7fa"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-run-findings.md"
artifact_commit: "e09af44445322e54bb8ec7a38e6ef928c12ee395"
artifact_blob: "9a2560235b9215e275ccaf857296903922c70fac"
artifact_digest: "sha256:08283cca09f45ed85d6c77f56ac49d3311fbbcdd6f40cce523227fe618ffc54e"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:906d1c8ad78ca7a3a1895ccc186d94a7954127640f6c4ef55680b7319be12fd8"
  identity_source: "runtime"
started_at: "2026-11-17T12:54:48.850Z"
submitted_at: "2026-11-17T12:58:51.075Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I re-reviewed the revised artifact (blob `9a25602`) against my turn-1 findings, using these sources:

- the author's response 1;
- the new attachment `attachments/2026-11-17-368-hosted-ancestry-api-readback.json`;
- the unchanged run receipt;
- the accepted plan's limits;
- the five retained raw responses, which are still in `/Users/Shared/aitm368-ancestry.9nEAFE39/`.

**Finding 1 (budget consequence and closeout charges) is resolved.**

- Lines 27–32 now say that 2.152 h + 0.348 h exhausted the original 2.5-hour admission/preflight stop. They also say another attempt needs the owner's explicit authorization of new admission budget, or an approved revision to the stop, followed by a fresh reviewed packet with a new product dispatch deadline.
- I recomputed the HOLD charges:
  - Acceptance cumulative 2.775611 h + (`12:52:42Z` − `12:31:32Z` = 1270 s = 0.352778 h) = **3.128389 h**.
  - Packet limit: 3.75 − 3.128389 = **0.621611 h** left.
  - Overall limit: 6 − 3.128389 = **2.871611 h** left.
- These match `charge_at_hold` in the attachment and the rounded figures 3.128, 0.622 and 2.872 in the artifact.

**Finding 2 (custody and capture time of the hosted evidence) is resolved.**

- The new attachment binds each of the five responses by SHA-256. It records each capture-completion time and copies the deciding fields.
- The at-deadline run and job snapshots completed at `12:52:40.18Z` and `12:52:40.82Z`. Both are after the `12:52:24Z` deadline and before the `12:52:42Z` cancellation. So "The recorded status at expiry was `queued`" is now backed by evidence that was captured inside the right interval.
- The recorded fields match the raw files I read in turn 1:
  - at-deadline: `status: queued`, `runner_id: null`, `steps: []`, `labels: ["macos-26"]`;
  - final: `completed`/`cancelled` at `12:52:42Z`, `runner_id: 0`, `steps: []`;
  - artifacts: `total_count: 0`.
- `queued_seconds_before_deadline: 701` matches `12:40:43Z` → `12:52:24Z`.

**Optional suggestions.** Suggestion 1 was adopted: the artifact now uses "product dispatch deadline" throughout. Suggestion 3 was adopted: line 14 now reads "home-directory and canary metadata". Suggestion 2 (queue latency) was taken up only in the attachment, which is acceptable.

Limits of this review are unchanged: no hashing tool was available. I did not recompute the SHA-256 of the attachment (`5ffe99d4…`), of the receipt (`a3378e20…`) or of the five raw responses. I checked them for consistency only.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Line 37 says the raw responses are "held in the executor's private cache". They are still in the 0700 scratch lab `/Users/Shared/aitm368-ancestry.9nEAFE39/`. Naming that path, or the path they move to, would let a resumer find the files that the attachment's hashes bind.
2. Author response 1 says the final job was named as the controlling evidence, but the artifact text does not say so. This does not block acceptance, because the at-deadline capture time now supports the claim directly.

## Decision

accepted
