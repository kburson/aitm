---
schema: "aitm.story/v0"
id: 124
title: "[M14] Compatible export and reconciliation"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/124"
parent: 100
children: []
blocking: [125, 126]
blocked-by: [123]
created: "2026-11-10T13:58:10Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M14", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "af58858131bb1cb677ce3f755942a827e5ee0ca303b9693363e5fe0b62568fc4"}
---

# [M14] Compatible export and reconciliation

[GitHub issue #124](https://github.com/kburson/aitm/issues/124) · [Parent #100](../100/story.md) · [Accepted plan leaf M14](../100/plan/multi-project-usage-monitor-implementation-plan.md#m14-versioned-exports-and-immutable-receiver-compatibility)

**Required predecessors** [M13 #123](../123/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M14. Versioned exports and immutable receiver compatibility

**Files** Extend `S/export.py` and `S/monitor_report.py`. Add `monitor receiver status --intent ID` and `monitor receiver reconcile --intent ID --evidence FILE` in `S/cli.py`. Add `T/test_monitor_export.py` and extend the receiver fixture in `T/fixtures/receiver.py`.

**Contract** `export_monitor_project(view: PublishedView, project_id: UUID, destination: Path) -> MonitorExportReceipt` and `compatible_delivery(view: PublishedView, receiver: ReceiverState) -> CompatibleDelivery`. Keep legacy `export_as_of` deterministic. Emit normalized monitor rows under a separate schema. Preserve Core-compatible original identity and receipt. Put changed immutable payloads into an explicit reconciliation queue instead of resending them. Use an approved receiver verification adapter to authenticate receipt or absence and feed M12’s exact-intent disposition. Refuse an unverified operator file. Persist the reconciliation disposition and original acceptance receipt. The fixture exercises this protocol until a real approved receiver exists. C44 itself remains separate.

- [ ] Write `test_legacy_export_bytes_remain_fixed`, `test_pending_and_disputed_rows_are_excluded_from_compatible_export`, and `test_time_correction_after_receiver_acceptance_never_reuses_key_or_charges_twice`. Add `test_accept_then_crash_resolves_receipt_or_retries_identical_after_absence`. Verify report and export use the same fenced revision and privacy allowlist, and test that a post-ACK dispute excludes the span without changing the previous view.
- [ ] Run red. Implement projection, export intent and receiver replay semantics. Run green with `test_export.py`, `test_rollup.py` and `test_monitor_recovery_fence.py`. Commit M14.
