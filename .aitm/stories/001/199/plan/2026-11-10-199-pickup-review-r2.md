# #199 independent pickup and split review, round 2

Claude Opus 5.5, high effort. Off-platform review of the full exact pickup and split on the literal trunk baseline. November 10, 2026.

# Independent review, round two: revised #199 JIT and M08b native split

I reviewed only the packet. I used no tools and made no writes or issue changes. I did not recompute the two SHA-256 values myself, so each verdict applies to the digest exactly as you supplied it. Neither verdict authorizes Develop for any later leaf, provider traffic, production work or a change to the parent order.

## Verdict 1: #199 JIT, `cc160a8c83169d8f3d20f6372487af882f08c27acaf2d3aecbfd3733d15fabbf` — **PASS**

All three round-one holds are substantively corrected.

- **H1 (witness carrier): fixed.**
  - **Private collector:** `read_delta(..., _revision_witnesses=None)` takes a private per-call collector. Only the final successful fixed-prefix read appends to it, and it is cleared before any enrollment rescan.
  - **Public shape unchanged:** `AdapterBatch` keeps its four fields and its serialization.
  - **Runtime-only copy:** the witnesses are copied into `VerifiedScopeBatch._revision_witnesses`, a private field (`repr=False, compare=False`, keyword construction, default empty). It never reaches a persisted or public wire shape.
  - **Who is trusted:** `verified_revision` accepts a batch only when `self._batches.get(id(batch)) is batch`, and only with the exact observation object from that batch. A batch or witness built by a caller conveys nothing.
  - **Keys:** the adapter derives fingerprints from the approved source's `source._ledger` key under two separate namespaces, `claude-revision-material` and `claude-revision-prefix`. ScopeState checks that this is the approved registry key, validates through `registry.source_evidence()`, and recomputes the material fingerprints from the exact pair of observations.
  - **Missing predecessor:** if the predecessor object is absent, no witness is issued.
- **H2 (emission sites): fixed.**
  - Only two places can emit a proof: the ordinary accept path with an exact prior, and the successful terminal reconciliation loop.
  - The tier-invalidation publish that comes with MALFORMED_USAGE, COUNTER_REGRESSION or UNRECONCILED_USAGE emits no witness, and there is a RED test for it. Report and withdraw emit none.
  - `terminal()` now receives the committing `SourceFrame` or `SidebandFrame`. The witness location is `SidebandFrame.ordinal`, and the timed diagnostic context is kept separately.
  - "Ordered distinct later spans" now applies only to successive revisions of the same request. A fixture covers one terminal row completing several requests at the same later ordinal.
- **H3 (quota seam): fixed by removing it from #199.** #199 now preserves every diagnostic byte for byte, and quota refinement belongs to M08b4.
- **Both round-one notes are addressed.** Linux hosted jobs reuse the Darwin/arm64 platform fixture, with an explicit statement that this is not Linux qualification. The inverse cost-state case is in Task 2.

The specific points you asked me to inspect:

- **Collector and predecessor requirements:** these are exact. Witnesses come only from the final fixed read, the predecessor object is required, and the material is recomputed by the issuer. Physical locator, incarnation and cursor stay in the fixed-read context, apart from the proof identity that survives a copy.
- **Zero cursor release on diagnostics:** this holds. #199 does no classification, claim mutation or cursor release, and it leaves the journal unchanged. The existing `_complete` check still refuses progress whenever `read.batch.diagnostics` is non-empty.
- **Scope behavior:** Task 2 covers all the required cases:
  - a story switch keeps the original scope
  - in a shared or handoff read, A's proof is used rather than B's later scope
  - when A is disabled, written to and re-enabled, no proof is issued, including for cumulative changes that straddle the gap
  - untimed rows at a boundary, and the inverse case
  - re-enrollment or a new location gives no legalization
  - a copy keeps its identity without permission to overwrite the first owner's frontier
- **3.75-hour scope:** it is confined to the native proof. The six named files are the only ones changed. There is no journal, ledger, coordinator or quota work, there is a 2.25-hour checkpoint, and the rule is to stop and re-plan if the cap is threatened.

Conditions on this PASS:

1. #199 enters Develop only after native readback shows all four of these exist: M08b2–M08b5, the chain #199→b2→b3→b4→b5, and each leaf's direct block on #119.
2. #199 closes only after a fresh native readback of those edges.

## Verdict 2: M08b split, `1c97ab7d36b9fe162e59472e89da03a36b2ddbcf83717f6fb70a89eeba85000f` — **PASS**

All seven round-one holds are substantively corrected.

- **S1:** all four children, the full predecessor chain and each direct #119 blocker must be created and read back before #199 enters Develop. The graph is rechecked before Close, and #199 never closes while a required gate is missing.
- **S2:** M08b5 closes only in one of two ways: it delivers the exact folded intent, or a changed parent plan is re-accepted and its replacement blocker on #119 is verified.
- **S3:** M08b4 owns `RoutingJournal.record_disposition(change: VerifiedRouteDisposition) -> JournalChange`. M08b5 extends it so the covering parent and every child withdrawal land in one `JournalChange`.
- **S4:** every leaf that adds private schema (M08b2 through M08b5) gets the full review. That review covers admission from the old version, an atomic schema change with retry, explicit handling of old rows, preserved historic views and rejection of unknown formats.
- **S5:** a successor is applied only when the issued immediate predecessor fingerprint equals the current durable head and the saved original route agrees. There is no bypassing or chaining through a held or unproved revision, and #199 exposes that fingerprint.
- **S6:** in #199 and M08b2, every unresolved diagnostic keeps the previous cursor, quota-only diagnostics included. A quota release in M08b4 also requires retention and replay in private writer custody, a named reader, and a restart proof. Same-code and mixed cases still hold, and every aggregate diagnostic (OVERLAP_UNVERIFIED included) stays unsettled before M08b5.
- **S7:** before M09, Claude is the only path. A positive Grok fold, or anything that depends on M11 or moves after M09, needs a changed parent plan to be re-accepted.
- **Ranks:** the readback confirms 226–229 are free.

The authorities are intact. The parent plan bytes `1a5e9bb3…a241a9` and `8899a4d1…4e5f21` and the #118 split `3ebb10df…9f6202f` are pinned and unchanged. #118 stays a direct prerequisite of #119. Spreading the #118 M08b obligations across the four new leaves is the explicit, gate-preserving split that #118 itself allows. M09, M11, M12 and M13 keep their roles, and the Linux and release gates stay outside these leaves.

## Notes for later JITs (none of these block either verdict)

1. **Tier-only accept path in #199.** If `contradictory_processing` is set while counts are unchanged, the plan emits a witness from the accept path. Pin this with a fixture. Also, a successor that follows an unwitnessed tier invalidation will name an unproved predecessor. M08b2's head-equality rule will hold it, so document that as an expected hold.
2. **Recheck in `verified_revision` (#199).** Membership in `_batches` is not enough. It must also do the full `_recheck_batch` (equal registry view and the fixed cursor). Add a RED case where the registry changes between issuing the batch and the query.
3. **M08b4 wording.** "Add the new direct #119 blocker before any predecessor closes" may be impossible to schedule. M08b4's JIT probably happens after M08b3 has closed. Safety still holds because M08b4 directly blocks #119. Reword it to "before b4 Develop, and in any case before b4 closes".
4. **M08b2 progress fixture.** Claude in the monitor without a verified quota account always emits COVERAGE_GAP. So M08b2's progress test needs a fixture that has passed the quota check; its JIT should confirm one exists.
