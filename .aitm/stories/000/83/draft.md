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
2. Record the agent's active work scope using a stable draft or issue ID and a phase. Phases cover brainstorming, design, planning and document review, development, testing, source review and delivery, and housekeeping. The agent or workflow records changes before beginning the next unit of work. Draft graduation links the draft ID to the permanent issue. See [attribution across the lifecycle](#attribution-across-the-lifecycle).
3. Save normalized usage and coverage to a durable project-local ledger. The proposed implementation is a single-writer SQLite database outside the Git checkout, with a versioned, sanitized JSONL export. Keep prompt and transcript content in the provider's local files. Advance the source checkpoint in the same transaction as its imported usage. Re-reading a Codex cumulative snapshot or a Claude request's streamed updates must preserve one count of each underlying observation. Keep late corrections and ambiguous boundaries auditable.
4. Record three separate measures. Price supported model-token categories against a dated API rate card for Buy a Feature. Record subscription snapshots by provider, account alias and reset window, with freshness and precision. Record actual spend only from attributable billing evidence. Let provider or version gaps show as Unknown. The collector runs without model calls, and its health does not drive Core workflow guards.

## Attribution across the lifecycle

**Backlog hydration and planning.** One agent can hydrate an epic, populate its children, and refine and plan them in one chat and worktree. Their planning and tracking artifacts live on the shared `planning` branch. The epic is the work scope for decomposition and batch work across its children. Before focused refinement, planning or review for a particular child, the agent or workflow records that child and phase as the active scope. When that focused work ends, it can return to the epic scope. Bootstrap can use an explicit scope marker emitted by the agent. Later workflow operations can supply the same marker automatically. The maintainer can stay in the same chat.

**Attribution boundaries.** Apply a scope change at a known model request or turn boundary. If one measured request serves several children as part of a known epic-wide batch, record it once directly against the epic. If the collector cannot determine the scope, preserve the usage for later assignment. A feature total includes direct epic work and each unique descendant's direct work. A document review can carry the same scope into distinct author and reviewer bindings, with usage recorded separately for each participant.

**Development and delivery.** When a story enters Develop, give its owner a fresh story worktree. Bind that worktree, its owner and the development attempt to the story through delivery. This gives implementation, verification and delivery work a stable default scope while other agents work in parallel. Housekeeping inside that scope can inherit the story with its own phase. Later housekeeping can reopen an explicit story or epic scope when it is related, and project-wide upkeep can use a separate project scope.

## First slice and proof

Use a Mac-local service that can start ahead of the first authorized Core delivery work. A per-user LaunchAgent is the proposed activation mechanism. Select the smallest reliable sources for the Codex and Claude Code routes already used in #73. Treat unsupported cloud or remote sources and gaps in retained logs as explicit coverage boundaries.

Dogfood one planning session that hydrates an epic with at least two children and then refines and plans them individually in the same worktree. Verify direct epic usage, distinct child scopes, and an inclusive rollup with each observation counted once. Exercise overlapping review participants and authorized development and housekeeping activity, including the binding when Develop creates the story worktree. Show that the ledger preserves an ambiguous observation for later assignment and restarts or replays without duplicating usage. Verify automatic startup and catch-up, then produce a sanitized export that can later map into C44 with the same source identities. Preserve feature rollups by counting each unique descendant and the feature's own work once.

The first delivery is collection, storage and verification. The backlog viewer, GitHub presentation, forecast calibration and policy for reporting shared overhead can be decided after we have recorded data. This is a P1 proposal for bootstrap adoption alongside Core's existing plan.
