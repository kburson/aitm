---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "981b8d77e2e988e9ec3f79768c7c9728cb66c11a"
artifact_digest: "sha256:2a31083b0095233d9d2d8ba1bc11d3054bd43fe977b6f90376eda9e8593d4026"
agent:
  host: "codex"
  provider: "openai"
  model_id: "gpt-6.1-sol"
  effort: "high"
reviewer_session: "01a1be88-ab35-75f0-aa41-1f21e6062d95"
started_at: "2026-11-09T04:20:01Z"
submitted_at: "2026-11-09T04:22:52Z"
finding_ids:
  - R1-F001
  - R1-F002
  - R1-F003
  - R1-F004
  - R1-F005
  - R1-F006
  - R1-F007
  - R1-F008
  - R1-F009
  - R1-F010
  - R1-F011
  - R1-F012
  - R1-F013
  - R1-F014
answered_finding_ids: []
---

## Summary

**Revisions requested.** The full first-round review covers the exact FUR in the header. I checked it against the story #1 decision record and accepted architecture, the story #2 draft, the store layout and actual hand-built #1/#2 records, the interim peer-review procedure, and the context-only master plan. The selected manual SAR procedure governs this round. The installed peer-review help exposes SPR and XPR. The reviewer session is this Codex thread's observed identifier.

The core has a coherent package boundary and walking-skeleton goal. Its proposed event replay can admit mutually exclusive transitions, several guard conditions have no authoritative evidence producer, and the initialization and migration paths leave the first real repository without a complete cutover. The findings identify contracts for the FUR. The choice of internal helpers and low-level implementation stays with the builder. “High” denotes a policy or correctness failure. “Medium” denotes a material interface or consistency omission.

## Findings

### R1-F001 — High — Serialize whole operations against their authoritative state

