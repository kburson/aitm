---
schema: "aitm.story/v0"
id: 373
title: "Prove private ledger custody without APFS"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/373"
parent: 372
children: []
blocking: []
blocked-by: [377]
created: "2026-11-18T23:38:27Z"
updated: "2026-11-19T03:28:37Z"
last-branch: "codex/373-physical-custody"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Prove private ledger custody without APFS

[GitHub issue #373](https://github.com/kburson/aitm/issues/373) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 500. Priority P2. Size S. Estimate 3 agent-hours.

#377 has moved the required Python jobs to Linux and taken the Mac-only tests off the required path. This pull request runs on that suite.

The writer guard and the project directory stay distinct physical directories. Identity is `(st_dev, st_ino)` from `ledger._path_id`. Two spellings of one inode are one directory. The proof is a same-inode fixture. A `/System/Volumes/Data` path is not part of the proof.

Cover `ledger._guard_path` and `backup._require_outside`.

This story does not change `.github/workflows/ci.yml`, `tools/ci/tia/local.py`, or the #355 advisory command.

