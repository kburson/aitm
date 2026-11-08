---
schema: aitm.doc/v0
story: 2
role: design
title: aitm-core design
created: 2026-11-08T20:05:00Z
updated: 2026-11-08T20:05:00Z
last-branch: planning
status: draft (awaiting review)
parent-design: ../../1/design/architecture.md
sources:
  - ../draft.md
  - ../../1/draft.md
---

# aitm-core design

`aitm-core` is the package every other part of aitm depends on. It owns the story store on the `planning` branch, the local index, the state machine and its rules, the `aitm` CLI, the extension API and the provider interfaces. This document is the full description a builder plans from; the architecture it sits in is [`../../1/design/architecture.md`](../../1/design/architecture.md), and the reasons behind each decision are in [`../../1/draft.md`](../../1/draft.md).

## Intent

ai-task-manager stalled because its records lived in GitHub issue bodies that many parts of the tool wrote and re-parsed, and because bookkeeping was the agent's job. The core fixes both at the root: records are typed files in git with exactly one writer each, current state is computed from an append-only event log, and every command records its own evidence. The core must be small enough to learn Python from and dependable enough that it is never the reason a story can't close.

## Goals

1. Capture ideas, shape drafts, graduate drafts to stories, and walk stories through every state, entirely from the CLI.
2. Record every state change, guard result, expansion, trip, pivot, session and estimate as a typed event, written by the command that caused it.
3. Write to `planning` from any worktree, concurrently, without checking it out and without conflicts.
4. Answer reads (show, list, search, explain) from a local index in well under a second.
5. Enforce the one-expansion limit and the trip rule, in advisory or enforce mode.
6. Let extensions add guards, actions, commands, event types, files and providers without editing the core.

## Non-goals

- Any GitHub-specific code (`aitm-github`).
- Harness skills, hooks and MCP (`aitm-harness`).
- Agent roles, peer review, viewer, rubric.
- Windows support in the first release (macOS and Linux first).
- Multi-user authentication or permissions beyond what git and the backlog service provide.

## Anti-goals

- A command that requires the agent to supply evidence the tool could produce itself.
- A guard that reads markdown, calls the network, or takes more than a few milliseconds.
- Any file written by more than one writer.
- A failure in a downstream projection that leaves the story's own record uncertain.

## Package layout

```
packages/aitm-core/
  pyproject.toml
  src/aitm_core/
    config.py            .aitm.toml loading and validation
    paths.py             ID → path rules (buckets, drafts, ideas)
    models/              Pydantic models: events, frontmatter, story, idea, draft, config
    store/
      backend.py         Backend protocol: read tree, write files, commit
      git_backend.py     planning-branch plumbing implementation
      memory_backend.py  in-memory implementation for unit tests
      workspace.py       materialize a story into a worktree; sync back
      render.py          generate story.md, frontmatter blocks, <details> views
    events.py            append, fold events into current state
    index/               SQLite schema, incremental build, queries, FTS search
    machine/
      states.py          the eight state definitions
      transitions.py     allowed edges, promote/demote algorithm
      guards.py          core guards
      actions.py         core resident actions
    rules/
      expansion.py       one-expansion limit
      trips.py           trip detection and decision
      timing.py          engaged-time computation from events
    providers/
      backlog.py         BacklogProvider protocol
      githost.py         GitHostProvider protocol
      local.py           local backlog provider
    ext/
      api.py             Extension declaration types
      registry.py        entry-point discovery, ownership checks, ordering
    cli/                 Typer app; one module per command group
```

## Configuration: `.aitm.toml` on trunk

```toml
[store]
remote = "origin"
branch = "planning"

[enforcement]
mode = "advisory"            # or "enforce"

[limits]
leaf_agent_hours = 4
expansions_per_story = 1

[providers]
backlog = "local"            # "github" once aitm-github is installed
githost = "none"

[extensions]
enabled = []                 # e.g. ["github", "harness"]

[test]
command = "uv run pytest"    # what `aitm test` runs
```

`aitm init` writes this file, adds `.aitm/` to trunk's `.gitignore`, and creates an orphan `planning` branch with the `.aitm/` README if none exists. Provider extensions extend `init` with their own steps.

## Store layout

As in [`.aitm/README.md`](../../../../README.md), with one change from the hand-built version: there are **no shared append files**. A discarded draft writes its own file, `drafts/discarded/<stamp>-<slug>.json` (title, reason, last SHA, discarded-by, time), instead of a line in a shared `discarded.jsonl`.

