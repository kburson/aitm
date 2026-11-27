<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-efbb7e41b341b1d2dac3a40da827d70b"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/2/design/2026-11-26-configured-workflow-amendment-draft.md"
artifact_commit: "27c54333856e11b8453b9f3a09b4458e89c99756"
artifact_blob: "c88410d3418c671cbd5a3f2f25b5f9526696db88"
artifact_digest: "sha256:330c2351403277f8845b6dd162472a7844ba0ac7e944ce60f7dae8f13589a1d5"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:4a404e4d685336b447771b3d5eceaa0ba37b0cc7a6f54d991bd8e177c503acc6"
  identity_source: "runtime"
started_at: "2026-11-27T03:30:37.750Z"
submitted_at: "2026-11-27T03:32:23.967Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed the configured-workflow amendment draft against the current Core design (`core-design.md`, especially the leaf forward chain, "Kind source and bounded splitting", "Terminal representation", "Edges and precedence", "Transition transaction", and the Core guard table at lines 385–428). The direction is sound. The draft moves to a data-driven N-state workflow with registry-owned capabilities. It also states that configuration grants no write authority, that Core validates structural obligations against the resolved graph, that provisioning happens at pickup, and that closeout is owned by Review. The capability tables are specific and mostly consistent with Core's admission and dispatch contracts.

Some gaps should be closed before the owner treats this as an amendment. The workflow model still finds the terminal state by array position, which contradicts its own rule against ordinal semantics, and it leaves reopen and non-delivery destinations unbound. Dev-entry provisioning conflicts with the integration-story ordering. The draft does not list which Core design statements it supersedes, so the Design state now contradicts Core's Backlog-exit design guard, its design-rework edge, and its split route. Advisory mode is not addressed. Review now has pre-merge and post-merge phases, but the draft does not define which recovery operations are admissible after delivery.

## Findings

1. **Major: terminal state and some recovery destinations rely on position or stay unbound.** The draft says "Core's atomic hooks ... do not infer lifecycle semantics from a label or ordinal position", but it also says "Done has no ordinary outgoing edge because it is the last state". Nothing in the TOML marks `done` as terminal. The `[recovery]` table binds `design_rework`, `implementation_rework`, `trip` and `scope_pivot`. It does not bind:
   - the destination for Core's non-delivery operations (abandon, supersede, duplicate, and the advisory `unverified` disposition), which per Core may close "any nonterminal story";
   - the reopen destinations, which the draft says route "to Design or Plan as required by its evidence invalidation" without saying which configured state IDs those are.

   Scenario: a project appends a `parking` state after `done`, or uses a different terminal ID. The validator then cannot tell which state carries dispositions or where `abandon` and reopen land, except by position or label. That is exactly what the draft forbids.

2. **Major: integration-story provisioning conflicts with Dev-entry attempt and clock start.** Provisioning now runs only in `core.dev.prepare-binding` on the Plan→Dev edge, and "Start the implementation attempt and its applicable clock when Dev entry commits." For a branch-backed epic, the integration story must provision its branch and upstream draft "before admitting dependent child pickup", and it "must wait for child deliveries to complete its own work." So the integration story must enter Dev, starting its attempt and clock, and then sit in Dev while children are planned, implemented, reviewed and merged. That can take far longer than the four-agent-hour leaf limit and its trip accounting. The draft gives no provisioning-only route, no clock-paused waiting condition, and no rule saying that time spent waiting on children is not qualifying activity. Without one of these, the ordering the draft introduces either forces spurious trips or makes children wait on an integration story that cannot safely enter Dev.

3. **Major: the Core design statements that this draft supersedes are not listed, and several now contradict it.** The draft says it "amends the lifecycle and capability composition in the Core design". It does not reconcile these specific statements:
   - Leaf forward chain `backlog → refine → ready-for-plan → plan → develop → test → review → done` (core-design.md:385). The new chain adds Design and removes Develop and Test.
   - Backlog exit `design-accepted` (core-design.md:420, and "every decomposed leaf needs its own authored design accepted ... before verified Backlog exit", :397). The new profile moves design acceptance to Design exit, and Backlog exit now checks only `description-complete`.
   - "Design rework may move Refine/Ready/Plan to Backlog" (:403), while the profile sets `design_rework = "design"`.
   - The split route records "a Refine→Backlog recovery transition" and requires a new accepted aggregate design (:389). The draft does not say whether split now routes to Design, nor that the Plan/JIT oversized path "first takes the existing design-rework edge to Backlog" (:391).
   - "Implementation rework moves Test/Review to Develop" (:403) and the Develop/Test rows of the guard table (:425–427). For example, `story-commits / expansion-resolved` at Develop exit has no counterpart in `core.dev.review-candidate-current`, so the draft does not say whether the expansion-resolved check survives.

   Readers of either document will get contradictory contracts for the same transitions.

