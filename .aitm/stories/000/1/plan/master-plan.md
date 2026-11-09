---
schema: aitm.doc/v0
story: 1
role: plan
title: aitm master plan
created: 2026-11-08T19:55:00Z
updated: 2026-11-09T06:34:30Z
last-branch: planning
status: review candidate (acceptance is in review records)
design: ../design/architecture.md
core-design: ../../2/design/core-design.md
---

# aitm master plan

**Goal:** Deliver the accepted architecture incrementally, with a usable, evidence-preserving core before replacing the bootstrap workflow.

**Architecture:** Git on the isolated planning branch owns story data; one core transaction API serializes changes. SQLite and backlog services are projections. Extensions use released core contracts; the core never calls a model.

**Stack:** Python 3.13, uv workspaces, Pydantic v2, Typer, pytest and Ruff; httpx in network extensions; TypeScript only in the viewer. The installed CLI is `aitm`; no Node runtime requirement for consumers.

**Sources:** [Owner decisions](../draft.md), [architecture](../design/architecture.md), [accepted core design](../../2/design/core-design.md). Architecture XPR publication: `981b8d77e2e988e9ec3f79768c7c9728cb66c11a`; core XPR publication: `1f4d4a354a10dfd173c70cc8421dafd28c25a57a`. Review manifests bind the accepted bytes despite historical draft-status frontmatter. This plan supersedes its earlier milestone assumptions, not those source decisions.

## Global constraints and authority

- Planning is `.aitm/` data only, never merged into trunk. Code, workflows, policy and tutorials live on trunk through PRs. Store history is never rewritten automatically.
- Only implementation is limited to four engaged agent-hours per leaf attempt, from Develop entry through effective passing source review (deliverable review for spikes). Epics use aggregate child evidence with no implementation clock. Planning is unbounded; tool elapsed time is not agent engagement. Parallel agents add engagement but can reduce calendar time.
- Each later section epic is a child of #1. A section stays a draft until its own brainstorm; section design belongs in Backlog and its accepted implementation plan decomposes into leaves of at most four hours. A dependent brainstorm may begin after its prerequisite reaches Develop, without declaring the prerequisite delivered.
- Agent sign-off follows verified delivery; there is no routine human sign-off. Passing review, publication, package release, runtime adoption and epic closure are separate facts.
- Core runs advisory on aitm. Store integrity always applies. Consumers pin released packages, never live trunk; hooks are optional backstops.
- This assignment authorizes **SAR alone for this master plan**, and **SAR → manual SPR → native Claude XPR for #2's implementation plan**. It does not decide the global review-depth matrix or authorize implementation, trunk merges, epic closure, host configuration changes or tooling repairs.
- Every review round reads the full current file. Publish each completed level and its portable record before the next. Earlier levels accept their own versions; changed authored content is never retroactively covered. Under a selected, supported committed policy, the relevant design/plan acceptance guards require missing exact-content coverage or a valid scoped exception. Enforce refuses the affected transition; advisory may advance with failed/unknown guards retained, without asserting verified acceptance or delivered closure while applicable requirements remain unsatisfied.

## Milestone delivery map

