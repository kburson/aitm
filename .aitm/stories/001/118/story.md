---
schema: "aitm.story/v0"
id: 118
title: "[M08] Service journal and claim order"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/118"
parent: 100
children: []
blocking: [119]
blocked-by: [117]
created: "2026-11-10T13:58:00Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M08", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "2b43bde5c32a6a64be8230b656f2a37ca972b453a1df7bac6767701cb2198d9f"}
---

# [M08] Service journal and claim order

[GitHub issue #118](https://github.com/kburson/aitm/issues/118) · [Parent #100](../100/story.md) · [Accepted plan leaf M08](../100/plan/multi-project-usage-monitor-implementation-plan.md#m08-single-owner-journal-and-verified-revision-order)

**Required predecessors** [M07 #117](../117/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M08. Single-owner journal and verified revision order

**Files** Create `S/monitor_journal.py` and `T/test_monitor_journal.py`.

**Contract** `RoutingJournal.reserve(candidate: RoutedRevision, progress: StreamCursor) -> ClaimDisposition`. Take a stable per-user coordinator lease. In one transaction reserve the canonical observation’s only project and retain normalized pending revision and replay cursor. A causal successor can supersede the current revision. Identical or proven older revisions have no additive effect. Incomparable content becomes disputed. `RoutingJournal.record_disposition(change: VerifiedRouteDisposition) -> JournalChange` records a causal scope conflict, coverage change or folded-usage replacement against the affected keys. Preserve prior views. A superseding covering representation and the withdrawal of its children must share a single publication change.

- [ ] Write `test_competing_project_claims_cannot_double_charge`, `test_causal_revision_survives_stale_replay_after_restart` and `test_reservation_and_cursor_commit_together`. Assert provider archive copies keep one canonical key, a distinct verified retry keeps its own key, and an injected rollback leaves no partial claim or cursor movement.
- [ ] Run red. Implement private keyed journal and lease. Run green with `test_ledger.py`. Commit M08.
