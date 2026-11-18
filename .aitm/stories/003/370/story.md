---
schema: "aitm.story/v0"
id: 370
title: "Run the TIA suite on Linux first"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/370"
parent: null
children: [371]
blocking: []
blocked-by: []
created: "2026-11-18T13:52:04Z"
updated: "2026-11-18T13:52:04Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Run the TIA suite on Linux first

[GitHub issue #370](https://github.com/kburson/aitm/issues/370) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 480. Priority P2. Size Feature.

Run the TIA tool on Linux first. Add macOS where a test needs Darwin or APFS. Leave Windows for a later epic.

The owner develops on macOS. The suite still has to run on Linux and on macOS. GitHub-hosted macOS runners are scarce, and the current product pytest lane requires one for every result.

This epic is independent of #133, #351, #356, and #362. It is not a child of #133. #351 still closes when #355 delivers the advisory command. #355 stays on that accepted command.

## Research, then development

1. #371 answers whether the Linux-first tool can stay in Python, whether a Node.js toolchain can select and run the existing pytest suite, and whether Python is a poor fit for this agentic suite.

A feature story is opened after that finding is accepted. The finding chooses the change. This epic does not start with a feature.

## Bound

The spike writes the finding. Production code, CI, the hosted path map, and #355 stay unchanged. Windows is named for a later epic and is not opened here.

Development does not start from this epic.
