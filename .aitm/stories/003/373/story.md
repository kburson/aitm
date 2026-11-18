---
schema: "aitm.story/v0"
id: 373
title: "Prove private ledger custody without APFS"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/373"
parent: 372
children: []
blocking: [376, 377]
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

# Prove private ledger custody without APFS

[GitHub issue #373](https://github.com/kburson/aitm/issues/373) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 490. Priority P2. Size S. Estimate 3 agent-hours.

The writer guard and the project directory stay distinct physical directories. Identity is `(st_dev, st_ino)` from `ledger._path_id`. Two spellings of one inode are one directory. The proof is a same-inode fixture. A `/System/Volumes/Data` path is not part of the proof.

Cover `ledger._guard_path` and `backup._require_outside`. Add the portable fixture beside the current firmlink tests in `packages/aitm-usage/tests/test_ledger.py`. Those firmlink tests remain until #377.

This story does not change `.github/workflows/ci.yml`, `tools/ci/tia/local.py`, or the #355 advisory command.

