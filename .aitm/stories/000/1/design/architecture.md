---
schema: aitm.doc/v0
story: 1
role: design
title: aitm architecture
created: 2026-11-08T19:40:00Z
updated: 2026-11-09T03:59:30Z
last-branch: review/1-architecture-xpr
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

1. **The tool is never the reason a story can't close.** Commands capture their own evidence; missing bookkeeping is reconstructed from retained proof or verification is rerun automatically. Unobserved work is never fabricated as passing evidence or exact timing. A genuinely failing test or undelivered change remains a substantive condition, not a bookkeeping failure.
2. **Planning failures surface when detected.** One expansion per attempt and a four-hour implementation limit, with the trip policy and its remaining interpretation described below.
3. **Every story teaches the next one.** Outcomes are recorded in a form the planning and estimation rubric can learn from.
4. **Runs from any frontier harness** (Claude Code, Codex, Grok first), with no dependency on any lab's SDK.
5. **Small and learnable.** Clear modern Python the owner can learn from; a core plus independent extensions.
6. **Cheap on remote APIs.** One projection per state change, REST before GraphQL.

## Non-goals

- Human-effort estimation.
- A new hosted backend service or hosted database. A static hosted viewer is in scope.
- A recovery framework for reconstructible backlog projections. Graduation's remote identity creation is a distinct operation whose uncertain result must be reconciled.
- Supporting backlog services other than GitHub in the first delivery (interfaces only).

## Anti-goals

- A gate that only a human can unblock because an agent forgot a bookkeeping step.
- Two parts of the tool writing the same fact, or a reader deciding what data is by its shape.
- The tool's own defects forming chains that block product work.
- Extended WIP: stories that never finish while new ones start.
- A required human gate in the routine flow: work stacks up behind it and sign-off decays into a rubber stamp.

## System overview

