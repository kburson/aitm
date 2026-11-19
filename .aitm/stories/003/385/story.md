---
schema: "aitm.story/v0"
id: 385
title: "Qualify the affected-test probe in hosted Ubuntu shadow runs"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/385"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-19T15:29:19Z"
updated: "2026-11-19T15:40:50Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-19-370-hosted-integration-decision.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-19-385-shadow-matrix.md"], "attachments": []}
expansions: []
trips: []
---

# Qualify the affected-test probe in hosted Ubuntu shadow runs

[GitHub issue #385](https://github.com/kburson/aitm/issues/385) · [Parent #370](../370/story.md) · [Hosted decision](../370/plan/2026-11-19-370-hosted-integration-decision.md).

Qualify the Python affected-test probe from [#383](https://github.com/kburson/aitm/issues/383) in an advisory GitHub-hosted Ubuntu shadow run under [#370](https://github.com/kburson/aitm/issues/370). Use the existing probe and the repository's locked toolchain. Bind each result to the exact PR, base, head, tested commit and tree, runner identity, controls, and workflow attempt. Record the selected IDs and witnesses or the reason for a full or unavailable result.

## Acceptance

- Exercise representative same-repository PR changes on hosted Ubuntu, including an ordinary in-scope source edit with a provable narrow assignment, shared or dynamic dependencies, a rename or deletion, and a CI or configuration input. Include a controlled direct and transitive regression pair. List the cases and expected results before running them.
- Compare the graph assignment and its observed outcomes with a full run on the same tested tree and comparable runner environment. Record the current hosted path-map decision for each PR, the exact inventories and outcomes, and assignment size and elapsed time. Investigate every missed failure, missing outcome, or contradictory binding. Qualification requires zero missed failures across the matrix and at least one explained useful narrowing on real repository code.
- Exercise stale or mismatched PR identity, missing inventory, and incomplete full evidence. Preserve full or unavailable decisions when the evidence is uncertain. Keep shadow execution appropriately isolated with read-only permissions and separate advisory evidence.
- Publish the qualification result for a future promotion decision. The required workflow, path map, gate, verifier, branch protection, and pinned #355 command retain their current roles. The shadow result carries no merge authority.

[Portable probe qualification](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/383/plan/2026-11-19-383-qualification.md)
