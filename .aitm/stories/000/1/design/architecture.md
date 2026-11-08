---
schema: aitm.doc/v0
story: 1
role: design
title: aitm architecture
created: 2026-11-08T19:40:00Z
updated: 2026-11-08T19:40:00Z
last-branch: planning
status: draft (awaiting review)
sources:
  - ../draft.md
  - ../attachments/research-ai-task-manager-survey.md
  - ../attachments/transcript.md
---

# aitm architecture

The architecture of aitm, the rewrite of ai-task-manager. Decisions and their origin are recorded in [`../draft.md`](../draft.md); this document arranges them into a system. Section designs (core first) refine each part.

## Intent

aitm binds AI agent work to backlog stories and walks each story from idea to Done. Agents do the work; aitm keeps the record, enforces a small set of rules, and publishes a sparse projection to the backlog service.

The rewrite exists because ai-task-manager made the GitHub issue body its database. Many writers, regex-parsed markers and remote round-trips turned every write into a distributed transaction, and the tool's own defects took over its backlog. aitm makes git the authority and the backlog service a downstream view.

## Goals

1. **The tool is never the reason a story can't close.** Bookkeeping is a side effect of commands; missing records are rebuilt, not repaired by hand.
2. **Planning failures surface immediately.** One expansion per story; a second expansion or a time overrun trips the story back to planning.
3. **Every story teaches the next one.** Outcomes are recorded in a form the planning and estimation rubric can learn from.
4. **Runs from any frontier harness** (Claude Code, Codex, Grok first), with no dependency on any lab's SDK.
5. **Small and learnable.** Clear modern Python the owner can learn from; a core plus independent extensions.
6. **Cheap on remote APIs.** One projection per state change, REST before GraphQL.

## Non-goals

- Human-effort estimation.
- A hosted service or hosted database.
- Recovery machinery for remote state. The backlog service is a projection; a failed sync is re-run.
- Supporting backlog services other than GitHub in the first delivery (interfaces only).

## Anti-goals

- A gate that only a human can unblock because an agent forgot a bookkeeping step.
- Two parts of the tool writing the same fact, or a reader deciding what data is by its shape.
- The tool's own defects forming chains that block product work.
- Extended WIP: stories that never finish while new ones start.

## System overview

```
                 +-------------------------- harness (Claude Code / Codex / Grok) --------------------------+
                 |   agent  --uses-->  skills (SKILL.md)      hooks --> aitm-harness translators            |
                 |      |                                       MCP --> aitm MCP server (optional)          |
                 +------|---------------------------------------------------------------------------------+
                        v
                 aitm CLI (aitm-core)  <-- the universal floor; all enforcement lives here
                        |
      +-----------------+------------------+---------------------+
      v                 v                  v                     v
  state machine     story store        local index        extension registry
  (guards/actions)  (.aitm on planning)  (SQLite, ignored)   (entry points)
                        |                                        |
                        v                                        v
                 git (planning branch)              extensions: github, harness, agents,
                        |                           peer-review, viewer, rubric
                        v                                        |
                 git host provider  <----------------------------+----> backlog provider
                 (push planning, PRs, CI, links)                        (issues, board projection, init)
```

## Branches

| Branch | Holds | Rules |
| --- | --- | --- |
| `trunk` | Implementation code, `.aitm.toml`, `docs/learn/` | No delete, no force-push, PR required |
| `planning` | `.aitm/` story data only | No delete, no force-push, **no PR requirement**; fast-forward only |
| story branches | Code for one story | Normal PR flow into trunk; never carry `.aitm/` (gitignored) |

`planning` is never merged into `trunk`. Its history is never rewritten, so `blob/planning/...` links always resolve to the latest file and SHA links are permanent snapshots. The store location (remote and branch) is configuration, so moving planning data to its own repo later is a config change.

## Data model

Defined in the core design. In outline:

- **Ideas → drafts → stories.** Ideas are single files; drafts are folders; a draft graduates to a story when the backlog provider assigns an issue number, and its folder moves to `.aitm/stories/<id // 100, 3 digits>/<id>/`.
- **Events are the authority.** Each story has an append-only `events.jsonl` of typed, namespaced events. Current state, timing, expansions and trips are computed from it.
- **Markdown is output.** `story.md` and every frontmatter block are generated. `<details>` JSON blocks are generated views and are never parsed back.
- **One writer per file.** No two writers share a file, including across extensions and across parallel agents.
- **The SQLite index is a cache**, rebuilt from `planning` whenever it is missing or stale.

## Lifecycle

