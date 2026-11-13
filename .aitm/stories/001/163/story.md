---
schema: "aitm.story/v0"
id: 163
title: "[#133 T26] Bind incident probes to the repaired revision"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/163"
parent: 133
children: []
blocking: [168]
blocked-by: [142, 162]
created: "2026-11-10T16:51:57Z"
updated: "2026-11-13T05:14:57Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T26", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "47d57a6a572301ec2cddca000bc95f0b5e6a43b2e3fcedcc0e22177116a6bd48"}
---

# [#133 T26] Bind incident probes to the repaired revision

[GitHub issue #163](https://github.com/kburson/aitm/issues/163) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L596)

**Required predecessors** [T05 #142](../142/story.md), [T25 #162](../162/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T26. Bind incident probes to the repaired revision — 3h, P1, T05/T25

**Owns** `tools/ci/tia/incident_probe.py`, `test_tia_incident_probe.py`.
**Interface** `bind_probe(incident, full_proof, approved_policy) -> IncidentProbe`.

- [ ] `test_probe_includes_all_failures_and_fences_version_change`
  rejects a stale, unsigned or client-chosen probe. Bind approval,
  current incident/version, exact repaired trunk and every verified
  failing test ID. An unresolved or missing required probe holds.
- [ ] For each challenged effective workspace, union the incident
  probe with selection over relevant local changes and conflict
  resolutions. Use trustworthy full fallback on uncertainty.
  V(incident_probe) passes for a local change that restores the bug.
  T31 and T32 consume only current authority-bound probes.

## Superseded scope hold

Keep this original scope on hold under the [reviewed #133 fallback](https://github.com/kburson/aitm/blob/62b2c5f5af388a1b889c8440d91bc89a365effbd/.aitm/stories/001/133/plan/2026-11-12-133-ci-warning-manual-recovery-replan.md). The native dependencies remain historical.