| Milestone | Section / prerequisite | Delivered outcome and exit evidence |
| --- | --- | --- |
| M0 Bootstrap | #1; historical setup | Hand-built planning branch, #1/#2 graduation and decision archive exist. **Bootstrap established 2026-11-08**, not a claim that #1 is Done or that runtime acceptance exists. Keep the bootstrap checkout until M1 cutover passes. |
| M1 Core | #2; M0 | Released `aitm-core` 0.x: schemas, single-owner CAS store, authoritative policy/init, index, binding, state/kind matrix, operations/admission, local provider, CLI, timing, verification/delivery/recovery, extension/provider interfaces, live document-review open/turn/complete and validated bundle import, plus v0 migration. Local-only and shared-clone tests plus the accepted core design's entire acceptance matrix pass. The core is usable without GitHub/harness adapters. |
| M2 First hosted slice | aitm-github draft; stable M1 provider contracts and released core | Real issue graduation with uncertain-outcome reconciliation; hierarchy/dependencies; sparse board projection; PR/CI/delivery mapping; host protection/default-branch APIs. Validate live REST capabilities before relying on them; GraphQL only where needed. GitHub-specific init complements core init. Prove publication-gated projection of the latest state, stale retry suppression and ambiguous acknowledgement reconciliation, using monotonic versions or serialized ownership/fencing; unsafe takeover stays pending. Every-push audit constraint must be reconciled before claiming all six protection layers. |
| M3 Harness integration | aitm-harness draft; stable M1 CLI/activity contract and released core | Claude Code first, then Codex, then Grok: skills, recorded-payload translator contract tests, optional MCP over core functions. Trusted activity coverage must be demonstrated; missing/duplicate/untrusted hooks cannot break correctness. No model calls from core. |
| M4 Peer review | aitm-peer-review + ai-peer-review draft; M1 import/canonicalization/timing contracts; M3 for harness adapters | Record-only, caller-chosen review output with common response headers, patches 000…N, full-file raw digests and canonical acceptance binding. Automated true per-turn starts where available and automatic submission to the existing M1 live/completion/import sink replace manual coordination. Preserve native originals, unknown timing and failed attempts. First enforcing consumer is the ai-peer-review work, installed against a released core. Choose existing JS refactor versus Python rewrite in its section design. |
| M5 Agents | aitm-agents draft; M3; M4 for automated reviewed-plan flow | Harness-neutral researcher, planner and independent plan-reviewer roles/context packets. Prove read-only research and design/plan-only planner permissions; epic industry research stays opt-in. Fixed plan contract includes ≤4 h leaves, touched areas, tests, risks, likely defect areas and evidence. Can prototype role definitions after M3; completion waits for review integration. |
| M6 Viewer | aitm-viewer draft; M1 index/schema export; M2 for hosted issue links | Local viewer first, then prebuilt Pages viewer from generated planning JSON; disclose snapshot freshness. Progress, flow, time/cost/bumps, summaries, retros and Discuss command. Select a valid scheduled/dispatched/other build trigger in section design; do not confuse this with every-push audit. |
| M7 History import | history-import draft; M1 schema/migration; M2 source access | Import the old ai-task-manager corpus with source identity/digests and explicit imported/incomplete timing and evidence. Inventory current corpus rather than treating the historical ~2,165 count as fixed. No old issue-body regex rules become core authority. Import is repeatable and does not make historical issues runtime-verified Done. |
| M8 Rubric | aitm-rubric draft; M1 estimate/outcome/usage/lesson events; M7 corpus | Comparable-story retrieval and quantile regression; only complete Refine/Plan/Close triads calibrate. Incomplete/imported/unknown observations stay distinguishable. Evaluate against held-out data before claiming useful estimates; attach lessons to future planning. |

C5 is M1 package delivery; C6 is a later production-adoption checkpoint. M1 is larger than a scaffold: its accepted recovery, isolation, review import and migration obligations cannot be postponed to M4 while claiming M1 complete. #2's own plan supplies the bounded leaf sequence and initial/revised engagement estimates; this master plan makes no calendar commitment from unmeasured history.

## Dependencies and independent work

- M2 and M3 may develop independently against frozen M1 interfaces once M1 is delivered. Their designs can start under the earlier brainstorm rule while M1 develops, with provisional contracts clearly labeled.
- M6 local work can proceed alongside M2/M3 after M1; hosted links wait for M2. M7 can proceed alongside M3–M6 after M1/M2. M8 waits for validated corpus provenance, not merely copied files.
- M4's core import/record contract is delivered by M1; peer-review output refactoring can be designed against it while M3 develops. Native harness integration waits for M3; M4 acceptance includes the full integrated route.
- Parallel stories use distinct worktrees and bindings and declare disjoint touched files or an integration order. A shared contract change serializes dependent leaves; a stable API is demonstrated by contract tests, not a milestone label.
- Extensions are published separately from day one in the uv workspace. Entry-point discovery and configuration are separate from installation; full-install packaging must do both. Extension files/events have declared owners and disabled/older data survives round-trip.

## Identity continuity across adoption

