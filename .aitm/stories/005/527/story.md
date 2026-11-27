---
schema: "aitm.story/v0"
id: 527
title: "[Core] Add hosted Core PR validation prerequisite"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/527"
parent: null
children: []
blocking: [3]
blocked-by: []
created: "2026-11-27T07:45:30Z"
updated: "2026-11-27T07:47:06Z"
last-branch: "codex/core-527-hosted-ci"
estimate: {"agent-hours": 2, "size": "XS"}
priority: "P1"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-27-hosted-ci.md"], "attachments": []}
expansions: []
trips: []
---

# Hosted Core PR validation prerequisite

The owner authorized a separately delivered Core CI workflow for #470. See the [bounded delivery plan](plan/2026-11-27-hosted-ci.md) and [draft PR #528](https://github.com/kburson/aitm/pull/528).

[PR #528](https://github.com/kburson/aitm/pull/528) passed hosted repository CI and [Grok 4.7 source SAR](plan/2026-11-27-pr-528-grok-sar.md). Its merge `34fd11588a1fecf3d04f16a311f1be9bd2f33c3b` is on the #470 integration branch. Closure is held for the first passing Core job on refreshed draft [PR #526](https://github.com/kburson/aitm/pull/526).
