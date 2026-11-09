---
schema: "aitm.review-response/v0"
level: "sar"
story: 2
role: "author"
round: 1
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "981b8d77e2e988e9ec3f79768c7c9728cb66c11a"
artifact_digest: "sha256:195fff0b8903bf1a94d5ae3337d368ba0a7bfeb7110d7dd5276f0f6900d9f4f3"
integrated_upstream_commit: "7e829d53c39bb100ab6761ea2861c6720a891e70"
integrated_upstream_digest: "sha256:aceb88b37eb36d2bc08b48e639aef4784de2949e95307ead02e5dc13ac9ccbea"
patch: "patch-001.diff"
agent: {"host":"codex","provider":"openai","model_id":"gpt-6-astra","effort":"xhigh"}
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
started_at: "2026-11-09T04:23:24.027Z"
submitted_at: "2026-11-09T04:43:17Z"
start_basis: "recorded"
finding_ids: []
answered_finding_ids: ["R1-F001","R1-F002","R1-F003","R1-F004","R1-F005","R1-F006","R1-F007","R1-F008","R1-F009","R1-F010","R1-F011","R1-F012","R1-F013","R1-F014"]
---

## Summary

Accepted all fourteen findings after comparing them with the owner decision record and accepted architecture. Revised only the core design. The detailed contracts replace unsafe provisional calls without changing owner decisions or deciding the existing open choices. This is design revision, not implementation or a claim that the proposed interfaces already exist.

## Upstream integration independent of reviewer findings

Before this author turn committed anything, the owner reported that planning had advanced and explicitly instructed a fast-forward. The review worktree fetched origin and fast-forwarded from `981b8d77e2e988e9ec3f79768c7c9728cb66c11a` to `7e829d53c39bb100ab6761ea2861c6720a891e70`, retaining the untracked reviewer response. Round 1 reviewed the original raw digest `sha256:2a31083b0095233d9d2d8ba1bc11d3054bd43fe977b6f90376eda9e8593d4026`; the upstream FUR alone produced `sha256:aceb88b37eb36d2bc08b48e639aef4784de2949e95307ead02e5dc13ac9ccbea`.

Those upstream additions were not requested by this reviewer and are not credited to its findings:

- A provenance-bearing backfill envelope and occurrence-time interpretation, including a proposed timestamp-based fold.
- Separate document-review turn and level-completion events, clarifying that the existing review verdict is for code PRs.
- Planning/review timing by state, level, role and model, start bases (recorded/claim/prior-submit), native registration-time caveats, overlap handling and review import.
- The review turn/complete/import CLI entries and review-timing acceptance case 5c.
- Migration preservation of the architecture review backfill sources, plus the FUR update timestamp. The same commit also updates story 1's decision record and backfilled events; those are context and were not edited by this author.

The integrated text was evaluated along with the findings. Dispositions below state every direct overlap. In particular, operational event order remains causal append order while historical reports can sort occurrence times, and elapsed response spans retain their timing basis and coverage limitations. Patch 000 remains the creation diff of the original 981b8d7 base. Patch 001 will include both the upstream FUR delta and this author revision; the manifest will record both base commits/digests. Round 2 must independently examine the full current document, including all upstream additions.

## Finding dispositions

- **R1-F001:** Accepted. Replaced timestamp/ULID event union and whole-file replay with the core-owned operation/read-set contract, append sequencing, payload-bound identities, coherent guard/refusal commits and preserved cross-clone conflicts. Advisory mode cannot bypass integrity. Upstream overlap: its new timestamp-sorted backfill folding was reviewed here and replaced for workflow state; occurrence-time sorting remains a reporting view with original provenance.

- **R1-F002:** Accepted. Defined structured description ownership, authored sync allowlists, binding generations/recovery, intended implementation branches, retained scrap/refactor evidence and one pinned cache/store snapshot. Actor heuristics are explicitly not authentication. No direct upstream-text overlap.

- **R1-F003:** Accepted. Added default-ref routing anchors, committed-policy resolution, bootstrap-pending readiness, local-only/refreshed/stale distinctions and frozen effective inputs. Story config cannot choose its own policy authority. No direct upstream-text overlap.

- **R1-F004:** Accepted. Added the shared versioned canonical digest and schema boundary, per-level raw acceptance provenance, verified portable import, stale-base handling, plan/attempt-bound JIT and conservative path coverage. Core-only manual review records remain supported. Upstream overlap: review import/turn/completion now share these validation rules but do not by themselves assert document acceptance.

- **R1-F005:** Accepted. Specified deterministic v0 mapping against actual #1/#2 files, stable migration identities, legacy header intake, inventory, raw acceptance snapshots, provider preservation and one CAS cutover with rerun detection. Upstream overlap: preserve and deduplicate the newly backfilled architecture review events, timing bases and readable source provenance.

