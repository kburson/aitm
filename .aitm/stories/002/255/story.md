---
schema: "aitm.story/v0"
id: 255
title: "[M6 V08] Add a read-only Discuss handoff"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/255"
parent: 247
children: []
blocking: [256]
blocked-by: [251]
created: "2026-11-12T00:32:59Z"
updated: "2026-11-12T00:35:22Z"
last-branch: "planning"
estimate: {"agent-hours": 2.5, "size": null, "scope": "proposed implementation estimate"}
priority: null
origin: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M6 V08] Add a read-only Discuss handoff

[GitHub issue #255](https://github.com/kburson/aitm/issues/255) · [M6 #247](../247/story.md) · [Decomposition section](../247/plan/2026-11-11-247-m6-viewer-decomposition.md#v08-255)

Proposed implementation estimate **2.5 agent-hours**. Internal predecessors: #251.

Supported released Discuss CLI or owning harness context handoff contract at JIT.

## Acceptance criteria

- [ ] Offer a copyable supported Discuss handoff for an admitted story and applicable historical context. Preserve the exact story scope and fail clearly when unsupported.
- [ ] The viewer generates an authorized command or link through the supported contract. It does not start a conversation, execute a shell or send story context on click.
- [ ] Test unavailable provider or story, safe argument handling, privacy and keyboard access.

Require an independently reviewed and accepted item-specific JIT implementation plan at pickup. Recheck source, prerequisites, scope, file ownership and estimate then.