| State | Work in the state | Leaves when |
| --- | --- | --- |
| Backlog | Graduation (issue, folder, body); design written and peer-reviewed | Design accepted |
| Refine | Design → agent-hour estimate, size, priority | Estimated; leaf ≤ 4 h or split |
| Ready for Plan | Queue | Not blocked |
| Plan | Implementation plan written and peer-reviewed; estimates revised; JIT deep-dive at pickup | Plan accepted; JIT recorded against current trunk |
| Develop | Implementation | Story commits present |
| Test | Tool-run verification | Passing receipt for current head |
| Review | Agent sign-off with retrospective | Retro present; human sign-off |
| Done | Disposition: delivered, abandoned, superseded, duplicate | — |

Backward moves: trip or human pivot → Plan; rework → Develop; design rework → Backlog. Abandoning moves to Done with a disposition and reason; the record stays in place.

Each state is `{ entry guards, resident actions, exit guards }`. Guards are fast local checks over the store and index — no network, no markdown parsing. Resident actions are idempotent and never refuse; the backlog projection is the resident action on state entry, which makes sync sparse by construction. The deep work (designing, planning, coding, reviewing) is done by agents while a story sits in a state; it is not part of the state object.

## Workflow rules

- Parallel stories are allowed, one agent and one worktree each, chosen as independent at planning time.
- Each story may absorb one expansion: a defect or a discovered story. The expansion has no allowance of its own.
- A second expansion, an expansion that expands, or a leaf exceeding the time limit trips the originating story back to Plan. Plan cannot be left until the trip is decided (scrap-and-restart or refactor-and-improve, with rationale) and a new plan is accepted.
- Human pivots are recorded separately from trips so planning isn't blamed for a change of direction.
- The only required human gate is sign-off after delivery.

## Enforcement modes

- **enforce:** a failing guard refuses the transition.
- **advisory:** a failing guard is recorded as an event and reported; the transition proceeds.

The aitm repo itself runs advisory until the core has been stable in enforcing consumer repos (extensions, the ai-peer-review rewrite), which install released versions of the core.

## Providers

Two interfaces, kept apart because one service can fill one role without the other:

- **Git host provider:** push and fetch `planning` and story branches, PRs, CI status, branch rulesets, file and commit URLs.
- **Backlog provider:** issues, parent/child and dependency links, board projection, `init`.

GitHub implements both first, REST before GraphQL. GitLab, Jira and Bitbucket Cloud are later extensions. The core imports nothing provider-specific; a local backlog provider exists for tests and offline use.

## Harness integration

- **CLI:** works in any harness that runs shell commands. Every command supports `--json`.
- **Skills:** one shared `SKILL.md` plus a thin shim per harness.
- **Hooks:** one Python entrypoint with per-harness envelope translators, contract-tested against recorded real payloads. Hooks record and warn; they are never required for correctness.
- **MCP:** optional server exposing the same functions as typed tools.
- **Agents:** researcher, planner and plan reviewer defined once, generated natively where the harness supports custom agents, skills elsewhere.

## Packages

| Package | Contents | Depends on |
| --- | --- | --- |
| `aitm-core` | store, index, state machine, rules, CLI, extension API, provider interfaces, local provider | — |
| `aitm-github` | GitHub backlog and git-host providers, board projection, `init` | core |
| `aitm-harness` | skills, hook translators, MCP server | core |
| `aitm-agents` | role definitions and context packets | core, harness |
| `aitm-peer-review` | bridge to ai-peer-review | core |
| `aitm-viewer` | TypeScript viewer build, local serve command, Pages workflow | core |
| `aitm-rubric` | planning and estimation rubric, ML | core |
| `aitm` | meta-package: full install | all |

Extensions are discovered through Python entry points, own namespaced event types and file paths, and may add guards, actions, CLI commands, providers, skills, hooks and MCP tools. The core refuses to load two extensions that claim the same event type or path. A repo declares its extensions in `.aitm.toml` on trunk.

All packages start in one uv-workspace repo, `kburson/aitm`, published separately from day one, and split into separate repos once the extension API reaches 1.0.

## Stack

Python 3.13, uv, Pydantic v2, Typer, httpx, pytest, Ruff, scikit-learn (rubric only). TypeScript for the viewer only, with types generated from the core's JSON Schema. Users need `uv`, `git` and `gh`; no Node at runtime.

## Human role

The owner watches through the viewer (progress, time, cost, bumps), intervenes when direction looks wrong, and signs off after delivery. Designs and plans are archival and reviewed by agents. On entering Review the agent writes a retrospective (alignment, what went well, planning misses, lessons, advisory confidence vote); the owner can start a conversation about any story in any harness with `aitm discuss <id>`.

## Learning

Code is written to be read and taught from. Each library choice gets a short "why this over that" record. Milestone tutorials built from the real code live in `docs/learn/` on trunk; each retro lists the Python concepts the story introduced.

## Open at the architecture level

- Whether human edits on GitHub are imported or overwritten (GitHub extension design).
- Grok MCP support; Codex and Grok custom-agent support (harness and agents designs).
- Confirmation of SAR / SPR / XPR definitions (peer-review design).
