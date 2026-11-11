"""Sanitized native-shaped rows from #88/#96 and deterministic replay variants."""

import json
import shlex
from dataclasses import replace
from datetime import timedelta
from hashlib import sha256
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
    event,
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
from aitm_usage.sources.scan import _capture_position
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    DiagnosticCode,
    LedgerView,
    ProcessingTier,
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


def _receipt_rows(checkout, *, settle=False):
    first, last = usage(8, 2), usage(6, 2)
    marker = tool_call(
        SimpleNamespace(root=checkout), "/private/tmp/command-body-secret"
    )
    rows = [
        startup(checkout, originator="Codex Desktop"),
        *begin(checkout),
        marker,
        response("before-private", first, first),
        tool_output(),
        counter(first, first),
        response("after-private", usage(14, 4), last),
        counter(usage(14, 4), last),
        end(),
    ]
    if settle:
        followup = UUID(int=0x211)
        rows.extend((*begin(checkout, followup), end(followup)))
    return rows


def _receipt_request(batch):
    (boundary,) = [
        item.boundary
        for item in batch.boundaries
        if item.boundary.kind is BoundaryKind.REQUEST and item.boundary.receipt_ref
    ]
    return boundary


def test_neutral_desktop_receipt_is_evidence_without_authority(
    monkeypatch, source, tmp_path
):
    module, adapter, root = _adapter(monkeypatch, source)
    key, directory, _ = source
    foreign = tmp_path / "foreign-private"
    foreign.mkdir()
    _write(directory / "receipt.jsonl", _receipt_rows(foreign))
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


def test_codex_receipt_usage_span_includes_the_later_native_counter(
    monkeypatch, source
):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    rows = _receipt_rows(checkout, settle=True)
    rows.insert(8, event("token_count", info=None))
    _write(directory / "receipt.jsonl", rows)
    (locator,) = adapter.discover(root)

    result = adapter.read_delta(locator, None)
    boundary = _receipt_request(result)
    (observation,) = [
        item for item in result.observations if item.usage.boundary == boundary
    ]
    assert observation.usage.boundary.ordinal == 7
    assert observation.span_end == 10


def test_monitor_rescan_enrolls_only_an_exact_receipt_at_the_capture_limit(
    monkeypatch, source, tmp_path
):
    _, adapter, root = _adapter(monkeypatch, source)
    key, directory, _ = source
    foreign = tmp_path / "foreign-private"
    foreign.mkdir()
    path = directory / "receipt.jsonl"
    rows = _receipt_rows(foreign, settle=True)
    _write(path, rows)
    (locator,) = adapter.discover(root)
    limit = _capture_position(locator._source, None).cursor
    _write(path, [*rows, event("token_count", info=None)])

    lookahead = adapter.read_delta(locator, None, _capture_limit=limit)
    assert not lookahead.observations
    boundary = _receipt_request(lookahead)
    forged = replace(
        boundary, receipt_ref=key.pseudonymize("scope-receipt", "unmatched")
    )
    assert not adapter.read_delta(
        locator, None, _scope_boundaries=(forged,), _capture_limit=limit
    ).observations

    scoped = adapter.read_delta(
        locator, None, _scope_boundaries=(boundary,), _capture_limit=limit
    )
    (observation,) = scoped.observations
    assert observation.usage.boundary == boundary
    assert observation.usage.tokens.total_tokens == 8
    assert observation.project_context is None
    assert scoped.cursor.checkpoint.cursor == limit


def test_monitor_scope_rescan_refuses_a_changed_raw_prefix(
    monkeypatch, source, tmp_path
):
    module, adapter, root = _adapter(monkeypatch, source)
    _, directory, _ = source
    foreign = tmp_path / "foreign-private"
    foreign.mkdir()
    path = directory / "receipt.jsonl"
    rows = _receipt_rows(foreign, settle=True)
    _write(path, rows)
    (locator,) = adapter.discover(root)
    lookahead = adapter.read_delta(locator, None)
    boundary = _receipt_request(lookahead)

    scan = module.scan

    def change_before_rescan(candidate, *args, **kwargs):
        if candidate._enrollments:
            rows[4] = response("rewritten-before-private", usage(8, 2), usage(8, 2))
            _write(path, rows)
        return scan(candidate, *args, **kwargs)

    monkeypatch.setattr(module, "scan", change_before_rescan)
    scoped = adapter.read_delta(locator, None, _scope_boundaries=(boundary,))
    assert not scoped.observations and scoped.cursor is None
    assert DiagnosticCode.BOUNDARY_UNVERIFIED in {
        item.code for item in scoped.diagnostics
    }


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


