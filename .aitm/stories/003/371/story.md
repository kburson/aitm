---
schema: "aitm.story/v0"
id: 371
title: "[Spike] Find how TIA runs on Linux first"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/371"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-18T13:52:04Z"
updated: "2026-11-18T13:52:04Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Find how TIA runs on Linux first

[GitHub issue #371](https://github.com/kburson/aitm/issues/371) · [Parent #370](../370/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 490. Priority P2. Size S. Estimate 3 agent-hours.

Question: what is the smallest change that lets the TIA tool run on Linux first, with macOS added only where a test needs Darwin or APFS?

Answer these four points in one finding:

1. Separate the tests and CI steps that require Darwin or APFS from the tests and steps that run on macOS only because the current gate and suite policy require it. Name the files and jobs.
2. Can that Linux-first tool stay in Python? If a Python implementation cannot meet the boundary, name the concrete obstacle.
3. Can a Node.js toolchain select and invoke the existing pytest suite? Say what Node would own and what pytest would still own.
4. Is Python a poor choice for this agentic tool suite? Judge that from the current agent path, which is uv, pytest, the path map, and the local advisory command. Keep that judgment separate from the shortage of hosted macOS runners.

Name the question a later Windows epic would have to answer. Do not open that epic and do not design the Windows solution.

## Bound

This is research for #370. Write the finding. Do not change production code, CI workflows, the hosted path map, or the #355 advisory command. Do not port the tool to Node in this spike. Do not add a blocker edge.

## Starting material

- `.github/workflows/ci.yml`: `python-base` and `python` use `macos-26`. `quality` and `file-checks` use `ubuntu-24.04`.
- `tools/ci/python_gate.py` rejects a result unless the capability is Darwin and APFS.
- `tools/ci/tia/suites.json` marks `product-base`, `product-cli`, and `ci-helpers` as the `darwin-apfs` runner.
- `docs/ci.md` describes the full product suite on Darwin APFS runners.
- #355 records the hosted macOS queue failure. [Pull request #369](https://github.com/kburson/aitm/pull/369) attempt 2 waited 15 minutes for both macOS arm64 jobs, and GitHub cancelled them with no runner and zero steps.
- Node in this repository installs markdownlint for the file lane under `tools/ci/file-lint`. The product tests are pytest.
- The product already has Linux and Darwin surfaces in `aitm_usage`.

## Handoff

The accepted finding names the feature story that would implement the Linux-first boundary. That story is created after acceptance. #356 continues to classify tests by execution category. It does not choose the operating system.
