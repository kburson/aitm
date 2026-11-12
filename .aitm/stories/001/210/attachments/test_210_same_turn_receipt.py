"""Observe the public reader while appending the accepted native disposition sequence."""
import json

import test_monitor_scope as fixtures
from aitm_usage.monitor_scope import ScopeState
from test_monitor_scope import SOURCE, native


def test_scope_receipt_on_command_output_and_close(native, tmp_path, monkeypatch, capsys):
    with native.registry.writer() as writer:
        native.append()
        scope = ScopeState(writer)
        prior = scope.read_source(SOURCE, native.locator())
        assert prior.cursor is not None
        assert any((item.usage.tokens.total_tokens or 0) > 0 for item in prior.observations)
        append_disposition = fixtures._append_ordered_disposition
        native_write = fixtures.write
        observed = []

        def record(phase, command_id):
            batch = scope.read_source(SOURCE, native.locator())
            receipt = native.receipt_ref(command_id)
            observed.append({
                "phase": phase,
                "receipt_ordinals": [
                    item.boundary.ordinal for item in batch.boundaries
                    if item.boundary.receipt_ref == receipt
                ],
                "cursor": batch.cursor is not None,
                "diagnostics": [item.code.value for item in batch.diagnostics],
                "rows": len(native.path.read_bytes().splitlines()),
            })

        def split_write(path, rows, append=False):
            assert append and path == native.path and len(rows) == 9
            assert rows[4]["payload"]["type"] == "token_count"
            assert rows[5]["payload"]["type"] == "custom_tool_call_output"
            assert rows[6]["payload"]["type"] == "task_complete"
            assert rows[7]["payload"]["type"] == "task_started"
            for phase, chunk in (
                ("through_accounted_command_output", rows[:6]),
                ("through_command_turn_completion", rows[6:7]),
                ("through_followup_turn_context", rows[7:]),
            ):
                before = path.read_bytes()
                native_write(path, chunk, append=True)
                assert path.read_bytes().startswith(before)
                record(phase, command)

        def observe_append(source, command_id, request_path, stdout):
            nonlocal command
            command = command_id
            with monkeypatch.context() as patch:
                patch.setattr(fixtures, "write", split_write)
                return append_disposition(source, command_id, request_path, stdout)

        command = None
        monkeypatch.setattr(fixtures, "_append_ordered_disposition", observe_append)
        case = fixtures._route_disposition_fixture(native, writer, tmp_path, monkeypatch, capsys)
        assert len(observed) == 3
        assert observed[0]["receipt_ordinals"] == observed[1]["receipt_ordinals"] == []
        assert observed[2]["receipt_ordinals"] == [case.terminal.position.ordinal]
        assert case.journal.cursor_for(SOURCE, native.locator()) == case.cursor
        with capsys.disabled():
            print(json.dumps(observed))
