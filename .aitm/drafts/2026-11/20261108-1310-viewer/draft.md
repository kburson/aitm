---
kind: draft
slug: viewer
title: aitm-viewer — story viewer web app, local and GitHub Pages
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: viewer
package: aitm-viewer
depends-on: [aitm-core]
---

# Draft: aitm-viewer

## Known

- TypeScript web app; types generated from the core's JSON Schema.
- Online: a GitHub Action builds JSON from `planning` and publishes to Pages. Locally: reads the SQLite index for live data while agents work; served by an `aitm` command (no Node at runtime).
- Board view similar to the GitHub Project view, plus story detail: progress, time per state, costs, bumps (defects, discovered work, review rounds, trips), design/plan summaries with full docs a click away, retros and confidence vote.
- Flow views mined from history: cumulative flow, cycle time per state, transition paths including loop-backs.
- "Discuss" gives `aitm discuss <id>` to start a conversation in any harness with a story context packet.

## Open

- Framework choice.
- How "costs" are sourced per harness.
