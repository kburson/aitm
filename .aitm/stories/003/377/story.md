---
schema: "aitm.story/v0"
id: 377
title: "Remove tests that require a Mac"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/377"
parent: 372
children: []
blocking: []
blocked-by: [373, 376]
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

# Remove tests that require a Mac

[GitHub issue #377](https://github.com/kburson/aitm/issues/377) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 530. Priority P2. Size S. Estimate 3 agent-hours.

The same-inode fixture from #373 is the custody proof. Delete `data_volume_alias` from the required ledger tests. Rewrite the `_darwin` watch tests in `packages/aitm-usage/tests/test_host_watch.py` onto the public watch events. Rewrite the `chmod +a` install test onto the portable ACL fixture. `tools/ci/tests/test_tia_local.py` runs on Linux.

Adapter tests that pass `system="Darwin"` as data stay. They record a monitored desktop app and do not call `diskutil` or `launchctl`.

After this story the suite has no test that requires a Mac.

