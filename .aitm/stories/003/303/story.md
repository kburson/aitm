---
schema: "aitm.story/v0"
id: 303
title: "Enforce closed live-source qualification at approval and reserve"
kind: "story"
state: "refine"
issue: "https://github.com/kburson/aitm/issues/303"
parent: 100
children: []
blocking: [119, 129, 300]
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

Implement an explicitly closed first-release qualification profile with real isolated and release authority boundaries, and enforce it at live source approval, approved-root payload read, prepare and reserve/current retry. Deliver a private authenticated source exclusion decision for #300. Preserve history, prior custody, plain refusal, native diagnostics, independent healthy progress and all unchanged qualification gates. Do not implement journal coverage persistence, reporting, shipping a production catalog or cutover.

[Exact split and verification requirements](https://github.com/kburson/aitm/blob/planning/.aitm/stories/003/300/plan/2026-11-14-300-qualified-policy-split.md). Requires independent Refine, JIT, exact signed Test, source review, delivery and Close. Epic #2, C01 and production cutover are excluded.

Project 24 Rank 229.055. [Accepted revision](https://github.com/kburson/aitm/blob/f98161a1728343cf2761fb9317735cd2241c0090/.aitm/stories/003/300/plan/2026-11-14-300-qualified-policy-split.md).
