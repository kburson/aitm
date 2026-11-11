# #203 M08b4a native disposition proof JIT

## Authority and bound

Epic #100 direct child. Rank 228, proposed Size M and 3.85 implementation agent-hours. Codex owns the isolated `codex/aitm-203-native-disposition-proof` branch and Close. Checkpoint at 2.25 implementation agent-hours requires the exact v1/v2 codec lane GREEN and committed, and both ordered native EOF and rejected later-usage RED controls. Stop for a further independently accepted split if the checkpoint or four-hour cap cannot hold.

The exact predecessor is #202 Closed (Completed) and Project Done. PR #207 delivered #202 as `1282538954dc5a7e7f7b27da4e3ab096892e3add`. The refreshed literal trunk is descendant `e4701f2e89d34f93f13d717199254b66aa3f0457`, tree `f62fbd48047f73baf52f65f86b33d475328b2f1f`. Intervening files are limited to `tools/story_dashboard/attribution.py` and its test. Clean detached local gate passed 996 product and CLI, 182 helpers, Ruff and raw 10,461/11,407 product and 778/821 helper lines. Recheck actual literal target and full native graph immediately before Develop and again before Close. Keep #209 M08b4b, #210 M08b4c, #204 and #119 intact. Native readback places all three disposition stories directly under #100 and directly ahead of #119. #210 also directly gates #204. The exact Refine split at SHA-256 `0158b267bcfcee8989639d7aa89a84bdf4e1687849ec449abfab07fe198a6cbf` owns the scope and graph.

## Scope

Change only `packages/aitm-usage/src/aitm_usage/monitor_scope.py` and `packages/aitm-usage/tests/test_monitor_scope.py`. Use the existing admitted macOS Codex Desktop parser for this proof. Keep legacy ScopeState hold, dispose, receipt, view, route behavior and the existing public reader. The new private proof is proposal evidence only. On the refreshed clean baseline, a private native probe registered and advertised an actual writer operator grant, called the existing scope enqueue path, verified the exact sealed pending DispositionRequest, and placed the resulting canonical queued stdout into the ordinary chronological Codex transcript parser. The distinct receipt is eligible on the same source, session and stream at ordinal 42 for the intact older span [27,34). It has no cursor and retains the unresolved boundary. Actual subsequent positive usage yields a cursor and the same receipt. This supports the proposal seam. Journal state, all frontiers, the effective holds, source adapters, operator CLI, project ACK and production activity remain outside this slice. M08b4b owns JournalChange recording. M08b4c separately owns the effective hold and qualified settled frontier.

## Exact codec

Keep the original `_ScopeSnapshot` dataclass, fields, file `scope-v1.json`, and v1 decoder byte-compatible. Add `_FORMAT_V2 = "aitm.usage.monitor-scope/v2"` and this closed v2 payload. The public proof wrapper is not serialized.

```python
@dataclass(frozen=True, slots=True)
class _HeldRouteTarget:
    hold_id: UUID
    boundary: SourceBoundary
    prefix: SourceCursor

@dataclass(frozen=True, slots=True)
class _RouteDispositionRecord:
    command_id: UUID
    command_digest: str
    request_digest: str
    hold_id: UUID
    outcome: HoldState
    boundary: SourceBoundary
    prefix: SourceCursor
    checkout: SourceRef

@dataclass(frozen=True, slots=True)
class _ScopeSnapshotV2:
    events: tuple[_ScopeEvent, ...]
    holds: tuple[ProofHold, ...]
    resolutions: tuple[_Resolution, ...]
    held_route_targets: tuple[_HeldRouteTarget, ...]
    route_dispositions: tuple[_RouteDispositionRecord, ...]
    format: str = _FORMAT_V2
```

Select exact shape with existing strict typed decoding. V1 never infers proof. V2 only admits exact fields, real owned target joins, positive raw offsets, distinct receipt and terminal ordinal, nonempty original span, unique hold target IDs, unique disposition IDs and at most one disposition per hold. Outcome is GAP or RESOLVED. Check command and sealed request digests as lower-case 64-hex. The linked ProofHold owns the source ID, surface, span and original digest. Require each boundary to be on that same provider/session/stream and its receipt ref to equal the writer-keyed command identity. Terminal ordinal is at or after the original affected end. Validate service refs of the new typed objects individually in writer custody before proof or any publication. Require the already initialized registry source key before taking this path. A read-only legacy view without a writer decodes the exact closed structural format and exposes only its unchanged events and holds. It cannot use the new records as authority. Preserve legacy ref decoding and ordinary read-only view behavior. Exact target boundary matches the hold's saved position, and new record and target preserve the same source/locator/incarnation tuple, with terminal offset greater than the saved hold prefix. Keep the file path, private size limit, atomic publication, publication confirmation and all three existing ordered collections. V2 writes remain v2. Invalid, mixed, foreign or unknown formats refuse before mutation. The exact old source reader refuses v2 at the strict codec and leaves it byte-identical.

## Exact issuance

Extend `ScopeState.hold(receipt, *, retain_route_target: bool = False)` as an explicit opt-in for newly created holds. The default follows the existing path. Retention requires the exact writer-issued current eligible admitted native receipt, matching anchored owner and nonempty original fixed physical prefix. Add the newly created ProofHold and original boundary/prefix together in one atomic scope publication. A legacy hold with no saved target cannot be promoted on a retry. An already retained hold returns the exact existing hold on exact receipt replay and holds conflicting bytes. The stored target witnesses the original current fixed prefix, not a filename or route assertion.

