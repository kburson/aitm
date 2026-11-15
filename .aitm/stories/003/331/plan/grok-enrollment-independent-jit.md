[15:46:46]
**JIT_331: PASS**

This is bound to base `30e1a13d64a88d43e7447e2199c0e389324a0857`. Binding pins J1–J10 below become part of #331's Develop contract. If any pin fails, the item goes Stop → Refine. No gates change.

## Verified against literal evidence

- **Delivery.**
  - #329 is natively closed with Project status Done.
  - PR #332 merged as `30e1a13d`, which is the base, with ordered parents and zero diff verified.
  - #329 is #331's only blocker. #121 is open and downstream.
- **Applied-command proof.**
  - `CaptureChange` has exactly `(project_id, source_id, enabled)`.
  - `ControlCommand` has `(command_id, payload, format)`, and its `__post_init__` rejects any format other than v1.
  - `payload_digest` is the sha256 of the full `_encode(ControlCommand)`.
  - Rebuilding the command from `receipt.command_id`, the edge and the enabled bit is therefore fully determined. Carried item 1 is closed.
  - `apply_pending` appends the receipt in order, runs `_save`, then calls `discard`, all inside `inbox.publication()`.
  - A REJECTED receipt carries the same digest but a distinct status, so it cannot pass as APPLIED.
- **Empty root.**
  - The literal `change.enabled and not offers → BoundaryUnavailable` is the single change point.
  - The `evidence_for is None` hold comes before it, so `test_monitor_grok_capture.py:138` is unaffected.
  - `_grok_capture_offers` requires offers ⊇ active, so zero offers implies zero active epochs.
- **Codec.**
  - The untagged UnionType decode requires an exact key-set match.
  - A `_GrokGrant` or witness alternative with distinct fields leaves legacy record bytes unchanged.
  - An old binary fails closed on the unmatched dict.
  - A grant-only view is non-empty, so the rule against extended-empty encodings still holds.
  - The existing helpers filter on `type(record) is`. Grant rows are therefore invisible to `_grok_span_disposition`, `_grok_read_fences` and the #329 apply paths.
  - The disable path's `item in active` check cannot match a grant.
- **Prospective safety.**
  - A stream identity with no epoch gets a read limit of 0, because `committed = max(..., default=0)`. Nothing before the witness is read or excluded before the commit.
  - After the commit, spans before the start are EXCLUDED and spans after it are ELIGIBLE.
  - So the post-witness hookless turn stays available with no change to disposition or fences. Carried item 4 is closed.
- **Arm semantics.** With `enabled=True`, the #329 arm branch:
  - holds on an unverified terminal;
  - holds on competing terminals;
  - holds on a prefix change;
  - otherwise commits at the verified terminal end, so the in-flight turn is excluded.
- **#330.**
  - The writable sets are disjoint.
  - #330 reads `_take_grok_admission` and the `_GrokEpoch` shape, both unchanged, and reads the registry only.
  - The `monitor_scope.py` blob `bb2a781b` matches #330's post-#329 pin.
  - There is no edge between #330 and #331.
- **Edit paths.**
  - Writable: `monitor_registry.py` (`766ddf80`), `monitor_scope.py` (`bb2a781b`), and `tests/test_monitor_grok_enrollment.py`, which is absent at base.
  - Read-only: the codec in `types.py` (`5417678e`), `monitor_control.py` (`5a8bacaa`), `test_monitor_grok_capture.py` (`845e28e1`) and `conftest.py` (`60db42c9`).
- **Authority.**
  - Watch and wake events only trigger a check. Authority comes solely from the owner-applied grant proven by its receipt.
  - No command is synthesized, and nothing is captured automatically from observation.

## Binding pins

- **J1 – Codec entry check.**
  - The first RED test encodes the retained #329 bytes and a grant view.
  - It must confirm that `grok_records` takes the untagged UnionType path. The trigger for the tagged `kind` branch is not in the evidence.
  - If adding an alternative needs a tag table or a codec edit, Stop → scope.
