<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-a4a8291ce43671588b36a83b461ad7fa"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/003/368/plan/2026-11-17-368-hosted-ancestry-run-findings.md"
artifact_commit: "6aebc0300ac50d07d34fa74516a78ab5264314c4"
artifact_blob: "0219a6254b6da55ddf2de71464158d5ad2684a59"
artifact_digest: "sha256:e3b27b2243efc1afcbf893eee8f8e36e5ccaf4ea8c9d99bc4238e77638ddf3a3"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:906d1c8ad78ca7a3a1895ccc186d94a7954127640f6c4ef55680b7319be12fd8"
  identity_source: "runtime"
started_at: "2026-11-17T12:54:48.850Z"
submitted_at: "2026-11-17T12:56:43.907Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed `2026-11-17-368-hosted-ancestry-run-findings.md` (blob `0219a62`) against these sources:

- the accepted plan `2026-11-17-368-hosted-ancestry-implementation-plan.md`, mainly the "Full hosted run and decisions" checklist;
- the execution packet `2026-11-17-368-hosted-ancestry-execution-packet.md`;
- the machine receipt `attachments/2026-11-17-368-hosted-ancestry-run-receipt.json`;
- the local evidence `attachments/2026-11-17-368-ancestry-local-reproduction.json`;
- the prior findings `2026-11-16-368-hosted-qualification-findings.md`;
- the five retained GitHub API responses in `/Users/Shared/aitm368-ancestry.9nEAFE39/` (`hosted-at-deadline-run.json`, `hosted-at-deadline-jobs.json`, `hosted-final-run.json`, `hosted-final-jobs.json`, `hosted-final-artifacts.json`).

The HOLD verdict is correct, and the artifact does not overstate any result. These facts check out:

- **Run identity.** Run `44085388689`, attempt 1, job `134046345090`, head `f5f1cf8f…` and tree `4c9cc4a5…` match the receipt and the retained run JSON (`head_commit.tree_id`). The job requested `labels: ["macos-26"]`.
- **Timing.** The run was created at `12:40:43Z`. Acceptance was at `12:31:32Z`. Acceptance + floor(0.348 h × 3600 s) = acceptance + 1252 s = `12:52:24Z`, which matches the receipt and packet deadline.
- **Final job state.** The final job is `completed`/`cancelled` at `12:52:42Z` with `steps: []`, `runner_id: 0` and an empty runner name. The artifact list has `total_count: 0`. Together these show that no runner was ever assigned and no step ran, independent of the at-deadline snapshot.
- **Local evidence.** The old profile gives `LedgerError` with exit 4. The revised profile gives exit 0 with a six-identity chain (`/`, `/Users`, `/Users/Shared`, lab, `worker`, `synthetic`), and the Python driver asserts the same physical path. `worker_rows` begins with the exact `controller_rows` text. It then lists eight EPERM rows: three LIST, two STAT, two ACL and one DATA. The green log shows 13 tests passing, which matches the packet's 12 existing tests plus 1 new test.
- **Profile change.** The profile delta adds exactly the three literal metadata grants.
- **Unchanged context.** The 7/23 baseline matches the prior findings table (`44028499403/1`). #368 stays open and #355 stays blocked, which matches `native_edge`.

Before acceptance, two things need fixing. The closeout does not state its budget consequence or its final charges. The decisive hosted evidence is also cited only by an unhashed, machine-local path. Neither changes the HOLD.

Limits of this review: this session could not run a hashing tool. I could not recompute the receipt SHA-256 `a3378e20…`, the local-evidence SHA-256 `cf32ba75…`, or the source blob and digest table. I checked them only for consistency between the receipt and the packet. I did not query the live GitHub API. I relied on the retained responses described above.

## Findings

1. **The closeout does not state that the 2.5-hour admission/preflight stop is exhausted, and it omits the closeout charges the plan requires.**
   - The plan applies "the original 2.5 cumulative admission/preflight-hour stop". It says the original limits govern this pickup and that closeout counts toward the overall and packet limits.
   - The artifact says the plan "charges the prior 2.152 preflight-hour upper bound plus the 0.348-hour new admission window". Those add up to exactly 2.5 h. The admission/preflight budget is therefore fully spent, but the artifact never says so.
   - The artifact then says "A new reviewed admission window with a fresh exact packet is required for another live attempt." Under the governing limits, a reviewed packet alone cannot open a new admission window. Another attempt also needs the owner's explicit authorization of new admission/preflight budget, or an approved change to the 2.5 h stop. As written, a reader could think the next step is only another packet review.
   - The receipt's `clock` block copies the acceptance-time values (`cumulative_hours_at_acceptance: 2.775611`, `headroom_to_packet_hours: 0.974389`, `headroom_overall_hours: 3.224389`). Neither the artifact nor the receipt records the cumulative overall and packet-limit charges at HOLD or closeout. Readers cannot check the remaining 3.75 h packet budget and 6 h overall budget, which the next pickup needs.

2. **The decisive hosted evidence is cited only by an unhashed, uncommitted, machine-local path, and the at-deadline snapshot has no capture time.**
   - The last line points to `/Users/Shared/aitm368-ancestry.9nEAFE39`. That is the mutable scratch lab, which also holds SAR drafts, workspaces, copied product source and sandbox fixtures. It is not in the repository, and neither the receipt nor the artifact records a digest of the five API responses.
   - The packet bound its local evidence by SHA-256. The stop-condition evidence here gets weaker custody than that, even though it is what justifies the HOLD.
   - The artifact says "The recorded status at expiry was `queued`". In `hosted-at-deadline-run.json`, `updated_at` is `12:40:43Z`. Neither that file, `hosted-at-deadline-jobs.json` nor the receipt (`status_at_deadline`) records when the snapshot was taken. So nothing shows that it was observed at or after `12:52:24Z`.
   - The conclusion still holds, because the final job record (`completed_at: 12:52:42Z`, `runner_id: 0`, `steps: []`) proves no runner was assigned before cancellation. But the artifact should rest the claim on evidence that can actually be verified.

## Required changes

1. In "Exact attempted run and stop condition", state plainly that the 2.152 h + 0.348 h charge reaches the original 2.5-hour cumulative admission/preflight stop. Say that another live attempt therefore needs the owner's explicit authorization of new admission budget, or an approved change to the stop, in addition to a fresh reviewed packet with a new deadline. Record the cumulative overall and packet-limit charges at HOLD or closeout, with timestamps, in the artifact or the receipt. This applies the plan's "record both charges" and "closeout counts" requirements to this endpoint.
2. Bind the five retained GitHub API responses by SHA-256: in the receipt (then refresh the receipt digest in the artifact), in a committed attachment, or both. Record when the at-deadline snapshot was captured. Otherwise, reword "The recorded status at expiry was `queued`" so that the HOLD rests on the final job record: `completed_at 12:52:42Z`, after the deadline, with `runner_id 0` and zero steps. Name that record as the controlling evidence.

## Optional suggestions

1. The packet calls `12:52:24Z` the "product dispatch deadline". The artifact calls it the "admission deadline". Use one term, or note that they are the same instant, so a reader comparing the documents doesn't suspect two different bounds.
2. Record queue latency as an input for the next packet's timebox. The push happened about 9 min 11 s into the 20 min 52 s window, and the job then sat queued for at least 11 min 41 s with no runner. That supports reserving more of any future window for `macos-26` runner allocation, or starting the hosted reservation earlier.
3. Say "home-directory and canary metadata" instead of "child metadata". The two STAT/ACL targets are `/Users/kpburson` and the `.canary` sibling, not children of the admission root.

## Decision

revisions-requested
