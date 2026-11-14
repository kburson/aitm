[07:18:09]
# HOLD: #295 M08b6 Claude Agent journal containment Refine

I'm holding #295 because R3's exact public-cursor proof can't be built on any existing path in the evidence. That leaves both feasibility and the 4.0-hour estimate unverified at Refine, and JIT can't fix this without a separate prerequisite. I am not approving JIT or implementation. The R3 gate, the current graph and the exclusions stay as they are.

## Blocking findings

**B1. No existing path gives an affected Claude stream a durable cursor.** The code you supplied shows why:
1. `_read_usage` creates `ClaudeState(source._ledger, neutral_markers=True)` without an account. Only the Codex branch gets one, through `_codex_quota_reference`.
2. `_quota(frame, None)` returns `()`. So a `rate_limit_event` adds `self.gap(frame, COVERAGE_GAP)`.
3. `run()` also adds `COVERAGE_GAP` whenever `latest is not None and not quota_checked`. So every eligible Claude read reports a diagnostic, whether or not a rate event is present.
4. `_complete` returns `False` if `read.batch.diagnostics` is non-empty. So `_write_progress` never runs for that stream.
5. The preflight confirms this. Both an ordinary request and a native rate event give `cursor_for(...) is None`. The `pending` claims still get reserved.

Tests 1, 2 and 4 each need a real Claude prior cursor:
- Test 1 needs "admitted ordinary prefix progress".
- Test 2 needs "the actual prior accounting cursor".
- Test 4 needs to "resume beyond it".

None of these can be met by honest means:
- **A read-only fixture can't do it.** The block is in the read and completion logic, not in the fixture data. A fixture could only make a cursor appear by seeding persistence or getting around a generic coverage diagnostic, and both are forbidden.
- **JIT can't settle it without a prerequisite.** The existing routes JIT would check (an ordinary request, a native rate event, the scope adapter) are the ones the preflight already tried.
- **Supplying a Claude account is out of scope.** It would add new quota authority to the scope adapter. That falls under the scope-enrollment and ownership limits #295 must not change, and it isn't one of the contracts the Refine names.
- **Weaker versions don't count.** A cursor that is absent and therefore "unchanged" proves nothing about holding the cursor. A Codex stream alone can't stand in for the affected cursor either.

If the plan owner knows of an existing writer-authenticated way to get a Claude account or quota for this stream, it should be cited. The packet doesn't contain one.

**B2. The estimate is unverified.** The 4.0 hours apply only "after a proven carrier", and the carrier's own cost is unknown. A carrier means wiring in authority plus its own qualification, which is unlikely to be small. Even without the carrier, the named work is at the top of M:
- a schema revision with migration and rollback
- immutable keyed coverage transitions
- the witness and expiry handling
- the `coverage_changes` reader
- checking root, namespace, stream, locator, incarnation, custody and boundary again before the write
- telling authenticated source loss apart from transient IO errors and revocation
- the fixture provenance
- four tests across two modes, plus stale-prepare checks

Refine can't size the leaf. A resubmission should break the hours down by contract.

**B3. The evidence isn't tied to exact versions.** The amendment's publication link and the literal trunk reference are both blank. The NA-1 section is cut off after its heading. I can't check the R3 bytes against digest `75d073bd…`. The resubmission must fill all of these in.

## Non-blocking items for a resubmission
- **Test 3 looks feasible with the Codex stream from the preflight.** It produced a claim and `cursor_for == read.progress` with no diagnostics. JIT should confirm that "separate stream" in R3 allows a stream from another provider. If it means a second Claude stream, test 3 runs into B1 too.
- **The typed locator-ambiguity refusal is new work.** Discovery currently returns a generic BoundaryUnavailable. Find out which module owns discovery. If it sits outside the three files R3 names, the scope grows.
- **Containment has to refuse before `_claim` inside `_reserve`.** `_complete` runs only after claims are staged, so it can't be relied on to stop them. The Refine already identifies this correctly.
- **The R3 tests must use only public paths.** The preflight reads the private `_read.batch.diagnostics`, which is acceptable in a preflight but not in the tests.

## Ways to resolve this (not decided here)
1. **A carrier prerequisite.** Write a separate, bounded proposal for a native Claude quota or account carrier under existing authority, with its own Refine and JIT. #295 stays gated behind it. Any graph edge needs accepted authority first.
2. **An R3 amendment.** A separately reviewed amendment could deal with the affected-cursor proof, for example by using R3's own clause to keep this surface out of the qualified matrix. Granting that isn't within this review's authority.
3. **Missing evidence.** The plan owner cites an existing carrier the preflight missed, and the Refine is resubmitted with B2 and B3 fixed.

Unchanged: the exact R3 gate; #119's prerequisites {118, 199, 201, 202, 203, 209, 210, 295}, where only #295 is open; #204 and #296 as stated; #282 as evidence only. Epic #2, C01 and production cutover remain excluded.
