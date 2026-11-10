"""Sanitized native-shaped rows from #88/#96 and deterministic replay variants."""

import json
import shlex
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from test_claude import MODEL, _native_tool_turn, cost, model_counts, request, user
from test_claude import row as claude_row
from test_claude import usage as claude_usage
from test_codex import (
    AFTER,
    COMMAND,
    CUTOFF,
    PROJECT,
    begin,
    counter,
    end,
    response,
    startup,
    tool_call,
    tool_output,
    usage,
)
from test_codex import (
    FIXTURE as CODEX_FIXTURE,
)
from test_scan import _native_startup_rows

from aitm_usage.ledger import Ledger
from aitm_usage.types import (
    Availability,
    DiagnosticCode,
    LedgerView,
    Revision,
    _decode,
    _encode,
)

CLAUDE_FIXTURE = Path(__file__).parent / "fixtures/claude/usage.jsonl"


class Evidence:
    """Simulate a pinned service view, without selecting a destination ledger."""

    def __init__(self, key, view=None):
        self.pseudonymize = key.pseudonymize
        self.validate_source_ref = key.validate_source_ref
        self._view = view or LedgerView(PROJECT, 0, (), ())

    def as_of(self):
        return self._view


@pytest.fixture
def source(tmp_path, monkeypatch):
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    key = Ledger.initialize(tmp_path / "evidence", PROJECT)
    root, checkout = tmp_path / "root-private", tmp_path / "checkout-private"
    root.mkdir()
    checkout.mkdir()

    def unexpected_open(*args):
        pytest.fail("adapter tried to open a project ledger")

    monkeypatch.setattr(Ledger, "open", unexpected_open)
    monkeypatch.setattr(Ledger, "writer", unexpected_open)
    monkeypatch.setattr(Ledger, "apply", unexpected_open)
    return key, root, checkout


def _adapter(monkeypatch, source, *, system="Darwin", arch="arm64"):
    from aitm_usage.sources import adapter

    key, root, checkout = source
    monkeypatch.setattr(adapter.platform, "system", lambda: system)
    monkeypatch.setattr(adapter.platform, "machine", lambda: arch)
    return (
        adapter,
        adapter.ProviderAdapter(),
        adapter.SourceRoot(root, CUTOFF, (checkout,), Evidence(key)),
    )


def _rows(fixture, checkout):
    return [
        json.loads(line)
        for line in fixture.read_text().replace("CHECKOUT", str(checkout)).splitlines()
    ]


def _write(path, rows):
    data = b"".join(json.dumps(row).encode() + b"\n" for row in rows)
    path.write_bytes(data)
    return len(data)


def _desktop(checkout):
    rows = _rows(CODEX_FIXTURE, checkout)
    rows[0]["payload"]["originator"] = "Codex Desktop"
    return rows


def _committed_view(result):
    return LedgerView(
        PROJECT,
        1,
        tuple(
            Revision(item.key, item.revision, item.usage)
            for item in result.observations
        ),
        (result.cursor.checkpoint,),
    )


def test_desktop_and_cli_in_shared_root_admit_only_qualified_surface(
    monkeypatch, source
):
    module, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    rows = _desktop(checkout)
    _write(directory / "desktop.jsonl", rows)
    rows[0]["payload"].update(originator="codex_cli_rs", source="cli")
    _write(directory / "cli.jsonl", rows)
    results = [adapter.read_delta(locator, None) for locator in adapter.discover(root)]
    assert len(results) == 2
    (allowed,) = (result for result in results if result.observations)
    (refused,) = (result for result in results if not result.observations)
    assert allowed.cursor is not None
    assert allowed.observations[0].project_context is not None
    assert refused.cursor is None
    assert [item.code for item in refused.diagnostics] == [
        DiagnosticCode.UNSUPPORTED_FORMAT
    ]
    wire = _encode(allowed, module.AdapterBatch)
    for sentinel in (
        "root-private",
        "checkout-private",
        "account-secret",
        rows[0]["payload"]["id"],
    ):
        assert sentinel not in wire
    assert set(json.loads(wire)) == {
        "observations",
        "boundaries",
        "diagnostics",
        "cursor",
    }


