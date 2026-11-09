---
schema: "aitm.story/v0"
id: 85
title: "[Usage U02] Scope inbox and provider-session binding"
kind: "story"
state: "backlog"
issue: "https://github.com/kburson/aitm/issues/85"
parent: 83
children: []
blocking: [86, 87]
blocked-by: [84]
created: "2026-11-09T14:42:16Z"
updated: "2026-11-09T14:43:23+00:00"
last-branch: "planning"
estimate: {"agent-hours": 3.5, "size": "S"}
priority: "P1"
origin: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
files: {"draft": "draft.md", "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan", "story": 83, "key": "U02", "path": ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md", "publication": "6ee371590ff3ce0cb5a108bdd1e89cfb17bc2300", "raw-sha256": "07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5", "section-sha256": "5bd0ab66177ad25c20eda276e12acca18f184037c58b97be353a012782120984"}
---

# [Usage U02] Scope inbox and provider-session binding

[GitHub issue](https://github.com/kburson/aitm/issues/85) · [Parent #83](../83/story.md) · Backlog

**Required predecessors** [#84](../84/story.md)

## Accepted parent decomposition

**Files** `src/aitm_usage/{scopes,cli}.py`, `tests/test_scopes.py`.

**Contract** `enqueue_marker(directory: Path, marker: ScopeMarker) -> MarkerId`, `resolve_scope(observation: Observation, view: LedgerView) -> ScopeResolution`, and `attest_marker(marker: ScopeMarker, boundary: SourceBoundary) -> MarkerDisposition`. The private inbox uses atomic file publication. Require a monotonic per-session scope sequence and proof the marker was published before its effective request or turn boundary. Validate against the SourceBoundary contract using fixtures in this leaf. A boundary may be proven for a candidate session under an approved source root before that session is enrolled. Candidate evidence carries no usage into the ledger. Admission covers only the explicit eligible segment after a proven marker. U04 and U05 provide real boundaries and U08 connects them. A late scan can resolve an already-published marker. A marker created after a claimed boundary can affect only a later verifiable boundary, and an explicit correction appends a revision. Return pending until the enrolled adapter validates the boundary, then commit the marker and return an accepted receipt. A supported serial request marker precedes the first child response in provider order. A turn-only marker is emitted before the child turn begins. Enrollment binds the explicit owner provider session and generation. A same-story marked reviewer keeps its own role and an unproven session is unassigned. Consume into the ledger before acknowledging. Expose scope mark, development bind and scope correct through the queued CLI operations in the command table.

**Normal session proof.** For Codex Desktop, derive the session reference from the invoking agent's `CODEX_THREAD_ID` and confirm it against the enrolled rollout's session metadata. A same-turn marker is admissible when a recognized in-session tool call and result carry its opaque command receipt in provider order before the next recorded model request boundary. Otherwise use a pre-turn marker with the next verifiable turn ID. For Claude Code, the controlled launcher reserves a session UUID with `--session-id` before work and verifies the emitted init or transcript session identity. An authorized resume uses the already enrolled session. For a native review launched by a broker, use its verified reviewer launch/join identity and bind the first provable boundary after enrollment. Setup work before that remains Unknown. A source-proven serialized tool receipt or a marker recorded before the next turn provides order. Timestamps on their own do not prove order. Keep unverifiable session or boundary claims pending or Unknown. Do not retain raw tool content.

- [ ] Write `test_planning_scope_and_development_owner` with one epic and two children in a single session. Verify first child request and switch-back for marker-first and observation-first arrival, Unknown while unresolved, scope before the next turn when the request boundary cannot be proven, owner-only development default, unmarked nonowner, compatible marked reviewer, conflicting marker quarantine, housekeeping and two review roles. Exercise actual CLI marker publication, idempotent inbox replay, recorded correction that preserves an earlier as-of result, invalid retroactive claim and duplicate sequence.
- [ ] Run `test_scopes.py` to show failure, implement the marker and rollup contract, then pass leaf verification.