aitm already uses GitHub issue numbers. M1's local provider cannot replace that issuer after migration. **Keep the bootstrap planning checkout and authorized issue-creation procedure through M1 C5 and the M2 bootstrap work**, including M2's section brainstorm, graduation and accepted leaf decomposition. M2 develops against a pinned released core in disposable fixtures/consumer repositories; it does not require aitm's own production cutover first. C6 on aitm waits until the required GitHub identity capability is released, installed/configured through its normal authorized path and verified for the existing namespace. Then the first post-cutover issue must be created through that provider and core finalization, with lost-response reconciliation proof. Other milestones may continue their authorized bootstrap planning meanwhile. If the provider is unavailable after cutover, existing story work/read/export can continue within core policy, but new GitHub issuance remains pending; never substitute local numbers or resume direct planning edits. This assignment performs none of that later graduation, installation or cutover.

## M1 checkpoints and migration

| Checkpoint | Required evidence / failure handling |
| --- | --- |
| C1 Contract baseline | #2 accepted design and reviewed plan, explicit operation/result types, provider ownership and canonical digest version. Actual #1/#2 v0 fixtures and current review records are pinned. Exact-content review obligations are evaluated separately from historical acceptance. Fixture policies for tests are explicit and are not production defaults. |
| C2 Store proof | Empty-tree orphan anchor, no checked-out planning ref, path/ancestry/continuity validation, multi-process CAS and operation deduplication. Shared publication/replay/conflict proof, repair retaining maximal valid prefix and invalid tail. Local transitions, remote publication and projection remain separately observable. |
| C3 Workflow proof | CLI-only local lifecycle and typed kind/disposition guards; clocks/trips/pivots, authoritative test lane, source review/delivery mapping and sign-off. Unknown timing never masquerades as exact engagement. Captured-export and contained assurances are named truthfully. Missing bookkeeping is reconstructed or real verification rerun, not manually declared passed. |
| C4 Review/migration dry run | Replay portable patches and verify each level's exact digest, participants, disposition coverage and timing provenance. Deterministic v0 conversion preserves authored bytes and accepted snapshots, maps them to versioned canonical content before generated metadata rewrite, and retains incompatible/unknown records. Adoption ID/store UUID/provider numbering continuity survive retries and two clones. Dry-run manifest lists every input/output hash and exception. The bounded legacy adapter covers the exact root/approved tip and deviations (including root README); preserve its prose/provenance within .aitm and remove it from the active root at cutover. Prove live review open before turn 1, provisional turn ingestion, completion and final import/backfill normalize to one fact set without duplicate time. |
| C5 Released package | Build/install released 0.x core in disposable macOS and Linux repositories with declared capability probes; exercise local-only and two-clone cases, migration/review import, repair and performance budgets. Record source revision, package hash/version and results. OS containment unavailability is visible, not silently downgraded. Publish the M1 tutorial from real code. |
| C6 Authorized adoption | Refresh and freeze a known planning snapshot; preserve dirty/untracked/ignored data and recovery refs. Require the supported, explicitly authorized production review policy (including any scoped exception authority), required GitHub identity capability and authoritative adoption declaration before apply; otherwise leave C6 pending. Land that declaration through normal PR delivery: exact legacy root/approved tip, adapter/allowed deviations, store UUID and provider/number namespace. A changed tip needs renewed inventory and declaration. Revalidate migration against that exact snapshot. Explicitly inventory all worktrees and coordinate owners; remove only the clean bootstrap planning checkout when safe. Apply with the core CAS writer, verify remote publication, imported content, index rebuild and a fresh clone; then record adoption evidence. |

Cutover is **not** simply `git worktree remove`. A stale snapshot, dirty checkout, live author reservation, incompatible required fact, ambiguous adoption or unavailable proof needed for safe apply leaves adoption pending with retained evidence. Optional unsupported records may remain opaque and incomplete historical reviews remain unaccepted evidence when safe to preserve; neither alone blocks cutover or confers acceptance. A fresh clone must verify the bounded legacy segment, declaration and cutover receipt. Do not remove unrelated or blocked review worktrees; they use distinct review refs. If apply has not committed, retain the bootstrap route. If migration has committed, recover forward with the same adoption identity; do not reset planning or resume arbitrary manual writes over the migrated store. An operator may keep the checkout absent while resolving a pending publication.

The configured planning ref must not be checked out once plumbing writes begin. Until the C6 freeze, including after C5 release, the legacy aitm store continues the authorized bootstrap publication of complete FUR and collateral through its planning checkout. C5 proves the core route in disposable migrated fixtures. After C6 verifies cutover publication and adopted readiness, production reviews still use temporary review refs/worktrees, but **FUR + collateral import uses `aitm review import` with path reservations, base/content checks and CAS**, never a recreated planning checkout. Prove this before retiring bootstrap. M4 changes review production and timing integration, not the safety requirement or the authoritative storage route.

