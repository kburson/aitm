---
schema: "aitm.story/v0"
id: 116
title: "[M06] Registry and capture epochs"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/116"
parent: 100
children: []
blocking: [117]
blocked-by: [114]
created: "2026-11-10T13:57:56Z"
updated: "2026-11-10T19:35:01+00:00"
last-branch: "planning"
estimate: {"agent-hours": 4.0, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/jit.md", "plan/jit-review.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M06", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "5bdd16b045dea84255d5896501f8a057417de612aeb99af5767898eacd2a5e21"}
---

# [M06] Registry and capture epochs

[GitHub issue #116](https://github.com/kburson/aitm/issues/116) · [Parent #100](../100/story.md) · [Accepted plan leaf M06](../100/plan/multi-project-usage-monitor-implementation-plan.md#m06-explicit-registrations-and-capture-epochs)

**Required predecessors** [M04 #114](../114/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M06. Explicit registrations and capture epochs

**Files** Create `S/monitor_registry.py`, `S/monitor_control.py` and `T/test_monitor_registry.py`. Extend `S/cli.py` with `monitor project register --config FILE`, `monitor source approve --config FILE`, `monitor project anchor add --project UUID --config FILE`, `monitor capture enable|disable --project UUID --source ID` and `monitor command status --id ID`.

**Contract** `Registry.register_project(request: ProjectRegistrationRequest) -> RegisteredProject` and `Registry.set_permission(change: CaptureChange, boundary: VerifiedBoundary) -> CaptureEpoch`. Store owner-approved roots and project-to-provider permission edges outside Git. Resolve physical anchors and reject cross-project identical or nested anchors. A project’s immutable identity survives display-name and remote changes. Store an optional default driver per project and enforce the adopted legacy registry refusals. Preserve per-stream enrollment, disable and re-enable boundaries. `ControlInbox.enqueue(command: ControlCommand) -> ControlReceipt` stores owner-authorized commands with stable request IDs in a private inbox. Only the monitor writer applies them after validation. Bootstrap registration before activation uses the same command contract under the coordinator lease, and an enqueue receipt does not claim the boundary was applied.

- [ ] Write `test_two_clones_share_identity_but_nested_foreign_anchor_fails`, `test_disable_reenable_excludes_late_disabled_interval` and `test_revoked_root_is_not_reread_for_prior_revision`. Assert pre-disable admitted work can settle where authorized, a crossing unsplittable span is a gap, and re-enable cannot backfill the disabled interval.
- [ ] Run red. Implement registration and epoch matching, then run green with `test_scan.py`. Test exact command retries and the distinction between queued and applied status. Commit M06.

[Accepted independent pickup](plan/jit.md) · [Review iterations](plan/jit-review.md).
