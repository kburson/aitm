---
schema: "aitm.story/v0"
id: 371
title: "[Spike] Analyze how one Python TIA program runs everywhere"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/371"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-18T13:52:04Z"
updated: "2026-11-19T14:08:03Z"
last-branch: "planning"
estimate: {"agent-hours": 3, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-19-371-portable-python-tia-findings.md", "plan/reviews/2026-11-19-371-independent-findings-review.md"], "attachments": ["plan/2026-11-19-371-probe-evidence.json"]}
expansions: []
trips: []
---

# [Spike] Analyze how one Python TIA program runs everywhere

[GitHub issue #371](https://github.com/kburson/aitm/issues/371) · [Parent #370](../370/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 550. Priority P2. Size S. Estimate 3 agent-hours.

Question: how does one Python TIA program run unchanged on every operating system that has a CPython interpreter?

Python is the cross-platform medium, in the same sense that Ruby source runs on a platform Ruby engine, JavaScript runs on a platform Node process, and Java bytecode runs on a platform JVM. The platform-specific piece is the interpreter. The TIA program is one body of source.

## Finding

Answer these four points in one finding:

1. Python's cross-platform medium. Describe the source program, the platform CPython interpreter, bytecode as a cache for one Python version, and a pure-Python wheel. Name the boundary where a call leaves that medium: an operating-system facility, a native extension, or a path that exists on only one operating system.
2. The selection job. The diff is the staging area, or HEAD, against the commit where the branch diverges from the parent branch. The dependency list is the chain among tests, imported functions, and libraries, unwound to the application. Show how that analysis reads source and therefore stays inside the portable medium.
3. The current tree. Classify `tools/ci/tia/python_graph.py`, `tools/ci/path_map.py`, `tools/ci/tia/local.py`, `tools/ci/tia/snapshot.py`, `tools/ci/python_gate.py`, and `tools/ci/tia/suites.json`. Distinguish source analysis, Git and host capability probes, and hosted evidence. Identify any remaining operating-system restrictions. The claim is one source program. Each operating system supplies its own CPython interpreter.
4. The conclusion. State whether the portable Python subset is sufficient for this selection job. If a current call cannot stay in that subset, name the call. Treat Node.js as a comparison for the interpreter model. A Node implementation is in scope only when this analysis names a gap that pure Python cannot close.

Name the question a later Windows epic would have to answer about Windows facilities. The same TIA program is the program that epic would run. Do not open that epic and do not design those facilities.

## Bound

This is research for #370. Write the finding. Do not change production code, CI workflows, the hosted path map, or the #355 advisory command. Do not add a blocker edge.

## Starting material

- `tools/ci/tia/python_graph.py` builds a file-level import graph with the Python `ast` module. It records dynamic imports, wildcards, parse failures, and pytest plugins as unresolved. It is not wired into pull-request selection.
- `tools/ci/path_map.py` is the delivered pull-request allowlist. It maps reviewed paths to test modules. It is not the import-chain unwind described above.
- `tools/ci/tia/local.py` probes private mode bits, no-follow and exclusive rename in scratch on Linux and Darwin. `tools/ci/tia/snapshot.py` resolves a Git binary from PATH with the required offline controls.
- `tools/ci/python_gate.py` consumes Ubuntu runner evidence and `tools/ci/tia/suites.json` declares the portable product and helper workloads. The required Python jobs in `.github/workflows/ci.yml` run on `ubuntu-24.04`.
- [#372 delivery](../372/retro/2026-11-19-372-delivery.md) and [#351 delivery](../351/retro/2026-11-19-351-delivery.md) are the current setup evidence. Analyze which operations leave Python source analysis for Git, filesystem or host-specific adapters.

## Owner direction

The owner accepted this direction on 2026-11-18. [Plan](../370/plan/2026-11-18-370-linux-suite-then-tia-probe.md).

Python stays the program. CPython is the platform interpreter. The required path now uses the portable custody checks and service supervisor delivered by #372. OS calls remain an explicit boundary. The read-only Darwin Grok adapter remains available for that platform. Ubuntu is the reference runner for the required suite, and macOS is a local portability cross-check.

The TIA probe starts after that cleanup. It lists the tests for the staging area, for `HEAD`, or for a pull request, each compared with the commit where the branch diverges from its parent. The verified local hosts are Linux and macOS with CPython 3.13.9 and Git with the required offline controls.

## Handoff

The feature story that wires the probe's list into the pull-request gate opens after the Linux suite is the required suite and the probe's list is accepted. #356 continues to classify tests by execution category. #355 continues the accepted advisory command. Production code stays unchanged until a feature story is picked up. Pull request #369 stays on its accepted scope.

## Accepted finding

Independent review passed on the exact current trunk. Linux and macOS produced the same dependency witnesses and fallback decision. [Finding](plan/2026-11-19-371-portable-python-tia-findings.md) · [Probe evidence](plan/2026-11-19-371-probe-evidence.json) · [Review](plan/reviews/2026-11-19-371-independent-findings-review.md) · [Follow-on #383](../383/story.md).
