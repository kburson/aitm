---
schema: "aitm.story/v0"
id: 228
title: "[Core] Qualify legacy dashboard timing replay"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/228"
parent: 2
children: []
blocking: []
blocked-by: [23, 53, 54, 55, 56, 72]
created: "2026-11-11T14:37:22Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "S", "scope": "post-release qualification"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
scope-transfer: {"story": 181, "key": "C02", "publication": "20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b", "path": ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":2,"design_sources":[2],"scope_entry":"#228","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json","slice_c_entry":"C02"}
---

# [Core] Qualify legacy dashboard timing replay

[GitHub issue #228](https://github.com/kburson/aitm/issues/228) · [Owner epic #2](https://github.com/kburson/aitm/issues/2)

## Current refinement

**Refine**, **Rank 10 within #2**, size **S**, estimate **3.75 agent-hours**. Qualify legacy dashboard timing replay against the released Core and pinned #181/#111 inputs. The existing 3.75 h transfer estimate covers evidence setup, scoped replay and failure cases, and verification of the result. The required release qualification in #72 remains an implementation prerequisite. [Sizing basis](../../000/2/2026-11-26-coordination-and-follow-up-refinement.md).

## Scope

This carries forward C02 from the owner-approved #181 scope transfer to #2. The 3.75 h estimate is preliminary and subject to refinement and JIT. #181's local delivery closes independently.

## Acceptance criteria

- [ ] Replay the frozen #181 and #111 timing evidence through the supported Core adoption and pinned reader on a disposable clone. Preserve stable identity, source digests, scoped qualified intervals, historical totals and Partial or Unknown coverage. Timing can qualify with usage absent.
- [ ] Exercise identical replay, proven splits, reattribution and interrupted publication. Hold conflicts and incomplete publication. Verify fresh-clone/index equality and preserve previous published views.
- [ ] Production adoption requires the applicable released Core and an authorized cutover. This follow-up consumes the existing adoption contracts and is scheduled after Core release.

## Evidence and prerequisites

- [Reviewed Slice C section](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c02-adopt-legacy-receipts-through-core) and [completed C01 evidence](https://github.com/kburson/aitm/blob/c794b1b0be8b7bb67ba7bb1d530fe8a80296f95b/.aitm/stories/002/227/attachments/qualification.md).
- Runtime prerequisites #23, #53, #54, #55, #56, #72. Preserve the release, scope and authority gates in the reviewed section.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **10** · **P1/S** · **3.75 agent-hours**. Design accepted for this manual workflow through issue #2 with scope entry **#228**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md). Admission to Planning waits for #72 and the remaining upstream prerequisites.
