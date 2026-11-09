---
schema: aitm.doc/v0
story: 1
role: plan
title: aitm master plan
created: 2026-11-08T19:55:00Z
updated: 2026-11-08T19:55:00Z
last-branch: planning
status: draft (awaiting review)
design: ../design/architecture.md
---

# aitm master plan

How the architecture in [`../design/architecture.md`](../design/architecture.md) gets delivered, section by section. Each section is a child epic of #1 with its own design and plan, written just in time when the section comes up. This plan sets order, dependencies, where each section lives, and the checkpoints between sections.

## Rules for every section

- A section graduates from its draft only after its own brainstorm. Its design is written in Backlog, its plan in Plan, and its plan decomposes it into leaf stories of at most 4 agent-hours.
- Leaf stories inside a section may run in parallel when the plan marks them independent.
- Section designs are not written ahead. A section's brainstorm may start once the section it depends on has reached Develop.
- The one-expansion limit and trip rule apply from M1 onward, in advisory mode on the aitm repo.

## Milestones

| # | Milestone | Section epic | Depends on | Outcome |
| --- | --- | --- | --- | --- |
| M0 | Bootstrap | #1 | — | `planning` branch hand-built; #1 and #2 graduated; brainstorm record saved. **Done 2026-11-08.** |
| M1 | Core walking skeleton | #2 aitm-core | M0 | Store, events, plumbing writer, index, state machine, local provider, CLI, extension API, advisory mode. aitm starts recording its own stories with the core; the hand-built layout and the `aitm-planning` checkout are retired. |
| M2 | First usable slice | aitm-github | M1 store + provider interfaces | Graduation creates real issues; board projection on state entry; `init` creates the Project and branch rulesets. aitm's own board runs on it. |
| M3 | Harness integration | aitm-harness | M1 CLI | Claude Code first, then Codex, then Grok: skills, hook translators with recorded-payload contract tests, optional MCP. |
| M4 | Peer review | aitm-peer-review + ai-peer-review | M1, M3 | Review sessions write into story folders; SAR/SPR/XPR recorded as events with the reviewed document's SHA. First **enforcing** consumer repo (ai-peer-review) installs a released core. |
| M5 | Agents | aitm-agents | M3, M4 | Researcher, planner, plan-reviewer roles with context packets and the plan output schema. |
| M6 | Viewer | aitm-viewer | M1 index; M2 for links | Local viewer on the index, then the Pages build from `planning`. |
| M7 | History import | history-import | M1, M2 | ai-task-manager's ~2,165 issues mined into marked, imported records. |
| M8 | Rubric | aitm-rubric | M1, M7 | Comparable-story retrieval and quantile-regression estimates feeding Refine and Plan. |

M2 and M3 can run in parallel once M1's interfaces are stable. M6 can start after M1 and gain links after M2. M7 precedes M8 so the rubric has a corpus on day one.

## Checkpoints

- **Advisory → enforce on the aitm repo:** when the core has run in enforce mode in at least two consumer repos for 20 stories combined with no tool-caused block. Recorded as an event on #1.
- **Repo split:** when the extension API reaches 1.0, each extension moves to its own repo with history preserved.
- **Release cadence:** every package publishes 0.x releases from M1. Consumer repos pin released versions, never trunk.

## Package naming

`aitm` is already taken on PyPI by an unrelated project (aitm.combostrap.com). `aitm-core`, `aitm-github`, `aitm-harness`, `aitm-agents`, `aitm-viewer`, `aitm-rubric` and `aitm-peer-review` were free on 2026-11-08. The full-install meta-package needs another name; the CLI command can stay `aitm`.

## Retiring the hand-built layout

The local clone is one repository with several worktrees, collected under `/Users/kpburson/projects/aitm-workspace/` (moved there 2026-11-08):

```
aitm-workspace/
  trunk/      main worktree (holds .git), always on trunk
  planning/   linked worktree on planning (hand-built phase only)
  review/     temporary review worktrees, review/<story>-<doc>-<level>
```

Until M1 ships, `planning` is edited through a normal checkout at `/Users/kpburson/projects/aitm-workspace/planning`. Before the core's plumbing writer is used for real, that checkout must be removed (`git worktree remove`), because writing to a checked-out branch by moving its ref leaves the checkout out of sync. The first core release includes a migration that validates the hand-built `v0` files and upgrades them to the core's schema.

## Learning track

Each milestone ends with a tutorial in `docs/learn/` on trunk, built from that milestone's real code: M1 Pydantic models, Typer CLIs, git plumbing from Python, SQLite; M2 httpx and REST; M3 subprocess hooks and contract testing; M6 TypeScript and JSON Schema; M8 scikit-learn.
