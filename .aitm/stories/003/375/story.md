---
schema: "aitm.story/v0"
id: 375
title: "Refuse an extra file grant without a macOS ACL"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/375"
parent: 372
children: []
blocking: []
blocked-by: []
created: "2026-11-18T23:38:27Z"
updated: "2026-11-18T23:38:27Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Refuse an extra file grant without a macOS ACL

[GitHub issue #375](https://github.com/kburson/aitm/issues/375) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 510. Priority P2. Size S. Estimate 3 agent-hours.

A private file and its ancestors grant nothing beyond the mode bits already checked. A missing ACL is success. A present extra grant is a refusal. Drop the home-directory deny-delete allowance in `host_fs._check_mac_acl`. A host with no ACL read succeeds, because there is no extra grant to refuse.

The required suite does not run `chmod +a`. Deleting the `native-acl` capability from `tools/ci/tia/suites.json` belongs to #376.

