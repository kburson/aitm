[16:39:58]
SOURCE_331: HOLD

Reviewed head `b55786b6` (tree `e932cc74`) against base `8be6d460`. The pre-image blobs `766ddf80` and `bb2a781b` equal the JIT pins, so the #330 merge did not touch either writable file. Only the three permitted paths change, with no coordinator or gate edits.

## Hold 1 – Pre-witness gap is lost when an untracked stream is enrolled through a reissue

**Source.** `packages/aitm-usage/src/aitm_usage/monitor_registry.py`, `_apply_grok_capture`, enabled branch with `current is not None`:
- Tracked streams are filtered out, then `generation = current.generation`.
- The `current is None and (not offers or grants)` grant rewrite is skipped.
- `additions = _GrokEpoch(identity, generation, cut)` is written for each untracked offer.
- Nothing is appended to `current.witnesses`.

**Behavior.** Trace:
1. Enable E1 applies on an empty root. This creates grant G(E1, gen 1, `witnesses=()`).
2. A qualified session S appears and completes bytes `[0, N)` before the coordinator enrolls it.
3. The owner queues enable E2. `enroll_grok` now must hold, because `monitor_scope.py` `enroll_grok` raises "An ordered Grok capture command is pending". So E2 applies first, through the reissue branch, and adds `_GrokEpoch(S, 1, cut N)` with no witness.
4. `grok_enrollment_gaps()` skips G (`if type(record) is not _GrokGrant or not record.witnesses: continue`).
5. A later `enroll_grok(S)` hits the readback early return (`prior is None and any(row.identity == identity and row.end is None ...)`).

**Result.** S's authenticated pre-witness range `[0, N)` under the active grant is never reported. The in-flight variant loses it too: the arm goes to `_GrokPending`, then commits through the same branch with no witness.

**Violated requirement.** The spec says "the authenticated pre-witness range is retained as unattributed unknown coverage". J8 says rows come from the grant's witnesses. J4 only fixes the generation and forbids a new grant. It does not permit dropping the witness.

**Fix within the three files.** When `current` is set, record each reissue-path addition as `_GrokFrozenCut(identity, cut)` in `replace(current, witnesses=...)`. Apply the same on pending resolution. Add a RED test: empty-root grant → S completes → queued reissue → gap row `[0, N)` persists after reopen.

## Hold 2 – Retired grants make the registry unloadable after an approval change

**Source.** `monitor_registry.py`, `_check_grok_grants`, which runs on every load after the duplicate-identity check:
- `approval.directory.identity != grant.root_identity or _LiveSourceTuple.from_approval(approval) != grant.installation` raises `LedgerError`.
- `_source(view, grant.source_id)` is also called unconditionally.
- Neither check is gated on `grant.active`.

**Behavior.**
- The spec expects an explicit regrant after a root change, with "earlier provenance readable" and "preserving historical ended grants and gaps".
- A root change requires a new approval with a new directory identity. The retired grant keeps the old `root_identity`, so the next load raises "Grok grant installation changed".
- Revoke has the same problem, because `_source` sees the approval missing. An installation-tuple change does too.
- No non-Grok path in the diff retires or rebinds grants. The only replacement test (`test_replacement_stream_or_profile_requires_exact_new_owner_authority`) covers profile revision and incarnation replacement. Neither is checked here, and the spec's "source replacement" case is not covered.

**Fix.**
- Apply the root and installation equality only to active grants.
- For retired grants, validate only receipt provenance and witness/epoch consistency.
- Add a root-change (or re-approval) regrant test showing that the old gap rows survive reload.

## Verified, no hold

- **J1, J10 – codec.**
  - Legacy #329 bytes round-trip through the local `_OldRegistryWithGrok` mirror.
  - The grant view fails closed in the old reader.
  - There is no codec edit and no extended-empty encoding.
  - Only the fixture is imported from `test_monitor_grok_capture`.
- **J2 – grant construction.**
  - The grant is built in `_apply_grok_capture` and published through the literal receipt tail.
  - `__post_init__` binds only the digest to the enable. The extra checks are structural.
  - The receipt, permission and no-later-disable checks run at load.
- **J3 – reissue.** A reissue keeps G's `command_id`. `test_reissued_enable_preserves_an_armed_stream_and_original_grant` shows one generation and readback-only repeats.
- **J5 – derived grant.** The derived grant uses the latest APPLIED enable and stops at a later APPLIED disable. Its generation is the maximum among active epochs at the live profile, and it holds when there are none.
- **J6 – mint.** The `_grok_capture_offer` delegation is behavior-identical, since the hoisted `next(..., None)` calls cannot raise. One offer goes through `registry._grok_capture_offers` with `active=()`, and no command is queued.
- **J7 – `enroll_grok`.**
  - It uses `inbox.publication()` plus `view(_confirm_publication=True)`, with inbox type, root and lease checks.
  - It holds on pending same-edge commands and on `_GrokPending`.
  - It checks the grant before `_capture_material`, as the rejected-receipt test shows.
  - It rechecks the identity, checks the lease and view before `_save`, and confirms by readback.
  - It never discards.
- **Arms.** Arms hold on a wrong terminal or a rewritten prefix with the view unchanged. A committed arm excludes the in-flight turn, and the later hookless turn routes.
- **Disable.** A disable retires only the active grant, ends epochs atomically, and turns an unresolved arm into an unknown gap row that survives reload.
- **J8 – gap rows.** Rows are frozen and sanitized: an opaque pseudonymized edge, stream and incarnation refs, the existing `COVERAGE_GAP` code, and no row for an empty range.
- **J9 – receipt retention.** It was not re-inspected here, since that is outside the diff.
