[21:29:15]
**Dispositions: RESEARCH COMPLETE (negative). AUTHORITY HOLD.**

The negative result holds. I checked it against the replay script's assertions, and none of the overclaims below would change it. The authority hold is narrow: nothing gets authorized, but the close is missing records that M08b5 requires (see "Gates"). I didn't verify the findings file's SHA-256, since you said no tools.

## What the replay itself proves

The assertions run during the reopen establish these:
- **Child admission:** the child locator is unique in a separately approved root (`_approved_candidate` passes). There is exactly one epoch, and it belongs to the parent. The child source has no capture permission. Child `span_disposition` is EXCLUDED.
- **Child read and proofs:** `read_source(child)` refuses with "no admitted unbounded read". The selected child observation at ordinal 19 has a `stream_ref` different from the locator's, so it gets zero scope proofs and its route is HELD.
- **Parent:** the parent, child and epoch share one `stream_ref`. `read_source(parent)` refuses with "Expected the unique current native stream". The epoch-34 cursor authenticates on the parent file. `span_disposition` over [37, 47) is ELIGIBLE.
- **Overlap:** `OVERLAP_UNVERIFIED` is present, there is no covering aggregate observation, and the aggregate read limit is 0.
- **Cursor swap:** putting the child's locator into the parent's cursor refuses with "Private source identity changed".
- **Lineage:** the child's promptId, agentId and final-request usage match the parent's `toolUseResult`.
- **No mutation:** all five artifacts hash the same before and after, and there are no `*.sqlite*` files.

## Claims that exceed the evidence

1. **"Three observed runs."** Only two artifact sets have receipts: preflight (parent `89c6…`) and admission (parent `e3b8…`). The negative-controls receipt has no hashes and no run identity.
2. **"Armed … at ordinal 9 before any metered assistant row," "two observations and zero in the locator's stream," "called `verify_boundary` after the native child appended usage."** All three come only from the progress journal (`armed[...]`). The replay never checks that rows 0–9 have no metered assistant row, never counts the two observations, and never calls `verify_boundary` again. Neither receipt says where the second observation sits (its ordinal or stream). That gap matters for the frontier claim and for child accounting.
3. **What caused the `verify_boundary` refusal.** `_verify_next` returns the same message in two cases: no fresh boundary, or a checkpoint offset that didn't advance. The `_native_delta` excerpt is cut off before any `stream_ref` filter. So "zero same-stream candidates" as the cause rests on a progress counter whose computation isn't shown.
4. **"A native-only replay joined the original child checkout, child session … sidecar metadata, outer tool."** The script shown joins only promptId, agentId and usage. Session ID, metadata content, outer tool identity and checkout appear only as boolean receipt fields (`native_only_baseline_join`, `…_replayed_without_stdout`). The code behind them isn't included. Also, the child scanner frames 8, 16 and 17 have no registered checkout, and the report doesn't mention it.
5. **"The observed child inode and prefix matched on completion."** Only the preflight receipt supports this. The admission run doesn't record or check the inode.
6. **"Capture eligibility over the parent file is established."** `span_disposition` is keyed on (project, source, `stream_ref`), not on the file. The report itself says the parent and child share that `stream_ref` and that the guard can't tell their ordinal spaces apart. What's actually established is eligibility for parent-source stream ordinals [37, 47), whose epoch cursor authenticates to the parent file.
7. **"Ordinary scope read still refused the parent after both files shared its discovered session stream."** This implies the child caused the refusal. There's no baseline showing the parent read succeeding before the child appeared. The replay also filters parent-root discovery to the parent path, so it never shows that the child is the second match. The same message fires for zero matches or a path mismatch.
8. **"Failed the incarnation check."** The swap changed only `locator_ref`, and the refusal says "Private source identity changed". The code that would show which check fired isn't included.
9. **Receipt fields that are written-in values, not computed:**
   - `parent_aggregate_scope: "held"`: no parent observation was routed. "held" is an interpretation of "no cover", not a `RouteStatus`.
   - `fold_or_journal_mutation: false`: the only check behind it is the absence of sqlite files in `monitor/`.
   - `client_version: "2.1.318"`: a literal. Neither receipt contains the trunk SHA or tree.
   - The 285-pass pytest output isn't tied to the tree and doesn't name the tests that cover "wrong scope, handoffs, disabled/re-enabled capture".
10. **The child scope refusal is presented as independent evidence.** It follows directly from the missing child epoch and capture permission. It confirms the boundary failure but isn't a separate result.
11. **"Treating hook data as ownership" can't replace the seam.** No hook was tested. This is a policy constraint, not a finding.
12. **The negative controls don't record refusal reasons.** That includes the copied sidecar and the same-size prefix mutation, so "refused" doesn't show which guard fired.
13. **The span conventions differ between receipts.** Preflight reports [37, 46] and admission reports [37, 47). The receipts should state that spans are half-open.

## Capture vs. span

The report keeps these apart correctly in principle: capture eligibility is shown, while the route and ownership remain unproved. Item 6 above is the one place where the wording mixes them.

## Controls

**Tested at writer level, on this path:** the parent's lookup isn't unique, the child has no boundary, epoch, proof or read, the cursor swap is refused, and the bytes are unchanged.

**Diagnostic only, with no writer authority:** the eight lineage controls.

**Not tested for the child path**, though M08b5 requires them:
- an extra sibling child
- a missing child file while the parent result exists
- an ineligible child by permission or scope
- a permission change partway through the child span
- restart or recovery during the child
- a closure fence against later usage
- parallel or nested children
- the second child observation's ownership and accounting

## Gates

The kept gates line up with what M08b5 requires:
- `OVERLAP_UNVERIFIED` is preserved.
- The earlier frontier is preserved (registry bytes identical).
- #119 stays blocked and #204 stays in Refine.
- No authority is issued.

These are missing, and they are the reason for the HOLD:
- The report never says **M08b5 remains open**.
- It doesn't name **the exact failing proof gate** using M08b5's own gate names. Those are "exact original eligible ownership/source-span authority" (no writer-issued child boundary) and "terminal closed set" (no closure fence).
- It doesn't say whether the seam stays inside M08b5 or is a **changed parent plan**. A distinct child ordinal namespace changes the accepted capture and stream-identity model. If that counts as a plan change, M08b5 requires independent re-acceptance and a replacement native blocker on #119 that has been verified.

## Next seam

The seam follows from the evidence for two of its parts:
- A separate child namespace answers the shared-`stream_ref` guard.
- An exact parent lookup after sidecar discovery answers the parent uniqueness refusal.

Calling it the "smallest" seam isn't supported. The report itself says native files don't provide a writer-visible closure fence, yet the seam relies on "verify … native closure" without showing that a fence can exist. Closure should be stated as an open research prerequisite, not as part of something ready to implement.

**To lift the HOLD:**
1. State that M08b5 stays open.
2. Name the failing M08b5 gates.
3. Say whether the seam is inside M08b5 or a changed parent plan that needs re-acceptance.
4. Narrow items 1–13 to what the evidence supports, or add the missing receipts.
