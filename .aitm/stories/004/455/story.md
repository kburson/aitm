---
schema: "aitm.story/v0"
id: 455
title: "[Spike] Investigate session-owned agent activity and cost reporting"
kind: "spike"
state: "done"
issue: "https://github.com/kburson/aitm/issues/455"
parent: null
children: []
blocking: []
blocked-by: []
created: "2026-11-25T15:05:37Z"
updated: "2026-11-25T15:21:25.060Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: null
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": ["attachments/455-findings.md", "attachments/100-child-assessment.md", "attachments/455-pilot-receipt.json", "attachments/455-publisher-receipt.json", "attachments/independent-evidence-review.md"]}
expansions: []
trips: []
---

# [Spike] Investigate session-owned agent activity and cost reporting

[GitHub #455](https://github.com/kburson/aitm/issues/455)

Use the delivered work from #422 onward and the earlier work in [Epic #100](https://github.com/kburson/aitm/issues/100) as research inputs.

## Question

What is the smallest reliable way for the agent in a live chat to record its own activity and the activity of the agents it supervises, then publish per-turn evidence to the active story on `planning`?

## Experiment

- Inventory the existing assets. Evaluate the portable receipt store, capture and exact recovery adapters, story and epic rollups, and report/export path from #435. Examine the headless, interactive, delayed-recovery, and review evidence from #426–#434, including the #444 AIPR companion receipts. Compare the per-turn cost tables and timing receipts in #442–#445 with the existing dashboard registration and #100 accounting, pricing, and snapshot code. Record each asset's reuse value, dependencies, and limitations.
- In a disposable project, exercise a solo live agent and a live orchestrator. Include the chat agent's own turns, a spawned headless agent, and supported SPR/XPR review turns under the orchestrator's supervision. Use Codex, Claude Code, and Grok Build across the cases. Keep each route's capture and review coverage explicit, including the Codex sealed-review gap where applicable.
- Bind each supervised turn to the project and active story in its owning session at the time the turn starts or is dispatched. Carry the same assignment through a story switch, resume or compaction, delayed or out-of-order completion, interruption, replay, and handoff. Exercise overlapping agents and simultaneous writers to planning. Preserve unsupported or ambiguous activity as pending, unknown, or unattached, with provenance. Verify that a late receipt settles the original story once and that nested or overlapping receipts do not inflate totals.
- Compare native completion and exact retained readback with the lightest viable session-owned helper. Test whether sanitized, replay-safe receipts and coverage records can be published to the story on `planning` under existing authority. Measure collection and publication overhead, extra model turns, and recovery cases. Keep native transcripts and credentials private and the AIPR sealed decision under AIPR authority.
- Verify a reproducible story subtotal and receipt-to-report cutoff. Preserve engagement, cached input, new input, output, provider-reported amounts, API-equivalent estimates with a pinned rate basis, and verified billed amounts as distinct measures where evidence supports them. Show which expected turns are measured, pending, missing, or unattributed.

## Deliverable

Publish a reuse matrix, a small end-to-end feasibility receipt, and a recommendation for the session-owned capture and reporting path. Evaluate each open #100 child against the session-owned pilot. Identify the concrete capability it would add, who benefits, what the delivered work already covers, and the expected implementation and maintenance effort. Recommend closing a child as **Not delivered** when the newer approach covers its useful outcome or the residual benefit does not justify the work. Where a child offers significant additional value, outline the smallest design and verification path that delivers that value using what we learned from #422 onward. Identify the impact of each recommendation on Core #2 and #230, including any dependency that would need a replacement. The spike concerns live chat sessions and their supervised work, using per-story evidence on `planning`. Global project discovery, an always-on host service, and a new platform integration are outside its scope.

## Evidence

[Feasibility findings and reuse matrix](attachments/455-findings.md) · [#100 child assessment](attachments/100-child-assessment.md) · [Native pilot receipt](attachments/455-pilot-receipt.json) · [Git publication receipt](attachments/455-publisher-receipt.json).

[Independent evidence review](attachments/independent-evidence-review.md) passed. [Research sign-off](retro/2026-11-25-spike-sign-off.md).

GitHub closed #455 as completed. Project 24 shows Done. The recommendations are recorded for a separate decision on the ten remaining #100 contracts and Core dependencies.