- **R1-F006:** Accepted. Added reserved graduation/expansion intent, uncertain-create reconciliation, coherent draft/story/link finalization and one allocation authority for shared local numbering. Permanent IDs are retained on failed finalization. No direct upstream-text overlap.

- **R1-F007:** Accepted. Pending actions are part of the transition commit, with stable keys, versioned owners, published-only shared projection, serialized/monotonic provider behavior and explicit uncertainty recovery. Terminal implementation session closure is atomic. No direct upstream-text overlap.

- **R1-F008:** Accepted. Defined clean pinned test inputs, retained actual execution results, review evidence validation, source/target delivery mapping including core-only delivery, coherent sign-off and receipt recovery without invented success. Upstream overlap: retained its explicit distinction between code PR review and document-review events; document facts do not certify code review or delivery.

- **R1-F009:** Accepted. Removed the unconfirmed second-trip cap from operative defaults/tests; retained the expansion-completion interpretation as open. Confirmed trips stop related work atomically at an observed command, while advisory reports; rework stays in the same attempt. Expansion dispositions preserve identity and clean up their precise links. No upstream cap decision was supplied; no existing open policy was resolved.

- **R1-F010:** Accepted. Added observed/estimated/partial/Unknown coverage, source deduplication, interval boundaries, same-attempt rework, Refine/Plan/Close lineage and usage/lesson semantics. Upstream overlap: retained planning/review timing and the recorded/claim/prior-submit bases, qualified elapsed spans rather than calling them exact engagement, added Unknown fallback, separated distinct-agent concurrency from same-session double counting, and retained the substance of acceptance 5c.

- **R1-F011:** Accepted. Defined kind-specific milestones and terminal/dependency meanings, separate expansion/epic relationships, cycle checks, aggregate epic closure and digest-bound spike review/delivery. No direct upstream-text overlap.

- **R1-F012:** Accepted. Added trusted legacy baseline/cutover, removal of the root README exception, candidate-ref quarantine, independently verifiable forward repair and fresh-clone validation. Shared ancestry remains owner intervention; every-push audit mechanism stays open. No direct upstream core-text overlap, although the new legacy events are preserved by the same cutover.

- **R1-F013:** Accepted. Added constrained persisted-write ownership, core path/namespace reservations, stable dependency order and schema/action versions, opaque retention and unavailable-owner behavior. Trusted Python is not portrayed as a security sandbox. Upstream review events are core-reserved types under this same boundary.

- **R1-F014:** Accepted. Added stable pre-story handles, reachable migration/recovery/delivery/import operations, a complete core-only CLI walk, explicit result/publication states and risk-based acceptance scenarios. Upstream overlap: retained review turn/complete/import commands and timing acceptance, integrated them with the stronger evidence/import contract, and preserved the code/document review distinction.

## Changes made

Reworked the operation, binding, policy, acceptance, lifecycle, timing, identity, recovery, extension and migration contracts; retained the package boundary and CLI-oriented skeleton. Added a local-operation status table and an acceptance matrix addressing concurrency, evidence and failure recovery. The new contracts are explicit builder/design choices subject to the next full review. No master architecture, master plan, owner decision file, existing event log, prior review record or implementation file changed in this author turn.

## Declined changes and rationale

None. No required finding is deferred, and no new owner decision is requested. The broader used-expansion trigger, second-trip cap, review-depth matrix and hosted every-push audit mechanism remain open. Removing the unconfirmed cap as an unconditional default/test does not decide that cap. The time limit and one-expansion budget are unchanged.

## Verification

- Read the complete reviewer response and current source decisions, including the incoming Review timing section. Inspected the actual #1/#2 v0 event files, legacy root README and upstream diff.
- Verified the current FUR is the only modified tracked file and `git diff --check` passes; all relative Markdown links resolve.
- Verified author model/effort from the active Codex turn context; reviewer selection is gpt-6.1-sol/high in its actual separate session.
- Checked the [Git ref compare-and-swap contract](https://git-scm.com/docs/git-update-ref), [pre-push inputs](https://git-scm.com/docs/githooks#_pre_push), [workflow-ref selection](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows#workflow-triggers), and [RFC 8785 canonicalization](https://www.rfc-editor.org/rfc/rfc8785) against primary documentation. The core contracts are design choices, not assertions that Git supplies application-level serialization or that provider APIs already implement them.
- No implementation tests apply. Response metadata, finding coverage and all raw-byte patches will be verified before publication; patches will reconstruct from the original review base, including the disclosed upstream delta.
- This response's recorded span includes the interrupted author work and upstream integration; it is elapsed author-turn provenance, not exact engaged time. No unseen duration is invented.
