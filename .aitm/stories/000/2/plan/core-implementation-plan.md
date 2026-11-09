---
schema: aitm.doc/v0
story: 2
role: plan
title: aitm-core implementation plan
created: 2026-11-09T06:44:00Z
updated: 2026-11-09T13:37:37Z
last-branch: review/2-core-plan-fullfile
status: review candidate (acceptance is in review records)
design: ../design/core-design.md
parent-plan: ../../1/plan/master-plan.md
---

# aitm-core Implementation Plan

> **For agentic workers:** Once implementation is separately authorized, use the executing-plans or subagent-driven-development skill, as selected for that work, task by task. This assignment authorizes planning and scoped leaf creation only. Checkboxes below describe future execution; none is marked done by plan review.

**Goal:** Deliver M1's usable core, portable review sink and safe migration capability without forcing production adoption before its prerequisites exist.

**Architecture:** One typed operation API owns append order, multi-story transactions and CAS writes to an isolated planning ref. Policy is pinned from the committed code default ref; SQLite/backlog output are projections. Agent-authored documents and exact review originals survive regeneration. Core never invokes a model.

**Tech stack:** Python 3.13, uv workspace, Pydantic v2, Typer, pytest, Ruff, SQLite and Git plumbing; no hosted provider or lab SDK in core. macOS and Linux first; no Windows commitment in M1.

**Spec:** [Accepted core design](../design/core-design.md), raw SHA-256 `5eaafbc1af04f13d4de25dcf5e9dacb35042ef775e0f230be89e4fba9452f3e7`, published `3702cfde855e7a2345e12439f19cc2ee9ebe7291`; [accepted architecture](../../1/design/architecture.md); [master plan](../../1/plan/master-plan.md), SAR publication `ca14c5de346235488d71f223c226385ad8a290f5`; [owner decisions](../../1/draft.md). Read the spec with each leaf. Review manifests, not historical draft-status headers, establish document acceptance.

## Global constraints

- Planning is `.aitm/` data only, separate history, no automatic reset/rewrite, never merged into trunk. New source/tests/workflows/tutorials belong on trunk through authorized story PR delivery. This plan itself remains on planning.
- One owning transaction API; no event union, timestamp sorting for workflow, blind authored overwrite, generated-details parsing, or hidden alternative policy authority. Integrity applies in both advisory and enforce modes.
- Four engaged implementation agent-hours maximum per leaf attempt, Develop entry through effective passing source review; tests and review are included. Epics aggregate with no implementation clock; spikes use effective deliverable review. Planning time is unbounded. Tool duration/response bounds are not measured engagement.
- One expansion per attempt; an expansion has none of its own. Preserve origin pause, fresh child clock, enforced stop/replan and same-attempt rework. Expansion completion interpretation and second-trip cap remain owner-open and are not new defaults.
- No routine human gate. Agent retrospective follows verified delivery; passing tests/review do not authorize merge, release, production adoption or closure.
- Hooks are optional. Installed package, activated configuration and observed live capability are separate claims. Core observations cannot promise live reasoning coverage or every-push hosted audit.
- Manual bootstrap remains the production route until master-plan C6 verifies adoption. M1 C5 is package delivery/capability proof, not the removal of this checkout. C6 needs GitHub identity-provider readiness for aitm's existing namespace and an explicitly authorized supported production review policy. Keep the legacy route through the C6 freeze; committed partial migration recovers forward.
- The original assignment's SAR → manual SPR → native Claude XPR sequence applies to its historical plan versions; the separately authorized full-file validation below reviews this reconciled candidate. Each level publishes before the next, with full-file rounds and a five-round cap. Historical levels bind their own bytes; a later runtime exact-content policy requests missing current-digest coverage/valid exceptions rather than upgrading old reviews. Global depth/sequence policy stays open.

## Estimate and scope baseline

[Initial Refine record](../refinement.md): **180 implementation agent-hours, XL epic, P1**. Bottom-up Plan estimate: **257.5 h over 79 leaves**, all 2.5–4 h, including local verification and source-review engagement. P1 reflects the foundational dependency, not emergency work; XL is this epic's aggregation label, not a universal size-policy change. Each leaf is a small deliverable, provisionally S (≤4 h). No calendar duration is promised and no implementation clock has started.

These are estimates, not proven throughput. Concurrency/recovery/platform/migration uncertainty is high. At JIT, split or redesign a leaf before Develop if the verified baseline, dependencies or proof burden makes four hours implausible. Do not consume its expansion allowance as planned overflow or relax acceptance to fit the estimate. Changes to leaf scope/dependencies invalidate the relevant accepted decomposition and need applicable review. Record Plan/JIT revisions separately; never overwrite the original Refine estimate.

This is a new repository: inspected trunk `4e896e049370df58fe870dc80790401056218b97` contains README and LICENSE only. All listed implementation paths are proposed new files except those explicitly described as shared updates. JIT must re-read current trunk rather than treating this empty baseline as permanent.

The preceding accepted Plan baseline was 220.5 h / 70 leaves. This pre-review reconciliation adds C71–C75 (17 h) for independently reviewable split, descriptor/applicability, source-review record, entity editing and decompose integration contracts. Existing producers receive 5 h of explicit added schema/acceptance work (C03/C54/C11/C16/C22/C28/C31/C38/C46), preserving every ≤4 h bound. These were author preparation changes following the separately accepted design, not findings from the subsequent plan review. The native review records establish their validation outcome. Round-1 revisions add C76 (4 h), C77 (2.5 h), C78 (3 h) and 3.5 h across C17/C29/C30/C51/C62 for explicit guard, wiring, sync, kind and explain proofs. That round-1 Plan estimate was 255.5 h / 78 leaves, with the original 180 h Refine and earlier Plan baselines retained. Round 2 adds the required C76/C79 prerequisites to C65/C66 and proactively splits the capped guard leaf: C76 becomes 3 h source-evidence work and new C79 is 3 h completion/signoff work, adding 2 h for separate integration/verification. Current total: 257.5 h / 79 leaves.

## File and interface map

`P = packages/aitm-core/`. In each leaf, `src/...` and `tests/...` are relative to P; root `pyproject.toml`/`uv.lock`, `.github/...` and `docs/...` are repository-root paths. Paths written as `packages/aitm-core/...` are already root-relative. This explicit expansion defines the touched-file allowlist; a JIT may refine helper filenames with rationale without hiding a scope change.

| Area | Responsibility |
| --- | --- |
| models/, reducers/, events.py, documents.py | Typed wire/schema contracts, causal reduction, canonical authored identities |
| store/, config.py, setup/ | Operations, objects/CAS, validation/gate/continuity, publication/repair, policy, init and bindings |
| ext/, providers/ | Registration, version/ownership capabilities and generic provider/local identity contracts |
| index/, drafts.py, description.py, relationships.py | Snapshot reads, authoring/pre-story workflow and links |
| machine/, rules/, attempts.py, jit.py | Kind/edge/guard/action logic and attempt/timing/trip authority |
| reviews/, execution/, verification/, delivery/ | Portable/live review facts, admission, actual execution evidence, source review and verified delivery |
| migration/ | Bounded v0 inventory/adoption/apply with retained original snapshots |
| cli/ | Thin typed-operation adapters, lazy imports and versioned JSON/human results |

C01 defines common result/status/identifier types and structural StoreAnchor/RefObservation/RefreshResult plus named ServicePorts wiring slots before consumers exist. Slots are not duplicate protocol-type definitions: C04 owns WriteAuthorizer/PendingActionRunner/AttemptPreflight and operation categories; C11 owns InitHooks; other domain producers own their named typed ports. C01 only declares availability/registration behavior and refers forward to those protocols. Tests explicitly inject fixtures; production required operations never fall through a missing implementation. All missing-port/module assertions target an explicit test composition with that slot deliberately unregistered, not a time-dependent default composition. Those negative vectors remain valid after later wiring lands. Each wiring leaf proves its actual production registration in its own allowlisted test file; it does not flip or skip predecessor assertions. Production unavailable behavior before installation is a rollout fact, not a permanently asserted absence in the default service graph. C02 owns event envelopes and reducer dispatch; C54/C55/C56 supply lifecycle, attempt and evidence domain schemas/reducers, then C56 composes them before C04 consumes the complete fold. C03 owns DocumentSchema/ContentIdentity. C04 owns Snapshot/Operation/read-set/write capability/result contracts, plus the typed AttemptPreflight port and operation category before normal/recovery dispatch. C07 owns validated PolicySnapshot/Installation and configuration semantics, using C01 routing/observation records. C13 owns provider/extension/activity interfaces; domain records are defined by their owning later leaf and consume
those contracts. Names/signatures below are proposed integration contracts; no task may silently fork one. A required contract change is coordinated, reviewed and reflected in dependent JIT coverage.

Each owning leaf also implements its named thin CLI module and `--json` adapter; no later CLI task is a bucket for missing behavior. C01 owns cli/app.py and the complete lazy route-to-module catalog in cli/catalog.py; each leaf supplies its named handler module without a shared registration edit. Missing modules report unavailable. C09 owns the separate operation/publication executor cli/dispatch.py and C28 its state-command pipeline. C63 alone later extends app composition for installed extensions; any new core route or schema-export change is an explicit coordinated contract/allowlist revision. A partially implemented capability reports unavailable until wired, never a fake pass. C67 audits the complete accepted-design CLI map below through installed commands. The audit may fix test composition only; missing production wiring belongs to the named owner and cannot be counted as qualification work.

## Execution and evidence contract for every leaf

Before Develop, create its design/plan/JIT records as required by the explicitly applicable policy. The accepted epic plan is input to those records, not an invented leaf acceptance. Bootstrap issue/story creation records intent and dependencies, not runtime readiness. All leaf issues are children of #2 (itself a child of #1); they are **not expansions**. Stable plan keys C01…C79 are mapped to actual issue IDs only after decomposition acceptance, in a separate ledger so issue creation does not mutate this reviewed file.

Each leaf executes this cycle with its concrete proof and interface below:

1. [ ] JIT: pin current source, prerequisite deliveries and touched/dependency paths; confirm remaining estimate ≤4 h and record assumptions.
2. [ ] Write the named failing test(s) with the exact assertions below; run the designated test file and retain the expected failure before implementation.
3. [ ] Implement the named interface and thin CLI adapter with minimal focused files; add schema vectors/negative cases specified by that leaf.
4. [ ] Run its test file to PASS, relevant dependency contract suites and Ruff on touched code; retain output, clean source/head/tree, command, policy and capability details. Unit tests use MemoryBackend/fakes; Git/process/platform cases live in separate integration/platform lanes.
5. [ ] Commit exact paths with `[#<actual issue ID>] ` prefix, obtain source review and retain reviewed head; delivery uses the task's actual authority and verified source-to-target mapping. Record retro/lessons/qualified actuals. Passing plan review does none of these steps.

Test command convention: `uv run --package aitm-core pytest <root-relative test-file> -q`; expected final result is exit 0 with all specified assertions passing. `uv run --package aitm-core ruff check <touched Python files>` must exit 0. C01 installs the unit-lane subprocess/network guard before C02 and all later unit leaves. The shared unit suite contains no subprocess Git/network and must stay under 10 s; platform and integration tests are separate commands. Tests use disposable repositories/targets and explicit fixture authority, not production planning/trunk mutation. Meaningful failure injection is preferred to tests that mirror helper implementation.

Acceptance evidence per leaf is its concrete proof below plus the common command/head/result/source-review/delivery record. If a test is unavailable on the host, retain a precise capability result and run the required supported lane elsewhere before claiming that capability proved. An unavailable containment probe is a tested behavior, not proof that containment itself works. No leaf may mark a skipped requirement passed.

C71 owns the bounded split, C72 owns pure typed plan-entry preparation/applicability, C73 owns source-review parsing/independence, C74 completes entity editing and C75 integrates decompose through the actual identity protocol. C76/C79 complete story/defect exit-evidence guards, C77 supplies pure legacy-kind mapping, and C78 wires full installed explain. C72 declares the applicability implementation before C28 consumes it; C75 later installs the production service. Until then a plan-entry child cannot obtain verified readiness from an absent port. Source-kind interfaces in C20/C22 already handle both frozen sources; later decompose does not create a draft-only escape from identity reservation.

## Review focus and risks

1. Same semantic action retried after lost ACK or competing clone: at most one exposed identity/dispatch, explicit retained conflicts (C09/C20/C21/C32/C41/C50).
2. Mutable source or prepared environment changes between check/run: captured bytes and declared assurance, fresh identities, real platform probe (C33–C37).
3. Historical acceptance/timing mistaken for current authority: canonical/raw separation, exact-content policy, public anchors and Unknown reporting (C03/C24–C26/C51).
4. A stop, early review or expansion gap changes clock/authority incorrectly: immutable boundary facts, CAS ordering and recovery generation tests (C23/C28–C32/C38/C42).
5. Legacy/foreign/unsupported data or unrelated work lost during cutover: exact inventory, bounded declaration, opaque preservation and two-clone recovery (C06/C10/C46–C48/C51).

## Ordered leaf backlog

Dependencies below are required delivered interfaces/evidence and mandatory shared-file integration predecessors, not mere issue closure. Independent means all listed predecessors are satisfied and touched shared exports/CLI registry are serialized. The table order is a valid topological execution order, not a demand to run everything serially. Keys are stable identities, not ordinal positions: added split leaves C54–C79 appear at their prerequisite position.


### Production composition ownership

`services.py` owns the real dependency graph, not a test-only container. C01 declares mandatory typed ports; C06 wires the validator/ref gate into every Git backend mutation and planning validate; C07 wires committed-policy resolution; C08 wires refresh/preflight. C09 wires default bounded publication in CommandService.execute for all ordinary mutators. C31 wires AttemptPreflight before ordinary sync/mutation, every CAS retry and effective completion; C32/C38 call it from their later execution/activation paths. C42 builds Close outcome in its single signoff transaction and C44 only consumes/reports it. C28 composes separately recorded authored sync after trip preflight and repins before normal transitions; C42 evidence reconcile calls C38 late activation. C10 installs independently verified forward-repair validation; C41 uses the common exact-target gate around delivery CAS. C63 discovers installed entry points and mounts committed-enabled CLI/provider/init contributions. C14 inserts WriteAuthorizer at the transaction ingress, so CLI/extension/direct API operations share enforcement. C11 declares the init hook/doctor/provider-step seam; C12 wires it and exercises real init. C17 calls the pending-action port after sync/publication and reports unavailable until C43 installs the durable runner and verifies real sync/actions retry. C35 wires the platform-neutral LaneAdapter selector to managed execution and doctor/init; C36/C37 implement its platform factories. Each wiring leaf declares services/shared call-site paths and tests the normal entry point; absent required wiring cannot report ready or successful enforcement. All detected touched-path overlaps receive explicit
earlier-writer edges in Depends on (including C08/C14, C31/C43 and C45/C61 ownership); no parallel worker owns the same shared file simultaneously.

### CLI coverage map

Commands inherit global `--json` and pinned context/freshness behavior. Examples use fixture story 7 and fixture files; they are future test commands, not instructions to mutate this repository.

| Required route / options | Operation / owner / adapter | Representative real CLI proof |
| --- | --- | --- |
| init --planning-branch (also interactive name prompt) --local --default-branch --review-policy --reconfigure | prepare/resume/reconfigure C11, hook composition C12; cli/setup.py | init proposal, commit fixture config, rerun ready; changed anchor stays adoption-pending |
| doctor | C12 diagnostics with C35 lane selector; cli/doctor.py | doctor shows policy/checkout/publication/hooks/lane separately |
| planning validate / repair | C06 validate, C10 repair; cli/planning.py | invalid candidate refused; forward repair restores maximal prefix |
| index rebuild; show/list/search/explain --refresh | C18 query/build, C78 full explain over C28, C08 explicit refresh; cli/read.py | read has no fetch; --refresh candidate validation; rebuild same query results |
| idea add/open/list; draft new/open/discard/list | C19 entity operations, C74 entity open/save; cli/drafts.py | stable handle, ambiguous slug and tombstone proof |
| graduate --kind/--parent; graduate resume; decompose --entry/--expected-plan | C20/C22 source-neutral protocol, C21 local authority, C72 preparation/C75 decompose; cli/stories.py + decompose.py | graduate same draft after lost ACK exposes one finalized ID |
| describe; link | C15 structured description cli/describe.py; C22 relationships cli/stories.py | describe --title --as --want --so-that --scope-file; link cycle refuses |
| discuss | C18 context exporter; cli/read.py + context.py | discuss 7 emits context/command, no model/process launch |
| bind --implementation/--deliverable/--evidence/--recover; unbind | C16 purpose/capability core cli/bind.py, C45 deliverable use, C61 recovery authority; C17 unbind | unavailable authority refuses; stale holder cannot sync/unbind replacement |
| sync --entity/--push/--reconcile; unbind --entity; actions retry | C17 sync adapter, C74 entity integration, C17 reconcile/push adapters over C09, C43 runner; cli/sync.py + actions.py | sync retries same pending key and cannot replay stale board state |
| attempt reconcile; estimate; jit | C27 owning operations; cli/plan.py | reconcile provisional attempt after accepted plan/bind without new budget |
| split --reason/--scope-file; promote --to; demote --to --reason | C71 bounded split; C28 transitions; cli/split.py + lifecycle.py + dispatch.py | enforce refuses missing proof, advisory records it; illegal edge always refuses |
| abandon; supersede --replacement; duplicate --of | C29 disposition; cli/dispositions.py | reason/replacement and cycles enforced, retained historical state |
| design accept --review; plan accept --review | C26 persisted accept_document; cli/design.py + plan.py | import alone is not acceptance; accepted current digest appends one fact |
| review open/turn --record --response/complete/import --story --doc | C25 live sink, C26 final CAS import; cli/review_turns.py + review_import.py | provisional turn then final import yields one normalized fact |
| test prepare --offline; test | C34 provisioning cli/test_prepare.py; C35 managed test cli/test.py | no hidden downloads; selected lane actually used with current admission |
| review pass/changes --evidence | C73 validated envelope, C38 source-record/activation; cli/review_source.py | early pass retained, genuine later activation stops clock |
| deliverable add/validate | C45 bound delivery/check operations; cli/deliverables.py | changed spike bytes invalidate review/archive proof |
| deliver | C39 observation/C40 transform/C41 admitted mutation; cli/deliver.py | checked-out target can be observed after authorized ordinary merge, never raw-mutated |
| signoff --retro --confidence; evidence reconcile | C42 closing/reconstruction plus C38 late activation; cli/evidence.py | one atomic closing operation, no bare pass flag or prior-signoff cycle |
| reopen --for evidence --reason | C61 recovery authority; cli/evidence.py + bind.py | new evidence-only generation, no source edit/expansion/new target mutation |
| expand --kind/--draft/--reason; trip decide --decision --analysis --rationale --expansion; pivot | C30/C31; cli/expand.py + trips.py | reservation pause, typed decision and human-only pivot limitation |
| migrate v0 --dry-run / --prepare --expected-tip / --apply --expected-tip | C46 inventory/dry-run, C47 declaration, C48 apply; cli/migrate.py | no-mutation dry-run, exact declared apply, one result after competing clone |


