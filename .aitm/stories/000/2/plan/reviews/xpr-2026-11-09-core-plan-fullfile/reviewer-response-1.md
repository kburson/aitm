---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "reviewer"
round: 1
artifact_path: ".aitm/stories/000/2/plan/core-implementation-plan.md"
artifact_base_commit: "ab631c02f2eef28517f8a864e54679fdd548f467"
artifact_digest: "sha256:ef3f278a4ce014e7f8a4e5866c25b1b9d3070f2ab0ce93168bfd1a2199e18719"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:00278e43df2c8f02eef7ab5892e8a19c3d1097a8b1ee6e0e18436dcf006ca043"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T13:20:53.298Z"
submitted_at: "2026-11-09T13:25:40.742Z"
start_basis: "claim"
start_source: "native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-review-manifest.md#claim-claim-3b778829-d7e5-492e-ab31-f62114d9738e"
finding_ids: []
answered_finding_ids: []
native_source: "native/plan/2026-11-09-core-implementation-plan-review-09e4246bfa4caa5feff1592de9f2249c/review-09e4246bfa4caa5feff1592de9f2249c-reviewer-response-1.md"
native_source_digest: "sha256:5b36a24353f6ca5110afbb21a5a43f906275b9caf204c37cabb725a1f06132ce"
---

Mode: `normal`

## Summary

Round 1 independent full-file validation of `.aitm/stories/000/2/plan/core-implementation-plan.md` (candidate at `ab631c02f2eef28517f8a864e54679fdd548f467`) against the accepted core design (`.aitm/stories/000/2/design/core-design.md`, read in full as context, 726 lines) and the author preparation note `preparation/provenance.md`. The C71–C75 additions and the C03/C54/C11/C16/C22/C28/C31/C38/C46 changes are author preparation, not reviewer findings. Every finding below is raised by this reviewer.

### Fresh full-file reread

- Tool: Read, contiguous chunks of ≤30 lines, this round only. Ranges read: 1–30, 31–60, 61–90, 91–120, 121–150, 151–180, 181–210, 211–240, 241–270, 271–300, 301–330, 331–360, 361–390, 391–420, 421–450, 451–480, 481–510, 511–540, 541–570, 571–600, 601–630, 631–660, 661–690, 691–720, 721–750, 751–780, 781–810, 811–840, 841–870, 871–900, 901–930, 931–960, 961–990, 991–1020, 1021–1050, 1051–1080, 1081–1110, 1111–1140, 1141–1170, 1171–1200, 1201–1230, 1231–1260, 1261–1290, 1291–1320, 1321–1350, 1351–1380, 1381–1410, 1411–1440, 1441–1470, 1471–1487. The last request (offset 1471, limit 30) returned only 17 lines, so line 1487 is EOF.
- Observed line count: 1487. Grep for lines matching `$` also counts 1487.
- Long-line check: Grep `^.{2001,}` returns 0 matches. No physical line exceeds 2,000 characters. The longest wrapped paragraphs (lines 62, 100, 220–221, 309, 757–758, 802–803, 819–820 and 1278–1280) came back in full with their continuation lines. No output was truncated, so no recovery was needed.
- Native input artifact digest: `sha256:ef3f278a4ce014e7f8a4e5866c25b1b9d3070f2ab0ce93168bfd1a2199e18719`. This value comes from this response's protected `artifact_digest` and matches the candidate raw SHA-256 in `preparation/provenance.md`. I could not compute it independently because shell hashing was denied in this session, so the author should confirm it during the audit.

### Independently verified (no finding)

