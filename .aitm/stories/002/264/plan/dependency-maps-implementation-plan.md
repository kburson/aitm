# #264 Epic Dependency Maps Implementation Plan

> Execution requires accepted Design and Plan plus the applicable item-specific JIT review. Use superpowers:subagent-driven-development or superpowers:executing-plans when execution is authorized.

**Goal.** Produce reviewable maps from pinned planning commits and let viewer users trace declared dependencies from an epic or a story.

**Architecture.** The Python command reads pinned Git planning data. The TypeScript viewer reads the released Core export through #250. Each adapter admits data before graph construction and feeds its own implementation of the same graph rules. Shared fixtures define the expected graph and audit results.

**Tech stack.** Python 3.13, Git, Graphviz `dot`, Mermaid Markdown, and the released viewer's TypeScript build and test stack.

**Spec.** [#264 design](../design/dependency-maps.md), SHA-256 `50a78e6dadb7e2058ae477b98c04f4775c59942960ecc25c5a66dd17a9aa16e7`. [Story #264](../story.md) is a linked follow-on to #247 outside the accepted M6 release.

## Scope and pickup gates

| Slice | Predecessor | Delivery and pickup gate | Preliminary agent hours |
| --- | --- | --- | ---: |
| D1 | — | Python pinned source and admission. Check the installed Git reader and approved profile contract at pickup. | 3.75 |
| D2 | D1 | Shared conformance fixtures and Python projection. | 3.75 |
| D3 | D2 | Static CLI, renderers, and complete bundle output. | 3.75 |
| D4 | D3 | Static qualification and backlog attachment instructions. | 2.50 |
| D5 | D2 | TypeScript projection and parity. Requires the released Core export, #250 and #251, and the viewer TypeScript CI baseline. | 3.75 |
| D6a | D5 | Viewer exploration model. | 2.75 |
| D6b | D6a | Graph, selected-story details, and accessible text view. | 3.75 |
| D7 | D6b | Viewer refresh integration and local package qualification. | 3.75 |
| D8 | D7 | Hosted qualification for this follow-on. Requires the applicable #258 hosting and M2 issue-link contracts, approved audience and route, and the release identity for the add-on. | 3.00 |

D1–D4 can qualify the static deliverable without a viewer runtime. Record any early static pickup and its sequencing authorization at JIT. D5–D7 qualify the local viewer deliverable independently of hosting. D8 qualifies only the follow-on's hosted delivery. Current M6 release dependencies and its 13-item completion scope remain as accepted. The estimates are planning inputs. Confirm source, ownership, prerequisites, and each leaf's estimate at pickup, and split work that exceeds four agent-hours. The temporary local reference tool is useful as comparison evidence. Its code is outside the product plan.

The viewer work starts from the released integration points. #72, #250, #251 and #258 were open at the plan's planning readback. At D5 pickup, inspect the released schema for stable story ID, direct blocker IDs, containment, lifecycle state and provenance, and visibility and directional coverage. If the contract lacks a required field, record the gap with its owner and hold the viewer slice until an approved released contract supplies it. Use the existing viewer toolchain and qualify any build or shell integration changes under that package's normal checks.

## Shared contract and review focus

- A snapshot carries the source pin, UTC lifecycle cutoff, versioned visibility profile and digest, allowed records and per-direction coverage. The static adapter uses the exact commit's UTC committer timestamp. A public or attached bundle requires the owning project's admitted projection and a source pin visible to its audience. `private-local-v1` is the explicit private reference profile.
- The projection exposes child nodes, declared edges, displayed internal edges, boundary links and explicit epic gates, omitted-edge witnesses, directional coverage, and approved links. A declared edge is a numeric pair ordered prerequisite first. An optional containing child epic identifies a nested boundary endpoint. A missing lifecycle state displays Unknown. The static bundle shows lifecycle state. Viewer detail may show readiness from the released story detail contract when coverage permits.
- Coverage distinguishes complete, partial, and restricted where disclosure is permitted. Hold for a missing selected epic or expected admitted child, an unreadable required declaration, or invalid admitted containment. An unreadable external direction permits a partial view with its valid declarations, including a known allowed unresolved link. An incomplete direction with zero known links never reads as verified empty. Withhold affirmative readiness when coverage is insufficient, including any readiness value from Core. Counts, source links, labels, diagnostics and witnesses are computed from the admitted input.
- Validate exact admitted edges touching the selected epic or a direct child before reduction, including boundary links and explicit gates. A detected cycle in that scope holds replacement. A chain through external records beyond the admitted incident edges is outside this validation claim. The parent overview states its direct-child scope. Edges touching neither a direct child nor the selected epic stay in their own maps.
- Reduce internal edges between direct children. For each omitted edge, choose the shortest path in the final displayed internal graph. Compare equal-length paths lexicographically by their ordered numeric story IDs. Boundary links and explicit gates cannot supply a witness. Collapse or filtering recomputes internal display edges over the visible endpoints. Restore a declaration if its visible witness disappears. Text and detail can explain an admitted path through hidden nodes when no declaration joins the visible endpoints.

The review should check five failure cases covered by the slices below. Legacy or conflicting story IDs can break the source index (D1). A restricted intermediate or boundary edge can produce a false witness (D2 and D5). A render or write failure can expose a mixed bundle (D3). Collapse can remove a shared or focused node incorrectly (D6). A late refresh can restore data for the wrong visibility context (D7).

## D1. Read and admit one pinned planning snapshot

**Files.** Add `tools/story_dashboard/dependency_source.py` and `tools/story_dashboard/tests/test_dependency_source.py`. Reuse the pinned Git reader and lifecycle fold in `tools/story_dashboard/evidence.py`. Add an opt-in record location map at the `_facts` read seam. Resolve the unique story directory by matching the numeric path ID to the header ID, including the historical `.aitm/stories/001/201/story.md` layout for a story whose canonical bucket is `002`. Accept only regular bounded blobs in the recognized numeric story layout. Use the actual directory's sibling journal for the same lifecycle fold. The dependency adapter opts into `_header` capture of `blocked-by` and `blocking` with the existing duplicate-key rejection and eligibility cutoff. Existing callers keep canonical lookup and their current header field set. Pass raw field validity and containment claims with the resolved parent map and gaps. The resolved parent from eligible evidence governs containment. A stale child claim superseded by a valid parent change cannot resurrect a child.

**Interfaces.** `load_dependency_profile(repo, commit, key, destination) -> Profile` loads `private-local-v1` or the pinned approved allowlist for the owning project. Store project profiles under `.aitm/visibility/dependency-map-profiles/<versioned-key>.json` with admitted story IDs, approved display titles, allowed fields and links, source pin visibility, destination, and approval reference. Record the raw profile SHA-256. At pickup verify how the owning planning project records approval and binds it to the exact profile digest. Hold attachment generation without that binding. The built-in profile admits all readable story records at the pin, uses a fixed versioned definition and digest, and is ineligible for attachment.

`read_dependency_snapshot(repo, commit, profile) -> AdmittedSnapshot` returns indexed story records, declared blockers and reverse fields, lifecycle state with provenance, and admitted coverage from one commit. Reject invalid hashes and non-commit objects. Read supported historical record locations by identity and flag conflicts so D2 can reject an expected child or mark an unreadable external record. The dependent's `blocked-by` supplies each declaration. Reverse fields report disagreements.

| Source condition | Selected epic or expected admitted child | Boundary record or scan |
| --- | --- | --- |
| Missing, conflicting ID, `future-story`, `invalid-story`, `ineligible-header`, or unreadable required `blocked-by` | Hold. Preserve the distinction between empty and unavailable. | Mark the affected direction partial. Keep known allowed declarations. |
| `invalid-ancestry`, `ancestry-conflict`, `ancestry-missing`, or `ancestry-cycle` affecting required containment | Hold if resolved containment is missing or inconsistent. Use a valid resolved parent when it supersedes an older claim. | Mark partial when the gap prevents boundary classification. |
| `invalid-state`, `missing-journal`, `invalid-journal`, or `invalid-event` | Preserve the existing eligible lifecycle fold when it provides trustworthy state. Show Unknown when it cannot. Hold only if required containment or declaration data is invalid. | Apply the same lifecycle rule. Preserve valid edges. |
| `future-event` or `unbound-draft-event` | Exclude the event under the existing reader rules. | Apply the same cutoff. |
| Unreadable reverse field, estimate or receipt gap | Keep authoritative declarations. Report allowed reverse-field gaps in the audit. Estimates and receipts are outside the graph input. | Apply the same rule and suppress excluded identities. |

- [ ] Add `test_dependency_source_replays_plan_to_develop`, `test_dependency_source_indexes_historical_ids`, `test_dependency_source_admits_before_reporting`, and `test_profile_checks_pinned_approval_and_destination`. Use temporary Git repositories in the unit suite. Reproduce the lifecycle transition, one identity per historical record, and no excluded IDs in outputs or errors. Exercise conflicting IDs, invalid input, unreadable required child declaration, unreadable external record, incomplete scan, unresolved link, unavailable or mismatched profile approval, and unauthorized destination. D4 runs the actual #133 pins.
- [ ] Implement the snapshot adapter and verify with `python3.13 -m unittest discover -s tools/story_dashboard/tests -p 'test_dependency_source.py'`. Run the existing lifecycle evidence tests with the same discovery command and `test_evidence.py` as the pattern.

## D2. Define fixtures and build the Python projection

**Files.** Add `tools/story_dashboard/dependency_graph.py`, `tools/story_dashboard/tests/test_dependency_graph.py`, the Git fixture loader `tools/story_dashboard/tests/dependency_fixture.py`, and shared JSON cases in `tools/story_dashboard/tests/fixtures/dependency-maps/`. Each `aitm.dependency-map-fixture/v1` case contains `records` before admission, `profile` (key, allowed records, titles and fields), `epic_id`, `scan_input` (simulated incoming and outgoing completeness and unresolved record conditions), and `expected` admitted nodes, edge classes, audit paths and coverage. Loaders use `scan_input` to reproduce source conditions and compare observed coverage to `expected`. Materialize the logical records, profile and gaps as pinned Git blobs for the Python adapter and as an export fixture at the supported Core policy boundary for the viewer.

**Interface.** `project_dependencies(snapshot, epic_id) -> DependencyMap` validates the admitted incident graph, computes the displayed edge classes and witnesses, and exposes complete declared adjacency to consumers.

- [ ] Add `test_projection_matches_shared_contract`. Include missing expected child, inconsistent containment, a diamond with equal-length witnesses, nested descendant links in both directions, a boundary that cannot witness an internal shortcut, a separate selected-epic gate that survives reduction and cannot supply a witness, a restricted intermediate, a cycle, a known unresolved incoming link, and zero known outgoing links with partial coverage. Include the #227/#193 pattern and a reverse-field reference to an excluded story. Emit allowed disagreements in the audit and check that excluded IDs never appear.
- [ ] Implement projection and drive D1 admission before projection in the restricted fixture. Run `python3.13 -m unittest discover -s tools/story_dashboard/tests -p 'test_dependency_graph.py'`. D4 runs the real #133 count checks.

## D3. Render and write a complete static bundle

**Files.** Add `tools/story_dashboard/dependency_map.py` and `tools/story_dashboard/tests/test_dependency_map_cli.py`.

**Interface.** `python -m tools.story_dashboard.dependency_map --repo REPO --commit SHA --epic ID --output NEW_DIRECTORY --visibility-profile KEY [--attachment-destination DESTINATION]` emits `dependency-map.md`, `dependency-map.svg`, and `dependency-audit.md`. Pass `private-local-v1` for a private reference. An attachment profile requires a destination that matches the pinned profile approval. All three outputs record the full pin, UTC cutoff, key, and profile digest. The command has no issue or publication API.

- [ ] Add `test_cli_bundle_renderers_agree` and `test_cli_keeps_prior_bundle_on_failure`. Compare Mermaid and SVG graph content, assert byte equality for the two Markdown outputs from the same input and generator version, and exercise a render or write failure after output begins. Assert a valid previous bundle still reads byte for byte and the requested replacement path has no partial files. Render the restricted canary through an attachment profile and compare exact Markdown, SVG including metadata and links, audit, and shareable diagnostics against the admitted fixture.
- [ ] Render both graphs top to bottom from the same sorted projection. Align entry stories where the renderer supports it. Stage and validate the three files under the destination's parent, then publish with one atomic directory operation. Use distinct directories for distinct pins or profiles. Reject an occupied destination with different contents. Run `python3.13 -m unittest discover -s tools/story_dashboard/tests -p 'test_dependency_map_cli.py'` with Graphviz available.

## D4. Qualify static output and document attachment

**Files.** Update `tools/story_dashboard/README.md` with the CLI, artifacts, coverage and attachment procedure. Add `tools/story_dashboard/tests/test_dependency_map_replay.py` for the pinned qualification.

- [ ] Rebuild #133 at full pins `05d33307c0164557359cb605e78158fc73d177d5` and `ea4a8384255e6ad8f28c69ffbd54f5399be0e78c`. Assert 41 children, 64 declarations, 55 displayed internal arrows, nine valid witnesses, the separate #133 → #2 gate, and absence of #160 → #162. Confirm #142 Plan → Develop in both views while the edge and audit sets stay fixed. From the source checkout run `python3.13 -m unittest discover -s tools/story_dashboard/tests -p 'test_*.py'`. Run the historical replay with `AITM_DEPENDENCY_REPLAY_REPO=/path/to/planning-repo python3.13 -m unittest discover -s tools/story_dashboard/tests -p 'test_dependency_map_replay.py'` and `dot` on PATH. Verify both Git objects and Graphviz first. An explicitly requested replay fails on missing prerequisites. The hermetic suite may skip the historical replay when it was not requested.
- [ ] Document attachment under the epic's `plan/dependency-maps/<source-planning-commit>/<visibility-profile>/`. Record cutoff, versioned profile key and authorized destination. Check exact Markdown, SVG metadata, audit and shareable diagnostics against that audience before attaching. Replan topology gets a new reviewed bundle. State-only rerenders are on demand. Retain the repository identity, both full pins and the passing replay result with static delivery evidence. A default-suite skip records an unrequested historical replay and cannot qualify D4.

## D5. Adapt the released viewer export and prove parity

**Files.** Add `packages/aitm-viewer/web/src/dependency-map/projection.ts`, `packages/aitm-viewer/web/tests/dependency-map/fixtures.ts` and `packages/aitm-viewer/web/tests/dependency-map/projection.test.ts`. Integrate with the released #250 contract adapter and its generated types at the owning boundary.

**Interface.** `projectDependencyMap(snapshot: AdmittedCoreSnapshot, epicId: StoryId): DependencyMap` is a pure operation over one authorized snapshot. The result carries the same edge classes and audit semantics as D2 plus the source identity and eligible detail links.

- [ ] Verify the released schema against the fields in the pickup gates. Load the canonical D2 fixture files by a repository-relative path resolved from the TypeScript fixture module. Map each logical profile to a released viewer visibility context with the same allowed identities and fields, then build the released export fixture through its owning policy boundary. Exercise the same raw records upstream of admission. Verify the viewer's accepted profile binding. Compare all expected outputs, including the gate, reverse-field audit, directional coverage and withheld readiness. Assert unsupported or incomplete required inputs produce the viewer's unavailable state and incomplete external coverage remains partial.
- [ ] Implement the adapter and projection. Run the released viewer's focused Vitest suite and its ESLint and `tsc --noEmit` checks. Register the shared fixture path with the viewer parity check so each fixture change reruns Python and TypeScript parity after D5. Record the exact Core export version and fixture result.

## D6a. Add the dependency exploration model

**Files.** Add `packages/aitm-viewer/web/src/dependency-map/exploration.ts` and `packages/aitm-viewer/web/tests/dependency-map/exploration.test.ts`.

**Interface.** `buildExploration(map, selection, expansion, filters): VisibleDependencyMap` returns visible nodes, declaration-based display edges, hidden path context and focus targets. A layer is one hop over the admitted declared graph. Traversal stops at boundary links. The existing detail surface consumes direct blockers, directly blocked stories, lifecycle, coverage, witness explanations, and authorized source links from that same snapshot.

- [ ] Add model cases for a diamond with shared nodes, one-hop expansion through a reduced declaration, nested map navigation, collapse and filter restoring a shortcut, and a hidden intermediate with no direct shortcut. Assert a shared node survives collapse while another expanded path reaches it. Implement the pure model and run the viewer's focused Vitest checks.

## D6b. Bind the graph, text view, and details

**Files.** Add `packages/aitm-viewer/web/src/dependency-map/view.ts` and `packages/aitm-viewer/web/tests/dependency-map/view.test.ts`. Bind the approved entry point from the released #251 hierarchy and detail UI and consume the D6a model.

- [ ] Add component checks for pointer and keyboard selection, expanding and collapsing, nested map links, direction and coverage in the text view, and an admitted audit explanation.
- [ ] Add the top-to-bottom graph, text view and existing detail pane. Use deterministic layers and stable story IDs so state-only refresh does not change the selected story. Exercise keyboard access to every graph action, focus recovery to the collapsing control or graph controls, and a narrow layout with details below the graph. Run the viewer component and accessibility checks.

## D7. Integrate viewer refresh and qualify the local package

**Files.** Add `packages/aitm-viewer/web/src/dependency-map/refresh.ts` and `packages/aitm-viewer/web/tests/dependency-map/refresh.test.ts`. Connect to the released viewer refresh lifecycle at its existing owner boundary.

- [ ] Add Vitest cases for older refresh completion and failed refresh after revocation. During an unresolved context change, assert the prior graph, text view, audit context, links, and story details are unavailable. Cover an older completion after a newer one, a failed refresh in the same authorized scope, a visibility change that keeps the selected story, a visibility change that removes it, state-only update, and removal of a focused story. Check that labels, links, details and freshness commit as one snapshot.
- [ ] Apply only the latest eligible completion for the current context. Retain same-context authorized stale data with its own provenance after failure. On any project or visibility transition, replace the entire prior graph, text, audit and detail surface with the viewer's unavailable state until the new context admits a snapshot. Keep only the internal selection key during that transition. Restore selection only if the newly admitted visible graph contains that story. Run the focused refresh tests and the released viewer's full build and test commands. Qualify a clean local package install, one pinned replay, and read-only behavior.

## D8. Qualify hosted delivery for the follow-on

**Files.** Add the feature's cases in `packages/aitm-viewer/tests/test_dependency_map_hosted.py` and the follow-on qualification record in the story's delivery evidence. Integrate with the approved #258 hosting entry point only after route and contract readback.

- [ ] Qualify a synthetic bundle first. Verify the graph, detail, links, audit context, metadata, counts, and diagnostics cannot disclose excluded records. Verify approved origin, pin and freshness with a browser. Simulate a failed or superseded refresh after an audience change. Keep a prior release available only while it is still authorized for the active audience.
- [ ] At pickup, pin the actual follow-on package and authorized hosted release vehicle. Verify #258 route, M2 issue-link rules and audience approval for the added fields. Record exact artifact and publication readback under #264 before claiming hosted delivery. Local delivery evidence stands on its own if the hosted gate is pending.