| Key | Leaf | Agent-hours | Depends on |
| --- | --- | --- | --- |
| C01 | Package foundation and command result contract | 3.5 | — |
| C02 | Event envelopes and reducer dispatch invariants | 2.5 | C01 |
| C03 | Canonical authored content and metadata ownership | 3.5 | C01 |
| C54 | Lifecycle, relationships and document-state reducers | 3.5 | C02, C03 |
| C55 | Attempt, execution and clock-boundary reducers | 3.5 | C02 |
| C56 | Evidence, action and provenance reducers with composition | 3 | C02, C54, C55 |
| C04 | Typed operations and MemoryBackend semantics | 4 | C02, C54, C55, C56 |
| C05 | Git snapshot reads and atomic operation commits | 4 | C04 |
| C06 | Planning history validation and worktree exclusion | 3.5 | C05, C01 |
| C07 | Committed configuration and routing anchors | 3 | C03, C06 |
| C08 | Candidate fetch and shared-history continuity | 3.5 | C06, C07 |
| C13 | Extension and provider registration contracts | 3 | C02, C07 |
| C14 | Constrained extension writes and retained unknown data | 3 | C04, C13, C08 |
| C15 | Deterministic views and structured descriptions | 2.5 | C02, C03, C04 |
| C09 | Publication replay and conflict recovery | 4 | C04, C08, C15, C14 |
| C10 | Forward repair from maximal valid prefix | 4 | C08, C09, C06 |
| C11 | Crash-resumable init and reconfiguration | 4 | C07, C09, C10 |
| C12 | Hook chaining and readiness diagnostics | 3 | C06, C11 |
| C16 | Authoring and implementation bindings | 4 | C06, C07, C15 |
| C17 | Allowlisted sync and authored conflict resolution | 4 | C09, C14, C16, C12 |
| C18 | Snapshot index and read-only queries | 3.5 | C02, C08 |
| C19 | Ideas, drafts and atomic discard | 2.5 | C09, C15 |
| C74 | Entity-scoped editing and graduation handoff | 3.5 | C16, C17, C19 |
| C20 | Semantic identity reservations and uncertain dispatch | 3.5 | C09, C13, C19, C74 |
| C22 | Graduation and atomic relationships | 3.5 | C15, C20, C74 |
| C21 | Shared local number allocation | 3.5 | C22, C17, C74 |
| C23 | Activity eligibility and implementation clock fold | 3.5 | C02, C13 |
| C24 | Portable review schemas and patch reconstruction | 3 | C02, C03, C56 |
| C33 | Private immutable input capture | 3 | C07, C16 |
| C34 | Offline environment provisioning and cache identity | 3 | C33 |
| C57 | Review finding closure, topology and policy assurance | 2.5 | C24 |
| C58 | Native review lineage and timing anchor adapters | 2.5 | C57 |
| C25 | Live review capsules and qualified turn timing | 3 | C09, C23, C58 |
| C26 | CAS review import and exact-content acceptance | 3.5 | C14, C17, C25, C58 |
| C27 | Attempts, JIT coverage and estimates | 3 | C16, C23, C26 |
| C72 | Typed decomposition descriptors and applicability | 3.5 | C03, C07, C20, C26, C27 |
| C28 | State transitions and atomic guard outcomes | 4 | C15, C22, C26, C27, C17, C21, C09, C72 |
| C71 | Bounded Refine split and kind invalidation | 3.5 | C28, C22, C26, C27 |
| C29 | Kind-specific guards and terminal dispositions | 4 | C28, C71 |
| C30 | Expansion reservation and resolution | 4 | C20, C21, C22, C23, C28, C29 |
| C31 | Trip ordering, replan decisions and human pivots | 4 | C23, C27, C28, C30, C14, C17, C71, C74, C29 |
| C32 | Single-use execution admission and cancellation | 3.5 | C09, C16, C31 |
| C35 | Captured-export test execution and receipts | 3 | C12, C32, C34, C31 |
| C73 | Source-review envelope and independence validation | 3 | C07, C16, C56, C57 |
| C36 | macOS contained-lane probe and profile | 3.5 | C35 |
| C37 | Linux contained-lane probe and profile | 3.5 | C35 |
| C38 | Source review evidence and effective pass activation | 3.5 | C29, C35, C73 |
| C39 | Positive delivery observation and archival proof | 3.5 | C38 |
| C40 | Reviewed squash and rebase transformation plans | 3 | C39 |
| C41 | Admitted target mutation and exact-result recovery | 3.5 | C32, C40, C06, C39 |
| C42 | Atomic sign-off and retained evidence reconstruction | 3.5 | C29, C38, C39 |
| C43 | Durable resident-action queue and replay | 3 | C09, C13, C17, C28, C35, C31, C74 |
| C44 | Estimate lineage, usage and learning outcomes | 2.5 | C23, C27, C42 |
| C45 | Spike deliverable binding and validation walk | 3 | C29, C33, C35, C38, C39, C42, C16 |
| C77 | Legacy kind normalization and unresolved inventory | 2.5 | C03, C54 |
| C46 | Legacy inventory and deterministic v0 adapters | 4 | C03, C06, C25, C58, C72, C77 |
| C47 | Stable legacy adoption preparation | 3 | C07, C11, C46 |
| C48 | Atomic migration apply and accepted-snapshot binding | 3.5 | C09, C17, C26, C47, C10 |
| C51 | Real review/migration and second-clone qualification | 3.5 | C48, C18 |
| C61 | Scoped evidence-only recovery and real rerun | 3 | C16, C27, C32, C35, C38, C42, C45 |
| C64 | Deterministic two-clone qualification fixtures | 2.5 | C09, C10, C21, C43 |
| C70 | Post-preflight consumer integration qualification | 3 | C31, C64, C27, C28, C30 |
| C50 | Shared-store conflicts and publication recovery qualification | 3 | C64, C17, C30 |
| C62 | Epic aggregation and scope-resolution checkpoint | 3 | C22, C29, C38, C42, C43 |
| C63 | Installed extension discovery and command/init composition | 3 | C12, C13, C14, C43, C01, C62 |
| C76 | Source commit guard and retained source evidence | 3 | C28, C29, C31, C35, C38, C39, C40, C41, C42, C62, C63 |
| C79 | Test and Review exit composites with atomic signoff | 3 | C76, C35, C38, C39, C42, C62 |
| C65 | Execution fences and clock-rebuild qualification | 3.5 | C64, C30, C31, C32, C35, C38, C42, C61, C76, C79 |
| C66 | Managed-delivery race and recovery qualification | 3 | C64, C41, C42, C76, C79 |
| C78 | Installed transition explanation and unknown guards | 3 | C18, C28, C29, C62, C76, C79 |
| C49 | Core-only nominal lifecycle qualification | 3 | C12, C18, C19, C22, C26, C27, C31, C35, C38, C39, C42, C43, C44, C45, C61, C62, C21, C10, C41, C48, C63, C76, C78, C79 |
| C75 | Plan-entry graduation and provenance reconciliation | 3.5 | C72, C21, C22, C28, C31, C64, C63, C76, C79 |
| C67 | Complete installed CLI surface audit | 2.5 | C49, C51, C63, C44, C71, C74, C75, C76, C78, C79 |
| C68 | Lifecycle reconciliation and limited-rerun qualification | 3 | C49, C61 |
| C52 | Entrypoint performance and unit-isolation budgets | 3 | C18, C49, C50, C51, C65, C66, C67, C68, C70 |
| C59 | Cross-platform wheel and CI qualification | 3 | C36, C37, C49, C50, C51, C52, C63, C65, C66, C67, C68, C70, C75 |
| C53 | Release workflow, tutorials and candidate handoff | 3.5 | C59, C03 |
| C69 | Read-only release checker and dual-platform workflow | 3 | C53 |
| C60 | Publish and qualify the exact released core | 2.5 | C53, C69 |

### C01: Package foundation and command result contract

**Estimate:** 3.5 h · **Depends on:** none · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/conftest.py; tests/__init__.py; tests/support/__init__.py; tests/integration/__init__.py; tests/unit/__init__.py; tests/platform/__init__.py; tests/performance/__init__.py; tests/packaging/__init__.py; uv.lock; src/aitm_core/cli/catalog.py; tests/unit/conftest.py; src/aitm_core/__init__.py; src/aitm_core/models/__init__.py; src/aitm_core/store/__init__.py; src/aitm_core/reviews/__init__.py; src/aitm_core/machine/__init__.py; src/aitm_core/verification/__init__.py; src/aitm_core/delivery/__init__.py; src/aitm_core/migration/__init__.py; src/aitm_core/ext/__init__.py; src/aitm_core/providers/__init__.py; src/aitm_core/index/__init__.py; src/aitm_core/reducers/__init__.py; src/aitm_core/setup/__init__.py; src/aitm_core/rules/__init__.py; src/aitm_core/execution/__init__.py; src/aitm_core/cli/__init__.py; pyproject.toml; packages/aitm-core/pyproject.toml; src/aitm_core/models/common.py; src/aitm_core/cli/app.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c01.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `CommandResult(operation_id, local, publication, pending, evidence, recovery); main() -> int; StoreAnchor, RefObservation, RefreshResult and ServicePorts structural records`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_installed_entrypoint: wheel installs on Python 3.13, aitm --help works without Node, JSON schema/version and distinct refused/conflict/integrity/pending exit codes round-trip. Imports make no Git/network/model call. Define mandatory ports for policy resolution/refresh, validation gate, write authorization, attempt preflight, init hooks, action retry and lane selection; absent required implementation returns unavailable. No permissive production fallback. Create regular packages with empty __init__.py files for every listed package; root aitm_core.__file__ must resolve to the installed wheel. Own lazy core route catalog in cli/catalog.py: a fixed route-to-module table for the complete CLI map below, loaded by cli/app.py without importing unused modules. A missing not-yet-delivered module reports unavailable, not success; each later command module exports its declared handler without editing this catalog. C09 cli/dispatch.py is the operation/publication executor, not the route registry. Install tests/unit/conftest.py autouse guards rejecting subprocess creation and network socket access before any unit leaf; integration tests verify those guards with deliberately failing temporary test cases. Pin Python/runtime/dev/build dependencies and root uv.lock: Pydantic, Typer, RFC8785 and strict-YAML support, pytest, Ruff and the chosen uv-compatible wheel builder. C03 may refine canonicalization dependencies under its explicit serialized manifest ownership; other later dependency additions require a coordinated allowlist/contract revision before edits, not an implicit permission. Own pytest import configuration: --import-mode=importlib in the package
  pyproject.toml, with tests/conftest.py adding only the resolved test-package parent to the harness import path. Tests are a regular tests package with the listed subpackage markers; helpers use qualified imports such as tests.support.shared_store and tests.packaging.installed_runner. Refuse a preloaded foreign tests package rather than silently importing it. Prove a cross-directory helper import in the integration scaffold and prove the test path setup does not add src/ or an editable core installation. Missing module/port negative vectors use deliberately unregistered test compositions and remain valid as later implementations land. The fixed lazy route catalog includes split, decompose, idea open and entity-scoped sync/unbind from the updated accepted design. Missing later handlers report unavailable; their owners install separate modules without editing the catalog. Declare mandatory KindRequirements, AggregateEvidence and StoryExitGuards slots with producer-owned protocols from C28/C29/C76/C79. Missing required kind/edge evaluators return unavailable/unknown; no generic story guard is applied to exempt kinds.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c01.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Keep scaffolding bounded to the core package; no meta-package or extension implementations.

### C02: Event envelopes and reducer dispatch invariants

**Estimate:** 2.5 h · **Depends on:** C01 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/events.py; src/aitm_core/events.py; packages/aitm-core/tests/unit/test_c02.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `validate_envelope(raw) -> EventEnvelope; fold(events, reducers: ReducerRegistry) -> StoryState`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_causal_envelope: same-timestamp/late occurrence preserves append order; sequence/prior digest and duplicate-ID/different payload fail. Reducer registry rejects missing required core reducer and retains unknown optional extension bytes. C54–C56 supply domain payload schemas and reducers before production fold is complete.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c02.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf owns only envelope/dispatch/causal identity, not every domain schema or clock algorithm. Unsupported required domains are unavailable, never folded as success.

### C03: Canonical authored content and metadata ownership

**Estimate:** 3.5 h · **Depends on:** C01 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C01. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** packages/aitm-core/pyproject.toml; uv.lock; src/aitm_core/models/documents.py; src/aitm_core/documents.py; packages/aitm-core/tests/unit/test_c03.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `canonicalize(raw: bytes, schema: DocumentSchema) -> ContentIdentity; rewrite_metadata(raw: bytes, generated: Metadata) -> bytes`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_canonical_vectors: RFC8785 vectors; semantic title/source/body change changes digest; generated updated/status changes do not; duplicate YAML keys, aliases/tags and unsupported fields fail. Body Unicode/whitespace remains exact. Prove the selected YAML loader rejects duplicate keys, aliases and tags explicitly; library defaults are not sufficient. Keep the package manifest and root lock consistent, with dependency selection serialized after C01. No later leaf silently adds another library. Pin the design's JSON-scalar resolver rather than YAML library defaults: true/false/null and JSON-number grammar only; yes/on/dates/0o12 remain strings, typed fields reject mismatches, unsafe integers/nonfinite values fail. Shared vectors cover quoted/unquoted forms, 1e3, leading zeros and ±(2^53−1) bounds. DocumentSchema supports the v1 semantic decomposition map; canonical content includes all descriptor fields, while descriptor-specific validation belongs to C72.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c03.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Dependency/library selection must prove RFC8785 rather than calling ordinary sorted JSON canonical.

### C54: Lifecycle, relationships and document-state reducers

**Estimate:** 3.5 h · **Depends on:** C02, C03 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/lifecycle.py; src/aitm_core/reducers/lifecycle.py; packages/aitm-core/tests/unit/test_c54.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `fold_lifecycle(state, event) -> StoryState; lifecycle_schemas() -> SchemaSet`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_lifecycle_reducers: initial/state/description/link/estimate/doc-accept/JIT/deliverable/signoff/disposition facts preserve typed state, reciprocal relation preconditions and source/version references; invalid edges/replacements/required fields reject. Pure event fixtures, no Git/process/network. Explicit graduation kind and source-kind draft|plan-entry are folded from facts. core.kind.changed records the bounded split invalidation, while decomposition/refine/plan/jit estimates remain distinct; a proposal cannot satisfy Refine. Preserve plan-entry source/provenance references and decomposition readiness status without claiming own-design acceptance.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c54.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Producer guards/transactions remain in later leaves; this reducer never invents an accepted review or state transition.

### C55: Attempt, execution and clock-boundary reducers

**Estimate:** 3.5 h · **Depends on:** C02 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/attempts.py; src/aitm_core/reducers/attempts.py; packages/aitm-core/tests/unit/test_c55.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `fold_attempt(state, event) -> StoryState; validate_boundary_batch(batch) -> None`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_attempt_reducers: prepared/admitted/started/uncertain phases differ; causal reservation/review/closure boundary requires matching prior/new clock mode and generation. No-child resolution and late activation reproduce pause/resume without mutable cache. RecoveryAuthority and BindingPurpose records specify allowed evidence-only scope.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c55.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This freezes boundary facts; observation eligibility arithmetic belongs to C23 and actual admission to C32.

### C56: Evidence, action and provenance reducers with composition

**Estimate:** 3 h · **Depends on:** C02, C54, C55 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C02. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/models/evidence.py; src/aitm_core/reducers/evidence.py; src/aitm_core/events.py; packages/aitm-core/tests/unit/test_c56.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `fold_evidence(state, event) -> StoryState; core_reducers() -> ReducerRegistry`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_complete_event_schema: every accepted-design event family has a payload schema and reducer or explicitly descriptive preserved fact; evidence/review-turn/action/outcome/usage provenance folds without duplicate authority. Compose C54/C55 through real fold and export complete JSON Schema. Include core.doc-review.opened and its source identity/time; a missing historical opening remains Unknown, not an invented runtime fact.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c56.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** C56 alone updates the shared reducer registration after C54/C55; no unfinished placeholder reducer is production-enabled.

### C04: Typed operations and MemoryBackend semantics

**Estimate:** 4 h · **Depends on:** C02, C54, C55, C56 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/operations.py; src/aitm_core/store/backend.py; src/aitm_core/store/memory_backend.py; packages/aitm-core/tests/unit/test_c04.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `Backend.read(snapshot: Snapshot, paths: Sequence[str]) -> Blobs; transact(op: Operation, expected: Snapshot) -> OperationResult; RelatedWriteSet(read_set, writes, events); FinalizationIntent(kind, version, related_preconditions, payload); WriteAuthorizer(owner, change) and PendingActionRunner(snapshot) ports; AttemptPreflight(context: OperationContext) -> PreflightResult; OperationCategory(normal, authored_sync, stop_reconciliation, recovery)`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_operation_cas: refusal records guards without transition; identical operation retry returns prior result, changed payload errors; stale read-set re-evaluates or conflicts, related-story update is atomic. Memory and later Git backends run same behavioral cases. Freeze category and applicability vectors: no attempt in the pinned read-set gives explicit not-applicable; attempt-bearing implementation mutation without installed AttemptPreflight reports unavailable. Stop/reconciliation and recovery categories have explicit narrow capabilities, not a blanket preflight bypass. Every pre-C31 attempt-bearing producer, explicitly C27 reconcile, C28 transitions and C30 expansion, uses an injected typed fixture preflight in test-only service composition; normal production remains unavailable when that required implementation is absent. attempt reconcile and expand both use category normal and require preflight; neither borrows stop_reconciliation/recovery to bypass trips. Stop/reconciliation categories cover only their separately declared narrow operations. WriteAuthorizer absence likewise refuses production writes before C14; C04–C08 backend tests use explicit fixture authority, not a shipped allow-all default. Test missing/fixture/real-registration distinctions and immutable category propagation across retries. Keep missing WriteAuthorizer and AttemptPreflight negative tests stable by deliberately unregistering the named slot in a test composition; do not assert permanent absence in the evolving production default.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c04.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Do not build a blind file-map API or a MemoryBackend with weaker semantics.

### C05: Git snapshot reads and atomic operation commits

**Estimate:** 4 h · **Depends on:** C04 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/store/git_backend.py; src/aitm_core/store/objects.py; packages/aitm-core/tests/integration/test_c05.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `GitBackend(Repository, ValidationGate).transact(op, expected) -> OperationResult; read_tree(oid) -> Snapshot`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_git_transaction: cat-file batch reads pin one tree; temporary index never touches user index; hash-object/commit-tree/update-ref CAS preserves all operation records. Inject crash before/after ref CAS and re-open by ID. Run C04 contract suite on real temporary Git.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c05.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** ValidationGate is an injected mandatory interface; production registration comes from C06, never an allow-all default.

### C06: Planning history validation and worktree exclusion

