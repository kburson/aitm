---
schema: "aitm.story/v0"
id: 370
title: "Select affected tests with one Python program"
kind: "epic"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/370"
parent: null
children: [371, 383, 385]
blocking: []
blocked-by: []
created: "2026-11-18T13:52:04Z"
updated: "2026-11-19T15:51:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "Feature"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-18-370-linux-suite-then-tia-probe.md", "plan/2026-11-19-370-hosted-integration-decision.md", "plan/2026-11-19-370-hosted-shadow-findings.md", "plan/2026-11-19-370-hosted-shadow-evidence.json"], "attachments": []}
expansions: []
trips: []
---

# Select affected tests with one Python program

[GitHub issue #370](https://github.com/kburson/aitm/issues/370) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 540. Priority P2. Size Feature.

Build the TIA selector once and run that same program anywhere a CPython interpreter is installed. Linux, macOS, and later Windows each supply that interpreter for the same source.

The owner develops on macOS. The program is still one program.

The job is the test list for a change. Compare the staging area, or HEAD, with the commit where the branch diverges from its parent branch. Follow the dependency chain among tests, imported functions, and libraries, and unwind that chain to the application.

#371 analyzes the Python language facility that makes one source program cross-platform, and names every current TIA binding that leaves that facility.

The Linux suite cleanup is [#372](../372/story.md). It comes before this probe. The order is a note. There is no blocker edge.

Inside that cleanup, [#377](../377/story.md) is first. It removes the tests that require a Mac and moves the required Python jobs to Linux. #373, #374, #375, and #376 wait on #377. GitHub is limiting macOS CI instances, so those later stories cannot pass CI until #377 lands.

The owner accepted the order on 2026-11-18. First remove the macOS host requirements so every required test runs on Linux in the cloud. Then this epic's probe builds the test list for a staging area, a commit, or a pull request. [Accepted plan](plan/2026-11-18-370-linux-suite-then-tia-probe.md).

This epic is independent of #133, #351, #356, and #362. It is not a child of #133. #351 still closes when #355 delivers the advisory command. #355 stays on that accepted command.

## Research, then development

1. #371 writes the Python cross-platform analysis and the classification of the current selector.

A feature story is opened after that finding is accepted. The finding chooses the change. This epic does not start with a feature.

## Bound

The spike writes the finding. Production code, CI, the hosted path map, and #355 stay unchanged. Windows stays a later epic for operating-system facilities. That later epic runs this same program. It is not opened here.

Development does not start from this epic.

## Implementation handoff

The accepted [#371 finding](../371/plan/2026-11-19-371-portable-python-tia-findings.md) opens [#383](../383/story.md) for the advisory index, HEAD and PR probe. Hosted gate integration follows separate qualification.

## Hosted integration decision

The portable advisory probe shipped in [#383](../383/story.md). The [decision](plan/2026-11-19-370-hosted-integration-decision.md) holds promotion to the required gate and advances [#385](../385/story.md) for hosted Ubuntu shadow qualification. That story compares the graph assignment with exact full-suite outcomes and the current path map on the same PR trees. #370 remains open.

## Hosted shadow result

The [qualification findings](plan/2026-11-19-370-hosted-shadow-findings.md) record all seven hosted cases. The decision is to hold promotion. Real input assignments were full or unavailable, and fixture narrowing preserved the seeded failure outcomes. #385 remains in Test.
