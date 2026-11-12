"""Read-only qualification using disposable native fixtures."""
import json

import pytest
from aitm_usage.monitor_scope import ScopeState
from test_codex import end, write
from test_monitor_scope import (
    SOURCE,
    _finish_disposition_turn,
    _route_disposition_fixture,
    native,
)

@pytest.mark.parametrize("mode", ["proof_only_eof", "counterless_completion", "later_usage"])
def test_chronological_public_terminal(native, tmp_path, monkeypatch, capsys, mode):
    with native.registry.writer() as writer:
        native.append()
        earlier = ScopeState(writer).read_source(SOURCE, native.locator())
        prior_positive = [
            obs.usage.boundary.ordinal for obs in earlier.observations
            if (obs.usage.tokens.total_tokens or 0) > 0
        ]
        assert earlier.cursor is not None and prior_positive
        case = _route_disposition_fixture(native, writer, tmp_path, monkeypatch, capsys)
        prefix = native.path.read_bytes()
        initial = case.state.read_source(SOURCE, native.locator())
        position = case.terminal.position.ordinal
        assert initial.cursor is None
        if mode == "counterless_completion":
            write(native.path, [end(case.followup, time=case.when)], append=True)
        if mode == "later_usage":
            _finish_disposition_turn(native, case.followup, case.when)
        contents = native.path.read_bytes()
        assert contents.startswith(prefix)
        timestamps = [json.loads(line)["timestamp"] for line in contents.splitlines()]
        assert timestamps == sorted(timestamps)
        batch = case.state.read_source(SOURCE, native.locator())
        ordinals = [obs.usage.boundary.ordinal for obs in batch.observations if (obs.usage.tokens.total_tokens or 0) > 0]
        later = [ordinal for ordinal in ordinals if ordinal > position]
        before = [ordinal for ordinal in ordinals if ordinal < position]
        assert max(prior_positive) < position
        assert bool(later) == (mode == "later_usage")
        matches = [item for item in batch.boundaries if item.boundary == case.terminal.native_boundary]
        assert len(matches) == 1
        assert case.state.verify_boundary(case.command, case.owner, batch, matches[0]).eligible
        assert case.journal.cursor_for(SOURCE, native.locator()) == case.cursor
        hold = next(hold for hold in case.state.view().holds if hold.command_id == case.hold.command_id)
        assert hold.state.value == "held"
        result = {
            "mode": mode,
            "terminal": position,
            "original_span": [case.hold.affected.start, case.hold.affected.end],
            "prior_committed_positive_usage": prior_positive,
            "earlier_usage_in_current_projection": before,
            "existing_journal_cursor_unchanged": True,
            "existing_scope_hold": hold.state.value,
            "later_usage": later,
            "has_progress_cursor": batch.cursor is not None,
            "diagnostics": [item.code.value for item in batch.diagnostics],
            "terminal_eligible": True,
        }
        with capsys.disabled():
            print(json.dumps(result, sort_keys=True))
