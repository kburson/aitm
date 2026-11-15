---
schema: "aitm.story/v0"
id: 303
title: "Enforce closed live-source qualification at approval and reserve"
kind: "story"
state: "refine"
issue: "https://github.com/kburson/aitm/issues/303"
parent: 100
children: []
blocking: [119, 129, 300, 304]
blocked-by: [210]
created: "2026-11-15T02:29:56Z"
updated: "2026-11-15T02:30:19Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/003/300/plan/2026-11-14-300-qualified-policy-split.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 300, "key": "M08b6-Release-Profile", "publication": "f98161a1728343cf2761fb9317735cd2241c0090", "raw-sha256": "afd2f1373f97c711f205aa0a3816872be821ec667c31371a73e7b87edc2ecea6", "issue-body-sha256": "741f325a425e11b35d3fe25796c70b26b533c9629c65e322850abfaa8b435e6f"}
---

# Enforce closed live-source qualification at approval and reserve

## M08b6-Release-Profile

Epic #100 first-release approved-source policy and custody prerequisite. Requires closed #210. Directly blocks #300, #119 and #129.

Implement the closed first-release policy contract and enforce it at live source approval, approved-root payload read, prepare and reserve/current retry. The profile has no product-reachable grant path in this leaf. #304 owns the real isolated host and authorization evidence. Deliver a private authenticated source exclusion decision for #300. Preserve history, prior custody, plain refusal, native diagnostics, independent healthy progress and all unchanged qualification gates. Do not implement journal coverage persistence, reporting, shipping a production catalog or cutover.

[Exact split and verification requirements](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/300/plan/2026-11-14-300-qualified-policy-split.md). Requires independent Refine, JIT, exact signed Test, source review, delivery and Close. Epic #2, C01 and production cutover are excluded.

Project 24 Rank 229.055. [Accepted revision](https://github.com/kburson/aitm/blob/f98161a1728343cf2761fb9317735cd2241c0090/.aitm/stories/003/300/plan/2026-11-14-300-qualified-policy-split.md).

## Independent Refine

Held on missing authenticated provider executable identity and policy generation or revocation source. The accepted split requires independent parent re-acceptance to reassign those inputs. JIT requires a passing Refine. [Review](plan/qualified-source-profile-independent-refine-r1.md).

## Current accepted enforcement scope

Independent acceptance assigned the real issuer to #304. Refine recovery is scoped to the closed policy and writer-local custody contract. [Accepted amendment](https://github.com/kburson/aitm/blob/79aecafe17c5dc0417fd00c2ecd37cdfe3651d58/.aitm/stories/003/303/plan/2026-11-14-303-isolated-source-issuer-amendment.md).