@pytest.mark.parametrize(
    "client,system,arch,change",
    [
        ("codex", "Darwin", "arm64", {"originator": "other"}),
        ("codex", "Darwin", "arm64", {"source": "exec"}),
        ("codex", "Darwin", "arm64", {"cli_version": "0.167.0-alpha.3.3"}),
        ("codex", "Darwin", "arm64", {"format_version": 2}),
        ("claude", "Darwin", "arm64", {"version": "2.1.319"}),
        ("claude", "Darwin", "arm64", {"format_version": 2}),
        ("codex", "Darwin", "x86_64", {}),
        ("claude", "Darwin", "x86_64", {}),
        ("codex", "Linux", "arm64", {"originator": "codex_cli_rs", "source": "cli"}),
        ("claude", "Linux", "arm64", {}),
    ],
)
def test_unqualified_native_tuple_withholds_evidence(
    monkeypatch, source, client, system, arch, change
):
    _, adapter, root = _adapter(monkeypatch, source, system=system, arch=arch)
    _, directory, checkout = source
    rows = _desktop(checkout) if client == "codex" else _rows(CLAUDE_FIXTURE, checkout)
    rows[0].get("payload", rows[0]).update(change)
    _write(directory / "unqualified.jsonl", rows)
    (locator,) = adapter.discover(root)
    result = adapter.read_delta(locator, None)
    assert result.observations == result.boundaries == ()
    assert result.cursor is None
    assert [item.code for item in result.diagnostics] == [
        DiagnosticCode.UNSUPPORTED_FORMAT
    ]


def test_recheck_native_origin_after_discovery(monkeypatch, source):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    rows = _desktop(checkout)
    path = directory / "changed.jsonl"
    _write(path, rows)
    (locator,) = adapter.discover(root)
    rows[0]["payload"]["source"] = "cli"
    _write(path, rows)
    result = adapter.read_delta(locator, None)
    assert not result.observations and not result.boundaries and result.cursor is None
    assert [item.code for item in result.diagnostics] == [
        DiagnosticCode.UNSUPPORTED_FORMAT
    ]


def test_codex_archive_counter_epoch_replays_once(monkeypatch, source, tmp_path):
    module, adapter, root = _adapter(monkeypatch, source)
    key, directory, checkout = source
    rows = _desktop(checkout)
    path = directory / "live.jsonl"
    frontier = _write(path, rows)
    with path.open("ab") as stream:
        stream.write(b'{"incomplete":"secret')
    (locator,) = adapter.discover(root)
    first = adapter.read_delta(locator, None)
    assert first.observations
    assert first.cursor.checkpoint.cursor.offset == frontier
    durable = _decode(_encode(first.cursor, module.StreamCursor), module.StreamCursor)

    archive = tmp_path / "archive"
    archive.mkdir()
    _write(archive / "copy.jsonl", rows)
    other_root = replace(
        root, path=archive, evidence=Evidence(key, _committed_view(first))
    )
    (reopened,) = adapter.discover(other_root)
    assert reopened.stream_ref == locator.stream_ref
    replay = adapter.read_delta(reopened, durable)
    assert replay.observations == ()
    assert replay.cursor == durable


