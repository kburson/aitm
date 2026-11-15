[21:40:00]
# REFINE_300_R2: PASS

**Basis:** I reviewed only the pasted Refine text, the split plan, the prior HOLD, the PR #306 and #303 state JSON and the code excerpts. I had no shell or file tool here, so I didn't recompute the SHA or read the file at that path. The pass covers Refine only. It doesn't approve the JIT and doesn't authorize any code.

## What holds up

- **Scope is bounded to the journal.** #303 is closed, and PR #306 is merged at `6b64ea87`, which matches trunk. That means everything that caused the last HOLD (profile default, activation authority, tuple sources, approval semantics and the reserve recheck) is now delivered upstream. What's left in #300 is a catch in `prepare`, a recheck, one insert, a v6 table and a readback. Service, cursor, ACK, report and registry encoding are all excluded.
- **The producer contract is real and works as a policy-only proof.**
  - `_LiveSourceUnavailable.decision` is either `_LiveExclusion(source_id, generation, installation)` or `None`.
  - A decision is only issued when the call is `observed` and the approved directory is still `_pinned`. So a lookup that is unauthorized or has lost its root can't produce one, as the Refine requires.
  - Calling `_require_live_source(approved, observed=True)` again reads only registry metadata, `source_evidence()` and `profile.current`. It reads no payload.
  - Comparing the frozen dataclasses for equality gives a clean "same decision" test, and a recheck that succeeds correctly invalidates the old decision.
  - If a profile is copied or forged, it fails `validate_source_ref` and falls back to the keyed `closed-v1` generation. It can't inject its own generation.
- **The live metadata check is in the right order.** The recheck happens inside the guarded write transaction against the registry source, root, lease and consent, and the original refusal is raised only after the commit. A refusal with no decision stays an ordinary error.
- **Compatibility is sound.**
  - Allocating sequences from `commits`/`_tip` means no second sequence counter.
  - Upgrading v4 to v6 adds both the paired and coverage tables, so paired settlement isn't skipped. `_enable_paired` is already a no-op on v6.
  - Reads on v4 and v5 return empty without changing the schema.
  - v1–v3 still go through the existing upgrade to v4 (`_current_version` enforces at least v4).
  - Old binaries still refuse v6 through the version set check in `_validate_identity`, and rollback stays with #126.
- **Sizing fits.** 0.6 + 0.6 + 0.6 + 0.7 = 2.5h, leaving 1.5h under the 4h cap. The test list is dense, but it reuses fixtures that already exist.
- **The existing gates are unchanged:** Test, review, delivery and Close.

## JIT must freeze these, and should hold if any can't be shown

1. **Producer call site.** Cite the line where `read_source` calls `_require_live_source(..., observed=True)`, and show the decision reaches `prepare` without being re-wrapped. If it doesn't, the feature never fires.
2. **The "existing policy-only metadata confirmation seam".** This seam isn't in the supplied evidence. Today `_fresh_view` needs a `_Read` (a batch plus progress), and the refusal path has neither. Name the exact function that rechecks consent by source ID without a batch.
3. **What a failed recheck does.** In the decision branch of `_require_live_source`, `self.source_evidence()` runs outside the `try`, and the branch never calls `lease.check()`. Specify that any recheck error or mismatch publishes nothing and raises the original refusal (or exactly which error is raised instead). The journal transaction also has to check the lease itself.
4. **Variants with no producer.** #303 only ever emits the installation variant with unknown extent. Either limit the v6 encoding to that, or carry "broader authorized root" and "known proven range" only as strictly rejected or reserved discriminators, each with a test. Don't ship code paths that can't be reached and aren't tested.
5. **Schema edits.**
   - In `_supported_schema`, change `version == _PAIRED_SCHEMA_VERSION` to `>=` and add coverage at v6.
   - Add v6 to the allowed set in `_validate_identity`, and keep rejecting v7 and later.
6. **Commit-gap audit.** Show that no existing reader assumes every row in `commits` belongs to a claim, dispute, disposition or paired settlement. Also show that `JournalView.dispositions` and `settlements` never surface a coverage-only commit.
7. **Who can read the data.** Name the authorization for `coverage_changes(after_sequence)` and for direct table reads. Freeze the canonical bytes and columns, and confirm the name doesn't collide with #209's coverage projection.