@pytest.mark.parametrize("terminal_kind", ["result", "cost-state"])
def test_claude_revision_witnesses_bind_each_committing_row(
    monkeypatch, source, terminal_kind
):
    module, adapter, root = _adapter(monkeypatch, source)
    key, directory, checkout = source
    path = directory / "revisions.jsonl"
    models = {MODEL: model_counts(8, 4, 10, 6, 8)}
    terminal = (
        claude_row(
            "result", checkout, subtype="success", is_error=False, modelUsage=models
        )
        if terminal_kind == "result"
        else cost(**models)
    )
    rows = [
        user(checkout),
        request(checkout, counts=claude_usage(2), stop=None),
        request(checkout, req="req-second", msg="msg-second"),
        request(checkout, counts=claude_usage(3), stop=None),
        request(checkout),
        terminal,
    ]
    _write(path, rows)
    (locator,) = adapter.discover(root)
    legacy = adapter.read_delta(locator, None)
    assert [
        (item.usage.boundary.ordinal, item.revision) for item in legacy.observations
    ] == [(1, 1), (2, 1), (1, 2), (1, 3), (1, 4), (2, 2)]

    witnesses = []
    batch = adapter.read_delta(locator, None, _revision_witnesses=witnesses)
    assert _encode(batch, module.AdapterBatch) == _encode(legacy, module.AdapterBatch)
    assert [
        (
            observation.usage.boundary.ordinal,
            witness.predecessor_ordinal,
            witness.later_ordinal,
            witness.kind,
        )
        for observation, witness in witnesses
    ] == [
        (1, 1, 3, "assistant"),
        (1, 3, 4, "assistant"),
        (1, 4, 5, terminal_kind),
        (2, 2, 5, terminal_kind),
    ]
    native_lines = path.read_bytes().splitlines(keepends=True)
    for (observation, witness), (prior_index, current_index) in zip(
        witnesses, [(0, 2), (2, 3), (3, 4), (1, 5)], strict=True
    ):
        assert witness.predecessor is batch.observations[prior_index]
        assert observation is batch.observations[current_index]
        assert witness.predecessor_material == key.pseudonymize(
            "claude-revision-material",
            _encode(
                Revision(
                    witness.predecessor.key,
                    witness.predecessor.revision,
                    witness.predecessor.usage,
                ),
                Revision,
            ),
        )
        assert witness.predecessor_material != witness.successor_material
        row_prefix = sha256(b"".join(native_lines[: witness.later_ordinal + 1]))
        stream = observation.usage.boundary.stream_ref.value
        assert witness.prefix_ref == key.pseudonymize(
            "claude-revision-prefix",
            f"{stream}:{witness.later_ordinal}:{row_prefix.hexdigest()}",
        )
    assert witnesses[-2][1].prefix_ref == witnesses[-1][1].prefix_ref
    assert [proof.terminal_contributor_spans for _, proof in witnesses] == [
        (),
        (),
        ((1, 5), (2, 3)),
        ((1, 5), (2, 3)),
    ]
    assert len({proof.prefix_ref for _, proof in witnesses}) == 3
    assert "req-first" not in repr(witnesses)

    archive = directory.parent / "archive-private"
    archive.mkdir()
    (archive / path.name).write_bytes(path.read_bytes())
    (archived,) = adapter.discover(replace(root, path=archive))
    copied_witnesses = []
    copied = adapter.read_delta(archived, None, _revision_witnesses=copied_witnesses)
    assert copied_witnesses == witnesses
    assert (
        copied.cursor.checkpoint.cursor.locator_ref
        != batch.cursor.checkpoint.cursor.locator_ref
    )


