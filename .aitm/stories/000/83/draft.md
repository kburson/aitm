---
kind: draft
slug: always-on-aitm-usage
story: 83
title: Always-on usage capture for Core dogfooding
status: brainstorming proposal
related: [2, 51, 73]
---

# Always-on usage capture for Core dogfooding

Core should begin accumulating evidence while we are still brainstorming, planning, reviewing, building and maintaining it. Start with a standalone collector on the Mac running Codex and Claude Code. It should work during bootstrap and later feed the accepted Core usage-ingestion seam. [Core #2](../2/story.md) · [C44 / #51](../51/story.md) · [Measurement spike #73](../73/attachments/report.md)

## Proposed workflow

1. A local service starts at login and reads supported usage records for this repository and its registered worktrees or explicitly bound sessions. It catches up after sleep or restart. A small local status command reports whether it is running, which sources it has read, capture lag, and any missing coverage.
2. Bind an agent's work to a stable draft or issue ID and a phase. Phases cover brainstorming, design, planning and document review, development, testing, source review and delivery, and housekeeping. A dedicated worktree with one confirmed item can supply the default. A mixed chat records an explicit task switch, effective at a known turn or request boundary. Keep ambiguous and repo-wide work separately assignable. A review launch carries the same item and review ID into separate author and reviewer bindings. Draft graduation links the old ID to the permanent issue so the rollup includes earlier work once.
3. Save normalized usage and coverage to a durable project-local ledger. The proposed implementation is a single-writer SQLite database outside the Git checkout, with a versioned, sanitized JSONL export. Keep prompt and transcript content in the provider's local files. Advance the source checkpoint in the same transaction as its imported usage. Re-reading a Codex cumulative snapshot or a Claude request's streamed updates must preserve one count of each underlying observation. Keep late corrections and ambiguous boundaries auditable.
4. Record three separate measures. Price supported model-token categories against a dated API rate card for Buy a Feature. Record subscription snapshots by provider, account alias and reset window, with freshness and precision. Record actual spend only from attributable billing evidence. Let provider or version gaps show as Unknown. The collector runs without model calls, and its health does not drive Core workflow guards.

## First slice and proof

Use a Mac-local service that can start ahead of the first authorized Core delivery work. A per-user LaunchAgent is the proposed activation mechanism. Select the smallest reliable sources for the Codex and Claude Code routes already used in #73. Treat unsupported cloud or remote sources and gaps in retained logs as explicit coverage boundaries.

Dogfood a live planning session, overlapping review participants and authorized development and housekeeping activity. Show that the ledger links observations to the right item and phase, preserves an ambiguous observation for later assignment, and restarts or replays without duplicating usage. Verify automatic startup and catch-up, then produce a sanitized export that can later map into C44 with the same source identities. Preserve feature rollups by counting each unique descendant and the feature's own work once.

The first delivery is collection, storage and verification. The backlog viewer, GitHub presentation, forecast calibration and policy for reporting shared overhead can be decided after we have recorded data. This is a P1 proposal for bootstrap adoption alongside Core's existing plan.
