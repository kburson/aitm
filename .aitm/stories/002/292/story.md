---
schema: "aitm.story/v0"
id: 292
title: "[#133] Build a candidate-bound fast story validation shadow runner"
kind: "story"
state: "done"
issue: "https://github.com/kburson/aitm/issues/292"
parent: 133
children: []
blocking: [293]
blocked-by: [147, 288]
created: "2026-11-14T13:09:52Z"
updated: "2026-11-15T14:10:22Z"
last-branch: "planning"
estimate: {"agent-hours": 4, "size": "M"}
priority: "P2"
origin: ".aitm/stories/001/133/plan/2026-11-14-133-behavior-driven-validation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": ["plan/2026-11-15-292-fast-story-shadow-plan.md", "plan/local-corrected.json", "plan/local-corrected.log", "plan/quality-first.log", "plan/trusted-verifier.json", "plan/hosted-signature.json", "plan/tree-disposition.json", "plan/reviews/formal-review.md", "plan/delivery.json", "plan/premerge-verifier.json", "plan/premerge-rules.json", "plan/shadow-admission.json", "plan/shadow-admission.json.sig", "plan/shadow-admission-review.md", "plan/shadow-evidence-review.md", "plan/2026-11-15-292-hosted-shadow-results.md", "plan/verify-hosted-shadow.py", "plan/formal-review.md", "plan/selected/shadow-admission.json", "plan/selected/shadow-admission.json.sig", "plan/selected/shadow-admission-review.md", "plan/selected/verified.json", "plan/selected/hosted-receipt.zip", "plan/selected/hosted.log", "plan/selected/closed-probe.json", "plan/selected/stale-refusal.log", "plan/fallback/shadow-admission.json", "plan/fallback/shadow-admission.json.sig", "plan/fallback/shadow-admission-review.md", "plan/fallback/verified.json", "plan/fallback/hosted-receipt.zip", "plan/fallback/hosted.log", "plan/fallback/closed-probe.json", "plan/fallback/stale-refusal.log", "plan/closure-receipt.json"], "attachments": []}
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

## Delivery

[Verified exact-tree delivery](plan/delivery.json) · [Pre-merge #103 verifier](plan/premerge-verifier.json).

## Hosted selected admission

[Signed admission](plan/shadow-admission.json) · [Independent review](plan/shadow-admission-review.md). This exact record authorizes the shadow probe.

## Hosted fallback admission

[Signed admission](plan/shadow-admission.json) · [Independent review](plan/shadow-admission-review.md). This exact record authorizes the shadow probe.

## Qualified bounded hosted evidence

[Hosted selected and fallback results](plan/2026-11-15-292-hosted-shadow-results.md) · [Signed independent review](plan/shadow-evidence-review.md) · [Exact source deployment review](plan/formal-review.md).

The Markdown-only hosted probe verified the exact seven mandatory tests and native child witnesses. The executable-scope probe returned full-required without running pytest. Both tested inputs were independently signed and are qualified only within this shadow profile. #103 retains production merge authority.

## Closure

[Verified closure receipt](plan/closure-receipt.json).