def test_claude_terminal_contributor_span_tracks_stop_with_unchanged_counts(
    monkeypatch, source
):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    _write(
        directory / "terminal.jsonl",
        [
            user(checkout),
            request(checkout, stop=None),
            request(checkout, req="req-second", msg="msg-second"),
            request(checkout),
            user(checkout),
            cost(**{MODEL: model_counts(8, 4, 10, 6, 8)}),
        ],
    )
    (locator,) = adapter.discover(root)
    witnesses = []
    batch = adapter.read_delta(locator, None, _revision_witnesses=witnesses)
    assert [item.revision for item in batch.observations] == [1, 1, 2, 2]
    (_, first), (_, second) = witnesses
    assert first.predecessor_ordinal == 1
    assert first.later_ordinal == second.later_ordinal == 5
    assert (
        first.terminal_contributor_spans
        == second.terminal_contributor_spans
        == (
            (1, 4),
            (2, 3),
        )
    )


@pytest.mark.parametrize(
    "linkage",
    [
        "linked",
        "foreign",
        "missing",
        "late-repaired",
        "foreign-after-link",
        "same-after-reset",
        "foreign-after-reset",
        "missing-after-reset",
        "unverified-at-origin",
    ],
)
def test_claude_terminal_witness_requires_verified_nested_contributor(
    monkeypatch, source, linkage
):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    tool_id = "toolu-terminal-agent"

    def child(parent, output=8):
        return request(
            checkout,
            req="req-terminal-child",
            msg="msg-terminal-child",
            counts=claude_usage(output),
            isSidechain=True,
            parent_tool_use_id=parent,
        )

    reset_updates = {
        "same-after-reset": tool_id,
        "foreign-after-reset": "toolu-unrelated",
        "missing-after-reset": None,
    }
    first_parent = {
        "linked": tool_id,
        "missing": None,
        "foreign-after-link": tool_id,
        "unverified-at-origin": tool_id,
    } | dict.fromkeys(reset_updates, tool_id)
    rows = [
        user(checkout),
        request(
            checkout,
            uuid=str(UUID(int=0x230)),
            stop="tool_use",
            isSidechain=False,
            content=[
                {
                    "type": "tool_use",
                    "id": tool_id,
                    "name": "Agent",
                    "input": {"prompt": "private"},
                }
            ],
        ),
    ]
    if linkage == "unverified-at-origin":
        rows.append(user(checkout))
    rows.append(child(first_parent.get(linkage, "toolu-unrelated")))
    if linkage in reset_updates:
        rows.append(user(checkout))
    child_output = 8
    updates = {
        "late-repaired": tool_id,
        "foreign-after-link": "toolu-unrelated",
    } | reset_updates
    if linkage in updates:
        child_output = 9
        rows.append(child(updates[linkage], child_output))
    rows.append(
        claude_row(
            "result",
            checkout,
            subtype="success",
            is_error=False,
            modelUsage={MODEL: model_counts(4 + child_output, 4, 10, 6, 8)},
        )
    )
    _write(directory / "terminal-agent.jsonl", rows)
    (locator,) = adapter.discover(root)
    legacy = adapter.read_delta(locator, None)
    assert legacy.cursor is not None
    completed = [
        item
        for item in legacy.observations
        if item.usage.availability is Availability.COMPLETE
    ]
    assert [item.usage.tokens.output_tokens for item in completed] == [4, child_output]
    assert (
        DiagnosticCode.OVERLAP_UNVERIFIED in {d.code for d in legacy.diagnostics}
    ) is (linkage in {"foreign", "missing", "late-repaired", "foreign-after-link"})

    witnesses = []
    batch = adapter.read_delta(locator, None, _revision_witnesses=witnesses)
    assert batch == legacy
    if linkage in {"linked", "same-after-reset"}:
        ((successor, witness),) = witnesses
        assert successor.usage.tokens.output_tokens == 4
        child_end = 5 if linkage == "same-after-reset" else 3
        assert witness.terminal_contributor_spans == ((1, 2), (2, child_end))
    else:
        assert witnesses == []


