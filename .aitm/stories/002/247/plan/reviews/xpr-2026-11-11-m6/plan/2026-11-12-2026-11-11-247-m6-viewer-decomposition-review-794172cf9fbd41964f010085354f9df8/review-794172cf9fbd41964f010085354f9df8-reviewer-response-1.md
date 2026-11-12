<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-794172cf9fbd41964f010085354f9df8"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md"
artifact_commit: "996dae42effef6a6de6bb3879262a28013e899dd"
artifact_blob: "4d70079e6cd08c9c14495ed981860a274e0f082f"
artifact_digest: "sha256:cfe9143eb81d25efe8b6b586a1f4242cc4218cfc30122ec134ea1e060e07000c"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:a9ddb00c18bf95949c28df14c6e2ddb64131150db394d645b943157c0af3d18e"
  identity_source: "runtime"
started_at: "2026-11-12T00:44:08.587Z"
submitted_at: "2026-11-12T00:47:39.992Z"
finding_ids: ["R1-F001"]
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

This is the round 1 independent XPR plan review of `.aitm/stories/002/247/plan/2026-11-11-247-m6-viewer-decomposition.md` at commit `996dae42effef6a6de6bb3879262a28013e899dd`, blob `4d70079e6cd08c9c14495ed981860a274e0f082f`. The digest `sha256:cfe9143eb81d25efe8b6b586a1f4242cc4218cfc30122ec134ea1e060e07000c` comes from this response's protected frontmatter. It matches the digest recorded in the round 2 SPR record. The review covers Backlog decomposition only. It grants no pickup, Develop entry, sequencing authorization for the bootstrap, hosting, Pages enablement or Core child work.

### Full-file read record

- **Tool and range.** One Read call returned lines 1–151 with no truncation. Line 151 (the "Aggregate review and evidence" paragraph) is the last content line.
- **Hashing.** Shell hashing was not available to this reviewer, because Bash is limited to the package join/submit commands. The digest above was not independently computed.

### Related material read for validation

None of the following is under review.

- **Product #1.** Master plan `.aitm/stories/000/1/plan/master-plan.md`, lines 1–105 in full, including the M6 row (line 44), the dependency rule (line 53) and the learning gate (line 91).
- **#247 story record.** `story.md`, `draft.md`, `events.jsonl` and `plan/backlog-hydration-receipt.json` in full. I also read the frontmatter of all 13 child `story.md` files: #248–#260.
- **#247 attachments.** In full:
  - hosted dashboard coverage design;
  - read-only preview refinement;
  - preview plan;
  - preview plan review;
  - #139 pilot and its readback JSON.
- **Earlier reviews.** The SAR and SPR round 2 records. They were read for context only, and every assessment below is my own.
- **#181 sources.** The production scope transfer in full, and the C06 section and C01–C07 table rows of the Slice C plan. #227 was checked for its C01 identity and #181 seed values.
- **Core #2 plan.** Line 116 and lines 522–528, the C18 `discuss` context exporter.

### Independently verified (no finding)

- **Arithmetic.**
  - Leaf hours: 3 + 3 + 3.75 + 3.5 + 3.75 + 3 + 3.25 + 2.5 + 3.75 + 3.5 + 3.5 + 3.5 + 3.5 = **43.5 h**.
  - Every leaf is ≤ 4 h.
  - The table predecessors give 1 + 1 + 2 + 3 + 4 + 1 + 2 + 2 + 3 = **19 edges**.
  - The graph is acyclic. Its topological order is V01, V03, V02, V04, V05–V08, V09, V10, V11/V12, V13.
