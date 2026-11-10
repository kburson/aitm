---
schema: "aitm.story/v0"
id: 117
title: "[M07] Native scope and handoff"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/117"
parent: 100
children: []
blocking: [118, 182]
blocked-by: [116]
created: "2026-11-10T13:57:58Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M07", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "f2e8d780402afd62b409a1259957ecb178afd4f29c33aa9725c21256d69b009d"}
---

# [M07] Native scope and handoff

[GitHub issue #117](https://github.com/kburson/aitm/issues/117) · [Parent #100](../100/story.md) · [Accepted plan leaf M07](../100/plan/multi-project-usage-monitor-implementation-plan.md#m07-authenticated-scope-handoff-and-proof-holds)

**Required predecessors** [M06 #116](../116/story.md).

The [reviewed M07 split](plan/2026-11-10-117-m07-split.md) retains this issue for native routing, handoff and proof holds. [#182 M07b](../182/story.md) owns producer and legacy compatibility. Both gate #118. [Accepted pickup](plan/2026-11-10-117-native-scope-plan.md) · [Independent review](plan/2026-11-10-117-native-scope-pickup-review.md).

Apply the accepted plan’s [legacy command surface after adoption](https://github.com/kburson/aitm/blob/be326aa06bbf0180969ecadb8df74cf4a37a62c4/.aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md#legacy-command-surface-after-adoption).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M07. Authenticated scope, handoff and proof holds

**Files** Create `S/monitor_scope.py` and `T/test_monitor_scope.py`. Extend verified marker and owner-binding reuse in `S/scopes.py` and proposal admission in `S/monitor_control.py`. Add `monitor scope mark|handoff|dispose --request FILE` in `S/cli.py`.

**Contract** `resolve_route(observation: NativeObservation, registry: RegistryView, scopes: ScopeView) -> RouteDecision` and `ScopeState.apply_handoff(command: Handoff, receipt: VerifiedBoundary) -> HandoffDisposition`. Validate authority, exact before-boundary generation and next native boundary. A valid ordinary marker contradicting a registered anchor holds both totals. A dedicated handoff may override only the verified stale anchor lineage. Keep bounded provenance-only replay holds with expiry and explicit gaps. Scope proposals submitted through the M06 command envelope must name the registered integration or operator authority and join the corresponding native marker before admission. A queued command is never proof of scope.

- [ ] Write `test_foreign_ordinary_marker_conflicts_then_prospective_handoff_routes`, `test_handoff_A_to_B_to_C_with_retained_A`, `test_competing_receipts_conflict_in_both_native_delivery_orders` and `test_expired_hold_releases_no_usage`. Return the bounded affected observation lineage and scope span. M09 and M13 test the post-ACK published transition. Persist hold expiry on a UTC basis and verify expiry across restart. Test the legacy scope and relationship command path with exact receipt shapes and idempotent queue IDs. Test a development owner lacking destination worktree proof.
- [ ] Run red. Implement evidence-backed routing and hold dispositions. Run green with `test_scopes.py`. Commit M07.
