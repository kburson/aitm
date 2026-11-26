---
schema: "aitm.story/v0"
id: 458
title: "Publish pinned story effort and cost reports"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/458"
parent: 456
children: []
blocking: [459]
blocked-by: [457]
created: "2026-11-25T16:06:40Z"
updated: "2026-11-26T04:09:26.737Z"
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
