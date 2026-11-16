# #121 Coordinator JIT recovery

Rank 250, Size M, 3.5 implementation agent-hours, with the accepted four-hour cap. The issue is open and Project 24 is at Refine. All eight direct prerequisites are Closed and Done (#115, #120, #304, #325, #326, #330, #331 and #335).

Source baseline is trunk `755fa2ece56cfa8c70a460b269d947ec6e958b2f`, tree `2ffe002416bacbb37670a325852fff0b88330ea1`, the verified merge of [PR #336](https://github.com/kburson/aitm/pull/336). Planning baseline is `46145d6cac758bdbb14d861527d2a803af61635f`. Preserve [JIT attempt 1](coordinator-independent-jit-r1.md) and the [accepted marker amendment](grok-scope-marker-independent-review.md). This recovery packet supplements the [coordinator JIT](2026-11-15-121-root-watch-coordinator-jit.md) with current baselines, source bindings and the remaining resolver question. Independent recovery is pending.

## Verified integration paths

1. **Watch and select.** Use the delivered `WatchSet` once per approved physical root and a single `Registry._inventory_cycle(_OriginCache)` per bounded selection cycle. Keep provider approval and route checks independent. Rotation, overflow, root loss, restart and timed fallback invalidate the selected locators and prompt revalidation. Measure that an unchanged parked payload is never opened.
2. **Capture and enroll.** Bind the current inventory into `ScopeState._grok_capture_evidence` through the callback to `Registry.apply_pending`. The callback accepts four positional arguments and a keyword-only inventory. Use the existing qualified Grok reader with the original installation, checkout, cutoff and source namespace. Return from `apply_pending` before calling `ScopeState.enroll_grok`, which takes its own inbox publication lock. Preserve explicit holds and hand sanitized enrollment gaps from `grok_enrollment_gaps()` to the cycle result.
3. **Authenticate and apply the exact mark.** Read `ScopeInboxReader.iter_verified(locked)` under inbox publication and leave that lock before entering the Grok mark context. Bind `scope_admission.grok_receipt_lookup(writer, source_id, checkout)` to the Grok adapter for the selected approved reader, then let the adapter identify the unique native hook and its later completion. When an authorized caller supplies the existing attested launch context, `stage_grok_attempt` stages the original queued request. Use `scope_admission.grok_mark(writer, request, source_id, checkout)` to reacquire publication custody and revalidate the exact original proposal, grant, profile and checkout while applying the mark. The returned typed mark goes through the original scope owner, `ScopeState.verify_boundary` and `apply_mark`. Scope-source mismatch remains held. Preserve the existing typed handoff and disposition paths and separate their boundary proof from the mark.
4. **Deliver and settle.** After the mark is applied, use `RoutingJournal.prepare` and `reserve_batch` for the exact selected stream. Use the original registered destination and `ProjectDelivery.commit` for owed claims, confirm durable readback and retire only on exact `RoutingJournal.ack`. On a recoverable hold, leave the same stream or claim retryable and let other projects progress. Finish the current scheduler lease only after verified catch-up.

The old service entry remains available. The new entry remains dormant. Writable product scope stays `packages/aitm-usage/src/aitm_usage/monitor.py`, `packages/aitm-usage/src/aitm_usage/service.py` and `packages/aitm-usage/tests/test_monitor_watches.py`. Keep the original reserves of 1.25 h for cycle and scheduler, 1.15 h for ordered control and scope proof, and 1.1 h for guarded delivery, compatibility and tests, subject to current JIT confirmation.

## Wake resolver question for recovery

Same-account `WakeIngress` checks private socket identity and peer credentials. `Scheduler._admit` sends PARK directly to `park(session)` against already verified keyed entries. CHANGE and STOP go through the coordinator resolver.

The v1 STOP frame carries provider and locator. It supplies neither a native session/turn nor a producer-issued completion identity. `_approved_candidate` and the Grok counterpart establish the selected stream and approved installation, leaving a separate freshness question for STOP. The scheduler requires the resolver to supply a verified current turn and `current_stop=True` before entering Settling. A late frame can carry the same locator as a newer turn. Codex Desktop's existing `ScopeState.completion_witness` is specifically gated on a typed `Disposition` and its exact request and hold. Its proof cannot serve as a generic Stop attestation.

First determine whether the current qualified caller and selected-reader contracts can provide a current-turn completion fact in the existing three files. An offline comparison should exercise an exact fresh completion, a late Stop while a newer turn is active or completed, and an excluded source using the same root. Assert that only the independently established current turn can settle and that refusal preserves bounded watch and timer recovery. Use `STOP_WITHOUT_CURRENT_TURN` wherever the proof is absent. If the accepted coordinator scope needs a successful native Stop and the existing contracts cannot establish it, return to Refine for an explicit ownership decision before Develop. Retain #320's installer ownership and #125's installed-service rehearsal.

## Offline verification

The locked focused suite passed 120 tests for native watches, inventory, scheduler, Grok enrollment, receipt authentication and guarded delivery. A separate offline fixture combined #335's product receipt callback with #330's actual journal and destination. It observed one story-scoped claim and one project-only claim, exactly two destination revisions, consistent receipt/ACK on retry after reopening the journal and destination, and no new claims at the resumed cursor. The fixture supplies synthetic process ancestry as in the existing scope-receipt regression. Live caller and coordinator wiring remain subject to JIT and Develop.

The combined probe uses the following scratch pytest module against the pinned trunk.

```python
from test_grok_scope_receipts import _ready_scope, staged_scope
from test_grok import PROMPT_A, SESSION
from test_monitor_grok_capture import isolated_grok_capture
from test_monitor_grok_delivery import _enable_delivery, _ledger

from aitm_usage import scope_admission
from aitm_usage.monitor_journal import ClaimStatus, RoutingJournal
from aitm_usage.monitor_scope import HandoffStatus, ScopeState
from aitm_usage.monitor_writer import ProjectDelivery
from aitm_usage.sources.grok import GrokAdapter


def test_product_receipt_through_guarded_delivery_after_lost_ack(staged_scope, monkeypatch):
    f, _, request, checkout, attempt, lookup, bind = _ready_scope(staged_scope, monkeypatch)
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    f.write([*f.rows[:6], *f.rows[7:]], 2)
    locator = f.locator()

    with scope_admission.grok_mark(f.writer, request, f.source_id, checkout) as mark:
        owner = f.state.operator(f.project)
        f.state.authorize(mark, owner)
        batch = f.state.read_source(f.source_id, locator)
        (boundary,) = batch.boundaries
        proof = f.state.verify_boundary(mark, owner, batch, boundary)
        assert f.state.apply_mark(mark, proof).status is HandoffStatus.APPLIED

    journal = RoutingJournal(f.writer, f.state)
    prepared = journal.prepare(f.source_id, locator)
    assert [candidate.route.scope for candidate in prepared.candidates] == [request.scope, None]
    assert all(candidate.route.project_id == f.project for candidate in prepared.candidates)
    outcomes = journal.reserve_batch(prepared)
    assert [outcome.status for outcome in outcomes] == [ClaimStatus.PENDING] * 2
    _enable_delivery(f, journal)
    tickets = [journal.reserve_delivery(outcome.key, 1) for outcome in outcomes]

    with _ledger(f).writer() as writer:
        delivery = ProjectDelivery.attach(journal, writer)
        receipts = [delivery.commit(ticket) for ticket in tickets]

    reloaded = RoutingJournal(
        f.writer, ScopeState(f.writer, grok_reader=GrokAdapter(f.find_origin, lookup))
    )
    with _ledger(f).writer() as writer:
        delivery = ProjectDelivery.attach(reloaded, writer)
        for ticket, receipt in zip(tickets, receipts, strict=True):
            assert reloaded.reserve_delivery(ticket.claim.key, ticket.claim.revision) == ticket
            assert delivery.commit(ticket) == receipt
            ack = reloaded.ack(delivery, ticket, receipt)
            assert reloaded.ack(delivery, ticket, receipt) == ack
        revisions = writer.monitor_as_of(receipts[-1].sequence).revisions
        assert len(revisions) == 2
        assert {row.observation for row in revisions} == {ticket.claim.usage for ticket in tickets}

    resumed = reloaded.prepare(f.source_id, locator)
    assert resumed._read.prior == prepared.progress
    assert resumed.candidates == ()
    assert reloaded.reserve_batch(resumed) == ()
    assert len(reloaded.as_of().claims) == 2
```

Save the module to a scratch directory and run it from trunk with `PYTHONPATH="$PWD/packages/aitm-usage/tests" uv run --project packages/aitm-usage --locked pytest -q "$probe"`, where `probe` is its absolute path. The original focused suite command targets `test_grok_scope_receipts.py`, `test_monitor_grok_delivery.py`, `test_monitor_grok_enrollment.py`, `test_monitor_inventory.py`, `test_monitor_scheduler.py` and `test_host_watch.py` under `packages/aitm-usage/tests`.

The Grok receipt store still fails closed at 1 MiB. Retention remains a separate design and scale-proof question. Keep independent JIT recovery, locked local and signed hosted Test, independent source review, protected delivery and verified Close. Epic #2, C01, production cutover and #204 remain outside this story.
