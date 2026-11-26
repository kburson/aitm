---
schema: "aitm.story/v0"
id: 458
title: "Publish pinned story effort and cost reports"
kind: "story"
state: "plan"
issue: "https://github.com/kburson/aitm/issues/458"
parent: 456
children: []
blocking: [459]
blocked-by: [457]
created: "2026-11-25T16:06:40Z"
updated: "2026-11-26T02:13:05.873Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/455/attachments/455-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-25-pinned-story-effort-cost.md"], "plan": ["plan/2026-11-25-pinned-story-effort-cost-plan.md"], "attachments": []}
expansions: []
trips: []
---

# Publish pinned story effort and cost reports

[GitHub #458](https://github.com/kburson/aitm/issues/458)

Preserve the useful report outcome from #123 using #435's portable store and rollups.

## Acceptance

- Pin a story report to a `planning` commit, exact receipt revisions, time basis and cutoff, and a reviewed rate-card digest. Reopening a report preserves its wording and numbers or returns an explicit unavailable result.
- Show agent engagement, known cached/new/output splits, expected and measured turns, and pending, missing, and unattributed coverage. Preserve provider-reported amounts, per-request API-equivalent estimates, and verified billing as distinct measurements.
- Prove late arrivals, repricing, interruptions, and replay cannot silently rewrite older reports. Show known subtotals with coverage. Enforce the accepted completeness rules before publishing Project Cost. Actual has its own evidence.

[Spike findings](https://github.com/kburson/aitm/blob/f39eb4d681c86f3c9a747d606e95d969e900b43b/.aitm/stories/004/455/attachments/455-findings.md)

## Design handoff

The builder check and Claude brokered XPR are complete. The design uses #461 as the real example and the existing #181 Cost intake for eligible results. The owner directed continuation and questioned the duplicate design-approval request. The coordinator accepted the sealed XPR disposition for the existing story scope and advanced the record to planning. [Reviewed design](design/2026-11-25-pinned-story-effort-cost.md) · [XPR manifest](../../../../docs/peer-reviews/spec/2026-11-26-2026-11-25-pinned-story-effort-cost-review-619e5e7edf5b675344a5e085d33d265d/review-619e5e7edf5b675344a5e085d33d265d-review-manifest.md).

[Implementation plan](plan/2026-11-25-pinned-story-effort-cost-plan.md) is ready for plan XPR. The planning baseline is the verified #457 merge. The #461 sample and existing #181 path remain the proposed qualification targets.
