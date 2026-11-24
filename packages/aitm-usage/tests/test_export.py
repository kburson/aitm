import json
import os
import stat
import subprocess
import sys
from collections import Counter
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call
from uuid import UUID

import pytest
from test_accounting import reference_rates as reference_rates
from test_ledger import _LedgerRows, _memory_ledger
from test_ledger import ledger_path_metadata as ledger_path_metadata
from test_ledger import modules as modules

from aitm_usage import ledger as store
from aitm_usage.accounting import account_observations
from aitm_usage.ledger import Ledger
from aitm_usage.pricing import load_rate_card
from aitm_usage.scopes import (
    BoundaryEvidence,
    drain_inbox,
    enqueue_command,
    enqueue_marker,
)
from aitm_usage.types import (
    AdapterResult,
    Availability,
    BoundaryKind,
    ClientVersion,
    Diagnostic,
    DiagnosticCode,
    InboxCommand,
    ItemKey,
    ItemKind,
    LedgerBatch,
    LedgerView,
    MarkerDisposition,
    ModelLabel,
    ProcessingTier,
    Provider,
    Revision,
    ScopeCorrection,
    ScopeEnrollment,
    ScopeMarker,
    SourceBoundary,
    TokenCounts,
    UsageObservation,
    WorkPhase,
)

PROJECT = UUID(int=91)
NOW = datetime(2026, 11, 9, 18, tzinfo=UTC)
CANARY = "private-export-canary"
SCHEMA = "aitm.usage.export/v1"
FIXTURE_KEY = b"export-policy-tests".ljust(32, b"e")


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "_control_root", lambda: tmp_path / "control")
    return Ledger.initialize(tmp_path / f"{CANARY}-project", PROJECT)


def _ref(project, name):
    return project.pseudonymize("export-fixture", f"{CANARY}:{name}")


def _public(ref):
    return ref.value.rsplit(":", 1)[0]


def _observation(project, name, *, partial=False):
    marker_id = UUID(int={"first": 1, "second": 2, "unbound": 3}[name])
    receipt = project.pseudonymize("scope-receipt", str(marker_id))
    boundary = SourceBoundary(
        Provider.CODEX,
        _ref(project, f"{name}:stream"),
        _ref(project, f"{name}:session"),
        1,
        BoundaryKind.REQUEST,
        _ref(project, f"{name}:boundary"),
        receipt_ref=receipt,
    )
    marker = ScopeMarker(
        marker_id,
        boundary.provider,
        boundary.session_ref,
        1,
        boundary.kind,
        boundary.boundary_ref,
        NOW,
        ItemKey(ItemKind.ISSUE, 91),
        WorkPhase.PLANNING,
        _ref(project, f"{name}:participant"),
        PROJECT,
        receipt_ref=receipt,
        attempt_ref=_ref(project, f"{name}:attempt"),
    )
    record = UsageObservation(
        boundary,
        NOW,
        ClientVersion.CODEX_0_167_0_ALPHA_3_2,
        1,
        TokenCounts(500, 400, 0, 0, None if partial else 200, 150),
        Availability.PARTIAL if partial else Availability.COMPLETE,
        request_ref=boundary.boundary_ref,
        message_ref=_ref(project, f"{name}:message"),
        model=ModelLabel.GPT_6_ASTRA,
        processing_tier=ProcessingTier.STANDARD,
        context_tokens=500,
    )
    return Revision(_ref(project, f"{name}:observation"), 1, record), marker


def _seed(project):
    first, first_marker = _observation(project, "first")
    second, second_marker = _observation(project, "second", partial=True)
    for marker in (first_marker, second_marker):
        enqueue_marker(project.root, marker)
    with project.writer() as writer:
        writer.apply(
            account_observations(
                AdapterResult((second, first)), load_rate_card(), ledger=project
            )
        )
        drained = drain_inbox(
            writer,
            tuple(BoundaryEvidence(rev.record.boundary) for rev in (first, second)),
        )
    assert [receipt.disposition for receipt in drained.receipts] == [
        MarkerDisposition.ACCEPTED,
        MarkerDisposition.ACCEPTED,
    ]
    return first, second, first_marker


@pytest.fixture
def export_evidence():
    return _memory_ledger(store, PROJECT, FIXTURE_KEY)


def _projected_view(project, card):
    first, first_marker = _observation(project, "first")
    second, second_marker = _observation(project, "second", partial=True)
    accounting = account_observations(
        AdapterResult((second, first)), card, ledger=project
    )
    enrollments = tuple(
        Revision(
            _ref(project, str(marker.marker_id)),
            1,
            ScopeEnrollment(marker, revision.record.boundary, None),
        )
        for revision, marker in ((first, first_marker), (second, second_marker))
    )
    return (
        LedgerView(PROJECT, 1, (*accounting.revisions, *enrollments), ()),
        first,
        second,
        first_marker,
    )


def _correct(project, marker):
    correction = ScopeCorrection(
        UUID(int=19),
        PROJECT,
        replace(marker, item=ItemKey(ItemKind.ISSUE, 86)),
        _ref(project, "correction-evidence"),
    )
    enqueue_command(
        project.root, InboxCommand(correction.correction_id, PROJECT, correction)
    )
    with project.writer() as writer:
        assert (
            drain_inbox(writer, ()).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )


