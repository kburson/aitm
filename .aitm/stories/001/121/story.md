---
schema: "aitm.story/v0"
id: 121
title: "[M11] Root watches and coordinator"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/121"
parent: 100
children: []
blocking: [123, 125]
blocked-by: [115, 120]
created: "2026-11-10T13:58:05Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M11", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "dd02c042d3e85c1e0e5b2d00006f513cf93ff24a2120a23f156e1e85910d8e94"}
---

# [M11] Root watches and coordinator

[GitHub issue #121](https://github.com/kburson/aitm/issues/121) · [Parent #100](../100/story.md) · [Accepted plan leaf M11](../100/plan/multi-project-usage-monitor-implementation-plan.md#m11-shared-root-watchers-and-coordinator)

**Required predecessors** [M05 #115](../115/story.md), [M10 #120](../120/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M11. Shared root watchers and coordinator

**Files** Create `S/host_watch.py`, `S/monitor.py` and `T/test_monitor_watches.py`. Add coordinator entry in `S/service.py` while keeping the old service interface available for rehearsal and rollback.

**Contract** `WatchSet.events(timeout: float) -> tuple[WatchEvent, ...]` and `Monitor.run_once(now: float) -> MonitorCycle`. Use checked ctypes bindings for Darwin FSEvents on a dedicated run-loop thread and Linux recursive inotify behind the same boundary. Include native resource ownership in the JIT split decision. Enroll new directories, invalidate stale locators after rotation, and request bounded metadata-first reconciliation after overflow or restart. Discover each authorized root once and reread only changed or due streams. Drain queued control commands through the coordinator, join scope proposals to native receipts before applying them, and return queued, applied or refused status. Exercise register, mark, handoff, dispose and park through their CLI paths, including a mismatched receipt and an unauthorized scope proposal.

- [ ] Write `test_watch_overflow_and_nested_rotation_reconcile`, `test_shared_root_enumerates_once_for_many_projects`, and `test_unchanged_parked_payload_is_not_read`. Verify a changed parked source wakes independently and a lost root becomes a coverage gap. Write during suspend or watch loss and recover on wake or bounded fallback without a queued event.
- [ ] Run red. Integrate scheduler, discovery, route decisions and guarded delivery. Run green with `test_monitor_scheduler.py`, `test_scan.py` and real watch probes. Commit M11.
