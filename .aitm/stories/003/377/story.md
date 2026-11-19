---
schema: "aitm.story/v0"
id: 377
title: "Remove tests that require a Mac"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/377"
parent: 372
children: []
blocking: [373, 374, 375, 376]
blocked-by: []
created: "2026-11-18T23:38:27Z"
updated: "2026-11-19T03:16:35Z"
last-branch: "codex/377-ubuntu-python-ci"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-18-377-linux-ci-checkpoint.md"], "attachments": []}
expansions: []
trips: []
---

# Remove tests that require a Mac

[GitHub issue #377](https://github.com/kburson/aitm/issues/377) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 490. Priority P2. Size S. Estimate 3 agent-hours.

GitHub is limiting macOS runners. The required `python-base` and `python` jobs run on `macos-26`, so a pull request that still needs those jobs waits. This story is first. #373, #374, #375, and #376 wait on it.

`python-base` and `python` run on `ubuntu-24.04`. Delete the `diskutil`, `plutil`, APFS, and `xcodebuild` steps from those jobs. `capability.json` records `os` and the runtime. The cache suffix names the Ubuntu image and Python 3.13.9. The jobs use `sha256sum` and the Linux `gh` archive in place of `shasum` and `gh_2.97.0_macOS_arm64.zip`. `tools/ci/python_gate.py` accepts a passing result without a Darwin APFS capability. `tools/ci/verify_pr.py` keeps the runner image string and Python 3.13.9. The CI tests those two modules run in the `python` job follow the Linux result.

Delete `data_volume_alias` from the required ledger tests. Rewrite the `_darwin` watch tests in `packages/aitm-usage/tests/test_host_watch.py` onto the public watch events. Rewrite the `chmod +a` install test so it runs on Linux. `tools/ci/tests/test_tia_local.py` runs on Linux and stops asserting APFS, `diskutil`, or native ACL.

Adapter tests that pass `system="Darwin"` as data stay. They record a monitored desktop app and do not call `diskutil` or `launchctl`.

`tools/ci/tia/local.py` stays as it is. That file is in [pull request #369](https://github.com/kburson/aitm/pull/369). Suite policy, the baseline identity, PATH git, and the local launcher probe stay on #376.

After this story the required suite has no test that requires a Mac, and the required Python jobs run on Linux.