- **Mirror consistency.** The table, hydration receipt, `story.md` children list, `events.jsonl` plan keys and every child's `parent`/`blocking`/`blocked-by` frontmatter agree. This includes the non-monotonic issue numbering: V10 = #258 and V11 = #257. Estimates in each child match the table. The story-level estimate is 43.5. Live GitHub readback was not repeated, because I had no shell or network access.
- **Master-plan M6 coverage.**
  - Local viewer first: V03/V04.
  - Prebuilt Pages viewer from generated JSON: V09/V10.
  - Snapshot freshness: V04, V09 and V10.
  - Progress: V04.
  - Flow: V06.
  - Time/cost: V05, V11 and V12.
  - Bumps, summaries, retros and confidence: V07.
  - Discuss: V08.
  - Valid build trigger, kept distinct from the every-push audit: V09 bullets 1 and 3, consistent with the coverage design's manual-dispatch-first sequence.
  - Learning tutorial with TypeScript/schema-generation rationale: V13.
  - No Node at runtime: V03 and V13.
  - "M6 local work can proceed alongside M2/M3 after M1; hosted links wait for M2" is reflected in the V03 and V10 gates and in line 9.
- **C06 intake coverage.** The #181 transfer row and the Slice C C06 section are covered as follows:
  - Versioned shared view: V05.
  - Refresh trigger and freshness: V09/V10.
  - Direct/descendant Actual, elapsed, owner wait, working wall time and independent watermarks: V05.
  - Offline fallback: V10 bullet 3 and V13.
  - Pinned replay over old seed and C01 views: V11 bullet 1, through the #227 fixtures that carry the #181 C01 seed.
  - Separate timing and Cost parity: V11/V12.
- **Discuss contract.** V08's gate ("Supported released Discuss CLI") resolves to a real producer: Core plan line 116 assigns `discuss` to C18. C18 emits context and a suggested command only, with no model or process launch. That matches V08 bullet 2.
- **Preview carry-forward.** V01/V02 preserve the reviewed preview plan's semantics:
  - pinned rebuild with the shipped reader;
  - reason precedence and empty-reason mapping;
  - pinned verification blob bound to metric, scope and digest, with forged, transplanted and future evidence rejected;
  - #209 kept in the input audit only;
  - 1,208 ms counted once, which matches the pilot readback JSON;
  - atomic content-addressed bundle with a serialized last-valid pointer;
  - preserved `make dashboard`.
- **#230 cycle.** Lines 39–41 correctly state the conditional cycle: #100 completion → #230 → Core #51 → the #100/#133 gate on Core children. The section holds V12/V13 without changing native graphs. V11's alternative #228/#229 gate correctly avoids an AND block.
- **Path overlaps.** V03 owns `src/aitm_viewer/`, and V05 writes `metric_view.py` inside it. That overlap is ordered through V03 → V04 → V05. V09 and V10 share `.github/workflows/viewer-preview.yml` and are ordered V09 → V10. V05–V08 use disjoint feature directories. Shared shell changes such as `app.ts`, `package.json` and the local server are routed back to JIT (line 11).

## Findings

### R1-F001 — Medium — V02 → V05 places the bootstrap preview on the formal critical path without saying what V05 inherits

**Location:** table line 27 (V05 predecessors "V02, V04"), lines 9, 23–24 and 37, and V05 bullet 2 (line 82).

**Problem.** Line 9 frames V01/V02 as the carried-forward *pre-M1 bootstrap option*. Line 37 describes "the formal local chain" as V03 → V04 and calls V01 → V02 "the bootstrap chain". However, the native graph makes V02 a hard predecessor of V05. V05 blocks V09, V11 and V12, so it transitively blocks V10 and V13. As a result, every hosted, parity and release leaf waits on delivery of `tools/story_dashboard` bootstrap tooling built on the legacy shipped reader.

The artifact never says which delivered output of V02 V05 consumes. V05 bullet 2 says V05 "own[s] the versioned approved metric view over the released Core export" and "preserve[s] the preview semantics". That reads as a new contract sourced from Core, not as reuse of V01/V02's versioned preview view. The coverage design (line 37: "Keep the bundled view versioned so the SPA can reuse it") implies reuse of the preview view schema. The two readings lead to different JIT scopes:

- Does V05 extend the V01 preview schema version, or define a separate product view?
- Does V05 consume the V02 #139 before/after and synthetic fixtures, or only the reviewed semantics in the preview plan document?

**Effect.**

- A V05 JIT author cannot tell whether the product metric view must stay backward-compatible with the V02 bundle's versioned JSON. The M2 readback comparison and V11/V12 parity both depend on one view contract.
- The edge has no stated basis for reconciliation. Suppose the owner never records early-bootstrap authorization, and after M1/C6 decides that a legacy-reader preview is superseded by V03–V05. The formal viewer then stays natively blocked by a leaf whose value is gone. The artifact gives no criterion for whether dropping or retargeting the edge preserves required scope. Line 151 requires reconciliation and new review for such a change, which needs a stated rationale to evaluate against.
- Readers of line 37 may assume the formal chain is independent of the bootstrap. They will find out only from the table that it is not.

**Closure criteria.** The artifact states, in the V05 row or leaf detail and in the line 37 narrative:

- (a) the concrete V02 outputs V05 consumes. For example: the versioned preview view schema and its version-compatibility rule, the controlled reason-code and precedence table, and the pinned #139 and synthetic fixtures as regression inputs.
- (b) whether the product metric view is a new version of the same contract or a separate contract that maps to it.
- (c) that the formal chain therefore includes V01 → V02. Alternatively, if only the reviewed semantics are needed, the artifact states that the dependency is on the reviewed preview plan and fixtures rather than on V02 delivery, and reconciles the native edge to match.

## Required changes

1. **R1-F001:** State what V05 inherits from V02 (schema/version compatibility, reason-code table, fixtures). Say whether the product view extends or replaces the preview contract. Make line 37 consistent with the V02 → V05 edge, or replace the edge with a reference to the reviewed plan and fixtures and reconcile the native graph and receipt.

## Optional suggestions

1. **V08 gate (line 30).** Name the producer explicitly, for example "released Core C18 `discuss` context/command contract (M1)". The core plan already assigns `discuss` to C18 (core plan line 116). The alternative "owning harness context handoff contract" currently has no named owner.
2. **Framework choice.** The graduated draft lists "Framework choice" as Open, and no leaf names it. Consider assigning it to the V03 JIT, with the rationale captured for V13's tutorial, so that V04–V08 do not each infer it.
3. **Live local data.** The draft says the local viewer "reads the SQLite index for live data while agents work". V03/V04 specify one consistent snapshot plus freshness disclosure. Consider stating at V03 JIT whether the local viewer refreshes (reload or poll) or stays snapshot-per-load, so the freshness indicator semantics are defined before V04.
4. **V01 file layout (line 47).** The reviewed preview plan's Leaf A defines `build_preview(...)` in `preview.py` with `test_preview.py` and a fixed unittest command. The decomposition proposes `preview_data.py` / `test_preview_data.py`. The paths are only "candidate paths", but the V01 JIT should explicitly reconcile with, or knowingly depart from, the reviewed plan's named function, files and test command.
5. **V05 size (lines 79–83).** V05 combines a Python metric-view contract, TypeScript rendering and a broad proof matrix at 3.75 h. Its proof matrix covers parallel actors, in-turn tools, scope changes, missing usage, stale evidence and estimate scope. Flag it as the likeliest leaf to exceed 4 h at JIT, with a pre-identified split of view contract versus UI.
6. **Redundant edges.** V05 → V11, V05 → V12 and V10 → V13 are transitively implied. Keeping them explicit is fine. If they are ever pruned, the "19 edges" count and the receipt must change together.
7. **Workflow name.** V10 publishes real data through `.github/workflows/viewer-preview.yml`. A name that does not say "preview" for the production route may avoid confusion with the bootstrap preview's manual build.

## Decision

revisions-requested
