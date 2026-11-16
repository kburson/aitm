# #121 Stop feasibility and JIT disposition

This evidence supplements the [coordinator JIT recovery packet](2026-11-15-121-coordinator-jit-recovery.md) on trunk `755fa2ece56cfa8c70a460b269d947ec6e958b2f`, tree `2ffe002416bacbb37670a325852fff0b88330ea1`. The evidence is for Planning. #121 is in Refine at Rank 250, with a 3.5 implementation agent-hour estimate and a four-hour cap.

## Source and result

- The v1 Stop encoder and decoder carry only kind, provider and native locator. A fresh Stop and a delayed Stop for different turns in the same stream serialize to the same bytes. [Wake codec](https://github.com/kburson/aitm/blob/755fa2ece56cfa8c70a460b269d947ec6e958b2f/packages/aitm-usage/src/aitm_usage/sources/hooks.py#L40)
- The same-account socket verifies peer UID and socket identity. Source admission verifies the selected installation and stream. Neither supplies an event-to-turn binding. The resolver is the first seam at which independently verified current-turn proof could be associated with the Stop. The Codex Desktop completion witness is gated on a verified disposition request and hold. Grok's scope receipt proves a selected prompt marker and completion under its own authority. The source review identified no generic wake Stop proof in the delivered interfaces. [Wake ingress](https://github.com/kburson/aitm/blob/755fa2ece56cfa8c70a460b269d947ec6e958b2f/packages/aitm-usage/src/aitm_usage/monitor_control.py#L655) · [Codex completion witness](https://github.com/kburson/aitm/blob/755fa2ece56cfa8c70a460b269d947ec6e958b2f/packages/aitm-usage/src/aitm_usage/monitor_scope.py#L1993)
- The scratch test used the delivered socket ingress, scheduler and sealed wake records. Both locator-only frames were refused with `STOP_WITHOUT_CURRENT_TURN`. An explicit older-turn fact was also refused after a newer turn was scheduled. Sealed wake bytes and pending work survived refusal. A later simulated approved observation got its own Active work. A supplied exact current-turn fact moved only that turn to Settling and its successful catch-up retired the work. The positive control uses the existing synthetic scheduler resolver fixture. It establishes the scheduler contract and leaves native producer provenance and coordinator wiring unverified. [Scheduler admission](https://github.com/kburson/aitm/blob/755fa2ece56cfa8c70a460b269d947ec6e958b2f/packages/aitm-usage/src/aitm_usage/monitor_scheduler.py#L235)
- The companion existing native adapter test passed with Desktop and excluded standalone CLI transcript shapes under a shared root. It establishes adapter eligibility for that fixture. The coordinator still needs the mixed-root test proving the excluded source produces no durable wake state. The scratch test, scheduler tests and shared-root adapter test passed, 26 total.

## Recommended JIT disposition

Within #121, preserve the v1 frame and refuse Stop unless a separately established, current and selected native fact binds that request to the exact session and turn. A matching path and the last completion in the transcript are insufficient together. Treat an ambiguous, stale or excluded request as a refusal with no retained scheduling, cursor or scope changes. The existing accepted M10 contract requires bounded native reconciliation after a lost or refused wake and permits `STOP_WITHOUT_CURRENT_TURN`. Keep explicit keyed PARK, admitted CHANGE and bounded native watch and timer reconciliation in #121, including recovery with no queued event. [Accepted M10 JIT](../../120/plan/2026-11-15-120-wake-park-jit-r2.md)

Ask independent JIT to confirm that this implements the accepted conditional Stop requirement within the three-file scope. If a positive native Stop is required for #121, return the missing producer-to-turn proof to Refine as an explicit scope and ownership issue. Assign no new dependency on #320's advisory installer or #125's rehearsal based on the probe alone. The receipt-capacity follow-up remains separate. Preserve all original gates and exclusions.

## Reproduction

Save the scratch test below and run it from the pinned trunk. Set `probe` to its absolute path.

```sh
PYTHONPATH="$PWD/packages/aitm-usage/tests" uv run --project packages/aitm-usage --locked pytest -q "$probe" \
  packages/aitm-usage/tests/test_monitor_adapters.py::test_desktop_and_cli_in_shared_root_admit_only_qualified_surface \
  packages/aitm-usage/tests/test_monitor_scheduler.py
```

```python
from test_monitor_scheduler import _change, _new_fact, wake

from aitm_usage.monitor_control import WakeIngress
from aitm_usage.monitor_scheduler import ScheduleState, WakeResolution, WakeResolutionKind
from aitm_usage.monitor_types import MonitorProvider
from aitm_usage.sources.hooks import HookEvent, HookSender, WakeDisposition, WakeKind, _frame


def test_same_stream_stop_requires_exact_independent_turn_fact(wake):
    scheduler, resolver, ref, now = wake
    tick = now[0]
    assert _change(scheduler, resolver)
    older = resolver.result
    old_stop = HookEvent(WakeKind.STOP, MonitorProvider.CODEX, "/raw-path-canary")

    _new_fact(resolver, turn=ref("newer-turn"), fact=ref("newer-fact"))
    newer = resolver.result
    assert _change(scheduler, resolver)
    fresh_stop = HookEvent(WakeKind.STOP, MonitorProvider.CODEX, "/raw-path-canary")
    assert _frame(old_stop) == _frame(fresh_stop)

    pending = {
        path.name: path.read_bytes()
        for path in (scheduler.root / "wake").iterdir()
    }
    with WakeIngress(scheduler, resolver).listen() as listener:
        sender = HookSender(scheduler.root)
        resolver.result = WakeResolution(WakeResolutionKind.STOP_WITHOUT_CURRENT_TURN)
        for event in (old_stop, fresh_stop):
            assert sender.notify(event) is WakeDisposition.SENT
            assert not listener.serve_once()
        resolver.result = older
        assert sender.notify(old_stop) is WakeDisposition.SENT
        assert not listener.serve_once()
        assert {
            path.name: path.read_bytes()
            for path in (scheduler.root / "wake").iterdir()
        } == pending

        items = scheduler.take_due(tick, 2)
        assert {item.turn for item in items} == {older.facts.turn, newer.facts.turn}
        assert all(item.state is ScheduleState.ACTIVE for item in items)
        assert all(scheduler.finish(item, caught_up=True) for item in items)

        resolver.result = newer
        _new_fact(resolver, fact=ref("subsequent-approved-observation"), current_stop=False)
        assert _change(scheduler, resolver)
        (fallback,) = scheduler.take_due(tick, 1)
        assert fallback.turn == newer.facts.turn and fallback.state is ScheduleState.ACTIVE
        assert scheduler.finish(fallback, caught_up=True)

        _new_fact(resolver, fact=ref("exact-current-completion"), current_stop=True)
        assert sender.notify(fresh_stop) is WakeDisposition.SENT
        assert listener.serve_once()
        (settling,) = scheduler.take_due(tick, 1)
        assert settling.turn == newer.facts.turn
        assert settling.state is ScheduleState.SETTLING
        assert scheduler.finish(settling, caught_up=True)
        assert scheduler.take_due(tick, 1) == ()
```
