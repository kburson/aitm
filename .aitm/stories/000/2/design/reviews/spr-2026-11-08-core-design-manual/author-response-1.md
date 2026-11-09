---
schema: "aitm.review-response/v0"
level: "spr"
story: 2
role: "author"
round: 1
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "73210b6da93942f06a0d6616cf5df02eaf64180c"
artifact_digest: "sha256:865cdcef8edfaa472fe31ae05425f99e6af26e00f8e238b59d42e045149cf257"
patch: "patch-001.diff"
agent: {"host": "codex", "provider": "openai", "model_id": "gpt-6-astra", "effort": "xhigh"}
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
started_at: "2026-11-09T05:18:20Z"
submitted_at: "2026-11-09T05:27:07Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: ["R1-F001", "R1-F002", "R1-F003", "R1-F004", "R1-F005", "R1-F006", "R1-F007", "R1-F008", "R1-F009", "R1-F010"]
---

## Summary

Accepted all ten required findings after checking the owner decisions, accepted architecture and core-only M1 scope. The revision specifies the missing race/evidence boundaries and their acceptance cases. It changes builder-level mechanisms, not the four-hour limit, expansion allowance, advisory policy, owner-only pivot or existing open decisions.

This is the explicitly authorized manual SPR. The separate native attempt remains unjoined and preserved. Neither this response nor the resulting author commit is a native protocol submission.

## Finding dispositions

- **R1-F001 — accepted.** Added Published continuity: a retained per-store/ref observed shared frontier is distinct from the content-valid base and unpublished local work. Rollbacks, sibling replacement, deletion and unknown ancestry fence shared effects; invalid descendant trees are quarantined without forgetting their observed shared ancestry. Forward repair must extend the diagnosed chain. Journal/ref recovery and a fresh clone's checkpoint limitation are explicit. This closes the counterexample without pretending that genesis validation proves no prior rollback. Store safety acceptance now exercises both rollback and structurally valid sibling history, plus legitimate unpublished divergence.
- **R1-F002 — accepted.** Added a clone-common ref/worktree gate around supported mutations, retries, init, migration and binding operations, with before/after inventory checks and preservation/fencing on detected external interference. The guarantee explicitly excludes an unobservable arbitrary out-of-band Git checkout; CAS is not presented as a HEAD/index lock. Local core delivery refuses a checked-out target and supports observation of an ordinary separately authorized worktree merge. This preserves the normal checked-out trunk flow without silently moving its branch behind the index. Acceptance covers both supported serialization and an injected external checkout race. Hooks remain optional.
- **R1-F003 — accepted.** Reserved the semantic draft identity across all active graduation intents, in addition to per-operation dispatch ownership. A different operation ID or frozen snapshot cannot evade that predicate; publication replay rechecks it before any eligible dispatch. A competing clone joins the holder or receives a conflict. Cancellation retains the reservation while old issuance is possible; only proven non-issuance/fencing permits replacement, while an issued identity must be reconciled/reused or explicitly dispositioned. Acceptance now races two distinct operation IDs for one stable draft as well as two senders for one intent.
- **R1-F004 — accepted.** The allowance-reserving transaction now records an expansion-pending origin condition and pause before external issue creation. Enforce blocks new implementation/verification/forward completion even without a child ID. Finalization atomically replaces that block with the child block; uncertainty cannot clear it, refund the slot or permit another issue. Cancellation/disposition needs proof or reconciliation of the issued identity. Advisory keeps its permitted waiver behavior, unresolved condition and pause provenance without claiming resolution or verified closure. This does not decide the separate open interpretation of continuing the accepted origin after a successfully resolved expansion.
- **R1-F005 — accepted.** Defined an attempt/source-bound single-use managed-start admission in the same planning order as stops, with publication before shared dispatch. Preparation and delivery intent are not admissions. A stop that wins refuses the start; an admission that wins becomes explicitly already-authorized in-flight work subject to cancellation. The executor's launch gate orders its observed cancellation and process creation; supported processes are terminated and disconnected/provider uncertainty remains pending. Delivery additionally checks current review/task authority and uses single-dispatch/fencing semantics, with target CAS as another condition. A late landing is retained without closing an invalidated attempt or triggering a second effect. Acceptance tests both orderings and lost/late outcomes. This is a bounded distributed guarantee, not a promise to recall an already sent request instantly.
- **R1-F006 — accepted.** Authoritative test receipts require stable captured actual inputs or an equivalent lane excluding intervening mutation, including accounted untracked fixtures. Declared source inputs are immutable for the run; outputs/derived temporary fixtures are separated. Endpoint checks determine applicability but cannot establish what ran. Unsupported lanes produce diagnostic results only, and the existing dirty/unaccounted-input refusal remains. Acceptance adds the transient edit/restoration counterexample alongside dirty and persistently moving sources.
- **R1-F007 — accepted.** Separated retained review evidence from an effective passing review. Activation needs Review position, current attempt/source and the kind's applicable predecessor evidence, including tests for code leaves. An early pass cannot stop time; later activation records its actual time. Sign-off checks all applicable requirements and unresolved waivers before verified Done/dependency eligibility. Real delivery remains visible independently. Missing derived proof is reconstructed; genuine reruns use managed verification in Test/Review, and changed code takes same-attempt rework. Historical waivers remain recorded rather than disappearing. Acceptance includes both an early pass and advisory Test waiver followed by real delivery/sign-off.
- **R1-F008 — accepted.** Defined an explicit M1 exact-content policy evaluator and the completion path for A→B→C: review the missing levels on C, recompute obligations if the candidate changes and retain incomplete/capped outcomes as unaccepted. Evaluation pins the current policy definition/revision while preserving historical acceptances. Exceptions require the policy's explicit authority, exact scope/digest, rationale and validity. A sequence/delta policy needs a separately supported coverage schema; it cannot be inferred from chronological records. The required-level matrix and sequence/delta choices remain open. The acceptance fixture demonstrates why historical A/B records alone do not satisfy an exact-content requirement on C. This review does not initiate extra levels or retroactively broaden SAR.
- **R1-F009 — accepted.** Separated observed agent engagement, subprocess elapsed duration and CLI-gap estimates. Only supported observation of bound actor engagement contributes to the confirmed lower bound; a long unattended process does not. Qualifying intervals are intersected with attempt/pause boundaries and deduplicated per actor, without adding overlapping tool duration. Core-only inability to establish engagement is disclosed as Unknown. Acceptance pairs a long unattended process with a genuinely observed overrun. Planning/review elapsed reporting and the owner’s four-hour engaged implementation limit remain unchanged.
- **R1-F010 — accepted.** Removed the conflicting claim that local-only init commits config. Both fresh local and hosted init prepare settings for the caller's ordinary commit/PR, retaining a bootstrap journal and becoming ready after verification. Added explicit legacy preparation before readiness, a stable versioned adoption identity/proposed UUID tied to legacy root/ref, retained expected tip/adapter/authority, committed declaration as cross-clone authority, and one atomic cutover. A fresh clone can resume from the committed declaration and verify the same identity afterward. Interrupted or competing preparations/apply cannot choose a second effective identity/allocator. Acceptance covers local bootstrap, interrupted adoption and a second clone.

