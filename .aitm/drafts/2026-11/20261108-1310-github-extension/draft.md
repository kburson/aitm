---
kind: draft
slug: github-extension
title: aitm-github — GitHub backlog and git-host provider, board projection, init
created: 2026-11-08T19:10:12Z
updated: 2026-11-08T19:10:12Z
origin: .aitm/drafts/2026-11/20261108-0852-aitm-rewrite-brainstorm/draft.md
section: github-extension
package: aitm-github
depends-on: [aitm-core]
---

# Draft: aitm-github

## Known

- Implements both provider interfaces for GitHub: backlog (issues, sub-issues, dependencies, Project v2 board projection, `init`) and git host (push/fetch `planning` and story branches, PRs, CI status, rulesets, blob-link URLs).
- REST wherever possible; GraphQL only where REST can't. Projects v2 REST read endpoints verified live; item-field PATCH not yet verified.
- Projection runs as a resident action on state entry: one sparse sync per state change.
- `init` translates ai-task-manager's `init-project-config.sh`: create/configure the Project, fields (Status, Priority, Size, Estimate, Engaged, Rank, Blocked By, Disposition…), and rulesets protecting `trunk` and `planning` (no delete, no force-push; PRs required on trunk only).
- Implements `protect_branch` for the core's `init`. It uses the rulesets API first (`POST /repos/{owner}/{repo}/rulesets`, target = the configured planning branch name), and classic branch protection if rulesets aren't available. It needs admin permission. On GitHub Free, protection works on public repos but not private ones. When the API can't apply protection, it returns `manual` with click-by-click steps and the repo's `settings/rules` URL. It also reads protection back so `aitm doctor` can check it. Planning branch rules: deletion, non_fast_forward, required_linear_history; no PR rule; no bypass actors.
- Ships a GitHub Action (installed by `init`) that runs on every push to the planning branch, checks the planning invariants (one parent per commit, only `.aitm/` paths plus root README, no history shared with the default branch), and opens an issue on violation. Layer 6 of "Guarding the planning branch" in the core design.
- Issue body is a projection: user story, scope, metadata, dependencies, link to `story.md` on `planning`. Never parsed back for decisions.
- Together with the core it forms the first usable slice.

## Open

- Do human edits on GitHub (board drags, labels, title) get imported on next sync, or overwritten?
- Field set for the new board, and which fields are projections vs human-owned.
- Verify REST item-field PATCH live before relying on it.
