---
schema: aitm.doc/v0
story: 2
role: design
title: aitm-core design
created: 2026-11-08T20:05:00Z
updated: 2026-11-09T04:25:31Z
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
branch = "planning"           # chosen at init; "planning" is the suggested default
trunk = "origin/trunk"        # the host repo's default branch, detected at init

[enforcement]
mode = "advisory"            # or "enforce"

[limits]
leaf_agent_hours = 4          # implementation clock per attempt, develop entry → review passed
expansions_per_story = 1      # per attempt; an expansion story has none
max_trips = 2                 # after this many trips the story returns to backlog
idle_gap_minutes = 15         # longest activity gap counted as engaged time

[providers]
backlog = "local"            # "github" once aitm-github is installed
githost = "none"

[extensions]
enabled = []                 # e.g. ["github", "harness"]

[test]
command = "uv run pytest"    # what `aitm test` runs
```

Everywhere else in this document, "`planning`" means the branch named by `[store] branch`. No code hard-codes the name.

## `aitm init`: installing into a host repo

`init` is safe to re-run. Each step checks first and skips what's already in place.

1. **Detect the default branch.** It reads the remote's HEAD (`git symbolic-ref refs/remotes/<remote>/HEAD`, or the git host provider when one is configured) and writes it as `[store] trunk`.
2. **Choose the planning branch name.** It suggests `planning`. Interactively, the user can accept it or type another name. Non-interactively, `--planning-branch <name>` sets it, and the default is `planning`. The name must be a valid ref name and must differ from the default branch (`trunk`, `main`, `master` or whatever step 1 found). It must not already exist locally or on the remote, unless that branch is already an aitm planning branch (its root commit carries the `aitm-planning-root` trailer).
3. **Create the branch with no shared history.** The branch is an orphan: its root commit has no parent and the empty tree, so nothing from the default branch is in it, and none of the default branch's history is either. The root commit message carries the trailer `aitm-planning-root: v1`. A second commit adds `.aitm/README.md`. Both commits are written through the plumbing backend, so nothing is checked out. The branch is then pushed.
4. **Protect the branch.** It calls `githost.protect_branch(branch, rules)` with: no deletion, no force-push (fast-forward only), linear history required (no merge commits), no PR requirement, and no bypass actors *(builder's call: agents run with the owner's token, so an admin bypass would also be an agent bypass; the deliberate override is an admin editing or disabling the rule)*. The provider returns `applied`, `already-protected`, or `manual` with step-by-step instructions and a settings URL. It returns `manual` when the API can't do it (no admin permission, a plan that doesn't support protection on this repo, or a host without an API). `init` prints those instructions and records the result. With no git host provider, it always prints the generic instructions.
5. **Write the trunk-side files.** It writes `.aitm.toml` and adds `.aitm/` to `.gitignore` in the working tree. It does not commit them: trunk is normally protected, so the user lands them through their usual PR flow. `init` prints the exact commands to do that.
6. **Install git hooks.** It installs the planning-branch hooks described below into the clone's shared hooks directory (`git rev-parse --git-common-dir`/hooks, or the configured `core.hooksPath`). It chains to any hook already there rather than replacing it.
7. **Run provider init steps.** Provider extensions add their own steps (the GitHub extension creates the Project and fields, and protects the default branch the same way).

## Guarding the planning branch

The planning branch must hold only `.aitm/` story data. Three accidents threaten that: an agent merges implementation code into it, someone opens a PR into it, or someone checks it out and commits story code there. Six layers defend it, from strongest to weakest:

1. **Unrelated history (structural).** The planning branch shares no ancestor with the default branch. GitHub refuses to compare or open a PR between them (verified on kburson/aitm 2026-11-08: "No common ancestor between planning and trunk"), and `git merge` refuses without `--allow-unrelated-histories`.
2. **Host ruleset.** No deletion, no force-push, linear history required. Linear history rejects every merge commit, whether pushed directly or created by merging a PR. aitm's writes are single-parent commits and pass. (GitHub's file-path push rules apply to the whole repo, not to one branch, so "only `.aitm/` on this branch" cannot be enforced on the server.)
3. **Git hooks installed by `init`.**
   - `pre-commit` and `pre-merge-commit` refuse any commit or merge while the planning branch is checked out. aitm's writer uses `commit-tree`, which runs no hooks, so it is unaffected.
   - `pre-push` checks every new commit bound for the planning branch against the **planning invariants**: one parent; changes only under `.aitm/` (plus the root `README.md`); no ancestor shared with the default branch.
   - Hooks can be skipped with `--no-verify`. They stop confusion, not intent.
4. **Harness hooks** (`aitm-harness`). They deny agent commands that check out or switch to the planning branch, add a worktree on it, open a PR with it as the base, or merge with `--allow-unrelated-histories`. Like all hooks here, a backstop, never required for correctness.
5. **Core checks.**
   - Every command checks `git worktree list --porcelain`. If the planning branch is checked out anywhere, writes are refused with the worktree's path and the fix (`git worktree remove <path>` or `git switch <story-branch>`). `aitm bind` refuses to bind in a worktree on the planning branch.
   - Every fetch of the remote planning branch validates new commits against the planning invariants. On a violation the core stops writing, **in advisory mode too**, because the store itself is damaged, and records the bad commits.
   - `aitm planning repair` writes a new commit whose tree is the last valid tree, on top of the bad tip. It is a fast-forward, so the ruleset allows it. The bad commit stays in history; the files are clean.
   - If the default branch's history was merged in, layer 1 is lost: the branches now share history. Restoring it needs an admin to disable the ruleset and reset the branch. `aitm doctor` reports this and prints the steps; aitm never does it.
6. **Server-side audit** (`aitm-github`). A GitHub Action on every push to the planning branch runs the same invariant check and opens an issue on violation. This catches pushes from clones without the hooks.

`aitm doctor` re-checks the steps that can drift. These are: the configured branch exists and is an aitm planning branch, it isn't checked out in any worktree, `.aitm.toml` is on trunk, the hooks are installed, the remote branch passes the planning invariants and still shares no history with the default branch, and the branch is protected (where the provider can read protection). It prints the fix for anything missing, including the manual protection steps again.

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
| `events.jsonl` | core's append API only (extensions append through it with namespaced types); see the event-log exception below |
| `story.md`, every frontmatter block | core, regenerated from events and `description.md` |
| `description.md` body, `draft.md` body, idea bodies | the agent or human working the story |
| `design/`, `plan/` documents | the agent writing them (later, `aitm-agents`) |
| `design/reviews/`, `plan/reviews/` | the review tool (later, `aitm-peer-review`) |
| `retro/` | the agent, through `aitm review` |
| Extension files | the extension that declared the path |

**The event-log exception** *(builder's call)*. `events.jsonl` is the one file with several writers: an agent's session, a human recording a pivot from another checkout, a trip recorded on an origin story by its expansion's process, extensions, other clones. It is safe because it is append-only and every line has a unique ULID:

- Events are never materialized into a worktree for editing. `append_event` writes straight to `planning` through the backend.
- On a compare-and-swap retry the backend re-reads the current blob and appends its new lines to it; it never replaces the file.
- On push replay and on fetch, `events.jsonl` is merged as the union of lines by event `id`, sorted by ULID. Every other file is replayed whole, because it has a single writer.
- Before running guards for a transition, the core fetches `origin/planning` when a git host provider is configured; if the fetch fails it proceeds on local data and records the fact in the guard events.

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
- `ts` is when the thing happened. An event written later from a record of something that already happened is **backfilled**: it carries `"backfill": {"recorded_at": …, "by": <actor>, "source": <repo-relative path of the record it was read from>}` beside `data`, and its `actor` is whoever did the original work. No event may be backfilled without a source record that a reader can open. Folding orders events by `ts`, then `id`, so a backfilled event lands where it happened, not where it was appended.

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
| `core.expansion.recorded` | `aitm expand` | kind (defect or story), child id, reason, attempt |
| `core.expansion.resolved` | rules engine, when the expansion story reaches done | child id, disposition |
| `core.trip.recorded` | rules engine | cause (second-expansion, nested-expansion, time-limit), on (the story whose limit was hit), attempt, engaged hours |
| `core.trip.decided` | `aitm trip decide` | decision (scrap or refactor), rationale, analysis path, expansion disposition, attempt |
| `core.pivot.recorded` | `aitm pivot` | by, reason, scope_change |
| `core.test.receipt` | `aitm test` | command, exit code, head SHA, duration, summary |
| `core.review.recorded` | `aitm review pass\|changes` (later, `aitm-peer-review` and `aitm-github`) | pull-request review of code: verdict, head SHA, reviewer refs |
| `core.doc-review.submitted` | `aitm review turn` (later, `aitm-peer-review` as each response lands) | one turn of a document review: level (sar, spr or xpr), doc path, round, role (reviewer or author), agent (host, provider, model id, effort, session id and its kind), started_at, submitted_at, start basis, input digest (reviewer) or output digest and patch (author), response path, finding ids raised or answered, decision (reviewer only) |
| `core.doc-review.completed` | `aitm review complete` (later, `aitm-peer-review` at finalization) | level, doc path, rounds, outcome (exhausted or round-cap), base and final digests, started_at, ended_at, manifest path |
| `core.signoff.recorded` | `aitm signoff` | retro path, confidence vote, verdict (delivered or not), by (always the agent) |
| `core.link.changed` | `aitm link` | parent, blocking, blocked_by |
| `core.description.set` | `aitm describe` | title, as, want, so_that, scope, content hash |
| `core.deliverable.added` | `aitm deliver` (spikes) | path |
| `core.activity.recorded` | any command touching the story; later the harness extension | source |

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
3. On a forward edge, run the current state's exit guards, then the target's entry guards, in registration order: core guards first, then extensions in load order. On a backward edge, an abandon, or a trip-forced move, skip the current state's exit guards and run only the target's entry guards; these moves require a reason instead *(builder's call)*. Record a `core.guard.evaluated` event for every guard.
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
| develop | exit | `expansion-resolved` | the current attempt's expansion, if any, has reached done |
| test | exit | `test-passing` | a passing `core.test.receipt` for the current branch head |
| review | exit | `review-passed` | a `core.review.recorded` with verdict `pass` for the current branch head |
| review | exit | `signed-off` | a `core.signoff.recorded` by the agent, with its retrospective |
| any forward | entry | `children-consistent` | an epic cannot pass a state its open children have not reached; an epic cannot reach done with open children |

**`aitm describe`** *(builder's call)* takes the story's content as structured input: `--title`, `--as`, `--want`, `--so-that`, and `--scope-file`. It records a `core.description.set` event (fields plus a content hash) and renders `description.md` from it. Writing the description is real authoring work, not evidence, so supplying it is the agent's job; the guard checks the event, never the prose. Later edits go through `describe` again.

**Guard sets by kind** *(builder's call)*:

| Kind | Differences from a story |
| --- | --- |
| story, defect | as above |
| spike | `story-commits` and `test-passing` are replaced by `deliverable-present` (a document under `attachments/` recorded by `aitm deliver`); `review-passed` is recorded against the deliverable's planning SHA instead of a branch head |
| epic | `leaf-size`, `jit-current`, `story-commits`, `test-passing`, `review-passed` and the implementation clock do not apply. An epic enters develop when its plan is accepted (its plan creates the children) and stays there while children run. It may leave develop only when every child has reached review or done, and leave review only when every child is done. `signed-off` applies; the epic's retrospective covers its children. |

**Branches and trunk** *(builder's call)*:

- The core does not create worktrees. `aitm bind` records the current checkout's worktree path and branch. On entering develop without a branch, `aitm bind` creates `story/<id>-<slug>` from the trunk tip; after a **scrap** decision the next attempt uses `story/<id>-<slug>-a<n>`.
- `[store] trunk = "origin/trunk"` in `.aitm.toml` names the trunk ref; it is fetched before `jit` and before the plan → develop transition.
- `jit-current` passes when the trunk SHA recorded by `aitm jit` is an ancestor of the current trunk tip **and** no commit since then touched a path listed in the plan's declared touched paths (when the plan declares them). Unrelated merges by parallel stories do not make the JIT stale.
- `story-commits` and `test-passing` read the branch recorded by the latest session and its head in the local repo; `test-passing` requires the receipt's head SHA to equal that head.

**Actors** *(builder's call)*. The actor is resolved in order: an explicit `--as-human` on commands that allow it (requires an interactive TTY and a typed confirmation), else `agent` when any known harness session variable is set (`CLAUDE_CODE_SESSION_ID`, `CODEX_SESSION_ID`, `GROK_SESSION_ID`, `AI_TASK_MANAGER_SESSION_ID` and the like, list in config), else `human` when stdin is a TTY, else `tool`. There is no required human gate, so the actor matters for attribution, not for permission, with one exception: `aitm pivot` is human-only, because an agent recording a pivot would hide a planning failure that should have been a trip. The core cannot fully stop an agent posing as a human on a single-user machine; the harness extension backs this up by denying agent tool calls to `pivot`.

**Review and sign-off.** Review holds the PR review: reviewers (agent peer review, CI, later the provider's PR approvals) record verdicts with `aitm review pass|changes`. Once a review passes for the current head, the agent runs `aitm signoff --retro <path> --confidence <1-5>`, which records its retrospective on its own work (design, plan and implementation alignment, what went well, what should have been planned better, lessons, advisory confidence vote) and moves the story to done. Sign-off never waits for a human. The owner may later discuss the retro with an agent (`aitm discuss <id>`); that is never required, because a required human gate stacks work up and turns sign-off into a rubber stamp.

**Core resident actions:** on entering any state, `project-to-backlog` calls the configured backlog provider's `project(story_state)` (a no-op for the local provider). On entering done, `close-sessions` ends any open session.

## Expansion and trip rules

**The implementation clock.** Only implementation is time-limited; planning (Backlog, Refine, Ready for Plan, Plan) never is.

- A story's clock runs from the moment it leaves plan and enters develop until a review passes in review (`review-passed`). Writing the retrospective after that is not counted.
- `rules.timing` computes engaged agent-hours on the running clock as the sum of gaps between consecutive activity events, counting no gap longer than 15 minutes (configurable) *(builder's call)*. A session left open overnight adds nothing while idle. Until the harness extension exists, the activity events are the commands themselves.
- Each entry into develop after an accepted plan starts a new **attempt**. Each attempt has a fresh clock of `leaf_agent_hours` and a fresh expansion allowance. Totals across attempts are kept for learning.
- The clock pauses while the story is blocked by its own expansion, and resumes when the expansion reaches done.

**Planning time.** Planning has no limit, but its time is recorded, because estimation calibration and usage reporting need the whole Refine → Plan → Close picture, not just implementation.

- `rules.timing` reports planning agent-hours per story by state, using the same gap rule over the same activity events as the implementation clock. Planning time never feeds a guard or a trip.
- Document review time is counted from `core.doc-review.submitted` events: each turn contributes `submitted_at − started_at`, reported by level (sar, spr, xpr), role and model. Turn spans and other activity in the same window are merged, so time is never counted twice.
- Each turn's `start_basis` says how its start was known: `recorded` (the participant wrote its own start), `claim` (the review tool's claim timestamp for that turn) or `prior-submit` (the previous turn's submission; used when nothing better exists). ai-peer-review 0.4.x writes a participant's registration time into every response's `started_at`, so for its records the start comes from the manifest's claim times, falling back to the previous turn's submission. Reported totals say how many turns rest on each basis.
- Turn spans cover writing a response, not setup, reading the inputs before the claim, or publication. The level's `started_at`/`ended_at` give the outer bound.
- `aitm review import <folder>` backfills a level's `core.doc-review.submitted` and `core.doc-review.completed` events from a portable review record (its responses and manifest, plus native records when present). It refuses a folder whose finding ids or digests don't reconcile, and is idempotent: a turn already recorded is skipped.

**Expansion.**

- `aitm expand <id> --kind defect|story --title "…" --reason "…"` creates a new story (graduating immediately through the backlog provider) with `expanded_from: <id>`, records `core.expansion.recorded` on the origin, sets the origin `blocked_by` the new story, and pauses the origin's clock.
- The expansion story starts with its own clock and its own `leaf_agent_hours` limit, and **no** expansion allowance. Work it discovers is absorbed inside it as long as it stays within its limit.
- When the expansion reaches done, `core.expansion.resolved` is recorded on the origin, the block clears and the origin's clock resumes.

**Trips.** A trip means the plan failed. It is recorded on the origin story, whichever story hit the limit:

| Cause | When |
| --- | --- |
| `time-limit` | the story's engaged hours in this attempt exceed `leaf_agent_hours`, or its expansion's engaged hours exceed the expansion's own limit |
| `second-expansion` | the story has used its expansion allowance in this attempt and asks for another |
| `nested-expansion` | the story's expansion asks for an expansion |

- Hours are checked by the next command that touches a story with a running clock. Expansion limits are checked by `aitm expand` itself.
- In enforce mode a trip stops all work at once: the request that tripped it is refused; open sessions on the origin and its expansion are ended; the origin moves to plan; the expansion, if open, moves to plan with reason `origin-tripped`. In advisory mode the trip is recorded and reported, and nothing moves.
- In plan, the agent examines the attempt (plan, decisions, commits, expansion, time) and writes a trip analysis to `plan/trip-<attempt>.md`. Then `aitm trip decide <id> --decision scrap|refactor --rationale "…" --analysis plan/trip-<n>.md [--expansion continue|fold|abandon]` records the decision. No human approval is required. For **scrap**, the story branch is left untouched and recorded as an abandoned attempt, and the next attempt starts a new branch. For **refactor**, the branch is kept. The expansion disposition says whether the expansion story continues under the new plan, is folded into the origin's new plan (and closed as superseded), or is abandoned.
- Plan cannot be left until the trip is decided and a new plan is accepted (`trip-decided`, `plan-accepted`). The next develop entry starts a fresh attempt.
- After a story's **second** trip, `trip decide` refuses `refactor` and `scrap` and the story returns to backlog for redesign or a split *(owner's "yes" read as agreeing to the cap; confirm)*.

**Pivots.** `aitm pivot <id> --reason "…" [--scope-change]` records a human pivot. With `--scope-change` it moves the story to plan and closes the current attempt without a trip; it never counts against planning.

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
    def default_branch(self) -> str: ...
    def protect_branch(self, branch: str, rules: ProtectionRules) -> ProtectResult: ...
    # ProtectResult: status (applied | already-protected | manual), instructions, settings_url
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
| setup | `init`, `doctor`, `index rebuild`, `planning repair` |
| ideas | `idea add`, `idea list` |
| drafts | `draft new`, `draft open`, `draft discard`, `draft list` |
| stories | `graduate`, `describe`, `show`, `list`, `search`, `explain`, `link` |
| work | `bind`, `unbind`, `sync [--push]` |
| lifecycle | `promote [--to]`, `demote --to --reason`, `abandon --reason`, `estimate`, `design accept`, `plan accept`, `jit`, `test`, `review pass\|changes`, `review turn`, `review complete`, `review import <folder>`, `signoff`, `deliver` |
| rules | `expand`, `trip decide`, `pivot` |

`aitm explain <id>` prints the story's state, the next forward state, which guards would pass or fail and why, and the exact command to run next. It is the agent's primary "what now?" tool.

## Performance budgets

- `show`, `list`, `explain` with a warm index: under 150 ms on a laptop.
- `promote` excluding provider actions and push: under 1 s.
- Unit test suite: under 10 s, with no git or network spawned (`MemoryBackend`, fake providers).
- A small integration lane exercises `GitBackend` against real temporary repos, including concurrent writers.

## Migration from the hand-built `v0` files

The first release ships `aitm migrate v0`, which reads `.aitm/stories/*/*/story.md` frontmatter and `events.jsonl` written by hand on 2026-11-08, converts `v0` events to `v1` (adding ULIDs and milliseconds), splits the prose out of `story.md` into `description.md`, regenerates `story.md`, and moves any shared discarded log to per-entry files. It keeps backfilled `v0` events (the SAR, SPR and XPR rounds of #1's architecture, backfilled on 2026-11-09) with their `backfill` blocks, and checks each one's source record still exists.

## Acceptance

The core is done when, in a temporary repo with only `aitm-core` installed:

1. `aitm init` creates `.aitm.toml`, the `.gitignore` entry and an orphan planning branch with an empty-tree root commit, under the suggested name or one chosen with `--planning-branch`. With no git host provider it prints the manual protection steps. Re-running it changes nothing, and it refuses a name that is already taken by a branch that isn't an aitm planning branch.
2. An idea and a draft can be created, the draft graduated through the local provider, and the story walked backlog → done with every core guard passing, using only CLI commands.
3. The same walk in enforce mode is refused at each guard when its condition is missing, with an `explain` output that names the missing condition and the command that fixes it.
4. Advisory mode records each failing guard as an event and continues.
5. A second expansion, a nested expansion, a time overrun on a story and a time overrun on its expansion each record the right trip on the origin; enforce mode ends the sessions, moves the origin (and an open expansion) to plan, and blocks develop until `trip decide` and a new `plan accept`. A third attempt is refused and sent to backlog.
5a. Engaged time counts only from develop entry to the first passing review, excludes planning, pauses while the story waits on its expansion, and restarts at zero for each attempt and for each expansion story.
5b. A story walks from review to done with no human command; `signoff` records the agent's retrospective.
5c. A two-round document review recorded with `aitm review turn` and `aitm review complete` produces planning time by level, role and model, with no double counting where turns overlap and with each turn's start basis reported. The same totals result from backfilling the same review from its portable record.
6. Eight concurrent processes binding eight different stories and syncing 50 times each produce a linear `planning` history with no lost writes.
7. Deleting the index and running any command rebuilds it with identical query results.
8. A sample extension registers an event type, a guard and a command; a second extension claiming the same event type is refused at load.
8a. In a temporary repo with the hooks installed: a commit while the planning branch is checked out is refused; a push to it of a merge commit, a commit touching a path outside `.aitm/`, or a commit sharing history with the default branch is refused; aitm's own writes pass. A violating commit injected past the hooks stops core writes, and `aitm planning repair` restores the last valid tree as a fast-forward.
9. `aitm migrate v0` upgrades the hand-built #1 and #2 records with no data loss.
10. Performance budgets are met.

## Left to the builder

- Module boundaries inside each folder, helper names, and test layout.
- ULID library or a small in-house implementation.
- Retry counts and jitter for compare-and-swap and push.
- `--json` output schemas, provided they are versioned and documented.
- Exact wording of CLI messages, provided every refusal names the fix.