**Evidence.** Ownership and replay at FUR lines 169–184, 229, 244–253 and 309–319 treat ULID-sorted event union and whole-file replay as safe. Two processes can evaluate the same Plan exit, commit mutually exclusive Develop entries, and then combine them. The same failure applies to a trip racing a promotion and a stale authored edit replayed over an import. A ULID encodes generation time, so clock skew or a delayed submission can reorder a causal successor before its predecessor and insert bytes before previously published events. Git's ref compare-and-swap checks the ref value. It does not re-evaluate the operation's guards. [Git update-ref](https://git-scm.com/docs/git-update-ref)

**Required change.** Assign event files to the core append API and specify stable operation/event identity, authoritative append order, duplicate-ID mismatch handling, and snapshot validation for state, consulted related stories and authored paths. A transition attempt should durably commit its guard outcomes and allowed changes as one coherent unit, or durably record the refusal with no transition. On a local CAS miss, re-read and re-evaluate affected preconditions or return a conflict. On divergent remote history, preserve the published prefix and reconcile whole operations under their original preconditions. Specify which local facts survive a rejected replay, how pending or conflicting local state is visible and recoverable, and how authored bytes and evidence are retained. Distinguish authoritative local recording from shared publication, and distinguish intentional workspace draft saving from a failed transition. Do not allow advisory mode to make an illegal edge, incompatible history or ownership conflict safe. Qualify the “without conflicts” goal and exercise same-story, same-path and cross-story races in acceptance.

**Basis.** Architecture lines 104–107, 126, 144 and 157. Existing tests at FUR lines 479–480 cover only disjoint story writers and cache rebuild.

### R1-F002 — High — Make binding and the workspace-to-store contract enforceable

**Evidence.** FUR lines 170–184, 233–240, 263–268, 341, 353–358 and 362 assign the description body both direct editing and event-driven generation. The folder copy includes core and extension-owned surfaces although the event log is said never to be materialized for editing. Binding has no competing-session check, and verification chooses the latest session's branch. An accidental second bind can redirect test evidence to the wrong branch. The first Develop entry also relies on a bind that is already performed to work on the Plan. Index-based guards could combine a newer source story with older dependencies if the cache is independently refreshed.

**Required change.** Specify one authored-source model for description and core metadata, exactly which workspace files sync can write or delete, and snapshot-based conflict checks for them. Protect the single writer for story authoring through bind, unbind, recovery and review import while keeping explicit core-mediated operations such as a human pivot possible. Define how Develop acquires the intended branch, how refactor and scrap preserve the appropriate source and evidence, and what a second bind or stale session can do. Reads for a decision must use a single pinned store snapshot even when the index is unavailable or being rebuilt. Clarify that machine metadata regeneration and rendering use the complete set of inputs and preserve authored bytes. Keep actor heuristics distinct from authenticated origin or command-specific authority. The human-only pivot limitation on a single-user host can remain explicit.

**Basis.** Story #1 draft lines 91, 96–97 and 152. Architecture lines 105–107, 144, 149 and 157.

### R1-F003 — High — Resolve policy before applying any guard or extension

**Evidence.** FUR lines 84–124, 182, 193, 209–210, 296 and 353–355 say where `.aitm.toml` belongs, but leave configuration resolution circular. If the loader reads the story copy to choose `[store] trunk`, the story branch can select itself as authority and disable enforcement or replace the test command. `init` leaves config uncommitted, while acceptance assumes core-only workflows can start. A missing remote HEAD or no remote leaves the init detection algorithm without a source. Fetch failures and branch-push skip behavior have no policy or freshness distinction.

**Required change.** Define bootstrap and ref identity from trusted installation or repository facts, then read the committed policy from the configured default branch. Specify when network preflight runs, what fetched or local source a no-remote setup trusts, and what stale, missing or invalid policy permits. Freeze the effective policy and git snapshot inputs for each operation and record the policy revision and relevant settings in evidence. Never silently use worktree policy or an unverified self-redirection. Treat offline local operation, configured-remote publication unavailable, and invalid store history as distinct states. Keep routine guard evaluation local, document startup and rerun behavior before the bootstrap config lands, and exercise a story-branch override in acceptance.

**Basis.** Story #1 draft lines 65, 125 and 156–158. Architecture lines 83–85, 126 and 157–161.

### R1-F004 — High — Bind document acceptance and JIT to a verified content version

**Evidence.** FUR lines 184, 214–215, 326, 330–332, 354–355, 452 and 464–483 make an acceptance event or a past trunk SHA sufficient. A later plan edit still passes `plan-accepted`, and its former JIT can qualify a different plan. The table requires the exact trunk tip, while the later text allows no-touch descendants and gives no conservative rule when touched paths are missing. A full-file hash alone would break on the next generated frontmatter refresh.

**Required change.** Define the versioned canonical authored-content digest, authored and generated field boundaries, treatment of unknown schema/header fields, and byte-level provenance for the portable review record. Define the typed review input, verification of final accepted content and configured required levels, how multiple levels with different digests are represented, and when an acceptance is effective for a guard. Keep review depth pending confirmation. Specify the core-only interim import into the correct story via CAS, restricted to the FUR and collateral, with stale-base detection and no dependence on retaining review branches. Bind JIT to the accepted current plan version, attempt and pinned code baseline. Define applicability for unrelated changes, missing/uncertain path coverage, non-descendant history, unavailable freshness, and a JIT revision that changes accepted plan content. Exercise authored edit invalidation, generated metadata stability and review import in acceptance.

**Basis.** Architecture lines 118, 128 and 132–140. Peer-review draft lines 39–49 and 67–75. Story #1 draft lines 59, 63 and 67–70.

### R1-F005 — High — Migrate real v0 records and make the checkout cutover repeatable

**Evidence.** FUR lines 148, 184, 196–229 and 464–483 reduce migration to changing event IDs/timestamps and splitting `story.md` prose. The actual v0 `events.jsonl` has story-less draft events, `core.state.entered`, `core.link.child-added` and `core.link.parent-set`, legacy actor keys and provider URLs. #2's graduation and state entry have identical timestamps. Both story headers have empty design/plan lists despite files already on disk. #1 has accepted byte-bound XPR collateral. Fresh IDs, timestamp sorting, stale file lists or reading the generated details back could corrupt meaning, inventory or provenance.

**Required change.** Specify input schema recognition, deterministic mapping and source order for existing facts, preservation of unmapped provenance, and inventory from actual files. Separate one-time legacy metadata intake from runtime authority. Establish canonical bindings only from demonstrably accepted v0 snapshots before metadata changes, preserve their exact bytes or reconstructible proof, and keep drafts and partial/unaccepted reviews distinct. Plan validation and all-or-nothing or resumable CAS cutover after releasing the planning checkout, including a safe preflight and preservation of unsupported material. State how a rerun after success or interruption avoids duplicate events, changed IDs, lost relationships, or conversion of imported/unmeasured history to complete evidence. Test against the real #1/#2 fixtures and their review records, including the existing branch baseline under R1-F012.

**Basis.** Architecture lines 104–107, 136, 140 and 215. Master plan lines 29 and 50–61 provide cutover context.

### R1-F006 — High — Specify graduation identity and expand as recoverable transactions

**Evidence.** FUR lines 208, 216, 224, 375–377 and 395–417 offer `create_issue(draft)` and a local max-plus-one allocator, but no operation protocol. A remote provider can create the issue and lose the response before the draft move. Concurrent expand requests can both create an issue before either commits the origin's allowance. Independently operating clones with the same local-number provider can both allocate the same numeric ID for different stories. Retrying CAS with another number after a number has been exposed can break permanent links.

**Required change.** Specify a stable graduation operation key and identity scope, when issuance is reserved, how an uncertain create is reconciled before any new create, and how the draft move, story initialization, links, expansion event and clock pause become one consistent result. Resolve races between completion, expansion and trip, including an expansion that was remotely issued but could no longer be finalized under the original state. For the local provider, allocate in the same authority transaction as initialization and define where independent offline allocation is allowed. If a shared local-numbered store has no serialization mechanism, make it fail visibly or require a single allocation authority, with no renumbering of published identities. Define provider selection before issue creation and preserve the already-real GitHub identities in migration. Test lost responses, duplicate retries and two concurrent allocations.

**Basis.** Story #1 draft lines 58, 92 and 98. Architecture lines 39, 103, 146 and 163–174. The provider endpoint details belong to M2. The published REST create contract is a reason to expose reconciliation as a capability rather than assume a request flag. [GitHub create issue](https://docs.github.com/en/rest/issues/issues#create-an-issue)

### R1-F007 — High — Make post-commit work discoverable and order its remote effects

**Evidence.** FUR lines 211, 253, 315–319 and 362 run resident actions after local commit, push last, and retry a failed action at the next sync. A crash between commit and the first action call yields neither a completed nor failed event. A delayed projection for Develop can overwrite Review on the board. A projection issued from an unreconciled clone can publish a local state its shared store cannot accept. The initial and terminal state flows also need a defined action trigger.

**Required change.** Specify how the transition makes post-commit work durably discoverable, the stable action identity and outcome lineage, and safe retry after a crash before or after the remote side effect. Define when projection is eligible relative to shared publication and how stale projections are suppressed or reconciled in canonical order. Define push retry and success evidence separately from workflow success. Keep the sparse state-entry cadence, including initial and terminal entry, and handle terminal session closure with a defined atomic write or retry boundary. Specify behavior when a required resident action implementation is disabled or temporarily missing. Test the no-outcome crash window, lost acknowledgement and overlapping projections.

**Basis.** Story #1 draft lines 52–53 and 65. Architecture lines 33, 39 and 126.

### R1-F008 — High — Prove verification and delivery for the version signed off

**Evidence.** FUR lines 221–223, 226, 334–338, 348, 360, 395–415 and 473–478 let a pass verdict and sign-off imply delivery. A reviewed but unmerged branch can be marked delivered. A standalone `review pass` assertion does not prove review or CI ran, and a test receipt keyed only to a head SHA can certify code that was actually tested with uncommitted changes. A passing review that is later invalidated or superseded by rework can remain available to the sign-off guard.

**Required change.** Specify how test, review and delivery evidence are captured for the exact reviewed source or deliverable, intended target and applicable attempt. Define dirty-tree handling and changes to the head during verification. Add the core-only local delivery proof and a typed provider contract for verified remote delivery, including source-to-target mapping for squash/rebase and a pending result when remote proof is unavailable. Sign-off should require verified delivery for a delivered disposition, record the agent retro and the Done transition coherently, and preserve the separate abandonment dispositions and clock boundary. In advisory mode a guard may warn and advance under policy, but the resulting record cannot claim delivery, a test pass or review proof it lacks. Define how authoritative receipts are reconstructed from retained proof or regenerated by rerunning verification. A real test/review failure remains a substantive condition, and missing timing remains unavailable. Test core-only delivery, missing proof, stale heads and retry recovery.

**Basis.** Story #1 draft lines 52–53, 75, 147 and 151. Architecture lines 28, 121–122, 128–130, 150, 159 and 167.

### R1-F009 — High — Preserve open trip policy and make the settled part executable

**Evidence.** FUR lines 95–99, 300–307, 331–335, 370–393 and 476–477 hard-code a second-trip cap in configuration and acceptance, although line 391 itself says confirm. The trigger table equates an expansion used with a second/nested request, while the owner also names a used slot with work still incomplete. The stop rule depends on separate origin and child mutations. A crash can leave the child active after origin demotion, or close the expansion while it still blocks the origin. “Any” abandon, current target entry guards, and trip-forced backward moves also leave room for a normal guard to block a mandatory stop.

**Required change.** Keep the expansion-boundary interpretation and cap visibly open and out of unconditional requirements/defaults. Identify what can be tested from the confirmed one-expansion budget, nested request and observed timeout behavior, and how an ambiguous case is represented pending owner decision. Specify explicit transition and disposition rules for origin/expansion, including atomic stop and pause/resume, idempotent trip detection per attempt, where a forced move applies, and the enforcement boundary at the next observed command. Distinguish advisory reporting from stopping, new attempts after an accepted replacement plan from Develop re-entry for rework, and scope pivots from trips. Define expansion disposition and dependency cleanup across refactor, scrap, abandon and restart. No new human gate is needed for the settled agent decision.

**Basis.** Story #1 draft lines 46–50, 77 and 147–152. Architecture lines 144–159 and 221.

### R1-F010 — High — Qualify telemetry, clocks and learning outcomes

**Evidence.** FUR lines 227–229, 366–371, 383–388 and 477 derive engaged time by summing CLI event gaps with a 15-minute rule. Two commands four hours apart provide no evidence whether the agent worked for zero or four hours. Several short gaps from inspection by a human or a different worktree can instead look like engaged work. The design does not define whether a review changed after a pass resumes the same clock, how intervals crossing a pause are handled, or what happens after clock skew, late activity or a repeated event. Its event table lacks a complete outcome/usage contract for learning.

**Required change.** Define observed, estimated/partial and Unknown coverage with source, attempt/session identity, activity-window, deduplication and freshness semantics. Define what the 15-minute rule actually counts, which activity contributes, how pauses and passing-review/rework boundaries segment it, and which measures can substantiate a time-limit trip. Keep missing observations Unknown or qualified rather than treating them as exact time or zero. Define the minimum durable Refine/Plan/Close outcome and telemetry hooks for estimates, actual coverage, expansions/trips, follow-on defects, lessons and available token/cost. Preserve incomplete and imported records separately from complete calibration inputs. Exercise core-only sparse observations, telemetry retries and crossing a clock boundary.

**Basis.** Story #1 draft lines 41, 51–53, 119–120 and 147–149. Architecture lines 28, 145, 159 and 215.

### R1-F011 — Medium — Define kind-specific lifecycle and related-story guard semantics

**Evidence.** FUR lines 298–307, 329, 334–349, 375–377 and 473–478 use one forward chain plus partial exceptions. The global child guard can stop an epic entering Develop until all its newly planned children already reached Develop. The epic table then requires Review/Done to leave Develop, and “open children” can make an abandoned dependency look satisfied. No rule says how an expansion gets a dependency without accidentally creating an epic hierarchy link, or how a cycle is rejected. A spike's deliverable path alone allows an edited file to reuse an old outcome.

**Required change.** State the explicit leaf, spike and epic milestones and guard precedence, including terminal/disposition semantics for dependencies and children, relationship direction and cycle checks where appropriate. Keep epics out of the leaf implementation clock, implementation commits, PR/test and delivery checks while defining their aggregate sign-off/closure evidence. Define a versioned reviewed deliverable for spikes and clear behavior for rework, abandon/supersede/duplicate and scope pivots. Include an epic with children in mixed states and a spike with a changed deliverable in acceptance.

**Basis.** Story #1 draft lines 51 and 129–130. Architecture lines 109–130. Master plan lines 15–21 are context for section epics.

### R1-F012 — High — Make planning validation and forward repair converge without policy exceptions

**Evidence.** FUR lines 114–144, 257 and 482 allow a root `README.md`, assert an every-push Action, and propose restoring the last valid tree on top of a bad commit. The current legacy tree contains a root README. An ordinary path-change checker can reject the repair itself because it deletes the violating outside path. A fresh clone scanning history can reject the retained violation forever after repair. A forward tree repair cannot restore branch isolation, and a rejected fetch must not become the next writer base. The hosted audit is unresolved because a normal push workflow is selected from the event's ref and the planning branch cannot hold it. [GitHub workflow triggers](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows#workflow-triggers)

**Required change.** Define validation of new history from a trusted baseline and of final trees, including initial empty-root handling, linearity, path/data integrity and checkout exclusion. Bring the legacy root README into the M1 data-only cutover without a standing outside-path allowance or history rewrite. Define a recognizable, independently verifiable forward repair that proves the quarantined tip and restored tree, works with the validator/hook on a fresh fetch, remains fenced against further remote changes, and preserves useful local or published evidence. Classify shared ancestry as requiring explicit owner intervention. Keep the GitHub every-push obligation and its trigger/location open as the architecture does, and define the provider-neutral validator it will invoke. For separated planning and code remotes, identify which default-branch history is used to check isolation. Test fresh clone after repair, a racing push, and an irreparable ancestry violation.

**Basis.** Story #1 draft lines 89–91 and 163–172. Architecture lines 79–97, 140, 157 and 222–226. A pre-push hook receives each destination ref and the old/new object names, so the normal and permitted repair transitions can be distinguished at this boundary. [Git hooks](https://git-scm.com/docs/githooks#_pre_push)

### R1-F013 — Medium — Enforce extension ownership and version compatibility at the write boundary

**Evidence.** FUR lines 165–184, 198–200, 291–296 and 419–439 validate declarations at load, but provide no constrained write capability or replay contract. A glob that covers a core path, a symlink escape, an extension using a disabled package's old namespace, or an action writing through another path can bypass registration checks. “Unknown types are kept” leaves old schema versions and unsupported core events ambiguous during folds and replay. Stable action/guard identifiers are needed when extension order or versions change.

**Required change.** Define core-reserved surfaces, normalization and overlap rules, typed event submissions and declared-path writes via the core boundary, and stable registration identity/ordering. Preserve original opaque extension data when its owner is absent or its version unsupported, and distinguish that case from an unsupported or invalid event needed for core state. Specify how extension removal or version changes affect existing data and pending actions. Clarify that in-process extensions are trusted Python code and where the core enforces persisted ownership without promising process isolation. Keep core functions transport-neutral and free of model calls, and separate installed distributions from enabled configuration. Test core-path overlap, unknown-version round trip and owner removal.

**Basis.** Story #1 draft lines 39–41 and 108–111. Architecture lines 73, 105–107, 157, 177–182 and 197–203.

### R1-F014 — Medium — Make the walking skeleton testable through real entry points

**Evidence.** FUR lines 204–208, 263–268, 341, 353, 360, 395–417 and 441–483 lack a consistent entry point for several promised features. Idea and draft events have no stated owning store before a story exists. `draft open <slug>` is ambiguous across dates and same-minute collisions. `migrate v0` and `discuss` are described outside the command surface, and the only described `deliver` is for spikes. Bind, checkout and command-side side effects lack a single executable acceptance sequence. Performance excludes actions/push without saying whether preflight fetch is included.

**Required change.** Identify ownership and stable handles for pre-story records, and how repeated create/open/discard uses them without a shared append file. Give one coherent core-only CLI flow from local initialization and graduation through design/plan acceptance, JIT, branch binding, verification, delivery and sign-off. List the recovery, migration, review import and local evidence commands or operations that make the stated behaviors reachable. Include expected exit and result distinctions for refused, locally committed, pending publication and completed cases. Keep wall-clock budgets explicit about the warmed data and remote work they measure. Tie acceptance scenarios to the high-risk outcomes in this response instead of counting a CLI walkthrough with synthetic pass assertions as proof.

**Basis.** Story #2 draft lines 16–29. Story #1 draft lines 40, 52–53, 57–58 and 93–94. Architecture lines 26–33, 126, 140 and 178.

## Required changes

Address R1-F001 through R1-F014 in the core FUR and disposition each finding. Where a detail belongs to a later package, give that package an implementable interface, its expected failure results, and a verification obligation. The FUR need not choose endpoint algorithms, a distributed transaction framework, or a review-depth matrix. Keep the accepted architecture and context-only master plan outside this revision.

## Optional suggestions

- Use one small operation-state table to show local commit, shared publication, projection and recovery. This could replace repeated prose across the store, transition and provider sections.
- A compact verification matrix can map concurrency, stale evidence, crash windows, migrations and store integrity to the normal CLI entry points. This can supplement the nominal walk without specifying test layout.

## Decision

**revisions-requested**

The next round should evaluate the revised FUR and the author's dispositions at its new digest. No new owner decision is needed for these corrections. The expansion-completion interpretation and second-trip cap remain existing open owner choices. The review-depth question and GitHub audit mechanism also remain open at their established boundaries. Any later proposal to relax the data-only branch rule or the every-push audit obligation would require a separate owner decision.
