---
schema: "aitm.story/v0"
id: 461
title: "[Spike] Validate agent-owned settlement and publication at story closeout"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/461"
parent: 456
children: []
blocking: []
blocked-by: [457]
created: "2026-11-26T00:04:56Z"
updated: "2026-11-26T00:07:17.678Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/457/attachments/qualification/457-desktop-forwarded-route.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Validate agent-owned settlement and publication at story closeout

[GitHub #461](https://github.com/kburson/aitm/issues/461)

Follow-up to #457 in Epic #456. Validate whether the chat agent can settle and publish its own and supervised turn receipts using the existing caller-owned helper and planning writer.

## Experiment

- Use a disposable Desktop chat and a bounded enrolled story. Capture the owner and one supervised subagent. Leave at least one callback pending until native retention is available. Switch the active story before settlement and reopen the store in a fresh process.
- Have the chat agent invoke the supported retry and publish commands as part of ordinary story closeout. Verify exact owner and subagent receipts land once on the original story on protected `planning`. Repeat the same batch and verify identical remote bytes with no duplicate registration.
- Exercise an unavailable or ambiguous publication result using the existing authorized writer and readback. Verify unresolved evidence stays visible and unassigned when the original binding cannot be proved.
- Record the exact operator steps, extra model turns, timing, review and cost, publication authority, and any required human intervention. Recommend the smallest viable closeout workflow. Keep collection session-owned and use existing project permissions.

[Composer and delayed recovery evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/004/457/attachments/qualification/457-desktop-forwarded-route.md)
