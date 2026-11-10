---
schema: "aitm.story/v0"
id: 186
title: "[#181 A01] Admit and register planning evidence"
kind: "story"
state: "test"
issue: "https://github.com/kburson/aitm/issues/186"
parent: 181
children: []
blocking: [187, 189]
blocked-by: []
created: "2026-11-10T21:02:13Z"
updated: "2026-11-10T22:48:37Z"
last-branch: "codex/aitm-186-planning-evidence"
estimate: {"agent-hours": 3.75, "size": "M"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "A01", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "fd0fd511b36ded6d59a5ead118af3c006d18971c5c1df307a1e0b2743d378aa3"}
---

# [#181 A01] Admit and register planning evidence

[GitHub issue #186](https://github.com/kburson/aitm/issues/186) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L57)

Required predecessors None. The proposed estimate is 3.75 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## A01. Admit and register planning evidence

- [ ] Test `test_pinned_tree_and_receipt_registration`. Build a small Git fixture containing a valid receipt and matching evidence event, an unregistered file, a path escape, mismatched digest, future-dated event and duplicate JSON key. Include identical duplicate registration (one receipt), one path with conflicting digests or a rewritten payload at the same path (held), and a subject/scope mismatch (held). Test declared and missing estimate scope. Move the branch and edit the worktree after pinning. Assert the original tree still supplies only its registered valid bytes, with an attributable gap for invalid inputs. Reject an as-of earlier than the commit and exclude later-recorded facts with coverage reasons.
- [ ] Run the A01 focused tests red. Implement the reader using Git objects and typed inputs. Test the one legacy exception. Admit only #181’s existing `historical-actual-backfill` event by matching `data.receipt_sha256` to the exact JSON path in its `data.evidence` list and to design SHA-256 `8d619b606cfd0142c46da7402ee52c20b95d3a78725894c12cc385309342b139`. Ignore its companion Markdown entries for timing. Reject any wrong story, path, digest or second registration that purports to introduce another seed. Expose the admitted seed bytes for A02, with missing typed dimensions kept Unknown. For v1, use explicit `core.evidence.recorded` kinds `story-timing-receipt` and `story-usage-receipt`, a relative path, SHA-256 and subject scope. Accept only bounded regular file blobs at registered paths under the subject's `attachments/timing/`. Bind path and scope to the subject. Resolve ancestry from the story records and relationship facts in the pinned tree. Ignore dependency edges and retain malformed or cyclic ancestry as a scoped gap. Use that graph in both projectors. Reject ambiguous or malformed records without accepting new workflow authority.
- [ ] Write the operator checklist with a fixed batch-plus-story path, stable observation ID, evidenced scope/phase/attempt, actor/role, start/end and recording UTC, safe evidence reference and coverage. Show one receipt and event pair. Use `python -m tools.story_dashboard.evidence --repo PATH --commit SHA --as-of UTC --receipt FILE --registration FILE` before publication, with both optional files supplied together. Without them the command validates the registered tree. Publish receipt and registration together. Confirm exact bytes after an uncertain write.
- [ ] Run green and retain the test output and exact candidate. An operator can prepare and validate sanitized receipts after this leaf.

## Delivery evidence

[Accepted design, plan and JIT](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)
