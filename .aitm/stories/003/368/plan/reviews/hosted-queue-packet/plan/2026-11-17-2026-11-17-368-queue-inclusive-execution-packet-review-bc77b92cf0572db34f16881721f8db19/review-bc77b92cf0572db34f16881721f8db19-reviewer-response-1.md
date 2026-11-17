<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-bc77b92cf0572db34f16881721f8db19"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-queue-inclusive-execution-packet.md"
artifact_commit: "fb03ec8c197db1c5c4d41c81907466b66eba30c4"
artifact_blob: "f4bebd11c067e3450226a6a0292d52e5aa04ff5c"
artifact_digest: "sha256:0f2f876d2ba2891006a77a8aee43d1bce000a0d8ecfdc1ac7083bc49e833ce55"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:bb2fa3e5d45b41281bb7b95072c1b45ffcf5d5bc308a372e581ac9e1d81b4e54"
  identity_source: "runtime"
started_at: "2026-11-17T13:05:49.179Z"
submitted_at: "2026-11-17T13:07:17.244Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

The packet's technical binding is sound. The one-string deadline change, the dispatch guard semantics, the runtime pins and the qualification gates all agree with the accepted ancestry plan, the prior reviewed execution packet and the HOLD record. The budget authority does not agree. The accepted plan applies three cumulative limits: a 2.5-hour admission/preflight stop, a 3.75-hour limit for the accepted exact packet and a six-hour overall limit. The packet replaces the first and measures against the third. It never mentions the 3.75-hour packet limit, and its own figures overrun that limit by about 1.55 hours. The packet also leaves the post-expiry closeout charge against the six-hour cap unstated. Revisions are requested.

Verification performed (read-only; no Git, no artifact edits):

- `integrated.py:327-336` in `/Users/kpburson/.codex/worktrees/aitm-344-functional-tia/trunk/.github/spikes/368/` reads only `ancestry_execution.deadline_utc` and requires the strict `YYYY-MM-DDTHH:MM:SSZ` form. It refuses when `decision > deadline`. The call at line 367 passes `datetime.now(timezone.utc)` immediately before `product_invocation_started`. The retained `plan_accepted_utc` and `plan_sha256` keys therefore do not affect the guard, which matches the packet's "provenance" statement. `test_integrated.py:98-113` covers the equality, one-second-late, malformed and absent cases.
- The working-tree `stage-b-inputs.json` carries `"deadline_utc": "2026-11-17T15:03:02Z"`. The admission pins (run `44024930299`, attempt 1, artifact `14302787413`, archive `3841df4c…`, manifest `1a5e9f5d…`, runtime `402dda54…`, image `20261112.0504.1`) match the prior reviewed packet.
- The scope has 30 `node_ids` and 74 `native_children` rows. 393 + 8,570 + 10 = 8,973 archive entries, which matches the "8,973" claim.
- `aitm-368-hosted-qualification.yml:15` has `timeout-minutes: 22`, which matches the "22-minute job timeout".
- Opening charge: the HOLD recorded 3.128 h at `12:52:42Z`. With 620 s (0.172 h) to `13:03:02Z`, the total is 3.300 h, so the packet's conservative 3.301 h is consistent. 3.301 + 2.000 = 5.301 h, which is also consistent.
- I could not independently confirm commit `a3249493…`, tree `8dfc90ad…`, blob `3c0e8d65…` or the single-path diff against `f5f1cf8f…`. The instructions forbid Git, and shell execution was unavailable to me. The working-tree file content agrees with the claim, but that is not commit-level verification.

## Findings

1. **[Blocking] The packet silently overruns the accepted plan's 3.75-hour packet limit.** Accepted plan line 19 sets three cumulative limits: "the original 2.5 cumulative admission/preflight-hour stop, the 3.75 cumulative agent-hour deadline for the accepted exact packet, and six cumulative agent-hours overall." The HOLD findings (lines 27-32) recorded 3.128 h, "leaving 0.622 hours under the 3.75-hour packet limit and 2.872 under the six-hour overall limit." They also said another attempt needs "the owner's explicit authorization of a new admission budget or an approved revision to the stop."
   - This packet says the two-hour allowance "replaces the exhausted admission sub-budget" and measures cumulative work "against the six-hour overall cap" (lines 17-19). It does not mention the 3.75-hour packet limit.
   - At opening (3.301 h), only 0.449 h (about 27 minutes, to about `13:30Z`) remains under that limit. A run admitted at, say, `14:30Z` would charge about 4.75 h, roughly one hour past the packet limit, and nothing in the packet records authority for that.
   - The fresh owner authorization is the only basis for exceeding any accepted limit. The packet asserts it but does not record when it was given, its wording, or which limits it covers.
   - Either the authorization covers the 3.75-hour packet limit as well as the 2.5-hour admission stop, or the window must end no later than the instant the cumulative charge reaches 3.75 h. A reviewer cannot tell which from the packet. As written, the packet could authorize a dispatch that the accepted plan forbids.

2. **[Required] The post-expiry closeout charge against the six-hour cap is not bounded.** The packet charges 5.301 h "at expiry," which leaves 0.699 h. The guard only stops *dispatch* at `15:03:02Z`.
   - A job that dispatches just before the deadline can keep running for up to the remainder of its 22-minute timeout (≤ 0.367 h).
   - After that come the required steps: raw-evidence download and reparse, findings publication, and independent Opus 5.5/high findings review. Plan line 19 says "Closeout and plan review count toward the overall/packet cumulative limits."
   - In the worst case, under 20 minutes remains for authenticated download, reconciliation, the findings draft and an independent review. The prior HOLD cycle alone spent more than that between cancellation and the next packet.
   - The packet does not say what happens if the six-hour cap is reached during an in-flight job or closeout. The options are to stop and record a bounded HOLD with retained evidence, or to have pre-authorized closeout headroom. Without this, the overall cap can be breached through closeout, which the "conservative" accounting is meant to prevent.

## Required changes

1. Address the 3.75-hour packet limit explicitly, using one of these options:
   - (a) Record the owner's authorization (UTC time, source and verbatim or exact scope) and state that it supersedes both the 2.5-hour admission stop and the 3.75-hour packet limit for this attempt, with the new packet ceiling stated numerically.
   - (b) Shorten `deadline_utc` so that review, queue, preflight and dispatch all fall within 3.75 h. Rebind the head, tree and blob accordingly.
   
   In either case, state all three limits and their remaining headroom at opening and at expiry.
2. Bound the post-dispatch tail and closeout against the six-hour overall cap. Show the worst case: expiry charge, plus the remaining job timeout, plus evidence download and reconciliation, plus findings publication and independent review. Show that it fits, or move the dispatch deadline earlier so it does. Also state the stop rule if the cap is reached during closeout: retain authenticated evidence and record a bounded HOLD.

## Optional suggestions

1. Name the executor's cancellation trigger concretely. For example, at `15:03:02Z`, if the job status is `queued` with no runner, cancel and record the cancellation readback time. This matches the prior HOLD's evidence shape.
2. Add a one-line statement that `plan_accepted_utc` and `plan_sha256` are not read by `authorize_dispatch`, with a citation to `integrated.py:327-336`. Readers would then not need to confirm themselves that the stale acceptance key cannot affect the new deadline.

## Decision

revisions-requested
