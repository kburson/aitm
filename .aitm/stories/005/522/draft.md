---
kind: draft
slug: history-import
title: History import from ai-task-manager
created: 2026-11-08T19:10:12Z
updated: "2026-11-27T05:59:57.455Z"
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: history-import
depends-on: ["aitm-core", "m2-source-access"]
---

# Draft: history import

## Known

- One-time mining of ai-task-manager's ~2,165 issues (bodies, Timing Log comments, markers, commit trails) into story records to seed the rubric corpus.
- Read through REST where possible to spare the GraphQL budget.
- Imported records are marked as imported, with source provenance, and kept apart from native records so calibration can weight or exclude them.

## Open

- Where imported records live (this repo's `planning`, or a separate archive).
- Which fields are trustworthy enough to label (timing logs have known corruption cases).

## Graduation

This draft graduated as [#522](https://github.com/kburson/aitm/issues/522). The [design draft](design/history-import-design.md) records the current handoff and dependency direction.