- **Totals:** I re-added the leaf table: 75 leaves, 242.5 h, every leaf 2.5–4 h. C71–C75 add 17 h, and 220.5 + 17 + 5 = 242.5.
- **Order:** the backlog table (lines 134–210) is a valid topological order. Every listed predecessor appears earlier.
- **`services.py`:** it has 19 writers, which matches the 19-writer chain in the shared-file table (C01→C06→C07→C08→C14→C09→C10→C11→C12→C17→C74→C21→C28→C71→C31→C35→C43→C63→C75).
- **Other shared paths:** each consecutive pair I checked carries a Depends-on edge: cli/plan.py, cli/stories.py, cli/bind.py, cli/evidence.py, cli/deliver.py, cli/migrate.py, cli/sync.py, store/sync.py, store/validation.py, store/gate.py, machine/transitions.py, machine/guards.py, machine/kinds.py, reviews/activation.py, reviews/acceptance.py, outcomes.py, graduation.py, setup/init.py, setup/doctor.py, pyproject/uv.lock and events.py.
- **Coverage I checked against the design:** most of the new design contracts trace to owning leaves and named tests, including:
  - kind/split (C71)
  - typed plan-entry descriptors and own-document coverage (C72/C26/C75)
  - source-review envelope and independence (C73/C38)
  - entity editing (C74)
  - review-open fact (C25/C56)
  - scalar resolver (C03)
  - reconfiguration (C11)
  - pivot (C31)
  - decomposition estimate (C27/C54)
- **Leaf structure:** each leaf has a test file, verify command and evidence clause. The checkpoints/gates and the C59/C69/C60 release chain are coherent.

Five required gaps remain, F1–F5 below:
- two production-wiring gaps for kind-specific later-state guards and the expansion finalizer, plus one for `explain` guard reporting;
- one design guard with no owner or tests (the source-commit guard);
- one CLI route with no owner (`sync --reconcile`/`--push`);
- one migration mapping omitted (v0 `kind`).

## Findings

1. **F1: required, major. The Develop-exit source-commit guard has no owning leaf and no executable vectors.**
   - **Design:** core-design lines 426 and 430 define story-commits as an exact subject prefix `[#<positive decimal story ID>] `, with:
     - no substring matching;
     - only nonempty implementation changes on the *recorded attempt branch* since its *pinned baseline*;
     - preflight retaining the matching source commits and reviewed head/tree;
     - delivery that need not preserve the prefix, where target-message text cannot replace source evidence.
   - **Plan:** Grep finds no `story-commits`, `subject prefix` or `[#` guard anywhere in the leaf tests.
     - C28 covers only the early-state matrix (Backlog/Refine/Ready).
     - C29 tests kind substitutions for epic and spike only.
     - C49's nominal walk makes one "tagged source change", which proves only the positive path.
   - **Failure scenario:** an implementation that matches `[#1` as a substring would let a story #1 attempt pass on commits tagged `[#12] `. So would a check that accepts commits outside the attempt branch or before its baseline, or an empty/merge-only change. Every planned test would still pass.
   - **Also missing:** the story/defect Test-exit `test-passing` binding (current receipt for the clean source snapshot and attempt) and the Review-exit composite (`review-passed / delivered / signed-off / evidence-complete` on the *same* source and attempt). Their producers exist (C35/C38/C39/C42), but no leaf owns the guard predicates that compare them, and no test names those predicates.

