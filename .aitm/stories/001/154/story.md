---
schema: "aitm.story/v0"
id: 154
title: "[#133 T17] Persist authority and merge intents"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/154"
parent: 133
children: []
blocking: [155, 164]
blocked-by: [153]
created: "2026-11-10T16:51:36Z"
updated: "2026-11-10T16:56:26Z"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 133, "key": "T17", "path": ".aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md", "publication": "dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84", "raw-sha256": "ec4ee32aa2f1770e903d80e9922b62b3e0a4a4bc79d5e71e9ca61a1179ce08d7", "section-sha256": "a8c790842f8a8853a738ceef84a98f04671bc79ac390aceb6642a1a9004dc033"}
---

# [#133 T17] Persist authority and merge intents

[GitHub issue #154](https://github.com/kburson/aitm/issues/154) · [Parent #133](../133/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/dbe0d68b3e7b977c9fbf51e26d9ae8c6f629af84/.aitm/stories/001/133/plan/test-impact-analysis-implementation-plan.md#L432)

**Required predecessors** [T16 #153](../153/story.md).

The planning estimate is 3.5 implementation agent-hours.
Recheck it at the leaf's own refinement and JIT. The parent plan
defines this leaf's boundaries. Its own applicable design, plan, JIT,
dependency proof, and implementation authority govern pickup.

## Accepted plan excerpt

### T17. Persist authority and merge intents — 3.5h, P1, T16

**Owns** `tools/ci/tia/authority_store.py`, `test_tia_authority_store.py`.
**Interface** `apply(expected_version, operation) -> Decision` and
`get_pending(repository) -> Intent | None`.

- [ ] `test_stale_version_and_crash_hold_pending_intent` races two
  writes and restarts between intent reservation and reconciliation.
- [ ] Use one protected SQLite store on the trusted host and durable
  compare-and-swap updates. Deduplicate authenticated event IDs.
  Persist pending host mutation and its exact authorization before
  dispatch, with no ordinary retry during uncertain state. Deliver
  T17 as a closed storage seam with fixture-only state transitions.
  The store exposes facts and intents, with no live Healthy or
  authority issuance. T18 adds continuity verification before any
  live admission. Missing, restored or inconsistent state stays held.
  V(authority_store) passes without discarding locks or evidence.
