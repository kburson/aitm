[10:16:17]
REFINE_122: HOLD

**Verdict basis.** Most of the scope is sound. Recovery, external-effect boundaries, receiver-retry safety, the test matrix and the gates all match the accepted M12 excerpt and the R3 amendment. The amended Claude coverage case is the exception. Its candidate authority does not reconcile with the closed dependency or the supplied source anchors.

## Blocking findings

1. **Candidate authority is unanchored.**
   - The amendment says to fence "the verified M09 journal-only coverage candidate", which would come from #119.
   - The Refine says to "Consume #310's exact journal-only coverage/dispute candidate."
   - #310 is not in `blocked-by`, its state is not supplied, and no anchor shows it was delivered at `ab9db800`.
   - Either #119 delivers the candidate, which makes the #310 reference wrong, or #310 does, which makes the dependency graph incomplete. Refine cannot pass with the producer of the fenced object unresolved.

2. **The source claim conflicts with the anchors.**
   - The Refine says #119 returns only an internal ACK receipt, "not a journal-only PublicationCandidate."
   - But `monitor_journal.py:326` defines `PublicationCandidate`, and `monitor_journal.py:1205` defines `publication_candidate(self, change: JournalChange) -> PublicationCandidate`.
   - **Missing fact:** whether `publication_candidate` accepts the Claude coverage `JournalChange` at `ab9db800`.
   - If it does, the "ACK-backed fence" design hole disappears, and the contract input is simply `protect(candidate)`.
   - If it does not, the M09 candidate the amendment calls "verified" does not exist at the pinned commit.

3. **Scope widened.** The amendment covers a *coverage* candidate only. The Refine adds "dispute" without amendment authority. Remove it, or cite the accepted text that includes it.

4. **The core design question is deferred to JIT.** JIT may accept exact APIs, codec, storage layout and ownership. But Refine must fix *what* is authenticated and fenced: the candidate, or the ACK plus receipt. "JIT must define the smallest honest binding" leaves the authority of the fence's primary input open, and that blocks a credible 3.8h estimate.

## Non-blocking gaps to close in the same revision

- **Rollback exclusion.** `backup.py:618 _restore_stopped` anchors restore. **Missing fact:** the anchor where the snapshot rollback set is enumerated. That anchor is needed to prove the private witness path sits outside it.
- **Claude test name.** The Refine checklist says "amended Claude coverage-only fence test." Name `test_claude_coverage_gap_cannot_escape_before_recovery_fsync` exactly.
- **No synthetic receipt.** Restate the amendment's rule that no destination receipt is issued for a journal-only coverage change. "Without forging a coverage candidate" covers the inverse risk, not this one.
- **#124 edge.** The Refine says #124 owns export and reconciliation integration, but #124 is not in `blocking` (#123, #126). **Missing fact:** whether #124 depends on #122 through another path.
- **Four-hour cap.** 3.8h is tight for:
  - the witness work: write-ahead witness, rollback exclusion and restore reconciliation;
  - the receiver work: export intent, receiver evidence and the verifier fixture;
  - four tests with before/after-append injection.

  Make the split trigger concrete. If resolving finding 2 needs a new journal-side candidate API, split the receiver-evidence slice (`record_export_intent`, `record_receiver_evidence` and the interrupted-export test) into its own leaf.

## Confirmed as adequate

- **Recovery.** Monotonic authenticated witness, reconcile to the last verified common sequence, a prepared record constrains replay without claiming exposure, and stale, unsupported, conflicting, modified or custody-lost witnesses are refused.
- **External-effect boundary.** No destination work inside the witness transaction. #123 owns view selection and #124 owns transport. Existing owners are preserved.
- **Receiver retries.** Proof binds the triple of receiver, key and payload digest through a pinned verifier. Unknown or conflicting proof is held. A resend after verified absence uses the identical key and bytes.
- **Observable tests.** The three original tests plus the failure matrix: before/after append, success, repeat, wrong receiver/key/bytes, missing or conflicting proof, and finite restart. Green runs with `test_monitor_journal.py` and `test_monitor_delivery.py`.
- **Gates.** Signed-hosted, independent source, delivery and Close gates are retained. Coverage-gap policy, cutover, C01 and Epic #2 stay excluded. JIT acceptance of exact APIs, codec, storage layout and ownership remains independent.

## To reach PASS

1. Name the single candidate producer: #119's `publication_candidate` (proven against a coverage `JournalChange`), or #310 added to `blocked-by` with a closed state and an anchor.
2. Remove "dispute" or cite its authority.
3. Correct the ACK statement to match `monitor_journal.py:1205`.
4. Supply the snapshot-set anchor and the #124 dependency fact.
5. State the concrete split trigger.