```
                 +-------------------------- harness (Claude Code / Codex / Grok) --------------------------+
                 |   agent  --uses-->  skills (SKILL.md)      hooks --> aitm-harness translators            |
                 |      |                                       MCP --> aitm MCP server (optional)          |
                 +------|---------------------------------------------------------------------------------+
                        v
                 aitm CLI (aitm-core)  <-- universal floor; authoritative workflow rules
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

The core never calls a model, through a lab SDK or any other transport. The harness agent reasons, researches and makes decisions, then records them through core commands. CLI and optional MCP expose the same core functions; external git protections and optional deny hooks add backstops around them.

## Branches

| Branch | Holds | Rules |
| --- | --- | --- |
| default branch (`trunk` here; `main`, `master`… elsewhere) | Implementation code, `.aitm.toml`, `docs/learn/` | No delete, no force-push, PR required |
| planning branch (suggested name `planning`, chosen at init) | `.aitm/` story data only | No delete, no force-push, **no PR requirement**; fast-forward only |
| story branches | Code for one story | Normal PR flow into trunk; never carry `.aitm/` (gitignored) |

When `aitm init` installs aitm into a host repo, it detects the default branch and suggests `planning` as the planning branch name; the user can choose another name, but it must differ from the default branch. The choice is stored in `.aitm.toml` on the default branch. The planning branch is an orphan whose root commit has an empty tree, so it shares no files or history with the default branch. `init` protects it through the git host's API, or prints step-by-step instructions where the API can't (no admin rights, plan limits, no API).

Workflow policy comes from the configured default branch's committed `.aitm.toml`, read locally from its fetched ref, rather than a story worktree's editable copy. Story-branch changes to enforcement mode, limits, enabled extensions or test commands take effect only after delivery to the default branch. Each transition records the effective policy revision and settings needed to explain its guards. The core design owns bootstrap before the first config lands, ref selection and freshness/offline behavior; these must not silently substitute an agent-edited policy for the authoritative one.

The planning branch must never receive implementation code. Six layers guard it, detailed in the core design ("Guarding the planning branch"):
1. Unrelated history: GitHub can't open a PR between it and trunk.
2. A host ruleset requiring linear history.
3. Git hooks installed by `init` that refuse commits on a checked-out planning branch and pushes that break the planning rules.
4. Harness hooks that deny agents' checkout, PR and merge commands.
5. Core checks that refuse writes while the branch is checked out anywhere and stop on a damaged remote, in either enforcement mode. `aitm planning repair` can restore valid current files with a forward commit; it cannot remove shared ancestry introduced by a bad merge. Recovery of history isolation would require an explicitly authorized owner intervention; the tool must not rewrite history automatically.
6. A GitHub Action that audits every push, including pushes from other clones. This is the agreed intent; its trigger and location remain unresolved under the `.aitm/`-only planning policy.

**GitHub section design obligation:** a normal push workflow is read from `.github/workflows` at the event's associated ref, so a workflow only on trunk does not implement every-push auditing of the isolated planning branch. The GitHub design must reconcile these constraints before claiming this layer works. This architecture does not authorize adding workflow code to planning or substituting polling for every-push coverage. See [GitHub workflow triggers](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows#workflow-triggers).

`planning` is never merged into `trunk`. Its history is never rewritten, so `blob/planning/...` links always resolve to the latest file and SHA links are permanent snapshots. The store location (remote and branch) is configuration, so moving planning data to its own repo later is a config change.

## Data model

Defined in the core design. In outline:

- **Ideas → drafts → stories.** Ideas are single files; drafts are folders; a draft graduates to a story when the backlog provider assigns an issue number, and its folder moves to `.aitm/stories/<id // 100, 3 digits>/<id>/`.
- **Events govern workflow state.** Each story has an append-only `events.jsonl` of typed, namespaced events. Current state, recorded timing, expansions and trips are computed from it.
- **Authored content survives regeneration.** Design, plan, draft and retrospective bodies and portable review collateral are authored records. `story.md`, machine-owned frontmatter and `<details>` JSON blocks are generated views; generated views are never parsed back as workflow authority. Metadata ownership does not authorize overwriting an author's body.
- **One owning writer per persisted surface.** The core append API owns event files; agents, extensions and other producers submit events through it. Authored files have one assigned writer, and extensions own declared paths. The core must define cross-process and cross-clone ordering, serialization, and conflict detection without losing events or silently overwriting authored content. The core design's current multiple-writer/event-union proposal is not accepted as an exception; the later core review must show it satisfies single-owner ordering through the append API or replace it.
- **The SQLite index is a cache**, rebuilt from `planning` whenever it is missing or stale.

## Lifecycle

The table describes the normal executable leaf flow. Epics aggregate child progress and do not need their own implementation clock, implementation commits, test receipt or PR. Spikes and other kinds have appropriate deliverables. The core design proposes detailed kind-specific guards; those builder calls still need its own review.

| State | Work in the state | Leaves when |
| --- | --- | --- |
| Backlog | Graduation (issue, folder, body); design written and peer-reviewed | Design accepted |
| Refine | Design → agent-hour estimate, size, priority | Estimated; leaf ≤ 4 h or split |
| Ready for Plan | Queue | Not blocked |
| Plan | Implementation plan written and peer-reviewed; estimates revised; JIT deep-dive at pickup | Plan accepted for its current content; JIT applicable to current code |
| Develop | Implementation (implementation clock starts) | Story commits present; expansion, if any, done |
| Test | Tool-run verification | Passing receipt for current head |
| Review | PR review (clock stops when it passes); delivery; agent sign-off with retrospective | Review passed for the delivered version; delivery and agent sign-off recorded |
| Done | Disposition: delivered, abandoned, superseded, duplicate | — |

Backward moves: trip or human pivot → Plan; rework → Develop; design rework → Backlog. Abandoning moves to Done with a disposition and reason; the record stays in place.

Each state is `{ entry guards, resident actions, exit guards }`. Guards are fast local checks over the store and index — no network, no markdown parsing. Resident actions are idempotent and never refuse; the backlog projection is the resident action on state entry, which makes sync sparse by construction. The durable local store commit establishes the transition. Push and projection are separate retryable results: their failure neither rolls that transition back nor claims that remote publication succeeded. The deep work (designing, planning, coding, reviewing) is done by agents while a story sits in a state; it is not part of the state object.

