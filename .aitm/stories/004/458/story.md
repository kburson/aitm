---
schema: "aitm.story/v0"
id: 458
title: "Publish pinned story effort and cost reports"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/458"
parent: 456
children: []
blocking: [459]
blocked-by: [457]
created: "2026-11-25T16:06:40Z"
updated: "2026-11-26T04:21:29.679Z"
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

[Implementation plan](plan/2026-11-25-pinned-story-effort-cost-plan.md) passed brokered plan XPR. [Plan review](../../../../docs/peer-reviews/plan/2026-11-26-2026-11-25-pinned-story-effort-cost-plan-review-844ccd1b697dc6e97c24b0bfb13a62fd/review-844ccd1b697dc6e97c24b0bfb13a62fd-review-manifest.md). The planning baseline is the verified #457 merge. The #461 sample and existing #181 path remain the proposed qualification targets.

Implementation pickup verified on protected trunk `87bc3d8a` after plan XPR `3b821b73`. The delivery target is trunk via `codex/458-pinned-story-reports`, with exact-head source review, authenticated CI and portable fixture checks.

[PR #462](https://github.com/kburson/aitm/pull/462) is in Test at head `5886ddd5de0c614af22138da94cef2ac898ae4e5` against trunk `87bc3d8a2875884014b59281117f68b9d63fabee`. The local focused effort and dashboard checks passed. Hosted CI and exact independent review are pending.

The Windows checkout converted the reviewed rate card to CRLF on candidate `5886ddd5`. The reproduced hash matched the hosted failure. Returned to Develop for an LF checkout rule that preserves the exact reviewed digests. [Superseded Windows run](https://github.com/kburson/aitm/actions/runs/45753000200/job/139684959255).

Replacement head `f709813b81fbe3b63329baa4e3d86b72081dd04e` preserves the two reviewed rate digests with checkout conversion enabled. Fresh CI and exact review are required for this head.

All nine hosted checks passed on the replacement head. All three installed-wheel artifacts report 220 passing fixtures each from the same tested merge tree. The trusted verifier requires the exact independently reviewed tree because the test inventory changed. [CI](https://github.com/kburson/aitm/actions/runs/45753366160) · [Portability](https://github.com/kburson/aitm/actions/runs/45753366161).

## Delivery

[Linked PR #462](https://github.com/kburson/aitm/pull/462) merged to protected trunk at `0f8c6ff70b5112bd3a17af3a2ab5665e347a416c`. The reviewed source, hosted CI, installed-wheel validation and exact delivered tree passed. The live #461 report is registered, reopens byte-for-byte, and reports the known **$0.1754084 Standard API-equivalent subtotal** for three turns. Project Cost is held for open admission and verified billed cost is Unknown. [Delivery evidence](attachments/qualification/458-delivery.md) · [Implementer sign-off](retro/2026-11-25-delivery-sign-off.md) · [Frozen #461 report](https://github.com/kburson/aitm/blob/52e57ed3c7ea54c473fe6b223d09000269856f2e/.aitm/stories/004/461/attachments/effort/reports/0feeb1478d08640faee709e4fff72b4e60d5cf39191eba36a9ca99baa0f0c40e.json).

## Agent Cost

| Agent turn or activity | Cached input tokens | New input tokens | Output tokens | Cost reference USD |
| --- | ---: | ---: | ---: | ---: |
| Design XPR | Unknown | Unknown | Unknown | Unknown |
| Plan XPR | Unknown | Unknown | Unknown | Unknown |
| Coverage and pinned reader implementer | Unknown | Unknown | Unknown | Unknown |
| Report pricing implementer and slice review | Unknown | Unknown | Unknown | Unknown |
| Protected publication and Cost adapter implementer | Unknown | Unknown | Unknown | Unknown |
| Grok preliminary source review | 168,064 | 79,258 | 70,141 | $0.451108 |
| Claude exact-head source review | 658 | 88,948 | 31,478 | $0.670634 |
| Claude hosted gate confirmation | 89,604 | 32,631 | 529 | $0.815404 |
| Codex implementation and delivery (partial turn) | 33,609,472 | 623,513 | 74,298 | Unknown |
| **Known subtotal** | 33,867,798 | 824,350 | 176,446 | $1.937146 |

The implementing turn was active at cutoff `2026-11-26T04:20:34.058Z`. New input includes cache creation where the provider reports it. Cost references come from provider CLI output. Verified billed cost is Unknown.

[Agent Cost evidence](attachments/qualification/458-agent-cost.json).

GitHub issue closed at `2026-11-26T04:21:00Z`. Project 24 read back **Done** with merged [PR #462](https://github.com/kburson/aitm/pull/462) in Linked pull requests.
