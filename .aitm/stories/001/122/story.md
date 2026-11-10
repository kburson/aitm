---
schema: "aitm.story/v0"
id: 122
title: "[M12] Recovery and publication fence"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/122"
parent: 100
children: []
blocking: [123, 126]
blocked-by: [119]
created: "2026-11-10T13:58:06Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M12", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "40fbe6a28387d25bbae6aba5da833599efec43d5ea17e27ee735a68eedc37d03"}
---

# [M12] Recovery and publication fence

[GitHub issue #122](https://github.com/kburson/aitm/issues/122) · [Parent #100](../100/story.md) · [Accepted plan leaf M12](../100/plan/multi-project-usage-monitor-implementation-plan.md#m12-independent-recovery-and-publication-fence)

**Required predecessors** [M09 #119](../119/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M12. Independent recovery and publication fence

**Files** Create `S/monitor_recovery.py` and `T/test_monitor_recovery_fence.py`.

**Contract** `RecoveryFence.protect(candidate: PublicationCandidate) -> FencedPublication` and `RecoveryFence.record_export_intent(delivery: ReceiverDelivery) -> ExportIntent`. Durably append the monotonic tail and authenticated decision digests before exposing a report view or sending an export. Keep the tail outside rollback snapshots. Prepared but interrupted publication can block replay without asserting it was exposed. Add `RecoveryFence.record_receiver_evidence(intent: ExportIntent, evidence: VerifiedReceiverEvidence) -> ReceiverDisposition`. Bind the intent and independently verified receipt or absence to the receiver identity, immutable key and payload digest. Record accepted or retry-eligible outcomes durably. Unknown or conflicting evidence remains held. A retry after verified absence must use the same receiver, key and bytes.

- [ ] Write `test_view_cannot_escape_before_recovery_fsync`, `test_restore_with_only_old_witness_holds_replay`, and `test_interrupted_export_requires_receiver_reconciliation`. Inject failure before and after persistence. Assert replay stops at the last proven common boundary when the current witness is missing.
- [ ] Run red. Implement durable write-ahead witness and recovery verification. Run green with `test_monitor_journal.py` and `test_monitor_delivery.py`. Commit M12.
