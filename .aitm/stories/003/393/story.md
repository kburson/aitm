---
schema: "aitm.story/v0"
id: 393
title: "Qualify one declared-input pytest suite in hosted Ubuntu shadow runs"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/393"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-19T16:05:11Z"
updated: "2026-11-19T18:37:47Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-19-370-suite-level-selection.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-19-393-grok-suite-matrix.md"], "attachments": []}
expansions: []
trips: []
---

# Qualify one declared-input pytest suite in hosted Ubuntu shadow runs

[GitHub issue #393](https://github.com/kburson/aitm/issues/393) · [Parent #370](../370/story.md) · [Suite-level plan](../370/plan/2026-11-19-370-suite-level-selection.md).

Qualify one existing pytest suite with declared inputs on GitHub-hosted Ubuntu. Use the Grok ingestion and replay tests in `packages/aitm-usage/tests/test_grok.py` as the first candidate. Its runner already exists. Audit the suite's fixtures, shared setup, imported helpers, and downstream consumers before claiming an input is bounded to that suite. Treat a source change used by other suites as shared unless the evidence establishes its reach.

## Acceptance

- Define the pytest target and its versioned input declarations. Trace the paths from changed inputs to the suite, including owned source and fixtures, shared fixtures and configuration, and any runtime or dependency input needed for safe selection. Use pytest to collect and report node IDs at execution time.
- Reuse #383's Git snapshot handling. For hosted comparisons bind the literal PR base, head, tested merge commit, and tested tree and verify ordered parents. Refuse mismatched or stale identity. For unknown inputs, overlapping suite ownership, shared setup, or unverified inventory, record a conservative full or unavailable decision with its reason.
- Declare the case expectations before running. Include a real bounded change that selects the existing suite, a controlled behavioral regression in that suite, and a shared or unknown change that requires full. Compare the suite outcomes and full outcomes on the same tested trees and comparable hosted Ubuntu runners. Record the current path-map decision, exact node outcomes, setup and selection time, execution time, total elapsed time, and a complete full baseline.
- Require zero missed failures or mismatched selected outcomes in the declared cases, and demonstrate a material total-time saving on a real bounded change. Publish the measured result under #370, including any failures to qualify. Keep the shadow isolated and advisory. Preserve the required workflow, path map, evaluator, verifier, branch rules, and #355 command.

[Completed experiment #385](https://github.com/kburson/aitm/issues/385) · [Git snapshot delivery #383](https://github.com/kburson/aitm/issues/383) · [Parent #370](https://github.com/kburson/aitm/issues/370)

## Hosted Grok suite result

[#393](../370/plan/2026-11-19-370-grok-suite-shadow-findings.md) qualified the declared replay test-body boundary. The bounded case passed 33 tests in 3.564 seconds including setup and selection. The matching full run passed 1,776 in 274.003 seconds. Shared inputs selected full. The required gate stays unchanged.
