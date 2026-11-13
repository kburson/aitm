---
schema: "aitm.story/v0"
id: 268
title: "[#146 Spike] Qualify a synthetic macOS/APFS observation boundary"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/268"
parent: 146
children: []
blocking: []
blocked-by: []
created: "2026-11-13T01:59:41Z"
updated: "2026-11-13T02:03:00Z"
last-branch: "codex/spike-268-macos-observation"
estimate: {"agent-hours": 3.5, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/146/plan/2026-11-12-146-trusted-observation-replan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [#146 Spike] Qualify a synthetic macOS/APFS observation boundary

Parent #146. Rank 50. Timebox 3.5 implementation agent-hours. Owner authorized one same-repository macos-26 job on a disposable branch with an allowlisted synthetic fixture.

Verify APFS on the test volume, distinct controller and unprivileged worker identities, and protected receipt custody before running the fixture. Verify an external catalog and outcome checks, both full and selected assignments, and explicit refusal when evidence is missing or untrusted. Publish the exact run evidence and obtain independent review. The fixture scope and limits are part of the result.

The existing #103 gate remains in effect. #146 remains open pending its own qualification disposition. #148 and #267 remain on hold.

[Reviewed #146 plan](https://github.com/kburson/aitm/blob/10992dc57915f84adafcb5ffb90f1ab04c70c856/.aitm/stories/001/146/plan/2026-11-12-146-trusted-observation-replan.md)
