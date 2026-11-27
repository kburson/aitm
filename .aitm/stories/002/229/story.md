---
schema: "aitm.story/v0"
id: 229
title: "[Core] Qualify native story and epic Actual"
kind: "story"
state: ready-for-plan
issue: "https://github.com/kburson/aitm/issues/229"
parent: 2
children: []
blocking: [523]
blocked-by: [23, 28, 34, 36, 72]
created: "2026-11-11T14:37:28Z"
updated: "2026-11-27T06:32:11.294Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "S", "scope": "post-release qualification"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
scope-transfer: {"story": 181, "key": "C03", "publication": "20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b", "path": ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"}
design-acceptance: {"mode":"owner-directed-manual-inheritance","parent":2,"design_sources":[2],"scope_entry":"#229","evidence":".aitm/stories/000/2/plan/2026-11-27-core-kickoff/refinement-readback.json","slice_c_entry":"C03"}
---

# [Core] Qualify native story and epic Actual

[GitHub issue #229](https://github.com/kburson/aitm/issues/229) · [Owner epic #2](https://github.com/kburson/aitm/issues/2)

## Current refinement

**Refine**, **Rank 20 within #2**, size **S**, estimate **3.75 agent-hours**. Qualify native story and epic Actual against the released Core and pinned #227/native inputs. The existing 3.75 h transfer estimate covers fixture setup, scoped attribution and coverage checks, and verification of the report. The required release qualification in #72 remains an implementation prerequisite. [Sizing basis](../../000/2/2026-11-26-coordination-and-follow-up-refinement.md).

## Scope

This carries forward C03 from the owner-approved #181 scope transfer to #2. The 3.75 h estimate is preliminary and subject to refinement and JIT. #181's local delivery closes independently.

## Acceptance criteria

- [ ] Qualify direct and inclusive Actual from scoped native agent turns, including tool execution within the turn once. Deduplicate overlapping observations of one actor, sum parallel actors, and report elapsed, working wall time, owner wait and coverage separately. Exclude idle and unattended execution from Actual.
- [ ] Exercise draft and story scope switches, phase/attempt attribution, review handoffs, owner requests and responses, partial telemetry, parallel agents and direct epic work. Keep all-phase timing independent of the implementation clock. Use applicable provider/host timing proof.
- [ ] Reproduce the #227 fixtures and a pinned native report with a fresh reader. Qualify each claimed host and keep unsupported evidence Partial or Unknown. Schedule after Core release.

## Evidence and prerequisites

- [Reviewed Slice C section](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c03-qualify-native-actual) and [completed C01 evidence](https://github.com/kburson/aitm/blob/c794b1b0be8b7bb67ba7bb1d530fe8a80296f95b/.aitm/stories/002/227/attachments/qualification.md).
- Runtime prerequisites #23, #28, #34, #36, #72. Preserve the release, scope and authority gates in the reviewed section.

## Core kickoff — 2026-11-27

**Ready for Planning** · rank **20** · **P1/S** · **3.75 agent-hours**. Design accepted for this manual workflow through issue #2 with scope entry **#229**. [Reviewed kickoff and pinned evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/000/2/plan/2026-11-27-core-kickoff/kickoff.md). Admission to Planning waits for #72 and the remaining upstream prerequisites.
