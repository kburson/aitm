[22:11:48]
**HOLD.**

The plan says B gets an ordinary `VerifiedBoundary` at ordinal 10. #269's own record contradicts this, and the packet doesn't explain the difference. The other gaps are wording and evidence gaps that can be fixed without changing any gate. I only saw the code excerpts in the packet. I did not see `_native_delta`, `_stream`, `_timeline` or `_require_direct_proof`.

## 1. B approval and a real VerifiedBoundary (M06/M07)

**Approval is sufficient.** The preflight shows the unmodified `ControlInbox` and `apply_pending` commit B's edge with no epoch. A disable on the child leaves A's edge intact, and the state survives reopen. M06 consent holds.

**The boundary is not proven.**
- In #269 the frontier was set at 9 and rows 10 and 19 were appended. `_verify_next` still returned "The next native capture boundary is unavailable", with 0 boundary candidates in the same stream.
- The offset did advance, so the fault is that `_native_delta` produced no boundary with an ordinal above 9.
- Row 10 is an observation ordinal, not a boundary the existing code produces. If the existing code never treats it as one, `enroll_stream` cannot get a real `VerifiedBoundary` unless the boundary definition changes. That would be an M07 capture-model change.

**Two more points in this area:**
- **When B enrolls.** Task 2 calls the qualification "read-only", but `enroll_stream` calls `_save`. The plan should say whether B enrolls live under the lease, or after exit from the saved pre-10 frontier through ordinary `_verify_next`. It should also say why that is not post-hoc admission.
- **"Before dispatch".** The writer cannot control when the model calls Agent. "Before dispatch" has to mean before the process is launched. A missed observation window counts as held, which is correct. Repeated misses would still use up the four hours.

## 2. Source-ID isolation and re-proving A's locator

**Isolation depends on one unstated precondition.** B sits inside A, so A's discovery also finds the sidecar.
- If the sidecar has the parent's stream_ref S, A's ordinary path is ambiguous and refuses. That matches the 2 matching locators in #269.
- If its stream_ref differs, A's ordinary capture could enroll the child as a new stream. Two sources would then hold authority over one physical file.
- The plan should require that the sidecar's stream_ref equals the parent's under the pinned scanner, and refuse otherwise.

**The second locator is still not recorded.** `parent_epoch_cursor_refused_on_child_incarnation` suggests it was the child, but #269 never recorded its path or incarnation. Record both from the saved artifacts before starting.

**A's epoch key does not bind a physical file.** (project, A, S, 34) would authorize any S-ordinal ≥34, including a longer child's rows. The private method must refuse any projection under A from the sidecar path. Picking the parent is not enough.

**Nested copies of child requests.** The parent span [37,47) contains copies of the child's requests in the progress records.
- The plan should say that no nested copy is eligible under A, and that the child's `ClaimEvidence` uses B's position only.
- "Refuse repeated identity across representations" conflicts with "join on an exact request match". Fix it as: exactly one nested copy and one raw record per request ID; anything else refuses.

**There is no named integration path for A.** For `resolve_route` and `_evidence` to work, A's covering observation must be a proof inside an issued `ScopeView` (`_ISSUED_VIEWS`, `scopes._proofs`). Ordinary batch issuance runs the uniqueness check, which fails with 2 matches. The plan must name:
- the exact private `ScopeState` issuance call,
- how it registers the batch in `_batches`, so that `_recheck_batch` covers it,
- why no ordinary entry point can reach it.

**The child's route needs two checks.**
- Confirm that `_stream()` and `_timeline` include `source_id` in their key. If not, A's scope events would mix into B's timeline, and A and B share S with different ordinal spaces.
- Confirm whether the scope timeline at child ordinal 19 needs rows [0,10). If ordinary `ScopeState` does not read rows before the epoch for scope, the child resolves as UNASSIGNED or HELD.

## 3. Receipt and restart authority, span, closure

**Specified well enough:**
- Spans are defined by rule: authority [10,20), origin witness [0,20), parent prompt-to-result. Both child requests fall inside the authorized span, so the earlier item 4 is met.
- Closure is concrete: process exit, a single task, fixed sizes and prefixes, invalidation on late appends, and the stated lock order.

**Gaps:**
- **A's epoch in a fresh session.** The session is new, so "pin the existing A epoch" needs explaining. The plan should say how ordinary capture enrolls A before the covering prompt (in #269 the epoch was at 34 and the prompt at 37).
- **What B may contain.** List the allowed set exactly: the agent `.jsonl` and its `.meta.json`. Otherwise the metadata file would trip "a later unrelated file holds".
- **Receipt write order.** Registry enrollment and receipt publication are separate writes. A crash between them leaves a B epoch with no receipt. The plan should say that state issues no proof, and that the resulting ordinary B behaviour is acceptable: the child is eligible on its own and the parent stays OVERLAP_UNVERIFIED.
- **Expiry.** Give the actual expiry value.
- **What the receipt is not.** The sidecar check can be recomputed from B's registry epoch, so the receipt holds no authority. The only fact that exists solely in the process is the [0,20) origin witness, and it confers no eligibility. Say both explicitly.

## 4. Four-hour cap

The cap is not credible as written. It is bounded only if the boundary replay and the second-locator record (below) pass before the clock starts, and the `ScopeState` path needs no new issuance logic. The most likely overrun is Task 3: the 14-case refusal matrix plus the local and hosted suites.

## Fixable without changing gates (do before the clock, then re-run JIT)

1. **Replay the boundary.** Run the unchanged `_native_delta`/`_verify_next` on the saved #269 child artifact (`a55fde…`), with B approved and the frontier on the prefix before row 10.
   - Pass means exactly one new boundary, at 10, plus a recorded reason why #269 found 0.
2. **Record the second locator and confirm the stream.** Record its path and incarnation, and confirm the sidecar has stream_ref S.
3. **Name the integration call.** Name the private `ScopeState` issuance call, and confirm `_stream` and `_timeline` include `source_id`.
4. **Fix the wording:** when B enrolls, where A's epoch comes from, the nested-copy rule, B's allowed files, receipt write order, and the expiry value.

A PASS is likely if items 1–3 hold.

## If the gaps can't be closed

- **If item 1 fails,** the existing code doesn't produce the child boundary, so this needs a capture-model change. Hold #270, keep #204 → #119, and send the change through parent-plan re-acceptance.
- **If items 1–3 hold but the work won't fit in four hours,** split along the checkpoints into three leaves. Each sits inside M08b5 ahead of #204. This adds recorded blockers on #204 without changing any gate:
  - **270a:** native qualification and closure trace, issuing no registry authority.
  - **270b:** registry and scope qualification, plus the receipt definition.
  - **270c:** restart and the refusal matrix.