def _canonical(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()


def _snapshot(path):
    return (path / "manifest.json").read_bytes(), (path / "usage.jsonl").read_bytes()


def _changed_snapshot(original, destination, *, mutate_row=None, mutate_manifest=None):
    manifest, data = _changed_snapshot_bytes(
        *_snapshot(original), mutate_row=mutate_row, mutate_manifest=mutate_manifest
    )
    destination.mkdir()
    (destination / "manifest.json").write_bytes(manifest)
    (destination / "usage.jsonl").write_bytes(data)
    return destination


def _changed_snapshot_bytes(manifest, data, *, mutate_row=None, mutate_manifest=None):
    manifest = json.loads(manifest)
    if mutate_row is not None:
        rows = [json.loads(line) for line in data.splitlines()]
        mutate_row(rows)
        data = b"".join(_canonical(row) + b"\n" for row in rows)
    manifest["sha256"] = sha256(data).hexdigest()
    if mutate_manifest is not None:
        mutate_manifest(manifest)
    return _canonical(manifest) + b"\n", data


def _export():
    # Keep the first test-first run a feature assertion, even before the module exists.
    try:
        from aitm_usage.export import export_as_of
    except ModuleNotFoundError as exc:
        if exc.name != "aitm_usage.export":
            raise
        pytest.fail("Missing U07 as-of export contract")
    return export_as_of


def test_replay_cutoff_and_pending_finalization(project, tmp_path):
    export_as_of = _export()
    from fixtures.receiver import ImportInterrupted, Receiver, ReceiverConflict

    first, second, marker = _seed(project)
    first_key, second_key = _public(first.key), _public(second.key)
    card = load_rate_card()
    before = project.as_of()
    original = tmp_path / "original"
    with project.writer() as writer:
        result = _invoke_installed_export(
            project, tmp_path, before.sequence, card.basis.identifier, original
        )
        assert result.returncode == 0, result.stderr
        assert writer.as_of().sequence == before.sequence
    receipt = export_as_of(before, card, original)
    cli_receipt = json.loads(result.stdout)
    assert (cli_receipt["cutoff"], cli_receipt["sha256"]) == (
        before.sequence,
        receipt.sha256,
    )
    original_manifest, original_data = _snapshot(original)
    rows = {row["source"]: row for row in map(json.loads, original_data.splitlines())}
    assert rows[first_key]["scope"]["item"] == {"kind": "issue", "id": 91}
    enrollment = next(
        rev
        for rev in before.current
        if isinstance(rev.record, ScopeEnrollment) and rev.record.marker == marker
    )
    assert rows[first_key]["scope"]["revision"] == {
        "number": 1,
        "source": _public(enrollment.key),
    }
    assert rows[first_key]["price"] == {
        "availability": "complete",
        "currency": "USD",
        "rate_basis": card.basis.identifier,
        "usd": "0.0114",
    }
    assert rows[second_key]["price"]["usd"] is None
    assert rows[second_key]["availability"] == "partial"
    assert receipt.sha256 == sha256(original_data).hexdigest()
    assert list(rows) == sorted(rows)
    assert json.loads(original_manifest)["schema"] == SCHEMA

    database = tmp_path / "receiver.sqlite"
    invalid_digest = _changed_snapshot(
        original,
        tmp_path / "invalid-digest",
        mutate_manifest=lambda manifest: manifest.update(sha256="0" * 64),
    )
    with Receiver(database, PROJECT) as receiver:
        with pytest.raises(ValueError, match="Invalid usage export digest"):
            receiver.import_snapshot(invalid_digest)
        assert receiver.watermark is None
        assert receiver.accepted == {}
        assert receiver.pending == set()
        with pytest.raises(ImportInterrupted):
            receiver.import_snapshot(original, interrupt_after=2)
        assert receiver.watermark is None
        assert receiver.accepted == {}
        assert receiver.pending == set()
    with Receiver(database, PROJECT) as receiver:
        assert receiver.import_snapshot(original) == "imported"
        accepted_first = receiver.accepted[first_key]
        assert accepted_first == sha256(_canonical(rows[first_key])).hexdigest()
        assert receiver.pending == {second_key}
        assert receiver.watermark == before.sequence
        assert receiver.import_snapshot(original) == "duplicate"
        assert (
            receiver.ingest_usage(first_key, _canonical(rows[first_key])) == "duplicate"
        )

        contradictory = dict(rows[first_key], client_version="unknown")
        with pytest.raises(ReceiverConflict, match="Different payload"):
            receiver.ingest_usage(first_key, _canonical(contradictory))
        assert receiver.accepted == {first_key: accepted_first}

    # Move the watermark while the partial record stays withheld.
    diagnostic = Diagnostic(DiagnosticCode.COVERAGE_GAP, NOW, Provider.CLAUDE)
    project.apply(LedgerBatch((Revision(_ref(project, "gap"), 1, diagnostic),)))
    advanced = project.as_of()
    gap = tmp_path / "advanced"
    changed_basis = tmp_path / "pending-new-basis"
    export_as_of(advanced, replace(card, version="2026-11-10"), changed_basis)

    def contradict_pending(rows):
        row = next(item for item in rows if item["source"] == second_key)
        row["tokens"]["input_tokens"] = 501

    conflicting_pending = _changed_snapshot(
        changed_basis, tmp_path / "pending-conflict", mutate_row=contradict_pending
    )
    with Receiver(database, PROJECT) as receiver:
        with pytest.raises(
            ReceiverConflict, match=r"source provenance \(observation\)"
        ):
            receiver.import_snapshot(conflicting_pending)
        assert receiver.watermark == before.sequence
        assert receiver.accepted == {first_key: accepted_first}
        assert receiver.pending == {second_key}
        assert receiver.reconciliation == {}

    # A snapshot can omit a withheld key. Moving the watermark must preserve
    # the receiver's unresolved disposition even without a row to reconsider.
    without_pending = replace(
        advanced,
        revisions=tuple(rev for rev in advanced.revisions if rev.key != second.key),
    )
    export_as_of(without_pending, card, gap)
    with Receiver(database, PROJECT) as receiver:
        receiver.import_snapshot(gap)
        assert receiver.watermark == advanced.sequence
        assert receiver.pending == {second_key}

    with Receiver(database, PROJECT) as receiver:
        conflicting = _changed_snapshot(
            original,
            tmp_path / "later-conflict",
            mutate_row=lambda rows: rows[0].update(client_version="unknown"),
            mutate_manifest=lambda manifest: manifest.update(
                cutoff=advanced.sequence + 1
            ),
        )
        with pytest.raises(ReceiverConflict, match="same source provenance"):
            receiver.import_snapshot(conflicting)
        assert receiver.watermark == advanced.sequence
        assert receiver.pending == {second_key}
        assert receiver.accepted == {first_key: accepted_first}

    final = replace(
        second,
        revision=2,
        record=replace(
            second.record,
            availability=Availability.COMPLETE,
            tokens=replace(second.record.tokens, output_tokens=200),
        ),
    )
    # A fixed view must still price an exact revision without a durable price row.
    project.apply(LedgerBatch((final,)))
    _correct(project, marker)
    after = project.as_of()
    corrected = tmp_path / "corrected"
    export_as_of(after, card, corrected)
    corrected_rows = {
        row["source"]: row
        for row in map(json.loads, _snapshot(corrected)[1].splitlines())
    }
    assert corrected_rows[first_key]["scope"]["item"] == {"kind": "issue", "id": 86}
    assert corrected_rows[first_key]["scope"]["revision"]["number"] == 2
    assert corrected_rows[second_key]["observation_revision"] == 2
    assert corrected_rows[second_key]["price"] == rows[first_key]["price"]
    with Receiver(database, PROJECT) as receiver:
        receiver.import_snapshot(corrected)
        assert receiver.accepted[first_key] == accepted_first
        assert second_key in receiver.accepted
        assert receiver.pending == set()
        assert receiver.reconciliation == {first_key: 1}
        assert receiver.watermark == after.sequence
        assert receiver.import_snapshot(gap) == "stale"
        assert receiver.reconciliation == {first_key: 1}

    repriced = tmp_path / "repriced"
    new_card = replace(
        card,
        version="2026-11-10",
        entries=tuple(
            replace(entry, output=Decimal("51"))
            if entry.model is ModelLabel.GPT_6_ASTRA
            else entry
            for entry in card.entries
        ),
    )
    export_as_of(after, new_card, repriced)
    assert _snapshot(corrected)[0] != _snapshot(repriced)[0]
    assert json.loads(_snapshot(repriced)[0])["rate_basis"] == new_card.basis.identifier
    assert {
        json.loads(line)["price"]["usd"] for line in _snapshot(repriced)[1].splitlines()
    } == {"0.0116"}
    with Receiver(database, PROJECT) as receiver:
        receiver.import_snapshot(repriced)
        assert receiver.accepted[first_key] == accepted_first
        assert receiver.reconciliation == {first_key: 2, second_key: 1}
        assert receiver.import_snapshot(corrected) == "duplicate"
        altered = _changed_snapshot(
            repriced,
            tmp_path / "conflict",
            mutate_row=lambda rows: rows[0]["tokens"].update(output_tokens=987),
        )
        with pytest.raises(ReceiverConflict):
            receiver.import_snapshot(altered)
        assert receiver.watermark == after.sequence
        assert receiver.accepted[first_key] == accepted_first
        assert receiver.reconciliation == {first_key: 2, second_key: 1}

    revised = replace(
        first, revision=2, record=replace(first.record, model=ModelLabel.UNKNOWN)
    )
    project.apply(LedgerBatch((revised,)))
    observation_revision = tmp_path / "observation-revision"
    export_as_of(project.as_of(), card, observation_revision)
    with Receiver(database, PROJECT) as receiver:
        receiver.import_snapshot(observation_revision)
        assert receiver.accepted[first_key] == accepted_first
        assert receiver.reconciliation == {first_key: 3, second_key: 1}
    with Receiver(database, PROJECT) as receiver:
        assert receiver.reconciliation == {first_key: 3, second_key: 1}
        assert receiver.accepted[first_key] == accepted_first
        assert receiver.watermark == project.as_of().sequence

    replay = tmp_path / "replay"
    assert export_as_of(project.as_of(before.sequence), card, replay) == receipt
    assert _snapshot(replay) == (original_manifest, original_data)
    assert export_as_of(before, card, original) == receipt


def test_export_allowlists_refs_and_gap_only_coverage(
    export_evidence, reference_rates, monkeypatch
):
    export_as_of = _export()
    from aitm_usage import export

    card = reference_rates
    project = export_evidence
    publish = Mock()
    monkeypatch.setattr(export, "_publish", publish)
    diagnostic = Diagnostic(
        DiagnosticCode.UNSUPPORTED_FORMAT,
        NOW,
        Provider.CLAUDE,
        _ref(project, "unparsed provider payload"),
        22,
    )
    gap_view = LedgerView(
        PROJECT, 1, (Revision(_ref(project, "diagnostic"), 1, diagnostic),), ()
    )
    gap = Path("/fixture/gap-only")
    export_as_of(gap_view, card, gap)
    published_path, files = publish.call_args.args
    assert published_path == gap
    manifest, data = files[export.MANIFEST_NAME], files[export.USAGE_NAME]
    assert data == b""
    assert json.loads(manifest)["coverage"] == {
        "complete": 0,
        "partial": 0,
        "unknown": 0,
    }
    assert json.loads(manifest)["diagnostics"] == [
        {"code": "unsupported-format", "count": 1, "provider": "claude"}
    ]
    assert diagnostic.source_ref.value.split(":")[-1].encode() not in manifest

    view, first, second, marker = _projected_view(project, card)
    unknown, _ = _observation(project, "unbound")
    unknown = replace(
        unknown, record=replace(unknown.record, model=f"{CANARY}:unknown-model")
    )
    malformed = replace(
        first, record=replace(first.record, availability=f"{CANARY}:payload")
    )
    writer = Mock(side_effect=AssertionError("malformed usage reached the writer"))
    monkeypatch.setattr(Ledger, "writer", writer)
    with pytest.raises(ValueError):
        project.apply(LedgerBatch((malformed,)))
    writer.assert_not_called()
    destination = Path("/fixture") / f"{CANARY}-export"
    view = replace(
        view, sequence=2, revisions=(*gap_view.revisions, *view.revisions, unknown)
    )
    export_as_of(view, card, destination)
    published_path, files = publish.call_args.args
    assert published_path == destination
    manifest, data = files[export.MANIFEST_NAME], files[export.USAGE_NAME]
    rows = {row["source"]: row for row in map(json.loads, data.splitlines())}
    assert rows[_public(first.key)]["scope"]["participant_ref"] == _public(
        marker.participant_ref
    )
    assert rows[_public(unknown.key)]["scope"] is None
    assert rows[_public(unknown.key)]["scope_availability"] == "unknown"
    assert rows[_public(unknown.key)]["price"]["usd"] is None
    assert rows[_public(unknown.key)]["model"] == "unknown"
    refs = (
        first.key,
        second.key,
        first.record.boundary.stream_ref,
        first.record.request_ref,
        marker.participant_ref,
        marker.attempt_ref,
    )
    for ref in refs:
        assert ref.value.split(":")[-1].encode() not in manifest + data
    assert CANARY.encode() not in manifest + data
    assert FIXTURE_KEY not in manifest + data
    assert FIXTURE_KEY.hex().encode() not in manifest + data

    _assert_receiver_refuses_snapshot(
        monkeypatch,
        files,
        match="Invalid usage export fields",
        mutate_row=lambda rows: rows[0].update(prompt=CANARY),
    )


def _invoke_installed_export(project, tmp_path, cutoff, rate, destination):
    runner = (
        "import runpy, sys; from pathlib import Path; from aitm_usage import ledger;"
        f"ledger._control_root = lambda: Path({str(tmp_path / 'control')!r});"
        "runpy.run_path(str(Path(sys.executable).with_name('aitm-usage')), run_name='__main__')"
    )
    return subprocess.run(
        [
            sys.executable,
            "-c",
            runner,
            "--project",
            str(project.root),
            "export",
            "--as-of",
            str(cutoff),
            "--rate-card",
            rate,
            "--output",
            str(destination),
            "--json",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_export_cli_reads_existing_project_without_writer_lease(
    export_evidence, reference_rates, monkeypatch, capsys
):
    from aitm_usage import cli, export

    project, card = export_evidence, reference_rates
    view, *_ = _projected_view(project, card)
    rows = _LedgerRows(project.identity, store.APPLICATION_ID, ())
    with rows.connect(write=True) as connection:
        connection.execute("INSERT INTO commits VALUES (?)", (view.sequence,))
        store._append_revisions(connection, view.sequence, view.revisions)
    writes = rows.writes.copy()
    opened = Mock(return_value=project)
    writer = Mock(side_effect=AssertionError("A read-only export acquired a writer"))
    monkeypatch.setattr(cli, "open_project", opened)
    monkeypatch.setattr(cli, "version", lambda _: "0.1.0")
    monkeypatch.setattr(cli, "load_rate_card", {card.version: card}.__getitem__)
    monkeypatch.setattr(Ledger, "writer", writer)
    monkeypatch.setattr(Ledger, "reader", lambda _: rows.connect(write=False))
    published = {}

    def publish(destination, files):
        assert published.setdefault(destination, files) == files

    monkeypatch.setattr(export, "_publish", publish)

    def invoke(cutoff, rate, destination):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "aitm-usage",
                "--project",
                str(project.root),
                "export",
                "--as-of",
                str(cutoff),
                "--rate-card",
                rate,
                "--output",
                str(destination),
                "--json",
            ],
        )
        return cli.main(), capsys.readouterr()

    cutoff = view.sequence
    output = Path("/fixture/cli-output")
    code, result = invoke(cutoff, card.basis.identifier, output)
    assert code == 0, result.err
    assert invoke(cutoff, card.version, output) == (0, result)
    for invalid_cutoff, invalid_rate in (
        (cutoff + 1, card.version),
        (cutoff, f"standard-api-USD:{card.version}:sha256:{CANARY}"),
    ):
        invalid_path = output.with_name(f"{CANARY}-invalid")
        code, rejected = invoke(invalid_cutoff, invalid_rate, invalid_path)
        assert code == 1
        assert not rejected.out and CANARY not in rejected.err
        assert invalid_path not in published
    receipt = json.loads(result.out)
    manifest = published[output][export.MANIFEST_NAME]
    assert receipt["cutoff"] == cutoff
    assert receipt["sha256"] == json.loads(manifest)["sha256"]
    assert CANARY not in result.out
    assert opened.call_args_list == [call(project.root)] * 3
    writer.assert_not_called()
    assert rows.writes == writes


@pytest.mark.parametrize(
    "kind", ["symlink", "parent-symlink", "traversal", "conflict", "hardlink"]
)
def test_refuses_unsafe_or_different_destination(
    request, monkeypatch, reference_rates, kind
):
    export_as_of = _export()
    from aitm_usage import export
    from aitm_usage.export import ExportError

    if kind == "traversal":
        inspect_destination = Mock(
            side_effect=AssertionError("unsafe filesystem access")
        )
        monkeypatch.setattr(export, "_validated_path", inspect_destination)
        with pytest.raises(ExportError, match="Invalid export snapshot or destination"):
            export_as_of(
                LedgerView(PROJECT, 0, (), ()),
                reference_rates,
                Path("/fixture/target/../destination"),
            )
        inspect_destination.assert_not_called()
        return

    if kind == "conflict":
        _assert_observed_destination_conflict(monkeypatch, reference_rates)
        return
    if kind == "parent-symlink":
        metadata = request.getfixturevalue("ledger_path_metadata")
        parent = metadata.base / "link"
        target = metadata.base / "target"
        metadata.add_directory(parent)
        metadata.replace_with_link(parent, target)
        assert parent.stat() == target.lstat()
        before = dict(metadata.entries)
        open_parent = Mock(side_effect=AssertionError("Linked export ancestor opened"))
        monkeypatch.setattr(export, "os", SimpleNamespace(open=open_parent))
        with pytest.raises(ExportError, match="Invalid export snapshot or destination"):
            export_as_of(
                LedgerView(PROJECT, 0, (), ()), reference_rates, parent / "child"
            )
        open_parent.assert_not_called()
        assert metadata.entries == before
        return

    if kind == "symlink":
        metadata = request.getfixturevalue("ledger_path_metadata")
        destination = metadata.base / "destination"
        target = metadata.base / "target"
        metadata.add_directory(destination)
        metadata.replace_with_link(destination, target)
        before = dict(metadata.entries)
        parent_info = destination.parent.lstat()
        open_parent = Mock(return_value=13)
        close_parent = Mock()
        stage = Mock(side_effect=AssertionError("Linked destination reached staging"))
        monkeypatch.setattr(
            export,
            "os",
            SimpleNamespace(
                O_RDONLY=os.O_RDONLY,
                O_DIRECTORY=os.O_DIRECTORY,
                O_NOFOLLOW=os.O_NOFOLLOW,
                open=open_parent,
                fstat=lambda fd: parent_info,
                stat=lambda name, *, dir_fd, follow_symlinks: destination.lstat(),
                close=close_parent,
            ),
        )
        monkeypatch.setattr(export, "_new_private_child", stage)
        with pytest.raises(ExportError, match="Invalid export snapshot or destination"):
            export_as_of(LedgerView(PROJECT, 0, (), ()), reference_rates, destination)
        stage.assert_not_called()
        close_parent.assert_called_once_with(13)
        assert metadata.entries == before
        return

    project = request.getfixturevalue("project")
    tmp_path = request.getfixturevalue("tmp_path")
    card = load_rate_card()
    target = tmp_path / "target"
    target.mkdir(mode=0o700)
    destination = tmp_path / "destination"
    export_as_of(project.as_of(), card, destination)
    os.link(destination / "usage.jsonl", tmp_path / "hardlinked")
    with pytest.raises(ExportError):
        export_as_of(project.as_of(), card, destination)

    linked = tmp_path / "linked-destination"
    linked.symlink_to(target, target_is_directory=True)
    with pytest.raises(ExportError):
        export_as_of(project.as_of(), card, linked)
    assert linked.is_symlink()
    assert list(target.iterdir()) == []
    assert not list(tmp_path.glob(".export-*"))


def _assert_observed_destination_conflict(monkeypatch, card, *, competing=False):
    from aitm_usage import export

    destination = Path("/fixture/export")
    ancestry = ((1, 1), (1, 2))
    pin = SimpleNamespace(identities=(*ancestry, (1, 3)), fd=13)
    contents = {} if competing else {"unrelated": CANARY.encode()}
    observed = Mock(return_value=ancestry)
    open_parent = Mock(return_value=9)
    stat_destination = Mock(return_value=object())
    sync = Mock(side_effect=AssertionError("A conflicting snapshot is not replayed"))
    stage = Mock(side_effect=AssertionError("A conflicting snapshot is not replaced"))
    remove = Mock(side_effect=AssertionError("An existing export must not be removed"))
    if competing:
        stat_destination.side_effect = FileNotFoundError
        stage, remove, publish = _observe_competing_publication(
            export, monkeypatch, destination, ancestry, contents
        )
    monkeypatch.setattr(export, "_validated_path", observed)
    monkeypatch.setattr(export, "_pin_directory", Mock(return_value=nullcontext(pin)))
    monkeypatch.setattr(export, "_new_private_child", stage)
    monkeypatch.setattr(
        export,
        "os",
        SimpleNamespace(
            O_RDONLY=os.O_RDONLY,
            O_DIRECTORY=os.O_DIRECTORY,
            O_NOFOLLOW=os.O_NOFOLLOW,
            open=open_parent,
            fstat=lambda fd: SimpleNamespace(st_dev=1, st_ino=2),
            stat=stat_destination,
            listdir=lambda fd: tuple(contents),
            fsync=sync,
            unlink=remove,
            close=Mock(),
        ),
    )
    with pytest.raises(export.ExportError, match="Conflicting export destination"):
        export.export_as_of(LedgerView(PROJECT, 0, (), ()), card, destination)
    open_parent.assert_called_once_with(
        destination.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    )
    stat_destination.assert_called_once_with(
        destination.name, dir_fd=9, follow_symlinks=False
    )
    export._pin_directory.assert_called_once_with(destination)
    if competing:
        publish.assert_called_once_with(15, "snapshot", 9, destination.name)
        assert stage.call_count == 2
        assert remove.call_args_list == [
            call("usage.jsonl", dir_fd=16),
            call("manifest.json", dir_fd=16),
        ]
    else:
        stage.assert_not_called()
        remove.assert_not_called()
    sync.assert_not_called()
    assert contents == {"unrelated": CANARY.encode()}


def _observe_competing_publication(
    export, monkeypatch, destination, ancestry, contents
):
    written = {}
    container = SimpleNamespace(fd=15, identities=(*ancestry, (1, 4)))
    staged = SimpleNamespace(fd=16, identities=(*container.identities, (1, 5)))

    @contextmanager
    def stage(parent_fd, path, identities):
        if parent_fd == 9:
            assert path.parent == destination.parent and path.name.startswith(
                ".export-"
            )
            assert identities == ancestry
            container.path = path
            pin = container
        else:
            assert parent_fd == container.fd and path == container.path / "snapshot"
            assert identities == container.identities
            pin = staged
        try:
            yield pin
        finally:
            assert not written

    def write(pin, files):
        assert pin is staged
        written.update(files)

    def compete(*_):
        assert written.keys() == {"usage.jsonl", "manifest.json"}
        assert not contents
        contents["unrelated"] = CANARY.encode()
        return False

    def unlink(name, *, dir_fd):
        assert dir_fd == staged.fd and name not in contents
        del written[name]

    publish = Mock(side_effect=compete)
    monkeypatch.setattr(export, "_write_snapshot", write)
    monkeypatch.setattr(export, "publish_noreplace", publish)
    return Mock(side_effect=stage), Mock(side_effect=unlink), publish


@pytest.mark.parametrize("identical", [False, True])
def test_competing_destination_keeps_complete_atomic_visibility(
    request, monkeypatch, reference_rates, identical
):
    if not identical:
        _assert_observed_destination_conflict(
            monkeypatch, reference_rates, competing=True
        )
        return

    project = request.getfixturevalue("project")
    tmp_path = request.getfixturevalue("tmp_path")
    export_as_of = _export()
    from aitm_usage import export

    destination = tmp_path / "destination"
    parent = tmp_path.stat()
    real_publish = export.publish_noreplace
    real_fsync = os.fsync
    parent_syncs = []

    def race(src_fd, source, dst_fd, target):
        assert not destination.exists()
        staged = os.open(
            source, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=src_fd
        )
        try:
            names = set(os.listdir(staged))
            assert names == {"manifest.json", "usage.jsonl"}
            assert stat.S_IMODE(os.fstat(staged).st_mode) == 0o700
            assert {
                stat.S_IMODE(os.stat(name, dir_fd=staged).st_mode) for name in names
            } == {0o600}
            destination.mkdir(mode=0o700)
            for name in names:
                with os.fdopen(
                    os.open(name, os.O_RDONLY, dir_fd=staged), "rb"
                ) as original:
                    copy = destination / name
                    copy.write_bytes(original.read())
                    copy.chmod(0o600)
        finally:
            os.close(staged)
        return real_publish(src_fd, source, dst_fd, target)

    def fsync(fd):
        if os.path.samestat(os.fstat(fd), parent):
            parent_syncs.append(fd)
        real_fsync(fd)

    monkeypatch.setattr(export, "publish_noreplace", race)
    monkeypatch.setattr(os, "fsync", fsync)
    view = project.as_of()
    card = load_rate_card()
    receipt = export_as_of(view, card, destination)
    assert receipt.sha256 == sha256(_snapshot(destination)[1]).hexdigest()
    assert len(parent_syncs) == 1
    assert not list(tmp_path.glob(".export-*"))


def test_replacing_outer_stage_during_rename_cannot_publish_substitute(
    project, tmp_path, monkeypatch
):
    export_as_of = _export()
    from aitm_usage import export

    view = project.as_of()
    card = load_rate_card()
    reference = tmp_path / "reference"
    receipt = export_as_of(view, card, reference)
    destination = tmp_path / "destination"
    displaced = tmp_path / "displaced-stage"
    real_publish = export.publish_noreplace

    def race(src_fd, source, dst_fd, target):
        (outer,) = tmp_path.glob(".export-*")
        outer.rename(displaced)
        outer.mkdir(mode=0o700)
        (outer / "competitor").write_text(CANARY)
        return real_publish(src_fd, source, dst_fd, target)

    monkeypatch.setattr(export, "publish_noreplace", race)
    try:
        result = export_as_of(view, card, destination)
    except export.ExportError:
        # Even a fail-closed publisher must not expose the replacement.
        assert not destination.exists() or {
            path.name for path in destination.iterdir()
        } == {
            "manifest.json",
            "usage.jsonl",
        }
        raise
    assert result == receipt
    assert _snapshot(destination) == _snapshot(reference)
    assert list(displaced.iterdir()) == []
    (replacement,) = tmp_path.glob(".export-*")
    assert (replacement / "competitor").read_text() == CANARY


@pytest.fixture
def rendered_snapshot(export_evidence, reference_rates):
    from aitm_usage import export

    view, _, _, _ = _projected_view(export_evidence, reference_rates)
    _, files = export._render(view, reference_rates)
    return files


def _assert_receiver_refuses_snapshot(
    monkeypatch, files, *, error=ValueError, match=None, **corruption
):
    from fixtures import receiver

    from aitm_usage import export

    directory = Path("/fixture/export")
    fixture_files = {directory / name: data for name, data in files.items()}
    monkeypatch.setattr(Path, "read_bytes", lambda path: fixture_files[path])
    manifest, rows = receiver._load_snapshot(directory, PROJECT)
    assert rows
    assert manifest["row_count"] == len(rows)
    manifest_path, data_path = (
        directory / export.MANIFEST_NAME,
        directory / export.USAGE_NAME,
    )
    fixture_files[manifest_path], fixture_files[data_path] = _changed_snapshot_bytes(
        fixture_files[manifest_path], fixture_files[data_path], **corruption
    )
    consumer = object.__new__(receiver.Receiver)
    consumer._project_id = PROJECT
    consumer._transaction = Mock(
        side_effect=AssertionError("invalid export reached storage")
    )
    with pytest.raises(error, match=match):
        consumer.import_snapshot(directory)
    consumer._transaction.assert_not_called()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema", "aitm.usage.export/v2"),
        ("project_id", str(UUID(int=92))),
        ("cutoff", True),
        ("rate_basis", CANARY),
        ("sha256", "0" * 64),
        ("diagnostics", [{"code": CANARY, "provider": "codex", "count": 1}]),
    ],
)
def test_receiver_refuses_invalid_manifest_before_writing(
    monkeypatch, rendered_snapshot, field, value
):
    def corrupt(manifest):
        manifest[field] = value

    _assert_receiver_refuses_snapshot(
        monkeypatch,
        rendered_snapshot,
        match="Invalid usage export digest" if field == "sha256" else None,
        mutate_manifest=corrupt,
    )