**Estimate:** 3.5 h · **Depends on:** C05, C01 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C01. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/validation.py; src/aitm_core/store/gate.py; src/aitm_core/services.py; src/aitm_core/cli/planning.py; packages/aitm-core/tests/integration/test_c06.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `validate_history(anchor: StoreAnchor, tip: str) -> ValidationReport; ref_gate(repo, target_ref: RefIdentity, purpose: RefMutationKind) -> ContextManager[Gate]; ForwardRepairVerifier(anchor, diagnosed_history, candidate) -> ValidationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_store_gate: empty-root/single-parent/data-path constraints; reject symlink/submodule/traversal/code/outside-path and code ancestry. Distinct review refs permitted. Serialize supported operations; inject external checkout between pre/post checks, retain both refs/index/unsynced bytes and fence publication. Wire ValidationGate into services.backend and planning validate; real planning validate and a normal GitBackend transaction must reject outside-path writes. No caller can omit the gate. Declare ForwardRepairVerifier as a mandatory typed validation seam for diagnosed repaired history; until C10 is installed, such history stays fenced. ref_gate(repo, target_ref, purpose) shares one clone lock but checks the exact target: planning validation is distinct from delivery content validation. Test missing ForwardRepairVerifier using an explicitly unregistered test composition; the negative case remains after C10 installation. Production registration proof belongs to C10 test_c10.py.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c06.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** The cooperative gate cannot prevent arbitrary transient external Git operations; diagnostics must state that limit.

### C07: Committed configuration and routing anchors

**Estimate:** 3 h · **Depends on:** C03, C06 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C06. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/config.py; src/aitm_core/models/config.py; src/aitm_core/store/installation.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c07.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `resolve_policy(anchor: Installation, refresh: RefreshResult) -> PolicySnapshot; classify_change(old, new) -> PolicyChange`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_policy_authority: story-edited limits/mode/commands are ignored; anchored code/default/store/issuer changes require reconfigure; tip-effective fields apply on next pinned policy evaluation. No remote/local ambiguity or unsupported policy silently defaults. StoreAnchor/RefreshResult structural types come from C01; wire services.policy from committed config. RefreshResult is an input port, not a future dependency on C08 implementation. Validate review.documents.design_coverage=own-document and the separate review.source schema/independence/assurance fields. Missing or unsupported inherited coverage stays unavailable; labeled fixture values are not product defaults. A delivered issuer/anchor change fences both modes; tip-effective githost configuration cannot redirect the anchored store.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c07.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Pure resolution consumes fetched facts; C08 owns network refresh and stale/unknown freshness.

### C08: Candidate fetch and shared-history continuity

**Estimate:** 3.5 h · **Depends on:** C06, C07 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C07. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/continuity.py; src/aitm_core/store/fetch.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c08.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `observe_shared(anchor, observation: RefObservation) -> SharedFrontier; refresh_refs(policy) -> RefreshResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_shared_frontier: rollback, deletion and valid sibling fence; valid unpublished divergence remains reconcilable; invalid descendant remains quarantined continuity checkpoint. Crash journal/ref updates, corrupt journal, first-clone rollback limitation and separate remote topology are visible. Wire services.refresh and the policy preflight: normal mutators refresh outside guards, cached reads do not, explicit --refresh uses the same candidate validator. Real command test rejects a story-edited policy and diagnoses stale remote preflight.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c08.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Never let a fetched receipt nominate its own anchor or replace the independently observed frontier.

### C13: Extension and provider registration contracts

**Estimate:** 3 h · **Depends on:** C02, C07 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/ext/api.py; src/aitm_core/ext/registry.py; src/aitm_core/providers/backlog.py; src/aitm_core/providers/githost.py; packages/aitm-core/tests/unit/test_c13.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `load_extensions(policy) -> Registry; register_activity(contract: ActivityProducerRegistration) -> ProducerRef; LocalGraduationAuthority.graduate(intent, finalization: FinalizationIntent) -> GraduationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_registration: dependency/version/order rules, cycles, duplicate namespace/IDs and unsupported measurement contracts refuse; installed-but-disabled stays disabled. BacklogProvider/GitHostProvider typed capabilities include observation, identity, publication, protection and pending unsupported results. Distinguish local atomic-graduation authority from externally issued IdentityResult pending finalization. Define InitStepRegistration and the Extension init_steps contribution plus lazy CLI/provider factories. These are schema/registry contracts; C63 owns installed entry-point discovery and production mounting/init routing, not a hidden unit-test registry.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c13.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No hosted endpoints, harness SDK or actual model invocation; fake providers exercise contracts.

### C14: Constrained extension writes and retained unknown data

**Estimate:** 3 h · **Depends on:** C04, C13, C08 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C08, C04. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/ext/ownership.py; src/aitm_core/ext/adapters.py; src/aitm_core/services.py; src/aitm_core/store/backend.py; packages/aitm-core/tests/unit/test_c14.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `authorize_write(owner: OwnerRef, change: Change) -> AuthorizedChange; resolve_adapter(owner, version) -> AdapterResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_ownership: real glob overlap with core/other owners, path-type changes, symlink escape and namespace mismatch fail at transaction boundary. Disabled/older records retain exact bytes; missing action/guard owner stays unavailable, not complete. Install WriteAuthorizer in the production transaction ingress and drive an extension write through the real operation API, proving reserved-path refusal before any tree/ref mutation. In test_c14.py prove production transaction ingress resolves the real WriteAuthorizer, while C04 explicitly unregistered-slot negative cases remain unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c14.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Trusted in-process extensions are not a hostile-code sandbox; preserve original action versions during replay.

### C15: Deterministic views and structured descriptions

**Estimate:** 2.5 h · **Depends on:** C02, C03, C04 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/store/render.py; src/aitm_core/description.py; src/aitm_core/cli/describe.py; packages/aitm-core/tests/unit/test_c15.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `describe(story, fields: DescriptionInput) -> Operation; render(state, authored, schema) -> Blobs`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_render: identical pinned inputs produce identical bytes despite wall clock; body and semantic fields survive metadata updates. Only describe owns description fields; generated details are never parsed; stable worktree labels replace physical paths in shared views.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c15.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Use typed events as authority; no reverse parsing from legacy generated JSON blocks.

### C09: Publication replay and conflict recovery

**Estimate:** 4 h · **Depends on:** C04, C08, C15, C14 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C14. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/services.py; src/aitm_core/cli/dispatch.py; src/aitm_core/store/publication.py; src/aitm_core/store/reconcile.py; packages/aitm-core/tests/integration/test_c09.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `publish(operation_id: str) -> PublicationResult; reconcile(operation_id: str, resolution: Resolution) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_publish_replay: two clones race disjoint operations, one FF push loses then safely replays whole operations with same IDs; related-story/policy/authored conflicts retain both sides. Lost ACK observes remote before retry. Local/pending/published states differ. Wire CommandService.execute so every ordinary mutating adapter attempts bounded publication after its local operation, even without --push. Real describe (C15) proves lost-ACK/pending output retains local completion; later C28/C49 prove the same path for promote. Read-only commands never invoke it.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c09.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No event union, stale positive guards or repetition of external side effects during replay.

### C10: Forward repair from maximal valid prefix

**Estimate:** 4 h · **Depends on:** C08, C09, C06 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C06, C09. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/validation.py; src/aitm_core/services.py; src/aitm_core/store/repair.py; src/aitm_core/cli/planning.py; packages/aitm-core/tests/integration/test_c10.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `plan_repair(anchor, bad_tip) -> RepairPlan; apply_repair(plan, expected_tip) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_maximal_prefix: fetch P→valid unseen V→bad B; repair extends B restoring V payload, rejects older P, retains invalid tail and unpublished recovery refs. Fresh clone reproduces prefix/proof. Shared code ancestry remains fenced. Install the ForwardRepairVerifier seam in the normal history validator: independently recompute the trusted maximal valid prefix and exact restored payload/repair receipt, allowing only that proved restoration after the retained diagnosed invalid span. Run real planning repair, then planning validate in a fresh clone; reject forged receipt, older non-maximal restoration or unprovable/code-shared ancestry. No receipt nominates its own anchor. In test_c10.py prove the production default resolves ForwardRepairVerifier and accepts independently verified repair through a normal fresh validation; C06 deliberately-missing-slot cases still run unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c10.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Repair restores valid current data only; no reset, rewrite or fabricated anchor repair.

### C11: Crash-resumable init and reconfiguration

**Estimate:** 4 h · **Depends on:** C07, C09, C10 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C10. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/setup/init.py; src/aitm_core/setup/journal.py; src/aitm_core/cli/setup.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c11.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `prepare_init(request: InitRequest) -> BootstrapProposal; resume_init(id) -> InitResult; reconfigure(proposal) -> AdoptionResult; InitHooks.install(context) port`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_init_resume: one UUID/genesis across interruption and rerun; prepare config without committing it; before landed anchor no remote publication/routine writes; afterward publish and protect. Fresh clone pending until original objects publish; explicit replacement proposal if irretrievable. Local-only and remote cases. The init pipeline calls its declared hook/doctor/provider steps; unavailable steps remain reported. C12 supplies and wires hook installation; readiness never silently marks an absent installer applied. Own --planning-branch <name> (default planning), the interactive accept/type prompt and validated Git-ref syntax. Refuse equality with the detected default branch. Refuse existing local or remote names unless complete history/store identity matches the trusted anchor or this same init journal; name existence alone is never reuse authority. Exercise a non-default records ref end to end through init, committed configuration, publication and ordinary mutation; no downstream code hard-codes planning. Test missing hook/doctor/provider steps in explicitly unregistered test compositions; C12 later proves production hook registration in test_c12.py without rewriting this negative vector. test_reconfigure_continuity exercises valid old/new anchor adoption, invalid/unprovable replacement refusal and an issuer/namespace switch that preserves every issued ID/provider reference. Ordinary delivered settings cannot bypass the adoption fence. Provider doubles prove the generic contract; no live GitHub claim.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c11.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Do not mutate global settings or overwrite foreign config; production adoption is not performed by this leaf.

### C12: Hook chaining and readiness diagnostics

**Estimate:** 3 h · **Depends on:** C06, C11 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C11. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/setup/hooks.py; src/aitm_core/setup/doctor.py; src/aitm_core/cli/doctor.py; src/aitm_core/services.py; src/aitm_core/setup/init.py; src/aitm_core/cli/setup.py; packages/aitm-core/tests/integration/test_c12.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `install_hooks(repo, policy) -> HookReport; doctor(context) -> ReadinessReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_hook_chain: preserve existing hooks/core.hooksPath; block ordinary planning commits and invalid pre-push candidates, permit review branches. Write root /.aitm/ ignore, diagnose broader foreign .aitm/ entry. Generic/manual host protection reports exact instructions and separate readiness facets. Invoke real aitm init and doctor to prove the hook installer is reached and foreign hook results retained. Doctor consumes the lane-probe port; C35 later wires the selector and C36/C37 provide platform profiles. In test_c12.py prove actual production init resolves the delivered hook installer. The missing lane-probe case deliberately unregisters that slot in a test composition so it remains true after C35; later production selector proof is in test_c35.py.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c12.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Hooks are optional and bypassable; core integrity must still pass with all hooks absent.

### C16: Authoring and implementation bindings

**Estimate:** 4 h · **Depends on:** C06, C07, C15 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/store/workspace.py; src/aitm_core/models/binding.py; src/aitm_core/cli/bind.py; packages/aitm-core/tests/integration/test_c16.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `bind(request: BindRequest) -> Binding; recover_binding(id, expected_generation) -> Binding; bind_purpose(purpose: BindingPurpose, authority: AuthorityRef) -> Binding`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_binding_generation: competing bind refuses, recovery exports unsynced bytes then fences old holder; planning binding cannot select default branch for implementation. Explicit existing branch, scrap new branch/refactor retained branch and stale receipt generation cases. Implement planning/implementation/deliverable/evidence purposes from C55. Evidence purpose requires an existing validated RecoveryAuthority and rejects implementation/expand/target-mutation capabilities; absent authority refuses. Later C61 produces that authority, not a new bypass flag. The Binding model distinguishes StoryRef from stable EntityRef and permits an entity-authored path allowlist without allocating a story number. Entity open/save/finalization integration is C74; purpose and generation checks remain the same core primitive, not a separate lock implementation.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c16.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Never create/remove/reset registered worktrees; use branch selection with explicit pinned baseline and allowed paths.

### C17: Allowlisted sync and authored conflict resolution

**Estimate:** 4 h · **Depends on:** C09, C14, C16, C12 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C12. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/sync.py; src/aitm_core/cli/sync.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c17.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `sync(binding, selected: PathSelection) -> SyncResult; unbind(binding) -> UnbindResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_sync: only owned authored inputs imported; scratch/generated/event/extension mutations diagnosed; explicit deletions cannot erase history; stale base retains both bodies. Failed unbind sync remains recoverable; rebind cannot redirect an old session. Invoke PendingActionRunner after the committed sync/publication result through its C04 port; until C43 installs the runner, report pending/unavailable without claiming completion. Test absent PendingActionRunner by explicitly unregistering that slot in test composition; do not assert that the evolving production default remains absent after C43. Expose the entity-scoped sync/unbind adapter seam over the same binding/base checks; C74 wires the opened-entity route and proves its positive behavior. An absent entity handler is unavailable, never a loose arbitrary-directory import. test_sync_reconcile_cli runs real sync --reconcile <operation-id> on a retained publication conflict, presents both versions and submits an explicit scoped resolution through C09.reconcile. It appends a new operation with supersession lineage; the old operation stays unpublished with its local evidence intact. Lost ACK reconciles that resolving operation once. test_sync_push_cli proves --push requests the same bounded default publication path, including retryable pending, without a second hidden sync or altered evidence. C17 owns both adapters in cli/sync.py; C09 remains their already-delivered library producer.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c17.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Reservation is clone-local; cross-clone conflicts remain publication conflicts, not a claimed global lock.

### C18: Snapshot index and read-only queries

**Estimate:** 3.5 h · **Depends on:** C02, C08 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/index/schema.py; src/aitm_core/index/build.py; src/aitm_core/index/query.py; src/aitm_core/cli/read.py; src/aitm_core/context.py; packages/aitm-core/tests/integration/test_c18.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `index_snapshot(tree: str) -> IndexView; query(snapshot, filter: Query) -> QueryResult; discuss(story, snapshot) -> ContextPacket`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_index_snapshot: WAL rebuild swap and concurrent readers never mix trees; missing/corrupt/locked index falls back to exact tree with equivalent results. FTS covers titles/descriptions/ideas/drafts/lessons; warm reads neither fetch nor publish. Real show/list/search/explain/discuss commands expose pinned freshness; --refresh invokes C08 explicitly, index rebuild uses the same snapshot. Discuss exports context and suggested harness command only, never calls a model. Until C78 supplies the full transition explanation adapter, explain reports that required explanation capability unavailable, alongside pinned freshness; it must not present the partial query view as a complete guard explanation. Other read commands remain usable. Its permanent missing-capability vector explicitly unregisters that handler in test composition.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c18.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Performance budget is checked in C52; avoid eager imports and hidden authoring claims now.

### C19: Ideas, drafts and atomic discard

**Estimate:** 2.5 h · **Depends on:** C09, C15 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/paths.py; src/aitm_core/drafts.py; src/aitm_core/cli/drafts.py; packages/aitm-core/tests/integration/test_c19.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `create_idea(input) -> EntityRef; create_draft(input) -> EntityRef; discard_draft(handle, reason) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_draft_identity: timestamp/slug collision gets checked suffix, stable IDs disambiguate handles, ambiguous bare slug lists candidates. Discard atomically removes live folder and adds per-draft tombstone with retained attachment/tree hashes. Discard retry uses stable entity/operation identity, colliding tombstone names receive a checked suffix, and graduated entities cannot be discarded. C74 adds open-entity binding/finalization checks on these same operations.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c19.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No shared append file, silent scratch import or deletion of graduated/retained history.

### C74: Entity-scoped editing and graduation handoff

**Estimate:** 3.5 h · **Depends on:** C16, C17, C19 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C16, C17, C19. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/entities.py; src/aitm_core/store/workspace.py; src/aitm_core/store/sync.py; src/aitm_core/drafts.py; src/aitm_core/cli/drafts.py; src/aitm_core/cli/sync.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c74.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `open_entity(handle: EntityRef) -> Binding; sync_entity(handle, expected_generation) -> SyncResult; finalize_entity_binding(source, outcome) -> BindingDisposition`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_entity_authoring drives idea open and draft open, real sync --entity/unbind --entity, edits and repeated saves without a story number. Expected-base conflict retains both versions; wrong owner/stale generation/escape/generated metadata refuses. The finalization seam computes a validated binding disposition for the caller's same source-finalization CAS; it makes no independent commit. Graduation/discard includes it to end/fence the exact binding and preserve unsynced conflicts, never silently retargeting the open editor to a numbered story. Unbind failure remains recoverable. Reuse C16/C17 primitives and a small temporary-repository fixture; do not duplicate the binding engine.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c74.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf completes pre-story editing, not a second authoring system. C22 later proves graduation invokes the seam with actual issue finalization; discard is exercised here.

### C20: Semantic identity reservations and uncertain dispatch

**Estimate:** 3.5 h · **Depends on:** C09, C13, C19, C74 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/providers/identity.py; src/aitm_core/models/identity.py; packages/aitm-core/tests/integration/test_c20.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `reserve_identity(intent: GraduationIntent) -> IdentityReservation; dispatch_or_observe(reservation) -> IdentityResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_identity_once: two operation IDs for one entity share one semantic reservation; two senders cannot dispatch twice. Lost creation response reconciles lookup proof before retry; uncertain cancellation keeps intent; unsupported safe reconciliation returns pending. GraduationIntent owns a tagged FrozenSource contract: draft identity/snapshot or plan-entry parent/key/design-plan-entry digests and typed descriptor. The semantic entity key is source-specific and excludes mutable revision digests. All reservation/dispatch/reconciliation logic uses that key, never a draft-only predicate. The plan-entry parser is supplied later by C72/C75; unavailable source preparation cannot dispatch.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c20.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Provider doubles establish the contract, not live GitHub capability; retain external identity even if finalization conflicts.

### C22: Graduation and atomic relationships

**Estimate:** 3.5 h · **Depends on:** C15, C20, C74 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/graduation.py; src/aitm_core/relationships.py; src/aitm_core/cli/stories.py; packages/aitm-core/tests/integration/test_c22.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `build_graduation(intent, source: FrozenSource, candidate: CandidateIdentity, finalization: FinalizationIntent) -> Operation; finalize_external_identity(reservation, expected_draft, finalization: FinalizationIntent) -> OperationResult; link(change) -> OperationResult; materialize_finalization(intent, chosen_child, pinned_snapshot) -> RelatedWriteSet; register_finalizer(kind, version, handler) -> FinalizerRegistry`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_graduate_links: exact draft moves with original facts/attachments, numbered story initialization and parent reciprocal links commit together. Concurrent draft edit conflicts; parent/dependency/replacement cycles and self-links refuse. Resume returns same issued identity. Supply the pure construction seam (number, exact draft move, initialized story, reciprocal relations and initial projection identity) before C21 local authority. External issuance may remain retained pending finalization; the local path may not expose such a partial permanent ID. FinalizationIntent is durable typed semantic input, not pre-rendered writes or a serialized callback. Core dispatches its registered kind/version through materialize_finalization(intent, chosen_child, pinned_snapshot) -> RelatedWriteSet after choosing the candidate. Ordinary graduation yields empty related changes; C30 supplies the expansion finalizer. The external finalizer first obtains the actual reconciled issuer identity, then materializes and atomically commits the same related facts after rechecking current origin reservation; a fenced origin retains issued identity pending scope reconciliation, never attaches it automatically. Record explicit resolved kind (omission default story) and source kind. For draft sources move the frozen draft; for plan entries initialize description from the already validated frozen descriptor without creating/moving a draft. Parent/cycle checks and one atomic numbered-story construction apply to both. Refuse an unvalidated source; C75 owns CLI plan-source preparation. Graduation finalization fences an existing entity binding via the C74 route and retains conflicting
  unsynced bytes.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c22.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Epic parent and expanded_from remain separate; dependent needs explicit resolution for non-delivered terminal outcomes.

