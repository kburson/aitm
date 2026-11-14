---
schema: "aitm.story/v0"
id: 295
title: "[M08b6] Contain unqualified Claude Agent overlap at the routing journal"
kind: "story"
state: "refine"
issue: "https://github.com/kburson/aitm/issues/295"
parent: 100
children: []
blocking: [119]
blocked-by: [210]
created: "2026-11-14T13:11:34Z"
updated: "2026-11-14T13:13:56Z"
last-branch: "planning"
estimate: {"agent-hours": null, "size": null}
priority: null
origin: ".aitm/stories/001/119/plan/2026-11-13-119-qualified-sources-reacceptance-r3.md"
files: {"draft": null, "events": "events.jsonl", "design": [], "plan": [], "attachments": []}
expansions: []
trips: []
plan-origin: {"kind": "accepted-parent-plan-amendment", "story": 100, "key": "M08b6", "path": ".aitm/stories/001/119/plan/2026-11-13-119-qualified-sources-reacceptance-r3.md", "publication": "54f2a7f93668d1a5c744be8a8a654a51b073e2cc", "raw-sha256": "75d073bda40f545f53f0dac6429dca571875592b864f72a37d17509698d0fd3c"}
---

# [M08b6] Contain unqualified Claude Agent overlap at the routing journal

