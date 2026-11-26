---
schema: "aitm.story/v0"
id: 459
title: "Qualify Core Cost export from planning"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/459"
parent: 456
children: []
blocking: [230]
blocked-by: [458]
created: "2026-11-25T16:08:08Z"
updated: "2026-11-26T14:18:31.506Z"
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

[PR #463](https://github.com/kburson/aitm/pull/463) entered Test at head `51d19ac11c8c515abf95664058b577e5bc2a7452` against trunk `0f8c6ff70b5112bd3a17af3a2ab5665e347a416c`. Focused tests, Ruff and wheel smoke passed. Hosted verification and replacement source disposition are pending.

The replacement source has independent approval. GitHub cancelled both hosted macOS opportunities before assigning a runner. The story remains in Test with the authenticated CI pass, the local installed-wheel results, and the provisional #461 fixture evidence recorded. [Source approval and verification hold](attachments/qualification/459-independent-source-review.md).

The owner-directed Linux-first checks passed. The exact CI and documentation delta received independent approval. [Combined review and verification](attachments/qualification/459-linux-first-source-review.md).

## Delivery

[Linked PR #463](https://github.com/kburson/aitm/pull/463) merged to protected trunk at `a5ad6965c1c5b8817c0503dedbf55f576b5ddc67`. The reviewed producer and unchanged fixture passed local, hosted and portable-wheel verification. The delivered wheel generated identical #461 bundles on replay. The fixture recorded three pending rows and zero accepted scoped rows. Story Cost remained held with a known **$0.1754084 Standard API-equivalent subtotal**. [Parity and handoff](attachments/qualification/459-delivery.md) · [Sign-off](retro/2026-11-26-delivery-sign-off.md).

## Agent Cost

| Agent turn or activity | Cached input tokens | New input tokens | Output tokens | Cost reference USD |
| --- | ---: | ---: | ---: | ---: |
| Codex design builder check | Unknown | Unknown | Unknown | Unknown |
| Claude plan XPR initial review | 288,822 | 49,065 | 5,488 | Unknown |
| Claude plan XPR consensus review | 263,897 | 9,013 | 1,936 | Unknown |
| Claude exact-source review | 658 | 32,098 | 17,288 | $0.301334 |
| Claude replacement source review | 32,754 | 25,564 | 2,553 | $0.432391 |
| Claude Linux-first CI review | 658 | 8,949 | 4,383 | $0.079688 |
| Claude replacement CI and documentation review | 9,605 | 6,083 | 845 | $0.113426 |
| Codex refinement and exporter implementation | 53,058,176 | 388,481 | 72,997 | Unknown |
| Codex CI policy and delivery through cutoff | 17,827,968 | 48,525 | 17,529 | Unknown |
| **Known subtotal** | 71,482,538 | 567,778 | 123,019 | $0.926839 |

The coordinating turn was active at cutoff `2026-11-26T14:18:30.656Z`. Provider-reported cache creation is included in new input. CLI reference amounts and verified billing are distinct. Verified billed cost is Unknown.

[Agent Cost evidence](attachments/qualification/459-agent-cost.json).
