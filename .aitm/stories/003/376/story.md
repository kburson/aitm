---
schema: "aitm.story/v0"
id: 376
title: "Run product tests on the Linux runner"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/376"
parent: 372
children: []
blocking: [377]
blocked-by: [373]
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

# Run product tests on the Linux runner

[GitHub issue #376](https://github.com/kburson/aitm/issues/376) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 520. Priority P2. Size S. Estimate 3 agent-hours.

`python-base` and `python` run on `ubuntu-24.04`. Delete the `diskutil`, `plutil`, and APFS assertions from `.github/workflows/ci.yml`. `capability.json` records `os` and `runtime`.

`tools/ci/python_gate.py` accepts a passing result without a Darwin APFS capability. `tools/ci/verify_pr.py` keeps the runner image string and Python 3.13.9. `tools/ci/tia/baseline.py` records the Linux run. `tools/ci/tia/suites.json` uses one portable runner. `tools/ci/tia/local.py` stops requiring Darwin, APFS, and native ACL. Git is resolved from `PATH` in `local.py` and `tools/ci/tia/snapshot.py`. `tools/ci/policy.json` drops the firmlink skip.

Start the `local.py` edit after [pull request #369](https://github.com/kburson/aitm/pull/369) merges. #355 keeps the accepted advisory command. That sequence is a note. #355 is not a blocker.

