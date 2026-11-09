---
kind: draft
slug: aitm-rewrite-brainstorm
title: aitm — Python rewrite of ai-task-manager
created: 2026-11-08T14:52:09Z
updated: 2026-11-08T19:10:12Z
origin: Claude Code brainstorm session 7046edcc-744e-49cf-847a-549bc0ec11ba (ai-task-manager worktree python-rewrite-backlog-state)
attachments:
  - attachments/transcript.md
  - attachments/research-ai-task-manager-survey.md
graduates-to: master epic (aitm product)
---

# Brainstorm record — aitm rewrite

Every decision reached in the 2026-11-08 brainstorm, with who made it.
Tags: **[user]** stated by the user · **[agreed]** proposed by the assistant and accepted · **[call]** assistant's call, not yet confirmed · **[open]** unresolved.
The full conversation is in [`attachments/transcript.md`](attachments/transcript.md); the survey of the old repo is in [`attachments/research-ai-task-manager-survey.md`](attachments/research-ai-task-manager-survey.md).

## Why a rewrite

- **[user]** ai-task-manager is buried under its own weight: stories take too long and hit too many blockers. Epic #2039, planned at 2–3 days, has run over a month with ~100 defects between its stories (#2000–#2171), blocking the real backlog below #2000.
- **[user]** The worst failure: an agent skips or botches a bookkeeping step (receipt, timing log) and a story can't close until someone repairs it. Second worst: an agent decides it can't proceed without fixing a defect elsewhere — a planning and execution failure.
- **[agreed]** Root cause is architectural, not the language: the GitHub issue body is the primary datastore, parsed with regexes over HTML-comment markers, written by many parts of the tool, so every write needs fetch/diff/verify/lock/fence/recovery. The #2169 Close bugs (timing rows erasing a waiver, a copied timing snapshot read as a second log, a projection call missing authority) are all "two facts on one text surface, recognised by shape."
- **[user]** Rewrite in a new repo, `kburson/aitm` (public, MIT, default branch `trunk`), assimilating lessons from the original.

## Language and stack

- **[user]** Use Python heavily, to learn it and demonstrate it. TypeScript considered for the parts where it fits.
- **[agreed]** Python will not make it faster by itself (measured: Node hook ~139 ms, bare Python ~88 ms). Speed comes from fewer processes, local reads, and far fewer guards.
- **[agreed]** Split by product, not by layer: Python for core, state machine, store, CLI, MCP, hooks, GitHub sync, rubric/ML; TypeScript only for the browser story viewer. Shared contract = JSON Schema generated from Pydantic models, TS types generated from it.
- **[agreed]** End users need only `uv`, `git`, `gh`. No Node at runtime; the viewer ships as a prebuilt static site.
- **[call]** Python 3.13, uv workspaces, Pydantic v2, Typer, httpx, pytest, Ruff, scikit-learn (rubric). Keep hook modules import-light; target < 100 ms per hook; never launch hooks through `uv run`.
- **[user]** Learning: agents explain the code and write tutorials from the real project. **[agreed]** Clear over clever code, a short "why this over that" record per library choice, milestone tutorials in `docs/learn/` on trunk. **[call]** Each story retro gets a "Python concepts introduced" section.

## Harnesses

- **[user]** Must run from any frontier-lab harness: Claude Code, Codex, Grok at minimum.
- **[agreed]** The core never depends on a lab SDK and never calls a model; the harness is the agent.
- **[agreed]** Four layers: CLI (universal floor, all enforcement lives here) · optional MCP server over the same functions · shared `SKILL.md` plus thin per-harness shims · one Python hook entrypoint with per-harness envelope translators, contract-tested against recorded real payloads.
- **[agreed]** Hooks are never required for correctness; a missing, untrusted or double-firing hook can't break the workflow.
- **[open]** Whether Grok supports MCP; whether Codex and Grok support custom agent definitions natively.

## Workflow discipline

- **[user]** Parallel stories are allowed (parallel agents, independent stories, separate worktrees) to save calendar time.
- **[user]** Each recorded story may absorb exactly one expansion: one defect or one discovered story. Each parallel story has its own allowance.
- **[agreed]** The spawned item has no allowance of its own; the chain is at most one level deep. If it expands, the parent story has tripped.
- **[user]** A trip means the JIT deep-dive planning failed. Work stops; the story returns to planning to find out what went wrong and get an executable plan.
- **[user]** On a trip the system should decide between scrap-and-restart and refactor-and-improve, and learn from the outcome. ~~**[call]** Initially the agent recommends with evidence and the human approves.~~ *Superseded 2026-11-08: the agent decides; see "Builder-check answers".*
- **[user]** Leaf stories are no larger than 4 agent-hours. Human-effort estimates are not valuable; plan agent engagement.
- **[agreed]** Bookkeeping is never the agent's job: the tool records receipts, timing and events as side effects of commands it runs. A missing record is rebuilt from git and events, never a close blocker.
- **[agreed]** The tool must never be the reason a story can't close.

