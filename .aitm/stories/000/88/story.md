---
schema: "aitm.story/v0"
id: 88
title: "[Usage U04] Codex cumulative usage adapter"
kind: "story"
state: "review"
issue: "https://github.com/kburson/aitm/issues/88"
parent: 83
children: []
blocking: [90]
blocked-by: [87]
created: "2026-11-09T14:42:18Z"
updated: "2026-11-09T18:04:45+00:00"
last-branch: "codex/aitm-usage-u04"
estimate: {"agent-hours": 4.0, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U04", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "b502b081441faa96a92d0e34b06d0d880d6a1456bba4c7a89113330496bb1c6b"}
---

# [Usage U04] Codex cumulative usage adapter

[GitHub issue](https://github.com/kburson/aitm/issues/88) · [Parent #83](../83/story.md) · Review

**Required predecessors** [#87](../87/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/sources/codex.py`, `tests/test_codex.py`, `tests/fixtures/codex/usage.jsonl`.

**Contract** `read_codex(batch: FrameBatch, state: CodexState, eligibility: Eligibility) -> AdapterResult`. Feed session metadata, turn context and token counters into the common observation format. Link scope boundaries to proven source order. Qualify a new epoch only with verified origin evidence. Priceable request usage needs a consistent delta and category relationship.

- [ ] Write `test_codex_deltas_exclusion_and_epochs` with a known-zero first request, pre-cutoff baseline, in-flight ambiguous request, repeated total, eligible→excluded→eligible, real reset reusing old totals, truncated start, conflicting key and unknown aggregate span. Assert exact known-category counts, separate gaps and no excluded usage spillover. Replay from the same logical archive without inflation. Restart a fresh process after an excluded segment and use the transactionally retained provider checkpoint to continue without spillover. Exercise model and effort change, a retried or errored request, an independently identified subprocess and one quota observation with reset metadata. Missing durable evidence is a gap.
- [ ] Run `test_codex.py` to show failure, implement the adapter using allowlisted field reads, then pass leaf verification.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.