### C21: Shared local number allocation

**Estimate:** 3.5 h · **Depends on:** C22, C17, C74 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C74, C22. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/providers/local.py; src/aitm_core/services.py; src/aitm_core/cli/stories.py; packages/aitm-core/tests/integration/test_c21.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `graduate_local(intent: GraduationIntent, finalization: FinalizationIntent) -> GraduationResult; project_latest(publication, key) -> ActionResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_allocator_two_clones: real graduate invokes C22 build_graduation inside one candidate operation; inject failure after number proposal/before construction and assert no permanent ID, moved draft, usable numbered story or partial relationship/action exists. Local CAS atomically commits all surfaces; shared mode exposes ID only after verified publication. Two drafts race for one number, loser rebuilds complete transaction under same semantic intent; lost ACK observes result. Same draft exposes one ID; offline candidates stay unissued. Pass FinalizationIntent to C22 construction after choosing each candidate. Every losing-number retry re-runs materialize_finalization with the newly chosen child ID and fresh snapshot; never reuse a RelatedWriteSet containing the old candidate. No caller may expose a proposed number before the complete operation is authoritative.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c21.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** C21 implements the C13 LocalGraduationAuthority.graduate(intent, finalization) method by delegating to graduate_local, and wires it into the existing graduate adapter. Allocation is internal candidate construction, never a separately exposed durable local ID; externally issued pending identities retain their distinct C20/C22 semantics.

### C23: Activity eligibility and implementation clock fold

**Estimate:** 3.5 h · **Depends on:** C02, C13 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/rules/timing.py; src/aitm_core/activity.py; packages/aitm-core/tests/unit/test_c23.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `ingest_activity(producer, observations) -> EventBatch; engagement(state, observations) -> CoverageReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_engagement_bounds: five-hour unattended tool run does not prove engagement; eligible fixture producer through real registry proves over-four-hour lower bound. Same actor overlaps union, distinct actors sum, pause/review boundaries intersect; skew/late/duplicate/gap>15min stays qualified/Unknown.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c23.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Fixture measured engagement is not a claim of real harness observation; planning time never triggers trips.

### C24: Portable review schemas and patch reconstruction

**Estimate:** 3 h · **Depends on:** C02, C03, C56 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/portable.py; src/aitm_core/reviews/patches.py; packages/aitm-core/tests/integration/test_c24.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `reconstruct_bundle(folder) -> ReconstructedReview`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_portable_reconstruction: parse v0 response/manifest schemas; replay repository-relative patch 000 plus all author deltas including empty ACK in a private directory; compare every reviewer input/author output/raw digest and final bytes. Reject escapes, symlinks and executable payload; retain immutable originals. Runs in integration lane if Git apply is used.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c24.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf proves bytes/schema/round-chain only. It cannot grant acceptance before C57 topology/finding/assurance validation and C58 native mapping.

### C33: Private immutable input capture

**Estimate:** 3 h · **Depends on:** C07, C16 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/verification/capture.py; src/aitm_core/models/verification.py; packages/aitm-core/tests/integration/test_c33.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `capture_inputs(binding, policy) -> CapturedInputs`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_capture_manifest: clean tracked tree plus declared extra globs copied without hardlinks outside worktrees; reject missing extras, traversal, symlinks and output overlap. Transient original-worktree edits cannot affect capture; later head/manifest change makes applicability stale.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c33.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Private export is not OS containment; preserve input manifest and hash before execution.

### C34: Offline environment provisioning and cache identity

**Estimate:** 3 h · **Depends on:** C33 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/verification/provision.py; src/aitm_core/cli/test_prepare.py; packages/aitm-core/tests/integration/test_c34.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `provision(inputs, policy, offline: bool) -> PreparedEnvironment; validate_environment(record, inputs) -> EnvironmentResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_provision_policy: deny/offline cache miss names exact retry; allow policy provisions only declared dependencies, reuses only lock-hash-verified copied cache. Stale lock/tool/policy/inventory refuses reuse. Store identity metadata clone-locally and record no planning event for provisioning alone.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c34.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Use git-common-dir/aitm/verification/environments/<content-id>.json; call this environment provisioning, distinct from execution admission prepared. Never modify global environment.

### C57: Review finding closure, topology and policy assurance

**Estimate:** 2.5 h · **Depends on:** C24 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/topology.py; src/aitm_core/reviews/policy.py; packages/aitm-core/tests/unit/test_c57.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `validate_review(record: ReconstructedReview, policy) -> ValidatedReview; compare_participants(left, right, mapping) -> IdentityRelation`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_review_policy: enforce round order/finding disposition/final exhausted decision, reject cap acceptance, identical-session SPR and same-provider XPR, contradictory/unknown identity comparisons and disallowed assurance. Test declared-manual/native-unavailable permitted only by explicit fixture policy and documented identity mapping.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c57.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No required-level default is selected. This validates one level and its assurance; current-content set evaluation is C26.

### C58: Native review lineage and timing anchor adapters

**Estimate:** 2.5 h · **Depends on:** C57 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/native.py; src/aitm_core/reviews/anchors.py; packages/aitm-core/tests/integration/test_c58.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `map_native(originals) -> PortableFacts; validate_bundle(folder, policy) -> ValidatedReview`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_native_mapping: actual accepted native originals bind input hashes, outgoing author artifacts, finalization-versus-revision commits and safe claim/predecessor anchors. Unsubmitted/blocked drafts stay unaccepted. Public source hashes and native fingerprint identity kinds survive without private handles or registration-time reuse.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c58.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Compose C24/C57 validation; no rewrite of protected original bytes or dependency on retained intermediate review commits.

### C25: Live review capsules and qualified turn timing

**Estimate:** 3 h · **Depends on:** C09, C23, C58 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/turns.py; src/aitm_core/reviews/timing.py; src/aitm_core/cli/review_turns.py; packages/aitm-core/tests/integration/test_c25.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `open_review(request) -> LevelRecord; record_turn(level, response) -> OperationResult; complete_review(level, bundle) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_live_backfill_same_fact: open before first turn without precommit, ingest provisional response, complete then reimport => one normalized turn. Claim/prior-submit anchors and hashes reproduce derivation; registration reuse/interruptions/exclusions keep response duration Unknown; state-boundary attribution and concurrent actor/wall totals stay distinct. Persist core.doc-review.opened with the capsule in one transaction and use that real open only as the level's outer start. Rebuild after interruption reproduces the open; legacy missing-open records retain qualified provenance/Unknown, not a synthesized start.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c25.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** An elapsed outer bound is not engagement. Changed bytes under same turn identity conflict; corrected interpretation appends provenance.

### C26: CAS review import and exact-content acceptance

**Estimate:** 3.5 h · **Depends on:** C14, C17, C25, C58 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/importer.py; src/aitm_core/reviews/acceptance.py; src/aitm_core/cli/review_import.py; src/aitm_core/cli/design.py; src/aitm_core/cli/plan.py; packages/aitm-core/tests/integration/test_c26.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `import_review(binding, bundle, expected_base) -> OperationResult; evaluate_acceptance(doc, policy, records) -> AcceptanceResult; accept_document(role, validated_review, expected_doc, policy) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_exact_content: SAR(A) SPR(B) XPR(C) cannot accept C under exact-content three-level policy; add missing levels on C, edit to D recomputes all obligations. Metadata-only rewrite preserves canonical binding. Stale FUR/collateral conflicts and immutable original overwrite refuse. Drive real design accept --review and plan accept --review: persist core.doc.accepted only for validated current content/policy, with plan generation; import/evaluation alone does not append acceptance or satisfy guard. Own-document coverage is explicit: parent plan acceptance alone cannot satisfy a child design guard, and missing/unsupported coverage policy is unavailable. Consume the typed decomposition applicability port declared here (C72 implements it) for plan-entry children; an absent required port cannot infer freshness. Ordinary draft-origin cases do not require that port.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c26.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Production level matrix remains owner-open; fixture policy explicitly permits manual/native-unavailable assurance. Scoped exception requires committed authority/digest/validity.

### C27: Attempts, JIT coverage and estimates

**Estimate:** 3 h · **Depends on:** C16, C23, C26 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C26. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/attempts.py; src/aitm_core/jit.py; src/aitm_core/estimates.py; src/aitm_core/cli/plan.py; packages/aitm-core/tests/unit/test_c27.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `record_jit(request: JitRequest) -> OperationResult; assess_jit(plan, attempt, baseline, changes) -> JitResult; reconcile_attempt(attempt, plan, binding) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_jit_scope: unchanged or proven unrelated descendant baseline passes; touched dependencies, incomplete coverage, non-descendant, old plan/generation/attempt require fresh JIT. Refine/Plan/JIT estimates retain original source and priority; epic size not limited to four hours. Define provisional attempt evidence attachment operation reconcile_attempt(attempt, plan, binding): same attempt/clock/allowance is retained; only actual scope/trip replan creates new generation. CLI attempt reconcile persists those facts. JIT supports research/deliverable input baseline as well as source code. The pre-C31 in-process MemoryBackend CLI reconcile proof injects the declared typed preflight fixture; attempt reconcile is category normal and requires preflight. No subprocess/Git is introduced into this unit lane. C70 repeats its positive and refusal behavior with the actual installed preflight after C64 supplies shared fixtures. A decomposition estimate is a retained initial proposal. test_decomposition_estimate requires an explicit phase=refine record after own-design acceptance, optionally adopting the same value with source/rationale; proposal history never becomes an invented Refine observation.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c27.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Accepted parent plan is not automatic leaf acceptance; initial provisional advisory attempt never resets budget when evidence arrives.

### C72: Typed decomposition descriptors and applicability

**Estimate:** 3.5 h · **Depends on:** C03, C07, C20, C26, C27 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C26. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/models/decomposition.py; src/aitm_core/decomposition.py; src/aitm_core/reviews/acceptance.py; packages/aitm-core/tests/unit/test_c72.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `prepare_plan_entry(snapshot, epic, key, expected_plan) -> FrozenSource; assess_decomposition(child, parent_snapshot) -> ApplicabilityResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_plan_entry_contract validates the accepted v1 semantic decomposition map: stable unique entry keys, kind, structured description/scope, estimate/size/priority and dependency keys. Canonical descriptor bytes/digest and accepted parent design/plan digests bind the source; arbitrary Markdown cannot be inferred as a descriptor. Entity key (store UUID,parent,key) survives plan revisions, while changed source requires reconciliation. Missing references/cycles/unsupported schema refuse. Own-document policy never accepts parent-only coverage; missing/unsupported coverage stays unavailable. Decomposition proposal does not satisfy Refine; parent design/plan changes produce stale applicability even if entry text is unchanged. Implement the C26 applicability port using pinned typed facts and MemoryBackend, without issuing identities or invoking Git/network.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c72.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Pure preparation/applicability has a separate gate from C75's live identity and CLI integration. Do not add inherited-design coverage or synthesize historical drafts.

### C28: State transitions and atomic guard outcomes

**Estimate:** 4 h · **Depends on:** C15, C22, C26, C27, C17, C21, C09, C72 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C21, C09. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/services.py; src/aitm_core/cli/dispatch.py; src/aitm_core/machine/states.py; src/aitm_core/machine/transitions.py; src/aitm_core/machine/guards.py; src/aitm_core/cli/lifecycle.py; packages/aitm-core/tests/integration/test_c28.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `transition(request: TransitionRequest) -> OperationResult; explain(snapshot, story) -> TransitionExplanation`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_transition_matrix: eight-state edges and entry/exit slots evaluated core then stable extensions on one pinned read-set. Enforce refusal records no transition; advisory advances with failed guards; illegal edge/integrity never waived. CAS race re-evaluates all related predicates. Real advisory promote to Develop with absent plan and implementation-unbound creates one provisional attempt/clock and failed guards. Later accepted plan, bind --implementation and attempt reconcile preserve attempt ID, cumulative coverage and consumed allowance. Own the normal state-command pipeline: C04 typed preflight first (declared fixture until C31 installs the real implementation), then C17 sync of eligible bound authored inputs as a separate saved/reported operation, then pin a fresh planning/policy/read-set before transition evaluation. Authored-sync has its own operation category so it does not recursively request pre-sync. A sync conflict retains both versions and prevents the normal transition; successful sync is not rolled back by a later guard refusal. Run these real CLI/Git/binding/sync cases in integration, with the preflight fixture explicitly supplied to the test service composition. Separately assert an attempt-bearing command returns preflight-unavailable with that slot deliberately unregistered in an explicit test service composition; no permissive fallback is enabled. The transition matrix itself may use MemoryBackend within this integration suite. C31 proves one representative real promote/qualifying-stop pipeline; C70 separately qualifies provisional-attempt/reconcile behavior with actual production preflight. The complete early-state matrix
  covers Backlog description/own-design acceptance, Refine estimate/size/priority and Ready dependency satisfaction for all kinds. Four-hour leaf-size applies to story/defect/spike; an epic may have a larger aggregate estimate. Plan-entry provenance/readiness uses the C72 port, not parent-plan acceptance as a leaf design pass. Its pre-C75 producer tests explicitly inject that typed implementation; C75 proves actual production registration and unavailable behavior without rewriting those fixtures. Declare the typed KindRequirements and StoryExitGuards ports used by the transition evaluator. C29 installs kind selection/substitutions; C76 installs story/defect Develop-exit source evaluation and C79 installs Test/Review composites in the same edge-dispatched StoryExitGuards port. Unknown/missing required evaluation cannot become pass; enforce refuses, advisory records unknown, and integrity rules remain mandatory. Earlier fixture-composed producer tests explicitly inject these typed ports; no default permissive implementation. C28 explain returns a TransitionExplanation over that same pinned evaluator; C78 owns its installed read-command wiring.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c28.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Resident action identities are persisted in transaction; action execution belongs to C43, never an unrecorded callback.

### C71: Bounded Refine split and kind invalidation

**Estimate:** 3.5 h · **Depends on:** C28, C22, C26, C27 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C28. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/splitting.py; src/aitm_core/machine/transitions.py; src/aitm_core/machine/guards.py; src/aitm_core/cli/split.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c71.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `split_leaf(request: SplitRequest) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_refine_split drives split --reason --scope-file on an oversized pre-Develop Refine story/defect/spike. One CAS keeps the permanent ID, records core.kind.changed and revised scope, returns to Backlog and invalidates effective old design/plan/JIT/estimate applicability while retaining all history. Reject expansion children, an existing attempt, unresolved execution/identity and bad relationships. A concurrent source/state change forces reevaluation or retained conflict. New own aggregate design and Refine estimate are required; Plan exit requires accepted nonempty child coverage, not conversion alone. For later Plan/JIT oversizing exercise the existing design-rework edge from Plan/JIT to Backlog, then Backlog→Refine before split; no Plan→Refine edge or post-attempt conversion. Use already delivered normal graduation/link to attach children; split dispatches no remote issue call.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c71.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** The 3.5 h budget reuses transaction, edge, description and acceptance primitives; general kind editing is out of scope. Wire the production route and guard invalidation at the listed call sites.

### C29: Kind-specific guards and terminal dispositions

**Estimate:** 4 h · **Depends on:** C28, C71 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C71. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/kinds.py; src/aitm_core/dispositions.py; src/aitm_core/cli/dispositions.py; packages/aitm-core/tests/integration/test_c29.py; src/aitm_core/machine/guards.py; src/aitm_core/machine/transitions.py; src/aitm_core/services.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `kind_requirements(kind, slot) -> Requirements; dispose(request: DispositionRequest) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_kind_matrix: epic initial Develop does not need children already active or its own JIT/PR/test; later aggregation requires child evidence/resolved scope. Spike uses deliverable binding/validation. Abandoned/superseded/duplicate need reason and replacement where required; no automatic dependency satisfaction. test_kind_registration uses actual promote through production KindRequirements registration in services.py and the C28 guards/transitions call sites. Story/defect later exits dispatch to the required StoryExitGuards port; an absent required edge evaluator is unknown/unavailable until C76 (Develop) or C79 (Test/Review). Spike substitutions read registered immutable deliverable/validation/review/archive facts, never source-commit or story-test requirements. Epic Plan exit needs a nonempty accepted child set, Develop entry needs no binding/JIT/clock, and later exits call the typed AggregateEvidence port declared here, installed by C62. Before the later evidence producers exist, these integration cases explicitly seed authoritative typed fixture facts and inject fixture aggregate evidence; a separately unregistered aggregate port refuses. Production registration and normal entry are proved, not import-time side effects.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c29.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Producers of source/deliverable evidence are later leaves; guards consume typed applicability and fail unknown conditions honestly.

### C30: Expansion reservation and resolution

**Estimate:** 4 h · **Depends on:** C20, C21, C22, C23, C28, C29 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C29. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/rules/expansion.py; src/aitm_core/cli/expand.py; packages/aitm-core/tests/integration/test_c30.py; src/aitm_core/services.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `reserve_expansion(origin, intent) -> OperationResult; resolve_expansion(origin, proof) -> OperationResult; build_expansion_related(finalization, chosen_child, snapshot) -> RelatedWriteSet`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_expansion_gap: reservation atomically consumes allowance, blocks/pauses origin before identity call; delayed/lost response and finalization never expose unblocked gap. Cancellation needs non-issuance/fencing proof, child delivery/disposition resolution updates all related facts. Local expansion uses C21 graduate_local with C22 construction: after the earlier allowance/pause reservation, materialize the durable FinalizationIntent into RelatedWriteSet using the exact live origin attempt/reservation and the actual chosen child, replace reservation block with child block, and append expansion/clock facts in the same child-number/story CAS. Real expand in local-only and shared stores tests construction failure, competing clone and lost ACK: no permanent number/usable child before authority, one child per intent and no unblocked interval. External uncertain issuance remains the distinct C20 protocol. Own build_expansion_related(finalization, chosen_child, snapshot) and register the core expansion finalizer with C22. Both local candidate retries and external lost-response finalization call it after identity selection. Assert origin block, expansion events, reciprocal child facts and projection identity all name the winning child ID; no duplicate finalization or attachment to a fenced origin and no unblocked interval. These pre-C31 real expand tests explicitly inject the declared typed fixture preflight into test-only service composition. expand is category normal and always requires preflight, including second/nested requests; no stop/recovery exemption is introduced. C70 repeats the local/shared construction-failure, competing-clone and lost-ACK
  vectors with actual production preflight using C64 fixtures. Expose --kind defect|story --draft <handle> --reason; freeze the source and initialize the child in Backlog. Its own design/Refine/plan/JIT gates precede its Develop clock while the origin remains paused. Install build_expansion_related in the C22 finalizer registry from services.py during explicit service composition, never an import-time callback. test_expansion_finalizer_registration runs normal expand using that production registration and verifies the one related write-set; an explicitly unregistered finalizer returns unavailable before exposing a child. Keep the pre-C31 typed preflight fixture explicit.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c30.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Second/nested request detection is C31; no child ID must not mean no reservation.

### C31: Trip ordering, replan decisions and human pivots

**Estimate:** 4 h · **Depends on:** C23, C27, C28, C30, C14, C17, C71, C74, C29 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C30, C14, C74, C29. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/services.py; src/aitm_core/store/backend.py; src/aitm_core/store/sync.py; src/aitm_core/machine/transitions.py; src/aitm_core/rules/trips.py; src/aitm_core/pivots.py; src/aitm_core/cli/trips.py; packages/aitm-core/tests/integration/test_c31.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `preflight_attempt(context) -> TripResult; decide_trip(decision) -> OperationResult; pivot(human_context, change) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_trip_precedence: confirmed overrun/second/nested expansion wins before ordinary sync/action/pass, atomically fences origin/child and demotes in enforce; advisory reports. Rework keeps budget, accepted replacement resets; continue/fold/abandon child scope stays coherent. Known agent cannot override pivot via --as-human. Wire the C04 AttemptPreflight port into CommandService before ordinary authored sync/mutation, backend decision retry before every CAS, and before effective completion. Stop/reconciliation operations use a typed non-implementation category to avoid recursive normal guards while retaining integrity. Actual sync after a proven trip preserves unsynced workspace bytes without importing them first; injected retry rechecks the new stop. In its own test_c31.py, prove the production default resolves AttemptPreflight and exercise one representative real C28 promote pipeline with a qualifying stop. Its own deterministic unit/single-store cases retain second/nested expansion and CAS-retry semantics; it does not reproduce the three predecessor suites or construct new two-clone infrastructure. C70 separately owns C27 reconcile, C28 provisional-attempt/reconcile and C30 local/shared construction-failure/competing-clone/lost-ACK re-proofs after C64. Earlier deliberately-unregistered and fixture-composed suites remain valid unchanged. The 4 h estimate covers only this bounded trip/pivot/decision implementation, three wiring points and representative pipeline proof. test_human_pivot uses a controlled genuine interactive-actor fixture, alongside known-agent/tool and --as-human refusal. Verify separate core.pivot.recorded (no fabricated trip),
  atomic affected origin/child Plan demotion, admission fences/cancellation status, coherent child disposition and fresh next accepted-plan attempt. Outcomes preserve pivot versus planning-failure attribution and the stated actor-authentication limit.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c31.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Expansion completion interpretation and second-trip cap remain open observations, not new default guards; actor heuristics are not authentication.

