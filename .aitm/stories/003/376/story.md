---
schema: "aitm.story/v0"
id: 376
title: "Run product tests on the Linux runner"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/376"
parent: 372
children: []
blocking: []
blocked-by: [377]
created: "2026-11-18T23:38:27Z"
updated: "2026-11-19T12:53:56Z"
last-branch: "codex/376-portable-launcher"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Run product tests on the Linux runner

[GitHub issue #376](https://github.com/kburson/aitm/issues/376) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 530. Priority P2. Size S. Estimate 3 agent-hours.

#377 has moved `python-base` and `python` to `ubuntu-24.04` and stopped the Darwin APFS pass/fail in the workflow, `python_gate.py`, and `verify_pr.py`. This story finishes the launcher and the suite policy on that Linux run.

`tools/ci/tia/baseline.py` records the Linux run. It records the Ubuntu image, `Linux`, and the filesystem the host reports. `tools/ci/tia/suites.json` uses one portable runner. Its capabilities are private mode bits, `O_NOFOLLOW`, and exclusive rename. `tools/ci/tia/local.py` stops requiring Darwin, APFS, and native ACL. Git is resolved from `PATH` in `local.py` and `tools/ci/tia/snapshot.py`. `tools/ci/policy.json` drops the firmlink skip.

Start the `local.py` edit after [pull request #369](https://github.com/kburson/aitm/pull/369) merges. #355 keeps the accepted advisory command. That sequence is a note. #355 is not a blocker.

`.github/workflows/ci.yml` stays as #377 left it.

