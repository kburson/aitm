---
schema: "aitm.story/v0"
id: 89
title: "[Usage U05] Claude Code request usage adapter"
kind: "story"
state: "develop"
issue: "https://github.com/kburson/aitm/issues/89"
parent: 83
children: []
blocking: [90]
blocked-by: [87]
created: "2026-11-09T14:42:19Z"
updated: "2026-11-09T18:17:36+00:00"
last-branch: "codex/aitm-usage-u05"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": ["design/design.md"], "plan": ["plan/implementation-plan.md", "plan/jit.md", "plan/pickup-review.md"], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U05", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "f083ea70f3c96977ead3cc714dd3def9479003b753a9a5d2d6badb55e9f320a7"}
---

# [Usage U05] Claude Code request usage adapter

[GitHub issue](https://github.com/kburson/aitm/issues/89) · [Parent #83](../83/story.md) · Develop

**Required predecessors** [#87](../87/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/sources/claude.py`, `tests/test_claude.py`, `tests/fixtures/claude/usage.jsonl`.

**Contract** `read_claude(batch: FrameBatch, state: ClaudeState, eligibility: Eligibility) -> AdapterResult`. Group per-session request rows, validate message identity and retain immutable revisions. Compare terminal checkpoints against exact request prefix totals. Keep unsupported terminal or account signals qualified as Unknown.

- [ ] Write `test_claude_revisions_terminal_and_nested_usage` for partial streamed rows, terminal reconciliation, conflicting request/message identity, a late revision to a pre-cutoff request, same row on replay, and nested child usage overlapping a parent aggregate. Assert each independent request contributes once and unresolved overlap is separate. Test eligible and excluded segments, retry, model or effort change, missing terminal evidence and supported structured quota observations. Restart from a committed partial prefix and prove exact reconciliation with sanitized durable fields.
- [ ] Run `test_claude.py` to show failure, implement the adapter and read boundaries, then pass leaf verification.

## Current pickup

[Design](design/design.md) · [Plan](plan/implementation-plan.md) · [JIT](plan/jit.md) · [Scoped review](plan/pickup-review.md). This is a manual Develop admission for the dedicated worktree at the pinned base.
