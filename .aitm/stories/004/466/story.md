---
schema: "aitm.story/v0"
id: 466
title: "Qualify live session-owned Claude Code accounting on Linux"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/466"
parent: null
children: []
blocking: []
blocked-by: []
created: "2026-11-26T14:41:26Z"
updated: "2026-11-26T14:43:42.024Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/135/story.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Qualify live session-owned Claude Code accounting on Linux

## Outcome

Qualify the shipped session-owned accounting path for explicitly supervised ordinary Claude Code CLI turns on one supported Linux host. Carry forward the live Linux proof from #135. The portable package already passes Linux fixtures, and live Claude capture and recovery have been demonstrated on macOS.

## Acceptance

- Use the installed effort package and existing session-owned workflow on an authenticated, isolated Linux host. Record the exact Linux distro and architecture, Claude Code version, package revision, and exercised route.
- Capture a fresh ordinary turn and a resumed turn using native evidence. Verify the exact token counters and story attribution assigned at dispatch. Recover a completed turn in a fresh process after switching the active story and verify it keeps its original attribution.
- Publish sanitized receipts through the existing planning workflow. Verify remote readback and that identical replay adds no usage or duplicate receipts. Keep missing evidence explicit and raw provider data private.
- Record independently reviewed native evidence and update the supported-route matrix only for the Linux tuple actually proved. Keep test fixtures and live qualification distinct.

Scope is bounded to the supervised CLI route. Global monitoring, legacy monitor bridge and journal changes, folded Agent accounting, and production activation are outside this story.

[#445 release qualification](https://github.com/kburson/aitm/blob/planning/.aitm/stories/004/445/attachments/qualification-matrix.md) · [#457 delivery evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/004/457/attachments/qualification/457-delivery-report.md) · [Retired epic #301](https://github.com/kburson/aitm/issues/301)
