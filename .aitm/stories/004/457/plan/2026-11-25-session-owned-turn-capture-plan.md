# Session-owned turn capture implementation plan

**Goal.** Persist exact, story-scoped turn expectations and publish sanitized immutable observations through the existing planning writer.

**Architecture.** Extend the effort store for caller-owned assignment and native binding. Expose small effort CLI commands for exact enrollment and recovery. Provider adapters normalize authorized evidence. A project-bound Git publisher creates immutable receipt files and verifies the remote ref.

**Stack.** Python 3.13, SQLite, Git, installed provider harnesses and the existing AIPR companion API.

**Spec.** [Accepted session capture design](../design/2026-11-25-session-owned-turn-capture.md).

## Work

1. Add a durable current-story selection per private session handle and transactional attempt enrollment. Store route and launch correlation beside the existing enrollment. Bind the exact native reference once and preserve the original assignment through story changes, restart and handoff. Test idempotent replay, correlation mismatch, cross-project isolation and sibling completion after the owner switches stories.
2. Reuse effort adapter recovery and the revision chain. Add bounded consumption of Codex app and subagent lifecycle evidence where the installed host verifies correlation. Keep unknown evidence visible. Retain AIPR authority for verdicts. Test wrong attempt, out-of-order revisions, interruption and overlap. Preserve only provider-verified pricing inputs and keep missing model or rate inputs explicit.
3. Expose enrollment, exact recovery, pending status and publication through `aitm-effort`. Keep recovery scoped to the supplied attempt, verified private evidence and configured authorization. Test the installed entry point and privacy canaries.
4. Publish deterministic, allowlisted turn revisions under the registered story on `planning` through one project-bound writer. Prove exact replay, collision hold, concurrent disjoint writers and lost-acknowledgement readback in disposable Git tests. Verify the existing protected remote with a scoped #457 receipt batch.
5. Qualify the native routes listed in the design, a same-provider review, and a sealed XPR companion. Record platform/build, immediate and delayed results, coverage gaps, normalization, persistence, publication and recovery overhead, and any additional model invocations. Exercise a story switch, restart, interruption and overlapping receipts. Record identity or lifecycle gaps against the exact advertised routes before disposition.
6. Review the candidate independently. Run the usage package suite, lint, installed-wheel smoke and authenticated hosted checks. Update the story’s GitHub PR property, qualification artifacts and engagement/cost table before delivery disposition.

## Review focus

- Story selection changes cannot relabel in-flight work, including replay of the original expectation.
- A callback from a different attempt cannot attach native usage. Recovery can only consume the exact enrolled reference.
- Out-of-order and overlapping evidence preserves the existing store and rollup semantics.
- The planning ref and project/story destination are checked before publication. Unknown usage, pricing and billing stay distinct.
- Local fallback and fixture success are recorded separately from the acceptance matrix for live automatic capture.

## Independent plan check

The reviewer confirmed the task ordering and asked for separate overhead measurements, explicit review-route evidence, and independent visibility into pending and unattributed work. The plan and qualification checkpoint incorporate those checks.
