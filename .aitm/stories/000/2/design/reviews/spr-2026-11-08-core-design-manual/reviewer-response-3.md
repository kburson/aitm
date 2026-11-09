---
schema: aitm.review-response/v0
level: spr
story: 2
role: reviewer
round: 3
artifact_path: .aitm/stories/000/2/design/core-design.md
artifact_base_commit: 73210b6da93942f06a0d6616cf5df02eaf64180c
artifact_digest: sha256:f791fdf08eab8495f2031d0033729ec884a8810217783f5e971b9bbdf2efaac1
agent:
  host: codex
  provider: openai
  model_id: gpt-6.1-sol
  effort: high
reviewer_session: 01a1bebb-3dd5-7422-8d7e-58de85638746
started_at: "2026-11-09T05:35:41Z"
submitted_at: "2026-11-09T05:36:38Z"
start_basis: recorded
finding_ids: []
answered_finding_ids: []
---

## Summary

I read the complete revised FUR and checked all four dispositions in the second author response. The changes are consistent with the prior fixes, the accepted architecture, and the recorded owner decisions. They give M1 a defined execution order, reconstructible clock boundaries, a recovery path for a real missing test, and a repair rule that preserves valid published work. The acceptance cases specify future executable proof for those scenarios.

## Findings

No new required findings. The round-two findings resolve as follows.

- **R2-F001 resolved.** The managed-start and delivery rules use one authority boundary per installation. A shared store requires published admission even for a local authoritative test, while a local-only store uses durable local CAS. A stale offline clone can retain preparation without starting authoritative work. The separate core-run delivery fixture uses an eligible local target and publication not applicable.
- **R2-F002 resolved.** The event inventory and fold contract explicitly record reservation/resolution, review activation/invalidation, clock modes, and execution phases. The owning CAS retains each causal boundary, so a full rebuild distinguishes a reservation that never produced a child and a review retained before it became effective. The enclosing commit supplies the admission version without a self-referential digest.
- **R2-F003 resolved.** Evidence-only reopening preserves the historical attempt and fences its ended generation. A new exact-source evidence binding can obtain an authoritative test admission and run the missing verification. The new clock segment excludes terminal waiting, retains prior usage and allowance, and stops at actual effective review activation. Recovery of derived proof alone can preserve an already applicable stop. The path excludes superseded attempts and fresh implementation.
- **R2-F004 resolved.** The repair validator derives the maximal valid prefix of the exact quarantined chain independently of the repairing clone's cache. In the P → V → B case it restores V, rejects P, and retains the invalid tail for explicit reconciliation. A fresh validator can reproduce the result.

The design preserves the existing open expansion-completion interpretation, second-trip cap, review-depth policy and hosted audit mechanism. This SPR accepts the pinned design version within its scope.

## Required changes

None.

## Optional suggestions

None.

## Decision

accepted
