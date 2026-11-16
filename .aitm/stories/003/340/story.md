---
schema: "aitm.story/v0"
id: 340
title: "[#133] Make a coarse path map the required PR check"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/340"
parent: 133
children: []
blocking: [341]
blocked-by: []
created: "2026-11-16T06:43:16Z"
updated: "2026-11-16T08:40:42Z"
last-branch: "story/340-341-path-map"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-pr-feedback-replacement.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/delivery-checklist.md", "plan/reviews/2026-11-16-head-fcd1d745.md", "plan/reviews/2026-11-16-head-a80b4420.md", "retro/2026-11-16-delivery.md"], "attachments": []}
expansions: []
trips: []
---

# [#133] Make a coarse path map the required PR check

[GitHub issue #340](https://github.com/kburson/aitm/issues/340) · [Parent #133](../../001/133/story.md) · [Replacement](../../001/133/plan/2026-11-16-133-pr-feedback-replacement.md)

Rank 180. 4 implementation agent-hours, M, P1. No predecessor.

Make a maintained path-to-test map the required check for an ordinary pull request. The trusted workflow reads the changed paths and chooses the tests. The candidate process does not. A mapped source or fixture change runs the mapped tests. A change to the map, a workflow, shared test setup, or an unmapped executable path runs the full suite.

#339 showed the stock selector refusing 250 unclassified tests. A pinned fixture-to-module run then caught the same failure locally in 1m 26s. This story ships that explicit map as the live pull-request check. It does not build a proof-grade selector, a scheduled backstop, or a merge hold.

The full suite remains the trunk backstop and the fallback. It may take up to 20 minutes. The existing three pytest-xdist workers stay on that full suite.

## Done when

- An ordinary mapped change is required to pass the mapped tests.
- An unmapped or control change is required to pass the full suite.
- Both results are the live pull-request check.
