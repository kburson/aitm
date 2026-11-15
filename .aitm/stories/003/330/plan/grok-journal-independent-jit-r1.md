[15:34:23]
**JIT_330: HOLD**

The supplied evidence proves the gate, the codec and the writer type. It does not prove three of the four dependencies that Refine marked "not proven", and it does not prove the R2, R3 and R5 inputs. No edit outside the three files is proven necessary yet. Several conditional ones are listed below.

**Verified**
- **Close and graph:**
  - #119 is closed and its Project status is Done.
  - #329 is closed and Done. PR #332 merged as `30e1a13d`, with ordered parents and zero diff verified.
  - #121 is the sole open dependent.
- **Base:**
  - Journal blob `e64622a3` is unchanged, so the swallow and the double admission are present in the shown `prepare`.
  - Scope blob `bb2a781b` carries `_take_grok_admission`.
- **Codec (dependency 1):**
  - `convert` handles `UnionType` by trying each choice in order.
  - A dataclass encodes only when `type(value) is expected` and decodes only on an exact key-set match.
  - So a `UsageObservation | GrokObservation` field on the journal-local `_UsageMaterial` needs no codec edit.
  - Goldens are present: material `d74678eb…`, claim `bd2c49dc…`, revision `2ae5685d…`. The evidence reports `codec_union_legacy_bytes_equal: true` and `current_repo_code_changed: false`.
- **Schema:**
  - The `progress` key is five TEXT columns with no CHECK, and `cursor` is a BLOB.
  - `claims.payload` is a BLOB.
  - Progress and claims therefore need no DDL.
- **Writer:**
  - `MonitorRevision.observation` is `MonitorObservation | GrokObservation`.
  - `_monitor_revision` is the only branch point. The `monitor-delivery-row-v1` key, `commit` and `_readback` need no change.
- **R1 last clause:** `cursor_for` → `_stream` already refuses any non-`CandidateSource`.
- **R5 changed prefix:** `_claim` already holds revision 1 with a changed digest, and holds a revision ≠ 1 that has no existing row.
- **Estimate:** 3.75h is within the 4.0h cap.

**HOLD reasons**
1. **R1 / dependency 3, single admission:**
   - The shown `prepare` calls `read_source(source_id, locator, cursor=prior)` with no admission and discards the `_grok_admission` result. So `read_source` appears to acquire its own admission.
   - `_take_grok_admission` only validates and pops. No supplied source shows a #329 read entry that accepts a caller-held `_GrokAdmission`.
   - Also unshown: the container type of `_grok_admissions` (weak or strong, which the discard path depends on) and the return type of `_grok_admission`.
   - If no such entry exists, a `monitor_scope.py` edit is required, which means Stop → Refine.
2. **Dependency 2, routing:**
   - The source for `resolve_route`, `_fresh_view` and `ScopeView._proofs` is not supplied.
   - Nothing shows that a Grok proof yields an `_ObservationProof` with `position`, `end` and `eligible_projects`.
   - Nothing shows that it routes marked work to its story, or hookless work to the project only.
   - R3 and R4 depend on this.
3. **Dependency 4, observation type:**
   - `MonitorRevision` admits `GrokObservation`.
   - Nothing shows that #329's `proof.observation` is that type, or that it carries the `revision`, `time_basis` and `native_surface` that `_claim` and `RoutedRevision` consume.
4. **R2, progress:**
   - The `StreamCursor` and `GrokCheckpoint` definitions are not supplied.
   - Unproven: that the batch cursor carries a `GrokCheckpoint`; that it exposes an authenticated byte offset, locator and incarnation; that every field is allowlisted by the codec.
5. **R3, marks and holds:** No source shows the Grok boundary or mark types, or that #117 events and holds in `ScopeView` can carry a Grok `native_boundary`.
6. **R5, epochs and surface:**
   - `_evidence` reads `registry.epochs`. Where the #329 Grok epochs live, with their profile generation, physical source and boundary, is unshown.
   - `NativeSurface` membership for the Grok surface, which `ClaimEvidence.surface` requires, is unshown.
7. **R7, R8 and R10, codec map:**
   - The schema excerpt stops at the base `_SCHEMA`. The schema version 5–7 paired, coverage and delivery tables are unseen, so the absence of a provider or surface CHECK on delivery and ACK rows is unverified.
   - The claim-key (source key) derivation and the `reserve_delivery`/ACK source are missing.
   - So the required claim, digest, source key, progress, seal, commit and ACK map is incomplete, and no re-estimate is possible.
8. **Pin:**
   - The blob list has no commit label. It is not bound to `30e1a13d`, even though the codec evidence names that trunk.
   - The writer, store, types, adapter and registry blobs have no earlier reference, so drift cannot be checked.
9. **Test path:** The existence of `packages/aitm-usage/tests/` is not evidenced. Neither are the locations of the #329 retained matrix and isolated issuer.

**Extra module or impossibility:**
- None is proven.
- Conditional candidates:
  - `monitor_scope.py`, for reason 1, and possibly reason 2 if `resolve_route` lives there.
  - `types.py` or `monitor_types.py`, for the `NativeSurface` and `StreamCursor` checkpoint union.
  - `_monitor_journal_store.py`, if the delivery tables constrain provider.
- Any of these confirmed means Stop → Refine.

**Estimate risk:** The 0.25h margin assumes zero work outside the three files. That is about eleven journal branch points plus a local seal BLOB and about 12 proof cases. Re-estimate after the map is complete.

**To clear:**
- An `ls-tree` at `30e1a13d`, with a commit label.
- Source excerpts:
  - `read_source`, including its signature and Grok path.
  - `_grok_admission` and the `_grok_admissions` declaration.
  - `resolve_route` and `_fresh_view`, plus how Grok proofs are built.
  - `StreamCursor`, `GrokCheckpoint` and the Grok boundary types.
  - `NativeSurface`.
  - Grok epoch storage.
  - Schema versions 5–7.
  - Claim-key derivation.
  - `reserve_delivery` and the ACK path.
- The test-root listing.

No code, coordinator, enrollment, release or gate was touched.

**JIT_330: HOLD**
