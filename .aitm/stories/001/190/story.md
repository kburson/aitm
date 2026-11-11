---
schema: "aitm.story/v0"
id: 190
title: "[#181 A05] Publish a reproducible local snapshot"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/190"
parent: 181
children: []
blocking: [191, 192]
blocked-by: [188, 189]
created: "2026-11-10T21:02:19Z"
updated: "2026-11-11T04:23:19Z"
last-branch: "codex/aitm-190-local-snapshot"
estimate: {"agent-hours": 3.0, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "A05", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "b72d456125bda64b53a884fb47e18a3f08d7168988896f532d8e66b3638765b0"}
---

# [#181 A05] Publish a reproducible local snapshot

[GitHub issue #190](https://github.com/kburson/aitm/issues/190) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L82)

Required predecessors #188, #189. The proposed estimate is 3 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## A05. Publish a reproducible local snapshot

- [ ] Test `test_rebuild_seed_snapshot_byte_for_byte` through the real command. Two clean readers with identical Git object, as-of and usage selector emit byte-identical normalized JSON. Compare all ten Actual values at the historical parity pin with the existing receipt and the #111 elapsed scopes with planning events. Assert estimate scope and basis, progress, coverage, links, direct versus child rollups and timing/usage watermarks. Incomplete or absent cost stays Unknown.
- [ ] Run red. Implement `build_snapshot` and the documented command. Emit `snapshot.json` and a deterministic `validation.json` in the chosen local directory outside the tracked checkout. Serialize sorted object keys, UTF-8, compact separators and a trailing newline. Use stable row ordering, integer milliseconds and exact decimal USD strings. Resolve output paths physically and reject paths in any Git worktree, including symlink escapes into one. Test bad pins and output aliases. Replace each output atomically. Bind the validation report to the snapshot digest so interrupted output cannot masquerade as the matching report. Keep inputs fixed across rerun and fail closed on a bad pin.
- [ ] Run green and record the source commit, command, output digests and seed parity. Use this as the same input for A06 and B01.

## Delivery evidence

[Reviewed pickup](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)
