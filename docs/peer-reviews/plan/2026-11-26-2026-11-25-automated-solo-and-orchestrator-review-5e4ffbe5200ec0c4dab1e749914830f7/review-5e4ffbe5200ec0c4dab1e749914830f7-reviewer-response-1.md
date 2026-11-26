<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-5e4ffbe5200ec0c4dab1e749914830f7"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/004/461/plan/2026-11-25-automated-solo-and-orchestrator.md"
artifact_commit: "4df8be1918ede0e24d4d2512cbdc397e80d603e8"
artifact_blob: "afcfe8797447d1ae8d1abb7471b118ce19088697"
artifact_digest: "sha256:d8d6545e635017362c9f192635266838b0dd6be654e0d310aabaed4581fa9e6c"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-sonnet-5-5"
  model_display: "claude-sonnet-5-5"
  session_fingerprint: "sha256:30ae7de6ccd3036c7a2d69e1bd021610bb63ff3b51db6bb1f98c184b428f1867"
  identity_source: "runtime"
started_at: "2026-11-26T01:50:01.221Z"
submitted_at: "2026-11-26T01:50:35.482Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed only the plan artifact (`2026-11-25-automated-solo-and-orchestrator.md`, 26 lines). I did not read the superseded composer plan, the forwarded addendum, the shipped #457 code, or any receipts, so claims about shipped command behavior are unverified here. The plan is a tight, well-scoped two-leg qualification with good evidence discipline (native-readback before binding, no-retry on conflict, immutable prior receipts, separate failure controls). The main gaps are in control flow when a leg fails, ambiguity in the solo leg's "enrollment/dispatch" semantics, undefined independence and sign-off roles, and missing cleanup and budget bounds. Four of these need a plan change before the run.

## Findings

1. **No branch for a failed or partial leg; steps 4–5 assume exactly three verified receipts.** Step 3 says that on conflicting evidence the launch is not classified verified and is not retried. Step 4 then requires a fresh `session-export-batch` to return "exactly three sanitized revision-1 receipts", and step 5 publishes "the same three verified receipts only". The Acceptance table (Research closeout) says "a failed leg remains visible and limits the recommendation", but no step says what happens to settlement, the frozen batch and publication if the orchestration leg (two attempts) never verifies. Scenario: the target turn completes but the child lineage is missing. Step 3 leaves it pending, so step 4's "exactly three" check cannot pass, and the executor has to improvise whether to settle the solo receipt alone, abort, or publish a partial batch. The plan should predefine the outcomes (e.g. solo-only batch of one; orchestration pending; publication count equals the verified count) and say which acceptance rows become "failed, recorded" rather than "blocked".

2. **The solo leg's enrollment and timing semantics are unclear and conflict with the "enroll before dispatch" framing.** Step 2 says to "record a retained-evidence expectation in the fresh store and acknowledge its actual post-dispatch timing". No dispatch exists for a solo turn that is already complete, so "post-dispatch" has no referent. Step 4 says "record whether retention was deliberately deferred or actually unavailable at the first observation", which is a different concept that is not tied back to step 2. The Acceptance row says it "records retrospective enrollment accurately" without defining what accurate means. Because this leg is retrospective by construction, its verdict should be explicitly scoped as "closeout of already-completed work enrolled after the fact", and the plan should state what the recorded expectation timestamp is compared against, and which field distinguishes deferred from unavailable.

3. **Solo sample selection is by the same actor who judges it, with an unnamed identifier.** The "intended sample" is "the previous turn that traced the manual-start requirement". Preflight says to record identities privately, but the plan sets no selection criteria beyond a prose description, and no pre-registered check that the turn "establishes #461 scope" other than the controller's own reading. Stating the exact eligibility predicate (terminal completion count = 1, no delegated work, native usage present, user request names or implies #461) and recording the sample ID before any readback of its outcome would stop post-hoc selection. Also say what happens if the intended turn fails the predicate: fall back to another turn, or record the leg as failed.

4. **"Independent" and "sign off" are used without defining who or what.** Step 6 requires "an independent evidence review" and "sign off after protected readback"; Acceptance requires "independence" on planning. Grok drafted this revision, the coordinator reconciled it, and this same chat both runs the experiment and invokes the writer. The plan should name the independence criterion (a reviewer that did not draft, execute, or select samples, and cannot edit evidence), name the sign-off authority, and say whether a failed independence check blocks the recommendation.

5. **Orchestration attempt naming is ambiguous.** Step 3 records "a delegated owner attempt and a worker attempt with that owner as parent", then requires "a single exact child whose retained native lineage points to the delegated owner". It is unclear whether "worker attempt" and the "single exact child" are the same entity. Step 5 then separately replays "the exact child terminal reference", and Acceptance mentions "a genuine child reference without a verified parent". Three terms (worker, child, target) appear for what may be two or three entities. A short glossary or table (controller turn → delegated owner chat/turn → native subagent child, and which two become the receipts) would remove the risk of binding the wrong pair.

6. **No cleanup, budget or stop condition for the disposable chat and extra model turns.** The plan creates a disposable agent-created chat and an extra subagent, and Step 6 reports "extra model turns, known usage and cost". There is no cap (turns, tokens, wall clock) after which the run is stopped, and no step to close or archive the disposable chat or remove the scratch stores and the armed composer enrollment if the run aborts midway. Step 1 restores the composer selection only at preflight. A pre-set ceiling and an abort/teardown path are cheap to add.

7. **Preflight and the hold control have no explicit pass criteria in Acceptance.** Step 1 (zero-new-receipt baseline, hook pins, branch rules, origin/writer authorization, composer selection restored) and step 5's hold test ("neither protected planning nor batch bytes change") are the safety preconditions, but only the "Failure controls" row covers the hold test, and nothing in Acceptance fails the run if preflight facts are missing. Add a precondition row, or state that any unmet preflight item blocks dispatch.

## Required changes

1. Add explicit failure/partial-leg branching for steps 3–6 (Finding 1), including how many receipts are settled, frozen and published in each case, and how the acceptance rows are marked.
2. Redefine step 2's enrollment/timing language for a retrospective solo turn, and tie "deferred vs unavailable" to a named recorded field (Finding 2).
3. State the solo sample's eligibility predicate and record its identifier before outcome readback; define the fallback if it fails (Finding 3).
4. Define "independent evidence review" and "sign off" by role and criteria (Finding 4).
5. Disambiguate owner / worker / child / target and name which two attempts correspond to the receipts (Finding 5).
6. Add a budget ceiling and an abort/teardown path (Finding 6).

## Optional suggestions

1. Add a Preflight precondition row to Acceptance (Finding 7).
2. Note in the Goal that "this plan supersedes the composer plan" takes effect only on XPR acceptance, and say which plan governs if XPR is revisions-requested; the current text is implied by step 1 but not stated.
3. The last paragraph (human message as historical scope evidence) could move to step 2, where the sample is selected, so the rule sits beside its use.
4. Step 5 packs six distinct experiments into one paragraph. Splitting it into hold, fixture, orphan-child replay and publication would make the evidence map to Acceptance rows more easily.

## Decision

revisions-requested
