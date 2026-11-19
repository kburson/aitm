---
schema: "aitm.story/v0"
id: 374
title: "Supervise the service without launchctl"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/374"
parent: 372
children: []
blocking: []
blocked-by: [377]
created: "2026-11-18T23:38:27Z"
updated: "2026-11-19T01:20:00Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-18-370-linux-suite-then-tia-probe.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Supervise the service without launchctl

[GitHub issue #374](https://github.com/kburson/aitm/issues/374) · [Parent #372](../372/story.md) · [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md)

Project 24 Rank 510. Priority P2. Size S. Estimate 3 agent-hours.

#377 has moved the required Python jobs to Linux and removed the tests that require a Mac. This pull request runs on that suite.

Introduce `ServiceSupervisor` and point `cli.py` and `qualification.py` at it. Start writes a pid file and a heartbeat, mode `0600`, and runs the service loop in a child process. Stop signals that child and waits until the pid file is gone. Status is the heartbeat age and the pid.

`sources/grok_scope_hook.py` and the old process-identity helper call one function: the supervisor's recorded start time and executable path. On Linux the function may confirm the pid against `/proc/<pid>`.

The class does not call `/bin/launchctl` and does not load `/usr/lib/libproc.dylib`.