### C32: Single-use execution admission and cancellation

**Estimate:** 3.5 h · **Depends on:** C09, C16, C31 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/execution/admission.py; src/aitm_core/execution/executor.py; packages/aitm-core/tests/integration/test_c32.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `admit(request: ExecutionRequest) -> AdmissionResult; dispatch(admission, executor) -> ExecutionResult; cancel(admission) -> CancellationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_admit_stop_orders: race admission/stop both ways; offline shared clone cannot launch after published stop; local-only durable CAS needs no remote. Last cancellation check/process creation serialized; crash/lost outcome never dispatches replacement generation. Events expose prepared/admitted/started/uncertain separately. Executor invokes the installed AttemptPreflight before admission and immediately after retained result/activity ingestion, before any effective success. Completion with a pass plus qualifying overrun records stop first; no result can first stop the clock by activating review.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c32.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Cannot instantly recall disconnected remote work; cancellation-pending is truthful. Retained stale output cannot advance stopped attempt.

### C35: Captured-export test execution and receipts

**Estimate:** 3 h · **Depends on:** C12, C32, C34, C31 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C31, C12. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/verification/run.py; src/aitm_core/verification/receipts.py; src/aitm_core/cli/test.py; src/aitm_core/verification/lanes.py; src/aitm_core/services.py; src/aitm_core/setup/doctor.py; packages/aitm-core/tests/integration/test_c35.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `run_verification(admission, prepared, assurance) -> VerificationResult; LaneAdapter.probe(resources) -> ContainmentCapability; LaneAdapter.command(prepared) -> ProcessLaunch; select_lane(policy, platform) -> LaneAdapter`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_captured_run: real passing/failing subprocess and retained logs; read-only inputs/separate writable roots; uv prepared env/no-sync/offline, no bytecode and redirected pytest cache. Persistent mutations or weaker-than-policy assurance produce diagnostic result. Receipt binds actual capture, command transformation and output hashes. Wire selector into real test/deliverable executor and doctor/init readiness port. Contained selects platform adapter C36/C37; missing/failing probe returns pending before admission/launch, with no fallback. Every ProcessLaunch executes through C32 and receipt records selected/proven assurance. In test_c35.py prove actual production execution/init/doctor resolve the installed LaneAdapter selector; C12 deliberately-missing-slot negative vectors remain unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c35.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Explicitly allow bounded captured-export only under selected policy; do not assert it prevents chmod self-mutation, undeclared host reads or arbitrary network.

### C73: Source-review envelope and independence validation

**Estimate:** 3 h · **Depends on:** C07, C16, C56, C57 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/source_review.py; src/aitm_core/reviews/source_record.py; packages/aitm-core/tests/unit/test_c73.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `validate_source_review(record, responses, binding_history, policy) -> ValidatedSourceReview`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_source_review_record parses aitm.source-review/v1: stable ID/story/attempt/reviewed generation, repository/base/head/tree/input-manifest or deliverable digest/baseline, participant identities/provenance, verdict, findings/dispositions, immutable response paths/digests and assurance. Retain/cross-check actual bytes; reject path escape, changed identity bytes, omitted implementing session, self-review, incomparable identity, source mismatch and unresolved required finding. Independence checks every implementing session from retained bindings, not caller claims; optional distinct-provider and allowed-assurance policy are enforced. Preserve declared-manual limits and require observation proof for provider claims. Recovery lineage may map unchanged-source generation explicitly, never by ignoring it. These are pure typed/bundle validation tests; activation and event writes belong to C38.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c73.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Reuse C57 compare_participants and its explicit unknown relation, not a second heuristic. No provider endpoint or authentication claim is invented.

### C36: macOS contained-lane probe and profile

**Estimate:** 3.5 h · **Depends on:** C35 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/verification/containment_macos.py; packages/aitm-core/tests/platform/test_c36.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `probe_macos(resources) -> ContainmentCapability; macos_profile(inputs, outputs) -> ProcessProfile; macos_adapter() -> LaneAdapter`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_macos_containment: where supported, descendant process cannot write sources/dependencies, read undeclared roots, network or escape profile; writable outputs work. Unavailable/deprecated sandbox-exec reports exact capability gap and remains pending under contained policy. The selector loads this adapter by platform through C35 fixed registration. Test actual installed aitm doctor/init and aitm test under committed contained policy, asserting the managed descendant process uses the profile and receipt names contained. Separately committed captured-export policy still runs its bounded nominal lane.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/platform/test_c36.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No machine permission changes to make tests pass. Capture OS/tool versions and supported/unsupported distinction; run on actual macOS.

### C37: Linux contained-lane probe and profile

**Estimate:** 3.5 h · **Depends on:** C35 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/verification/containment_linux.py; packages/aitm-core/tests/platform/test_c37.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `probe_linux(resources) -> ContainmentCapability; linux_profile(inputs, outputs) -> ProcessProfile; linux_adapter() -> LaneAdapter`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_linux_containment: supported user/mount/network namespace and filesystem profile confines process tree, sources/environment read-only and outputs writable; remount/privilege escape fails. Disabled namespace/kernel/helper capability returns diagnostic pending, never downgrade. The selector loads this adapter by platform through C35 fixed registration. Test actual installed aitm doctor/init and aitm test under committed contained policy, asserting the managed descendant process uses the profile and receipt names contained. Separately committed captured-export policy still runs its bounded nominal lane.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/platform/test_c37.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Run on actual Linux; no sysctl/global permission edits. Capability tests distinguish supported enforcement from denial-path-only proof.

### C38: Source review evidence and effective pass activation

**Estimate:** 3.5 h · **Depends on:** C29, C35, C73 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/reviews/source.py; src/aitm_core/reviews/activation.py; src/aitm_core/cli/review_source.py; packages/aitm-core/tests/integration/test_c38.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `record_source_review(evidence) -> OperationResult; reconcile_review(story, source) -> ActivationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_effective_review: retained early pass cannot stop time until Review and all predecessor evidence apply; source changes/rework invalidate and reopen remaining clock. Provider claims require observation; declared core-only review needs retained source/session/provenance, not bare pass. Before activation, call the same C31 preflight after retained evidence ingestion and on each CAS retry. The normal review pass command with a qualifying overrun cannot activate its pass before the stop. Consume C73's validated source-review envelope rather than parsing ad hoc JSON here. Prove actual review pass cannot activate self-review, unknown identity, missing response bytes, unresolved required findings or stale source/attempt/generation; the conforming independent record stops time only at genuine eligible activation. Reuse the validated binding-history participant set and explicit current source-review policy. Any producer test here that crosses a story/defect Develop/Test/Review exit uses an explicitly composed typed StoryExitGuards fixture until C76/C79 deliver the real evaluators. An explicitly unregistered required edge must refuse as unavailable; no permissive production default. C49/C68 and C65/C66 later re-prove the relevant paths with actual C76/C79 registrations and specific guard causes.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c38.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Activation/clock events commit together; later valid proof cannot invent earlier review stop.

### C39: Positive delivery observation and archival proof

**Estimate:** 3.5 h · **Depends on:** C38 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/delivery/observe.py; src/aitm_core/delivery/trees.py; src/aitm_core/cli/deliver.py; packages/aitm-core/tests/integration/test_c39.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `observe_delivery(request: DeliveryRequest) -> DeliveryResult; verify_integration(inputs, observed) -> MappingResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_delivery_content: observed ordinary checked-out-target merge succeeds only for exact clean integration tree/parents; FF exact source succeeds. Ours merge, dropped delta, unreviewed conflict resolution and issue-closed-only evidence fail. Spike archive confirms exact bytes; unavailable remote capability stays pending.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c39.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Observation is not permission to merge; source and delivered SHAs may differ only with verified mapping.

### C40: Reviewed squash and rebase transformation plans

**Estimate:** 3 h · **Depends on:** C39 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/delivery/transforms.py; packages/aitm-core/tests/integration/test_c40.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `plan_transformation(inputs: DeliveryInputs, method: DeliveryMethod) -> ApprovedTransformation`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_transform_mapping: pinned pretarget/base/source yield reproducible approved tree/commit mapping for squash/rebase; changed target or conflict requires new reviewed result, not strategy-name acceptance. External transformation without adequate proof remains pending.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c40.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Planning transformation never mutates target. Record approved source/result and authority separately for C41.

### C41: Admitted target mutation and exact-result recovery

**Estimate:** 3.5 h · **Depends on:** C32, C40, C06, C39 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C06, C39. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/store/gate.py; src/aitm_core/delivery/mutate.py; src/aitm_core/delivery/reconcile.py; src/aitm_core/cli/deliver.py; packages/aitm-core/tests/integration/test_c41.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `execute_delivery(intent: DeliveryIntent, admission) -> DeliveryResult; reconcile_delivery(intent) -> DeliveryResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_delivery_once: durable intent/admission precede expected-head CAS on non-checked-out target; checked-out target refuses. Crash after CAS recovers exact result through retained intent/history despite later target advance; invalidation/cancellation cannot authorize second mutation. Use C06 ref_gate with DELIVERY_TARGET around exact target-head CAS, inventory immediately before/after, and preserve target refs/index/unsynced bytes on detected out-of-band checkout. Fence further mutation/publication eligibility and require explicit reconciliation without reset; an already-landed result stays retained historical evidence. Real Git fixture injects external checkout across CAS as well as serializes supported operations; a pre-existing checked-out target alone is not sufficient proof. Any producer test here that crosses a story/defect Develop/Test/Review exit uses an explicitly composed typed StoryExitGuards fixture until C76/C79 deliver the real evaluators. An explicitly unregistered required edge must refuse as unavailable; no permissive production default. C49/C68 and C65/C66 later re-prove the relevant paths with actual C76/C79 registrations and specific guard causes.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c41.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Test authority is explicit disposable fixture authority; implementation never assumes a review pass permits real trunk delivery.

### C42: Atomic sign-off and retained evidence reconstruction

**Estimate:** 3.5 h · **Depends on:** C29, C38, C39 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C38. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/reviews/activation.py; src/aitm_core/outcomes.py; src/aitm_core/signoff.py; src/aitm_core/evidence.py; src/aitm_core/cli/evidence.py; packages/aitm-core/tests/integration/test_c42.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `build_close_outcome(snapshot, retro) -> Outcome; signoff(retro: RetroInput) -> OperationResult; reconcile_evidence(request) -> EvidenceResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_signoff_atomic: current review/delivery/applicable prior lifecycle proof and proposed retro close in one transaction, never require prior signoff; missing earlier conditions yield Done/unverified without satisfying delivered dependency. Reconstruct derived receipts only from retained authoritative proof; preserve already stopped clock. Missing actual proof returns typed rerun requirement for C61, not a fabricated pass. C42 owns construction of the complete typed Close outcome from C56 schema, current estimate/attempt/source/coverage/retro facts. Real signoff commits outcome, retrospective, session end, Done and related-story resolution with one operation ID/CAS; refusal or crash before CAS leaves none, retry after CAS returns the single whole close. No later callback appends the missing outcome. Wire evidence reconcile to C38 reconcile_review after retaining/reconstructing applicable proof and running current preflight. It may activate a single retained early verdict only in Review with current prerequisites, recording the genuine later clock stop without a second verdict. A missing real test reports the managed rerun route and never activates prematurely. Any producer test here that crosses a story/defect Develop/Test/Review exit uses an explicitly composed typed StoryExitGuards fixture until C76/C79 deliver the real evaluators. An explicitly unregistered required edge must refuse as unavailable; no permissive production default. C49/C68 and C65/C66 later re-prove the relevant paths with actual C76/C79 registrations and specific guard causes.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c42.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** C42 owns signoff/reconstruction, C61 owns evidence-only reopening and managed rerun. No hidden human gate or extension of the implementation clock through retrospective time.

### C43: Durable resident-action queue and replay

**Estimate:** 3 h · **Depends on:** C09, C13, C17, C28, C35, C31, C74 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C35, C31, C74. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/actions.py; src/aitm_core/cli/actions.py; src/aitm_core/services.py; src/aitm_core/store/sync.py; src/aitm_core/cli/sync.py; packages/aitm-core/tests/integration/test_c43.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `run_pending(snapshot, registry) -> ActionBatchResult; retry_action(key: ActionKey) -> ActionResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_action_recovery: crash before first call leaves pending record; missing/disabled version stays unavailable. Shared action runs only after publication and uses latest state; stale retry/lost ACK and provider monotonic-or-fenced contract tested with doubles. Local no-op projection records completion. Install the PendingActionRunner port. Real aitm sync discovers/retries a durable action after crash before first call, and actions retry uses the identical owner/version/key route; no helper-only qualification. In test_c43.py prove production sync/actions resolve PendingActionRunner; C17 deliberately-unregistered-slot negative vectors remain unchanged.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c43.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** M2 owns actual hosted endpoint proof; core must not claim fake-provider tests demonstrate GitHub safety.

### C44: Estimate lineage, usage and learning outcomes