JIT freshness means the plan still applies to current code, not necessarily that trunk's SHA is unchanged. The core proposes checking intervening changes against declared touched paths; its exact freshness contract remains part of core review. On the delivered path, core records authoritative delivery evidence supplied through the relevant provider or deliverable mechanism before sign-off completes Done. Passing review alone is not delivery. Provider mechanics and merge strategy belong to section design; delivery does not extend the agreed clock beyond passing PR review.

The delivered version is the reviewed source head or deliverable that the delivery mechanism verifies as landed at the declared target. Evidence must bind that reviewed source to its delivery result, including the target commit where applicable; source and target SHAs need not match after squash or rebase. An issue's closed state alone is not delivery proof. Core must also provide verifiable delivery evidence for core-only and offline operation, including local delivery targets; an unverifiable remote target remains pending rather than being reported delivered. The core and provider designs choose the mechanism and checks that prevent unreviewed changes from being attributed to the reviewed version.

## Review contract

An iterative review repeats review and revision until the reviewer has no required changes. SAR uses a chosen model and effort from the current provider; SPR uses a distinct reviewer session in that provider; XPR uses another provider. All levels use common reviewer/author response formats and retain a numbered patch for every author revision in the story's design or plan review folder. The final file, patches and manifest form a self-contained portable record: acceptance and reconstruction cannot depend on retaining intermediate review commits or pre-committing the FUR. Caller-chosen output keeps the record with the story.

Acceptance names the reviewed authored-content version and its review record. Core and peer-review designs must define one versioned canonical digest covering the authored body and semantically authored header fields, excluding only schema-defined generated metadata. Regenerating machine-owned metadata never invalidates that acceptance; any change to authored content requires renewed acceptance. This preserves the owner's required frontmatter in story data files. Exact full-file digests and patches remain in review records for byte-for-byte reconstruction, separately from the canonical acceptance digest. A historical acceptance cannot approve different authored content. The review-depth matrix for master, section, leaf and JIT files remains a recommendation pending confirmation. JIT can be reviewed when stored as a story-local file; issues link to it rather than carrying its content. Drafts need no review.