- **J2 – Construction order.**
  - The grant row is added in `_apply_grok_capture`, reached through `_apply`'s Grok branch.
  - The generic receipt tail of `apply_pending` stays literal and supplies the single `_save`.
  - `_GrokGrant.__post_init__` checks only that `digest == ControlCommand(id, CaptureChange(edge, True)).payload_digest`.
  - The receipt binding (APPLIED, same digest, no later applied disable) is validated on load or derivation, not during transient construction.
  - Otherwise the view built before the receipt exists would raise, and the command would hold forever.
- **J3 – Grant provenance.**
  - A grant stays bound to the ID of the APPLIED enable that created it.
  - It is valid only if that receipt is APPLIED and no APPLIED same-edge disable follows it.
  - A reissue receipt is a later enable and does not rebind the grant.
- **J4 – Reissue on an edge with an active persisted grant.**
  - Offers for identities the grant already tracks, as a witness or an arm, are dropped on the registry side.
  - Untracked present streams follow #329's path at the grant's capture generation, with no generation bump and no new grant.
  - Without this rule, a reissue would arm a stream the grant already arms, and `enroll_grok`'s pending-hold would deadlock against it.
  - Edges without a persisted grant keep #329's literal `1+max` path.
  - `:750` and all of `test_monitor_grok_capture.py` must pass unmodified. If any existing test pins the callback-present empty wait, Stop → Refine.
- **J5 – Derived grant on a populated #329 edge (first enrollment).**
  - The capture generation is the maximum generation among the edge's active epochs at the live profile.
  - If there are no such epochs, the enrollment holds.
  - Validation accepts pre-grant epochs at or below that generation. Every witness-backed epoch must equal it.
- **J6 – Mint.**
  - Refactor `_grok_capture_offer` into an internal helper that takes `(previous_cut, arm)`. The existing signature delegates to it byte-exact.
  - Enrollment issues exactly one offer through a registry-side verifier that mirrors `_grok_capture_offers`:
    - sink set and reset;
    - lease, profile and installation identity;
    - edge, surface, profile and executable;
    - ref validation;
    - live and root recheck.
  - `CaptureChange(edge, True)` is rebuilt from the grant and never queued.
- **J7 – `enroll_grok` contract.**
  - **Lock and custody:** it runs inside `inbox.publication()` with `view(_confirm_publication=True)`. It requires `inbox.root` to equal the registry root and requires the writer lease.
  - **Holds on:**
    - any same-edge `CaptureChange` in `iter_pending`;
    - any `_GrokPending` on the edge;
    - an invalid or stale grant.
  - **Result:** it returns `None` on commit or exact readback, raises `BoundaryUnavailable` for a retryable hold, and raises `ConflictError` or `LedgerError` for invariant or custody failures.
  - It never discards.
  - **#121 obligation:** it must not be called inside a held publication or an `apply_pending` callback, because the lock is not reentrant.
- **J8 – Gap rows.**
  - The extent is `[0, committed witness offset)`. For arms, this includes the excluded in-flight turn.
  - A retired unresolved arm reports an explicit unknown extent. An empty range emits no row.
  - Rows are frozen and carry the surface, an opaque edge ref, the stream and incarnation refs, the range or unknown, and the existing `COVERAGE_GAP` value.
  - Rows come from both active and retired grants, independent of live admission.
- **J9 – Receipt retention.** If any receipt retention or compaction exists at base, Stop. Grant proof depends on retained receipts.
- **J10 – Tests.**
  - Import only fixtures and helpers from `test_monitor_grok_capture`, with no `test_*` names. Confirm the configured import mode allows this.
  - Prove the old binary fails closed by using a local mirror of the #329 `_RegistryWithGrok` shape.

## Estimate

Keep 2.75h (0.95 / 1.15 / 0.65), with the 1.375h checkpoint and the 4h cap.

- The checkpoint requires the grant derivation, the J1 and J2 codec checks, and the first prospective-cut proof.
- The pins fit the existing buckets. J4 and J6 are the likeliest overruns.
- If either needs a file outside the three or pushes past 4h, Stop → split.

## Not verified (non-blocking)

- Whether the Project Rank field accepted 249.5 for #331. No project JSON for #331 was supplied.
- #121's consumer side of J7 and J8. #121's own JIT pins it.

All gates are unchanged: separate locked local Test, signed hosted Test, independent source review, protected merge, native Close, and the accepted scope exclusions.