def test_receiver_refuses_duplicate_source_and_authenticated_tag(
    monkeypatch, rendered_snapshot, export_evidence
):
    from fixtures.receiver import ReceiverConflict

    first, _ = _observation(export_evidence, "first")
    _assert_receiver_refuses_snapshot(
        monkeypatch,
        rendered_snapshot,
        error=ReceiverConflict,
        match="Unordered or duplicate export source",
        mutate_row=lambda rows: rows.insert(0, rows[0]),
    )
    _assert_receiver_refuses_snapshot(
        monkeypatch,
        rendered_snapshot,
        match="Invalid usage export reference or decimal",
        mutate_row=lambda rows: rows[0].update(source=first.key.value),
    )


@pytest.mark.parametrize("field", ["observed_at", "draft_id"])
def test_receiver_rejects_non_string_datetime_and_draft_uuid(
    monkeypatch, rendered_snapshot, field
):
    def corrupt(rows):
        if field == "observed_at":
            rows[0]["observed_at"] = 123
        else:
            rows[0]["scope"]["item"] = {"kind": "draft", "id": 123}

    _assert_receiver_refuses_snapshot(
        monkeypatch,
        rendered_snapshot,
        match={
            "observed_at": "Invalid observation time",
            "draft_id": "Invalid draft UUID",
        }[field],
        mutate_row=corrupt,
    )


