---
schema: "aitm.story/v0"
id: 143
title: "[#133 T06] Deliver local advisory feedback"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/143"
parent: 133
children: []
blocking: [172]
blocked-by: [142]
created: "2026-11-10T16:51:10Z"
updated: "2026-11-12T14:48:25Z"
last-branch: "planning"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-12-143-local-tia-design.md", "design/reviews/sar-2026-11-12-wave50-design/review-manifest.md"], "plan": ["plan/2026-11-12-143-refinement.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T06", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "fc2eef29fc3410c7e4a56949ba44c28dc76ef94ee4fc87557d71bd44ca2bdbcb"}
---

# [#133 T06] Deliver local advisory feedback

[GitHub issue #143](https://github.com/kburson/aitm/issues/143) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L256)

**Required predecessors** [T05 #142](../142/story.md).

The planning estimate is 3 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T06. Deliver local advisory feedback — 3h, P2, T05

**Owns** `tools/ci/tia/local.py`, `test_tia_local.py`.
**Interface** `python -m tools.ci.tia.local --base <ref> --plan|--run`.

- [ ] `test_local_dirty_snapshot_never_mints_hosted_proof` and
  `test_selection_failure_runs_entire_applicable_suite` check output
  scope, deduped IDs, actual exit status and full escalation.
- [ ] Render summary plus a machine-readable plan and runner result.
  Stop on post-snapshot drift or unsupported required capability.
  V(local) passes and a controlled local fixture runs both modes.

## Wave 50 leaf design and refinement

- [Design](design/2026-11-12-143-local-tia-design.md) · SHA-256 `467f647b560118c51783313118b01854c8cecb4fc4d53083005a00411cdcbc96`
- [Refinement](plan/2026-11-12-143-refinement.md) · SHA-256 `8320cbccf6f113b8001d900f020fec8a79a61ff1c7b2bcd6195ffa0b16019e99`
- [Independent review](design/reviews/sar-2026-11-12-wave50-design/review-manifest.md)
