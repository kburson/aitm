---
schema: aitm.doc/v0
story: 2
role: design
title: aitm-core design
created: 2026-11-08T20:05:00Z
updated: 2026-11-09T04:49:38Z
last-branch: review/2-core-design-sar
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
3. Write to `planning` from story worktrees without checking it out; serialize safe concurrent operations and expose conflicting work without losing it.
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
remote = "origin"            # absent for an explicitly local-only store
branch = "planning"           # chosen at init; "planning" is the suggested default
trunk = "origin/trunk"        # the host repo's default branch, detected at init

[enforcement]
mode = "advisory"            # or "enforce"

[limits]
leaf_agent_hours = 4          # implementation clock per attempt, develop entry → review passed
expansions_per_story = 1      # per attempt; an expansion story has none
idle_gap_minutes = 15         # qualified CLI-gap estimate; not proof of complete engagement

[providers]
backlog = "local"            # "github" once aitm-github is installed
githost = "none"

[extensions]
enabled = []                 # e.g. ["github", "harness"]

[test]
command = "uv run pytest"    # what `aitm test` runs
```

Everywhere else in this document, "`planning`" means the branch named by `[store] branch`. No code hard-codes the name.

**Policy authority and bootstrap.** Installation records the code repository identity, local default-branch ref, optional remote/ref pair, and planning store identity in clone-local `<git-common-dir>/aitm/installation.json`. These routing anchors come from an explicit `init --default-branch <ref>` or an unambiguous repository/remote HEAD, never from a story's `.aitm.toml`. A no-remote repository uses its explicitly selected local default branch. The core validates distinct code/planning refs and resolves committed configuration from that anchored default ref. An existing installation cannot be redirected by a story's `[store] trunk`; a delivered config change must be checked against the current anchor and adopted through `init --reconfigure`. The descriptor is a routing cache with a recorded bootstrap source, not an alternative policy file. A fresh clone establishes it from its selected default branch; ambiguous refs require an explicit choice.

`init` may write the initial config and store without policy already on trunk. It reports `bootstrap-pending` until the config lands on the selected default branch. Only init, doctor, migration preflight and read/export operations run before that point. This is installation readiness, not a routine human workflow gate. In a local-only repo the installer commits these files on its local default branch; a protected hosted repo uses its normal PR flow. Re-running init preserves existing foreign files and resumes its recorded steps rather than creating a second store.

Before a command evaluates policy, the core attempts to refresh the configured default and planning refs outside guards, validates fetched history in a candidate ref, and pins the policy commit, code head(s), planning tree and consulted story/path versions. Guards and enabled extensions use that immutable input. A story-worktree config is never consulted for mode, limits, extensions, test command or routing. Every operation records effective policy revision/settings and fetch status. Story-scoped operations live under that story; pre-story/store operations use the store operation area. Local-only operation trusts committed local policy. With a configured remote, failed refresh permits local recording against the last validated policy with explicit stale/unknown freshness; a freshness-dependent guard is not a pass, and shared effects remain pending. No last valid policy, invalid configuration, invalid store history or ambiguous routing is an integrity refusal in both modes; diagnostic reads remain available. Publication rechecks current committed policy and the original operation's relevant inputs before reconciling offline work. A newer policy does not silently rewrite the historical policy under which local evidence was produced.

The second-trip cap and the expansion-completion boundary remain open owner choices; neither is an operative default in this configuration. The explicit four-hour and one-expansion constraints remain unchanged.

**Trust anchor.** The committed default-branch configuration contains the expected store UUID, planning repository/ref and genesis commit SHA. Init computes them from the store it created, records them in its crash-recoverable local bootstrap journal before publishing, and proposes those exact values in the initial config. Before that config is committed, only the same verified bootstrap operation can resume. A fresh clone trusts the configured code repository/default-branch policy obtained through its selected Git transport, then verifies the planning genesis, store UUID and complete history against it; it never trusts a candidate planning receipt to nominate its own root. This is ordinary repository/configuration trust, not independent user authentication. Explicit reconfiguration validates both the old anchor and proposed replacement. An existing unrecognized branch is refused even if its trailer looks familiar.


## `aitm init`: installing into a host repo

`init` is safe to re-run. Each step checks first and skips what's already in place.

1. **Detect the default branch.** It establishes the routing anchor as above, using the remote HEAD when available or `--default-branch` for a local-only or ambiguous repository, then writes the corresponding `[store] trunk`.
2. **Choose the planning branch name.** It suggests `planning`. Interactively, the user can accept it or type another name. Non-interactively, `--planning-branch <name>` sets it, and the default is `planning`. The name must be a valid ref name and must differ from the default branch (`trunk`, `main`, `master` or whatever step 1 found). It must not already exist locally or on the remote, unless its complete history and store identity match the configured trusted anchor or the same init operation’s retained bootstrap journal. A root trailer alone is not proof.
3. **Create the branch with no shared history.** The branch is an orphan: its root commit has no parent and the empty tree, so nothing from the default branch is in it, and none of the default branch's history is either. The root commit message carries the trailer `aitm-planning-root: v1`. A second commit adds `.aitm/README.md` and `.aitm/store.json` with a fresh store UUID, schema, root identity and initial local allocation-authority generation, all bound to the retained init operation. Rerun reuses these values. Both commits are written through the plumbing backend, so nothing is checked out. The branch is then published when a remote is configured; local-only init records publication as not applicable. A failed push is pending, not an initialization rollback.
4. **Protect the branch.** It calls `githost.protect_branch(branch, rules)` with: no deletion, no force-push (fast-forward only), linear history required (no merge commits), no PR requirement, and no bypass actors *(builder's call: agents run with the owner's token, so an admin bypass would also be an agent bypass; the deliberate override is an admin editing or disabling the rule)*. The provider returns `applied`, `already-protected`, or `manual` with step-by-step instructions and a settings URL. It returns `manual` when the API can't do it (no admin permission, a plan that doesn't support protection on this repo, or a host without an API). `init` prints those instructions and records the result. With no git host provider, it always prints the generic instructions.
5. **Write the trunk-side files.** It writes `.aitm.toml` and adds `.aitm/` to `.gitignore` in the working tree. It does not commit them: trunk is normally protected, so the user lands them through their usual PR flow. `init` prints the exact commands to do that.
6. **Install git hooks.** It installs the planning-branch hooks described below into the clone's shared hooks directory (`git rev-parse --git-common-dir`/hooks, or the configured `core.hooksPath`). It chains to any hook already there rather than replacing it.
7. **Run provider init steps.** Provider extensions add their own steps (the GitHub extension creates the Project and fields, and protects the default branch the same way).

## Guarding the planning branch

The normal planning tree contains only `.aitm/` data. Its history is isolated from the code repository's anchored default branch, including when a separate remote holds planning. Core exposes one provider-neutral history/tree validator used by its writer, fetch, hooks and the later hosted audit.

1. **Unrelated history.** New stores begin at an empty zero-parent root marked `aitm-planning-root: v1`; later commits have exactly one parent. Planning is never merged into the code branch. Normal Git merge refuses unrelated histories without its override; this is a structural backstop, not an authorization system.
2. **Host protection.** Init requests no deletion, no force-push, linear history and no bypass actors. If unsupported it records the manual instructions. This does not enforce data paths per branch by itself.
3. **Git hooks.** Pre-commit and pre-merge-commit refuse ordinary commits while the configured planning ref is checked out. The plumbing writer does not depend on them. Pre-push validates every candidate planning update from the supplied old/new refs, including its final tree and intervening commits. Hooks are bypassable backstops and must preserve existing hooks.
4. **Harness hooks.** Optional rules deny checking out the configured planning ref, PRs targeting it and unrelated-history merges. A temporary review branch derived from planning is a distinct ref and is permitted.
5. **Core enforcement.** Before every write, check `git worktree list --porcelain`; refuse if the configured planning ref is checked out anywhere, including when code and store locations differ. Reads still work. Fetch into a candidate ref, validate it, then advance the validated local view; an invalid candidate is quarantined and never becomes a writer base. Ownership, schema, path and history failures are integrity errors in advisory and enforce modes.
6. **Hosted audit.** The agreed GitHub requirement is an audit of every planning push. Its trigger/location remains unresolved: a normal push workflow is read from the event's ref, and no workflow code is allowed on planning. The GitHub design must solve that obligation without assuming a trunk-only workflow runs on planning pushes or substituting polling. The core supplies the validator; M1 does not claim that hosted layer already exists.

**Validation and baseline.** Verify the root, complete parent chain from a trusted anchor, isolation from the anchored code-default history, normalized regular data paths, supported schemas and append/ownership constraints. For routine writes, changed paths and the final tree must both comply. Reject symlinks, submodules, path traversal and executable/code payloads presented as core metadata. Attachment data and declared extension schemas have explicit allowed types; a `.aitm/` prefix alone does not prove a valid store. Cached validation is keyed by anchor, tip and validator version. A fresh clone checks the full chain. An unknown or unsupported anchor is not trusted because a commit carries a familiar trailer.

The hand-built aitm root and its root `README.md` are a bounded migration input, not a permanent root-path exception. `migrate v0` validates the recorded legacy root/tree/history as a legacy baseline, retains that provenance, moves any useful README prose into `.aitm/README.md` and removes the root README in the forward cutover commit. The migration receipt records exact old tip, accepted legacy violations and resulting valid tree, so a fresh validator can verify that cutover. It cannot bless arbitrary unrelated history or code. New stores never use this exception.

Before legacy apply, init/migration preflight proposes a bounded legacy anchor in the code-default policy: exact legacy root and approved pre-cutover tip, schema adapter version and allowed deviations (for the hand-built store, its existing root README and v0 record shapes). That policy must be committed on the already anchored code default branch; a fresh clone reads it independently of planning's migration receipt. Apply requires its expected tip to match this declaration and verifies the entire declared legacy segment. A candidate receipt cannot extend that segment or add a new deviation. A later remote tip requires an updated validated preflight/declaration, not implicit trust. Receipt result bindings use the tree with that receipt path omitted (the validated payload tree), plus the receipt schema/path; the final Git commit binds the complete tree externally. No receipt contains a self-referential final-tree hash.

**Forward repair.** `aitm planning repair` is a narrowly allowed integrity operation while ordinary writes are fenced. It pins the quarantined tip, last validated tree and offending commits, and produces a single-parent child of that exact bad tip whose tree restores the last valid data plus a core-owned repair receipt under `.aitm/repairs/<operation-id>.json`. The receipt binds bad tip, valid anchor/tree, offending paths and the deterministic restoration. The validator permits precisely that restoration (including deletion of outside paths), checks the reconstructed expected tree and all subsequent normal commits, and retains the bad history as diagnosed evidence. Thus a fresh clone recognizes a verified repair instead of rejecting the same historical defect forever. A marker alone is insufficient. A changed remote tip forces revalidation and a new repair candidate; no force-push occurs. Local unpublished work and bad blobs are retained under recovery refs before repair, never discarded or silently treated as restored.

A forward repair cannot remove shared code ancestry, reverse a rewrite or repair an unprovable anchor. Those remain fenced with diagnostics and an explicitly authorized owner intervention path; the core never resets protected history itself. `doctor` reports local integrity, remote validation/publication, checkout exclusion, committed policy, hooks and protection separately, with the exact missing capability or repair path.

## Store layout

As in [`.aitm/README.md`](../../../../README.md), with one change from the hand-built version: there are **no shared append files**. A discarded draft writes its own file, `drafts/discarded/<stamp>-<slug>.json` (title, reason, last SHA, discarded-by, time), instead of a line in a shared `discarded.jsonl`.

```
.aitm/
  store.json                 core-owned store identity, schema and allocation authority
  operations/<operation-id>.json   pre-story/store operations only; no shared append log
  repairs/<operation-id>.json      verified repair evidence
  ideas/<YYYY-MM>/<YYYYMMDD-HHMM>-<slug>.md
  drafts/<YYYY-MM>/<YYYYMMDD-HHMM>-<slug>/draft.md, attachments/
  drafts/discarded/<YYYYMMDD-HHMM>-<slug>.json
  stories/<bucket>/<id>/
    story.md              generated
    description.md        agent-authored prose (title, user story, scope)
    events.jsonl          append-only authority
    operations/           story-owned operation/action records
    evidence/             retained execution/provider proof
    draft.md              the graduated draft
    design/  plan/  retro/  attachments/