**Estimate:** 2.5 h · **Depends on:** C23, C27, C42 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C42. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/outcomes.py; src/aitm_core/usage.py; packages/aitm-core/tests/unit/test_c44.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `ingest_usage(source, payload) -> OperationResult; triad(story) -> TriadStatus; report_outcomes(snapshot) -> OutcomeReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_triads: original Refine/Plan/JIT retained separately, Close binds delivered/attempted source and qualified actuals/lessons. Duplicate usage with same identity dedups, contradictory payload conflicts; unavailable time/cost and imported/incomplete triads stay excluded from complete calibration. Consume C42 atomic Close outcome through public reporting; C44 adds usage ingestion/triad queries and never becomes a delayed signoff writer. Shared outcomes.py query additions follow C42 source delivery. Expose reporting through the typed query API; no new outcomes CLI route is introduced in M1.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c44.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No rubric/ML implementation; distinguish engaged hours, planning spans, tool duration, wall time and provider units.

### C45: Spike deliverable binding and validation walk

**Estimate:** 3 h · **Depends on:** C29, C33, C35, C38, C39, C42, C16 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C16. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/deliverables.py; src/aitm_core/cli/deliverables.py; src/aitm_core/cli/bind.py; packages/aitm-core/tests/integration/test_c45.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `register_deliverable(binding, path) -> DeliverableRef; validate_deliverable(ref, checks) -> ValidationReceipt`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_spike_cli_walk: real bind --deliverable, research/input JIT, deliverable add/validate, effective independent review, exact archival delivery and signoff operate without story implementation commits. Executable checks use C34 preparation and C32 admission through C35 selected lane. Changed bytes invalidate proof and stale binding cannot certify replacement.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c45.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** C16 owns generic binding purpose/capability validation; C45 wires deliverable registration/adapter and tests it. No arbitrary deliverable pass flag.

### C77: Legacy kind normalization and unresolved inventory

**Estimate:** 2.5 h · **Depends on:** C03, C54 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/models/migration_kind.py; src/aitm_core/migration/kinds.py; packages/aitm-core/tests/unit/test_c77.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `map_legacy_kind(header, existing_facts, source_provenance) -> KindMapping`. Domain records live with this producer and reuse the existing typed evidence/guard contracts.

- [ ] **Test first:** test_legacy_kind_mapping maps explicit legacy kind to the normalized initial graduation/kind fact, retaining header path and raw digest. Table vectors cover story/defect/spike/epic; #1/#2 sample headers remain epic. Missing, unknown or contradictory header/fact kinds produce unresolved required inventory, never a story default. No historical split is synthesized. This pure helper owns only kind resolution; C46 supplies pinned actual header bytes/provenance and integrates its unresolved entries, C48 blocks apply, and C51 proves actual whole-corpus folds. The model/result is reused by C46 rather than redefining MigrationInventory.
- [ ] **Implement:** the named bounded contract and production adapter within these paths; no hidden later wiring.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/unit/test_c77.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Pure in-memory vectors only; no Git/process/network in this unit lane. Retain the distinction between authoritative historical facts and header-derived backfill.

### C46: Legacy inventory and deterministic v0 adapters

**Estimate:** 4 h · **Depends on:** C03, C06, C25, C58, C72, C77 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** src/aitm_core/migration/v0.py; src/aitm_core/migration/inventory.py; tests/fixtures/v0/; src/aitm_core/models/migration.py; src/aitm_core/cli/migrate.py; packages/aitm-core/tests/integration/test_c46.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `inventory_v0(tip: str) -> MigrationInventory; map_v0(inventory) -> MappedRecords; MigrationReceiptV1(input_tip, declaration_hash, adapter, deviations, input_hashes, payload_tree_hash); CutoverBuilder.preview(inventory, declaration, build_context) -> CutoverTree`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_actual_v0: copy pinned actual #1/#2 including all review/backfill/refinement and later leaf-bootstrap records; map same-time state-entered, reciprocal links, null-story draft facts and actor spelling deterministically. Legacy headers fill only absent facts with source/conflict checks; never parse generated details. Early migrate v0 --dry-run emits complete input inventory, planned transformations/deviations and explicitly unbound output values before an exact declaration exists, with no ref, journal, identity or allocation mutation. It declares a pure CutoverBuilder.preview(inventory, declaration, build_context) port; until C48 provides it, predicted output hashes stay unavailable rather than invented. Receipt payload hash excludes the receipt path itself; schema includes exact declaration/prefix and source inventory identities. Inventory every observed event/envelope/data/header shape across the pinned current corpus, not only #1/#2. Pair dependency-added(blocked_by) and dependent-added(blocking) with reciprocal/cycle checks; map bootstrap plan-entry source/alias and parent-plan-decomposition→decomposition proposal, plan-origin/priority and non-runtime provenance without inventing CLI execution or a v1 descriptor. Absolute last-worktree becomes an opaque legacy display ID with unresolved host association; raw source remains retained, never used to select a checkout. Missing required mappings or ambiguous issuance aliases block the affected safe operation; optional unknown data stays opaque. Delegate explicit legacy kind normalization to C77, retaining header path/hash in mapped initial graduation/kind facts and surfacing
  missing/unknown/contradictory values as required unresolved inventory. test_actual_v0_kind checks actual #1/#2 remain epic and no split is synthesized. This is bounded adapter integration over C77's delivered pure mapping, not additional kind-parser implementation inside the already 4 h C46 leaf.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c46.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Freeze source path/hash/license and explicit deviations. Optional opaque/incomplete records survive; required contradictions block safe apply.

### C47: Stable legacy adoption preparation

**Estimate:** 3 h · **Depends on:** C07, C11, C46 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C46. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/migration/prepare.py; src/aitm_core/cli/migrate.py; packages/aitm-core/tests/integration/test_c47.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `prepare_adoption(inventory, expected_tip) -> AdoptionProposal`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_adoption_identity: versioned legacy-root/ref identity yields same adoption ID/UUID across reruns/clones and tip advance; proposal binds exact approved tip/deviations/adapter/provider numbering. Commit-selected declaration overrides local proposals, no precommit legacy writes or allocation.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c47.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Changing expected tip needs renewed declaration, not a fresh store identity; existing GitHub issuance stays unavailable until provider exists.

### C48: Atomic migration apply and accepted-snapshot binding

**Estimate:** 3.5 h · **Depends on:** C09, C17, C26, C47, C10 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C10, C47. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/migration/apply.py; src/aitm_core/migration/bindings.py; src/aitm_core/store/validation.py; src/aitm_core/cli/migrate.py; packages/aitm-core/tests/integration/test_c48.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `apply_adoption(declaration, expected_tip) -> MigrationResult; build_cutover(inventory, declaration, build_context) -> CutoverTree`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cutover_cas: build/validate whole tree off-ref; checkout exclusion and exact declaration recheck; crash before/after CAS and competing clone return one result. Preserve snapshots before metadata rewrite, map canonical bindings per level without upgrading old digests. Move root README prose/provenance under .aitm, remove active root exception. Construct MigrationReceiptV1 over deterministic output payload excluding its own path, then validate whole tree. Wire bounded-legacy/cutover verification into the normal fresh-history validator; reject forged extension of approved legacy prefix, altered declaration/receipt/payload and extra deviations. Own one pure build_cutover(inventory, declaration, build_context) -> CutoverTree used by both bound dry-run preview and apply, and wire the C46 preview port. Build context pins schema-defined deterministic serialization/provenance inputs; actual apply/publication observations live in the separate receipt, not unpredictable payload fields. Preserve source occurrence precision. With identical pinned inputs/declaration/context, preview and apply must agree on mapped facts, raw accepted snapshots, regenerated views and receipt-excluded payload tree hash. Apply may not implement a second transformation path. An unresolved required kind inventory entry blocks bound preview/apply before CAS; accepted declarations cannot bypass that blocker or silently supply a default kind.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c48.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No renumbering, precision fabrication, lost ignored/untracked work, reset or direct writes after committed migration.

### C51: Real review/migration and second-clone qualification

**Estimate:** 3.5 h · **Depends on:** C48, C18 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_v0_cutover.py; tests/integration/test_review_import.py; docs/learn/core-migration.md.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `qualify_cutover(legacy_fixture, declared_policy) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cutover_fresh_clone: actual portable/native #1/#2 plus created leaf fixtures reconstruct every version; live/backfill duplicates normalize once; legacy namespace retained. Clone before/after cutover resumes same identity; compare all input/output hashes and unknown coverage; exact-content missing levels remain unaccepted. Snapshot all refs/journal/allocation files before/after dry-run and prove no mutation. Fresh validator rejects modified declaration/receipt or an undeclared extra legacy commit; exact output payload hash excludes receipt path. Rebuild index from adopted files and compare all query results to tree authority. After binding the exact declaration, run read-only preview and actual fixture apply using the same construction inputs and compare every predicted output/hash, mapped event and accepted snapshot to the actual payload (receipt excluded). Before declaration, verify unavailable output hashes are explicitly marked; neither mode allocates/ref-mutates during dry-run. test_full_corpus_inventory pins the complete current tree and representative decomposed leaves in addition to #1/#2. Every observed required shape has a collected mapping vector, including both dependency directions, historical decomposition estimate, manual provenance, legacy worktree paths and no duplicate plan-entry issuance alias. Compare full source inventory before/after migration; unsupported required shapes cannot disappear. test_migrated_kinds folds actual migrated #1/#2 as epics with header provenance, keeps all known leaf kinds and their old sources, and proves aggregate estimates do not trigger the leaf four-hour rule. Missing/unknown/contradictory kinds
  refuse cutover without mutation and no historical split event is invented. Reuse C77/C46 fixtures and C48 constructor.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_v0_cutover.py packages/aitm-core/tests/integration/test_review_import.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Fixture policy only. Historical blocked/unsubmitted attempts remain evidence, never upgraded to accepted during import.

### C61: Scoped evidence-only recovery and real rerun

**Estimate:** 3 h · **Depends on:** C16, C27, C32, C35, C38, C42, C45 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C42, C45. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/recovery.py; src/aitm_core/cli/evidence.py; src/aitm_core/cli/bind.py; packages/aitm-core/tests/integration/test_c61.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `reopen_evidence(story, source) -> RecoveryAuthority; recover_missing_proof(authority) -> RecoveryResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_evidence_only_rerun: real reopen --for evidence from unchanged Done/unverified retains old disposition/waivers/signoff, used budget and allowance. bind --evidence grants new generation via C16, then real admission/test yields later eligible interval and activation before new signoff. Old, tripped, pivoted or superseded generation refuses. Evidence-only binding cannot edit source, expand or mutate target; reconstruction of existing valid receipt leaves stopped clock unchanged. Shared mode obeys published admission/stop order. Any producer test here that crosses a story/defect Develop/Test/Review exit uses an explicitly composed typed StoryExitGuards fixture until C76/C79 deliver the real evaluators. An explicitly unregistered required edge must refuse as unavailable; no permissive production default. C49/C68 and C65/C66 later re-prove the relevant paths with actual C76/C79 registrations and specific guard causes.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c61.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No source change is hidden inside evidence recovery. Normal same-attempt rework fences recovery generation; true replan creates fresh attempt only under accepted policy.

### C64: Deterministic two-clone qualification fixtures

**Estimate:** 2.5 h · **Depends on:** C09, C10, C21, C43 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/support/shared_store.py; tests/integration/test_shared_fixture.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `SharedStoreFixture(clones, remote, barriers, faults); run_schedule(seed, steps) -> ScheduleTrace`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_shared_fixture: disposable two-clone/remote construction, explicit barriers, seeded schedule replay and operation/command capture; prove a blocked worker is released deterministically and cleanup preserves failure evidence. Fault hooks delegate existing producer injection seams for publication ACK, allocation, stale action and repair; test each hook once. This leaf builds infrastructure only, not the full product race matrix. Import support through C01 tests.support.shared_store and its delivered importlib/test-package configuration; no unlisted path hack or pytest config edit is needed.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_shared_fixture.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No live service, generic scheduler or new product recovery behavior. Consumers reuse this delivered harness and producer fixtures.

### C70: Post-preflight consumer integration qualification

**Estimate:** 3 h · **Depends on:** C31, C64, C27, C28, C30 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_preflight_consumers.py.

**Consumes:** actual production AttemptPreflight from C31, delivered consumer behavior and C64 deterministic two-clone fixtures. **Produces:** `qualify_preflight_consumers(fixture: SharedStoreFixture) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_reconcile_with_real_preflight covers C27 positive/refusal behavior; test_provisional_attempt_with_real_preflight covers C28 advisory provisional entry and later acceptance/bind/reconcile retaining attempt/clock/allowance. test_expand_with_real_preflight parametrizes C30 local/shared construction failure, competing-clone candidate retry and lost ACK against actual installed preflight; all final related facts name the winning child and the origin never has an unblocked gap. Reuse C64 barriers and delivered producer input vectors, not a new harness. Include required trip/second-expansion refusal and assert no fixture preflight is installed. These are post-installation consumer proofs in this one owned suite; predecessor suites remain unchanged.
- [ ] **Implement:** compose the named integration proofs over delivered behavior; missing product semantics return to their owning leaf/replan.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_preflight_consumers.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Three bounded consumer groups reuse C64 and existing producers. No new trip algorithm, allocator, framework or private fixture fork. Gate B stays pending until this post-installation matrix passes; C31/C32 alone establish only the control baseline.

### C50: Shared-store conflicts and publication recovery qualification

**Estimate:** 3 h · **Depends on:** C64, C17, C30 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_shared_store.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_shared_matrix(disposable_remotes) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_eight_by_fifty: eight disjoint stories ×50 real CLI syncs retain all work using C64 barriers. test_conflicting_inputs covers same-story/related-policy/authored conflicts with both versions retained. test_publication_recovery covers the existing ACK-loss, allocator, stale-action and maximal-valid-prefix repair hooks through two clones; deterministic fault fixtures are reused, not rebuilt. No execution/delivery races are owned here.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_shared_store.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Bounded shared-store matrix over delivered behavior; missing production semantics return to their owning leaf/replan.

### C62: Epic aggregation and scope-resolution checkpoint

**Estimate:** 3 h · **Depends on:** C22, C29, C38, C42, C43 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C29, C43. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/aggregation.py; src/aitm_core/machine/kinds.py; packages/aitm-core/tests/integration/test_c62.py; src/aitm_core/services.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `aggregate_children(snapshot, epic) -> AggregateEvidence`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_epic_aggregate: real epic transitions start with accepted plan/child set despite mixed child states; later Test/Review rechecks required verification and delivered or explicitly scope-resolved children. Changed child scope invalidates assessment; abandoned/replaced dependency needs explicit dependent resolution. No epic clock/JIT/PR/test subprocess. Register aggregate_children in C29's AggregateEvidence port from services.py. The real promote cases use this production registration, not a test-only monkeypatch, and an explicitly missing slot stays unknown/unavailable. C29 owns the kind/edge dispatch; this leaf supplies its aggregate implementation without duplicating transitions.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c62.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Use one pinned related-story snapshot and CAS read-set; scope resolution is retained evidence, not blanket acceptance of abandoned work.

### C63: Installed extension discovery and command/init composition

**Estimate:** 3 h · **Depends on:** C12, C13, C14, C43, C01, C62 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C62, C01, C12. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/ext/discovery.py; src/aitm_core/services.py; src/aitm_core/cli/app.py; src/aitm_core/setup/init.py; tests/fixtures/extension-package/; packages/aitm-core/tests/integration/test_c63.py.

**Consumes:** C13 registration/factory/init-step contracts, C12 setup composition and C14 constrained ingress. **Produces:** `discover_installed(policy: PolicySnapshot) -> Registry; mount_extension_command(registry, route) -> CommandHandler; run_provider_init(registry, context) -> InitStepResults`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_installed_extension: build/install a disposable package exposing aitm.extensions with a command, guard/action, typed owner/provider and safe fake init step. Ordinary installed aitm and init discover it through importlib.metadata, select only committed enabled versions/order, mount the route and invoke its init contribution. Disabled policy never invokes it; missing required provider/owner is reported unavailable, not applied. Registry/ownership errors remain enforced through real ingress. Warm reads keep unused factories lazy.
- [ ] **Implement:** wire pinned registry into services, CLI dispatch and init contributions at the named call sites; no hosted endpoint or foreign package config changes.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c63.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** this leaf proves generic installed integration with a fixture package, not GitHub or harness functionality. Existing hooks/config remain preserved and plugin code is trusted in-process, not sandboxed. Budget reuses C13/C14 logic and C12 init ports; no second registry implementation.

### C76: Source commit guard and retained source evidence

**Estimate:** 3 h · **Depends on:** C28, C29, C31, C35, C38, C39, C40, C41, C42, C62, C63 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C29, C31, C63. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/source_guards.py; src/aitm_core/machine/guards.py; src/aitm_core/machine/transitions.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c76.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `evaluate_source_exit(snapshot, attempt) -> GuardResults; capture_source_commits(attempt, source) -> SourceCommitEvidence`. Domain records live with this producer and reuse the existing typed evidence/guard contracts.

