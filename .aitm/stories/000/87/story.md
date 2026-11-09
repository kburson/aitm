---
schema: "aitm.story/v0"
id: 87
title: "[Usage U03] Eligible source cursor and activation boundary"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/87"
parent: 83
children: []
blocking: [88, 89]
blocked-by: [85]
created: "2026-11-09T14:42:17Z"
updated: "2026-11-09T22:48:38+00:00"
last-branch: "codex/aitm-usage-u03"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md", "plan/source-review.md", "plan/claude-sideband-repair.md", "plan/claude-sideband-jit.md", "plan/claude-sideband-pickup-review.md", "plan/claude-sideband-source-review.md", "plan/claude-startup-jit.md", "plan/claude-startup-pickup-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U03", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "c857dc2a70fbd5acc6d67a1fb38287ca93ed5d1666d6dca4c3e94361298ab489"}
---

# [Usage U03] Eligible source cursor and activation boundary

[GitHub issue](https://github.com/kburson/aitm/issues/87) · [Parent #83](../83/story.md) · Review

**Required predecessors** [#85](../85/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/sources/{__init__,scan}.py`, `tests/test_scan.py`.

**Contract** `discover(registration: Registration) -> Iterator[CandidateSource]` and `scan(source: CandidateSource, checkpoint: SourceCheckpoint | None, cutoff: datetime) -> FrameBatch`. Return sanitized source-boundary evidence from approved-root candidates so U02 can verify enrollment before any usage admission. Resolve project eligibility per segment using configured checkout/worktree anchors or a validated explicit enrollment from U02. Keep readable unbound segments excluded. Separate physical incarnation from verified logical stream. Use keyed source locators and anchors and rediscover under approved roots. Check root confinement before opening and after replacement detection. Keep raw paths transient and record observed client/format versions. Read complete JSONL rows only. Publish cursor and observations through U01.

- [ ] Write `test_activation_cutoff_and_archive_continuity` with pre-cutoff, delayed first scan, partial final row, verified archive copy, overlap without continuity, replacement mid-read and symlink escape. Assert that one logical stream resumes once, unverifiable overlap is quarantined, and diagnostics include neither raw path, cwd, branch nor malformed payload. An unsupported format, unfamiliar usage shape, and recognized turn activity without recognized usage report gaps independently of the heartbeat. Include an explicitly enrolled reviewer outside the checkout under an approved root, an unbound session under that root and a later unrelated segment from the same session. Verify only enrolled project evidence enters the ledger.
- [ ] Run `test_scan.py` to show failure, implement discovery, cutoff and cursor handling, then pass leaf verification.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.

[Source verification and independent review](plan/source-review.md). Staged for the reviewed #83 integration. Delivery evidence is recorded when the package lands.

## Supplemental scanner pickup

The [native Claude metadata plan](plan/claude-sideband-repair.md) passed scoped independent review at raw SHA-256 `8df8dc435006f4520defef5f5b255cb7df136ca0b8a544f1460735bcc952e2d8`. The review verified that untimed metadata cannot change eligibility, cutoff or watermarks. The original reviewed scanner remains staged while #88 finishes. Reopen the scanner in its owned worktree on the exact subsequent integration base before #89 starts.

[Supplemental JIT](plan/claude-sideband-jit.md) · [Independent pickup review](plan/claude-sideband-pickup-review.md). The original source receipt remains part of the story history.

[Supplemental exact source verification and independent acceptance](plan/claude-sideband-source-review.md).

[Claude startup scanner JIT](plan/claude-startup-jit.md) · [Independent pickup review](plan/claude-startup-pickup-review.md). Earlier source acceptance remains retained.