4. **Medium: enforce and advisory modes are not addressed.** Core's transition transaction distinguishes enforce from advisory: advisory may advance with failed workflow guards and record an `unverified` disposition, while integrity and edge legality still apply. The draft introduces structural obligations ("A profile with a structural bypass is invalid"), new capability result types (pass, blocked, unavailable), and an "unavailable" status for missing providers. It does not say how each result behaves in advisory mode. Two questions are left open: whether `unavailable` is treated like a failed guard (recordable and advanceable) or always refuses, and whether structural-obligation operations such as attempt start, merge, and finalization are integrity rules that advisory cannot skip.

5. **Medium: Review revalidation after target movement is under-specified and risks livelock.** The draft says "If HEAD or target moves while Review is active, the engine reconciles ... and requires revalidation in Dev before the new candidate can be reviewed or merged." `core.pr.merge-and-verify` requires the "exact approved head/base/tree and target." On an active trunk, every unrelated trunk advance would bounce a story from Review back to Dev and then require a fresh XPR. The draft does not say:
   - which target movements invalidate the review verdict and which invalidate only CI;
   - whether a rebase or update counts as an "approved transformation";
   - whether re-review can be scoped to the delta.

   Without that, a busy target can keep stories from ever merging.

6. **Medium: recovery admissibility in post-delivery Review is undefined.** Review now spans pre-merge and post-merge (closeout) work, and "pending merge or paperwork stays visible in Review, including after restart." The rework edge says it "cannot ... unwind a delivered attempt". The draft does not say whether trip, scope pivot, design rework, or abandon/supersede/duplicate are refused, or handled some other way, once verified delivery exists but Review is still current. Scenario: a scope pivot is requested during closeout after merge. Moving to Plan would orphan a real delivery, and closing as `abandoned` would contradict the verified landing. The draft should state that post-delivery Review admits only closeout, finalization, or an explicit delivery-reconciliation route, or else define the alternative.

7. **Minor: the cutover mapping is incomplete.** The cutover covers legacy Test and Review. It does not cover:
   - legacy Develop, presumably mapped to Dev under the new entry contract;
   - legacy Backlog records whose design is already accepted, which under the new profile must still pass through Design;
   - legacy Refine, Ready, and Plan records whose design acceptance lives on Backlog-exit evidence.

   It also does not say whether an existing accepted design satisfies `core.design.accepted-current` without a synthetic Design visit.

8. **Nit: TOML key naming is inconsistent.** The keys mix camelCase (`onEnter`, `onExit`), a singular noun for a list (`action`), and snake_case (`design_rework`, `on_unavailable`). Choose one convention, preferably snake_case for TOML, and plural list names such as `actions` and `guards`. Fixing this before the schema is published avoids a later `aitm.workflow/v2`.

## Required changes

1. Add an explicit terminal marker or typed terminal-state binding. Add recovery bindings for non-delivery dispositions and reopen, or state that Core derives them from a declared typed role. Remove the "because it is the last state" rationale. Have the validator check these bindings (Finding 1).
2. Define how a branch-backed epic's integration story provisions its shared branch and draft without running an implementation clock while it waits for children. Examples are a provisioning-only operation, a waiting condition that pauses the clock, or a rule that waiting is not qualifying activity. Make the corresponding installed-path proof explicit (Finding 2).
3. Add a "Superseded Core design statements" section listing each affected Core design contract and its replacement. At minimum cover the forward chain, the Backlog design-accepted exit, the design-rework edge and destination, the split route, the Develop/Test guard rows (including expansion-resolved), and the implementation-rework edge (Finding 3).
4. State how pass, blocked, and unavailable results and the structural obligations behave in advisory mode, consistent with Core's existing rules (Finding 4).
5. Define the classes of target and head movement during Review and what each invalidates: CI only, the review verdict, or both. Include how an approved transformation or rebase is handled, and make sure an unrelated target advance cannot livelock delivery (Finding 5).
6. Define which Core operations are admissible while Review is current after verified delivery, and add a proof that a trip, pivot, or abandon request during post-merge closeout is handled as specified (Finding 6).
7. Complete the cutover mapping for legacy Develop and for pre-Plan records whose design acceptance is already recorded (Finding 7).

## Optional suggestions

1. Let each capability declare its placement requirements as typed metadata, for example "requires obligation X to dominate this slot on every path" or "must precede terminal finalization". Then "compatible placement" becomes a mechanical graph-dominance check instead of a list of rules for each contract.
2. In the explanation example, show one blocked case where a guard returns `unavailable` because a provider is missing. That makes the Explain contract ("show the reason without dispatching effects") concrete.
3. Normalize the TOML naming before publishing `aitm.workflow/v1` (Finding 8).

## Decision

revisions-requested