def test_exact_replay_resyncs_parent_after_interrupted_publication(
    monkeypatch, reference_rates
):
    from aitm_usage import export

    destination = Path("/fixture/destination")
    ancestry = ((1, 1), (1, 2))
    container = SimpleNamespace(fd=15, identities=(*ancestry, (1, 3)))
    staged = SimpleNamespace(fd=16, identities=(*container.identities, (1, 4)))
    existing = SimpleNamespace(identities=(*ancestry, (1, 4)), check=Mock())
    private_stages = []
    staged_files = {}
    published_files = {}

    @contextmanager
    def new_private_child(parent_fd, path, identities):
        if parent_fd == 9:
            assert path.parent == destination.parent and path.name.startswith(
                ".export-"
            )
            assert identities == ancestry
            container.path = path
            pin = container
        else:
            assert parent_fd == container.fd and path == container.path / "snapshot"
            assert identities == container.identities
            pin = staged
        private_stages.append(path)
        try:
            yield pin
        finally:
            assert private_stages.pop() == path

    def write_snapshot(pin, files):
        assert pin is staged
        staged_files.update(files)

    def publish(source_fd, source, target_fd, target):
        assert (source_fd, source, target_fd, target) == (
            container.fd,
            "snapshot",
            9,
            destination.name,
        )
        assert staged_files.keys() == {"manifest.json", "usage.jsonl"}
        published_files.update(staged_files)
        staged_files.clear()
        return True

    def stat_destination(name, *, dir_fd, follow_symlinks):
        assert (name, dir_fd, follow_symlinks) == (destination.name, 9, False)
        if not published_files:
            raise FileNotFoundError(name)
        return SimpleNamespace(st_dev=1, st_ino=4)

    def check_snapshot(pin, expected):
        assert pin is existing
        assert published_files == expected

    sync = Mock(
        side_effect=[None, OSError("initial sync"), OSError("retry sync"), None]
    )
    parent_open = Mock(return_value=9)
    parent_close = Mock()
    verify = Mock(side_effect=check_snapshot)
    publish_once = Mock(side_effect=publish)
    monkeypatch.setattr(export, "_validated_path", Mock(return_value=ancestry))
    monkeypatch.setattr(export, "_new_private_child", new_private_child)
    monkeypatch.setattr(export, "_write_snapshot", write_snapshot)
    monkeypatch.setattr(export, "publish_noreplace", publish_once)
    monkeypatch.setattr(
        export, "_pin_directory", Mock(return_value=nullcontext(existing))
    )
    monkeypatch.setattr(export, "_check_snapshot", verify)
    monkeypatch.setattr(
        export,
        "os",
        SimpleNamespace(
            O_RDONLY=os.O_RDONLY,
            O_DIRECTORY=os.O_DIRECTORY,
            O_NOFOLLOW=os.O_NOFOLLOW,
            open=parent_open,
            close=parent_close,
            fstat=lambda _: SimpleNamespace(st_dev=1, st_ino=2),
            stat=stat_destination,
            fsync=sync,
        ),
    )
    view = LedgerView(PROJECT, 0, (), ())
    with pytest.raises(
        export.ExportError, match="Invalid export snapshot or destination"
    ):
        export.export_as_of(view, reference_rates, destination)
    complete = published_files.copy()
    assert not private_stages and not staged_files
    with pytest.raises(
        export.ExportError, match="Invalid export snapshot or destination"
    ):
        export.export_as_of(view, reference_rates, destination)
    receipt = export.export_as_of(view, reference_rates, destination)

    assert sync.call_args_list == [call(container.fd), call(9), call(9), call(9)]
    assert verify.call_args_list == [call(existing, complete), call(existing, complete)]
    existing.check.assert_called_once_with()
    publish_once.assert_called_once()
    assert parent_close.call_args_list == [call(9)] * 3
    assert published_files == complete
    assert receipt.sha256 == sha256(complete["usage.jsonl"]).hexdigest()


