---
schema: "aitm.story/v0"
id: 129
title: "[M19] Native Linux qualification"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/129"
parent: 100
children: []
blocking: []
blocked-by: [128, 134, 135]
created: "2026-11-10T13:58:18Z"
updated: "2026-11-10T15:38:43+00:00"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M19", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "b51931139199a0a7382546e295fe0c38f46c8e990b8f102b7c59021d5fcd1da3"}
---

# [M19] Native Linux qualification

[GitHub issue #129](https://github.com/kburson/aitm/issues/129) · [Parent #100](../100/story.md) · [Accepted plan leaf M19](../100/plan/multi-project-usage-monitor-implementation-plan.md#m19-controlled-linux-qualification-and-delivery-gate)

**Required predecessors** [M18 #128](../128/story.md).

Use the completed [Grok #101](https://github.com/kburson/aitm/issues/101) and [Linux #102](https://github.com/kburson/aitm/issues/102) reports as applicable. They are evidence inputs carried by the parent.

Use the complete [NA-1 acceptance case](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#native-acceptance-case-na-1).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M19. Controlled Linux qualification and delivery gate

**Files** Extend `S/qualification.py`, `T/test_activation_receipt.py` and `README.md` after M18.

- [ ] Add `test_linux_receipt_requires_user_manager_ext4_native_receipts_and_arch` and `test_container_evidence_cannot_satisfy_linux_activation`. Reject any missing NA-1 outcome per target. Run red, implement and run green.
- [ ] Reproduce #102 credential-free checks on arm64 and x86-64. On each real supported target, verify authenticated Linux-native receipt and cursor continuity on Codex CLI, Claude Code and Grok Build CLI. On each architecture require two distinctly story-bound Grok turns through production admission across resume and a separate hookless eligible Grok turn counted once in its interval without a story. Prove user-manager startup, logout, allowed headless persistence, exact unit/process heartbeat, recursive watch overflow, crash replay, safe restore and qualified atomic operations on ext4. Run the complete NA-1 case and capture release receipts per target.
- [ ] Run the full locked suite and Ruff on the release candidate. Confirm the documented supported matrix matches actual receipts. Keep unqualified surfaces out of support claims. A production installation needs a separately authorized cutover with an explicit rollback or forward-recovery decision. Commit M19 and submit the integrated package for the project’s applicable review and delivery gates.

The verified Linux carrier prerequisites are [#134 M04-LC](../134/story.md) and [#135 M04-LA](../135/story.md), alongside M18 #128. [Reviewed split](../114/plan/jit.md#host-evidence-and-split).