def test_neutral_desktop_receipt_is_evidence_without_authority(
    monkeypatch, source, tmp_path
):
    module, adapter, root = _adapter(monkeypatch, source)
    key, directory, _ = source
    foreign = tmp_path / "foreign-private"
    foreign.mkdir()
    first, last = usage(8, 2), usage(6, 2)
    marker = tool_call(
        SimpleNamespace(root=foreign), "/private/tmp/command-body-secret"
    )
    _write(
        directory / "receipt.jsonl",
        [
            startup(foreign, originator="Codex Desktop"),
            *begin(foreign),
            marker,
            response("before-private", first, first),
            tool_output(),
            counter(first, first),
            response("after-private", usage(14, 4), last),
            counter(usage(14, 4), last),
            end(),
        ],
    )
    (locator,) = adapter.discover(root)
    result = adapter.read_delta(locator, None)
    assert not result.observations
    (proof,) = [
        item for item in result.boundaries if item.boundary.receipt_ref is not None
    ]
    assert proof.project_context is None
    assert proof.boundary.receipt_ref == key.pseudonymize("scope-receipt", str(COMMAND))
    wire = _encode(result, module.AdapterBatch)
    for sentinel in (
        str(foreign),
        "command-body-secret",
        "after-private",
        str(COMMAND),
    ):
        assert sentinel not in wire


def test_claude_streamed_revision_and_nested_overlap(monkeypatch, source):
    module, adapter, root = _adapter(monkeypatch, source)
    key, directory, checkout = source
    path = directory / "claude.jsonl"
    rows = _rows(CLAUDE_FIXTURE, checkout)
    first_offset = _write(path, rows[:2])
    (locator,) = adapter.discover(root)
    first = adapter.read_delta(locator, None)
    (partial,) = first.observations
    assert partial.usage.availability is Availability.PARTIAL
    assert first.cursor.checkpoint.cursor.offset == first_offset
    (prefix,) = first.cursor.checkpoint.provider.request_prefix
    assert (prefix.request_ref, prefix.message_ref) == (
        partial.usage.request_ref,
        partial.usage.message_ref,
    )
    serialized = _encode(first, module.AdapterBatch)
    for sentinel in (
        "synthetic-private",
        "msg_synthetic",
        "req_synthetic",
        str(checkout),
    ):
        assert sentinel not in serialized

    with monkeypatch.context() as patch:
        original = module.read_claude

        def missing_prefix(*args):
            result = original(*args)
            return replace(
                result,
                provider_checkpoint=replace(
                    result.provider_checkpoint, request_prefix=()
                ),
            )

        patch.setattr(module, "read_claude", missing_prefix)
        held = adapter.read_delta(locator, None)
        assert held.cursor is None and held.observations == ()

    durable = _decode(_encode(first.cursor, module.StreamCursor), module.StreamCursor)
    _write(path, rows + [rows[2]])
    (reopened,) = adapter.discover(
        replace(root, evidence=Evidence(key, _committed_view(first)))
    )
    second = adapter.read_delta(reopened, durable)
    (revised,) = second.observations
    assert (revised.key, revised.revision) == (partial.key, partial.revision + 1)
    assert revised.usage.tokens.total_tokens == 18

    parent, completed = (
        "00000000-0000-0000-0000-000000000220",
        "00000000-0000-0000-0000-000000000221",
    )
    call = "toolu-private-agent"
    _write(
        path,
        [
            user(checkout),
            request(
                checkout,
                uuid=parent,
                stop="tool_use",
                isSidechain=False,
                content=[
                    {
                        "type": "tool_use",
                        "id": call,
                        "name": "Agent",
                        "input": {"prompt": "private"},
                    }
                ],
            ),
            request(
                checkout,
                req="req-child",
                msg="msg-child",
                counts=claude_usage(8),
                isSidechain=True,
                parent_tool_use_id=call,
            ),
            claude_row(
                "user",
                checkout,
                uuid=completed,
                parentUuid=parent,
                sourceToolAssistantUUID=parent,
                isSidechain=False,
                message={
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": call,
                            "content": "private-child",
                        }
                    ],
                },
                toolUseResult={
                    "status": "completed",
                    "agentId": "private-id",
                    "usage": claude_usage(8),
                },
            ),
        ],
    )
    (nested,) = adapter.discover(root)
    result = adapter.read_delta(nested, None)
    assert sorted(item.usage.tokens.output_tokens for item in result.observations) == [
        4,
        8,
    ]


