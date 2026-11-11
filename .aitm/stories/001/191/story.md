---
schema: "aitm.story/v0"
id: 191
title: "[#181 A06] Prove one live manual capture and board readback"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/191"
parent: 181
children: []
blocking: [193]
blocked-by: [190]
created: "2026-11-10T21:02:20Z"
updated: "2026-11-11T04:43:18Z"
last-branch: "codex/aitm-191-live-pilot"
estimate: {"agent-hours": 2.75, "size": "S"}
priority: "P1"
origin: ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": ["plan/jit.md"], "plan": ["plan/jit.md", "plan/delivery-checklist.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 181, "key": "A06", "path": ".aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md", "publication": "fd5b22ff0c33c582dd9a0926435d071f09ac6156", "raw-sha256": "147cbee5740f725c9c65df9c09034912220d179475dc1c707e0844316a6c1c80", "section-sha256": "ce6bf8365ae59684a364b3e08d1034d2607f234fd19544184abe34feff6fc953"}
---

# [#181 A06] Prove one live manual capture and board readback

[GitHub issue #191](https://github.com/kburson/aitm/issues/191) · [Parent #181](../181/story.md) · [Exact accepted plan section](https://github.com/kburson/aitm/blob/fd5b22ff0c33c582dd9a0926435d071f09ac6156/.aitm/stories/001/181/plan/story-timing-dashboard-implementation-plan.md#L88)

Required predecessors #190. The proposed estimate is 2.75 implementation agent-hours. Recheck scope and estimate at the leaf’s own refinement and JIT.

## Accepted plan excerpt

## A06. Prove one live manual capture and board readback

- [ ] Select an approved child and recorder at pickup. Retain one evidenced turn, in-turn tool wait, scoped switch and explicit owner request/response. If an endpoint cannot be verified, record the gap. Verify the declared observation against its safe source reference.
- [ ] Publish one sanitized receipt and its exact registration in the child's planning record in the same commit. Rebuild from another checkout with that commit pinned and confirm the observed change. Retry the same batch with identical bytes and registration. It is a no-op once readback proves the first commit. Verify there is one contribution.
- [ ] As the named operator, reconcile the target GitHub item and existing value before projecting Actual and coverage together from the reviewed snapshot. Set and read back an interim Pending verification coverage label before writing the numeric Actual. Read the numeric result back, then set the final coverage label and verify both fields against the snapshot. If any write is interrupted or its result is uncertain, read both fields and reconcile against the exact intended snapshot before retrying. Test interruption after the interim label and after the numeric write. Hold a stale or conflicting item for reconciliation. Set Cost only with complete coverage from A04’s verified report binding for the exact target scope and selector. Retain the verified export/report identity, coverage and readback. Keep an unsupported Cost field blank where no valid value exists.
- [ ] Record the reproducible capture and readback instructions in `operator.md`. The evidence links the leaf, planning commit, timing watermarks and board readback without private payloads.

## Delivery evidence

[Reviewed pickup](plan/jit.md) · [Independent pickup review](plan/jit-review.md) · [Delivery checklist](plan/delivery-checklist.md)
