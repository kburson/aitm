# #209 M08b4b atomic journal disposition and coverage projection JIT

> Implement the exact approved tasks inline with the executing-plans and test-driven-development skills.

**Goal** Record a current #203 verified native proposal once, with deterministic historical coverage projection at a requested journal sequence.

**Architecture** The existing writer-bound SQLite transaction stores one exact immutable proposal and its commit sequence. The existing historical journal view projects matching first claims and dispute origins at the requested sequence. #210 owns settlement, the effective hold and both independently qualified frontiers.

**Tech stack** Python 3.13, SQLite STRICT/WAL, the existing writer-bound source service and pytest.

**Spec** [Accepted #203 disposition split](../../203/plan/2026-11-10-203-disposition-proof-split.md) and [accepted #209 Refine](2026-11-11-209-journal-disposition-refine.md).

## Authority and bound

#203 Closed Completed and Project Done. PR #211 delivered literal trunk `b0f8ac79b8bd3f178b1d47dc2e66650f1f54e0d5`, tree `6b684109b1d85d98ba01563fb034a2d3040ddc5d`. The clean detached isolated locked baseline passed 1,071 product and CLI tests, 182 helpers, Ruff and raw 10,655/11,604 product and 778/821 helper lines. Two earlier full baseline attempts each had one inherited native capture setup refusal in different tests. Three exact targeted repeats of the first case passed. The clean pass isolated test fixture storage from contemporaneous review and result files. No suite or custody check changed. The precise earlier trigger remains unverified.

Independent #209 Refine R2 PASS covers exact SHA-256 `c20f8af889015ec24f1bb6b78f1fd2a989347bbeb74fa4df35f463f052f25b80`. Live native #209 → #210 and #209/#210 → #119 remain in force. #203 and #210 gate #204. The current exact #119 direct prerequisites are #118, #199, #201, #202, #203, #204, #209 and #210. Recheck literal trunk and graph at Develop and Close.

Epic #100 direct child, Rank 228.1, Size M and 3.90 implementation agent-hours. Use an isolated `codex/aitm-209-journal-disposition` branch. At 2.25 implementation agent-hours require committed GREEN strict migration and genuine native proposal and late-overlap REDs. Track observed implementation engagement. Re-estimated after source trace: 0.80h for migration and frozen readers, 1.05h for recording/custody, 1.15h for projection and native replay, and 0.90h for held controls and focused validation. Reuse the existing migration fixture helpers and native probes. The bounded total is 3.90h. A threatened four-hour cap or failed checkpoint requires an independently reviewed custody split before continuing. Preserve all eight direct #119 prerequisites and both downstream edges #209 → #210 and #210 → #204.

Scope four paths under `packages/aitm-usage`: `src/aitm_usage/_monitor_journal_store.py`, `src/aitm_usage/monitor_journal.py`, `tests/test_monitor_journal_store.py` and `tests/test_monitor_journal.py`. Keep the scope snapshot bytes and routing, effective holds, usage/ownership/content state and progress unchanged by the proposal call. M09 owns project write and ACK. Codex owns Develop, delivery and Close. Epic #2, C01 and production cutover remain outside this leaf.

## Review focus

- An interrupted migration must leave an exact prior schema and rows that can be reopened and retried.
- A second authority failure must leave both the commit sequence and new row absent.
- A different owner recorded as a contender must be evaluated on its own matching origin, while foreign or touching spans never enter the result.
- A later real overlapping claim changes only the newer projection and cannot retroactively change or authorize a historical proposal.
- Diagnostics with similar codes must retain their distinct source and scope evidence, and none can move a saved cursor.

## Task 1. Strict v4 journal store

Add a v4 shape using the existing file, writer custody and pinned transaction. Give v3 its own named version for the existing content disputes. The only additive DDL is:

```sql
CREATE TABLE route_dispositions (
    command TEXT PRIMARY KEY,
    hold TEXT NOT NULL UNIQUE,
    sequence INTEGER NOT NULL UNIQUE REFERENCES commits,
    payload BLOB NOT NULL
) STRICT;
```

On new creation add the table before setting version 4. On admission check the exact v1, v2, v3 or v4 schema plus application/key identity and foreign keys. In the existing single pinned write transaction, v1 adds and verifies exact v2 first, v1/v2 then add and verify exact v3, and every supported old version adds the v4 table. Set user_version 4 after all additions, validate exact v4 and FKs and recheck custody before commit. Reuse the existing rollback/atomic retry path. Migration preserves every old column value, including payload bytes, and exact historical semantics. An old reader or rejected migration must preserve the existing database and sidecar bytes. Strict format admission refuses unknown, mixed, unexpected schema objects or a journal identity key different from the pinned writer source key with the old bytes intact. Read prior legitimate data without rewriting it.

Start with store REDs in `tests/test_monitor_journal_store.py`. Reuse the existing legacy schema/row helpers and preserve their node IDs. Then add the table, run the focused suite GREEN, and commit the store paths. RED and GREEN for v1, v2, v3 migrations retaining representative actual rows, new exact shape, old/wrong/mixed identity and illegal uniqueness or FK, injected failure after v4 DDL and before commit, and exact reopen/retry. The actual frozen readers are v1 `1452999b`, v2 `5324a80b` and v3 `12825389` from first-parent history. In isolated historical source subprocesses, verify each actual reader's schema gate refuses v4 and the DB and preexisting sidecars remain byte-identical. Use the same pinned writer identity for old reader refusal so schema, rather than wrong key, explains it. Keep product tests independent of Git history by replaying these separate frozen-source probes outside the tracked suite.

## Task 2. Recording and projection

Add these types in the journal module using frozen slotted dataclasses. `hold_digest` is the verified original `ProofHold.command_digest`. `record` is the current authenticated immutable scope record. Append the default-empty field `JournalView.dispositions: tuple[JournalChangeProjection, ...] = ()` after the existing defaults.

```python
_JournalDispositionPayload(
    project_id: UUID,
    position: ScopePosition,
    start: int,
    end: int,
    hold_digest: str,
    record: _RouteDispositionRecord,
)
JournalChange(sequence: int, disposition: _JournalDispositionPayload)
JournalChangeProjection(change: JournalChange, affected: tuple[SourceRef, ...])
RoutingJournal.record_disposition(change: VerifiedRouteDisposition) -> JournalChange
```

Use the journal's exact existing ScopeState issuer. Verify the token with `self._scopes.require_route_disposition(change)` inside one writer-pinned SQLite write transaction. That method owns the existing inbox lock and checks the pending request, grant, expiry/withdrawal witness, revocation under the current operator registry, current route, hold and native custody. Acquire no second inbox lock. Copy only verified hold project, native position, affected start/end and digest with the authenticated record. Confirm that record and hold agree on command UUID and recorded hold state. The proof API and current ScopeState storage remain untouched. Recheck and compare the same current authenticated record immediately before exiting the transaction on both new and exact replay paths. The transaction rechecks store identity/custody on exit. If that last authority check fails, the staged commit and proposal roll back. The record is a historical assertion of verified evidence at recording. It supplies no authority to release, settle or advance any cursor.

Use canonical existing `_encode` and `_decode` with `self._store.evidence.validate_source_ref` for each ref. One shared reader validation path checks canonical command and hold UUID text match the row and payload, are distinct, and positive sequence references an existing commit (check the row join, including a missing commit). Require exact canonical payload bytes on read. Validate strict full 64-lowercase-hex hold/command/request digests and a nonempty nonnegative span. The terminal is a real Codex TURN with the receipt keyed to the exact disposition command via `evidence.pseudonymize("scope-receipt", str(record.command_id))`, same session/stream as the original Codex Desktop ScopePosition, a matching prefix stream and a positive raw offset. Terminal ordinal follows the original hold ordinal and is at or beyond the affected end. Keep the stored checkout and physical refs in the closed payload. Valid hold states are HELD/GAP, outcomes GAP/RESOLVED, and RESOLVED requires recorded HELD. Invalid row fails closed. Historical reads use persisted evidence, with no current queue, scope file or live source needed for replay of the view. The disposition API requires current proof even for an exact persisted replay. Recording never consumes the queued typed request, so normal exact live replay can use the same still-pending request. An externally consumed request, expired or withdrawn witness, revoked grant, changed hold or later usage makes even an exact retry refuse with no mutation. This also governs a retry after a visible commit. Read the committed result through history.

Read the existing row by command, validate it, and compare the complete canonical payload. Exact live replay returns the same immutable change with the old sequence and no new write. Changed same-command payload or another recorded command for the same hold raises ConflictError. Otherwise insert one commit and one proposal row under the same transaction. No writes to claims, revisions, disputes, progress or scope. The private payload remains local and contains no raw locator or tokens. The receipt contains no derived keys. One proposal per hold is intentional. If it becomes stale, #209 leaves the hold unchanged and supplies no replacement proposal for that hold. #210 must qualify its own settled authority and its single atomic change, without relying on #209 to reissue proof. #204 folds intent into that later atomic change without a second entry. If qualification needs an additional path, it belongs in #210's independently accepted design.

In `as_of` include only changes at or before the limit, ordered by sequence and command. Derive each `affected` tuple from admitted first claims and evidence from both types of disputes in the same snapshot. Compare the candidate project's evidence at each origin separately: first claim project, ownership contender project, and content dispute project for each of its accepted and contender origins. Require exact source UUID, native surface, session and stream, and intersect half-open spans by `left.start < right.end and right.start < left.end`. Different coordinates, foreign project and touching endpoints contribute nothing. Deduplicate the canonical SourceRef key and sort by its stable value. The scope's capped observation-key hints neither include nor exclude keys. Current capture and custody were verified at issuance and recheck. Historical overlap uses durable source/coordinate and owned span evidence and does not need an epoch or live prefix join beyond that frozen authority. Changing a later claim affects only newer projections. First claims, dispute order, revised material and earlier views are preserved.

### RED and GREEN controls

First add the actual proposal and late-overlap controls and run both to confirm the new entry point is missing before the 2.25h checkpoint. Implement the record and projection, rerun the native controls and focused journal/store suites, and commit the two journal paths.

- Use the public normal Codex reader and real current queue grant to issue one #203 no-cursor proposal with a real earlier durable claim. Exercise both GAP and prospective RESOLVED. Compare journal row count, old rows, exact ScopeState bytes, current route/view, effective holds and cursors before/after and after replay. Recheck exact terminal/older span positions and actual chronological rows.
- Reproduce the exact fixture with held interval [41,62). Preserve the preexisting legacy disposition receipt inside that fixed span. First record the later proposal, then append genuine positive later usage, apply the separate original in-span legacy disposition and stage a second real overlapping claim. This release is fixture setup. Compare before/at/after sequence views and after restart. The historical immutable change and earlier affected tuple remain exact. A fresh proposal replay fails after the later usage and after resolution.
- Exercise malformed/mixed payloads and wrong keyed terminal, same-command conflicting bytes, different command same hold, copied/foreign proof, actual consumed or expired/revoked authority, and last recheck refusal. In a forced second-check failure prove neither sequence nor row becomes visible. Verify exact live idempotence and old/new views under an unrelated claim.
- Exercise first, ownership contender, and both content origins separately with typed durable evidence. Include foreign project, source, surface, stream and session, touching ends, duplicates and omitted hint. The positive source overlap is verified through the native fixture.

## Task 3. Preserve held inputs and deliver

Exercise the existing real #115 approved Grok reader with its keyed contradiction and compare an actual prior Codex claim and cursor. The genuine diagnostic is linked to the earlier native key. No Grok project capture epochs or route admission exist, and the candidate cannot seed an admitted Grok journal claim today. Record the missing source-admission prerequisite. Assert unchanged scope, progress and durable journal claims. Reuse the existing exact baseline case `test_claude_revision_cold_reads_behind_an_earlier_persisted_cursor` for the real completed Claude quota-only batch. It asserts the singleton diagnostic code, settled eligible routing boundaries, actual durable prior cursor and no cursor advance. The first detached run passed that individual case. Retain it and exercise same-code generic native Codex coverage, mixed real Claude aggregate/quota/unreconciled diagnostics, a separate native OVERLAP_UNVERIFIED aggregate check, and an independently admitted Claude copy with valid successor material and a different original story scope. All remain held. The copy must refuse revision specifically because scope differs, with original usage/progress unchanged. Five private native preflights passed on this exact source. The aggregate and mixed controls assert real aggregate provenance and the existing cursor, not diagnostic codes alone. Keep synthetic native fixtures local.

Run the exact locked local candidate against frozen current trunk. Preserve all baseline test IDs and the raw product and helper floors. Open the literal-trunk PR, run six hosted jobs, verify the signed attestation and raw replay against the same head/tree/base, and obtain the exact independent source acceptance. Recheck current base, PR state, native merge rules and applicable trunk gates. Ordinary expected-head merge, then verify ordered parents, candidate tree and ancestry. Original implementers sign before native dependency recheck and Closed Completed/Project Done. Publish source-backed Estimate and Actual as the story proceeds.
