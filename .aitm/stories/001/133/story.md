---
schema: "aitm.story/v0"
id: 133
title: "Test impact analysis, CI sharding, and Stop the Line"
kind: "epic"
state: "plan"
issue: "https://github.com/kburson/aitm/issues/133"
parent: null
children: [138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178]
blocking: []
blocked-by: []
created: "2026-11-10T15:32:13Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 146.5, "size": "XL"}
priority: "P2"
origin: ".aitm/drafts/2026-11/20261110-0915-test-impact-analysis/draft.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/test-impact-analysis-design.md"], "plan": ["plan/test-impact-analysis-implementation-plan.md"], "attachments": []}
expansions: []
trips: []
---

# Test impact analysis, CI sharding, and Stop the Line

[GitHub issue #133](https://github.com/kburson/aitm/issues/133)

As an AITM contributor, I want story validation to show which tests are
affected, run them on independent CI shards, and run the full suite
whenever impact is uncertain. If a defect escapes PR validation and
fails the scheduled trunk suite, restore trunk and deliver the fix to
all governed workspaces before ordinary work resumes.

This is a follow-on to the delivered [#103 CI quality gates](../103/story.md).

## Design review

The [graduated draft](draft.md) records the initial requirements. The
[design specification](design/test-impact-analysis-design.md) is the
accepted design. Use the [review intake](design/reviews/README.md)
to trace the exact revision and every review round.

Design accepted at raw digest `sha256:2558bcbdbcc4ed8871078428dd11ddd0381a21627d4dfb744fd13cb5832ce928` and Git blob `82581ae31746d3ddfbd5701568533d476daa15d2`.
[Manual SAR](design/reviews/sar-2026-11-10-tia-design/review-manifest.md) ·
[Independent Codex SPR](design/reviews/spr-2026-11-10-tia-design/review-manifest.md) ·
[Native Claude XPR](design/reviews/xpr-2026-11-10-tia-design/review-manifest.md).

Design acceptance preceded implementation refinement.

## Later product enhancement

After base optimizer proof, develop independent distribution and optional
AITM-Core runtime configuration as a separate enhancement.
[Proposed design](design/independent-deployment-enhancement.md) ·
[Proposed plan](plan/independent-deployment-enhancement.md).

## Accepted implementation plan

The [implementation plan](plan/test-impact-analysis-implementation-plan.md) was accepted at SHA-256
`ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7` and published at `dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84`.
[Manual SAR](plan/reviews/sar-2026-11-10-tia-plan/review-manifest.md) ·
[Independent Codex SPR](plan/reviews/spr-2026-11-10-tia-plan/review-manifest.md) ·
[Native Claude XPR](plan/reviews/xpr-2026-11-10-tia-plan/review-manifest.md).

#133 is the aggregate for 41 bounded Backlog leaves with 64
direct dependency edges. The [leaf catalog](plan/leaf-stories.md) gives
their verified issue numbers and estimates, totaling 146.5 implementation
agent-hours. The [readback receipt](plan/leaf-issue-receipt.json) binds
native links and Project identities to the exact plan.

The parent stops in Planning at plan acceptance. Child pickup and
operational activation have separate gates.
