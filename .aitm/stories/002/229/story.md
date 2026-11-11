---
schema: "aitm.story/v0"
id: 229
title: "[Core] Qualify native story and epic Actual"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/229"
parent: 2
children: []
blocking: []
blocked-by: [23, 28, 34, 36, 72]
created: "2026-11-11T14:37:28Z"
updated: "2026-11-11T14:41:24Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "S", "scope": "preliminary transfer estimate"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
scope-transfer: {"story": 181, "key": "C03", "publication": "20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b", "path": ".aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md"}
---

# [Core] Qualify native story and epic Actual

[GitHub issue #229](https://github.com/kburson/aitm/issues/229) · [Owner epic #2](https://github.com/kburson/aitm/issues/2)

## Scope

This carries forward C03 from the owner-approved #181 scope transfer to #2. The 3.75 h estimate is preliminary and subject to refinement and JIT. #181's local delivery closes independently.

## Acceptance criteria

- [ ] Qualify direct and inclusive Actual from scoped native agent turns, including tool execution within the turn once. Deduplicate overlapping observations of one actor, sum parallel actors, and report elapsed, working wall time, owner wait and coverage separately. Exclude idle and unattended execution from Actual.
- [ ] Exercise draft and story scope switches, phase/attempt attribution, review handoffs, owner requests and responses, partial telemetry, parallel agents and direct epic work. Keep all-phase timing independent of the implementation clock. Use applicable provider/host timing proof.
- [ ] Reproduce the #227 fixtures and a pinned native report with a fresh reader. Qualify each claimed host and keep unsupported evidence Partial or Unknown. Schedule after Core release.

## Evidence and prerequisites

- [Reviewed Slice C section](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c03-qualify-native-actual) and [completed C01 evidence](https://github.com/kburson/aitm/blob/c794b1b0be8b7bb67ba7bb1d530fe8a80296f95b/.aitm/stories/002/227/attachments/qualification.md).
- Runtime prerequisites #23, #28, #34, #36, #72. Preserve the release, scope and authority gates in the reviewed section.
