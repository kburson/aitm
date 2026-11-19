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
updated: "2026-11-19T04:14:00Z"
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

`ServiceSupervisor` is the AITM service. `cli.py` and `qualification.py` use it. Start writes a pid file and a heartbeat, mode `0600`, and runs the service loop in a child process. Stop signals that child and waits until the pid file is gone. Status is the heartbeat age and the pid. The supervisor does not launch Grok. It does not call `/bin/launchctl` and it does not load `/usr/lib/libproc.dylib`.

A scope hook from a Grok session the person started is still accepted. `sources/grok_scope_hook.py` walks the parent chain of its own process, at most 8 hops, and matches the qualified Grok pid, start time, and executable. The supervisor's pid file is the service record. It is not that Grok process.

On Linux the walk reads the parent, start time, and executable from `/proc/<pid>`. On Darwin the walk reads them with `proc_pidinfo` and `proc_pidpath`. A hop that cannot be read rejects the hook. The Linux walk does not load `libproc`. The required suite runs the Linux walk.

