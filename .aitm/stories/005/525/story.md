---
schema: "aitm.story/v0"
id: 525
title: "[M2] Qualify read-only legacy source access for M7"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/525"
parent: 524
children: []
blocking: [522]
blocked-by: [72]
created: "2026-11-27T06:05:34Z"
updated: "2026-11-27T06:05:49.247Z"
last-branch: "planning"
estimate: {"agent-hours": 3.75, "size": "S"}
priority: null
origin: ".aitm/stories/005/524/design/github-extension-design.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
---

# [M2] Qualify read-only legacy source access for M7

[#525](https://github.com/kburson/aitm/issues/525) · Parent [#524](https://github.com/kburson/aitm/issues/524) · Backlog

**Blocked by:** [#72](https://github.com/kburson/aitm/issues/72)

**Blocking:** [#522](https://github.com/kburson/aitm/issues/522)

Deliver the bounded read-only GitHub source adapter and capability proof required by #522. Consume released Core #72. Expose approved legacy issue and Timing Log evidence reads with canonical repository identity, cutoff, stable IDs, pagination and typed incomplete/unavailable results. M7 owns the full crawl and corpus normalization.

## Acceptance criteria

- [ ] Qualify an installed source-only adapter with a pinned multi-page fixture. Exercise wrong repository, missing page, stale cursor, rate limit and permission failure. Verify incomplete and unavailable results stay distinct from an empty result.
- [ ] Against the configured legacy repository, verify a bounded authorized read of representative issue metadata and Timing Log evidence. Retain scoped source IDs, cutoff, pagination/readback evidence and digests. Use only the authorized read surface.
- [ ] Publish the versioned interface and sanitized capability receipt that #522 can consume. Export enough provenance for exact replay or a visible incomplete disposition.
- [ ] The installed source capability can qualify without Project, hosted PR writes, rulesets, M3, or closure of the parent epic.

Proposed estimate **3.75 implementation agent-hours**, size **S**. This covers the narrow read contract, fixture and live receipt. Further legacy fields or the full history scan belong to a separate reviewed scope.

[M2 design and source handoff](../524/design/github-extension-design.md#read-only-source-access-for-m7).

## Reviewed independent landing and M7 intake

Qualify and land the source-only capability and exact compatible wheel independently after #72. M7 #522 checks its release and qualified live receipt before corpus capture. Use a versioned selection predicate with fixture and approved bounded live input so qualification does not wait for M7 policy. [Reviewed M2 handoff](https://github.com/kburson/aitm/blob/4db85c4b31b8a091716bc97303cb3538a31a2a57/.aitm/stories/005/524/design/github-extension-design.md#delivery-handoff-and-sequencing).