Until the M4 refactor ships, follow the [interim procedure](../../../../drafts/2026-11/20261108-1310-peer-review/draft.md#interim-review-procedure-until-the-ai-peer-review-refactor-ships): review on a temporary branch/worktree from planning, then import only the final FUR and collateral into planning with a fast-forward commit. The current base-from-empty `patch-000` representation is a recorded builder call used by that procedure, not a new owner policy. The future record-only interface must preserve the owner's no-precommit contract.

The planning checkout is only the pre-M1 import route. M1 must provide import of the revised FUR and review folder through the core's compare-and-swap plumbing writer, restricted to that story's paths, before retiring the checkout. The M1-to-M4 interim procedure uses that writer instead of recreating or committing in a planning checkout. A temporary review branch derived from planning is a different ref, not the configured planning branch checked out; git, harness and core guards must permit this review workflow while continuing to protect the planning ref. Current hand-built review records bind exact full-file bytes, so their accepted snapshots remain unchanged. M1 migration must preserve those snapshots and establish their authored-content binding under the shared canonicalization contract before generated metadata is rewritten; it must not label an arbitrary later file accepted.

## Workflow rules

- Parallel stories are allowed, one agent and one worktree each, chosen as independent at planning time.
- Only implementation is time-limited. Each attempt at a story gets 4 engaged agent-hours, counted from entering Develop until the PR review passes. Planning has no time limit.
- Each attempt may absorb one expansion: a defect or a discovered story. The origin is blocked and its clock paused while the expansion runs. The expansion gets its own fresh 4-hour clock and no expansion allowance; work it discovers is absorbed inside it within that limit.
- A trip is a planning failure. The owner's rule covers a time overrun or the one expansion slot used with the story still incomplete. The core's current operational interpretation detects a second/nested expansion request or a timeout. The boundary between continuing already-planned work after an expansion and declaring that attempt unsuccessful remains an open interpretation; neither creating an expansion nor that proposed interpretation silently replaces the owner's rule.
- In enforce mode, a detected trip stops work on the origin and expansion and returns them to planning. The agent analyses the attempt and decides refactor or scrap-and-re-plan, with rationale, without human approval; a new plan must be accepted before Develop. The next attempt gets a fresh clock and allowance. Returning to Backlog after a second trip is an **unconfirmed call**, not a settled cap. Advisory trip behavior is described below.
- Human pivots are recorded separately from trips so planning isn't blamed for a change of direction. `pivot` is human-only; an agent cannot relabel its planning failure as a human change of direction.
- There is no required human gate. Sign-off is the agent's retrospective on its own work, recorded on leaving Review. The owner may discuss any retro later; making that a gate would stack work up and turn sign-off into a rubber stamp.

## Enforcement modes

- **enforce:** a failing workflow guard refuses the transition; detected trips stop the affected work and demote it as described above.
- **advisory:** a failing workflow guard is recorded and reported; the transition proceeds. Trips are recorded and reported without automatically stopping sessions or moving stories.

Store-integrity failures stop unsafe writes in both modes. Advisory mode relaxes workflow policy, not ownership, safe persistence or planning-branch integrity. Optional hooks may warn, record or deny dangerous operations as a backstop; correctness must not depend on a hook being installed, trusted or firing exactly once.

The CLI observes commands, not arbitrary work outside it. Without hooks, a running story's time/trip checks occur at the next command that touches it, and enforce mode directs the agent to stop immediately once detected. Core and harness designs must define activity coverage, freshness and missing telemetry explicitly. Retained evidence can reconstruct bookkeeping; verification can be rerun automatically. Unobserved time remains unavailable or qualified, never an invented exact duration, and missing proof is not a passing test.

The aitm repo itself runs advisory until the core has been stable in enforcing consumer repos (extensions, the ai-peer-review rewrite), which install released versions of the core.

## Providers

Two interfaces, kept apart because one service can fill one role without the other:

- **Git host provider:** push and fetch `planning` and story branches, PRs, CI status, verified delivery/merge status mapping a reviewed source head to its target result, branch rulesets, file and commit URLs.
- **Backlog provider:** issues, parent/child and dependency links, board projection, and backlog-specific initialization.

Core `init` owns generic configuration, store creation and hook installation, then invokes provider-specific setup and protection capabilities. GitHub implements the remote steps; installing only core must still support local setup.

Graduation is the exception to the backlog's downstream-view role: the provider-created issue supplies the permanent story identity before the draft moves. Core and provider designs must reconcile an uncertain creation result to one identity, including a successful remote creation whose response or local recording was lost; blind retry must not create another story. Projection of an already identified story remains reconstructible and retryable. This contract does not prescribe a distributed transaction framework.

GitHub implements both first, REST before GraphQL. GitLab, Jira and Bitbucket Cloud are later extensions. The core imports nothing provider-specific; a local backlog provider exists for tests and offline use.

## Harness integration

- **CLI:** works in any harness that runs shell commands. Every command supports `--json`.
- **Skills:** one shared `SKILL.md` plus a thin shim per harness.
- **Hooks:** one Python entrypoint with per-harness envelope translators, contract-tested against recorded real payloads. Hooks record, warn and optionally deny unsafe commands as a backstop; they are never required for correctness.
- **MCP:** optional server exposing the same functions as typed tools.
- **Agents:** a read-only researcher, a planner writing only the story's design and plan, and an independent plan reviewer, defined once and generated natively where supported, skills elsewhere. They use the existing superpowers skills. Plans have a fixed output contract including leaves of at most four agent-hours, touched files, risks and likely defect areas. Industry research is opt-in for epics.

## Packages

| Package | Contents | Depends on |
| --- | --- | --- |
| `aitm-core` | store, index, state machine, rules, CLI and generic init, extension API, provider interfaces, local provider | — |
| `aitm-github` | GitHub backlog and git-host providers, board projection, GitHub-specific init steps | core |
| `aitm-harness` | skills, hook translators, MCP server | core |
| `aitm-agents` | role definitions and context packets | core, harness |
| `aitm-peer-review` | ai-peer-review integration and portable story-local review records | core |
| `aitm-viewer` | TypeScript viewer build, local serve command, Pages workflow | core |
| `aitm-rubric` | planning and estimation rubric, ML | core |
| name unresolved | meta-package: full install; the CLI/product name remains `aitm` | all |

Extensions are discovered through Python entry points, own namespaced event types and file paths, and may add guards, actions, CLI commands, providers, skills, hooks and MCP tools. The core refuses to load two extensions that claim the same event type or path. A repo declares its extensions in `.aitm.toml` on trunk. Installing distributions and enabling/configuring extensions are separate steps; the full-install flow must perform both for the complete product. The master plan records the existing `aitm` PyPI name conflict; this document does not select a replacement.

All packages start in one uv-workspace repo, `kburson/aitm`, published separately from day one, and split into separate repos once the extension API reaches 1.0.

## Stack

Python 3.13, uv, Pydantic v2, Typer, httpx, pytest, Ruff, scikit-learn (rubric only). TypeScript for the viewer only, with types generated from the core's JSON Schema. Users need `uv`, `git` and `gh`; no Node at runtime.

## Human role

The owner watches through the viewer (progress, time, cost, bumps) and intervenes with a pivot when direction looks wrong. No routine transition waits on the owner. Designs and plans are archival and reviewed by agents. After passing PR review and recording delivery, the agent signs off with a retrospective on its own work (alignment of design, plan and implementation, what went well, planning misses, lessons, advisory confidence vote) and the story moves to Done. The owner can start a conversation about any story or retro in any harness with `aitm discuss <id>`; it is never required.

The viewer is a prebuilt static site: locally it reads the index; a GitHub Pages build reads generated JSON from planning. It shows progress, flow history, time, costs, bumps, design/plan summaries and retros, with a Discuss action giving a harness command. The viewer design must distinguish a hosted snapshot's freshness from the current local record. Its build has the same workflow-ref constraint described for the planning audit: a workflow only on trunk cannot assume it runs on a planning push. A scheduled, dispatched or other suitable trigger is acceptable for the viewer with disclosed snapshot freshness; the viewer/GitHub designs select it. That flexibility does not weaken the separate every-push audit requirement or allow workflow code on planning.

## Learning

Code is written to be read and taught from. Each library choice gets a short "why this over that" record. Milestone tutorials built from the real code live in `docs/learn/` on trunk; each retro lists the Python concepts the story introduced.

The planning and estimation rubric learns from recorded Refine/Plan/Close estimates and outcomes, including post-acceptance defects, expansions, trips, lessons, and available token/cost telemetry. Core owns the durable events and extension ownership boundaries; harness integrations supply observed activity and usage, and the rubric owns its derived index and models. Only complete triads calibrate estimates; incomplete, imported or unavailable measurements stay identifiable rather than being treated as complete training examples. Comparable-story retrieval and quantile regression are the agreed starting direction, with lessons retrieved into planning. Exact schemas and measurement semantics belong to the core, harness and rubric designs; history import supplies a corpus without weakening those quality rules.

## Open at the architecture level

- Whether human edits on GitHub are imported or overwritten (GitHub extension design).
- Grok MCP support; Codex and Grok custom-agent support (harness and agents designs).
- The operational interpretation of a used expansion slot with the origin still incomplete, and confirmation of the proposed second-trip cap (owner decisions; existing uncertainty preserved).
- How the GitHub every-push audit works while planning contains only story data. Any proposal to relax either requirement needs an owner decision; the GitHub section owns the technical investigation.
- The full-install distribution name (`aitm` is already taken); the CLI name remains `aitm`.
- Whether the peer-review patch refactor is built in the existing JS repo or the Python rewrite at M4, and confirmation of review depth by document, including whether core design review follows this architecture review.

The later core review must reconcile its current calls and omissions with this architecture's single-owner persistence, canonical authored-content acceptance and metadata migration, M1 review import, authoritative configuration, delivery-before-Done (including merge-strategy mappings and core-only evidence), and evidence-recovery contracts. Its proposed root `README.md` allowance also needs reconciliation with the planning data-only policy; no new exception is approved here. This architecture review does not accept or revise the context-only core design or master plan.