```

`<bucket>` is `id // 100` zero-padded to three digits. Slugs are lowercase ASCII, hyphen-separated, at most 40 characters. Each idea/draft also has a collision-resistant entity ID allocated by the core. A colliding display path gets a checked unique suffix within the same transaction; the stable ID/full path, not a bare slug, is the command handle. Pre-story metadata and its operation record are owned by the core before any numbered story exists. No shared append log is needed.

## Ownership: one writer per file

Ownership names the API responsible for a persisted surface, not an exception for independent processes. All producers submit typed operations to the core; they never concatenate or union event files themselves.

| Surface | Owning write route |
| --- | --- |
| Event logs, operation records, generated story metadata | Core transaction/append API |
| `description.md` | `describe` accepts structured authored fields and scope, records `core.description.set`, then renders the document; direct body edits are rejected with the import command |
| Draft, idea, design, plan and attachment bodies | Assigned author through a bound workspace and `sync`; draft/idea commands before graduation |
| Review collateral | Validated `review import`, preserving exact native/portable bytes |
| Retrospective body | Agent-authored input to `signoff`, imported with its digest |
| Extension files | The declared owner through a constrained core transaction capability |

A Markdown document has distinct authored and generated fields, defined by its schema. Core refreshes only the generated header fields, preserving the authored body and semantic header fields. The canonical-content contract below names the boundary. Review originals and patches are immutable records and are never regenerated. JSON/JSONL metadata is represented by typed fields and the story file inventory; generated `<details>` blocks are never parsed back.

Story authoring has one active binding per story per clone, identified by session, worktree, generation and allowed path set. A second bind refuses with the current holder; `bind --recover` explicitly fences the old generation, preserves its unsynced files and starts a replacement after verifying no live writer is being silently displaced. Stale holders cannot sync, verify against another session's branch, or unbind the replacement. Core-mediated operations such as pivots, dependencies or telemetry may still append through transactions; they do not become body writers. Review import takes the same authoring reservation and path preconditions. Cross-clone authoring conflicts are detected at publication, not concealed by a claim of a global local lock. Until reconciled, a conflicting clone cannot project or perform a shared external action.

Every decision reads a single pinned planning snapshot, including related stories. The index must serve exactly that snapshot or core reads its tree directly. Rendering is deterministic from the pinned state, authored blobs, schema and policy versions; it never consults wall-clock time or a separately refreshed cache to invent metadata.

## Events

Every event is one JSON line. This example abbreviates required operation ID, sequence/prior-log digest, policy/read-set references and recording provenance described below:

```json
{"v":1,"id":"01JC...","ts":"2026-11-08T19:24:00.123Z","type":"core.state.changed",
 "story":2,"actor":{"kind":"agent","harness":"claude-code","session":"…","on_behalf_of":"kburson"},
 "data":{"from":"backlog","to":"refine","reason":null,"mode":"advisory"}}
```

- `id` is a stable opaque event identity (ULID for newly recorded events), not an ordering authority. Each operation has a stable ID and payload digest; retrying the same ID/payload returns the recorded outcome, while an ID with different bytes is an integrity error. Migration may use deterministic source-derived IDs under its versioned schema.
- `ts` is the known occurrence time in UTC, retaining the source precision; recording time and source/coverage are separate. Adding `.000` does not create millisecond precision.
- `type` is `<namespace>.<noun>.<verb>`. The core owns `core.*`; each extension owns its own namespace.
- `actor.kind` is `agent`, `human` or `tool`.
- Each event type has a Pydantic model for `data`; unknown types from uninstalled extensions are kept and shown, never dropped.
- An event written later from a record of prior work is **backfilled**: `backfill` carries `recorded_at`, `by`, a readable repo-relative `source`, and its immutable source digest/version. `actor` remains the original actor with the observed session identity kind; unknown attribution stays unknown. Backfill never invents an original actor or exact duration.
- Workflow folding uses committed append order and explicit operation preconditions, never timestamp/ULID sorting. Each story append carries its next sequence and prior-log digest, assigned only by the owning transaction. Historical display and timing reports may sort occurrences by `ts` then `id`, retaining recording order separately. Late descriptive review/activity facts do not retroactively execute a transition; correcting historical workflow state requires a typed reconciliation operation with source proof and a new append. Occurrence-time reporting does not authorize rewriting causal history.

Core event types:

| Type | Recorded by | Data |
| --- | --- | --- |
| `core.idea.created` | `aitm idea add` | path, tags |
| `core.draft.created` / `core.draft.discarded` | `aitm draft new` / `discard` | path, reason |
| `core.story.graduated` | `aitm graduate` | from draft, issue ref |
| `core.state.changed` | `promote`, `demote`, `abandon` | from, to, reason, mode |
| `core.guard.evaluated` | every transition attempt | operation, pinned read-set and policy refs, state, slot, stable guard/version, ok, code, reason, mode |
| `core.action.pending` / `core.action.completed` / `core.action.failed` | transition transaction / action runner | stable action key, owner/version, target state version, attempt, outcome and proof refs |
| `core.session.started` / `core.session.ended` | binding/closing operations | session and generation, worktree, branch/head, attempt, allowed paths and end/fence reason |
| `core.attempt.started` / `core.attempt.closed` | accepted-plan Develop entry / trip, pivot or closure | attempt ID, plan generation, binding/source, allowance, clock segment and closure reason |
| `core.estimate.set` | `aitm estimate` | phase (refine, plan, jit), agent_hours, size, priority |
| `core.doc.accepted` | `aitm design accept`, `aitm plan accept` | role, path, canonical version/digest, raw digest, verified review refs/levels and policy, source planning SHA, plan generation |
| `core.jit.recorded` | `aitm jit` | accepted plan digest/generation, intended attempt, code baseline, coverage paths/status, outcome and reviewed revision refs |
| `core.expansion.recorded` | `aitm expand` | kind (defect or story), child id, reason, attempt |
| `core.expansion.resolved` | verified child resolution / explicit scope disposition transaction | child id, origin attempt, disposition, plan/delivery evidence and affected dependency |
| `core.trip.recorded` | rules engine | cause (second-expansion, nested-expansion, time-limit), affected origin/child attempts, observed hours and proof/coverage, detection time |
| `core.trip.decided` | `aitm trip decide` | decision (scrap or refactor), rationale, analysis path, expansion disposition, attempt |
| `core.pivot.recorded` | `aitm pivot` | by, reason, scope_change |
| `core.test.receipt` | `aitm test` | attempt, source ref/head/tree, clean-input check, effective command/policy, observed execution interval/result, retained output hash |
| `core.review.recorded` | `aitm review pass\|changes` (later, `aitm-peer-review` and `aitm-github`) | pull-request review of code: verdict, head SHA, reviewer refs |
| `core.doc-review.submitted` | `aitm review turn` (later, `aitm-peer-review` as each response lands) | one turn of a document review: stable level-record ID, level (sar, spr or xpr), doc path, round, role (reviewer or author), agent (host, provider, model id, effort, session id and its kind), started_at, submitted_at, start basis, input digest (reviewer) or output digest and patch (author), response path, finding ids raised or answered, decision (reviewer only) |
| `core.doc-review.completed` | `aitm review complete` (later, `aitm-peer-review` at finalization) | stable level-record ID, level, doc path, rounds, outcome (exhausted or round-cap), base and final digests, started_at, ended_at, manifest path |
| `core.signoff.recorded` | `aitm signoff` | retro path, confidence vote, verdict (delivered or not), by (always the agent) |
| `core.link.changed` | `aitm link` | parent, blocking, blocked_by |
| `core.description.set` | `aitm describe` | title, as, want, so_that, scope, content hash |
| `core.deliverable.added` | `aitm deliverable add` (spikes) | path, raw/canonical digest as appropriate, attempt, source snapshot |
| `core.delivery.verified` | `aitm deliver` | reviewed source/deliverable, declared target, verified result mapping, method, proof refs, attempt |
| `core.outcome.recorded` / `core.usage.recorded` | sign-off / observed usage import | Refine/Plan/Close lineage, qualified actuals/lessons / deduplicated provider usage with units and availability |
| `core.activity.recorded` | eligible observed agent/tool activity; later harness extension | producer identity, session/attempt, interval or point, occurrence/recording time, coverage and freshness |

**Folding.** `events.fold(events) -> StoryState` validates operation/sequence lineage and produces current state, estimates, relationships, effective acceptance, attempts, qualified timing and pending actions. Unknown extension facts are retained opaquely. An unsupported core event required to compute state prevents a trustworthy fold and unsafe writes; it does not silently disappear. Projections and guards consume the typed snapshot, never generated prose.

## `story.md`

Generated on every sync from `StoryState` and `description.md`:

1. Frontmatter: schema, id, title, kind (story, epic, defect, spike), state, issue URL, parent, children, blocking, blocked-by, created, updated, last-branch, last-worktree, estimate (agent-hours, size), origin, files map, and a dense `expansions` and `trips` list (`[{id: 14, kind: defect, at: plan}]`).
2. Title and a link to the issue.
3. The body of `description.md`.
4. Generated `<details><summary>` blocks with fenced JSON: state history, guard results, expansions and trips, estimates, test receipts. A blank line follows each `</summary>` so GitHub renders the code block.

The renderer is deterministic over `StoryState`, the pinned authored blobs and schema version; the same complete inputs produce byte-identical output. Recorded update times are used, never the current render time.

## The planning backend

`GitBackend` owns writes to the configured planning ref without a checkout. Its input is a typed operation: stable ID and request digest, actor/binding, pinned policy, read-set (story versions, related-story predicates and authored path base digests), intended writes/events, and required follow-up actions. It is not an arbitrary map of replacement blobs.

1. Resolve a validated local tip and immutable inputs; validate ownership, schemas, edge legality and request identity. Acquire a clone-local transaction lock to avoid unnecessary concurrent work, but retain CAS correctness.
2. Recheck the operation's read-set against that tip and evaluate guards. A CAS miss restarts this step against the new tip. Changed user-authored input returns a conflict with both versions; a semantic request may be reevaluated only while its original intent/preconditions still hold. Never reuse a stale positive guard.
3. Build one tree with a temporary `GIT_INDEX_FILE`, `hash-object` and `update-index`. Commit the operation outcome, guard records, allowed events, related-story updates, generated views and pending action records together. A refused workflow operation records its failed guards/outcome but no transition. Integrity failures write only local diagnostics outside the damaged store. A prior explicit draft sync is a distinct saved operation, not a partial transition.
4. Create a single-parent `commit-tree` and CAS `update-ref <ref> <new> <old>`. On failure retry within bounds or report contention with retained inputs. Append order is this committed order; no event union or timestamp sort is allowed. An origin/expansion stop and both story updates share this one tree/ref transaction.

**Publication and reconciliation.** The local commit is the local operation result; publication is a separately verified result. With no configured planning remote, publication is not applicable. Otherwise push fast-forward and verify the remote tip/result, preserving uncertainty after a lost acknowledgement. On rejection fetch into a candidate and validate it. Retain the original local chain under a recovery ref plus its operation/evidence records. Replay only whole local operations whose complete read/write-set and policy preconditions still hold on the new published prefix (normally disjoint stories); reuse stable IDs, never repeat external side effects. Already published identical IDs are deduplicated. Any incompatible event, authored path, relationship or policy input stops replay with an explicit publication conflict. Never union same-story event logs or overwrite remote prose.

A conflicted local outcome remains accessible as locally recorded, unpublished evidence and is excluded from shared projections. `sync --reconcile <operation-id>` presents retained local and published versions and accepts a new scoped operation resolving the substantive conflict, with explicit supersession lineage; it cannot silently reinterpret the old result as published or erase its evidence. The original unpushed commits are retained even if the active local view is rebuilt on the validated remote prefix. Published commits are never rewritten. Uncertainty is reconciled by remote observation before retry, not treated as proof of either success or failure.

| Operation status | Durable meaning | Next step |
| --- | --- | --- |
| refused | Workflow evaluation recorded; no transition | Fix the named condition and submit a new attempt |
| locally-committed | Local operation/event snapshot established | Publish, or report local-only completion |
| publication-pending | Local result retained; remote result unavailable | Observe/retry publication by operation identity |
| publication-conflict | Original local facts retained apart from incompatible shared history | Reconcile explicitly; shared effects remain ineligible |
| published | Remote contains the validated operation | Run eligible pending external actions |

**Reads** batch immutable tree access through `git cat-file --batch`; the read API always names the snapshot. `MemoryBackend` implements the same operation, CAS, refusal and conflict semantics without spawning git, so tests exercise behavior rather than an easier blind-write substitute.

## Working on a story from a worktree

`bind <id>` reserves the story's authored surfaces and records session/binding generation, worktree, code branch when applicable, and base planning tree/blob digests in `<worktree>/.aitm/.state/<id>.json`. It materializes only allowed authored documents/attachments and read-only generated previews. Event logs, operation records, review originals and extension-owned files are not editable sync inputs; changing a preview produces a diagnostic, not a store overwrite. Extension views use their own declared route. Untracked scratch is not implicitly imported.

`sync` imports only the bound allowlist of changed authored bodies/semantic headers. It validates containment, rejects symlinks and unknown path ownership, compares each path to the recorded base and current store version, and preserves both sides of a conflict. Deletions require explicit path selection and cannot remove event history or acceptance evidence. Generated metadata is refreshed only after authored import succeeds. No body is recreated from stale generated fields. `describe` is the sole structured route for description changes; draft/idea bodies use their assigned authoring route.

Before first Develop, `bind --implementation` selects or creates an isolated story branch from the pinned code baseline and records it against the intended attempt. A planning binding does not implicitly turn the user's default-branch checkout into an implementation branch. Existing branches require an explicit binding with observed head/tree; the core never resets uncommitted work or creates/removes a worktree. After scrap it creates a fresh attempt branch and preserves the old ref/evidence; refactor retains the recorded branch. Rework in an existing attempt preserves its clock and allowance. Verification uses the matching binding/attempt generation, never whichever session happened to bind last.

`unbind` first syncs the selected authored changes, then ends that exact binding; failed sync leaves it recoverable. A crashed holder's unsynced bytes remain in its workspace and are exported before recovery. A new generation cannot make old receipts current. A pivot or trip can fence implementation activity atomically while retaining authoring material for analysis.