2. **F2: required, major. Kind-specific later-state guards and the expansion finalizer have no production registration or call-site owner.**
   - **Kind guards:** C29 produces `kind_requirements(kind, slot)` in `machine/kinds.py`, and C62 extends kinds.py with epic aggregation. Neither leaf touches `machine/guards.py`, `machine/transitions.py` or `services.py`, and C29's only test is a unit test.
   - **Why that breaks:** C28 owns the transition pipeline but lands before C29, so it cannot import or register C29's matrix. C01's mandatory-port list has no kind-requirements port either. Lines 100 and 65 state the plan's own rule: each wiring leaf declares its services/shared call-site paths and tests the normal entry point, and no later task is a bucket for missing wiring.
     - As written, the real `promote` on a spike (C45 walk) or epic (C62 "real epic transitions") has no owned path to apply the design's substitutions (core-design lines 432–438).
     - Those substitutions are: spike deliverable/validation receipt instead of commits and a test receipt; epic with no JIT, binding or clock, aggregate Test/Review over children, and nonempty accepted child set at Plan exit.
     - Without them, the pipeline would apply story guards to epics and spikes, refusing legal epic Develop entry in enforce mode or passing unsupported checks.
   - **Expansion finalizer:** C30 says it will "register the core expansion finalizer with C22", but C30 touches only `rules/expansion.py` and `cli/expand.py`. C22's `register_finalizer` registry must be populated from a composition point (`services.py` or `graduation.py`). Neither appears in C30's allowlist or in the shared-file table. An import-time side-effect registration would be a hidden dependency from C22's module on a later leaf.
   - **Ordering consequence:** adding guards.py/transitions.py/services.py to C29/C62/C30 creates new overlaps with C71 and C31. Those need explicit edges, for example C29 after C71 or C71 after C29, and C30 inside the services chain before C71/C31. The chain must be recomputed rather than assumed.

3. **F3: required, moderate. `sync --reconcile <operation-id>` and `sync --push` have no CLI adapter owner or positive operational proof.**
   - **Design:** core-design line 329 specifies that `sync --reconcile` presents retained local and published versions and accepts a new scoped operation that resolves the conflict, with explicit supersession lineage. It may not reinterpret the old result as published or erase evidence. Line 633 makes `sync --push` the explicit request for the default publication guarantee.
   - **Plan:** CLI map line 118 assigns `--reconcile` to "C09 reconcile; cli/sync.py".
     - C09 does not touch `cli/sync.py`, which is created later by C17. C09 produces only the library `reconcile(operation_id, resolution)`.
     - C17's test (line 509) never mentions `--reconcile` or `--push`, and neither do C74 or C43, which also write cli/sync.py.
     - C50's `test_conflicting_inputs` only proves conflicts are retained, not resolved through the route with supersession lineage.
     - C67 checks help and arguments only, and explicitly cannot stand in for positive behavior.
   - **Failure scenario:** the route could ship as an unavailable stub, or with a parse-only option, and no planned test would fail. The route ledger at line 1236 has no positive owner for it.

4. **F4: required, moderate. The v0 migration omits the explicit `kind` mapping and the unresolved-kind blocker.**
   - **Design:** core-design line 679 has the adapter map each story's explicit legacy `kind` into the normalized initial graduation/kind fact with header path/digest provenance. #1 and #2 remain epics. A missing, unknown or contradictory kind is unresolved inventory needing an explicit mapping and is never defaulted to story. The adapter does not synthesize a historical split.
   - **Acceptance:** the design's acceptance row "Kind and splitting" (line 698) requires "Migrate #1/#2 as epics with header provenance; unknown kind stays unresolved."
   - **Plan:** C46 (line 1028), C48 (line 1060), C51 (line 1074) and the scenario map (lines 1399/1411) do not mention kind. Grep finds no `as epics`, `unknown kind` or `kind field`, and line 1353's coverage row does not list C46/C51 for this obligation.
   - **Failure scenario:** fold derives kind only from typed facts (core-design line 387). A migration without this mapping yields kind-less stories or silently defaulted stories. Defaulted stories would then hit the leaf four-hour Refine guard on migrated aggregate estimates such as epic #1/#2, and every planned test would still pass.

5. **F5: required, moderate. Installed `explain` is never wired to the transition explanation, and its required semantics are untested.**
   - **Design:** core-design line 648 requires `explain <id>` to name the pinned state/policy, the next kind-appropriate edge, each guard's pass/fail/unknown reason, pending side effects and the exact next command, and never to present an unobserved condition as passing. Line 155 requires freshness-dependent guards to be reported as unknown when they cannot be proved.
   - **Plan:** C28 produces `explain(snapshot, story) -> TransitionExplanation` but does not touch `cli/read.py`. That file is owned by C18, which lands before C28, and C18's test only checks pinned freshness for explain. No later leaf touches cli/read.py, and no test asserts guard pass/fail/unknown, the next edge or the exact next command through the installed command. C52 only times explain, and C67 checks only help and arguments.
   - **Failure scenario:** the shipped `aitm explain` could keep showing only the C18 pinned/freshness view, or could report an unobservable freshness guard as passing. No planned test would fail.