def test_claude_held_startup_replays_after_checkout_proof(monkeypatch, source):
    module, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    path = directory / "startup.jsonl"
    rows = _native_startup_rows(checkout)
    command = shlex.join(
        [
            "aitm-usage",
            "--project",
            "/private/tmp/declared-project-secret",
            "scope",
            "mark",
            "--marker",
            "/private/tmp/marker-command-secret",
            "--session-id",
            rows[-1]["sessionId"],
            "--json",
        ]
    )
    following = _native_tool_turn(
        checkout, command, json.dumps({"command_id": str(COMMAND), "status": "queued"})
    )
    for row in following:
        row["sessionId"] = rows[-1]["sessionId"]
    rows.extend(following)
    _write(path, rows)
    (locator,) = adapter.discover(replace(root, checkout_anchors=()))
    held = adapter.read_delta(locator, None)
    assert held.observations == ()
    assert held.cursor.checkpoint.cursor.offset < path.stat().st_size
    (linked,) = [
        item for item in held.boundaries if item.boundary.receipt_ref is not None
    ]
    assert linked.boundary.ordinal == len(rows) - 1
    assert linked.project_context is None
    (verified,) = adapter.discover(root)
    admitted = adapter.read_delta(verified, held.cursor)
    assert len(admitted.observations) == 2
    assert all(item.project_context is not None for item in admitted.observations)
    assert admitted.cursor.checkpoint.cursor.offset == path.stat().st_size


def test_desktop_retains_unfinished_native_turn_before_restart(monkeypatch, source):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    path = directory / "desktop.jsonl"
    rows = _desktop(checkout)
    _write(path, rows[:-1])
    (locator,) = adapter.discover(root)
    pending = adapter.read_delta(locator, None)
    assert pending.cursor is None
    assert not pending.observations

    _write(path, rows)
    (locator,) = adapter.discover(root)
    complete = adapter.read_delta(locator, pending.cursor)
    assert complete.observations
    assert complete.cursor.checkpoint.cursor.offset == path.stat().st_size


def test_claude_holds_linked_receipt_until_adjoining_request(monkeypatch, source):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    path = directory / "linked.jsonl"
    first = user(checkout)
    command = shlex.join(
        [
            "aitm-usage",
            "--project",
            "/private/tmp/declared-project",
            "scope",
            "mark",
            "--marker",
            "/private/tmp/marker",
            "--session-id",
            first["sessionId"],
            "--json",
        ]
    )
    rows = [
        first,
        *_native_tool_turn(
            checkout,
            command,
            json.dumps({"command_id": str(COMMAND), "status": "queued"}),
        ),
    ]
    _write(path, rows[:-1])
    (locator,) = adapter.discover(root)
    pending = adapter.read_delta(locator, None)
    assert pending.cursor is None
    assert not pending.observations

    _write(path, rows)
    (locator,) = adapter.discover(root)
    complete = adapter.read_delta(locator, pending.cursor)
    assert complete.cursor.checkpoint.cursor.offset == path.stat().st_size
    (proof,) = [
        item for item in complete.boundaries if item.boundary.receipt_ref is not None
    ]
    assert proof.boundary.ordinal == len(rows) - 1