```
.aitm/
  ideas/<YYYY-MM>/<YYYYMMDD-HHMM>-<slug>.md
  drafts/<YYYY-MM>/<YYYYMMDD-HHMM>-<slug>/draft.md, attachments/
  drafts/discarded/<YYYYMMDD-HHMM>-<slug>.json
  stories/<bucket>/<id>/
    story.md              generated
    description.md        agent-authored prose (title, user story, scope)
    events.jsonl          append-only authority
    draft.md              the graduated draft
    design/  plan/  retro/  attachments/
```

`<bucket>` is `id // 100` zero-padded to three digits. Slugs are lowercase ASCII, hyphen-separated, at most 40 characters. A second draft or idea with the same stamp and slug gets a two-character suffix.

## Ownership: one writer per file

| File | Writer |
| --- | --- |
| `events.jsonl` | core (and extensions, through the core's append API, with namespaced types) |
| `story.md`, every frontmatter block | core, regenerated from events and `description.md` |
| `description.md` body, `draft.md` body, idea bodies | the agent or human working the story |
| `design/`, `plan/` documents | the agent writing them (later, `aitm-agents`) |
| `design/reviews/`, `plan/reviews/` | the review tool (later, `aitm-peer-review`) |
| `retro/` | the agent, through `aitm review` |
| Extension files | the extension that declared the path |

Frontmatter in markdown files is owned by the core and regenerated on every sync; the body is owned by the file's writer. The core reads frontmatter only from files it wrote, as YAML between `---` delimiters, never by pattern-matching text. JSON and JSONL files carry no frontmatter; their metadata appears in `story.md`'s `files` map.

## Events

Every event is one JSON line:

```json
{"v":1,"id":"01JC...","ts":"2026-11-08T19:24:00.123Z","type":"core.state.changed",
 "story":2,"actor":{"kind":"agent","harness":"claude-code","session":"…","on_behalf_of":"kburson"},
 "data":{"from":"backlog","to":"refine","reason":null,"mode":"advisory"}}
```

- `id` is a ULID (sortable, unique without coordination).
- `ts` is UTC with milliseconds.
- `type` is `<namespace>.<noun>.<verb>`. The core owns `core.*`; each extension owns its own namespace.
- `actor.kind` is `agent`, `human` or `tool`.
- Each event type has a Pydantic model for `data`; unknown types from uninstalled extensions are kept and shown, never dropped.

Core event types:

| Type | Recorded by | Data |
| --- | --- | --- |
| `core.idea.created` | `aitm idea add` | path, tags |
| `core.draft.created` / `core.draft.discarded` | `aitm draft new` / `discard` | path, reason |
| `core.story.graduated` | `aitm graduate` | from draft, issue ref |
| `core.state.changed` | `promote`, `demote`, `abandon` | from, to, reason, mode |
| `core.guard.evaluated` | every transition attempt | state, slot, guard, ok, code, reason, mode |
| `core.action.completed` / `core.action.failed` | resident actions | action, detail |
| `core.session.started` / `core.session.ended` | `bind` / `unbind` | worktree, branch |
| `core.estimate.set` | `aitm estimate` | phase (refine, plan, jit), agent_hours, size, priority |
| `core.doc.accepted` | `aitm design accept`, `aitm plan accept` | role, path, planning SHA, review refs |
| `core.jit.recorded` | `aitm jit` | plan path, trunk SHA, outcome (accepted or revised) |
| `core.expansion.recorded` | `aitm expand` | kind (defect or story), child id, reason |
| `core.trip.recorded` | rules engine | cause (second-expansion, nested-expansion, time-limit), detail |
| `core.trip.decided` | `aitm trip decide` | decision (scrap or refactor), rationale, by |
| `core.pivot.recorded` | `aitm pivot` | by, reason, scope_change |
| `core.test.receipt` | `aitm test` | command, exit code, head SHA, duration, summary |
| `core.retro.added` | `aitm review` | path |
| `core.signoff.recorded` | `aitm signoff` | by, verdict, note |
| `core.link.changed` | `aitm link` | parent, blocking, blocked_by |

**Folding.** `events.fold(events) -> StoryState` is a pure function producing current state, state history, estimates, expansions, trips, accepted docs, sessions and engaged time. Everything else (frontmatter, `story.md`, index rows, guards) reads `StoryState`, never raw text.

## `story.md`

Generated on every sync from `StoryState` and `description.md`:

1. Frontmatter: schema, id, title, kind (story, epic, defect, spike), state, issue URL, parent, children, blocking, blocked-by, created, updated, last-branch, last-worktree, estimate (agent-hours, size), origin, files map, and a dense `expansions` and `trips` list (`[{id: 14, kind: defect, at: plan}]`).
2. Title and a link to the issue.
3. The body of `description.md`.
4. Generated `<details><summary>` blocks with fenced JSON: state history, guard results, expansions and trips, estimates, test receipts. A blank line follows each `</summary>` so GitHub renders the code block.

The renderer is deterministic: the same `StoryState` always produces byte-identical output, so regeneration never creates noise commits.

## The planning backend

`GitBackend` writes to `refs/heads/planning` without a checkout:

1. Read the current ref value `old`.
2. Build a tree from `old`'s tree plus the changed paths, using a temporary index (`GIT_INDEX_FILE`) and `git hash-object -w` / `update-index --cacheinfo`.
3. `git commit-tree` with parent `old`.
4. `git update-ref refs/heads/planning <new> <old>`: compare-and-swap. If the ref moved, rebuild from the new tip and retry (bounded, with jitter).

Because each writer owns disjoint paths, a retry never conflicts: the same path changes are re-applied on top of the new tip.

**Push.** `aitm sync --push` and every state change push `planning` fast-forward. On rejection, fetch, replay local unpushed commits path-by-path onto `origin/planning`, and push again. Pushed commits are never rewritten. Without a git host provider, push is skipped and recorded.

**Reads** use `git show planning:<path>` or `git ls-tree`, batched through `git cat-file --batch` for speed.

**Guard:** the backend refuses to run if `planning` is checked out in any worktree (`git worktree list --porcelain`), and says how to fix it.

`MemoryBackend` implements the same protocol in memory, so unit tests never spawn git.

## Working on a story from a worktree

- `aitm bind <id>` copies the story folder from `planning` into `<worktree>/.aitm/stories/<bucket>/<id>/` (gitignored on trunk), records the base tree SHA in `<worktree>/.aitm/.state/<id>.json`, and records `core.session.started`.
- The agent edits `description.md`, design and plan documents with ordinary file tools.
- `aitm sync` commits files that changed since the base back to `planning`, regenerates `story.md`, and updates the base. If `planning`'s copy of a file changed since the base (it shouldn't, given one writer per story), sync refuses for that file and shows both versions.
- Every state-changing command syncs first.
- `aitm unbind` syncs and records `core.session.ended`.
- Ideas and drafts are written straight to `planning` by their commands; `aitm draft open <slug>` materializes a draft for editing the same way.

