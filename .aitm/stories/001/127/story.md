---
schema: "aitm.story/v0"
id: 127
title: "[M17] Privacy and scale integration"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/127"
parent: 100
children: []
blocking: [128]
blocked-by: [126]
created: "2026-11-10T13:58:15Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M17", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "c3c59d673c65d1ecaccc52edcbea8b72af7b54111d49e04f7d97dc0ae23fbade"}
---

# [M17] Privacy and scale integration

[GitHub issue #127](https://github.com/kburson/aitm/issues/127) · [Parent #100](../100/story.md) · [Accepted plan leaf M17](../100/plan/multi-project-usage-monitor-implementation-plan.md#m17-cross-project-privacy-saturation-and-scale-proof)

**Required predecessors** [M16 #126](../126/story.md).

Use the complete [NA-1 acceptance case](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#native-acceptance-case-na-1).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M17. Cross-project privacy, saturation and scale proof

**Files** Create `T/test_monitor_integration.py` and allowlisted two-project fixtures under `T/fixtures/monitor/`. Add sanitized work counters in `S/monitor.py` only where the verification needs them.

- [ ] Write `test_two_projects_same_issue_distinct_routes_and_three_roles`, `test_sentinel_secrets_never_persist_or_cross_export`, and `test_two_active_and_fifty_parked_with_one_changed_source` and `test_hookless_grok_beside_unqualified_shared_root_source_exports_no_sibling_data`. Include all NA-1 outcomes. Check actual persisted wake, hold, journal, witness, ledger, report and export data against field allowlists. Assert no unapproved path, raw provider ID or sibling identity in the emitted artifacts and no unapproved raw path in repository-visible files. Measure zero unchanged parked payload reads over a healthy reconciliation and constant root discovery count as project count increases.
- [ ] Run red if the proof finds a gap and return the fix to the owning leaf before continuing. Run all locked tests and Ruff. Capture workload read counts, latency, CPU and memory. Record release budgets from evidence. Commit M17 evidence and tests.