def test_claude_terminal_witness_holds_nonzero_excluded_baseline(monkeypatch, source):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    before = CUTOFF - timedelta(seconds=1)
    _write(
        directory / "excluded.jsonl",
        [
            user(checkout, before),
            request(checkout, time=before),
            request(checkout, req="req-in-window", msg="msg-in-window"),
            cost(**{MODEL: model_counts(8, 4, 10, 6, 8)}),
        ],
    )
    (locator,) = adapter.discover(root)
    legacy = adapter.read_delta(locator, None)
    assert [item.usage.availability for item in legacy.observations] == [
        Availability.PARTIAL,
        Availability.COMPLETE,
    ]

    witnesses = []
    assert adapter.read_delta(locator, None, _revision_witnesses=witnesses) == legacy
    assert witnesses == []


def test_claude_terminal_witness_holds_contributor_from_prior_read(monkeypatch, source):
    _, adapter, root = _adapter(monkeypatch, source)
    key, directory, checkout = source
    path = directory / "resumed-terminal.jsonl"
    prior_rows = [user(checkout), request(checkout)]
    _write(path, prior_rows)
    (locator,) = adapter.discover(root)
    first = adapter.read_delta(locator, None)
    _write(
        path,
        [
            *prior_rows,
            request(checkout, req="req-in-window", msg="msg-in-window"),
            cost(**{MODEL: model_counts(8, 4, 10, 6, 8)}),
        ],
    )
    (reopened,) = adapter.discover(
        replace(root, evidence=Evidence(key, _committed_view(first)))
    )
    legacy = adapter.read_delta(reopened, first.cursor)
    assert [item.usage.availability for item in legacy.observations] == [
        Availability.PARTIAL,
        Availability.COMPLETE,
        Availability.COMPLETE,
    ]

    witnesses = []
    assert (
        adapter.read_delta(reopened, first.cursor, _revision_witnesses=witnesses)
        == legacy
    )
    assert witnesses == []


@pytest.mark.parametrize("regression", [False, True])
def test_claude_processing_invalidation_requires_accepted_counts(
    monkeypatch, source, regression
):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    rows = [
        user(checkout),
        request(checkout, counts=claude_usage(3), stop=None),
        request(
            checkout, counts=claude_usage(2 if regression else 3) | {"speed": "fast"}
        ),
        request(checkout, counts=claude_usage(4)),
    ]
    _write(directory / "tier.jsonl", rows)
    (locator,) = adapter.discover(root)
    legacy = adapter.read_delta(locator, None)
    assert legacy.observations[0].usage.processing_tier is ProcessingTier.STANDARD
    assert legacy.observations[1].usage.processing_tier is None
    assert (
        DiagnosticCode.COUNTER_REGRESSION in {d.code for d in legacy.diagnostics}
    ) is regression

    witnesses = []
    batch = adapter.read_delta(locator, None, _revision_witnesses=witnesses)
    assert batch == legacy
    if regression:
        assert witnesses == []
    else:
        (observation, proof), *rest = witnesses
        assert observation is batch.observations[1]
        assert proof.predecessor is batch.observations[0]
        assert proof.kind == "assistant"


def test_claude_revision_witness_requires_predecessor_in_fixed_read(
    monkeypatch, source
):
    _, adapter, root = _adapter(monkeypatch, source)
    key, directory, checkout = source
    path = directory / "resumed.jsonl"
    rows = _rows(CLAUDE_FIXTURE, checkout)
    _write(path, rows[:2])
    (locator,) = adapter.discover(root)
    first = adapter.read_delta(locator, None)
    _write(path, rows)
    (reopened,) = adapter.discover(
        replace(root, evidence=Evidence(key, _committed_view(first)))
    )
    witnesses = []
    resumed = adapter.read_delta(reopened, first.cursor, _revision_witnesses=witnesses)
    assert [item.revision for item in resumed.observations] == [2]
    assert witnesses == []


