---
schema: "aitm.story/v0"
id: 370
title: "Select affected tests with one Python program"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/370"
parent: null
children: [371]
blocking: []
blocked-by: []
created: "2026-11-18T13:52:04Z"
updated: "2026-11-18T20:56:33Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Select affected tests with one Python program

[GitHub issue #370](https://github.com/kburson/aitm/issues/370) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 480. Priority P2. Size Feature.

Build the TIA selector once and run that same program anywhere a CPython interpreter is installed. Linux, macOS, and later Windows each supply that interpreter for the same source.

The owner develops on macOS. The program is still one program.

The job is the test list for a change. Compare the staging area, or HEAD, with the commit where the branch diverges from its parent branch. Follow the dependency chain among tests, imported functions, and libraries, and unwind that chain to the application.

#371 analyzes the Python language facility that makes one source program cross-platform, and names every current TIA binding that leaves that facility.

This epic is independent of #133, #351, #356, and #362. It is not a child of #133. #351 still closes when #355 delivers the advisory command. #355 stays on that accepted command.

## Research, then development

1. #371 writes the Python cross-platform analysis and the classification of the current selector.

A feature story is opened after that finding is accepted. The finding chooses the change. This epic does not start with a feature.

## Bound

The spike writes the finding. Production code, CI, the hosted path map, and #355 stay unchanged. Windows stays a later epic for operating-system facilities. That later epic runs this same program. It is not opened here.

Development does not start from this epic.