def _restart_rows(case, checkout):
    if case == "desktop":
        rows = _desktop(checkout)
        first_turn_end = len(rows)
        turn = UUID(int=0x199)
        time = AFTER + timedelta(seconds=1)
        total = rows[-2]["payload"]["info"]["total_token_usage"]
        extra = usage(5, 2)
        cumulative = usage(
            total["input_tokens"] + 5,
            total["output_tokens"] + 2,
            cache=total["cached_input_tokens"],
            reasoning=total["reasoning_output_tokens"],
        )
        rows.extend(
            [
                *begin(checkout, turn, time=time),
                response(
                    "second-response-private", cumulative, extra, time=time, turn=turn
                ),
                counter(cumulative, extra, time=time),
                end(turn, time=time),
            ]
        )
        return rows, {1, first_turn_end}
    if case == "streamed":
        rows = _rows(CLAUDE_FIXTURE, checkout)
        return [*rows, cost(**{MODEL: model_counts()})], set(range(1, len(rows) + 1))
    if case == "receipt":
        first = user(checkout)
        command = shlex.join(
            [
                "aitm-usage",
                "--project",
                "/private/tmp/private-project",
                "scope",
                "mark",
                "--marker",
                "/private/tmp/private-marker",
                "--session-id",
                first["sessionId"],
                "--json",
            ]
        )
        output = json.dumps({"command_id": str(COMMAND), "status": "queued"})
        return [first, *_native_tool_turn(checkout, command, output)], {1}
    call = "toolu-private-agent"
    child_tool = "toolu-private-child-bash"
    parent, child, child_result, completed = (
        str(UUID(int=i)) for i in range(0x231, 0x235)
    )
    rows = [
        user(checkout),
        request(
            checkout,
            uuid=parent,
            stop="tool_use",
            isSidechain=False,
            content=[
                {
                    "type": "tool_use",
                    "id": call,
                    "name": "Agent",
                    "input": {"prompt": "private"},
                }
            ],
        ),
        request(
            checkout,
            uuid=child,
            req="req-child",
            msg="msg-child",
            counts=claude_usage(8),
            stop="tool_use",
            isSidechain=True,
            parent_tool_use_id=call,
            content=[
                {
                    "type": "tool_use",
                    "id": child_tool,
                    "name": "Bash",
                    "input": {"command": "true"},
                }
            ],
        ),
        claude_row(
            "user",
            checkout,
            uuid=child_result,
            parentUuid=child,
            sourceToolAssistantUUID=child,
            isSidechain=True,
            parent_tool_use_id=call,
            message={
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": child_tool,
                        "content": "private",
                    }
                ],
            },
        ),
        claude_row(
            "user",
            checkout,
            uuid=completed,
            parentUuid=parent,
            sourceToolAssistantUUID=parent,
            isSidechain=False,
            message={
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": call,
                        "content": "private-child",
                    }
                ],
            },
            toolUseResult={
                "status": "completed",
                "agentId": "private-id",
                "usage": claude_usage(8),
            },
        ),
    ]
    return rows, {1}


@pytest.mark.parametrize("case", ["desktop", "streamed", "nested", "receipt"])
def test_every_native_split_matches_one_read_after_restart(monkeypatch, source, case):
    module, adapter, root = _adapter(monkeypatch, source)
    key, directory, checkout = source
    path = directory / "restart.jsonl"
    rows, safe_splits = _restart_rows(case, checkout)

    def latest(*batches):
        return {item.key: item for batch in batches for item in batch.observations}

    _write(path, rows)
    (locator,) = adapter.discover(root)
    whole = adapter.read_delta(locator, None)
    assert whole.observations
    assert whole.cursor.checkpoint.cursor.offset == path.stat().st_size

    for split in range(1, len(rows)):
        offset = _write(path, rows[:split])
        (locator,) = adapter.discover(root)
        prefix = adapter.read_delta(locator, None)
        if split not in safe_splits:
            assert prefix.cursor is None, (case, split)
            assert not prefix.observations
        else:
            assert prefix.cursor is not None, (case, split)
        if prefix.cursor is not None:
            assert prefix.cursor.checkpoint.cursor.offset == offset, (case, split)
            prior = _decode(
                _encode(prefix.cursor, module.StreamCursor), module.StreamCursor
            )
            restarted_root = replace(
                root, evidence=Evidence(key, _committed_view(prefix))
            )
        else:
            prior = None
            restarted_root = root
        _write(path, rows)
        (restarted,) = adapter.discover(restarted_root)
        suffix = module.ProviderAdapter().read_delta(restarted, prior)
        assert latest(prefix, suffix) == latest(whole), (case, split)
        expected_proofs = {
            item.boundary for item in whole.boundaries if item.boundary.receipt_ref
        }
        actual_proofs = {
            item.boundary
            for batch in (prefix, suffix)
            for item in batch.boundaries
            if item.boundary.receipt_ref
        }
        assert actual_proofs == expected_proofs, (case, split)