def test_claude_revision_witnesses_follow_the_fixed_capture_frontier(
    monkeypatch, source
):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    path = directory / "frontier.jsonl"
    rows = [
        user(checkout),
        request(checkout, counts=claude_usage(3), stop=None),
        request(checkout),
    ]
    _write(path, rows)
    (locator,) = adapter.discover(root)
    limit = _capture_position(locator._source, None).cursor
    _write(path, [*rows, cost(**{MODEL: model_counts()})])
    fixed = adapter.read_delta(locator, None, _capture_limit=limit)
    assert fixed.cursor.checkpoint.cursor == limit
    assert all(
        item.usage.availability is Availability.PARTIAL for item in fixed.observations
    )

    witnesses = []
    bounded = adapter.read_delta(
        locator, None, _capture_limit=limit, _revision_witnesses=witnesses
    )
    assert bounded == fixed
    ((observation, witness),) = witnesses
    assert observation is bounded.observations[-1]
    assert (witness.kind, witness.later_ordinal) == ("assistant", 2)


def test_claude_revision_witnesses_withheld_after_failed_rescan(
    monkeypatch, source, tmp_path
):
    module, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    foreign = tmp_path / "foreign-private"
    foreign.mkdir()
    path = directory / "rescan.jsonl"
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
            user(checkout)["sessionId"],
            "--json",
        ]
    )
    rows = [
        user(checkout),
        request(
            checkout,
            req="req-prefix",
            msg="msg-prefix",
            counts=claude_usage(3),
            stop=None,
        ),
        request(checkout, req="req-prefix", msg="msg-prefix"),
        user(foreign),
        *_native_tool_turn(
            foreign,
            command,
            json.dumps({"command_id": str(COMMAND), "status": "queued"}),
        ),
    ]
    _write(path, rows)
    (locator,) = adapter.discover(root)
    lookahead = adapter.read_delta(locator, None)
    assert [item.revision for item in lookahead.observations] == [1, 2]
    boundary = _receipt_request(lookahead)

    scan = module.scan

    def change_before_rescan(candidate, *args, **kwargs):
        if candidate._enrollments:
            rows[2] = request(
                checkout, req="req-prefix", msg="msg-prefix", counts=claude_usage(6)
            )
            _write(path, rows)
        return scan(candidate, *args, **kwargs)

    monkeypatch.setattr(module, "scan", change_before_rescan)
    witnesses = []
    failed = adapter.read_delta(
        locator, None, _scope_boundaries=(boundary,), _revision_witnesses=witnesses
    )
    assert not failed.observations and failed.cursor is None
    assert not witnesses
    assert DiagnosticCode.BOUNDARY_UNVERIFIED in {d.code for d in failed.diagnostics}


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


def test_claude_aggregate_retraction_has_no_revision_witness(monkeypatch, source):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    path = directory / "nested.jsonl"
    rows, _ = _restart_rows("nested", checkout)
    _write(path, [*rows[:2], rows[-1], *rows[2:-1]])
    (locator,) = adapter.discover(root)
    legacy = adapter.read_delta(locator, None)
    (retracted,) = [
        item
        for item in legacy.observations
        if item.usage.availability is Availability.UNKNOWN
    ]
    assert retracted.revision == 2
    assert DiagnosticCode.OVERLAP_UNVERIFIED in {d.code for d in legacy.diagnostics}

    witnesses = []
    assert adapter.read_delta(locator, None, _revision_witnesses=witnesses) == legacy
    assert witnesses == []


def test_claude_revision_witness_refuses_a_foreign_message(monkeypatch, source):
    _, adapter, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    _write(
        directory / "message.jsonl",
        [
            user(checkout),
            request(checkout, stop=None),
            request(checkout, msg="msg-foreign", counts=claude_usage(5)),
        ],
    )
    (locator,) = adapter.discover(root)
    legacy = adapter.read_delta(locator, None)
    assert [item.revision for item in legacy.observations] == [1]
    assert DiagnosticCode.IDENTITY_CONFLICT in {d.code for d in legacy.diagnostics}

    witnesses = []
    assert adapter.read_delta(locator, None, _revision_witnesses=witnesses) == legacy
    assert witnesses == []


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