Draft opening takes a stable entity ID or full path (`draft open <handle>`); ambiguous slugs return candidates instead of guessing. State-changing commands perform an explicit, separately reported sync of eligible authored inputs first, then pin a fresh snapshot for their operation. Read-only commands do not acquire an authoring claim merely to inspect a story.

For a command that could continue implementation or close a passing review, the trip preflight below runs before that ordinary sync or action. Explicit export, retained-evidence ingestion and trip-analysis saves remain available while implementation is fenced; they do not authorize further implementation work.

## Local index

- Location: `<git-common-dir>/aitm/index.sqlite`, shared by every worktree of the clone, never committed.
- Keyed by the `planning` tree SHA it was built from. On each command the core compares SHAs and updates incrementally by diffing trees; a missing, corrupt or schema-mismatched index is rebuilt from scratch.
- Tables: `stories` (folded state), `events`, `files`, `ideas`, `drafts`, plus an FTS5 table over titles, descriptions, idea and draft bodies, and lessons.
- WAL mode. A decision pins one tree and a matching read transaction; it never mixes rows from two revisions. A locked, stale or broken index falls back to that exact planning tree. Concurrent rebuild swaps the indexed snapshot atomically.

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
    def __call__(self, ctx: GuardContext) -> GuardResult: ...

class Action(Protocol):
    id: str
    def __call__(self, ctx: ActionContext) -> ActionResult: ...
