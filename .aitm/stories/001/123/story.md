---
schema: "aitm.story/v0"
id: 123
title: "[M13] Snapshot reports"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/123"
parent: 100
children: []
blocking: [124, 230]
blocked-by: [121, 122]
created: "2026-11-10T13:58:08Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M13", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "af164cbe3b92708780913eb04fe54d6ae42327e3b33b1235089da3805733e8ba"}
---

# [M13] Snapshot reports

[GitHub issue #123](https://github.com/kburson/aitm/issues/123) · [Parent #100](../100/story.md) · [Accepted plan leaf M13](../100/plan/multi-project-usage-monitor-implementation-plan.md#m13-pinned-project-and-story-reports)

**Required predecessors** [M11 #121](../121/story.md), [M12 #122](../122/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M13. Pinned project and story reports

**Files** Create `S/monitor_report.py` and `T/test_monitor_report.py`. Connect the fence to the coordinator in `S/monitor.py`, and reuse relationship and rollup logic in `S/rollup.py`. Add CLI `report projects` and `report stories --project UUID --snapshot ID` in `S/cli.py`.

**Contract** `ReportReader.projects(window: ReportWindow, rates: RateBasis) -> ProjectSummary` and `ReportReader.stories(project_id: UUID, snapshot_id: str) -> StoryBreakdown`. `Monitor.publish(candidate: PublicationCandidate) -> FencedPublication` must protect the candidate with M12 before making it visible to `ReportReader`. `PublishedViewStore.open(snapshot_id: str) -> PublishedView` reopens a durable manifest keyed by the fenced snapshot. Pin its journal view, ledger sequences, acknowledged revisions and scope history. `SnapshotToken.issue(publication: PublicationID, window: ReportWindow, rates: RateBasis) -> str` uses a versioned, authenticated read-only token binding the exact publication ID, canonical UTC interval, rate card digest and pricing basis. Summary issues the token without persisting new state. Drilldown verifies it and loads the retained publication and exact pricing inputs. Return unavailable if a pinned input expired and refuse malformed tokens. Keep unacknowledged undisputed changes on the previous visible revision. Refuse unfenced CLI rollup for adopted projects and direct users to the new report. Keep status read-only and legacy export confined to its frozen sequence and rate card. Expose the legacy baseline without synthetic ACKs. Use the declared native observation time basis and preserve legacy times. Direct totals reconcile to distinct stories, drafts, project-wide work and unattributed story scope.

- [ ] Write `test_snapshot_pins_scope_time_and_rates_across_commands`, `test_project_totals_reconcile_without_inclusive_epic_double_count` and `test_partial_unknown_and_hookless_grok_visibility`. Verify a time correction moves only a new snapshot and a missing historical view returns explicit unavailable. Assert an ACK alone is invisible through the CLI when the coordinator cannot persist the fence. Issue summaries for two intervals over one publication and a third after a rate-card update without a new usage write. Reopen all three from a separate process after restart. Require exact original window and price or explicit unavailable if a pinned input expired. Verify a late post-ACK dispute removes current usage while the previous report stays identical.
- [ ] Run red. Implement read-only local reporting with structured JSON. Run green with `test_rollup.py` and `test_monitor_recovery_fence.py`. Commit M13.
