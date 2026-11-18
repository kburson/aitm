---
schema: "aitm.story/v0"
id: 371
title: "[Spike] Analyze how one Python TIA program runs everywhere"
kind: "spike"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/371"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-18T13:52:04Z"
updated: "2026-11-18T23:20:01Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [Spike] Analyze how one Python TIA program runs everywhere

[GitHub issue #371](https://github.com/kburson/aitm/issues/371) · [Parent #370](../370/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 490. Priority P2. Size S. Estimate 3 agent-hours.

Question: how does one Python TIA program run unchanged on every operating system that has a CPython interpreter?

Python is the cross-platform medium, in the same sense that Ruby source runs on a platform Ruby engine, JavaScript runs on a platform Node process, and Java bytecode runs on a platform JVM. The platform-specific piece is the interpreter. The TIA program is one body of source.

## Finding

Answer these four points in one finding:

1. Python's cross-platform medium. Describe the source program, the platform CPython interpreter, bytecode as a cache for one Python version, and a pure-Python wheel. Name the boundary where a call leaves that medium: an operating-system facility, a native extension, or a path that exists on only one operating system.
2. The selection job. The diff is the staging area, or HEAD, against the commit where the branch diverges from the parent branch. The dependency list is the chain among tests, imported functions, and libraries, unwound to the application. Show how that analysis reads source and therefore stays inside the portable medium.
3. The current tree. Classify `tools/ci/tia/python_graph.py`, `tools/ci/path_map.py`, `tools/ci/tia/local.py`, `tools/ci/tia/snapshot.py`, `tools/ci/python_gate.py`, and `tools/ci/tia/suites.json`. Say which of these are already one portable program and which require Darwin, APFS, or a macOS runner. The claim is one source program. Each operating system supplies its own CPython interpreter.
4. The conclusion. State whether the portable Python subset is sufficient for this selection job. If a current call cannot stay in that subset, name the call. Treat Node.js as a comparison for the interpreter model. A Node implementation is in scope only when this analysis names a gap that pure Python cannot close.

Name the question a later Windows epic would have to answer about Windows facilities. The same TIA program is the program that epic would run. Do not open that epic and do not design those facilities.

## Bound

This is research for #370. Write the finding. Do not change production code, CI workflows, the hosted path map, or the #355 advisory command. Do not add a blocker edge.

## Starting material

- `tools/ci/tia/python_graph.py` builds a file-level import graph with the Python `ast` module. It records dynamic imports, wildcards, parse failures, and pytest plugins as unresolved. It is not wired into pull-request selection.
- `tools/ci/path_map.py` is the delivered pull-request allowlist. It maps reviewed paths to test modules. It is not the import-chain unwind described above.
- `tools/ci/tia/local.py` refuses to start unless `platform.system()` is Darwin and the filesystem is APFS.
- `tools/ci/tia/snapshot.py` uses `/usr/bin/git` when `sys.platform` is `darwin`.
- `tools/ci/python_gate.py` rejects a result unless the capability is Darwin and APFS. `tools/ci/tia/suites.json` marks the product and helper workloads as the `darwin-apfs` runner.
- `.github/workflows/ci.yml` runs the product pytest jobs on `macos-26`. Quality and file checks run on `ubuntu-24.04`.
- #355 records the hosted macOS queue failure on [pull request #369](https://github.com/kburson/aitm/pull/369). That shortage is a runner fact. It does not by itself decide the language of the selector.

## Owner direction

The owner accepted this direction on 2026-11-18. [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md).

Python stays the program. CPython is the platform interpreter. The calls that leave the portable medium are the Darwin host requirements: APFS, `diskutil`, `chmod +a`, `launchctl`, and `libproc.dylib`. Those requirements are deleted and replaced with POSIX identity, mode bits, and one supervisor. The required suite then runs on Linux. GitHub has no macOS job for that suite.

The TIA probe starts after that cleanup. It lists the tests for the staging area, for `HEAD`, or for a pull request, each compared with the commit where the branch diverges from its parent. The same program runs wherever CPython and git are installed.

## Handoff

The feature story that wires the probe's list into the pull-request gate opens after the Linux suite is the required suite and the probe's list is accepted. #356 continues to classify tests by execution category. #355 continues the accepted advisory command. Production code stays unchanged until a feature story is picked up. Pull request #369 stays on its accepted scope.