## Lifecycle and states

- **[user]** Idea = parking lot. Draft = brainstorming, before design. Graduation happens when brainstorming has enough for a story description and a design.
- **[user]** Graduation steps: (1) create the GitHub issue; (2) create the story folder and move the draft; (3) generate the issue body: user story ("As a developer I want…"), scope, metadata (origin, draft path, creation date), dependencies (parent, blocking, blocked by).
- **[user]** Backlog: design is generated, then reviewed at several levels (SAR, SPR, XPR) with ai-peer-review, collateral stored in the story folder. **Backlog exit requires an accepted design** — nothing to refine without knowing what to build. No separate Design state.
- **[user]** Design = what to build. Plan = how to deliver the design.
- **[user]** Refine: design feeds the agent-engagement estimate, size, original estimate, priority.
- **[user]** Plan: plan generated from the design, multi-level review until accepted, no human review; epic/story estimates revised.
- **[user]** JIT deep-dive: accepts the plan if fresh, or revises it against the current code; estimates revised; then ready for Develop. **[call]** It sits just before Develop.
- **[user]** Keep the three-part state object: entry guards, resident actions, exit guards.
- **[agreed]** Guards are fast local checks (files + index, no network, no markdown parsing). Resident actions are idempotent; the GitHub projection is the resident action on state entry — that is the sparse sync cadence.
- **[user]** ai-peer-review needs a refactor so each review session writes to a caller-chosen location. **[call]** SAR = single-agent review, SPR = same-provider peer review, XPR = cross-provider review.
- **[user] (2026-11-08)** SAR confirmed: a model and effort level from the current provider run a multi-phase review, iterating review/revise until nothing is left to revise. No broker or cross-provider conduit (SPR doesn't need them either). SAR exists so all review collateral has one format: reviewer and author responses follow the same format and frontmatter rules, and every revision gets a diff file.
- **[user] (2026-11-08)** The ai-peer-review refactor records a patch file of the file under review for every author turn that revises it. Patches are numbered by turn and committed with the review record, so every revision from the base can be rebuilt and compared with the notes, and the record survives squash merges. Details and open items are in the peer-review draft.
- **[user] (2026-11-08)** The review levels apply to spec and plan files, and can also apply to the JIT deep-dive, provided it lives as a file in the story folder and the issue only links to it. Drafts need no review. Review depth for the master design and master plan was left to investigation; the recommendation is in the peer-review draft.
- **[user] (2026-11-08)** With per-turn patches, a review record is the final FUR plus patches 000…N, a portable collection; nothing needs pre-committing. Until the refactor ships, reviews run on a temporary branch off the planning branch, and the final collateral is copied into planning safely. Each later level refreshes from planning first, so an interrupted cycle loses nothing.
- **[agreed]** The review → revise loop that runs until the reviewer is exhausted is called an **iterative review**.

## Human role

- **[user]** One sign-off, after delivery (Review → Done). Designs and plans are archival; the user relies on agent peer review rather than reading them. *Refined 2026-11-08: that sign-off is the agent's, not the human's; see "Builder-check answers".*
- **[user]** The user watches through the story viewer (progress, time, costs, bumps) and intervenes when the direction looks wrong; pivots happen there.
- **[agreed]** Pivots are recorded events. A scope-changing pivot returns the story to Plan but is recorded as a human pivot, not charged to the agent's planning.
- **[user]** On Review entry the agent writes a retrospective (design/plan/implementation alignment, what went well, what should have been planned better, lessons, confidence vote) attached to the story. Conversations about the story are user-initiated in any harness, using the viewer and sign-off docs as context. **[agreed]** `aitm review` produces the retro itself. **[call]** The confidence vote is advisory. *Refined 2026-11-08: the retro is written on leaving Review (after the PR review passes), by `aitm signoff`.*

## Specialized agents

- **[user]** Investigate specialized design and plan agents, including codebase and industry research.
- **[agreed]** Three roles: researcher (read-only, cheaper model), planner (writes only to the story's `design/` and `plan/`), independent plan reviewer. Each defined once in a harness-neutral form, generated as native agents where supported, falling back to skills. They use the superpowers skills rather than replacing them. The plan has a fixed output schema (leaf ≤ 4 h, touched files, risks, likely defect areas). Industry research is opt-in for epics.

## Data store

- **[user]** Local, git-committed, fast CRUD, no hosted DBMS, travels with the clone; human-accessible through the story viewer.
- **[agreed]** Files in a hidden folder tree are the authority. SQLite is a gitignored, rebuildable index, never committed.
- **[user]** `planning` is a sister branch of `trunk`, both protected (no delete, no rewrite without an explicitly authorised user). **[agreed]** `planning` has no PR requirement; agents push fast-forward commits directly. `planning` is never merged into trunk.
- **[agreed]** One repo, two branches now; store location (remote + branch) is configurable so a separate planning repo later is a config change. Two repos only if planning and code need different visibility.
- **[agreed]** Writes to `planning` use git plumbing (temporary index, `commit-tree`, compare-and-swap `update-ref`) from any worktree; `planning` must never be a checked-out working tree once the core takes over. **[call]** On bind, the story's folder is copied into the worktree's gitignored `.aitm/`; `aitm sync` and every state change commit it back; one writer per story.
- **[user]** Folders must be neither deep nor wide. **[agreed]** `stories/<id // 100, 3 digits>/<id>/`: at most 100 entries per folder, fixed depth, path computable from the ID alone.
- **[user]** Drafts in `.aitm/drafts/`, deletable if discarded before graduation, indexed by timestamp and description. **[agreed]** Timestamp + slug folder names (a shared counter collides under parallel work), grouped by month. Discarding appends a line to `drafts/discarded.jsonl`.
- **[user]** Ideas and drafts are mineable during any planning session. **[agreed]** The index covers ideas and drafts; stories record their `origin`.
- **[user]** Design and plan documents and all review collateral live in `.aitm/stories/<id>/{design,plan}/`, not on trunk.
- **[user]** Every story data file has frontmatter: story ID (GitHub issue), creation date, last update, last working branch and worktree, estimate, references to related data files. Expansions, trips and discovered work are recorded in frontmatter in a dense, agent-optimised format.
- **[user]** Markers become embedded JSON inside `<details><summary>` blocks. **[agreed]** Those blocks are generated from `events.jsonl` and never parsed back; events are append-only and typed; current state is computed from them.
- **[user]** The story file links to the GitHub issue; the issue links to the story file.
- **[agreed]** Link on GitHub: `blob/planning/.aitm/stories/<bucket>/<id>/story.md` (always latest, never breaks). Snapshot links by SHA stay valid because `planning` is never rewritten. Abandoned stories stay in place with their reason.

## GitHub and providers

- **[agreed]** Projects v2 REST endpoints work on the REST budget, separate from GraphQL (verified live listing fields and items). Use REST wherever possible; GraphQL only where REST can't. REST item-field PATCH is documented by third parties only and not yet verified live.
- **[user]** Abstract both git-origin access and backlog access for GitHub, GitLab, Jira, maybe Bitbucket Cloud; build GitHub only for now. **[agreed]** Two interfaces: git host provider (push/fetch, PRs, CI status, rulesets, file-link URLs) and backlog provider (issues, hierarchy, dependencies, board projection, `init`). Core imports nothing GitHub-specific.

## Packaging

- **[user]** Core plus extensions, each extension eventually its own repo; full install loads and configures all; extensions may depend on each other; all depend on core.
- **[agreed]** Entry-point discovery; meta-package `aitm` = full install; per-repo `.aitm.toml` on trunk **[call]** declares the extensions in use; extensions own their own namespaced files and event types and the core refuses two extensions claiming the same one.
- **[agreed]** Start as a uv-workspace monorepo in `kburson/aitm` with packages published separately from day one; split into separate repos when the extension interface reaches 1.0.
- **[agreed]** Packages: `aitm-core`, `aitm-github`, `aitm-harness`, `aitm-agents`, `aitm-peer-review`, `aitm-viewer`, `aitm-rubric`.

## Viewer

- **[user]** A hosted UI, local and on GitHub Pages, data-rich like the GitHub Project view, plus flow visualisations mined from git history. **[agreed]** A GitHub Action builds JSON from `planning` for Pages; locally it reads the index. Shows progress, time, costs, bumps, design/plan summaries, retros. A "Discuss" button gives `aitm discuss <id>` to run in any harness.

## Estimation and learning

- **[user]** Expand the estimation rubric into a planning and estimation rubric using ML; learn from every committed story — defects after acceptance, expansions past 4 h, discovered work. Deployable as a separate plugin.
- **[agreed]** Reuse the ai-task-manager #1821 design (Refine/Plan/Close record per story, rebuildable index, only complete triads calibrate). Comparable-story retrieval plus quantile regression to start; lessons retrieved into planning. Record tokens/cost alongside time.

## Dogfooding

- **[user]** Dogfooding too early is what blocked ai-task-manager.
- **[agreed]** The core repo runs in advisory mode: record-keeping on, guards report instead of refusing, so the tool can never lock itself out. Enforcement runs in extension repos and the ai-peer-review rewrite, which install released core versions, never live trunk. Core enforcement on its own repo switches on only after it is stable elsewhere.

## Planning structure

- **[user]** A master plan with sub-plans per section (core, viewer, extensions, …).
- **[agreed]** Master epic (#1) holds the architecture design and master plan. Each section is a child epic whose design and plan are written just in time. Only the core graduates now; the other sections stay as drafts until brainstormed.

## Delivery order (proposed)

1. Core (store, state machine, CLI, extension API, provider interfaces) — starter.
2. GitHub extension (backlog + git host provider, projection, `init`) — together with 1 forms the first usable slice.
3. Harness integration (skills, hook translators, optional MCP).
4. Agents (researcher, planner, plan reviewer).
5. ai-peer-review rewrite / output-location refactor.
6. Story viewer.
7. Planning and estimation rubric.
8. History import from ai-task-manager (~2,165 issues).

## Builder-check answers (2026-11-08)

A reviewer read the core design as its builder would and raised eight questions. Five were settled as builder's calls (marked in the core design). The owner answered the other three:

- **[user]** The 4-hour limit covers implementation only: it starts when the story leaves Plan and enters Develop, and ends when the story passes PR review. There are no time limits on planning.
- **[user]** When a story finds a defect or creates a story for discovered work, the original story is blocked and its timer paused. The new defect or story starts a fresh clock with a 4-hour limit. Further work it finds is absorbed inside it up to its limit; otherwise all work stops and the story goes back to planning to work out what went wrong and either fix it or abandon and re-plan.
- **[user]** "Yes" to a fresh expansion allowance and a fresh clock after a trip is decided and a new plan accepted. **[call]** Read as also agreeing to the proposed cap: after a second trip the story returns to Backlog for redesign or a split. To confirm.
- **[user]** A trip is: the 4-hour limit exceeded, or the one expansion slot used and the story still not complete. It requires an immediate stop on all work and a demotion to Plan, where the progress and decisions from plan through develop are examined and a resolution reached: refactor, or abandon and re-plan. **[call]** The agent decides and records an analysis; no human approval.
- **[user]** Agent sign-off happens only on exiting Review into Done, and requires no user interaction: it is the agent's full retrospective on its own work. The owner may later ask about the retro to dig into ideas, but that is never required. A required human step becomes a bottleneck: stories stack up waiting, and fatigue turns sign-off into a rubber stamp.
- **[agreed]** Consequence: there is no required human gate. The only human-only command is `pivot`, so an agent can't relabel a planning failure as a change of direction.

## Installation into a host repo (2026-11-08)

- **[user]** The planning branch is configurable and chosen during installation in the host repo. Its name is a recommendation the user can override, stored in the toml/rc file on the default branch. The suggested default is `planning`, which is distinct from the repo's default branch (`trunk`, `main`, `master`…).
- **[user]** The branch starts from the very base, before anything was committed, so its workspace is clean. **[call]** Implemented as an orphan whose root commit has an empty tree (no shared files, no shared history), marked with an `aitm-planning-root` trailer so `init` and `doctor` can recognise it.
- **[user]** Installation must protect the planning branch. Where the API can't do it, initialization gives the user instructions. **[call]** The git host provider gets `protect_branch` and `default_branch`. GitHub uses the rulesets API first and classic protection as the fallback. `init` never commits to the default branch itself; it writes `.aitm.toml` and `.gitignore` for the user to land through their PR flow.
- **[agreed]** Found 2026-11-08: neither `trunk` nor `planning` on kburson/aitm was protected. **[user]** Protect both. Done 2026-11-08 with rulesets: "aitm: protect trunk" (id 26821811: no deletion, no force-push, PR required with 0 approvals) and "aitm: protect planning" (id 26821812: no deletion, no force-push). **[call]** No bypass actors on either, because agents use the owner's token; an override means an admin editing or disabling the ruleset in Settings → Rules.

## Guarding the planning branch (2026-11-08)

- **[user]** How do we protect the planning branch from an agent merging implementation code into it, a PR targeting it, or a user checking it out to edit directly and leaving it open in a worktree that is implementing story code?
- **[agreed]** Six layers, recorded in the core design ("Guarding the planning branch"):
  1. Unrelated history: verified, GitHub reports "No common ancestor between planning and trunk".
  2. A host ruleset with required linear history.
  3. Git hooks installed by `init`: pre-commit, pre-merge-commit and pre-push checks of the planning invariants.
  4. Harness deny rules.
  5. Core checks: a worktree check on every command; fetch validation that stops writes even in advisory mode; `aitm planning repair` as a fast-forward fix.
  6. A GitHub Action that audits every push.
- **[agreed]** Server-side path restriction is impossible: GitHub's file-path push rules apply repo-wide, not per branch.
- **[user]** Add `required_linear_history` to the live "aitm: protect planning" ruleset (26821812). Done 2026-11-08; active rules on `planning`: deletion, non_fast_forward, required_linear_history.
