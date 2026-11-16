---
schema: "aitm.story/v0"
id: 341
title: "[#133] Run the short check on every push and the full suite once"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/341"
parent: 133
children: []
blocking: []
blocked-by: [340]
created: "2026-11-16T06:43:16Z"
updated: "2026-11-16T06:43:16Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-pr-feedback-replacement.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#133] Run the short check on every push and the full suite once

[GitHub issue #341](https://github.com/kburson/aitm/issues/341) · [Parent #133](../../001/133/story.md) · [Replacement](../../001/133/plan/2026-11-16-133-pr-feedback-replacement.md)

Rank 190. 4 implementation agent-hours, M, P1. Requires [#340](../340/story.md).

Run the short mapped check on every push. Run the full suite once for the head under review. Run it again only when a later push changes the mapped selection or falls back to the full suite. Cancel a run whose head has been superseded.

#337 measured final successful full attempts at about 6 to 9 minutes. The median wait from first registration to the final signed result was 22m 01s because those pull requests took 2 to 5 attempts. This story removes the repeated full runs. A full suite of up to 20 minutes is acceptable for the one reviewed head and for trunk.

## Done when

- An amended pull request does not start a second full suite unless the amendment changes the mapped selection or requires fallback.
- A superseded run is cancelled.