## Local index

- Location: `<git-common-dir>/aitm/index.sqlite`, shared by every worktree of the clone, never committed.
- Keyed by the `planning` tree SHA it was built from. On each command the core compares SHAs and updates incrementally by diffing trees; a missing, corrupt or schema-mismatched index is rebuilt from scratch.
- Tables: `stories` (folded state), `events`, `files`, `ideas`, `drafts`, plus an FTS5 table over titles, descriptions, idea and draft bodies, and lessons.
- WAL mode. The index is a cache: if it is locked or broken, commands fall back to reading `planning` directly.

## State machine

```python
@dataclass(frozen=True)
class State:
    id: StateId
    entry_guards: tuple[Guard, ...]
    resident_actions: tuple[Action, ...]
    exit_guards: tuple[Guard, ...]

class Guard(Protocol):
    id: str
    def __call__(self, ctx: GuardContext) -> GuardResult: ...   # ok, code, reason

class Action(Protocol):
    id: str
    def __call__(self, ctx: ActionContext) -> None: ...          # idempotent; never refuses
```

`GuardContext` carries the folded `StoryState`, related stories from the index, config, and a read-only view of the local git repo. Guards may not perform network calls or parse markdown.

**Forward chain:** backlog → refine → ready-for-plan → plan → develop → test → review → done.

**Backward edges:**

| From | To | Trigger |
| --- | --- | --- |
| develop, test, review | plan | trip, or human pivot with scope change |
| test, review | develop | rework |
| refine, ready-for-plan, plan | backlog | design rework |
| any | done | abandon (disposition and reason required) |