@pytest.mark.parametrize(
    "kind", ["accepted-observation", "pending-observation", "scope", "price"]
)
def test_receiver_rejects_component_conflict_under_changed_provenance(
    export_evidence, reference_rates, kind
):
    _assert_component_conflict(export_evidence, reference_rates, kind)


def _assert_component_conflict(project, card, kind):
    from fixtures.receiver import Receiver, ReceiverConflict

    from aitm_usage import export

    before, first, second, marker = _projected_view(project, card)
    enrollment = next(
        rev
        for rev in before.current
        if isinstance(rev.record, ScopeEnrollment) and rev.record.marker == marker
    )
    corrected = replace(
        enrollment,
        revision=2,
        record=replace(
            enrollment.record, marker=replace(marker, item=ItemKey(ItemKind.ISSUE, 86))
        ),
    )
    after = replace(before, sequence=2, revisions=(*before.revisions, corrected))
    selected = card if kind == "price" else replace(card, version="2026-11-10")
    pending_observation = kind == "pending-observation"
    source = _public(
        second.key if kind in {"scope", "pending-observation"} else first.key
    )

    def render_row(view, rates):
        _, files = export._render(view, rates)
        rows = map(json.loads, files[export.USAGE_NAME].splitlines())
        return next(row for row in rows if row["source"] == source)

    original = render_row(before, card)
    candidate = render_row(after, selected)
    altered = json.loads(_canonical(candidate))
    component = kind
    if kind == "scope":
        assert candidate["price"]["rate_basis"] != original["price"]["rate_basis"]
        altered["scope"]["item"]["id"] = 123
    elif kind == "price":
        assert candidate["scope"]["revision"]["number"] == 2
        altered["price"]["usd"] = "0.5"
    else:
        assert candidate["price"]["rate_basis"] != original["price"]["rate_basis"]
        altered["tokens"]["input_tokens"] = 501
        component = "observation"

    components = {}
    pending = {}

    def execute(statement, values):
        if statement.startswith("SELECT payload FROM component"):
            payload = components.get(values)
            return Mock(fetchone=lambda: (payload,) if payload is not None else None)
        if statement == "SELECT digest FROM accepted WHERE source = ?":
            assert pending_observation and values == (source,)
            return Mock(fetchone=lambda: None)
        if statement.startswith("INSERT INTO pending VALUES"):
            pending_source, digest, payload = values
            assert pending_observation and pending_source == source
            pending[source] = (digest, payload)
            return None
        assert statement.startswith("INSERT INTO component")
        key = values[:2]
        assert key not in components
        components[key] = values[2]

    # The receiver owns provenance keys and comparisons. This double stores
    # the component and pending rows that those methods read and insert.
    receiver = object.__new__(Receiver)
    receiver._db = Mock(execute=execute)

    def consider(row):
        receiver._consider(row, _canonical(row))

    store = consider if pending_observation else receiver._remember_components
    store(original)
    baseline = components.copy()
    initial_pending = pending.copy()
    with pytest.raises(ReceiverConflict, match=rf"source provenance \({component}\)"):
        store(altered)
    assert pending == initial_pending
    if pending_observation:
        assert components == baseline
        assert initial_pending[source][1] == _canonical(original)
    components = baseline
    store(candidate)
    if pending_observation:
        payload = _canonical(candidate)
        assert pending == {source: (sha256(payload).hexdigest(), payload)}