```

`GuardContext` contains one pinned store snapshot (including related stories), effective committed policy, typed document/evidence metadata and read-only code facts captured in preflight. Guards do no network or Markdown parsing. Actions return observed success, failure or uncertainty for their stable invocation; they never undo/refuse an already committed transition.

**Leaf forward chain:** backlog → refine → ready-for-plan → plan → develop → test → review → done.

**Edges and precedence.** The kind-specific edge table is checked before policy guards and is an integrity constraint in both modes. Design rework may move Refine/Ready/Plan to Backlog. Implementation rework moves Test/Review to Develop within the same attempt. A confirmed trip or scope pivot moves an active leaf and its affected expansion to Plan atomically. These recovery edges bypass ordinary exit and target workflow guards, retain their reason/lineage and cannot be blocked by an accepted-plan guard; integrity validation still applies. An explicit abandon/supersede/duplicate disposition may close any nonterminal story without delivered-path guards. Reopening a terminal record is a new scoped operation with reason and explicit invalidation/replan rules, not an untyped repeat of `promote`.

**Transition transaction.** First report any separate authored-input sync. Pin the snapshot, policy, code/binding and related read-set; check edge legality and kind. For a normal forward edge evaluate current exit and target entry guards in stable registration order (core first, then dependency-ordered extensions). Commit all evaluation records and either a refusal or the state change, related-story changes, generated projections and pending-action identities in one CAS operation. Enforce mode refuses on failed workflow guards. Advisory mode may advance while recording the failed conditions and an unverified disposition; it cannot fabricate passing evidence, ignore an illegal edge, claim delivery or bypass safe storage. A CAS retry rechecks the whole affected decision.

At each observed command boundary, ingest already-produced activity/evidence as retained facts, pin/recheck the attempt and evaluate confirmed trip causes before ordinary implementation mutation, new verification execution or an effective passing-review result. A detected enforce-mode trip commits the stop/demotion transaction first and refuses the requested normal action. Advisory records the trip and continues according to policy. Repeat this ordering on every CAS retry. A subprocess is checked before launch and its newly observed interval/result is retained and checked immediately on completion before any success advances the workflow; a command that arrives with a pass plus proven overrun cannot first stop the clock by declaring review passed. Late proof may diagnose a past overrun, but never fabricates a past stop. While fenced, reads/export, ingestion/reconciliation of already-produced evidence, safe authored saves explicitly for analysis, trip decisions and replanning remain available. A retained result can be shown as historical success/stale evidence without making it effective for the stopped attempt.

**Core guards for executable leaves:**

| State | Slot | Guard | Passes when |
| --- | --- | --- | --- |
| Backlog | exit | description-complete | Current structured description has title, user story and scope |
| Backlog | exit | design-accepted | Current authored-content digest has verified effective acceptance under applicable review policy |
| Refine | exit | estimated / leaf-size | Refine estimate includes agent-hours, size and priority; leaf estimate ≤ configured four-hour limit |
| Ready for Plan | exit | not-blocked | Every required dependency has a satisfying disposition, not merely state Done |
| Plan | exit | plan-accepted / trip-decided | Current plan generation/digest is accepted; all trips affecting the next attempt have recorded decisions |
| Plan | exit | jit-current / implementation-bound | JIT applies to that plan, intended attempt and pinned code baseline; intended implementation binding is valid |
| Develop | entry | not-tripped | No unresolved confirmed trip or fenced implementation generation |
| Develop | exit | story-commits / expansion-resolved | Recorded attempt branch contains story-tagged implementation commits; its expansion has a verified resolution |
| Test | exit | test-passing | Tool-produced passing receipt is current for the clean source snapshot and attempt |
| Review | exit | review-passed / delivered / signed-off | Current verified review, corresponding verified delivery and agent retrospective refer to the same source/deliverable and attempt |

`describe` takes structured `--title`, `--as`, `--want`, `--so-that` and `--scope-file`; it records authored fields/hash and renders `description.md`. Guards read that typed record, not prose.

**Advisory representation and recovery.** A transition always needs a valid store/story identity, legal edge/kind, attributable operation and unambiguous affected attempt/relations. Those are integrity requirements. Missing accepted-plan proof or implementation binding is workflow evidence/readiness: advisory may enter Develop with a stable provisional attempt ID, the current authored plan digest or an explicit absent-plan value, waived guard records and `implementation-unbound` if needed. This starts the same attempt's coverage accounting and allowance without claiming that plan acceptance exists. A write/verification command still requires an actual valid binding/source snapshot; `bind --implementation` supplies it through the normal route and cannot reset the provisional attempt. `attempt reconcile` attaches subsequently verified current plan/binding evidence to that same attempt, preserving waived history, accumulated time and consumed allowance. If new evidence instead requires scope rework, use the explicit Plan/replan edge; do not reset an attempt just to erase an advisory failure.

`done/unverified` is a terminal historical result, not delivered closure. `reopen --for evidence --reason ...` returns it to Review for the same attempt/source when the work itself is unchanged, retains the original Done/waiver events and permits evidence reconciliation and a fresh sign-off to record a later verified disposition. If code/deliverable changes are needed, take Review → Develop rework in that same attempt, invalidate affected evidence and resume its remaining clock; only an actual trip/scope replan grants a fresh attempt. No reopening operation upgrades an old unsupported claim in place.

**Kinds and related stories.**

- Story/defect use the leaf chain and implementation clock. `expanded_from` is a separate relation from an epic parent. Expansions block their origin through an explicit dependency; they are not automatically epic children.
- A spike follows the leaf planning/review flow and its attempt clock, but uses an immutable registered deliverable instead of implementation commits and test receipts. `deliverable add` records bytes/digest, reviewer evidence names that version, and delivery verifies its declared archival target. Editing it invalidates the old review/delivery for the current version.
- An epic passes design/estimate/plan gates, then enters Develop when its accepted plan and child set are recorded; children need not already be in Develop. It remains there while children work, may advance through aggregate Test into Review only when every required child has reached Review with required verification or has a satisfying terminal disposition, and reaches delivered Done only when all required children are delivered or explicitly scope-resolved and its aggregate retro is recorded. It has no implementation branch, JIT guard, clock, commits, test receipt, PR or independent delivery requirement. Aggregate Test is a checkpoint over child evidence, not an epic test command. Changed child scope invalidates the relevant aggregate plan/closure assessment.
- Parent/child edges are reciprocal and acyclic; dependency edges are directed (`A blocked_by B` means B must satisfy A's need), reject self-links/cycles, and are updated together. `done/delivered` satisfies a dependency. Abandoned, duplicate or superseded requires an explicit scope/disposition resolution recorded by the affected dependent; duplicate/superseded also follows a valid replacement without cycles. A failed or abandoned expansion does not silently resume its origin as fixed. All related facts come from the transaction's snapshot.

**Actors.** Record observed harness/session identity and whether it is runtime-observed, declared or unavailable. CLI/TTY heuristics may attribute an actor but are not authentication. `pivot` refuses known agent/tool invocation; a genuine interactive human invocation is the sole human-only path. `--as-human` cannot override a detected agent session. This is limited on a single-user machine where an actor can imitate environment/TTY state; optional harness deny rules add a backstop, not proof. No other routine transition adds a human gate. Core commands never call a model; the harness agent supplies authored reasoning and retrospective input.

### Document acceptance, review import and JIT

`aitm.authored-content/v1` computes SHA-256 over UTF-8 [RFC 8785 canonical JSON](https://www.rfc-editor.org/rfc/rfc8785) containing schema identity, story, role, semantic header map and the exact authored body string. Parse only a schema-defined JSON-compatible subset of YAML (reject duplicate keys, aliases/tags and invalid values). Preserve body bytes decoded as UTF-8 without whitespace or Unicode normalization; exclude only the schema's generated header keys (`created`, `updated`, `last-branch`, `last-worktree`, `status` for `aitm.doc/v1`). Title, role, story, source references and all semantic fields remain covered. Unknown header fields are not silently excluded: unsupported schemas/fields require validation or a versioned schema migration before acceptance. Core exposes this one canonicalizer and test vectors to peer-review. Raw full-file SHA-256 and patches remain separate reconstruction evidence. A version change requires an explicit proven binding migration, never a claim that a new digest was historically reviewed.

`review import <folder> --story <id> --doc <path>` accepts typed portable records (and mapped native originals), replays base plus numbered patches, checks every reviewer input/author output digest, finding/disposition coverage, round order, final decision and final bytes, and produces a validated review record. A round-cap record is retained as unaccepted evidence. Each level binds only its own reviewed content; earlier SAR/SPR does not approve later XPR edits. `design accept` / `plan accept` consume this verified record and the configured required levels/exception policy, comparing canonical digest with the current authored document and recording exact provenance. They do not accept an arbitrary path or caller-provided `accepted=true`. The recommended review-depth matrix remains unconfirmed; init must record an explicit applicable policy before a guard can assert its requirements are satisfied. In advisory mode missing policy is reported as unknown/failed, not inferred as acceptance. Core-only M1 can import manual portable reviews without the later peer-review extension.

The validator also checks participant topology and provenance: SAR has one selected review worker from the author's current provider (independence is not claimed); SPR requires author and reviewer to have distinct sessions in the same provider; XPR requires distinct provider families and participants. Validate continuity across turns or an explicitly recorded, policy-permitted participant replacement. Compare raw IDs/fingerprints only through a documented identity mapping; an uncomparable identity is unknown, not proof of distinctness. Policy separately names permitted assurance kinds, such as declared manual records, ordinary native consensus with authority unavailable, or independently attested evidence. Contradictory provider/session claims, missing required identity evidence, no-commit test mode where normal mode is required, or disallowed assurance cannot satisfy a level even when all file hashes match. Retain those records as useful unaccepted collateral/timing evidence. M1 manual records work under an explicitly recorded policy allowing their declared assurance; no stronger assurance is invented. Migration preserves the v0 native XPR's unavailable authority and declared identity/model evidence. Neither this validation nor migration chooses the still-open required-level matrix.

The import transaction holds the authoring reservation, checks expected current FUR/base and existing collateral digests, and writes only that story's revised FUR, review folder and core-owned story metadata/events/operation record. It rejects foreign paths, executable setup, scratch, overwrite of native originals or a stale authored base. It does not require a retained review branch or intermediate Git objects. The review's original patch base and a later upstream integration base are separate provenance: replay must reconstruct the actual accepted result, while import must compare against the refreshed store base. Metadata is regenerated only after an accepted raw snapshot is retained/reconstructible and bound to its canonical content. M1 supplies this route before retiring the planning checkout; M1–M4 reviews use temporary distinct review refs plus this writer.

`jit` records the current accepted plan digest/generation, intended attempt, pinned code baseline and explicit touched-path/dependency coverage. An unchanged baseline is applicable. A descendant baseline is applicable only when coverage is complete and no intervening change touches the declared dependency set; missing/incomplete coverage, non-descendant history or unavailable freshness requires a fresh JIT, not automatic acceptance. A plan revision made by JIT goes through the applicable review/acceptance policy before Develop. Unrelated changes can pass without exact-tip equality. A stale JIT, old plan digest or previous attempt cannot satisfy the guard by existence alone. Refine/Plan/JIT estimates remain separately recorded; a new attempt starts only with the recorded new plan generation, not every re-entry into Develop.

### Verification, delivery and sign-off

`test` captures policy/command, attempt, binding, clean head/tree and tool execution output. It refuses to certify a dirty tracked tree or unaccounted test-input files; the test lane defines the input manifest, including relevant untracked fixtures, and uses an isolated snapshot when needed. It checks source identity before and after execution. A moving head or changed inputs yields stale/inconclusive evidence, even if the subprocess exited zero. Retain exit/result, output hashes and observed execution interval in core-owned receipts; a retry reuses execution identity or records a new run, never manufactures a missing success.

`review pass|changes --evidence <record>` imports a verifiable review result for the same source/deliverable, attempt, reviewer identity and applicable policy. Core validates the record and source binding; provider CI/approval claims require provider observation, while a core-only agent review has its retained signed-by-session/declared provenance and explicit assurance. Bare pass assertions are not authoritative evidence. New source bytes or a changes/rework verdict supersede current review/verification applicability. The original evidence stays in history. The implementation clock stops at a valid passing review; rework reopens the same attempt's remaining clock, without resetting its used allowance or erasing earlier time.

`deliver` observes a declared target and records a verified mapping from reviewed source to target result. A local-only core supports a local Git merge target with positive content verification. For fast-forward, verify the exact reviewed source/tree landed. For a merge, pin the pre-target, reviewed source and merge base, compute the permitted clean integration tree for their reviewed delta, and compare the delivered tree and parent mapping against that result. Ancestry alone is insufficient: an `ours` merge, discarded reviewed changes or unreviewed conflict resolution does not pass. Conflict resolution or any non-permitted transformation requires review of that exact resulting content before delivery can be verified. Core-run squash/rebase likewise records and verifies the approved source-to-result transformation against pinned inputs; strategy names alone are not proof. Externally performed squash/rebase without adequate mapping remains pending until verified evidence exists. For a spike, the archival target confirms the exact registered deliverable bytes. Remote target claims require the git-host capability below; absence/offline status is pending, not proof. Issue closure alone is never delivery. Core does not automatically merge just because review passed; delivery follows the task's actual authority.

Before an authorized core-run target mutation, persist a stable delivery operation with pre-target ref/head, reviewed source/delta, method, approved expected tree/commit and attempt. Publish that intent first for a shared target, then update the target using its expected-old-head CAS. A crash after target update but before the planning receipt is reconciled by observing that exact expected result/operation in the target history; do not run a second merge. A competing target update, lost observation or unverified transformed result remains pending/conflicting with its original evidence. This retained intent also supports recovery when the target later advances normally; existence of a dangling commit alone is not evidence that it landed.

`signoff --retro <path> --confidence <1-5>` is agent authoring plus one coherent closing operation: verify current review/delivery, import the retrospective and digest, record sign-off/outcome and Done disposition, end implementation sessions and resolve related expansions/dependencies where permitted. The retro covers design/plan/implementation alignment, lessons, planning misses and confidence. It does not wait for a human. An advisory override may record `done/unverified` with missing conditions and cannot become delivered evidence or satisfy a delivered dependency. Non-delivery terminal commands retain abandoned/superseded/duplicate reasons and do not require fabricated delivery receipts. `discuss` exports context and a suggested harness invocation; it does not call a model or gate closure.

**Evidence recovery.** Operations retain their source hashes, output artifacts and provider/execution identity before projecting derived summaries. `evidence reconcile <id>` rebuilds lost derived receipts from retained authoritative results with recovery lineage; if proof is insufficient it reruns supported verification or observes the exact remote result. It never turns missing proof into a pass. Uncertain non-idempotent external actions are reconciled before another attempt. Actual failed tests, unreviewed bytes or unverified delivery remain substantive conditions, distinct from repairable bookkeeping.

### Resident actions and publication

Every initial/normal/terminal state entry writes pending action records in the same transition transaction, with key `(operation, owner, action-id, target-version)` and implementation/schema version. Crash before the first call is therefore discoverable; `sync` or `actions retry` scans pending/uncertain entries. An attempt records its result or uncertainty with the same key. A missing/disabled owner retains the action as unavailable; it is not marked complete or discarded. Core terminal session closure is atomic with the state operation, not delegated to a losable callback.

Local projections can run from committed local state. Shared backlog projection is eligible only after the corresponding operation is verified on the configured shared planning ref, and always reconciles the latest published story state rather than blindly replaying an old snapshot. Its provider must either enforce monotonic version/idempotency semantics or use one designated projection authority per store with a serialized durable queue and crash recovery. A second authority must be fenced before takeover; when the provider cannot support safe takeover, it reports pending/manual recovery instead of concurrent writes. The provider re-observes after ambiguous acknowledgement and suppresses superseded queued versions. No old retry may roll the board backward. M2 owns the endpoint-specific mechanism and must demonstrate this contract. A local backlog provider's no-op projection still produces a recorded completion.

Push and action results are separate from workflow outcome. Local commit succeeds even if publication/projection fails; output names all three states. Shared side effects of unpublished/conflicting operations stay ineligible. State-entry cadence is sparse: ordinary reads/telemetry do not generate a new board projection, though they may retry an already pending action.

## Expansion and trip rules

**Attempt and clock boundaries.** Only implementation is limited: a new accepted plan generation plus first Develop entry opens an attempt with the four-hour limit and one expansion allowance. Test/Review rework returns to Develop in the same attempt. A confirmed trip or scope pivot closes/fences that attempt; a replacement accepted plan opens a fresh one. Refactor may keep its branch; scrap preserves the old branch/evidence and uses a fresh branch. Each expansion has its own attempt clock and no expansion allowance. Origin intervals are paused while its expansion is unresolved. A valid passing review stops implementation time; later rework resumes the remaining budget of the same attempt. Planning and post-pass retrospective time never enter a trip calculation.

**Activity and coverage.** Activity records carry producer/event identity, session/binding, attempt, interval or observation point, source, occurrence/recording times, freshness and coverage. Deduplicate by source identity; mismatched duplicates are integrity errors. Merge overlaps for the same actor/session and intersect them with state/attempt/pause boundaries before summing. Reject negative/skewed intervals as invalid/unknown and retain them for diagnostics. Late telemetry may refine measured history but does not reorder workflow events or retroactively pretend a stop already occurred.

The provisional 15-minute gap rule counts only successive eligible agent-activity observations in the same session/attempt separated by at most that gap. It is an estimate of the gap, not proof that the whole interval was engaged. Longer or unobserved spans remain Unknown rather than zero; human inspection, idle open sessions and other bindings do not count. Reports separate observed coverage, estimated/partial coverage and Unknown, with bounds where supportable. An enforce-mode timeout requires sufficient observed engagement to establish the limit was exceeded; an estimate alone reports a possible overrun and missing coverage. Core-only CLI observations normally provide partial coverage plus actual tool-run intervals, not a claim to detect all outside work. Checks happen at the next observed command and direct the agent to stop then; hooks are optional and cannot make an unseen event observable retroactively.

**Planning and document-review time.** Planning has no limit, but Refine/Plan/review effort is recorded for calibration and usage reporting. State/actor-qualified activity produces planning estimates with the same coverage limits. `core.doc-review.submitted` records each response and `core.doc-review.completed` records the level, distinct from a code PR verdict. Report elapsed response spans by level, role and model; label them as elapsed spans/estimates, not necessarily continuous engaged agent-hours.

Each turn has `start_basis`: `recorded` for a true per-turn participant start, `claim` for a claim tied to that turn, or `prior-submit` as a fallback proxy. `unknown` is used when none is defensible; retain an end without inventing a duration. Native ai-peer-review 0.4.x participant registration timestamps reused across rounds are not per-turn starts. Import uses exact-turn native claims, then the preceding turn's submission, retaining source paths/digests and basis. A proxy spanning waiting is identified as such. Turn spans concern response work and exclude separately identified setup, pre-claim reading and publication; the level's start/end is an outer elapsed bound, not the sum of engagement. Merge overlapping spans/activity for the same actor/session so the same work is not double counted. Distinct agents may work concurrently: report both summed agent-time estimates and elapsed wall-clock union, never silently collapse two agents into one. Breakdown totals reconcile via explicit attribution of overlapping activity to review spans first.

`review turn`, `review complete` and `review import` validate response/manifest and digest/finding lineage, preserve original participant/session-kind and timing basis, and append their fact records idempotently by level-record identity plus round/role. Same identity with changed bytes is a conflict, not a skip. Backfill retains original occurrence time, recording actor/time and readable immutable provenance; it contributes to historical reporting without moving the current state backward. These facts alone do not constitute `core.doc.accepted`.

**Live turn lifecycle.** `review open --story --doc --level` creates a stable level-record ID and initial capsule before any turn, without starting a model or requiring the FUR to be committed. `review turn --record <id> --response <file>` imports an immutable response copy and its input/output content identity, participant metadata and available timing anchors into that story's review folder through the core writer, even while work continues on a separate review branch. It can record a provisional turn without a final manifest; validate schema, containment, source hashes and known predecessor links now, mark final patch/digest/finding closure pending. `review complete` or final `review import` supplies/verifies the full patch chain and manifest and appends completion; only a subsequent verified acceptance operation can satisfy a design/plan guard. Native review files are copied only after their own submission and never edited by this importer.

Turn identity is `(level-record ID, round, role)` with an immutable normalized source fact digest. Its recording actor/time and backfill/derivation envelopes are separate append-only provenance. Live ingestion followed by import of the same normalized response is the same turn, not a second duration. Changed source bytes under that identity are a conflict. Legacy records without a level ID receive a deterministic import identity bound to document, level and original source-record identities; retain the alias mapping so live/backfilled/native/portable copies do not duplicate the same turn. A later better timing interpretation is a versioned correction referencing the original fact, never an overwrite or duplicate turn.

Each timing basis is reproducible: `recorded` references the exact per-turn start record; `claim` references a public native claim record tied to the turn; `prior-submit` references the preceding submitted response and digest. Persist the minimal safe anchor records alongside the response (never private provider handles or wholesale runtime scratch). If the native adapter cannot yet export a claim, leave that anchor unknown until completion supplies public evidence. A backfill whose selected start differs from its response header retains that derivation and predecessor/claim source too. The real v0 XPR migration reconstructs these references from the retained public manifest and predecessor response; the original simplified backfill envelope is preserved rather than relabeled complete proof.

A prior-submit or interrupted turn may bound setup, waiting, pre-claim reading or publication as well as response work. Such an outer span is not added as measured response-writing time. Subtract separately evidenced excluded intervals; if the remainder cannot be established, report response duration Unknown with the proxy bound and basis count. Preserve those exclusions/coverage in state/role/model breakdowns. Split proven intervals at observed state boundaries for per-state reporting; ambiguous boundaries receive unallocated/Unknown attribution. Count each same-session interval once, then sum distinct agents separately from wall-clock union. This preserves the owner's response-only timing boundary without treating an imprecise anchor as exact work.

**Expansion transaction.** `expand <id>` first reserves an operation and the origin's single allowance against its exact attempt/state; no issue creation occurs before that reservation is valid. The recoverable identity protocol below obtains the child identity. Finalization commits child initialization, `expanded_from`, origin block/pause and expansion event together, validating the reservation against trips, closure or pivots. If external issuance succeeded after the reservation was invalidated, preserve the issued identity and report a pending reconciliation disposition; never issue another item or silently discard/attach it. Only a delivered or explicitly disposition-resolved child can clear the origin block and resume its clock. An abandoned child requires a recorded plan/scope resolution, not an automatic success.

**Confirmed detections and open policy.** One expansion per attempt and no nested expansion are settled; a second/nested request and an observed time-limit violation are detected by core. The owner's broader phrase, a used slot with the origin still incomplete, needs interpretation; merely continuing the accepted origin plan after a successful expansion is not silently declared a trip by this design. Ambiguous cases are recorded as unresolved policy observations with current evidence, not labeled confirmed trips. The proposed second-trip cap is unconfirmed and is absent from defaults and unconditional acceptance tests. These existing owner choices remain open; this review does not settle them.

For a confirmed trip, one transaction records the trigger on the origin with affected attempt, stops/fences its implementation generation and that of an open expansion, pauses/closes clock segments and moves affected active leaves to Plan. Ordinary plan-entry guards cannot prevent the stop. The triggering work request is refused in enforce mode; advisory mode records/reports the trip without silently ending sessions or moving stories. Re-observing the same cause/attempt is idempotent. A concurrent completion, pivot or expansion operation must re-evaluate against this commit and cannot resurrect the old attempt.

The agent writes `plan/trip-<attempt>.md` and records `trip decide --decision scrap|refactor --analysis <path> --rationale ...` with `--expansion continue|fold|abandon` when needed. No human approval is required. The decision atomically resolves or carries the expansion relation: continue retains the same child identity and makes its resumed attempt consume the origin's new attempt allowance; fold/abandon records the child disposition and clears only the corresponding block, with its remaining work explicitly in the replacement plan if applicable. New independent dependencies are not erased. A fresh plan acceptance is required before a new attempt. Abandoning/pivoting an origin likewise records the child disposition or explicit continuing independent ownership and clears/resets links coherently, rather than leaving orphaned active work.

**Learning outcomes.** Core retains Refine and Plan estimates with their design/plan versions, JIT revisions separately, and a Close outcome binding attempted/delivered source, measured or qualified actuals, expansions/trips/pivots, follow-on defect links and retrospective lessons. Usage events include source/provider/model/session, units, token/cost availability and deduplication keys. Missing cost/time stays unavailable. Imported, partial and incomplete triads remain identifiable and are excluded from complete-triad calibration by the rubric. Planning time, review elapsed spans and implementation engagement remain separate measures; no planning measure triggers a trip.

## Providers

Core defines capabilities, typed results and replay obligations; endpoint details belong to extensions.

```python
class BacklogProvider(Protocol):
    name: str
    def prepare_identity(self, operation: GraduationIntent) -> IdentityReservation: ...
    def create_or_reconcile(self, reservation: IdentityReservation) -> IdentityResult: ...
    def project_latest(self, publication: PublishedStory, action: ActionKey) -> ActionResult: ...
    def issue_url(self, ref: IssueRef) -> str: ...

