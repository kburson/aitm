---
schema: "aitm.story/v0"
id: 104
title: "[CI1] Bootstrap Actions and Python validation"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/104"
parent: 103
children: []
blocking: [105]
blocked-by: []
created: "2026-11-10T02:57:04Z"
updated: "2026-11-10T12:55:12+00:00"
last-branch: "codex/aitm-104-ci-bootstrap"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/001/103/plan/implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["design/design.md", "design/github-tested-merge-binding-replan.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/delivery-checklist.md", "plan/signing-probe-jit.md", "plan/signing-probe-pickup-review.md", "plan/delivery-jit.md", "plan/delivery-jit-review.md", "plan/local-source-review.md"], "attachments": ["attachments/github-binding-probe-attempt-1.md", "attachments/github-signing-probe-result.md", "attachments/local-delivery-checkpoint.md"]}
expansions: []
trips: []
---

# [CI1] Bootstrap Actions and Python validation

[GitHub issue #104](https://github.com/kburson/aitm/issues/104) · [Parent #103](../103/story.md) · [Parent plan](../103/plan/implementation-plan.md).

Deliver the first real Actions route with the full supported macOS suite, 90% product and helper line coverage, exact wheel smoke, and stable aggregate. Use manual exact evidence for this leaf. Verify protected delivery, the trunk check and the representative integration-target route before its own sign-off.

Refined forecast **4.0 implementation agent-hours**. Leaf design, implementation plan and exact JIT accepted in [pickup review](plan/pickup-review.md). Attempt 1 returned to **Planning** after the hosted job succeeded and the binding gate failed. [Exact binding probe evidence](attachments/github-binding-probe-attempt-1.md). [Delivery checklist](plan/delivery-checklist.md).

[Ordinary PR binding design and replan](design/github-tested-merge-binding-replan.md) accepted on exact SHA-256 `c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0` through [SAR](design/reviews/sar-2026-11-09-pr-attestation/review-manifest.md), [independent manual Codex SPR](design/reviews/spr-2026-11-09-pr-attestation/review-manifest.md), [native Claude XPR](design/reviews/xpr-2026-11-09-pr-attestation/review-manifest.md). It adds a signed attempt-to-merge proof while preserving the normal story PR. #104 remains in Planning. The previous JIT is historical. A refreshed JIT, separate execution and publication authorization, and successful live proof are required before production CI work.

A [fresh JIT](plan/signing-probe-jit.md) and [independent control review](plan/signing-probe-pickup-review.md) authorize one ordinary PR signing probe. The owner authorized the scoped signing permissions and public attestation for this probe. #104 remains in Planning.

The [single authorized signing probe](attachments/github-signing-probe-result.md) passed on draft PR #107. The certificate and signed evidence bind the exact run attempt to GitHub’s temporary merge. This checkpoint leaves #104 in Planning and records no production gate.

The [delivery JIT](plan/delivery-jit.md) and [scoped review](plan/delivery-jit-review.md) admit local preparation and review under Full-Auto. The production signing-capable push and pre-Develop transition are held pending the applicable separate authority.

[Local delivery checkpoint](attachments/local-delivery-checkpoint.md) records exact independently reviewed source and passing local evidence. The recurring-signing authorization and first-production-gate preflight remain open.

Full-Auto delivery resumed on November 10. The owner authorized recurring public attestations with the reviewed permissions and sanitized digests and metadata, and authorized #104 to enter Develop before the first CI result. Actual passing CI and independent review remain merge gates.