class _ReceiverHistory:
    """Store the observed receiver rows independently of the reader lifetime."""

    def __init__(self):
        self.watermark = None
        self.snapshots = {}
        self.components = {}
        self.accepted = {}
        self.pending = {}
        self.reconciliation = {}

    @contextmanager
    def transaction(self):
        before = {
            name: value.copy() if isinstance(value, dict) else value
            for name, value in vars(self).items()
        }
        try:
            yield
        except Exception:
            vars(self).update(before)
            raise

    def execute(self, statement, values=()):
        sql = " ".join(statement.split())
        row = None
        if sql == "SELECT watermark FROM meta":
            row = (self.watermark,)
        elif sql == "SELECT source, digest FROM accepted":
            return tuple((key, data[0]) for key, data in self.accepted.items())
        elif sql == "SELECT source, COUNT(*) FROM reconciliation GROUP BY source":
            return tuple(Counter(key for key, _ in self.reconciliation).items())
        elif (
            sql
            == "SELECT basis, digest, projection_digest FROM snapshot WHERE cutoff = ?"
        ):
            return tuple(
                (basis, *data)
                for (cutoff, basis), data in self.snapshots.items()
                if (cutoff,) == values
            )
        elif sql == "SELECT payload FROM component WHERE kind = ? AND identity = ?":
            if values in self.components:
                row = (self.components[values],)
        elif sql == "SELECT digest FROM accepted WHERE source = ?":
            (key,) = values
            if key in self.accepted:
                row = (self.accepted[key][0],)
        elif sql == "INSERT INTO component VALUES(?, ?, ?)":
            kind, identity, payload = values
            self.components[kind, identity] = payload
        elif sql == "INSERT OR IGNORE INTO accepted VALUES(?, ?, ?)":
            key, digest, payload = values
            assert key not in self.accepted
            self.accepted[key] = (digest, payload)
            return SimpleNamespace(rowcount=1)
        elif sql.startswith("INSERT INTO pending VALUES(?, ?, ?) ON CONFLICT(source)"):
            key, digest, payload = values
            self.pending[key] = (digest, payload)
        elif sql == "DELETE FROM pending WHERE source = ?":
            self.pending.pop(values[0], None)
        elif sql == "INSERT OR IGNORE INTO reconciliation VALUES(?, ?, ?)":
            key, digest, payload = values
            self.reconciliation.setdefault((key, digest), payload)
        elif sql == "INSERT INTO snapshot VALUES(?, ?, ?, ?)":
            cutoff, basis, digest, projection = values
            self.snapshots[cutoff, basis] = (digest, projection)
        else:
            assert sql == "UPDATE meta SET watermark = ?", sql
            (self.watermark,) = values
        return SimpleNamespace(fetchone=lambda: row)


