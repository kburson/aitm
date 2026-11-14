---
schema: "aitm.story/v0"
id: 119
title: "[M09] Project writes and ACK"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/119"
parent: 100
children: []
blocking: [120, 122]
blocked-by: [118, 199, 201, 202, 203, 204, 209, 210]
created: "2026-11-10T13:58:01Z"
updated: "2026-11-11T02:41:48+00:00"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M09", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "27ac74e3d46391ecd3bfcff3b19d46fb12f75e04be809c35aedeb4842ba299a6"}
---

# [M09] Project writes and ACK

[GitHub issue #119](https://github.com/kburson/aitm/issues/119) · [Parent #100](../100/story.md) · [Accepted plan leaf M09](../100/plan/multi-project-usage-monitor-implementation-plan.md#m09-guarded-destination-writes-and-ack)

**Required predecessors** [M08 #118](../118/story.md).

Apply the accepted plan’s [legacy command surface after adoption](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#legacy-command-surface-after-adoption).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M09. Guarded destination writes and ACK

**Files** Create `S/monitor_writer.py` and `T/test_monitor_delivery.py`. Extend `S/monitor_journal.py` and `S/ledger.py`.

**Contract** `ProjectDelivery.commit(claim: PendingClaim) -> ProjectWriteReceipt` and `RoutingJournal.ack(receipt: ProjectWriteReceipt) -> PublicationCandidate`. Reuse stable project pseudonyms and guarded transactions. `ProjectDelivery.attach(ledger: Ledger) -> WriterCustody` retains the original guard through coordinator attachment. M16 recognizes a late legacy revision only by verifying native lineage against the existing row with the adopted #83 project key and request-key algorithm. Bind the matching service claim to that original project. A project pseudonym alone cannot seed a service claim. Both operations compare exact lineage and revisions. Bound pending capacity per destination. A failed destination keeps pending state and backpressure for its shared stream. Reserve progress capacity for independent healthy streams. `RoutingJournal.publication_candidate(change: JournalChange) -> PublicationCandidate` creates a view change for a verified journal-only dispute or coverage event without inventing a project write ACK. A folded parent replaces eligible published children only after its actual write ACK and then in one publication candidate.

- [ ] Write `test_restart_at_reserve_commit_and_ack_yields_one_row`, `test_stale_ack_never_rewinds_publication`, and `test_full_destination_queue_preserves_independent_progress`. Add `test_late_conflict_after_ack_produces_dispute_without_new_write` and `test_folded_replacement_and_child_withdrawal_share_view`. Assert a blocked stream’s cursor remains replayable and settlement after recovery preserves two distinct project scopes.
- [ ] Run red. Implement guarded delivery and bounded dispositions. Run green with `test_monitor_journal.py` and `test_ledger.py`. Commit M09.

The [reviewed M08 split](../118/plan/2026-11-10-118-m08b-revision-disposition-split.md) requires [M08a #118](../118/story.md) and [M08b #199](../199/story.md).

The [second independently reviewed M08b split](../199/plan/2026-11-10-199-m08b-proof-split.md) retains #118 and #199 and adds direct prerequisites [#201](../201/story.md), [#202](../202/story.md), [#203](../203/story.md), [#204](../204/story.md). Keep the project write ACK and atomic publication of a qualifying folded replacement in M09. [Native split receipt](../199/plan/2026-11-10-199-m08b-proof-split-receipt.json).

The [accepted M08b4 split](../203/plan/2026-11-10-203-disposition-proof-split.md) adds direct [#209](../209/story.md) and [#210](../210/story.md) prerequisites while keeping all prior journal gates.

## Qualified-source release re-acceptance

The [exact R3 amendment](plan/2026-11-13-119-qualified-sources-reacceptance-r3.md) passed [independent re-acceptance](plan/qualified-source-review-r3.md). [Review status and exact digests](plan/qualified-source-review-status.json). Native graph change awaits verified installation of the replacement and folded follow-up.
