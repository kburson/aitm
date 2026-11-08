---
kind: draft
slug: rubric
title: aitm-rubric — planning and estimation rubric with ML
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: rubric
package: aitm-rubric
depends-on: [aitm-core]
---

# Draft: aitm-rubric

## Known

- Separately installable plugin. Learns how to design, plan and estimate from every story committed to history.
- Estimates agent engagement only; leaf stories ≤ 4 h.
- Training signal: defects after acceptance, expansions, trips (with scrap/refactor decision and its outcome), discovered work, loop-backs, engaged time, tokens/cost, human pivots (recorded separately so planning isn't blamed for direction changes).
- Reuse ai-task-manager #1821: per-story Refine/Plan/Close records, rebuildable index, only complete triads calibrate, amendments append rather than rewrite.
- Start with comparable-story retrieval (kNN over compact feature vectors) plus quantile regression (scikit-learn); lessons are retrieved into the planner's context packet.
- Feeds Refine and Plan exit guards (estimate present, leaf ≤ 4 h).

## Open

- Feature set and units.
- Minimum corpus before numeric calibration is trusted.