def test_receiver_checks_reconciled_observation_after_reopen(
    export_evidence, reference_rates, monkeypatch
):
    from fixtures.receiver import Receiver, ReceiverConflict

    from aitm_usage import export

    project, card = export_evidence, reference_rates
    initial, first, *_ = _projected_view(project, card)
    files = {}

    def render(name, view, rates):
        directory = Path("/fixture") / name
        _, raw = export._render(view, rates)
        files.update({directory / name: data for name, data in raw.items()})
        return directory

    monkeypatch.setattr(Path, "read_bytes", lambda path: files[path])
    original = render("original", initial, card)
    newer = replace(
        first,
        revision=2,
        record=replace(first.record, client_version=ClientVersion.UNKNOWN),
    )
    view = replace(initial, sequence=2, revisions=(*initial.revisions, newer))
    revision = render("revision", view, card)
    history = _ReceiverHistory()

    def reopen():
        receiver = object.__new__(Receiver)
        receiver._project_id = PROJECT
        receiver._db = history
        receiver._transaction = history.transaction
        return receiver

    receiver = reopen()
    assert receiver.import_snapshot(original) == "imported"
    assert receiver.import_snapshot(revision) == "imported"
    accepted = receiver.accepted
    assert receiver.reconciliation == {_public(first.key): 1}

    new_card = replace(card, version="2026-11-10")
    repriced = render("repriced", view, new_card)

    def contradict(rows):
        row = next(item for item in rows if item["source"] == _public(first.key))
        row["tokens"]["input_tokens"] = 501

    # A later cutoff and a new card do not erase the remembered revision.
    altered = Path("/fixture/altered")
    manifest, data = _changed_snapshot_bytes(
        *_snapshot(repriced),
        mutate_row=contradict,
        mutate_manifest=lambda manifest: manifest.update(cutoff=view.sequence + 1),
    )
    files[altered / export.MANIFEST_NAME] = manifest
    files[altered / export.USAGE_NAME] = data
    reopened = reopen()
    with pytest.raises(ReceiverConflict, match=r"source provenance \(observation\)"):
        reopened.import_snapshot(altered)
    assert reopened.watermark == view.sequence
    assert reopened.accepted == accepted
    assert reopened.reconciliation == {_public(first.key): 1}
    assert reopened.import_snapshot(repriced) == "imported"
