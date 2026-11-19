---
schema: "aitm.story/v0"
id: 372
title: "Run the required suite on Linux"
kind: "epic"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/372"
parent: null
children: [373, 374, 375, 376, 377]
blocking: []
blocked-by: []
created: "2026-11-18T23:38:27Z"
updated: "2026-11-19T03:29:44Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-18-372-delivery-checkpoint.md"], "attachments": []}
expansions: []
trips: []
---

# Run the required suite on Linux

[GitHub issue #372](https://github.com/kburson/aitm/issues/372) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 480. Priority P2. Size Feature.

The required test suite runs on Linux. The cloud workflow has no macOS job for that suite. The same Python program runs on a developer machine that has CPython 3.13 and git, including a Mac.

Remove the host requirements on APFS, `diskutil`, `chmod +a`, `launchctl`, and `libproc.dylib`. Keep private mode bits, `O_NOFOLLOW`, filesystem identity `(st_dev, st_ino)`, and one supervisor.

This epic is independent of #133, #351, #370, #356, and #362. It is not a child of #133. [#370](../370/story.md) is the TIA probe that follows this cleanup. The order is a note. There is no blocker edge between the epics.

#377 is the first story. GitHub is limiting macOS CI instances. Until the tests that require a Mac are gone, and the required Python jobs run on Linux, the later stories cannot pass CI.

#355 and [pull request #369](https://github.com/kburson/aitm/pull/369) stay on the accepted advisory command. The story that edits the local launcher starts after that pull request merges. That wait is written on the story. It is not a blocker edge.

## Stories

1. [#377 Remove tests that require a Mac](../377/story.md). First. It moves `python-base` and `python` to `ubuntu-24.04` and removes the tests that need a Mac, so the pull request can pass while GitHub limits macOS runners.
2. [#373 Prove private ledger custody without APFS](../373/story.md). Blocked by #377.
3. [#374 Supervise the service without launchctl](../374/story.md). Blocked by #377.
4. [#375 Refuse an extra file grant without a macOS ACL](../375/story.md). Blocked by #377.
5. [#376 Run product tests on the Linux runner](../376/story.md). Blocked by #377. The local launcher edit starts after pull request #369 merges. That wait is a note, not a blocker edge.

Codex develops the stories. Filing this epic does not change trunk.