## Changes made

Revised only core-design.md and this manual SPR folder. Added the specified concurrency/continuity, immutable-input, effective-evidence, multi-level policy, engagement and adoption contracts; tied them to acceptance cases; updated the FUR's timestamp and working-branch metadata.

Optional suggestions were addressed: prose next to the config example identifies the mandatory generated trust anchor and complete review-policy definition rather than presenting an incomplete runtime-settings example as deployable policy. The command inventory now includes init reconfiguration and migration preparation. Trip records explicitly identify the origin, triggering child and all affected attempts.

The post-SAR base already includes upstream 7e829d5. None of those additions is attributed to these SPR findings. SAR's original patch-000 and both recorded bases/digests remain unchanged. This revision touches timing, lifecycle events' interpretation, CLI and acceptance, so the next reviewer must read the complete combined file.

## Declined changes and rationale

None. All ten required findings are accepted; no required change is deferred. Existing expansion-completion interpretation, second-trip cap, review-depth matrix and GitHub every-push audit mechanism remain open. No additional owner decision is needed for this round.

## Verification

- Checked every finding against the owner record and accepted architecture. The revision preserves the no-model core, single owning writer, authoritative committed policy, qualified timing, advisory reporting and absence of routine human gates.
- Checked the Git premises against primary documentation: [fast-forward ancestry](https://git-scm.com/docs/git-push#_note_about_fast_forwards), [expected-old ref updates](https://git-scm.com/docs/git-update-ref#_description) and [worktree state/checkout behavior](https://git-scm.com/docs/git-worktree#_description). The design's cooperative gate and external-interference limits are explicit engineering choices; Git documentation does not establish a joint checkout/ref lock.
- Reviewed the combined FUR diff for contradictory old clauses, retained clean-input refusal, and aligned effective-review timing and delivery admission language.
- Checked FUR relative links, Markdown whitespace, response metadata and complete R1 finding coverage before committing. No implementation tests apply to this document-only revision; acceptance rows specify later executable proof rather than claiming it already ran.
- Only this FUR and manual review folder are staged for the temporary author-turn commit. The blocked native worktree's recorded file digests, HEAD and branch remain unchanged. No native command, implementation, context file, prior review record, trunk update or XPR is included.
- The level's final verification will reconstruct every revision from patch 000 plus numbered author patches and compare all bytes/digests before planning publication.
