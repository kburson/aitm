---
schema: "aitm.story/v0"
id: 292
title: "[#133] Build a candidate-bound fast story validation shadow runner"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/292"
parent: 133
children: []
blocking: [293]
blocked-by: [147, 288]
created: "2026-11-14T13:09:52Z"
updated: "2026-11-15T13:56:56Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-15-292-fast-story-shadow-plan.md", "plan/local-corrected.json", "plan/local-corrected.log", "plan/quality-first.log", "plan/trusted-verifier.json", "plan/hosted-signature.json", "plan/tree-disposition.json", "plan/reviews/formal-review.md"], "attachments": []}
expansions: []
trips: []
---

# [#133] Build a candidate-bound fast story validation shadow runner

Parent #133. Rank 120.

Build a bounded hosted fast-path shadow runner on reviewed inputs. Bind exact base, head and tested tree. Independently reconcile selected and mandatory IDs, outcomes, fallback and protected evidence custody. Record any unqualified input classes.

[Reviewed epic plan](../../001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md). #103 governs production.

## Bounded hosted runner

[Implementation plan](plan/2026-11-15-292-fast-story-shadow-plan.md) specifies exact input and fallback evidence.

## Test candidate

[Draft PR #314](https://github.com/kburson/aitm/pull/314) includes the pinned independent signature and exact path/content archive checks. [Local candidate](plan/local-corrected.json) reconciled both complete collections and all seven required outcomes. [Initial #103 quality log](plan/quality-first.log) retained for the correction.

## Exact candidate and review

[Trusted #103 verifier](plan/trusted-verifier.json) · [Signed review](plan/reviews/formal-review.md).
