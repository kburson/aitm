---
schema: "aitm.story/v0"
id: 120
title: "[M10] Wake and park scheduler"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/120"
parent: 100
children: []
blocking: [121]
blocked-by: [115, 119]
created: "2026-11-10T13:58:03Z"
updated: "2026-11-10T14:00:46Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 100, "key": "M10", "path": ".aitm/stories/001/100/plan/multi-project-usage-monitor-implementation-plan.md", "publication": "be326aa06bbf0180969ecadb8df74cf4a37a62c4", "raw-sha256": "8899a4d1c35c2e2508d0ae3278f91261795e22bdba9955e96264cb4e414e5f21", "section-sha256": "49d715a1eff778056c37cf9c91352498eb0d05e71611a50f8e47c6d55050af86"}
---

# [M10] Wake and park scheduler

[GitHub issue #120](https://github.com/kburson/aitm/issues/120) · [Parent #100](../100/story.md) · [Accepted plan leaf M10](../100/plan/multi-project-usage-monitor-implementation-plan.md#m10-private-wake-ingress-and-parked-session-scheduling)

**Required predecessors** [M05 #115](../115/story.md), [M09 #119](../119/story.md).

This Backlog record is bound to the accepted parent plan at `be326aa06bbf0180969ecadb8df74cf4a37a62c4`. Before Develop, obtain the applicable leaf design, Refine estimate, plan and JIT approval. Validate the four implementation agent-hour cap at JIT. Paths in the accepted excerpt are relative to `packages/aitm-usage`.

## Accepted plan excerpt

### M10. Private wake ingress and parked-session scheduling

**Files** Create `S/monitor_scheduler.py` and `T/test_monitor_scheduler.py`. Add wake ingress to `S/monitor_control.py`, approved provider producers in `S/sources/hooks.py` and `monitor park --session-ref ID` and `monitor hooks install --project UUID --provider ID` in `S/cli.py`.

**Contract** `Scheduler.notify(hint: WakeHint) -> None` and `Scheduler.take_due(now: float, limit: int) -> tuple[WorkItem, ...]`. Use a same-user Unix socket inside the pinned private state directory for wake ingress. Reject a mismatched peer UID, bounded-message violations and unauthorized source locators. Resolve raw locators transiently and return a nonblocking best-effort result so a failed wake cannot stall a provider. Persist only allowlisted keyed hints. Coalesce by native provider, session and verified turn where available. Apply Active, Settling and Parked as scheduling states. Explicit park carries no workflow or scope authority. `HookSender.notify(event: HookEvent) -> WakeDisposition` publishes bounded best-effort signals. The installer verifies owner approval and the pinned provider surface. Use an owned Codex user-local plugin in its private provider home, an owned Claude Code hook entry in user-local settings, and an owned Grok Build file in the private Grok user hooks directory. Filter out unauthorized context before persistence. Preserve foreign hooks and native trust. The installed launcher resolves approved private settings itself. Embed no checkout, state or socket path in the command and change no tracked repository files. M10 tests and M15 rehearsal use isolated provider homes. Use checked ctypes for peer credentials where required. [Codex plugins](https://developers.openai.com/plugins/build/plugins) · [Claude Code settings](https://code.claude.com/docs/en/settings) · [Grok hooks](https://docs.x.ai/build/features/skills-plugins-marketplaces#hooks) The Grok scope producer uses the qualified M05 prompt-scoped carrier to carry an M07 authorized marker proposal. The adapter joins it to a durable completion. A wake sender alone has no marking authority. Keep fairness when another project is blocked.

- [ ] Write `test_park_final_catchup_then_late_write_reopens`, `test_stale_stop_cannot_park_newer_turn`, and `test_duplicate_and_missing_hooks_keep_idempotent_progress`. Verify concurrent turns, resume, retained cursors and bounded quiet backoff. A lost or refused wake must allow the provider to proceed and leave native reconciliation able to recover. Test an approved install with unchanged tracked files, consumed wake retirement and explicit park without scope change.
- [ ] Run red. Implement the scheduler using monotonic deadlines and bounded work units. Run green with `test_monitor_delivery.py`. Commit M10.
