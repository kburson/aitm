---
schema: "aitm.story/v0"
id: 363
title: "[Spike] Identify the run a failure flag should watch"
kind: "spike"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/363"
parent: 362
children: []
blocking: [365]
blocked-by: []
created: "2026-11-16T19:41:49Z"
updated: "2026-11-22T00:24:25Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": "S"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-16-133-decomposition.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-21-363-delivery-plan.md", "plan/2026-11-21-363-scheduled-run-contract.md"], "attachments": ["attachments/2026-11-21-363-actions-evidence.json"]}
expansions: []
trips: []
---

# [Spike] Identify the run a failure flag should watch

[GitHub issue #363](https://github.com/kburson/aitm/issues/363) · [Parent #362](../362/story.md) · [Decomposition](../../001/133/plan/2026-11-16-133-decomposition.md)

Project 24 Rank 630. Priority P2. Size S.

Confirm that the flag watches the production scheduled Category full sweep from #361 in `kburson/aitm`, workflow ID `425235652`, path `.github/workflows/category-full-sweep.yml`, event `schedule`, branch `trunk`.

## Acceptance

- Read the canonical workflow metadata and exact attempt for [verified run 44864075824](https://github.com/kburson/aitm/actions/runs/44864075824/attempts/1). Record the authenticated identity, source, timestamps and successful same-attempt reconcile job.
- Define the activation floor and ordering key, what constitutes a qualifying failure or success, and the disposition of manual events, reruns, cancellations, incomplete runs, delayed or missing slots, and API errors. Specify the rule for a newer qualifying failure while the flag is active.
- Deliver the research receipt via a PR to `planning` with independent Grok PR review on the current candidate before merge. #365 consumes the accepted receipt.

[Delivery plan](plan/2026-11-21-363-delivery-plan.md).

[Research receipt](plan/2026-11-21-363-scheduled-run-contract.md) and [evidence](attachments/2026-11-21-363-actions-evidence.json).
