[15:39:44]
JIT_330: HOLD

Eight of the nine prior HOLD reasons are cleared. The one that remains is a single boundary question: `PendingClaim` and `_delivery_claim` are not supplied. They decide whether Grok delivery and ACK can stay inside the three paths.

**Prior HOLD reasons**

| # | Reason | Disposition | Evidence |
|---|---|---|---|
| 1 | Single admission | **Cleared** | `read_source` has `_grok_admission: _GrokAdmission \| None` (scope:1530) and forwards it as `admission=` (scope:1622). `_read_grok` acquires an admission only when `None`. `_take_grok_admission` pops it once, by identity. `_grok_admissions` is a `WeakValueDictionary[int, _GrokAdmission]` (scope:833). `_grok_admission` returns `_GrokAdmission` and registers it on issue. |
| 2 | Routing | **Cleared** | `_ObservationProof` carries `position`, `end`, `checkout`, `anchor_project`, `eligible_projects` and `grok`. Hookless work routes as `ROUTED(anchor)` with no story, and only if the anchor is in `eligible_projects`. Marked work requires exactly one APPLIED event with the same position and the same `native_boundary`, plus scope equality. An unresolved overlapping hold returns HELD. `_fresh_view` was not shown; the required equality check is journal-local regardless. |
| 3 | Observation type | **Cleared** | `NativeObservation.usage` is `UsageObservation \| GrokObservation` and carries revision, surface, time basis and position. The adapter builds revision 1 with a `NativePosition` and `span_end=None`, so the proof end is ordinal+1. The claim span must therefore come from `grok.start`/`grok.end`. |
| 4 | Progress | **Cleared** | `StreamCursor.checkpoint` is `SourceCheckpoint \| GrokCheckpoint`. `GrokCheckpoint` carries stream, incarnation, offset, prefix and completions, but no locator, so the journal-local seal is justified. `_read_grok` enforces the `GrokCheckpoint` type and calls `_recheck_grok_prefix`. |
| 5 | Marks and holds | **Cleared** | `GrokBoundary`, `_VerifiedGrokMark.boundary` and the `event.native_boundary ==` comparison are shown. No resolved-hold receipt verifier is shown, so under Refine condition 5 a resolved Grok hold stays held. That fails closed and needs no edit. |
| 6 | Epochs and surface | **Cleared** | `_GrokEpoch(identity, generation, start: _GrokCut, end)` is reachable through `_grok_records(view)`. The identity includes profile, incarnation, checkout, session and stream. `NativeSurface.GROK_BUILD_MACOS` exists. |
| 7 | Delivery and ACK map | **Open** | `delivery_acks` has no provider or surface CHECK, and `ack`, `reserve_delivery`, `_monitor_revision` and `_readback` are shown. However, `ack` computes the digest as `_encode(claim, PendingClaim)`, and `_monitor_revision` reads `claim.usage`. If `PendingClaim.usage` is annotated `UsageObservation` in `types.py` or `monitor_types.py`, the exact-type codec refuses a `GrokObservation`. That would make an outside edit necessary. `_delivery_claim`, which builds the issued claim and digest, is also unshown and could filter by provider. |
| 8 | Pin | **Cleared** | `git grep` output prefixed with `30e1a13d…` pins the scope module and the tests. The journal and scope blob IDs match the prior JIT. The evidence JSON names the same trunk. |
| 9 | Test root | **Cleared** | The `tests/` tree, `fixtures/grok/updates.jsonl`, the `isolated_grok_capture` fixture (capture:326), the marker/hookless reload test (capture:569) and `_isolated_qualification.py` are all present. If importing the fixture across modules fails, compose it locally from `_isolated_qualification` rather than touching `conftest`. |

**Refine conditions:** Conditions 1–6 and 8–10 are verified as stated. Condition 7 is verified except for the `PendingClaim`/`_delivery_claim` link. Condition 10 holds: 3.75h is within the 4.0h cap, with the 1.75h gate requiring a typed reserve and byte-identical legacy goldens.

**Outside-file decision:** No outside edit is proven necessary. The only candidate left is the `PendingClaim.usage` annotation, if it lives outside `monitor_journal.py`. Nothing in the supplied evidence requires a scope, registry, store, codec, types or schema edit.

**To clear:**
- The `PendingClaim` definition and its file, at `30e1a13d`.
- The `_delivery_claim(conn, key, revision)` body.
- Disposition:
  - If `PendingClaim` lives in `monitor_journal.py`, or its usage field is already a union, and `_delivery_claim` has no provider filter, this becomes PASS with no further review.
  - Otherwise Stop → Refine.

**Develop constraints:**
- Pass the identical `locator` object to both `_grok_admission` and `read_source`, because `_take_grok_admission` checks `original is locator`.
- Assert all of the following on the batch:
  - `type(batch) is VerifiedScopeBatch`
  - `batch._grok_strict`
  - `batch.surface is GROK_BUILD_MACOS`
  - a `GrokCheckpoint` cursor
- Discard the admission in `finally` only when `_grok_admissions.get(id(a)) is a`.
- Re-derive identity through the existing `_grok_identity`, which the batch does not expose. Hold unless exactly one epoch interval matches.
- Tripwire: the `GrokCompletion` codec round trip, checked at 1.75h.
- Branch from `30e1a13d`, not from this worktree's `codex/aitm-325-native-host-watch` HEAD.

All gates are preserved: locked local Test, same-head signed hosted Test, independent source, protected merge, native Close and the 4h cap.

JIT_330: HOLD
