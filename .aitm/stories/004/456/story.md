---
schema: "aitm.story/v0"
id: 456
title: "[Epic] Session-owned agent activity and cost reporting"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/456"
parent: null
children: [457, 458, 459, 461]
blocking: [100]
blocked-by: []
created: "2026-11-25T16:06:13Z"
updated: "2026-11-26T00:07:17.678Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/004/455/attachments/455-findings.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Epic] Session-owned agent activity and cost reporting

[GitHub #456](https://github.com/kburson/aitm/issues/456)

Implement the delivery recommendation approved after [Spike #455](https://github.com/kburson/aitm/issues/455). The agent in a live chat owns recording its own turns and the turns it supervises. Publish sanitized, attributable evidence to each story on `planning`.

## Delivery

1. Capture and publish exact per-turn receipts from explicitly supervised sessions.
2. Build pinned story effort and cost reports with visible coverage and pricing provenance.
3. Provide a deterministic planning producer for the Core Cost receiver fixture. Live receiver qualification stays in #230 and retains #51.

Use the shipped #435 portable assets and the narrow validated #100 components. Native provider scope follows advertised, verified routes. The epic excludes always-on global discovery, host-service adoption and rollback. [Research findings](https://github.com/kburson/aitm/blob/f39eb4d681c86f3c9a747d606e95d969e900b43b/.aitm/stories/004/455/attachments/455-findings.md) · [Child assessment](https://github.com/kburson/aitm/blob/f39eb4d681c86f3c9a747d606e95d969e900b43b/.aitm/stories/004/455/attachments/100-child-assessment.md)

## Kickoff

First delivery story [#457](../457/story.md) has started design. Its story holds the engagement and cost records.

[Spike #461](https://github.com/kburson/aitm/issues/461) validates agent-owned settlement and publication at story closeout after #457.
