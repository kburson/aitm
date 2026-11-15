[14:20:32]
# JIT_329: PASS

This review uses only the evidence in the brief; no tools were run. The design corrections close the semantic findings of the prior HOLD. The remaining items are mechanical, so they are recorded as Develop entry conditions rather than reasons to hold.

## H1–H11 on cut `84b936d1`

| H | Result | Basis |
|---|---|---|
| H1 | Pass, with condition E1 | The rank 248/249/250 rows are unique: #329, #330, #121. The #121 file list (`monitor.py`, `service.py`, `test_monitor_watches.py`) is disjoint from the four #329 paths. The `--is-ancestor 84b936d1 84b936d1` check compares trunk with itself, so it proves nothing. The #326 → trunk binding currently rests only on the stated attestation. |
| H2 | Pass, no Stop | **Union decode:** `_wire` tries every `UnionType` arm and requires exact key-set equality for dataclasses. **Disjoint shapes:** `SourceBoundary` carries `{epoch_ref, kind, provider}`, which `GrokBoundary` lacks (its `provider` is a property, not a field). So both shapes decode to exactly one arm. **Encode:** uses `type(value) is expected`, so there is no subclass bleed. **No codec edit:** `_fields` needs no registration, and the probe ran with `no_product_change: true`. |
| H3 | Pass, with condition E2 | Canonical form is pinned: exact `RegistryView` when empty, refusal of the extended-empty shape, and an explicit `RegistryView.__post_init__(self)` call. Command/edge uniqueness is enforced across both pending tuples. The old-binary fail-closed residual is recorded against the #122 snapshot. |
| H4 | Pass | **Quiescent stream:** the cut is the exclusive prefix end P, so enable admits the first new turn and disable excludes it. **One open turn:** the cut is terminal + 1. Enable excludes that turn and disable includes it. **Held terminal:** disable falls back to the verified start and enable stays queued. **No straddling:** because the cut moves to terminal + 1, no committed fence can split a span. **Multi-stream:** resolved cuts and open arms freeze together, all-or-none. Prefix hashing uses the frame's byte end, kept separate from the interval cut. |
| H5 | Pass | **Epoch binding:** epochs bind the per-run generation. **Lost or replaced generation:** the result is capture-held, never exclusion. **Replacement:** needs a new command, and an equal enable is not deduplicated. **Tests:** the three restart cases are tested separately. Positive restart is a same-writer cold reload. |
| H6 | Pass | Only witnesses present at the cut are covered. Late streams and forks get zero ROUTED. A pending stream routes only below its own bound. Enrollment is removed from #329. |
| H7 | Pass, with owner action O1 | With no callback, the command stays queued with no receipt. Native paths are exact. The leaf tests a real `ScopeState` callback directly. |
| H8 | Pass | After the read, lease, profile/generation, root/origin and strict prefix are rechecked before any authority is issued. There is a single seeded admission and no fallback. |
| H9 | Pass | **Fixture:** blob `a2ca339b` is pinned. **Unchanged replay:** the expected outcome is pinned before RED: the strict read is held at the first attempt, and the observational entry reproduces the journal refusal. **Positive marks:** they use in-test receipt joins through the selected #304 issuer. **Hookless:** the second hook row is omitted and the user-start row kept; story is `None` after the prior mark. |
| H10 | Pass | The existing `DiagnosticCode.UNSUPPORTED_FORMAT` is used, with no `types.py` edit. |
| H11 | Pass | **Sink:** `_GrokAttemptHeld` returns through the proof sink. **Cursor:** stays at or before the attempt's start, and nothing is emitted at or after the attempt. **Separation:** the strict prefix label is domain-separated, so an observational prior cannot resume a strict read. **Failure cases:** the nine cases hold with no hookless fallthrough. |

**Authority checks:**
- **Current authority:** in-memory live profile + writer lease + ordered inbox/`held_edges`.
- **Restarted authority:** same writer means a disk reload resumes. A new writer, or a regrant without a command, holds.
- **Codecs:** old bytes are canonical. New bytes appear only when Grok records are present.
- **Lease proof:** rechecked both before and after the read.

## Develop entry conditions

If any of these fails, Stop and Refine.

- **E1.** Record #326's PR `mergeCommit.oid` and confirm it equals `84b936d1`. This replaces the vacuous self-ancestry check.
- **E2.** The test must assert:
  - `sha256(registry canonical) == 626314e3…`
  - `sha256(scope canonical) == 7e56be80…`

  The probe's `old_registry_sha256 badc4ff0…` is a different value. Identify its provenance and do not embed it as the golden.
- **E3.** `VerifiedBoundary` stays untouched. A Grok `_ScopeEvent` is built from `_VerifiedGrokMark` inside `monitor_scope.py`. If the mark has to flow through a widened `VerifiedBoundary` that lives in `monitor_types.py`, that is a Stop.
- **E4.** `GrokBoundary` must be importable at runtime in `monitor_scope.py`, because `get_type_hints` resolves it. Do not import it only under `TYPE_CHECKING`.

## Required added tests

These fit within the existing allocations:
- **Held Grok command (no callback):** a later Codex/Claude command on another edge still applies, and a same-edge successor waits.
- **Wrong verifier:** a valid receipt from a verifier other than the one selected by the current profile/generation holds. Verifier, authority and profile are independent only as test inputs; the product must cross-bind them.
- **Never-terminating open turn on disable:** reads stay below P and no receipt is issued. Safety holds; liveness is the residual.
- **Extended-empty registry:** decode refuses it.

## Residuals carried forward

- **Old binary:** fails closed for the whole registry once any Grok epoch exists, including Codex/Claude. Recovery uses the #122 snapshot.
- **Strict reads:** cannot resume an observational cursor, so the first strict read starts at 0. Journaling of duplicate observations belongs to #330.
- **O1 (#121 owner action):** the #121 body shown does not yet record the obligation to pass the Grok-evidence callback. #121's own JIT must also decide whether its acceptance needs new-session enrollment. If it does, enrollment gets its own story ranked before #121.

## Feasibility

3.75h fits inside the 4.0h cap, leaving 0.25h of margin. It is feasible because the H2 probe removes the risk of a codec edit.

| Phase | Allocation |
|---|---|
| Codec and cuts | 1.45h |
| Strict parser and current owner route | 1.35h |
| Restart/failure matrix and regressions | 0.95h |

- **Main risk:** the frozen multi-stream record and the nine-case parser.
- **Checkpoint at 1.75h:** the literal codec tests and identity-bound epoch tests must be green.
- **Stop triggers:** any projection above 4.0h, or any edit outside the four files. Either one stops for a narrower review.

Automatic enrollment stays outside this leaf. All gates and scope limits remain as accepted.

**JIT_329: PASS**