Add `ScopeState.verify_route_disposition(command: Disposition, terminal: VerifiedBoundary) -> VerifiedRouteDisposition`. It verifies the same operator, exact command and receipt object, and currently admitted fixed native source. It reads the exact currently pending typed DispositionRequest through the existing writer-bound ScopeInboxReader and ControlInbox publication lock, verifies the grant and sealed envelope, and matches command ID, project, hold and release_previous. Store the verified envelope digest. A same-ID Mark or Handoff envelope, missing/revoked authorization and different bytes hold. The native parser's receipt ID alone cannot supply typed authority. The new proof consumes no queue item or terminal receipt. Only the two listed files change and the existing queue verifier is reused.

Require the original held target's keyed receipt in the same current cold batch with exact native SourceBoundary equality and pinned earlier physical prefix. Reauthenticate that fixed prefix against the actual same source, locator and incarnation. Require both original exact half-open span and terminal to be eligible for the same owner under current registry. The operator, original, terminal and saved checkpoint must all agree on identity. Use exact source/session/stream and capture, distinct terminal command and boundary and a later native ordinal. This slice issues only a proposal from the qualified unsettled terminal form. Require the authenticated terminal TURN as the final recognized native boundary, an absent progress cursor, and only the ordinary native BOUNDARY_UNVERIFIED obligation for the unresolved fixed read. Confirm no appended bytes beyond that prepared full physical read at issuance. The provider adapter may drop observations on an unsettled read. An empty observation tuple or missing cursor conveys no assertion that later usage is absent, and the proof records no such assertion. The ordered positive fixture demonstrates actual EOF with no later rows in the input. A fresh completed read with genuine later usage still proves the same receipt in the existing parser. The new unsettled-terminal method refuses to issue or reissue on that completed read, and its later cursor supplies no settlement authority for the older span.

A false release_previous may propose GAP for a currently held or expired-GAP owned target. True may propose RESOLVED only for the exact active unexpired held target and an identical unblocked original route throughout the target under the present timeline and same verified checkout/owner. A failed RESOLVED check stays held. Do not coerce it to GAP. The durable ScopeState hold retains its original state in both cases. Record the separate terminal evidence in the same pinned scope file. No view or routing effect follows from the proposal.

Use the existing writer registry and physical confirmation before and after publication. If publication is visible but its directory sync fails, issue no proof until re-open confirms and an exact current replay rechecks it. For same-ID replay, require exact command digest, sealed envelope digest, source, held target, boundary, captured prefix and outcome before returning current proof without rewriting. Conflicting ID bytes or a second command for the target refuse. A persisted result by itself never issues current authority. A route-proof record's command ID cannot be re-used for a different legacy action. Exact legacy command lookups continue to return only legacy outcomes.

`VerifiedRouteDisposition` is a frozen slotted weak-referenceable wrapper holding the immutable record, ProofHold and exact issued terminal receipt. Keep it in an issuer-local weak identity map. `ScopeState.require_route_disposition(proof)` verifies the exact issued object and revalidates the current pending typed envelope, current registry, exact target/hold state and route, both source prefixes and confirmed current scope publication before returning the record. It does not write. Cloned, stale and foreign writer objects refuse. An exact fresh same-writer replay can reissue after current checks. A new writer must supply fresh current operator, queue and source proof.

## Work and tests

1. Write codec and custody REDs against exact v1, v2 malformed/unknown/foreign, legacy equivalence, bound file, atomic interrupted publication and old-reader refusal. Implement only exact codec and gated held-target persistence. Prove the original legacy dispose test remains byte and behavior compatible.
2. Use real ordered NativeScopeFixture Codex Desktop proof. Build actual scoped queue authorization using registered and advertised operator grant and queued typed DispositionRequest. Add distinct later terminal receipt at EOF with monotonically ordered rows, only genuine positive earlier usage, source/session/stream equality, preserved old prefix and no backdated or zero-delta counter. Verify legacy path refuses and current scope, holds, journal bytes and prior cursors remain unchanged by proposal and exact replay. Verify actual stored prefix and historical hold survive reopen. Preserve unresolved BOUNDARY_UNVERIFIED. Add genuine later usage to the same terminal and prove the parser still sees the receipt but the unsettled-terminal proposal refuses and cannot settle the earlier span.
3. Verify GAP and prospective RESOLVED positives with real native prior route. RED exact current proposal rejection on changed old prefix, source move/replacement, wrong authority, copied receipt, wrong typed queue request, disabled capture, late genuine usage, expired RESOLVED and conflicting command ID. Simulate a visible publication without durable sync and prove no issued token until exact recheck. Legacy holds/resolutions without retained target remain historical. Forged proof and fresh writer without new exact evidence refuse.
4. Freeze the exact code, retain old test identities, run locked local gates and raw floors, open exact PR to trunk, run all six hosted jobs with trusted attestation and raw replay. Independently review the exact passing source. Then ordinary merge, ordered parents/tree/ancestry verification, original implementer sign-offs, native graph check, and Closed Completed and Project Done.

Epic #2, C01 and production cutover are outside the authorized delivery.
