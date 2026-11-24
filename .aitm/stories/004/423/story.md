---
schema: "aitm.story/v0"
id: 423
title: "[Spike] Validate TIA selection against full-suite runs"
kind: "spike"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/423"
parent: null
children: []
blocking: []
blocked-by: [422]
created: "2026-11-23T00:30:38Z"
updated: "2026-11-24T13:31:10Z"
last-branch: "codex/423-tia-validation"
estimate: {"agent-hours": 3.5, "size": "L"}
priority: "P2"
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/refinement.md", "plan/experiment.md", "plan/reviews/grok-round-1.md", "plan/reviews/grok-round-2.md"], "attachments": []}
expansions: []
trips: []
---

# [Spike] Validate TIA selection against full-suite runs

[GitHub issue #423](https://github.com/kburson/aitm/issues/423)

## Question

How reliably does Test Impact Analysis identify and run the smallest defensible set of tests for representative changes, and what time does it save?

Use #422 as the timing and coverage baseline. Exercise the suite-level selector and the hosted advisory path independently from the current required PR path map.

## Evidence to deliver

- Use matched candidates for a leaf module, transitive import, shared fixture/config, docs only, test add/rename/delete, and an unresolved or dynamic dependency. Record the independently expected affected suites and any justified full-fallback cases before observing results.
- For each candidate, compare TIA's reason, predicted suites and exact executed test IDs with an independently run full-suite oracle for that same candidate. Include reversible seeded behavioral regressions to test whether selected runs catch failures. Verify the seed appears in the oracle before counting it.
- Report missed failing node IDs, outcome mismatches on overlapping tests, excess suites and node IDs relative to the predeclared oracle, safe fallbacks, selection and execution wall time, and the fraction of the full inventory executed. Record source, host, commands, run IDs and artifacts. An ambiguous or flaky oracle is inconclusive.
- State the selectors, scenarios and runtime behavior covered by the evidence. Keep policy and the required PR gate outside the experiment.

Use the exact delivered #422 tree as the baseline. The original draft #424 was merged for #422. Leave the replacement experiment draft unmerged.

Experiment workspace: [draft PR #425](https://github.com/kburson/aitm/pull/425).
