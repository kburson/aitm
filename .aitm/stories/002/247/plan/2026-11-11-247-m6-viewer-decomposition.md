# #247 M6 Viewer backlog decomposition

**Goal.** Deliver the read-only preview and the M6 product viewer with a local experience, a static hosted experience, and verified timing and Cost evidence for the supported scopes.

**Inputs.** [Product master plan](../../../000/1/plan/master-plan.md), [accepted product architecture](../../../000/1/design/architecture.md), [graduated M6 draft](../draft.md), [reviewed preview plan](../attachments/2026-11-11-1-m6-read-only-preview-plan.md), [preview review](../attachments/2026-11-11-1-m6-read-only-preview-plan-review.md), [#139 pilot](../attachments/2026-11-11-139-m6-timing-pilot.md), and [#181 production handoff](https://github.com/kburson/aitm/blob/456207d741affff4b6b97530af8977f63ad48898/.aitm/stories/001/181/attachments/2026-11-11-production-scope-transfer.md).

## Boundaries and architecture

M6 is a child of #1. #100 and #133 remain prerequisites of #2. M6 uses only the published M1 release and index/schema contracts for its formal product implementation. V01 and V02 carry forward the reviewed pre-M1 bootstrap option. An early pickup would need separate sequencing authorization as well as accepted JIT plans. This hydration establishes Backlog scope only. The formal M6 local path may run alongside M2 and M3 after M1; hosted issue links and board parity require the delivered M2 contracts. Keep native timing qualification and priced usage separate so either can be verified in its own scope.

The bootstrap reuses the shipped Python dashboard reader and validated evidence. V01 owns the pure preview projection and V02 owns the CLI and bundle. The production viewer uses TypeScript generated from released Core JSON Schema, a prebuilt local package without Node at runtime, and static hosting from a pinned sanitized export. The V03 contract and V04 shell expose stable view entry points for V05–V08. Each later leaf writes its own feature module and test; any required shared shell changes return to JIT for serialized ownership. No viewer-owned timing capture, cost computation, board writer, new hosted backend or migration is part of M6.

The first preview ends at a verified downloadable bundle. V09 separately qualifies a manual default-branch refresh with synthetic inputs. V10 verifies an authorized GitHub Pages route and audience at pickup; a recurring trigger requires the agreed freshness target and verified last-valid behavior. A deployment never assumes a planning push can run trunk workflows. Real hosted links use the M2 contract. Current authorized local work continues through the shipped dashboard path.

The leaf estimates are implementation agent-hours including local verification and independent source review. Planning and waiting are tracked separately. Each item requires an accepted JIT implementation plan at pickup, with applicable Design and Plan acceptance, current prerequisites, source pin, scope, file ownership, tests, likely defects and a refreshed estimate of four hours or less. Native Backlog status and this epic review do not move any item into Develop.

## Backlog and execution graph

The native graph represents required M6 predecessors. External release, provider, approved audience and alternative-path gates are declared per leaf. Verify each at JIT against delivered evidence. Do not add an AND block for the #228/#229 alternative. Add M2 issue linkage when its owning milestone graduates. Parent and dependency mirrors inside M6 are recorded in the story store. The receipt records preliminary issue-body estimates. AITM-PY Estimate remains unset until independently reviewed item pickup establishes the JIT estimate.

| Key | Issue | Hours | Internal predecessors | External pickup gate |
| --- | --- | ---: | --- | --- |
| V01 | [#249](https://github.com/kburson/aitm/issues/249) | 3 | — | Formal M6 after M1 release #72. An early bootstrap requires separately recorded sequencing authorization at pickup. |
| V02 | [#248](https://github.com/kburson/aitm/issues/248) | 3 | V01 | Same sequencing as V01. Local and downloadable preview only. |
| V03 | [#250](https://github.com/kburson/aitm/issues/250) | 3.75 | — | M1 released Core #72, versioned index/read/export contracts and installed consumer support. |
| V04 | [#251](https://github.com/kburson/aitm/issues/251) | 3.5 | V03 | Released Core story and hierarchy export through V03. |
| V05 | [#252](https://github.com/kburson/aitm/issues/252) | 3.75 | V02, V04 | The UI can be qualified with safe fixtures and unavailable states. Live timing and Cost are qualified by V11 and V12. |
| V06 | [#253](https://github.com/kburson/aitm/issues/253) | 3 | V04 | Released workflow and event export with pinned source scope. |
| V07 | [#254](https://github.com/kburson/aitm/issues/254) | 3.25 | V04 | Released safe document and outcome references; display missing or unapproved content as such. |
| V08 | [#255](https://github.com/kburson/aitm/issues/255) | 2.5 | V04 | Supported released Discuss CLI or owning harness context handoff contract at JIT. |
| V09 | [#256](https://github.com/kburson/aitm/issues/256) | 3.75 | V05, V06, V07, V08 | Use an explicitly authorized synthetic route at JIT. No real-data destination or hosted issue-link claim. |
| V10 | [#258](https://github.com/kburson/aitm/issues/258) | 3.5 | V09 | Delivered M2 hosted issue-link contract, authorized GitHub Pages audience/route and current refresh target. Board parity remains V11 and V12. |
| V11 | [#257](https://github.com/kburson/aitm/issues/257) | 3.5 | V05, V10 | Supported timing scope from #229 (native) or #228 (legacy), plus M2 field/readback contract. Declare supported path at JIT; an unselected path remains explicitly unsupported. |
| V12 | [#259](https://github.com/kburson/aitm/issues/259) | 3.5 | V05, V10 | Qualified #230, including #123/#124 and Core #51, plus M2 Cost field/readback contract and authorized scope. Resolve #100 completion accounting for the post-Core #230 follow-up with the owner first. |
| V13 | [#260](https://github.com/kburson/aitm/issues/260) | 3.5 | V10, V11, V12 | Applicable supported hosted and local scope, exact released package dependencies and aggregate verification. |

Total **43.5 implementation agent-hours** across **13** leaves and **19** internal dependency edges. V01 → V02 is the bootstrap chain. The formal local chain starts at V03 after released M1, then V04. V05–V08 may work on disjoint feature paths once their predecessors and pickup gates pass. V09 integrates the local features before V10 qualifies real-data hosting. V11 and V12 then qualify separate metric scopes. V13 is the aggregate release and tutorial gate.

## Open dependency affecting Cost and release

#230 is a post-Core follow-up under #100 and depends on Core #51. The owner gates every Core child on completion of #100 and #133. If #100 completion includes #230, those conditions form a cycle. At planning review there is no verified owner decision that excludes #230 from #100's completion or moves it to another owner. V12 and V13 therefore remain held for Cost and release until the owner records the #100 completion boundary or rehomes the post-Core follow-up and the normal prerequisites are satisfied. This does not authorize work on a Core child or change the native #100 or #2 graphs.

## Leaf details

### V01 #249

**Build the pinned read-only preview data.** 3 h. **Candidate paths:** `tools/story_dashboard/preview_data.py`, `tools/story_dashboard/tests/test_preview_data.py`.

- [ ] Rebuild from the exact Git planning pin and cutoff with the shipped reader. Verify snapshot and validation bytes and produce a versioned allowlisted view with source and build provenance.
- [ ] Map Unknown, Partial, verified zero, empty reasons, and source admission. Enforce visibility profile, approved values, restricted descendant rollups, and pricing basis. Record evidence through separately from last verified.
- [ ] Trust only pinned operator verification blobs bound to the exact metric, scope and digest. Reproduce the single #139 1,208 ms contribution and exact Actual and working wall verification timestamps. Preserve each source value, coverage, reason and evidence-through time, and leave last verified null without matching verification. Report #209 only in the input audit. Reject forged, transplanted or future evidence.

### V02 #248

**Render and qualify the downloadable preview bundle.** 3 h. **Candidate paths:** `tools/story_dashboard/preview.py`, `tools/story_dashboard/preview.html`, `tools/story_dashboard/tests/test_preview_bundle.py`, `tools/story_dashboard/README.md`.

- [ ] Render sanitized JSON and standalone HTML from the same approved object. Show primary and detailed reasons, evidence-through UTC, last verified UTC, publication time, pin, pending waits and staleness.
- [ ] Validate an atomic content-addressed bundle and serialized last-valid pointer. Cover reversed completion, stale lineage/cutoff, incomparable scope profiles, partial writes, replay and prior bundle retention.
- [ ] Rebuild the pinned #139 before/after and synthetic fixtures. Verify browser pin and manifest digest separately, check redaction canaries across outputs and diagnostics, and preserve make dashboard.

### V03 #250

**Consume released Core exports and serve the local viewer.** 3.75 h. **Candidate paths:** `packages/aitm-viewer/pyproject.toml`, `packages/aitm-viewer/src/aitm_viewer/`, `packages/aitm-viewer/web/package.json`, `packages/aitm-viewer/web/src/contracts/`, `packages/aitm-viewer/tests/test_local_export.py`.

- [ ] Pin a released Core export, generate TypeScript types from its JSON Schema and test supported/unsupported versions and malformed input.
- [ ] Read one consistent local index snapshot through the supported interface. Package a static viewer shell and expose a loopback-only local entry point through the released extension API without Node at runtime.
- [ ] Verify a clean install, schema mismatch and missing data failures, local origin isolation, and reproducible export by pin. Establish viewer build checks required by repository policy before product TypeScript delivery.

### V04 #251

**Show story progress, hierarchy and detail.** 3.5 h. **Candidate paths:** `packages/aitm-viewer/web/src/story/`, `packages/aitm-viewer/web/src/app.ts`, `packages/aitm-viewer/web/tests/story.test.ts`.

- [ ] Render a board-style progress view, state and parent/child navigation from the exported story graph. Support project/epic, lifecycle and coverage filters. Distinguish a current local index view from a hosted snapshot and expose its freshness.
- [ ] Use an explicit empty, partial, orphaned or held view when ancestry or source evidence is missing. Filter and navigate consistently at desktop and narrow widths.
- [ ] Prove linked story identity, no leakage through excluded descendants, readable details, accessible keyboard navigation and no state changes from the viewer.

### V05 #252

**Show timing, Cost and evidence coverage in the local viewer.** 3.75 h. **Candidate paths:** `packages/aitm-viewer/src/aitm_viewer/metric_view.py`, `packages/aitm-viewer/web/src/metrics/`, `packages/aitm-viewer/web/tests/metrics.test.ts`.

- [ ] Present Actual, elapsed, owner wait, working wall time, direct/descendant totals and Cost with independent value, coverage, reason, basis and source/verification times.
- [ ] Own the versioned approved metric view over the released Core export. Produce the same pinned metric payload for the local viewer, hosted build and M2 readback comparison, with independent timing and usage watermarks. Preserve the preview semantics without introducing a second timing or pricing fold. Show Unknown, supported Partial and verified zero, and label pricing basis.
- [ ] Prove parallel actors, in-turn tools, scope changes, missing usage, stale evidence and exact estimate scope. Keep Partial or Unknown outside calibration.

### V06 #253

**Show workflow flow history.** 3 h. **Candidate paths:** `packages/aitm-viewer/web/src/flow/`, `packages/aitm-viewer/web/tests/flow.test.ts`.

- [ ] Show cumulative flow, cycle time per state, lead time, transition paths and loopbacks for the selected project and period.
- [ ] Distinguish open intervals, phase changes, rework, missing events and scope exclusions. Do not infer duration or state from unverified timing.
- [ ] Prove deterministic ordering, open and completed paths, multiple attempts, empty results and missing history.

### V07 #254

**Show evidence summaries, bumps and retrospectives.** 3.25 h. **Candidate paths:** `packages/aitm-viewer/web/src/evidence/`, `packages/aitm-viewer/web/tests/evidence.test.ts`.

- [ ] Expose sourced design and plan summaries, fixed links to the approved full design and plan documents, bumps, lessons, retrospectives and advisory confidence from supported read-only exports.
- [ ] Use approved summary values and fixed provenance links, enforce visibility scope and handle unapproved or absent material without exposing private content.
- [ ] Test hostile or unavailable document inputs, revision provenance, current versus historical artifacts and accessible disclosure.

### V08 #255

**Add a read-only Discuss handoff.** 2.5 h. **Candidate paths:** `packages/aitm-viewer/web/src/discuss/`, `packages/aitm-viewer/web/tests/discuss.test.ts`.

- [ ] Offer a copyable supported Discuss handoff for an admitted story and applicable historical context. Preserve the exact story scope and fail clearly when unsupported.
- [ ] The viewer generates an authorized command or link through the supported contract. It does not start a conversation, execute a shell or send story context on click.
- [ ] Test unavailable provider or story, safe argument handling, privacy and keyboard access.

### V09 #256

**Qualify a static hosted build with synthetic data.** 3.75 h. **Candidate paths:** `.github/workflows/viewer-preview.yml`, `packages/aitm-viewer/hosting/build.py`, `packages/aitm-viewer/tests/test_hosted_build.py`.

- [ ] Build the complete static viewer from a pinned safe fixture. Select and qualify a default-branch manual dispatch; evaluate recurring refresh as a separate behavior using measured latency and a declared freshness target.
- [ ] Verify that a failed, superseded or stale build retains the last valid artifact. Prove origin, manifest, browser digest, pin, visibility profile and anonymous-access behavior on the authorized synthetic route.
- [ ] Keep workflow code on trunk and distinguish viewer refresh from the separate every-push planning audit.

### V10 #258

**Qualify real-data GitHub Pages hosting and issue links.** 3.5 h. **Candidate paths:** `.github/workflows/viewer-preview.yml`, `packages/aitm-viewer/hosting/publish.py`, `packages/aitm-viewer/tests/test_hosted_publish.py`.

- [ ] Publish only the approved view to the authorized GitHub Pages route for approved public data. Prove allowlisted data, link authority, permissions and authorized browser readback for the published pin and digest. For a restricted audience, qualify an authenticated route after a reviewed routing decision. An alternate formal public target requires a reviewed change to the M6 scope.
- [ ] Exercise recurring or dispatched refresh, stale indicators, last-known-good recovery and independent verification of origins and alternate access routes.
- [ ] Qualify on the approved scope; verify restricted or public policy as applicable and keep the local viewer available.

### V11 #257

**Qualify timing replay and board-to-view parity.** 3.5 h. **Candidate paths:** `packages/aitm-viewer/tests/test_timing_parity.py`, `packages/aitm-viewer/docs/timing-parity.md`.

- [ ] Compare direct, descendant and inclusive Actual and wait/elapsed scope against the same pinned approved view and verified board values. Include #227 shared fixtures and #139 pilot as preserved historical inputs.
- [ ] Verify independent timing freshness when usage is absent, scoped unsupported evidence, exact decimal board rounding and live authorized readback. Keep pricing outside timing parity.
- [ ] Prove stable pinned replay and document differences attributable to scope or watermark.

### V12 #259

**Qualify priced Cost replay and board-to-view parity.** 3.5 h. **Candidate paths:** `packages/aitm-viewer/tests/test_cost_parity.py`, `packages/aitm-viewer/docs/cost-parity.md`.

- [ ] Verify the pinned pricing report, rate basis, cutoff, scope and independent usage watermark against the same approved viewer and board publication.
- [ ] Prove verified priced subtotal with Partial coverage in the viewer, held board projection for incomplete price, replay, later usage refresh, and no effect on timing.
- [ ] Retain real-data authorized readback and provenance without raw provider evidence in the hosted bundle.

### V13 #260

**Qualify M6 release and publish the viewer tutorial.** 3.5 h. **Candidate paths:** `docs/learn/aitm-viewer.md`, `packages/aitm-viewer/tests/test_release_viewer.py`.

- [ ] Qualify and release the separately installable aitm-viewer distribution through the approved package delivery route at pickup. Pin exact released Core and any required extension versions. Exercise clean install, prebuilt static assets, offline fallback and latest hosted readback.
- [ ] Publish the operator tutorial and TypeScript/schema-generation rationale. Cover refresh, missing data, supported timing/price scope and Discuss.
- [ ] Retain exact reviewed source, distribution digest, release identity and aggregate verification. Keep the milestone's eventual completion with its owner.

## Aggregate review and evidence

Verify each master outcome is represented, every leaf has a testable positive and failure case, and every path overlap is ordered or assigned to a separate JIT conflict resolution. Read back the native parent, exact internal blockers, reciprocal links, estimate and Backlog status. Prove the graph is acyclic. Check #2's existing #100/#133 blockers and preserve their scope. Bind review acceptance to the final complete decomposition bytes, including revisions. Confirm that the candidate leaves and publication receipt match the accepted table. A later edit to scope or dependencies requires reconciliation and the applicable new review.
