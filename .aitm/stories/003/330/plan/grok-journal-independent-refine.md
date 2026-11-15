[15:28:20]
REFINE_330: PASS, subject to conditions R1–R10 below. These become part of #330's accepted body. Any condition that fails at JIT triggers Stop → Refine.

**Gate validation**
- **Close:**
  - #119 is natively closed.
  - #329 is closed with Project status Done. PR #332 merged as `30e1a13d`, with ordered parents and zero diff verified.
  - #119's Project status Done is not in the supplied evidence. JIT confirms it before Develop.
- **Base binding:**
  - The `monitor_journal.py` blob `e64622a3` equals the post-#326 reproduction blob. So #329 did not touch the journal, and the supplied `prepare` (with the swallow) is current.
  - The `monitor_scope.py` blob moved from `a69ff3b2` to `bb2a781b`. That is consistent with #329 delivering the admission handle.
  - The blob list carries no commit label. JIT re-pins all six blobs at the Develop base, which is `30e1a13d` or a descendant. Any drift in the journal, writer or store forces a re-map.
- **Graph:** #121 remains the sole dependent, with no new edge. Epic #2, C01, cutover, #204, #331 enrollment and #121's coordinator and live callback all stay outside this leaf.

**Exact three-file ownership**
- **`monitor_journal.py`** carries every Grok blocker visible in the supplied source:
  - `_stream` and `_source_checkpoint`, which are CandidateSource/SourceCheckpoint-only.
  - `_cursor` and `_settlement_stream`.
  - The `prepare` double admission and its swallow.
  - `_boundaries_settled`. It returns False on any non-`SourceBoundary`, so Grok could never write progress today.
  - `_paired_frontier` and `_paired_receipts`.
  - The `_reserve` offset check.
  - `_UsageMaterial`, `_ClaimPayload` and ClaimEvidence epoch selection.
- **`monitor_writer.py`:** only `_monitor_revision` gains a type-selected Grok branch. `commit`, `_readback`, the `monitor-delivery-row-v1` key derivation and `_commit_monitor_delivery` stay unchanged.
- **New test file:** `test_monitor_grok_delivery.py` goes in the existing aitm-usage test root, at an exact path JIT pins. It reads #329's retained matrix and isolated issuer read-only. It makes no conftest, fixture or existing-test edits.
- **Read-only, resolved:**
  - `_monitor_journal_store.py`: the progress key is five TEXT columns with no surface CHECK, and the cursor, payload and evidence columns are opaque BLOBs. Grok therefore needs no DDL and no schema version 8.
  - `monitor_scope.py`: the admission is consumed through the delivered `_take_grok_admission`.
  - `monitor_types.py` and `sources/adapter.py`.
  - `monitor_registry.py` and the coordinator.
- **Not proven by the supplied source:** each of the following is an actual dependency. Needing an edit to any of them means Stop and a separately reviewed extraction.
  - The `_encode`/`_decode` codec module carrying a closed alternative without changing legacy bytes.
  - `resolve_route` accepting the #329 Grok proof.
  - The #329 read path accepting the prepare-held admission.
  - GrokObservation in the claim being the same type that MonitorRevision admits.

**Conditions**
- **R1 – One admission.**
  - `prepare` acquires exactly one admission. It derives the stream from that admission, reads the cursor through internal `_cursor`, not `cursor_for`, and consumes the same handle in ScopeState.
  - Delete the `except (LedgerError, OSError, ValueError)` fallthrough. Keep `_LiveSourceUnavailable → _record_live_exclusion` and `_StaleLiveExclusion` exactly as they are.
  - An admission left unconsumed on any failure must not stay redeemable, using an existing #329 discard path or one that is provably bounded.
  - The admission's `view` must equal the `_fresh_view` registry inside the prepare transaction, else ConflictError.
  - Public `cursor_for` keeps refusing a Grok locator.
- **R2 – Strict identity.**
  - The Grok stream tuple is the admitted opaque source, actual surface, stream, physical locator anchor and incarnation.
  - `_cursor`, the `prepare` post-read check and `_settlement_stream` dispatch on the exact checkpoint type. SourceCheckpoint stays byte- and behaviour-identical, and a GrokCheckpoint must match the tuple.
  - Mixed types, pre-enrolled or unqualified streams, a consumed or mismatched handle, and any disagreement between cursor and native tuple all refuse before reserve.
  - `_reserve` requires strictly increasing authenticated byte offsets in the snapshot/strict domain. Restart supplies the stored GrokCheckpoint.
  - Revocation between prepare and reserve causes a conflict, with no claim and no progress.
- **R3 – Exclusions and holds.**
  - A stable policy exclusion is recorded journal-only, with no ACK and no cursor.
  - A Grok settled predicate replaces the `SourceBoundary`-only rejection for Grok streams only:
    - A marked boundary settles only on an exact applied #117 receipt or a resolved hold.
    - An unresolved hold or an unverified mark blocks all progress past its authenticated boundary and produces no accounting row.
  - `_paired_receipts`' Codex repeat-receipt rule never applies to Grok.
  - A clean independent stream still progresses.
- **R4 – Accounting.**
  - Marked versus hookless is selected by type and never by an either-satisfies check.
  - Hookless work produces project-only claims with no story, only in the authorized project.
  - Marked work requires the receipt, the native position and the original owner and story.
  - A contradicted mark is never downgraded to hookless.
  - The payload stores pseudonymized refs only.
- **R5 – Claim codec.**
  - For Grok, ClaimEvidence selects the exact #329 epoch under the batch's original checked profile generation and physical source. It uses the typed prompt start and terminal end, and keeps that epoch's own capture generation and start boundary.
  - Legacy `_UsageMaterial` / `_ClaimPayload` / `_RevisionPayload` bytes and digests stay byte-identical. A golden-byte test runs against retained pre-#330 rows.
  - Grok claims are revision 1. A changed prefix becomes a dispute or hold, never a revision.
- **R6 – Writer.**
  - The Grok branch builds MonitorRevision from the proven GrokObservation, with native tokens and cost.
  - Project check, readback-exact ACK and causal revision behaviour for existing providers are unchanged.
- **R7 – Reserve and ACK.**
  - Only the existing #119 reserve, guarded commit and exact ACK under #122 custody are used.
  - A lost or replayed ACK and a retry keep the original project and story. They neither reattribute a positive nor add counts.
- **R8 – #122 rollback.**
  - With no schema version bump, the pinned snapshot restore is proven.
  - Legacy code that meets a Grok payload or cursor must refuse closed, with no misparse, no ACK and no progress.
  - If that requires a version marker or store edit, Stop → Refine.
- **R9 – Proofs.**
  - Every matrix case in the story is covered: delivered marked story and hookless project-only through reserve/write/ACK, lost or replayed ACK, restart and the same-writer cursor versus live-grant distinction as accepted in #329, changed native prefix, competing owner, unverified receipt hold, incidental unrelated progress, typed-refusal coverage, and legacy byte and rollback gates.
  - No live turns, no issuer expansion and no Linux surface claim.
- **R10 – Estimate.**
  - The estimate is 3.75h, within the 4h cap with a 0.25h margin. Exact JIT is a separate step and is not counted in it.
  - JIT maps the claim, digest, source key, progress, seal, guarded commit and ACK codecs and re-estimates.
  - If the codec or route dependencies above require any edit, or the estimate exceeds 4h, Stop → split.

All existing Test, independent source review, protected merge and native Close gates are preserved.
