---
schema: "aitm.story/v0"
id: 398
title: "Qualify suite selection for a bounded production change on hosted Ubuntu"
kind: "story"
state: "planning"
issue: "https://github.com/kburson/aitm/issues/398"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-19T21:12:18Z"
updated: "2026-11-19T21:48:42Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-19-370-suite-level-selection.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-19-398-production-boundary-refine.md", "plan/2026-11-19-398-independent-refinement.md"], "attachments": []}
expansions: []
trips: []
---

# Qualify suite selection for a bounded production change on hosted Ubuntu

[GitHub issue #398](https://github.com/kburson/aitm/issues/398) · [Parent #370](../370/story.md) · [Suite-level plan](../370/plan/2026-11-19-370-suite-level-selection.md).

Qualify suite-level selection for one real, bounded production-code change on hosted Ubuntu. Build on [#393's Grok ingestion and replay qualification](https://github.com/kburson/aitm/issues/393) and reuse [#383's exact Git snapshot resolver](https://github.com/kburson/aitm/issues/383). Use the existing Grok replay pytest suite first. Audit the private headless token decoder in `packages/aitm-usage/src/aitm_usage/sources/grok.py` as a candidate. Its containing adapter is shared, so qualification depends on establishing the specific changed behavior's reach. If the proposed input cannot be bounded, record the fallback and choose another demonstrably bounded production input.

## Acceptance

- Declare the runnable pytest target, the versioned production-input boundary, and the expected cases before execution. Trace the production path through its callers, callback or argument flow, fixtures, and downstream consumers, including any subprocess use. Explain what binds the change to the target suite and how shared or ambiguous consumers cause a full assignment.
- Bind each case to the literal PR base, head, GitHub-tested merge commit and tree, verify ordered parents, and recheck the exact snapshots. Exercise a positive production-code edit, a seeded behavior regression in the same boundary, and a related shared or out-of-boundary edit that falls back to full. Invalid or drifted identity and incomplete test evidence must hold the result.
- Compare the declared suite assignment, current path-map decision, and full-suite outcomes on the same tested tree and comparable hosted Ubuntu runner for each case. Retain exact pytest IDs, per-test outcomes, setup, selection and execution times, and total measured lane time. Demonstrate a useful total-time saving on the positive production change and zero missed failures or mismatched selected outcomes in the declared cases.
- Record the evidence and disposition under [#370](https://github.com/kburson/aitm/issues/370). Keep the experiment advisory and isolated. Preserve the required workflow, path map, evaluator, verifier, branch rules, and pinned #355 command.

[#393 qualification and scope](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/370/plan/2026-11-19-370-grok-suite-shadow-findings.md)