**Transition algorithm** (`promote`, `demote`, `abandon`):

1. Sync the bound story folder, if any.
2. Check the edge is allowed.
3. Run the current state's exit guards, then the target's entry guards, in registration order: core guards first, then extensions in load order. Record a `core.guard.evaluated` event for every guard.
4. In enforce mode, any failure refuses: nothing else is written. In advisory mode, failures are reported and the transition continues.
5. Append `core.state.changed`, regenerate `story.md`, commit to `planning`. **This commit is the transition.**
6. Run the target's resident actions. Each records `core.action.completed` or `core.action.failed`. A failed action is retried by the next `aitm sync`; it never undoes the transition.
7. Push `planning` if a git host provider is configured.

Because the transition is committed before any projection runs, a crash or network failure can never leave the story's own record uncertain.

**Core guards:**

| State | Slot | Guard | Passes when |
| --- | --- | --- | --- |
| backlog | exit | `description-complete` | `description.md` has a title, user story and scope (checked via its frontmatter fields set by `aitm describe`, not by reading prose) |
| backlog | exit | `design-accepted` | a `core.doc.accepted` event with role `design` exists |
| refine | exit | `estimated` | a refine-phase estimate with agent-hours, size and priority |
| refine | exit | `leaf-size` | kind is epic, or agent-hours ≤ `leaf_agent_hours` |
| ready-for-plan | exit | `not-blocked` | every `blocked_by` story is done |
| plan | exit | `plan-accepted` | a `core.doc.accepted` event with role `plan`, after the latest trip if any |
| plan | exit | `trip-decided` | every trip has a `core.trip.decided` |
| plan | exit | `jit-current` | a `core.jit.recorded` event exists against the current trunk tip |
| develop | entry | `not-tripped` | no undecided trip |
| develop | exit | `story-commits` | the story branch has at least one commit whose subject carries `[#<id>]` |
| test | exit | `test-passing` | a passing `core.test.receipt` for the current branch head |
| review | exit | `retro-present` | a `core.retro.added` event |
| review | exit | `signed-off` | a `core.signoff.recorded` with verdict `accept` |
| any forward | entry | `children-consistent` | an epic cannot pass a state its open children have not reached; an epic cannot reach done with open children |

`description.md` frontmatter fields (title, has-user-story, has-scope) are written by `aitm describe`, which the agent runs after editing. That keeps the guard on structured data.

**Core resident actions:** on entering any state, `project-to-backlog` calls the configured backlog provider's `project(story_state)` (a no-op for the local provider). On entering done, `close-sessions` ends any open session.

## Expansion and trip rules

- `aitm expand <id> --kind defect|story --title "…" --reason "…"` creates a new story (graduating immediately through the backlog provider) with `expanded_from: <id>`, and records `core.expansion.recorded` on the origin story.
- A story may have at most `expansions_per_story` expansions. A request for one more records `core.trip.recorded` (cause `second-expansion`) on that story. A story with `expanded_from` set has no allowance: any expansion it requests trips its origin story (cause `nested-expansion`).
- `rules.timing` computes engaged agent-hours from session intervals (and, once the harness extension exists, its activity events). When a leaf story's engaged hours exceed `leaf_agent_hours`, the next command touching it records a trip (cause `time-limit`) on the story, or on its origin if it is an expansion.
- In enforce mode, a trip refuses the expansion and moves the tripped story to plan. In advisory mode the trip is recorded and reported, and nothing moves.
- `aitm trip decide <id> --decision scrap|refactor --rationale "…"` records the decision. For **scrap**, the current story branch is left untouched and recorded as an abandoned attempt; the next Develop entry starts a new branch. For **refactor**, the branch is kept.
- `aitm pivot <id> --reason "…" [--scope-change]` records a human pivot. With `--scope-change` it moves the story to plan; it never counts as a trip.

## Providers

```python
class BacklogProvider(Protocol):
    name: str
    def create_issue(self, draft: DraftSnapshot) -> IssueRef: ...
    def project(self, story: StoryState) -> None: ...          # idempotent full projection
    def issue_url(self, ref: IssueRef) -> str: ...

class GitHostProvider(Protocol):
    name: str
    def push(self, ref: str) -> PushResult: ...
    def fetch(self, ref: str) -> None: ...
    def file_url(self, branch: str, path: str) -> str: ...
    def commit_url(self, sha: str) -> str: ...
```