[GitHub #295](https://github.com/kburson/aitm/issues/295) · [Independently accepted amendment](https://github.com/kburson/aitm/blob/54f2a7f93668d1a5c744be8a8a654a51b073e2cc/.aitm/stories/001/119/plan/2026-11-13-119-qualified-sources-reacceptance-r3.md).

Project 24 Rank 229.1.

Epic #100 direct child. Prerequisite #210. Blocks #119. The existing independent Refine, JIT, Test, Review, delivery and Close checks apply.

**Files** Extend `S/monitor_journal.py`, `S/monitor_scope.py` and `S/monitor_registry.py` at the authenticated read and reserve boundary. Extend `T/test_monitor_journal.py`. Put the allowlisted native-shape fixture under `T/fixtures/monitor/`. S and T use the accepted parent plan's package path definitions.

**Contract** Keep `RoutingJournal.prepare(source_id: UUID, locator: SourceLocator) -> PreparedRouting` and `RoutingJournal.reserve_batch(prepared: PreparedRouting) -> tuple[ClaimDisposition, ...]`. The prepare path consumes the current writer-owned authenticated diagnostic or typed locator-ambiguity refusal, distinguishes other diagnostics and persists a held coverage change before refusing an ambiguous source. No caller-supplied assertion can create or settle a coverage hold. Extend `JournalChange` with `coverage: JournalCoverage | None`, with coverage mutually exclusive with disposition and paired settlement. `JournalCoverage` carries private keyed source, stream, locator and incarnation references, a private authenticated prior replay checkpoint when retained, the start and optional verified exclusive end, reason `OVERLAP_UNVERIFIED`, state `held` or `gap`, and the bounded expiry. Keep any replay checkpoint private. A coverage record conveys no ownership. M09 consumes an exact stored `JournalChange` via `RoutingJournal.coverage_changes(after_sequence: int) -> tuple[JournalChange, ...]` and the existing planned `publication_candidate(change: JournalChange) -> PublicationCandidate`. Check exact durable change identity and sequence before candidate creation. M09 can publish held and expired journal-only changes. It does not write a destination or fabricate an ACK.

`RoutingJournal.expire_coverage() -> tuple[JournalChange, ...]` uses the writer's authenticated time and source availability, records an exact same-key gap transition, and releases the replay state atomically. A transient read failure or revoked authority is not proof of retention loss. `RoutingJournal.cursor_for(source_id: UUID, locator: SourceLocator) -> StreamCursor | None` reads the durable accounting cursor. Coverage has its own monotonic journal changes and cannot move that cursor. Current native authority and a freshly authenticated pre-request admission are required before a new source incarnation can become eligible. Check source, locator and incarnation identity at transaction commit. If no affected identity or range can be verified, refuse before reserve and retain only the authorized broader coverage indication with unknown range. Exclude any surface that cannot be contained under amended NA-1.

At the verified native read and journal reserve boundary, retain one private keyed `OVERLAP_UNVERIFIED` coverage record for an unresolved foreground Claude Agent parent/child overlap. Treat authenticated native locator ambiguity as a refusal before reserve with the same keyed coverage hold and timer. Where the approved parent remains readable, treat its overlap diagnostic as a hold at the same boundary. Neither mode may create or update a usage claim for the unsupported span, apply an estimated correction, issue a destination ACK, or advance the affected accounting cursor. Persist only allowlisted coverage metadata. This story supplies journal containment and a coverage receipt for later milestones. Publication, user-facing labels and exports belong downstream.

Apply the existing bounded hold/expiry rule. With a retained source, the affected stream holds at its last verified replay checkpoint, including later ordinary rows on that stream. The backlog spans from that checkpoint through the latest verified observation boundary for the same incarnation. Use half-open bounds when both are known. Use an unknown endpoint when the current boundary cannot be independently verified. A healthy independent stream and an ordinary request before the affected boundary can route under existing authority. Preserve prior claims. Duplicate/restarted reads of the same affected stream leave the existing hold and cursor unchanged. A late child extends the affected interval only when verified against the same stream and incarnation. Otherwise it remains independently unresolved with zero charges and cannot mutate the existing overlap interval. An unrelated diagnostic retains its existing independent hold and reason and cannot clear, relabel or advance the overlap. At expiry or loss of provider retention, use the existing design rule to record a durable coverage gap and retire the expired replay state. A known last verified end bounds the lost interval. An unproven end stays explicitly unknown. Expiry grants no accounting progress for the lost interval. Re-enrollment may resume future work only at a freshly verified native boundary under current authority. Keep the previous gap and previously verified claims. If an affected surface cannot deliver these semantics, keep that surface/configuration out of the qualified matrix.

Use an isolated, allowlisted fixture based on verified retained native producer shape. Rewrite private native paths, provider IDs, prompt/tool text and unrelated identities to synthetic values. Record provenance digest, surface/build and field allowlist, with raw trace private. Exercise the real prepare/reserve path, publicly supported cursor readback and real journal reopen. Do not seed a cursor directly in persistence.

- `test_claude_overlap_holds_affected_cursor_without_claims` proves admitted ordinary prefix progress, dual-locator refusal and readable-parent diagnostic cases, same-stream trailing ordinary held, unrelated diagnostic remains unresolved, and no usage claim or ACK from overlap.
- `test_claude_overlap_restart_retry_and_late_child_preserve_hold` proves both native refusal and readable-parent diagnostic modes preserve one keyed hold across identical retry and reopen, the actual prior accounting cursor and claims, while a verifiably associated late child may extend the backlog but cannot add usage, change owner or advance the cursor.
- `test_claude_overlap_independent_stream_can_reserve` proves a healthy eligible separate stream reaches its own existing project route, records one journal claim, and can advance its own cursor under the same writer. Do not depend on #119 destination delivery.
- `test_claude_overlap_expiry_records_gap_without_advancing_lost_interval` proves both modes handle hold timeout and authenticated provider retention loss, retiring expired replay state into a gap with verified or unknown endpoint, preserve the prior verified claim, and require fresh native admission to resume beyond it. The expired range cannot be charged or silently skipped.
- [ ] Run the four named tests red on literal trunk. Implement the bounded journal changes and run the named tests green with `test_monitor_journal.py`, `test_monitor_scope.py`, `test_monitor_registry.py` and locked lint. Record the exact regression evidence and commit M08b6. Use the existing hosted and source-review delivery gates.

[Independently accepted R3](https://github.com/kburson/aitm/blob/54f2a7f93668d1a5c744be8a8a654a51b073e2cc/.aitm/stories/001/119/plan/2026-11-13-119-qualified-sources-reacceptance-r3.md) · [Independent verdict](https://github.com/kburson/aitm/blob/54f2a7f93668d1a5c744be8a8a654a51b073e2cc/.aitm/stories/001/119/plan/qualified-source-review-r3.md).

## Refine hold

[Independent Refine](plan/claude-overlap-refine-r1.md) held on the unproven ordinary Claude accounting cursor and estimate. The submitted packet also omitted its literal-trunk and amendment references. [Corrected Refine draft](plan/2026-11-14-295-claude-overlap-refine.md) · [Reproduced controls](plan/claude-overlap-preflight.json) · [Proposed carrier qualification](plan/2026-11-14-295-claude-cursor-carrier-proposal.md). JIT awaits a qualifying carrier and accepted Refine.
