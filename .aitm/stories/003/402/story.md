---
schema: "aitm.story/v0"
id: 402
title: "Qualify a reusable suite declaration across edits and bases on hosted Ubuntu"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/402"
parent: 370
children: []
blocking: []
blocked-by: []
created: "2026-11-19T22:12:31Z"
updated: "2026-11-19T23:52:00Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: "P2"
origin: ".aitm/stories/003/370/plan/2026-11-19-370-suite-hosted-integration-decision.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# Qualify a reusable suite declaration across edits and bases on hosted Ubuntu

[GitHub issue #402](https://github.com/kburson/aitm/issues/402) · [Parent #370](../370/story.md) · [Integration decision](../370/plan/2026-11-19-370-suite-hosted-integration-decision.md).

Qualify a repeatable declaration for one real pytest suite in hosted Ubuntu shadow runs. Reuse the #383 exact Git snapshot resolver and the Grok replay qualification from #393 and #398. The current production pilot admits two exact source variants on one base. Establish what evidence lets a later eligible edit use the same suite and what changes invalidate that evidence.

## Acceptance

- Define a versioned, reviewable declaration for the bounded Grok replay production input. Record the target, allowed change shape, caller and callback boundaries, suite and shared inputs, runtime, and required evidence. Bind decisions to current Git identities. An unrelated base advance may carry the declaration forward only when all declared inputs and assumptions are verified. Relevant drift requires full or unavailable with a clear reason.
- Qualify a fresh bounded production edit beyond the #398 variants, and exercise the declaration again after an unrelated advance of the base. A controlled regression must fail in both the assigned suite and full run. Include relevant dependency or configuration drift and invalid Git identity controls. Record the case expectations before hosted execution.
- On each exact hosted PR tree, compare the suite assignment, current path map, and complete full-suite outcomes on a comparable Ubuntu runner. Preserve node IDs, per-test outcomes, decoder reach, setup and selection costs, and measured lane time. Require useful real narrowing with no missed failures or mismatched selected outcomes in the declared cases.
- Publish the repeatability result and a recommendation for routine hosted advisory integration under #370. Keep the experiment isolated and advisory. Preserve the required workflow, map, evaluator, verifier, branch rules, and pinned #355 command.

[Parent #370](https://github.com/kburson/aitm/issues/370) · [#393 results](https://github.com/kburson/aitm/issues/393) · [#398 results](https://github.com/kburson/aitm/issues/398)

## Replaced

Replaced before work started on 2026-11-19. Do not run this story. [#403](../403/story.md) lists the tests reached by the import chain for one real product change. The acceptance above stays as the record of the story that was filed and then replaced. GitHub #402 is closed as not planned.