class GitHostProvider(Protocol):
    name: str
    def fetch_candidate(self, ref: RefIdentity) -> FetchResult: ...
    def publish(self, intent: PublicationIntent) -> PublicationResult: ...
    def observe_delivery(self, request: DeliveryRequest) -> DeliveryResult: ...
    def observe_review(self, request: ReviewRequest) -> ReviewResult: ...
    def file_url(self, ref: RefIdentity, path: str) -> str: ...
    def commit_url(self, sha: str) -> str: ...
    def default_branch(self) -> RefIdentity: ...
    def protect_branch(self, branch: str, rules: ProtectionRules) -> ProtectResult: ...
```

Identity results distinguish reserved, issued, uncertain, absent-with-proof and failed; delivery/review results distinguish verified, pending, rejected and unsupported with evidence. Protection reports applied/already-protected/manual plus instructions/URL. Publication reports observed remote tip and operation containment rather than interpreting process exit alone as success. A separate built-in local Git transport can publish/fetch configured planning refs without a hosted API; `githost=none` means no host capabilities, not a silent promise that a configured remote was updated. Local delivery verification is a core capability. Remote approval, CI, PR, squash/rebase mapping and hierarchy projection remain provider responsibilities with source/target/version binding.

**Graduation.** Before external creation, core commits a stable operation key, frozen draft snapshot, selected provider/repository identity, reservation and expected finalization preconditions. In a shared store this intent must be published before an external side effect. The provider must reconcile that key to one permanent identity after an uncertain create; it may use an existing remote correlation record or a provider-supported idempotency mechanism but cannot assume a generic endpoint has an idempotency parameter. Unknown results remain pending and are observed before any new create. The provider must document what constitutes proof of absence. A retry never blindly duplicates an issue.

Reservation is not dispatch ownership. Before a non-idempotent create, a sender acquires a distinct durable dispatch claim for that intent through the shared store's CAS/publication order; only its verified published holder may send. Two clones resuming one intent cannot both acquire it. A provider with proven request-key idempotency may safely share retries under that same key; otherwise an uncertain/in-flight dispatch is observation-only. Timeout or absence of a correlation marker is not proof that the old sender cannot still issue. Re-dispatch/takeover requires positive evidence that the prior sender is fenced/terminated and no delayed request can complete, plus provider-specific proof of absence; if that cannot be established, retain pending identity instead of creating again. Claims and observed outcomes survive restarts and are reconciled by the exact operation ID.

Once identity is verified, one CAS operation moves the exact draft snapshot, creates the numbered story with initial events and links, queues initial projection and marks the identity operation finalized. Concurrent edits retain the newer draft bytes and require reconciliation rather than moving them under the wrong description. The returned story ID is exposed only from this durable finalization; an already issued remote identity remains retained if finalization cannot proceed. Expansions use the same protocol plus their reserved allowance. `graduate resume <operation-id>` is the normal recovery route. A permanently canceled intent retains any issued identity and records its explicit disposition instead of renumbering or deleting evidence.

The **local backlog provider** allocates the next number and initializes the story in the same authority transaction; a CAS retry rechecks allocation before exposing an ID. It supports no-remote single-clone stores and shared stores with one configured allocation authority. Other clones of a shared local-numbered store cannot allocate offline or pretend their local CAS is global serialization; they must route graduation to that authority or wait. Store identity and authority generation are recorded in `store.json`; takeover must fence the former writer.

For a shared local-numbered store, final allocation/initialization must be accepted at the shared planning ref with the current authority generation before the permanent ID is exposed as issued. An offline stale allocator cannot satisfy that publication predicate; it may retain a draft/reservation but must not return an issued ID. Handoff serializes the generation update at that same authority, so an old generation's publish loses its CAS/precondition check. A no-remote single-clone store still allocates atomically and exposes its ID on local commit, with no invented network prerequisite. Existing GitHub-numbered stories retain their provider/repository identity during migration; no fallback to local numbering or in-place renumbering is allowed. A core-only install may preserve/read imported provider references while new remote issuance remains unavailable until its provider is installed/configured.

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

At load, validate core/dependency versions and immutable registration IDs. Resolve extension dependencies topologically, with namespace/registration ID as the stable tie-breaker; cycles or missing required owners are configuration errors. Record the resulting versions/order with each operation. Installed distributions are not automatically enabled: only the committed effective policy selects them.

Core reserves `core.*`, store/operation/repair metadata, all story event logs and generated surfaces, review-import/acceptance metadata and its evidence namespace. Extension paths are normalized relative to `.aitm`, checked for actual glob overlap with other owners and core-reserved paths, and cannot traverse, follow symlinks or change path type. Every persisted write/event passes the transaction boundary with the submitting owner identity and schema version. A capability permits only that owner's declared file patterns and typed event namespace; an action cannot acquire another writer's path merely by using ordinary sync. Review body authoring uses its distinct reservation rather than a broad extension path claim.

Extensions are trusted in-process Python, not sandboxed hostile code. Ownership validation protects writes made through core and detects invalid imported history; it does not claim to stop malicious Python from invoking git itself. Guards remain pure/local and extension logic cannot make core call a model. Transport adapters all invoke the same typed core functions.

Unknown/disabled extension records are retained byte for byte and displayed as opaque data with owner/schema status. Core can fold its own state without pretending those facts passed an extension guard. If active policy requires an unavailable guard/action/schema, report unavailable: enforce cannot pass that condition, advisory records the failure, and pending external actions remain pending. Unsupported core events needed for state are an integrity refusal, distinct from opaque optional extension facts. Removal never deletes old files/events, grants their namespace to another package, or marks pending work complete. Upgrades provide versioned event/action adapters or keep affected work unavailable; replay records the original versions and never silently runs a changed action under an old key.

## CLI

Every command has a versioned `--json` result with operation ID, local outcome, publication outcome, pending actions, evidence/freshness and recovery command. Exit 0 means the requested local operation completed (including advisory advancement with explicit failed guards), not that a remote write happened. Refusal, conflict and integrity/input errors are distinct nonzero codes. A requested remote completion that is pending returns a distinct retryable nonzero result while preserving `locally-committed=true`; a retry by operation ID cannot duplicate the local operation. Human-readable output states the same distinctions.

| Group | Commands / typed core operations |
| --- | --- |
| setup | `init [--local] [--default-branch] [--review-policy]`, `doctor`, `index rebuild`, `planning validate`, `planning repair`, `migrate v0 --dry-run` / `--apply --expected-tip` |
| ideas | `idea add`, `idea list`; stable handles returned |
| drafts | `draft new`, `draft open <handle>`, `draft discard <handle>`, `draft list` |
| stories | `graduate <draft-handle>`, `graduate resume <operation-id>`, `describe`, `show`, `list`, `search`, `explain`, `link`, `discuss` |
| work | `bind [--implementation] [--recover]`, `unbind`, `sync [--push] [--reconcile <operation-id>]`, `actions retry`, `evidence reconcile`, `attempt reconcile` |
| lifecycle | `promote [--to]`, `demote --to --reason`, `abandon --reason`, `reopen --for evidence --reason`, `estimate`, `design accept --review`, `plan accept --review`, `jit`, `test`, `review pass\|changes --evidence`, `signoff`, `deliverable add`, `deliver` |
| document review | `review open`, `review turn --record --response`, `review complete`, `review import <folder> --story --doc` |
| rules | `expand`, `trip decide`, `pivot` |

`explain <id>` names the pinned state/policy, next kind-appropriate edge, each guard's pass/fail/unknown reason, pending side effects and the exact next command. It never presents an unobserved condition as passing. `discuss` produces the context packet/command only.

**Core-only executable walk.** In a new temporary code repo with an initial default-branch commit, `init --local --default-branch <ref> --review-policy <fixture-policy>` creates the store/config/hooks; commit its generated config/gitignore on that local default branch, then re-run init to verify ready/idempotent. The fixture policy explicitly selects the levels used by the test; it is not an implicit product-wide review-depth decision. Create an idea and draft, open/edit that stable draft handle, graduate it through the local authority, bind for planning and describe it. Import a genuine portable design review and accept its verified digest; promote to Refine, record an estimate and advance through Ready to Plan. Author/import the plan review and accept it, record the Plan estimate, then select an implementation branch/binding and record JIT against its code baseline. Promote to Develop, make a real story-tagged change, move to Test and run the configured test over the recorded clean input. Promote to Review, import a real independent code-review record, deliver to the declared local target (observe an authorized merge, or explicitly authorize the core local-delivery operation), then sign off with an agent-authored retro. `show`/`explain` must show delivered Done, exact evidence and local-only publication. The negative cases below use missing/stale/failed real evidence, never a fake pass flag.

Manual current reviews and native provider records are imported through documented schema adapters. Core generates doc-review facts as `review turn`/`review complete` receives each record; importing older records uses backfill provenance. No GitHub or model SDK is required for this local walk, and no hidden human approval or test receipt authoring step is inserted.

## Performance budgets

- `show`, `list`, `explain` with a warm index matching the pinned validated local tree: under 150 ms on the documented laptop fixture.
- Local transition evaluation/commit: under 1 s. Report remote preflight fetch, provider actions, verification subprocesses and push separately and also report total command wall time; excluding them from the local budget never hides user-visible delay.
- Unit suite: under 10 s with MemoryBackend/fake providers, no spawned git/network.
- Integration lane uses real temporary repositories for concurrency, remote rejection, hooks, recovery and migration. Cold index rebuild has its own measured corpus/time result rather than the warm-read claim.

## Migration from the hand-built `v0` files

`migrate v0 --dry-run` pins the actual planning tip, validates the legacy root/chain and all files, and emits a migration inventory/plan without changing the ref. It can inspect the existing planning checkout, but apply must wait until that checkout is released with its uncommitted work preserved. `--apply --expected-tip <sha>` revalidates the exact tip and checkout exclusion, computes the complete new tree off-ref, validates it, and CAS-publishes one cutover commit. A crash before CAS leaves no partial store; a crash after CAS is recognized by the stable migration ID/input digest. Reruns return that result without fresh events/IDs. If the tip changes, regenerate and inspect the new plan instead of overwriting it.

The migration adapter recognizes the actual hand-built schema rather than guessing from current names. For #1/#2 it maps `core.state.entered` to an initial state fact, pairs `core.link.child-added` and `core.link.parent-set` into one consistent relation, preserves the original draft-origin facts whose story is null, and normalizes actor key spelling while retaining the original payload. It handles equal timestamps in original per-file append order and transaction/link provenance, not by random new IDs or timestamp sorting. IDs derive deterministically from source snapshot/path/line/content. Preserve original time precision and mark imported/retroactive observations; adding modern fields never upgrades measurement coverage.

Legacy story headers are a one-time documented migration input for fields absent from events, with source references and conflict checks. Never parse their generated details blocks as a second event authority. Preserve descriptions/attachments, provider issue URLs and original identity scope; enumerate design/plan/review files from the tree even when legacy `files` arrays are empty. Unknown or contradictory material is retained in the inventory and blocks only an unsafe cutover; it is not dropped or converted into invented facts. Unsupported optional records may remain opaque under explicit schema status. Core-only migration preserves existing GitHub IDs and reports unavailable new issuance until that provider is configured.

Before refreshing any document metadata, replay each portable accepted v0 review to its exact accepted raw snapshot, retain its originals/patches and compute the canonical binding under the explicit v0-to-v1 authored-field mapping. Record both schema/digest identities and source proof; an existing draft or a different later file is not accepted because a historical record exists. Retain older SAR/SPR and newer XPR bindings separately. Unsupported or incomplete review records remain unaccepted evidence. M1 review import and this migration share the same canonicalizer and adapters.

The existing backfilled architecture doc-review events are preserved with `backfill` blocks, original actor/session-kind and claim/prior-submit timing basis. Check every source exists and freeze its digest; reconcile those events with their portable/native records instead of appending duplicates. Missing source or contradictory timing is retained as unavailable provenance requiring reconciliation, never calibrated as complete measured work. The source record identity also deduplicates later `review import`.

Cutover removes the legacy root README from the active tree after preserving its content/provenance inside `.aitm`, records the verified legacy baseline and migration receipt, and regenerates story views from the mapped typed data. Existing Git history is not rewritten. Tests use copies of the actual hand-built #1/#2 fixtures, including the backfilled review events, empty file inventories, same-time state events, relationships and raw SAR/SPR/XPR patch records. The resulting current store is valid under normal v1 rules; the legacy baseline remains independently explainable to a fresh clone.

## Acceptance

The core is complete only when a temporary repository with `aitm-core` alone demonstrates the nominal walk and failure cases below. Provider integration adds contract tests for capabilities it implements; M1 does not claim unimplemented hosted behavior.

| Area | Required proof |
| --- | --- |
| Init and policy | Configurable orphan planning ref and initialized store UUID/authority anchored in committed code policy; fresh clone verifies that anchor; explicit no-remote bootstrap; existing hooks/config preserved; repeat init unchanged. A story edits mode, test command or routing and still cannot change effective committed policy. Missing/invalid/stale policy has the specified result. |
| Local lifecycle | The complete CLI walk above with real artifacts; enforce refuses missing conditions. Advisory Develop with missing plan/binding recovers through binding/attempt reconciliation without resetting time; Done/unverified can reopen for evidence and later sign off without rewriting history. No routine human sign-off. |
| Operations and concurrency | Eight disjoint stories × 50 syncs retain all work. Same-story transitions, trip versus promote, stale authored import, dependency changes and cross-clone divergence either serialize under rechecked inputs or retain explicit conflicts. Duplicate IDs with different payloads fail. |
| Binding and snapshots | Competing binds and stale generations cannot redirect a branch or overwrite bytes; recovery retains unsynced work. Concurrent index rebuild never mixes snapshots; corrupt/missing cache gives equivalent pinned-tree queries. |
| Acceptance and JIT | Authored edits invalidate current acceptance; generated metadata does not. Patch reconstruction, per-level digests, participant topology/continuity, allowed assurance, finding coverage and stale-base import are checked; a well-formed SPR with identical sessions or XPR with identical providers remains unaccepted evidence. JIT rejects changed plan/attempt, missing coverage and relevant code changes; unrelated complete-coverage changes can pass. |
| Graduation/expansion | Lost issue response, repeated create and concurrent expansion requests reconcile to one identity/allowance; atomic finalization updates every related story. Two clones resuming the same issued intent cannot dispatch twice. Local allocation has one authority; a stale/offline allocator after handoff cannot expose a shared permanent ID before valid publication. |
| Trip and attempt | Second/nested expansion request and demonstrably observed timeout produce the confirmed cause. Enforce atomically stops affected implementation and demotes to Plan; advisory only reports. Trip preflight precedes a simultaneous pass/transition and is repeated on CAS retry; completed subprocess evidence is retained without granting continued work. Rework keeps attempt/budget; new accepted plan resets them. Existing expansion-boundary and second-trip-cap questions are not silently implemented or asserted. |
| Timing and outcomes | Sparse CLI observations stay partial/Unknown; duplicate, late, skewed and boundary-crossing intervals retain coverage. Planning time never trips. Refine/Plan/Close lineage, usage and lessons preserve incomplete/imported status. |
| Document-review timing | A real level opened before its first turn, live `review turn` plus completion/import, and backfill of the same portable/native records produce identical normalized turns, qualified totals and basis counts. Predecessor/claim anchors reproduce derived starts; interrupted turns, state-boundary spans and unknown/excluded work remain qualified. Same-session overlaps are deduplicated, distinct-agent concurrency and wall time are reported separately; registration-time reuse or unavailable starts never becomes exact engagement. |
| Evidence/delivery | Dirty/moving source, stale review or lost receipt cannot certify a new version. Retained proof reconstructs bookkeeping; absent proof causes observation/rerun. Local delivery rejects ancestry-only/ours merges and unreviewed resolutions; a crash after target mutation reconciles the retained intended result without a second delivery. Unavailable remote delivery remains pending. Sign-off/Done and session closure are coherent. |
| Kind/disposition | Mixed-state children do not block an epic's initial Develop or require epic PR/tests. Abandoned dependencies need explicit resolution. Changed spike deliverables invalidate prior proof. Relationship cycles and orphaned expansion transitions are rejected. |
| Actions/publication | Crash before first action call, lost remote ACK and overlapping projections retain discoverable work; replay suppresses stale writes. Local result, remote publication and projection statuses remain distinct. Missing action owner is visible/pending. |
| Store safety/repair | Hooks and core reject ordinary outside-path/merge/ancestry violations; distinct review branches work. A verified forward repair and legacy cutover pass validation in a fresh clone using an independently committed code-policy legacy anchor and non-self-referential payload-tree receipt; racing push revalidates; shared ancestry stays fenced for owner intervention. |
| Extensions | Core-path/glob overlap, event mismatch and symlink escapes fail at write boundaries. Disabled/old-version extension records round-trip unchanged, pending actions remain visible, and unsupported required core state fails safely. |
| Migration | Actual #1/#2 v0 fixtures, backfill sources and review snapshots survive deterministic all-or-nothing cutover; rerun after interruption is idempotent; no false acceptance, renumbering, fabricated precision or data loss. |
| Performance | Warm-read/local-transition budgets and separately measured remote/total timings are met on declared fixtures. |

## Left to the builder

- Module boundaries inside each folder, helper names, and test layout.
- Event-ID library and internal helpers, provided stable identity never substitutes for causal order and migration IDs remain deterministic.
- Bounded retry counts and jitter, preserving the specified read-set, conflict and retained-evidence semantics.
- `--json` output schemas, provided they are versioned and documented.
- Exact wording of CLI messages, provided every refusal names a supported next action and uncertain/publication states remain explicit.

The existing owner questions on expansion completion, second-trip cap and review depth remain open. Endpoint-specific remote projection/identity/delivery mechanisms belong to their provider design and must meet these interfaces; the GitHub every-push audit mechanism remains unresolved. No implementation or later section is accepted by this document review.
