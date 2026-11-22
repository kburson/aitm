---
schema: "aitm.story/v0"
id: 364
title: "[Spike] Find where a person and an agent can read one flag"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/364"
parent: 362
children: []
blocking: [365]
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-22T00:37:02Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-21-364-delivery-plan.md", "plan/2026-11-21-364-advisory-store-contract.md"], "attachments": ["attachments/2026-11-21-364-storage-examples.json"]}
expansions: []
trips: []
---

# [Spike] Find where a person and an agent can read one flag

[GitHub issue #364](https://github.com/kburson/aitm/issues/364) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 640. Priority P2. Size S.

Choose one durable location for the warning that a person can inspect and an agent can query. Evaluate a dedicated GitHub issue with one versioned record and a generated summary as the leading candidate.

## Acceptance

- Specify how the publisher binds the target, which permissions it needs, and how readers access it. Restrict publication to the one advisory record. Keep the publisher outside the sweep workflow and outside merge and workspace authority.
- Define exact fields for active and clear results, evidence link and UTC time, the persisted #363 ordering watermark, and the response when the record is uninitialized, unavailable or invalid. Keep the decision and watermark in one update.
- Deliver the research receipt via a PR to `planning` with independent Grok PR review on the current candidate before merge. #365 reconciles the storage and evidence contracts at JIT.

[Delivery plan](plan/2026-11-21-364-delivery-plan.md).

[Research receipt](plan/2026-11-21-364-advisory-store-contract.md) and [evidence](attachments/2026-11-21-364-storage-examples.json).

[Delivery sign-off](retro/2026-11-21-364-sign-off.md).