- [ ] **Test first:** test_source_commit_guard exercises real story/defect Develop-exit promote with the production source-edge evaluator registered in StoryExitGuards: exact subject prefix [#<positive decimal story ID>] including its trailing space, no substring matching; reject [#12] for story 1, embedded prefixes, missing trailing space, nondecimal/zero/negative IDs, commits outside the recorded attempt branch or before its pinned baseline, and empty/tagged merge-only changes with no implementation delta. Preflight/evaluation retains matching source commit IDs and reviewed head/tree in typed evidence/read-set; recheck on CAS/source changes. C31 trip preflight remains first. Reuse C39/C40/C41 source-mapping fixtures to prove squash/rebase target messages without the prefix preserve valid source evidence; target-message text alone is insufficient. Register only the Develop-exit evaluator here through services.py and C28's edge-dispatched port. Until C79 supplies Test/Review exit evaluators those required edges remain unknown/unavailable, not passing. Prove this with explicit unregistered-edge fixtures. Existing C29/C62 spike/epic substitutions stay intact.
- [ ] **Implement:** the named bounded contract and production adapter within these paths; no hidden later wiring.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c76.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Bounded source-commit selection, retained evidence and one edge registration over delivered Git/delivery interfaces. C79 separately owns completion composites and signoff wiring. Re-estimate/split before Develop if the 3 h bound is not defensible.

### C79: Test and Review exit composites with atomic signoff

**Estimate:** 3 h · **Depends on:** C76, C35, C38, C39, C42, C62 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C76, C42. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/machine/completion_guards.py; src/aitm_core/machine/guards.py; src/aitm_core/machine/transitions.py; src/aitm_core/services.py; src/aitm_core/signoff.py; packages/aitm-core/tests/integration/test_c79.py.

**Consumes:** delivered source/evidence/guard contracts and the C76 Develop-exit evaluator. **Produces:** `evaluate_completion_exit(snapshot, attempt, edge, proposed_close=None) -> GuardResults`. Register the Test/Review edge evaluators in the existing StoryExitGuards port; do not create an alternate guard engine.

- [ ] **Test first:** test_test_exit_binding uses actual promote and the production evaluator to require a tool-produced passing receipt for the current clean source and attempt/generation; stale/dirty/wrong-attempt receipts refuse with the specific reason. test_review_exit_composite compares effective review, verified source-to-target delivery, retrospective and every applicable lifecycle proof on the same source/attempt, rejecting mixed evidence and target-message substitution. Wire signoff.py to the same registered evaluator using C42's proposed atomic retrospective/outcome plus existing authoritative facts; no prior-signoff requirement or second commit is introduced. Exercise one real signoff success and one mismatch refusal, proving all-or-none outcome publication. Reuse delivered source/review/delivery fixtures and retain C76 source evidence. Explicitly unregister each required edge to prove unavailable rather than pass; default production composition resolves all story exit evaluators. Kind-specific spike/epic paths remain C29/C62 responsibilities. Later C49/C65/C66/C68 prove complete real lifecycles.
- [ ] **Implement:** the bounded composite evaluation and explicit production call-site registration within these paths.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c79.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Reuse C42's transactional signoff constructor and producer fixtures. This is evidence comparison and wiring, not a new runner, delivery engine or retrospective schema. Re-estimate/split at JIT if three hours is not defensible.

### C65: Execution fences and clock-rebuild qualification

**Estimate:** 3.5 h · **Depends on:** C64, C30, C31, C32, C35, C38, C42, C61, C76, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_execution_races.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_execution_races(fixture: SharedStoreFixture) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** Using C64 and delivered producer cases, collect test_expansion_completion_fence (pending expansion versus actual test/promote/signoff), test_shared_stop_no_test_launch (published enforce stop versus offline test, no subprocess marker), test_trip_before_sync_and_pass (qualifying overrun before sync, CAS retry and completion), and test_reservation_and_review_rebuild (lost identity response resolved without child plus early verdict/later evidence-reconcile activation, discard private caches and rebuild pause/resume/stop from events). Retain workspace/results; no authored import, second launch or effective pass overtakes a stop. Four focused scenarios reuse contract-conforming activity and race hooks; no harness implementation here. Resolve the actual production StoryExitGuards edge evaluators from C76/C79; no fixture evaluator is installed. Before injected failures, establish the applicable positive source/receipt/review/delivery prerequisites through the real pipeline. Assert the specific intended refusal cause (expansion-pending, trip, admission-fenced or stale-generation as appropriate), and reject evaluator-unavailable as a satisfying outcome. This prevents missing composition from making negative assertions pass vacuously.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_execution_races.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** No fabricated engagement, source-review authority or real provider capability; fixture evidence is explicit.

### C66: Managed-delivery race and recovery qualification

**Estimate:** 3 h · **Depends on:** C64, C41, C42, C76, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_delivery_races.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_delivery_races(fixture: SharedStoreFixture) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** Collect test_local_delivery_admission: local-only admitted core-run delivery succeeds with publication N/A; checked-out/invalidated targets refuse. test_delivery_crash_reconcile: crash before/after target CAS and lost result re-observe one target outcome without a repeated mutation. test_delivery_checkout_race: an external checkout between the common pre/post gate checks is detected and fenced with target/ref/index/workspace evidence retained. Reuse C41/C64 injection seams. Resolve the actual production StoryExitGuards edge evaluators from C76/C79; no fixture evaluator is installed. Before injected failures, establish the applicable positive source/receipt/review/delivery prerequisites through the real pipeline. Assert the specific intended refusal cause (expansion-pending, trip, admission-fenced or stale-generation as appropriate), and reject evaluator-unavailable as a satisfying outcome. This prevents missing composition from making negative assertions pass vacuously.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_delivery_races.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Only disposable target refs; no production delivery authority or checkout race prevention beyond the accepted cooperative-gate guarantee.

### C78: Installed transition explanation and unknown guards

**Estimate:** 3 h · **Depends on:** C18, C28, C29, C62, C76, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C18. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/cli/read.py; packages/aitm-core/tests/integration/test_c78.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `explain_command(story, refresh=False) -> TransitionExplanation`. Domain records live with this producer and reuse the existing typed evidence/guard contracts.

- [ ] **Test first:** test_installed_explain invokes the installed command with C28's real pinned transition evaluator and current production kind/exit registrations. Assert pinned state/policy, next kind-appropriate edge, every guard's pass/fail/unknown reason, pending side effects and exact next command for story/spike/epic fixtures. Freshness-dependent conditions that cannot be proved remain unknown, never pass. Ordinary explain performs no fetch/write/model call; explicit --refresh uses C08 then repins. Assert absent required evaluator reports unavailable/unknown. Keep lazy loading of only selected guard/extension modules; C52 measures this complete path including interpreter, not C18's earlier partial view.
- [ ] **Implement:** the named bounded contract and production adapter within these paths; no hidden later wiring.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c78.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Thin read-only adapter over the same guard engine; no parallel implementation of transition logic or hidden refresh.

### C49: Core-only nominal lifecycle qualification

**Estimate:** 3 h · **Depends on:** C12, C18, C19, C22, C26, C27, C31, C35, C38, C39, C42, C43, C44, C45, C61, C62, C21, C10, C41, C48, C63, C76, C78, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_core_walk.py; tests/fixtures/reviews/; docs/learn/core-cli-walk.md.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_core_walk(fixture_policy, local_repository) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_complete_cli_walk: installed init/config commit/rerun, idea/draft/local graduation, genuine imported design/plan review fixtures, estimates/JIT, tagged source change, test, independent source review, observed authorized fixture merge and retro yield delivered Done. Negative missing/stale proof retains failures. No SDK/GitHub; every action is real installed CLI, not direct helper substitution. The nominal init --local walk asserts publication not-applicable. A separate test_default_publication_pending uses a remote-configured disposable store and verifies promote without --push attempts default publication and reports retryable pending after simulated ACK loss. Deliver the matching nominal-walk tutorial; exceptional lifecycle and broad route audits have separate owners C68 and C67.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_core_walk.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

C48 remains a conservative integration predecessor because it installs the final normal-history validator, which this nominal lifecycle uses. This edge requires the composed validator baseline, not production migration or cutover.

**Risk/boundary:** Qualification only; no late feature implementation. Reuse reviewed producer fixtures and preserve honest fixture-policy assurance.

### C75: Plan-entry graduation and provenance reconciliation

**Estimate:** 3.5 h · **Depends on:** C72, C21, C22, C28, C31, C64, C63, C76, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C22, C79. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** src/aitm_core/decompose.py; src/aitm_core/graduation.py; src/aitm_core/cli/decompose.py; src/aitm_core/services.py; packages/aitm-core/tests/integration/test_c75.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `decompose(epic, entry, expected_plan) -> GraduationResult; reconcile_decomposition(child, expected_source, proposed_source) -> OperationResult`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_decompose_once uses C64's shared-store harness and actual installed decompose --entry --expected-plan. C72 freezes typed source and C20/C21/C22 reserve/issue/finalize one Backlog child per parent/key with explicit kind, reciprocal parent and decomposition estimate, no draft creation. Two clones/lost ACK/retry after plan revision cannot issue a second child; changed source is retained pending reconciliation. Resolve descriptor dependency keys to permanent IDs via cycle-checked links; unresolved required entries remain visible blockers. test_decomposition_reconcile retains old/new scope and identities, applies explicit scoped reconciliation and invalidates affected description/design/plan applicability; it cannot invent renewed acceptance or auto-overwrite authored files. Own leaf design and explicit Refine estimate are still required. Prove ordinary graduation uses the same generic source predicate and that a missing plan-source adapter returns unavailable before dispatch. Register the C72 applicability service and production source route at the listed sites.
- [ ] **Implement:** the named contract and owned adapter within these paths; keep source preparation, authority, publication and effective evidence distinct.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_c75.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** 3.5 h integrates already tested descriptor, allocator, relations and publication contracts using C64 fixtures; no new allocator or inherited review mechanism. It lands after C63 to serialize services/graduation wiring, before CLI/release qualification.

### C67: Complete installed CLI surface audit

**Estimate:** 2.5 h · **Depends on:** C49, C51, C63, C44, C71, C74, C75, C76, C78, C79 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_cli_surface.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `audit_cli_surface(required_routes) -> RouteCoverageReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_cli_surface parametrizes every route and option in the complete CLI map: installed lazy registration, help, argument validation and versioned JSON/unavailable statuses. Assert init --planning-branch and all documented global/route options are exposed; no new unmapped command is shipped. Collect a route-to-positive-operational-test ledger from C49/C50/C51/C65/C66/C68/C59 instead of claiming help alone proves behavior. Future suite names are declared references; Gate C/D validates their actual collection once all owners are delivered. The positive operational ledger additionally includes C71 split, C74 entity editing and C75 decompose/provenance reconciliation; help/argument coverage alone is insufficient. The positive ledger also collects C17::test_sync_reconcile_cli/test_sync_push_cli, C29::test_kind_registration, C30::test_expansion_finalizer_registration, C62::test_epic_aggregate, C76's source and C79's Test/Review exit vectors and C78::test_installed_explain. An unavailable or parse-only route cannot satisfy this ledger.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_cli_surface.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** A missing command/wiring returns to its owning leaf; this audit cannot implement absent product behavior.

### C68: Lifecycle reconciliation and limited-rerun qualification

**Estimate:** 3 h · **Depends on:** C49, C61 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/integration/test_lifecycle_recovery.py.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `run_lifecycle_recovery(fixture_policy) -> QualificationReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_authored_sync_and_late_activation: installed promote on edited bound accepted plan saves a distinct sync operation, repins and refuses stale acceptance; concurrent authored-base conflict retains both versions and no transition. An early pass remains ineffective until evidence reconcile activates once at the later observed time. test_provisional_attempt: advisory absent-plan/unbound Develop followed by accepted plan/bind/attempt reconcile retains attempt identity, clock and allowance. test_evidence_only_rerun: unchanged unverified Done gains a new limited evidence generation, old one remains fenced, real test/activation yields genuine later interval before signoff. Reuse producer and C49 fixture data; no duplicate harness.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/integration/test_lifecycle_recovery.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Scope is exactly three integration scenarios over delivered C27/C28/C38/C42/C61 behavior; unavailable prerequisites remain blockers.

### C52: Entrypoint performance and unit-isolation budgets

**Estimate:** 3 h · **Depends on:** C18, C49, C50, C51, C65, C66, C67, C68, C70 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/performance/test_budgets.py; docs/learn/core-performance.md.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `measure_entrypoint(fixture: BenchmarkFixture) -> BudgetReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_budgets: declared warm-cache laptop show/list/explain <150ms including interpreter; local transition <1s; measure the entire MemoryBackend unit suite <10s by launching its pytest command from this non-unit performance lane; C01 tests/unit/conftest.py traps child-suite subprocess/network access from the first unit test. Record corpus/hardware/OS/repeats and cold rebuild/remote/actions/push/total wall separately. Keep Git patch replay C24 in integration lane. The parent performance test records complete child-suite wall time including collection/startup, exit status and collection count; it lives outside tests/unit and its own process launch is permitted. CI also runs the unit directory directly under the same C01 guards. C52 never adds a subprocess test inside the unit suite. The warm explain budget covers C78's full guard-explaining installed path, including lazy guard/extension loading and interpreter startup; no freshness-only shortcut or suppressed unknown/pending information is allowed.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/performance/test_budgets.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf measures and performs only bounded lazy-import corrections. Any substantive failed budget becomes explicitly bounded replan, never subtraction of startup or hidden optimization scope.

### C59: Cross-platform wheel and CI qualification

**Estimate:** 3 h · **Depends on:** C36, C37, C49, C50, C51, C52, C63, C65, C66, C67, C68, C70, C75 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/packaging/harness-pytest.ini; tests/packaging/suite_manifest.json; tests/packaging/installed_runner.py; tests/packaging/test_wheel.py; .github/workflows/core-ci.yml.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `qualify_wheel(candidate_hash, platform) -> PackageReport; run_installed_suites(artifact, suite_manifest, platform) -> PackageReport`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_installed_matrix: build candidate wheel, verify hash, install in clean macOS/Linux environments and run actual CLI smoke, selected contained readiness/execution or explicit capability denial plus captured-export lane. CI collects all exact C49–C52 suites and platform tests and archives reports. User runtime needs no Node. Provide run_installed_suites(artifact, suite_manifest, platform): copy the reviewed test/fixture harness outside the source workspace, install only the target wheel and test dependencies in a fresh venv, clear PYTHONPATH/editable paths, and assert aitm executable plus aitm_core.__file__/distribution RECORD resolve to the installed artifact. This reusable runner executes the actual C5 suite manifest for candidate now and released wheel in C60; source checkout imports invalidate results. The isolated runner copies tests/support and conftest files with suites. All suites use its already installed target and invoke the same prepared consumer; wheel smoke checks the supplied artifact and does not build or install a different candidate. Candidate build is a separate outer preparation step. Shared C5 suite_manifest.json is owned here and lists core walk, CLI surface, lifecycle recovery, shared-store/execution/delivery races, C10 repair, v0 cutover/review import, C63 extension, performance/full guarded unit suite, wheel smoke and each OS platform suite. Candidate and released consumers use the identical manifest. Copy the entire required tests package skeleton, including root tests/conftest.py, every package marker, tests/support and packaging helpers, into the isolated harness and preserve C01 importlib mode with an explicitly
  supplied harness configuration. The copied conftest adds only that copied test-package parent; assert tests and helper modules resolve there and aitm_core resolves exclusively to the target installed wheel. No source src/ path or original checkout is on the import path. Own/copy minimal tests/packaging/harness-pytest.ini with reviewed marker definitions (including post_release) and required collection settings; run pytest with -c <copied-harness-pytest.ini> --rootdir <harness-root> --confcutdir <harness-root> --import-mode=importlib and explicit suite paths from the manifest. The harness root is the parent of the copied tests/ directory; configuration storage below tests/packaging never defines the discovery boundary. Candidate collection excludes the named live post-release suite; only C69/C60 explicitly selects it with --release-manifest. test_wheel.py asserts effective rootdir/confcutdir/import mode/config/markers and collected suite names, not merely intended arguments. Inside the isolated harness, assert the loaded plugin paths include the copied tests/conftest.py and tests/unit/conftest.py. Using the same interpreter/config/flags as the real suite, create disposable unit probes that attempt subprocess and socket access: the outer packaging test requires the expected guard failure and absence of a subprocess side-effect marker. An integration probe imports tests.support from the exact copied path. These probes verify active protection and root loading before any guarded-suite claim; probe failure is expected evidence handled by the outer test, never a skipped full-suite requirement. No original source checkout is consulted. Include test_preflight_consumers.py in
  the shared C5 manifest.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_wheel.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Candidate wheel proof is not released-package proof. CI platform/capability failures remain visible; no host-security-setting change to make probes pass.

### C53: Release workflow, tutorials and candidate handoff

**Estimate:** 3.5 h · **Depends on:** C59, C03 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C03. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** uv.lock; docs/learn/core-overview.md; docs/release/core-m1.md; packages/aitm-core/pyproject.toml; .github/workflows/core-release.yml; tests/packaging/test_release_workflow.py.

**Consumes:** delivered contracts from the listed dependencies (or no core prerequisite for C01). **Produces:** `release checklist consumes delivered source and candidate reports; workflow builds/verifies immutable artifact identity`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_release_candidate: validate workflow/config against a candidate wheel in disposable CI, assert source/version/hash mapping and refusal of mismatched artifact. Source-review and deliver release workflow, package metadata, tutorial and library-choice rationale through normal PR before any publication using them. Hand off exact delivered source and candidate proof to C69/C60. The release workflow supports a retained once-per-release operation identity and queryable source/version/hash mapping; an uncertain dispatch is reconciled before retry.
- [ ] **Implement:** the named contract and its owned adapter within the stated paths; preserve every global constraint and failure distinction.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_release_workflow.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** This leaf does not require its own released artifact before source review. It implements/tests candidate preparation; release publication and post-publication consumer proof belong to separately authorized C60.

### C69: Read-only release checker and dual-platform workflow

**Estimate:** 3 h · **Depends on:** C53 · **Parent:** #2 · **Priority/size:** P1/S.

**Touched files:** tests/packaging/release_checker.py; tests/packaging/conftest.py; tests/packaging/test_release_checker.py; tests/packaging/test_published_release.py; .github/workflows/core-post-release.yml; docs/release/core-checker.md.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `qualify_published(manifest: ReleaseManifest) -> ReleaseEvidence; pytest --release-manifest PATH option; read-only core-post-release workflow`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** test_release_checker_fixtures: success and mismatched version/hash/source, missing/uncertain artifact, omitted manifest and unsupported evidence; checker cannot publish/dispatch. conftest.py registers --release-manifest. Live test_published_release is excluded from ordinary fixture collection and must fail clearly if explicitly invoked without a manifest. The post-release workflow accepts a completed observed-release manifest and runs C59 isolated runner/full suite_manifest.json on macOS/Linux plus the declared warm-laptop budget lane; it has read-only artifact access and no publication capability. Fixture-test the workflow/option/checker and required-suite collection before source review. Missing required host/capability leaves released proof pending.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_release_checker.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

**Risk/boundary:** Checker/workflow source must be reviewed and delivered before C60 uses it. It is test infrastructure outside the target wheel; never a pre-release assertion that a release exists.

### C60: Publish and qualify the exact released core

**Estimate:** 2.5 h · **Depends on:** C53, C69 · **Parent:** #2 · **Priority/size:** P1/S.

**Mandatory shared-file predecessors:** C53. These are included in Depends on and must be carried into the leaf issue graph.

**Touched files:** docs/release/core-m1.md; docs/release/core-m1-evidence.json.

**Consumes:** delivered contracts from the listed dependencies. **Produces:** `release-operation receipt and exact released C5 evidence manifest`. Domain request/result records live with this producer and reference the shared typed contracts above.

- [ ] **Test first:** First re-run delivered C69 checker fixtures to prove the observer before any live release. Then, only with separate release-task authority, observe/dispatch/reconcile the delivered C53 once-per-release operation for (version, delivered source, expected artifact hash). Existing conflicting artifact blocks; lost result queries exact workflow/version/provenance before retry. After publication, obtain observed-release.json and run the delivered read-only C69 checker/workflow against that exact immutable wheel. C59 runner executes the full C5 manifest on both OSes and the declared warm-laptop lane, including local-only/two-clone/repair/migration/import/budgets and containment. No source import, candidate substitution or required skip can pass C5.
- [ ] **Implement:** the named qualification/checker contract within these paths; no missing product behavior is hidden here.
- [ ] **Verify and retain:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_release_checker.py -q` to PASS plus affected contract suites and Ruff; complete source review/delivery evidence under the common cycle.

- [ ] **Post-publication verification:** run `uv run --package aitm-core pytest packages/aitm-core/tests/packaging/test_published_release.py --release-manifest <observed-release.json> -q` through the delivered read-only workflow on the named hosts, retain the complete C5 manifest/results in core-m1-evidence.json. Fixture PASS is pre-operation observer evidence only; this leaf cannot be accepted as released qualification until the post-publication PASS and all required suite reports are retained. Publication/dispatch is outside pytest; retries of the checker cannot publish.

**Risk/boundary:** Evidence-only release follow-on; no new harness implementation. Target source is delivered C53, observer source is delivered C69, and neither depends on this evidence commit. No production C6 adoption or epic closure. External waits are not implementation engagement; missing credentials/capability remains a blocker, not permission repair.

## Independent work and integration order

After C01, C02 envelope work and C03 canonicalization are independent. C54/C55 domain reducers follow; C56 serializes their composition. After that foundation, contract-ready store C05–C12, registry/ownership C13–C14 and rendering/index C15/C18 can branch when their exact prerequisites permit. C22 supplies pure graduation construction before C21 atomically allocates/finalizes; the numbering and story update are never separate authority results. C24→C57→C58 splits reconstruction, topology and native mapping, then feeds live/import work C25/C26. C33 capture can proceed beside workflow after C07/C16. C36 and C37 are independent OS adapters after C35, with actual separate platform lanes.

C43 follows C17 and C28 to wire real sync/action retry, and can proceed beside delivery. C46/C47 migration preparation can proceed after its review/policy dependencies while later workflow work completes. C49/C50/C51/C65–C68 qualify separate matrices after their exact dependencies; C49 owns the nominal walk; C67 owns the complete CLI-surface audit and C68 owns lifecycle reconciliation/reruns; C64 supplies shared fixtures before C70 post-preflight consumer qualification, C50 conflicts, C65 execution/clock races and C66 delivery races, C51 includes the index, and positive operational proof is distributed by the scenario map rather than inferred from help output; C63 completes installed extension composition; C52 measures, C59 packages/CI and supplies the isolated artifact runner, C53 delivers release preparation, C69 delivers the read-only release checker/workflow, and C60 separately publishes/qualifies the released artifact. C61 handles evidence-only recovery after C42 signoff; C62 handles epic aggregation separately from C45 spike validation. The complete Depends on graph includes mandatory shared-file predecessors, not merely a serial fallback; those edges are copied to the leaf ledger and native issue dependencies.

Shared services, reducer exports and CLI modules have explicit serial owners. If interfaces change, update dependent JIT/branch coverage and rerun the contract suite before proceeding. A passed issue with an undelivered interface is not an eligible predecessor.

C74 follows the generic binding/sync and entity operations before graduation consumes its handoff. C72 follows document acceptance/estimate contracts; C71 follows the full transition baseline. C73 pure source-review validation can proceed beside OS adapters once its prerequisites land. C75 follows C64 fixtures and C63 composition (and appears after C49 in the topological list); it reuses those fixtures for real source-neutral identity and provenance reconciliation rather than duplicating concurrency infrastructure. C67 and release qualification wait for its actual route proof.

## Acceptance coverage and checkpoints

| Accepted core design requirement | Owning leaves / integrated proof |
| --- | --- |
| Package layout; init/authoritative policy/topology/hooks | C01, C06–C08, C11–C14; C49/C52 |
| One owner, typed causal events, deterministic views | C02/C54–C56, C03–C06, C14–C17; C50 |
| Operations/concurrency/publication/continuity/repair | C04–C10, C17; C50/C65/C66 (8×50 plus races) |
| Binding, snapshot index and full kind/guard explanation | C16–C18/C28/C78; C49/C50/C52 |
| Ideas/drafts/graduation/local numbering/relationships | C19–C22, C30; C49/C50 |
| State slots, common planning guards, kinds/split/dispositions/epics | C27–C31/C54/C71/C76/C79, C42/C45/C61/C62; C49/C71/C76/C79; migrated kinds C77/C46/C51 |
| Typed decomposition, own-document coverage and proposal estimates | C03/C07/C20–C22/C26/C27/C72; C75 |
| Entity editing, source finalization and discard | C16/C17/C19/C74/C22; C74 |
| Explicit source-review record, independence and assurance | C07/C57/C73/C38; C49/C73 |
| Pivot actor/fencing and reconfiguration continuity | C07/C11/C31; their collected integration vectors |
| Canonical acceptance, review topology/patches/live import/JIT | C03/C24–C27/C57/C58; C51 |
| Trip/attempt/admission and late boundary facts | C02/C55/C23/C27–C32/C38/C42/C61; C65/C70 |
| Engagement, planning/review time, usage/triads | C23/C25/C44; C49/C51 |
| Captured/contained lanes, preparation and actual receipts | C33–C37; C49/C52 on macOS and Linux |
| Source review, delivery transformation/sign-off/recovery | C38–C42/C45/C61; C49/C66/C68 |
| Actions, disabled extensions and unavailable capabilities | C13/C14/C43/C63; C49/C50/C59 |
| Real v0 migration, kind backfill and accepted snapshots | C77/C46–C48; C51 |
| Complete CLI walk, performance and released-package behavior | C49–C53/C59/C60/C64–C70 |

Gate A (after C14 and needed contract leaves): freeze versioned operation/provider/canonicalization contracts and pin fixtures; no production readiness claim. Gate B: C31/C32 plus prerequisites establish the control baseline; full Gate B remains pending until C70 qualifies the post-installation consumer paths using C64 fixtures. This is not released-package or production-adoption readiness. Gate C (C49–C51/C64–C68/C70–C79): complete accepted-design nominal and failure matrix with actual artifacts and reconstructable evidence. Gate D (C52/C59 candidate proof, C53 source delivery and C69 observer delivery, then C60 released proof; master C5): packaged macOS/Linux capability, budgets, installed smoke, release version/hash and learning artifacts. Any unresolved required test/finding or unsupported required capability keeps the relevant gate pending.

C60 release evidence must include the full acceptance matrix, package source/review/delivery revision, built/released hashes, tested platforms and declared assurance. Consumer fixtures pin a released core version; a local wheel smoke proves the candidate only until the actual release artifact is verified. C53 tests the candidate workflow/artifact before its source commit/review/delivery; C69 separately delivers the observer/checker and post-release workflow. C60 then uses those delivered workflows under later explicit release-task authority and verifies the resulting released artifact. C60's own evidence commit is not a prerequisite part of that target package. C5 remains pending until exact released hash/version checks on both platforms and delivered tutorial/rationale are recorded, including the complete C5 installed-artifact manifest from C59, executed by C69/C60 (local-only, two-clone, repair, migration/import, performance and platform capability evidence). Later release authority is distinct from this planning assignment. Extension API 1.0/repo split and full-install meta-package remain later master-plan scope.

## Migration and production handoff

C77 supplies kind normalization before C46 inventories actual source fixtures; C48 supplies the shared bound preview/apply constructor and C51 proves predicted-versus-actual payload parity. C46 freezes actual source fixtures from planning at a named SHA, including #1/#2 and the leaf records created from this plan; new later fixture inputs require a recorded refresh. Preserve original backfill envelopes, native-unavailable/manual assurance, blocked/unsubmitted attempt evidence and unknown timing. C47 creates an inspectable proposal; C48 applies only the independently committed exact declaration. Tests never migrate the live project. C51 verifies fresh clones before/after cutover, same adoption identity, no issue renumbering, accepted raw snapshots preserved before metadata conversion and no false exact-content coverage.

M1 delivery includes these capabilities and review open/turn/complete/import before retiring any checkout. The real aitm production store remains on the authorized bootstrap process through M2's required GitHub identity capability, production policy selection and C6 freeze/readiness verification. At C6, inventory every checkout/owner, preserve dirty/untracked/ignored work and retained reviews, and obtain the current owners' explicit release of live authoring reservations before freeze; if unrelated live work cannot be reconciled, retain it and keep adoption pending while independent work continues. Land the approved default-branch declaration, remove only the safely released planning checkout, then CAS-apply/publish/verify. Readiness evidence includes fresh-clone validation, full index rebuild/query parity and the first post-cutover GitHub identity issuance plus lost-response reconciliation in the existing namespace (M2/C6 live-provider proof). If no cutover commit exists, retain bootstrap. If cutover committed but publication/readiness is pending, recover forward under the same identity; do not resume arbitrary manual writes. Once ready, use core live review ingestion and CAS FUR+collateral import through M4's later producer automation.

Existing GitHub IDs remain scoped to their issuer/repository. Core-only production migration cannot begin issuing replacement local IDs. Every-push hosted audit stays M2 investigation, not a fabricated M1 layer. Actual production adoption, configuration changes, repo enforcement switch and epic closure are outside this assignment and this plan's acceptance.

## Review procedure, leaf creation and open decisions

The original SAR → manual SPR → native XPR sequence below is completed historical provenance for its own bytes. The owner's later 2026-11-09 instruction separately authorizes this full-file native validation after the design validation: Astra-6/ExtraHigh author and Opus 5.5/high reviewer, full fresh current-file rereads in every round, five-round cap, verified publication, then stop before implementation. It does not request another SAR/SPR or change global review policy. Prepare the candidate against design publication 3702cfde855e7a2345e12439f19cc2ee9ebe7291; preserve the prior published plan plus the author preparation diff separately from native round patches, with both base commits/digests. Long physical lines are wrapped before review so Read output can be checked completely. Verify actual returned-line coverage before every next turn/finalization, not merely the reading instruction.


The completed original sequence used author Astra-6/xhigh, manual SAR and a distinct manual SPR reviewer GPT-6.1 Sol/high, then native Claude Opus 5.5/high XPR, isolated per-level worktrees. Read the full current file each round, disposition every finding, preserve patch 000 plus each author delta/empty final ACK, actual identities/settings and qualified timestamps. Publish each exhausted level before the next; retain five-round-cap failures honestly. Preserve both blocked native attempts and their private recovery evidence. Follow the owner-designated, ignored trunk `.tmp/interim-review-strategy.md` (input snapshot SHA-256 `7fa46bdce88681d8ac15e4de7f3af3772189644c3ddd21aefa15bab8f2057a39`; local bootstrap help, not a portable dependency). This paragraph and the published response/patch/manifests retain the operative procedure for other clones. Use that strategy (current owner assignment overrides any historical stop boundary) while the core is unavailable. This is the owner's scoped assignment, not a global policy edit.

After this revised decomposition is accepted, reconcile existing C01–C70 issue/story records and create only newly accepted C-keys; retain old estimate/source provenance and all existing permanent IDs. For each stable C-key, retain one issue/story with parent #2, exact estimate, dependency IDs, plan section link, touched areas/tests/evidence/risks, a likely-defect note derived from the proof, and Backlog status. Search the deterministic C-key before retrying an uncertain issue creation. Publish a separate leaf ledger mapping C-key↔issue ID↔story path and dependency/parallel order; keep this accepted file unchanged. Update #2's children, Plan estimate and issue links through the bootstrap record route with explicit manual provenance; never claim a native core transition or leaf design/plan review occurred.

No unresolved owner choice is silently decided: global review-depth/sequence policy, expansion completion boundary, second-trip cap, hosted every-push audit, future provider/harness details and full-install name remain open. Production review policy/provider readiness gates C6, while all current planning and leaf creation can finish independently. Routine calls made here: proposed module boundaries and bounded interfaces; explicit fixture policies rather than product defaults; clone-local environment identity metadata with no provisioning-only planning event; terminology distinguishes provisioning from admission preparation. Revisit these through review/JIT if evidence changes them.


## Executable qualification scenario map

The commands in C49–C53/C59/C60/C64–C70 select the actual listed suite files, not empty test_cNN wrappers. Each required scenario below has a collected test; CI owns collection evidence, exit status, platform and report artifacts. Low-level doubles cannot replace the real CLI/Git assertions specified here.

| Scenario | Collected suite/test and prerequisite owner |
| --- | --- |
| Story/defect source-commit, Test receipt and Review composite guards; kind/finalizer production registration | tests/integration/test_c76.py::test_source_commit_guard; test_c79.py::test_test_exit_binding, ::test_review_exit_composite; test_c29.py::test_kind_registration; test_c30.py::test_expansion_finalizer_registration; test_c62.py::test_epic_aggregate |
| Publication-conflict CLI resolution and explicit push retain operation lineage | tests/integration/test_c17.py::test_sync_reconcile_cli and ::test_sync_push_cli |
| Full installed explain: kind edges, pass/fail/unknown, pending effects and exact command | tests/integration/test_c78.py::test_installed_explain; tests/performance/test_budgets.py (C52) |
| Explicit legacy kind provenance, #1/#2 epics, unresolved-kind blockers and no synthetic split | tests/unit/test_c77.py::test_legacy_kind_mapping; tests/integration/test_c46.py::test_actual_v0_kind; test_v0_cutover.py::test_migrated_kinds (C51), apply blocker C48 |
| Entity authoring/handoff; bounded split; source-review envelope; decomposition source and reconciliation | tests/integration/test_c74.py::test_entity_authoring, test_c71.py::test_refine_split, tests/unit/test_c73.py::test_source_review_record, tests/unit/test_c72.py::test_plan_entry_contract, tests/integration/test_c75.py::test_decompose_once and ::test_decomposition_reconcile |
| Delivered anchor/issuer adoption and genuine pivot | tests/integration/test_c11.py::test_reconfigure_continuity, test_c31.py::test_human_pivot |
| Full current v0 shape inventory and typed mapping | tests/integration/test_v0_cutover.py::test_full_corpus_inventory (C46/C51) |
| Nominal local-only source lifecycle; complete CLI route coverage | tests/integration/test_core_walk.py::test_complete_cli_walk (C49); test_cli_surface.py::test_cli_surface (C67) |
| Default publication is attempted without --push and lost ACK reports retryable pending | test_core_walk.py::test_default_publication_pending, remote-configured disposable store (C09/C49); nominal local-only walk separately asserts N/A |
| Eligible authored sync is separate, transition repins, conflict retained; early verdict activates later through evidence reconcile | test_lifecycle_recovery.py::test_authored_sync_and_late_activation (C17/C28/C38/C42, C68) |
| Advisory absent-plan/unbound Develop; later acceptance/bind/reconcile same attempt | test_lifecycle_recovery.py::test_provisional_attempt (C27/C28 producers, C68 qualification) |
| Unverified Done real missing-test rerun; new limited generation, old one fenced, genuine later clock interval | test_lifecycle_recovery.py::test_evidence_only_rerun (C61/C42/C38, C68) |
| Actual installed preflight with reconcile, provisional attempt and local/shared expand construction/retry/lost ACK | tests/integration/test_preflight_consumers.py::test_reconcile_with_real_preflight, ::test_provisional_attempt_with_real_preflight, ::test_expand_with_real_preflight (C27/C28/C30/C31/C64, C70) |
| 8 stories ×50 syncs; related-story/policy/authored publication conflicts | tests/integration/test_shared_store.py::test_eight_by_fifty and ::test_conflicting_inputs (C50) |
| Two clones: pending expansion fences actual test/promote/signoff; enforce stop wins before test launch | tests/integration/test_execution_races.py::test_expansion_completion_fence and ::test_shared_stop_no_test_launch (C30/C31/C32/C35/C42/C61/C76/C79, C65; actual exit evaluators and specific refusal causes) |
| Trip before authored sync, on CAS retry and at completion before effective pass | test_execution_races.py::test_trip_before_sync_and_pass (C31/C32/C38/C76/C79, C65; actual evaluators, specific trip cause) |
| Lost issue reply resolved without child; early review activated later; full rebuild without private state | test_execution_races.py::test_reservation_and_review_rebuild (C20/C23/C30/C38/C76/C79, C65; actual exit evaluators) |
| Local-only core-run target delivery succeeds with publication N/A; checked-out/invalidated target refuses; post-CAS crash observes one result | test_delivery_races.py::test_local_delivery_admission and ::test_delivery_crash_reconcile (C39–C41/C76/C79, C66; actual evaluators and specific admission/refusal causes) |
| No-mutation dry-run; forged declaration/receipt/legacy extension rejected; second clone adoption identity and index parity | tests/integration/test_v0_cutover.py::test_dry_run_read_only, ::test_receipt_forgery, ::test_two_clone_cutover (C46–C48, C51) |
| Real portable/native bytes, historical levels and qualified timing live/backfill normalize without duplicate acceptance | tests/integration/test_review_import.py::test_actual_review_records (C24–C26/C57/C58, C51) |
| Forward repair validates through the normal fresh-clone path; managed target mutation detects external checkout interference | tests/integration/test_c10.py and test_delivery_races.py::test_delivery_checkout_race (C06/C10/C41, C66) |
| Installed extension command/provider/init under committed enabled/disabled policy | tests/integration/test_c63.py (C63; C49/C59 collection) |
| Actual selected contained executor and readiness on each OS, plus denied capability and explicit captured-export policy | tests/platform/test_c36.py and test_c37.py; installed-wheel matrix in tests/packaging/test_wheel.py (C36/C37/C59) |
| Full entrypoint budgets and entire pure unit suite isolation | tests/performance/test_budgets.py with tests/unit/conftest.py guard; also run pytest packages/aitm-core/tests/unit -q (C52) |
| Candidate release procedure before source delivery; exact published artifact after authorized publication | tests/packaging/test_release_workflow.py (C53) and test_release_checker.py (C69), then read-only tests/packaging/test_published_release.py with the observed release manifest (C60; publication is a separate authorized operation) |

C59 core-ci.yml runs the full unit and integration directories, OS-specific platform suite and explicitly selected candidate packaging suites (not the post-release suite), plus the named performance fixture job where hardware is available. The delivered C69 core-post-release.yml job, invoked under C60 authority, reruns the named full C5 suites against the exact installed released wheel through C59's isolated runner, with executable/module/RECORD path checks. Candidate/source reports alone cannot pass C5. The post-release suite is explicitly marked/separate and invoked only after the publication operation completes; it observes/installs that exact release and cannot dispatch publication; it is not a pre-delivery assertion or a silently skipped C5 proof. Platform-unavailable jobs retain diagnostics and require a supported host for a positive contained claim. Qualification reports enumerate collected tests and any exclusions; an uncollected or skipped required scenario keeps its gate pending.


## Mandatory shared-file integration additions

Functional dependencies are retained. Each consecutive writer below is an explicit predecessor in the next writer's Depends on; transitive order also protects all nonadjacent overlapping pairs. New path ownership at JIT requires a refreshed overlap check before parallel execution. This table names path ownership, not an instruction to run otherwise disjoint work serially.

| Shared path | Previous writer | Next writer |
| --- | --- | --- |
| `packages/aitm-core/pyproject.toml` | C01 | C03 |
| `uv.lock` | C01 | C03 |
| `packages/aitm-core/src/aitm_core/events.py` | C02 | C56 |
| `packages/aitm-core/src/aitm_core/services.py` | C01 | C06 |
| `packages/aitm-core/src/aitm_core/services.py` | C06 | C07 |
| `packages/aitm-core/src/aitm_core/services.py` | C07 | C08 |
| `packages/aitm-core/src/aitm_core/services.py` | C08 | C14 |
| `packages/aitm-core/src/aitm_core/store/backend.py` | C04 | C14 |
| `packages/aitm-core/src/aitm_core/services.py` | C14 | C09 |
| `packages/aitm-core/src/aitm_core/store/validation.py` | C06 | C10 |
| `packages/aitm-core/src/aitm_core/services.py` | C09 | C10 |
| `packages/aitm-core/src/aitm_core/cli/planning.py` | C06 | C10 |
| `packages/aitm-core/src/aitm_core/services.py` | C10 | C11 |
| `packages/aitm-core/src/aitm_core/services.py` | C11 | C12 |
| `packages/aitm-core/src/aitm_core/setup/init.py` | C11 | C12 |
| `packages/aitm-core/src/aitm_core/cli/setup.py` | C11 | C12 |
| `packages/aitm-core/src/aitm_core/services.py` | C12 | C17 |
| `packages/aitm-core/src/aitm_core/store/workspace.py` | C16 | C74 |
| `packages/aitm-core/src/aitm_core/store/sync.py` | C17 | C74 |
| `packages/aitm-core/src/aitm_core/drafts.py` | C19 | C74 |
| `packages/aitm-core/src/aitm_core/cli/drafts.py` | C19 | C74 |
| `packages/aitm-core/src/aitm_core/cli/sync.py` | C17 | C74 |
| `packages/aitm-core/src/aitm_core/services.py` | C17 | C74 |
| `packages/aitm-core/src/aitm_core/services.py` | C74 | C21 |
| `packages/aitm-core/src/aitm_core/cli/stories.py` | C22 | C21 |
| `packages/aitm-core/src/aitm_core/cli/plan.py` | C26 | C27 |
| `packages/aitm-core/src/aitm_core/reviews/acceptance.py` | C26 | C72 |
| `packages/aitm-core/src/aitm_core/services.py` | C21 | C28 |
| `packages/aitm-core/src/aitm_core/cli/dispatch.py` | C09 | C28 |
| `packages/aitm-core/src/aitm_core/machine/transitions.py` | C28 | C71 |
| `packages/aitm-core/src/aitm_core/machine/guards.py` | C28 | C71 |
| `packages/aitm-core/src/aitm_core/services.py` | C28 | C71 |
| `packages/aitm-core/src/aitm_core/machine/guards.py` | C71 | C29 |
| `packages/aitm-core/src/aitm_core/machine/transitions.py` | C71 | C29 |
| `packages/aitm-core/src/aitm_core/services.py` | C71 | C29 |
| `packages/aitm-core/src/aitm_core/services.py` | C29 | C30 |
| `packages/aitm-core/src/aitm_core/services.py` | C30 | C31 |
| `packages/aitm-core/src/aitm_core/store/backend.py` | C14 | C31 |
| `packages/aitm-core/src/aitm_core/store/sync.py` | C74 | C31 |
| `packages/aitm-core/src/aitm_core/machine/transitions.py` | C29 | C31 |
| `packages/aitm-core/src/aitm_core/services.py` | C31 | C35 |
| `packages/aitm-core/src/aitm_core/setup/doctor.py` | C12 | C35 |
| `packages/aitm-core/src/aitm_core/store/gate.py` | C06 | C41 |
| `packages/aitm-core/src/aitm_core/cli/deliver.py` | C39 | C41 |
| `packages/aitm-core/src/aitm_core/reviews/activation.py` | C38 | C42 |
| `packages/aitm-core/src/aitm_core/services.py` | C35 | C43 |
| `packages/aitm-core/src/aitm_core/store/sync.py` | C31 | C43 |
| `packages/aitm-core/src/aitm_core/cli/sync.py` | C74 | C43 |
| `packages/aitm-core/src/aitm_core/outcomes.py` | C42 | C44 |
| `packages/aitm-core/src/aitm_core/cli/bind.py` | C16 | C45 |
| `packages/aitm-core/src/aitm_core/cli/migrate.py` | C46 | C47 |
| `packages/aitm-core/src/aitm_core/store/validation.py` | C10 | C48 |
| `packages/aitm-core/src/aitm_core/cli/migrate.py` | C47 | C48 |
| `packages/aitm-core/src/aitm_core/cli/evidence.py` | C42 | C61 |
| `packages/aitm-core/src/aitm_core/cli/bind.py` | C45 | C61 |
| `packages/aitm-core/src/aitm_core/machine/kinds.py` | C29 | C62 |
| `packages/aitm-core/src/aitm_core/services.py` | C43 | C62 |
| `packages/aitm-core/src/aitm_core/services.py` | C62 | C63 |
| `packages/aitm-core/src/aitm_core/cli/app.py` | C01 | C63 |
| `packages/aitm-core/src/aitm_core/setup/init.py` | C12 | C63 |
| `packages/aitm-core/src/aitm_core/machine/guards.py` | C29 | C76 |
| `packages/aitm-core/src/aitm_core/machine/transitions.py` | C31 | C76 |
| `packages/aitm-core/src/aitm_core/services.py` | C63 | C76 |
| `packages/aitm-core/src/aitm_core/machine/guards.py` | C76 | C79 |
| `packages/aitm-core/src/aitm_core/machine/transitions.py` | C76 | C79 |
| `packages/aitm-core/src/aitm_core/services.py` | C76 | C79 |
| `packages/aitm-core/src/aitm_core/signoff.py` | C42 | C79 |
| `packages/aitm-core/src/aitm_core/cli/read.py` | C18 | C78 |
| `packages/aitm-core/src/aitm_core/graduation.py` | C22 | C75 |
| `packages/aitm-core/src/aitm_core/services.py` | C79 | C75 |
| `uv.lock` | C03 | C53 |
| `packages/aitm-core/pyproject.toml` | C03 | C53 |
| `docs/release/core-m1.md` | C53 | C60 |