Hierarchy, dependency links, PRs, CI and rulesets belong to the provider extensions and are passed through `project()` and their own commands; the core interface stays small.

The **local backlog provider** assigns issue numbers from the highest story ID present on `planning` plus one, committed through the backlog's compare-and-swap so parallel creators can't collide. It is for tests, offline work and repos without a remote. Switching an existing repo from local to GitHub numbering is out of scope for the first release.

## Extension API

An extension is a Python package exposing an `aitm.extensions` entry point that returns:

```python
Extension(
    name="github",
    version="0.1.0",
    requires_core=">=0.1,<0.2",
    namespace="github",
    event_types=[...],          # Pydantic models, type names under the namespace
    owned_paths=["stories/*/*/github/*"],
    guards=[GuardRegistration(state="review", slot="exit", guard=...)],
    actions=[ActionRegistration(state="*", action=...)],
    cli=typer_app,              # mounted as `aitm github …`
    providers={"backlog": GitHubBacklog, "githost": GitHubHost},
    config_model=GitHubConfig,  # validates the [github] table in .aitm.toml
)
```

At load, the registry checks the core version range, refuses duplicate namespaces, event types or overlapping owned paths, and orders registrations deterministically. Only extensions listed in `.aitm.toml` are loaded.

## CLI

Every command supports `--json` (stable output schema) and exits non-zero only on real errors or enforce-mode refusals.

| Group | Commands |
| --- | --- |
| setup | `init`, `doctor`, `index rebuild` |
| ideas | `idea add`, `idea list` |
| drafts | `draft new`, `draft open`, `draft discard`, `draft list` |
| stories | `graduate`, `describe`, `show`, `list`, `search`, `explain`, `link` |
| work | `bind`, `unbind`, `sync [--push]` |
| lifecycle | `promote [--to]`, `demote --to --reason`, `abandon --reason`, `estimate`, `design accept`, `plan accept`, `jit`, `test`, `review`, `signoff` |
| rules | `expand`, `trip decide`, `pivot` |

`aitm explain <id>` prints the story's state, the next forward state, which guards would pass or fail and why, and the exact command to run next. It is the agent's primary "what now?" tool.

## Performance budgets

- `show`, `list`, `explain` with a warm index: under 150 ms on a laptop.
- `promote` excluding provider actions and push: under 1 s.
- Unit test suite: under 10 s, with no git or network spawned (`MemoryBackend`, fake providers).
- A small integration lane exercises `GitBackend` against real temporary repos, including concurrent writers.

## Migration from the hand-built `v0` files

The first release ships `aitm migrate v0`, which reads `.aitm/stories/*/*/story.md` frontmatter and `events.jsonl` written by hand on 2026-11-08, converts `v0` events to `v1` (adding ULIDs and milliseconds), splits the prose out of `story.md` into `description.md`, regenerates `story.md`, and moves any shared discarded log to per-entry files.

## Acceptance

The core is done when, in a temporary repo with only `aitm-core` installed:

1. `aitm init` creates `.aitm.toml`, the `.gitignore` entry and an orphan `planning` branch.
2. An idea and a draft can be created, the draft graduated through the local provider, and the story walked backlog → done with every core guard passing, using only CLI commands.
3. The same walk in enforce mode is refused at each guard when its condition is missing, with an `explain` output that names the missing condition and the command that fixes it.
4. Advisory mode records each failing guard as an event and continues.
5. A second expansion, a nested expansion and a time overrun each record the right trip; enforce mode moves the story to plan and blocks Develop until `trip decide` and a new `plan accept`.
6. Eight concurrent processes binding eight different stories and syncing 50 times each produce a linear `planning` history with no lost writes.
7. Deleting the index and running any command rebuilds it with identical query results.
8. A sample extension registers an event type, a guard and a command; a second extension claiming the same event type is refused at load.
9. `aitm migrate v0` upgrades the hand-built #1 and #2 records with no data loss.
10. Performance budgets are met.

## Left to the builder

- Module boundaries inside each folder, helper names, and test layout.
- ULID library or a small in-house implementation.
- Retry counts and jitter for compare-and-swap and push.
- `--json` output schemas, provided they are versioned and documented.
- Exact wording of CLI messages, provided every refusal names the fix.
