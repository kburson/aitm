---
kind: draft
slug: core
title: aitm-core — story store, state machine, CLI, extension API
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: core
package: aitm-core
---

# Draft: aitm-core

The starter section. Brainstormed enough to graduate (see the master brainstorm record).

## What it is

The Python package every other part depends on: the `.aitm/` story store on the `planning` branch, the local index, the state machine (entry guards, resident actions, exit guards), the expansion limit and trip rule, advisory/enforce modes, the `aitm` CLI, the extension API, and the git-host and backlog provider interfaces (interfaces only; GitHub lives in `aitm-github`).

## Decisions carried from the brainstorm

See the master record sections: Workflow discipline, Lifecycle and states, Data store, GitHub and providers (interfaces), Packaging, Dogfooding.

## Open going into design

- Exact event types and frontmatter schema.
- Backward transitions and what triggers each.
- How engaged time is measured without the harness extension.
- How the core assigns an issue number with no backlog provider installed (local provider).
