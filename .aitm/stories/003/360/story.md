---
schema: "aitm.story/v0"
id: 360
title: "Run a CI full sweep as category shards"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/360"
parent: 356
children: []
blocking: [361]
blocked-by: [359, 411]
created: "2026-11-16T19:41:49Z"
updated: "2026-11-20T21:28:00Z"
last-branch: "codex/360-hosted-runner-isolation"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-20-360-delivery-plan.md"], "attachments": []}
expansions: []
trips: []
---

# Run a CI full sweep as category shards

[GitHub issue #360](https://github.com/kburson/aitm/issues/360) · [Parent #356](../356/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 600. Priority P2. Size S.

Run a CI full sweep as the same category shards delivered locally by #359.

## Development

A full CI sweep starts those suites as parallel jobs. The ordinary pull-request path map stays the short check. This story adds no schedule, no merge hold, and no failure flag.

Stay blocked until #359 is accepted. The schedule is #361.

## Acceptance criteria

- Expose a manual full-sweep CI workflow. Run the #359 category plan in parallel jobs when compatible, with an explicit runner for each required capability and custody of receipts per run and attempt.
- Verify exact source, expected shard set, collected IDs and test and child outcomes before emitting the overall verdict. Demonstrate hosted success and incomplete or failing run behavior. Include separate queue, setup and execution durations.
- Keep the ordinary hosted PR path-map and merge controls in their existing roles. #361 owns the scheduled trigger.

[Delivery plan](plan/2026-11-20-360-delivery-plan.md).

[Hosted sweep candidate](https://github.com/kburson/aitm/pull/409).

## Trusted image build

[#411](../../004/411/story.md) blocks this story. The trusted receipt must accept any observed build of the runner label the workflow requested. That label is not fixed at Ubuntu 24.04. A canonical run of PR #410 waits until this rule has landed. Do not fold the rule change into PR #410.
