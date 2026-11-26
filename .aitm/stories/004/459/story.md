---
schema: "aitm.story/v0"
id: 459
title: "Qualify Core Cost export from planning"
kind: "story"
state: "plan"
issue: "https://github.com/kburson/aitm/issues/459"
parent: 456
children: []
blocking: [230]
blocked-by: [458]
created: "2026-11-25T16:08:08Z"
updated: "2026-11-26T13:05:50.467Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
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
