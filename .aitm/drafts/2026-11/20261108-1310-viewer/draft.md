---
kind: draft
slug: viewer
title: aitm-viewer — story viewer web app, local and GitHub Pages
created: 2026-11-08T19:10:12Z
updated: 2026-11-11T14:41:24Z
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


## C06 intake from #181

M6 owns the versioned shared view, approved refresh trigger, hosted freshness and readback. Use #228 or #229 for the matching timing scope, #230 for qualified priced evidence, and M2 for board parity. Show direct and descendant Actual, elapsed, owner wait, observed working wall time and independent timing and usage coverage. Preserve the offline fallback and prove pinned replay. Expose only sanitized evidence.

Preliminary integration estimate 3.00 h. Carry this intake into the milestone's own refinement and JIT when it graduates.

[Reviewed requirements](https://github.com/kburson/aitm/blob/20ae85e8e38fd3417e1ec0acd6e4e9f99b5cb22b/.aitm/stories/001/181/plan/2026-11-11-181-slice-c-implementation-plan.md#c06-prove-viewer-and-board-parity) · [Shared qualification evidence](https://github.com/kburson/aitm/blob/c794b1b0be8b7bb67ba7bb1d530fe8a80296f95b/.aitm/stories/002/227/attachments/qualification.md)

[Coverage audit and hosted preview design](attachments/2026-11-11-1-hosted-dashboard-coverage-design.md)
