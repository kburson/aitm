# Verdict REVISIONS REQUIRED

Reviewed all 237 physical lines of the #100 plan in six separate bounded reads. The plan SHA-256 is `2ac103dd7130a01112b7182da7e59c5f4f0e7bde7482759692f9511f0ed2b330`. The accepted spec and both spike reports matched their recorded digests.

## Blocking findings

1. **High — Make schema compatibility and cutover executable.** Plan lines 41–43, 55–56, 87–94, 195–211, 231–233. Spec lines 65–71, 80. M03 owns the schema change, but the existing backup and restore paths compare against a single `SCHEMA_VERSION`, and the installer probes a single schema fingerprint. M15 owns service enablement before M16 supplies adoption and recovery. The plan leaves the enforcement boundary between isolated rehearsal and production activation implicit.

   **Required change.** Assign schema compatibility changes and their tests to the leaf that introduces the format, or defer the format change and its consumers to a single dependent leaf. Define the guarded operator sequence for backup and checkpoint verification, legacy stop, guard transfer, adoption, readiness verification, and first write. Make production activation require the approved cutover and exact target qualification. Specify how recovery establishes the independently retained current tail before releasing replay.

   **Test acceptance.** On representative #83 state, prove the new runtime can read and verify the old store and backup before migration, preserve the fixed export byte for byte, and refuse a competing writer. Inject failure before and after the first new write. Verify prior-service recovery before the write and preservation of accepted observations afterward. A matching old backup and old witness must hold affected replay.

2. **High — Assign the durable transition from acknowledged usage to disputed or superseded usage.** Plan lines 109–111, 127–148, 168–184, 188–193. Spec lines 23, 47, 55, 59–61, 76, 80. M07 calls for a post-ACK conflict test before M09 introduces ACKs. M08 reserves revisions and M09 creates publication candidates from write receipts, but neither owns publishing a dispute against an existing ACK when no new project write occurs. The same gap affects a late folded parent after a child has already been published.

   **Required change.** Keep native-order unit tests in M07 and assign the post-ACK transition and its integration tests to the downstream owners. Specify how a durable route or coverage change produces a new fenced view, how a separate CLI invocation reopens that immutable snapshot, and how existing `rollup` and `export --as-of` entry points stay confined to their permitted views. Define the handoff from `FencedPublication` to the view consumed by reports and exports.

   **Test acceptance.** Publish and reopen a snapshot across a process restart. Deliver competing handoff receipts in both orders, including after ACK. Verify the old snapshot stays identical, the current report and compatible export omit the disputed span, and a pending undisputed revision leaves the prior published revision visible. Publish a child before a late folded parent and prove each snapshot counts at most one covering representation. Exercise the public CLI while fence persistence is blocked.

3. **High — Complete the immutable receiver delivery and reconciliation path.** Plan lines 170–175, 186–193, 208–211. Spec lines 55, 61, 69, 76, 80. M12 defines an export intent and M14 names a reconciliation queue, but the plan leaves receipt ingestion, durable reconciliation state, and the supported operator path unassigned. The restart behavior after a receiver accepts a payload but before the monitor records acceptance is therefore underspecified.

   **Required change.** Give M12 and M14 explicit ownership of the intent, receipt, and reconciliation interfaces. Bind them to the exact receiver, immutable key, and payload digest. Define how the operator inspects an uncertain delivery and supplies verified receiver evidence. Cover matching acceptance, verified absence, conflicting evidence, and unavailable evidence. Keep C44 implementation outside #100.

   **Test acceptance.** Interrupt delivery after send and before local acknowledgement. Recover the original receipt when the receiver confirms acceptance. Allow an exact retry only after verified absence, and keep unknown or conflicting outcomes on hold. For a time correction, prove the original key, payload, and receipt survive, the compatible export withholds the correction, and the current report counts the corrected observation once.

4. **High — Give the operator commands and provider-side producers owners.** Plan lines 98–103, 107–130, 150–166. Spec lines 15–17, 21–23, 29–43, 47. #101 report lines 42–45. M06 names registration and capture commands, M07 defines an internal handoff method, and M10 defines the wake receiver. No leaf owns the complete submit-and-observe path for handoff, evidence-backed disposition, or explicit park. The plan also leaves provider hook installation and the production Grok scope producer between adapter, control, and qualification leaves.

   **Required change.** Name the supported operator or integration entry points for root approval, scope and handoff submission, disposition, park, and command status. Assign the provider-side hook sender and owner-approved Grok marker producer. Specify which coordinator leaf consumes commands and joins them to native evidence before application. Update file ownership and dependencies for any shared CLI, adapter, or control files.

   **Test acceptance.** Exercise the supported entry points through the coordinator. Show queued and applied status separately. Reject an unauthorized scope proposal, a mismatched native receipt, and a stale stop. Show an approved hook sends a bounded wake, a failed wake lets the provider proceed, and an explicit park triggers catch-up without changing scope.

5. **Medium — Move native capability discovery ahead of implementation commitments and make release cases explicit.** Plan lines 59–65, 98–112, 220–233. Spec lines 45–47, 71, 75–80. #101 report lines 42–45 and #102 report lines 19–21, 39–44. M04 makes the Linux Codex receipt fixture conditional, while M19 owns qualification and documentation files only. If the Linux carrier differs from the assumed interface, the plan has no explicit owner for the resulting product change. The release scripts also leave the required two-turn Grok story proof implicit.

   **Required change.** Make native carrier discovery a prerequisite for freezing each affected adapter contract, or name a dependent implementation slice and its retest path. Assign the deterministic and live cases to concrete leaves. Require two distinctly story-bound Grok turns through the real admission path on each claimed target, including resume and a separate hookless eligible turn. Require Linux-native receipt and continuity proof per provider and architecture, with the real systemd user manager and ext4 checks tied to the exact candidate.

   **Test acceptance.** On each claimed target, show the two Grok turns settle once each under their verified scopes and the hookless turn counts once in the correct interval with story scope unattributed. In deterministic tests, show a complete qualified turn with no snapshot counts with a corroboration gap, while snapshot-only or contradictory evidence cannot create a charge. Container-only evidence, a wrong build or architecture, or a missing native story carrier must leave the affected release gate open.

## Optional

- List M17’s `monitor.py` edit and M18/M19’s shared receipt tests and runbook in the ownership table. The current dependencies already serialize those edits.
