---
schema: "aitm.story/v0"
id: 459
title: "Qualify Core Cost export from planning"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/459"
parent: 456
children: []
blocking: [230]
blocked-by: [458]
created: "2026-11-25T16:08:08Z"
updated: "2026-11-26T13:12:32.345Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: null
origin: ".aitm/stories/004/455/attachments/455-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/2026-11-26-core-cost-fixture.md"], "plan": ["plan/2026-11-26-core-cost-fixture-plan.md"], "attachments": []}
expansions: []
trips: []
---

# Qualify Core Cost export from planning

[GitHub #459](https://github.com/kburson/aitm/issues/459)

Preserve the useful producer outcome from #124 with a deterministic planning export for Core.

## Acceptance

- Pin the existing approved receiver-fixture contract. Qualify stable receipt identities, normalized payloads, verified provenance, and compatible versioning. Use the same pinned report inputs and keep partial or disputed usage visible under the consumer contract.
- Exercise identical retry, late or corrected input, and ambiguous receiver disposition. Verify receipt or absence through the fixture path before reconciliation. Refuse conflicting payloads and prove privacy at the export boundary.
- Publish fixture parity and compatibility evidence usable by #230. Use the agreed receiver fixture independently of #51 implementation delivery. #230 retains #51 and owns live receiver qualification.

[Spike findings](https://github.com/kburson/aitm/blob/f39eb4d681c86f3c9a747d606e95d969e900b43b/.aitm/stories/004/455/attachments/455-findings.md) · [#230](https://github.com/kburson/aitm/issues/230)

## Refinement and plan

The #458 predecessor is delivered. This story adapts its exact report inputs to the existing M14 receiver fixture. The planning estimate is 3.5 implementation agent-hours, size S. It includes local and hosted qualification and independent source review. [Design](design/2026-11-26-core-cost-fixture.md) · [Plan](plan/2026-11-26-core-cost-fixture-plan.md).

Claude Sonnet 5.5 accepted the revised plan in the sealed XPR. Pickup is pinned to trunk `0f8c6ff70b5112bd3a17af3a2ab5665e347a416c`. [XPR consensus](https://github.com/kburson/aitm/blob/e2478a2815c28c75a529dc0c20151ef484ebbf69/docs/peer-reviews/plan/2026-11-26-2026-11-26-core-cost-fixture-plan-review-267e823be939722787b850589663a74b/review-267e823be939722787b850589663a74b-review-manifest.md).
