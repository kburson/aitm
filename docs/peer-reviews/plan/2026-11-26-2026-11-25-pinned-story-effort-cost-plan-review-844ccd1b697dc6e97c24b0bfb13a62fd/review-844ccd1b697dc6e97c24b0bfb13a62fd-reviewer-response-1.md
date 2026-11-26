<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-844ccd1b697dc6e97c24b0bfb13a62fd"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/004/458/plan/2026-11-25-pinned-story-effort-cost-plan.md"
artifact_commit: "e907b571dd34d68ac1017d60cbccead05ba736c9"
artifact_blob: "04d582a033e5a75cfc433aaf08e9334faeec7b4d"
artifact_digest: "sha256:426a7c83a6e5ad14109bbf0688798e815819af379e5c4b041b10fd01002980f1"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-sonnet-5-5"
  model_display: "claude-sonnet-5-5"
  session_fingerprint: "sha256:89dc554194234ba6f6f2cbf6b7c156235bf15d2013dacdae795df1c601977685"
  identity_source: "runtime"
started_at: "2026-11-26T02:14:04.486Z"
submitted_at: "2026-11-26T02:14:32.957Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

I reviewed the plan against the XPR-reviewed design, reading both in full. Tasks 1–5 cover the design's five risk areas well: pinned Git reads, closed coverage, independent coverage/timing/pricing authority, digest-checked reopen and guarded publication. The gaps are in sequencing and ownership. Three places let an implementer finish every checkbox and still not satisfy the design's acceptance scenarios, mainly for the real #461 example and registration. I did not run or verify any code or external pricing page. This is a document-only review.

## Findings

1. **Registration step has no owner or test of its own (Task 5).** The design requires registering the report ID, artifact commit, window and cutoff in the story's event stream in a later commit, with no-op replay and a conflict hold. Task 5 says "the authorized planner registers that pair", and the red tests list "registration conflict". Nothing says which package code writes the event, what event kind and payload it has, or how replay and conflict are detected. The task does not say whether registration is implemented here or by an existing planning tool. If the planner already does it, the plan should name that interface. If not, it needs an implementation step and a closed-schema test. Today, "zero duplicate registrations" from the design's last acceptance scenario cannot be shown.

2. **The real #461 example lacks a coverage prerequisite chain (Task 6).** Task 6 builds and publishes #461 "at a pinned commit". Per the design, a coverage record must first be exported (Task 1 CLI), published as a story-relative file, and registered through a `core.evidence.recorded` fact of kind `story-effort-coverage`. Both the file and its registration must be present at the pin, and the record must attest coverage through the cutoff. The plan never schedules these steps, who attributes the closed admission set for #461, or what happens if that cannot be attested. Without them the real report silently falls to "observed subset only", and the plan cannot reach its stated aim of publishing the real example's actual Cost disposition. The order is: coverage export, publish, register, choose pin, then build. The plan should state it, along with the expected fallback outcome.

3. **The plan XPR gate sits last, but it must run first (Task 6).** Task 6 first bullet says to seal the plan XPR and verify the base "before Develop", yet it is the final task. An executing-plans implementer reads tasks in order and could start Task 1. Move the precondition and gate steps (base revalidation, review sealing, tracker transitions, shard inventory registration) into an explicit Task 0 or a pre-start section. Keep the hosted-validation and live-report steps in the final task.

4. **CLI inputs are underspecified (Task 4).** `story-report-build` must take the planning commit, project UUID, story, window, cutoff and reviewed rate digest/path. These are spelled out in the design and Global constraints, but the Task 4 interface lists only `--project` and "Git arguments". CLI tests are only described as guarding existing entry points. Name the full argument list and add tests for missing or malformed required arguments, and for the exit codes for unavailable (code 2) versus invalid input.

## Required changes

1. Resolve finding 1: in Task 5, specify the registration writer's owner, event kind and payload schema, and add red tests for replay (no-op), same-pair conflict and readback mismatch. If an existing planner tool owns it, cite its interface and test the integration boundary instead.
2. Resolve finding 2: add explicit Task 6 steps for coverage export, publication and registration for #461 before the pin is chosen, plus the expected outcome if closed-admission attribution cannot be evidenced.
3. Resolve finding 3: move the XPR seal, base revalidation and tracker steps ahead of Task 1.

## Optional suggestions

1. Finding 4: list the complete `story-report-build` and `story-report-open` argument sets and failure exit codes in Task 4.
2. In Task 3, store a snapshot of the official GPT-6.2 Sol pricing evidence (captured bytes or a dated excerpt with digest) alongside the rate card. A bare URL can change after the cutoff, and a later reviewer could not reproduce the review.
3. Task 5's "Conflicting discovery facts hold automatic discovery" names a consumer that no task builds or tests. Say who reads discovery pairs, or drop the claim and keep only the exact-pair reopen.

## Decision

revisions-requested