## Review and timing obligations

Every completed level publishes the final FUR, response pairs including final acknowledgement, reconstructable patches, manifest, actual model/effort/session provenance, finding dispositions, changed calls and open choices. Native originals and qualified timing anchors remain available; private credentials/handles are excluded. A five-round cap with unresolved required findings is not acceptance.

M1 owns review open, live provisional review turn, review complete and final import/validation, as well as the portable v0 adapter and migration. On a ready adopted store after C6, until M4 automation, the coordinator opens a level through core before review, ingests each submitted manual/native response and available public timing anchors, completes the bundle, and uses the core writer for final FUR import. Missing native claim/start evidence stays Unknown until a public source supports it. M4 owns the no-precommit record-only producer, automatic true per-turn starts where supported and automatic handoff to that existing sink. Planning time is recorded by story/state/level/role/model but never feeds trips. Registration time reused across native rounds is not per-turn engagement; claim/prior-submit bounds, unknown spans, setup and publication exclusions remain explicit. Backfill names and hashes its sources, deduplicates turns and does not manufacture observations. Live and backfilled import of the same record must normalize identically.

The core design's published SAR/SPR/XPR and this assignment's plan levels are historical digest-bound decisions. If migration policy requires several levels on one current digest, it requests only the missing current-content coverage or a legitimate scoped exception; it neither upgrades historical approvals nor silently rewrites them. The assignment's chosen depths remain scoped evidence, not the global default.

## Release and adoption gates

- **Advisory → enforce on aitm:** retain the existing proposed checkpoint of at least two enforcing consumer repositories and 20 stories combined without a tool-caused block. Treat this as a measurable builder checkpoint, not authorization to switch modes now; record cohort, released versions, exclusions and observed failures on #1. The ai-peer-review work is the planned first candidate; select and authorize a second extension/consumer repo during its own section planning. No unnamed repository is implicitly enrolled. If not met, continue advisory.
- **Repo split:** after extension API 1.0, preserve history and verify packages/contracts across the split. No split is part of M1.
- **Full-install product gate (after applicable M2–M8 releases):** #1 owns completion with the packaging section. Once the name is decided, build the meta-distribution from pinned released packages and prove a fresh install resolves dependencies, discovers every entry point, enables/configures the complete supported extension set, and runs an integrated smoke workflow without Node at user runtime. Retain package versions, config and capability gaps; individual package releases alone do not pass this gate. This does not block M1.
- **Package naming:** the `aitm` PyPI conflict was observed on 2026-11-08; other names were available then. Recheck availability at release. The full-install distribution name remains unresolved; CLI stays `aitm`.
- **Learning:** each milestone ends with a trunk `docs/learn/` tutorial from its delivered code, plus short library-choice rationale. M1 covers Pydantic, Typer, plumbing and SQLite; later sections cover httpx, translator contracts, TypeScript/schema generation and ML. Retros capture Python concepts and planning lessons.

## Open choices and scoped assumptions

| Choice | Owner / effect on delivery |
| --- | --- |
| Expansion completion boundary; proposed second-trip cap | Owner-open. #2 implements the accepted provisional behavior with explicit provenance; no new hard second-trip cap. A later decision may require policy/fixture revisions before enforcement. |
| Global review depth by document and exact-content obligations | Owner-open. Only this assignment's depths are settled. Do not publish a universal default based on them. |
| Hosted every-push planning audit versus data-only branch | GitHub section investigates; owner decision required to relax either constraint. Does not block core-only M1, but blocks a claim of complete hosted six-layer protection. |
| Import or overwrite human edits on GitHub | GitHub section design; sparse projection must not silently decide bidirectional authority. |
| Grok MCP and native agent definitions | Harness/agents capability investigation; CLI/skill fallback preserves correctness. |
| Existing JS peer-review refactor or Python rewrite; meta-package name | Later section/release choices, not M1 blockers. |

Routine planning calls: retain M0–M8 identifiers for stable references; define explicit acceptance checkpoints rather than calendar dates; make migration/review import M1 release obligations; keep future sections as drafts. No runtime functionality, migrations or configuration changes are performed by accepting this plan.