## Required changes

1. **F1:** Assign an owner for the story/defect later-state guard predicates. This can be a C28 extension or C29 within ≤4 h; otherwise add a bounded leaf. Add named vectors:
   - exact `[#<id>] ` prefix acceptance;
   - rejection of a substring or other-ID prefix (`[#12] ` for story 1), a missing trailing space and a non-decimal ID;
   - rejection of commits outside the recorded attempt branch or before its pinned baseline, and of empty implementation changes;
   - retention of the matching commits plus reviewed head/tree in preflight;
   - a squash/rebase target message without the prefix that still verifies through source mapping;
   - the Test-exit current-receipt binding and the Review-exit same-source/attempt composite.

   Update the acceptance coverage row and the scenario map.
2. **F2:**
   - Add the production call sites to the owning leaves' allowlists: guards.py/transitions.py/services.py for C29 (and C62 if it registers aggregate guards), and services.py or graduation.py for C30 finalizer registration. Each owner must prove its real registration through the normal `promote`/`expand` entry point in its own test file.
   - Recompute and record the resulting shared-file predecessor edges against C28/C71/C31 and the services chain, keeping the table topological.
   - Alternatively, declare typed kind-requirement and finalizer-registry ports in C01/C28/C22, with fixture-composed negatives and production-registration proofs, following the existing port pattern.
3. **F3:** Name the cli/sync.py owner for `--reconcile` and `--push`. It must run after C09 and serialize with C17/C74/C43. Add an integration test where a real `sync --reconcile <op>` on a retained publication conflict appends a new scoped resolving operation with supersession lineage, keeps the original local evidence unpublished and never relabels it as published. Prove `sync --push` uses the same bounded publication path. Add the test to the C67 positive ledger and the scenario map.
4. **F4:** Extend C46 mapping/inventory and C51 qualification, plus the C48 cutover if needed, so that:
   - the explicit legacy `kind` header maps to the typed graduation/kind fact with header path/digest provenance;
   - #1/#2 fold as epics;
   - a missing, unknown or contradictory kind is a cutover blocker, never defaulted;
   - no historical split is synthesized and no migrated aggregate estimate is treated as an oversized leaf.

   Name the test vector in the scenario map and the coverage row at line 1353. Keep the ≤4 h bound by re-estimating or splitting if needed.
5. **F5:** Assign the wiring of installed `explain` to C28's `TransitionExplanation`. This needs an owner that touches `cli/read.py` after both C18 and C28, with the edge recorded. Add an installed-command test asserting:
   - the next kind-appropriate edge;
   - per-guard pass/fail/unknown, including freshness-dependent unknown;
   - pending side effects;
   - the exact next command.

   Also confirm that C52's timing still covers that complete path.

## Optional suggestions

1. **C71 wording (line 774):** "exercise the existing Backlog→Refine recovery path" reads as a single edge. Per core-design line 391, oversizing found at Plan or JIT first takes the design-rework edge to Backlog and then Backlog→Refine before split. Naming both steps would avoid implying a shortcut.
2. **C49's dependency on C48 (migration apply):** the nominal core-only walk does not exercise migration, and this edge delays the walk behind the whole migration chain. Either state why it is needed, for example a shared validator wiring prerequisite, or drop it, preserving any real shared-file reason.
3. **`explain` performance:** after F5, consider stating that C52's warm `explain` budget applies to the guard-explaining path with lazy guard/extension loading, not to the freshness-only C18 view.

## Decision

revisions-requested
