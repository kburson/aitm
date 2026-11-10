---
schema: "aitm.story/v0"
id: 182
title: "[M07b] Scope command admission and legacy compatibility"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/182"
parent: 100
children: []
blocking: [118, 194]
blocked-by: [117]
created: "2026-11-10T20:23:14Z"
updated: "2026-11-10T21:31:09+00:00"
last-branch: "codex/aitm-182-scope-command-admission"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-10-182-scope-command-admission-plan.md", "plan/2026-11-10-182-m07c-launcher-split.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind":"accepted-parent-plan-split","story":100,"key":"M07b","path":".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md","source-leaf":117,"publication":"be326aa06bbf0180969ecadb8df74cf4a37a62c4","raw-sha256":"8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21","section-sha256":"f2e8d780402afd62b409a1259957ecb178afd4f29c33aa9725c21256d69b009d","split-sha256":"c6b848d06140e44849ea31ffd0579e7f170c076cf381888a3ae0b25dc23ff987"}
---

# [M07b] Scope command admission and legacy compatibility

[GitHub issue #182](https://github.com/kburson/aitm/issues/182) · [Parent Epic #100](../100/story.md) · [M07a #117](../117/story.md) · [Dependent #118](../118/story.md)

Implement the producer and legacy compatibility half of the accepted M07 requirement. The [reviewed split](../117/plan/2026-11-10-117-m07-split.md) records the inherited command, receipt, owner, and installed launcher constraints. #117 must close before this leaf can enter Develop. Obtain the applicable exact design, Refine estimate, plan and JIT within the four-hour implementation cap. Keep the scope command and installed invocation tests in the leaf's delivery evidence.

Both producer routes require the admitted monitor consumer before acknowledging a queue write. Preserve existing legacy grammar, exact UUID and receipts, and pre-adoption behavior. Cover the session memo adoption race, the mixed scope/control queue and the new verified native grammar. The [independent pickup](plan/2026-11-10-182-pickup-review-r2.md) approved moving both installed launcher variants to [M07c #194](../194/story.md). [Split receipt](plan/2026-11-10-182-m07c-split-receipt.json). M11 owns runtime retirement and M16 owns legacy adoption and cutover.
