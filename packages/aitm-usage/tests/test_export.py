import json
import os
import stat
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime
from decimal import Decimal
from hashlib import sha256
from uuid import UUID

import pytest

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
    manifest, data = _snapshot(original)
    manifest = json.loads(manifest)
    if mutate_row is not None:
        rows = [json.loads(line) for line in data.splitlines()]
        mutate_row(rows)
        data = b"".join(_canonical(row) + b"\n" for row in rows)
    manifest["sha256"] = sha256(data).hexdigest()
    if mutate_manifest is not None:
        mutate_manifest(manifest)
    destination.mkdir()
    (destination / "manifest.json").write_bytes(_canonical(manifest) + b"\n")
    (destination / "usage.jsonl").write_bytes(data)
    return destination


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
    receipt = export_as_of(before, card, original)
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
    with Receiver(database, PROJECT) as receiver:
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

    replay = tmp_path / "replay"
    assert export_as_of(project.as_of(before.sequence), card, replay) == receipt
    assert _snapshot(replay) == (original_manifest, original_data)
    assert export_as_of(before, card, original) == receipt


def test_export_allowlists_refs_and_gap_only_coverage(project, tmp_path):
    export_as_of = _export()
    assert project.as_of().sequence == 0
    diagnostic = Diagnostic(
        DiagnosticCode.UNSUPPORTED_FORMAT,
        NOW,
        Provider.CLAUDE,
        _ref(project, "unparsed provider payload"),
        22,
    )
    project.apply(LedgerBatch((Revision(_ref(project, "diagnostic"), 1, diagnostic),)))
    gap = tmp_path / "gap-only"
    card = load_rate_card()
    export_as_of(project.as_of(), card, gap)
    manifest, data = _snapshot(gap)
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

    first, second, marker = _seed(project)
    unknown, _ = _observation(project, "unbound")
    unknown = replace(
        unknown, record=replace(unknown.record, model=f"{CANARY}:unknown-model")
    )
    project.apply(LedgerBatch((unknown,)))
    malformed = replace(
        first, record=replace(first.record, availability=f"{CANARY}:payload")
    )
    with pytest.raises(ValueError):
        project.apply(LedgerBatch((malformed,)))
    destination = tmp_path / f"{CANARY}-export"
    view = project.as_of()
    export_as_of(view, card, destination)
    manifest, data = _snapshot(destination)
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
    key_bytes = project.key_path.read_bytes()
    assert key_bytes not in manifest + data
    assert key_bytes.hex().encode() not in manifest + data

    from fixtures.receiver import Receiver

    invalid = _changed_snapshot(
        destination,
        tmp_path / "invalid",
        mutate_row=lambda rows: rows[0].update(prompt=CANARY),
    )
    with Receiver(tmp_path / "privacy.sqlite", PROJECT) as receiver:
        with pytest.raises(ValueError):
            receiver.import_snapshot(invalid)
        assert receiver.watermark is None
        assert receiver.accepted == {}


def test_export_cli_reads_existing_project_without_writer_lease(project, tmp_path):
    _seed(project)
    output = tmp_path / "cli-output"
    card = load_rate_card()
    runner = (
        "import runpy, sys; from pathlib import Path; from aitm_usage import ledger;"
        f"ledger._control_root = lambda: Path({str(tmp_path / 'control')!r});"
        "runpy.run_path(str(Path(sys.executable).with_name('aitm-usage')), run_name='__main__')"
    )

    def invoke(cutoff, rate, destination):
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

    with project.writer() as writer:
        cutoff = writer.as_of().sequence
        result = invoke(cutoff, card.basis.identifier, output)
        assert result.returncode == 0, result.stderr
        assert invoke(cutoff, card.version, output).stdout == result.stdout
        assert writer.as_of().sequence == cutoff
        for invalid_cutoff, invalid_rate in (
            (cutoff + 1, card.version),
            (cutoff, f"standard-api-USD:{card.version}:sha256:{CANARY}"),
        ):
            invalid_path = tmp_path / f"{CANARY}-invalid"
            rejected = invoke(invalid_cutoff, invalid_rate, invalid_path)
            assert rejected.returncode == 1
            assert not rejected.stdout and CANARY not in rejected.stderr
            assert not invalid_path.exists()
    receipt = json.loads(result.stdout)
    manifest, _ = _snapshot(output)
    assert receipt["cutoff"] == cutoff
    assert receipt["sha256"] == json.loads(manifest)["sha256"]
    assert CANARY not in result.stdout


@pytest.mark.parametrize(
    "kind", ["symlink", "parent-symlink", "traversal", "conflict", "hardlink"]
)
def test_refuses_unsafe_or_different_destination(project, tmp_path, kind):
    export_as_of = _export()
    from aitm_usage.export import ExportError

    card = load_rate_card()
    target = tmp_path / "target"
    target.mkdir(mode=0o700)
    destination = tmp_path / "destination"
    if kind == "symlink":
        destination.symlink_to(target, target_is_directory=True)
    elif kind == "parent-symlink":
        destination.symlink_to(target, target_is_directory=True)
        destination = destination / "child"
    elif kind == "traversal":
        destination = target / ".." / "destination"
    elif kind == "hardlink":
        export_as_of(project.as_of(), card, destination)
        os.link(destination / "usage.jsonl", tmp_path / "hardlinked")
    else:
        destination.mkdir(mode=0o700)
        (destination / "unrelated").write_text(CANARY)

    with pytest.raises(ExportError):
        export_as_of(project.as_of(), card, destination)
    assert list(target.iterdir()) == []
    assert not list(tmp_path.glob(".export-*"))
    if kind == "conflict":
        assert (destination / "unrelated").read_text() == CANARY


@pytest.mark.parametrize("identical", [False, True])
def test_competing_destination_keeps_complete_atomic_visibility(
    project, tmp_path, monkeypatch, identical
):
    export_as_of = _export()
    from aitm_usage import export

    destination = tmp_path / "destination"
    parent = tmp_path.stat()
    real_rename = export._rename_exclusive()
    real_fsync = os.fsync
    parent_syncs = []

    def race(src_fd, source, dst_fd, target, flags):
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
            if identical:
                for name in names:
                    with os.fdopen(
                        os.open(name, os.O_RDONLY, dir_fd=staged), "rb"
                    ) as original:
                        copy = destination / name
                        copy.write_bytes(original.read())
                        copy.chmod(0o600)
            else:
                (destination / "competitor").write_text(CANARY)
        finally:
            os.close(staged)
        return real_rename(src_fd, source, dst_fd, target, flags)

    def fsync(fd):
        if os.path.samestat(os.fstat(fd), parent):
            parent_syncs.append(fd)
        real_fsync(fd)

    monkeypatch.setattr(export, "_rename_exclusive", lambda: race)
    monkeypatch.setattr(os, "fsync", fsync)
    view = project.as_of()
    card = load_rate_card()
    if identical:
        receipt = export_as_of(view, card, destination)
        assert receipt.sha256 == sha256(_snapshot(destination)[1]).hexdigest()
        assert len(parent_syncs) == 1
    else:
        with pytest.raises(export.ExportError):
            export_as_of(view, card, destination)
        assert (destination / "competitor").read_text() == CANARY
        assert {path.name for path in destination.iterdir()} == {"competitor"}
        assert parent_syncs == []
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
    real_rename = export._rename_exclusive()

    def race(src_fd, source, dst_fd, target, flags):
        (outer,) = tmp_path.glob(".export-*")
        outer.rename(displaced)
        outer.mkdir(mode=0o700)
        (outer / "competitor").write_text(CANARY)
        return real_rename(src_fd, source, dst_fd, target, flags)

    monkeypatch.setattr(export, "_rename_exclusive", lambda: race)
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
    project, tmp_path, field, value
):
    export_as_of = _export()
    from fixtures.receiver import Receiver

    _seed(project)
    original = tmp_path / "original"
    export_as_of(project.as_of(), load_rate_card(), original)
    invalid = _changed_snapshot(
        original,
        tmp_path / "invalid",
        mutate_manifest=lambda manifest: manifest.update({field: value}),
    )
    with Receiver(tmp_path / "receiver.sqlite", PROJECT) as receiver:
        with pytest.raises(ValueError):
            receiver.import_snapshot(invalid)
        assert receiver.watermark is None
        assert receiver.accepted == {}
        assert receiver.pending == set()


def test_receiver_refuses_duplicate_source_and_authenticated_tag(project, tmp_path):
    export_as_of = _export()
    from fixtures.receiver import Receiver, ReceiverConflict

    first, _, _ = _seed(project)
    original = tmp_path / "original"
    export_as_of(project.as_of(), load_rate_card(), original)
    duplicate = _changed_snapshot(
        original,
        tmp_path / "duplicate",
        mutate_row=lambda rows: rows.insert(0, rows[0]),
    )
    authenticated = _changed_snapshot(
        original,
        tmp_path / "authenticated",
        mutate_row=lambda rows: rows[0].update(source=first.key.value),
    )
    with Receiver(tmp_path / "receiver.sqlite", PROJECT) as receiver:
        with pytest.raises(ReceiverConflict):
            receiver.import_snapshot(duplicate)
        with pytest.raises(ValueError):
            receiver.import_snapshot(authenticated)
        assert receiver.watermark is None
        assert receiver.accepted == {}


@pytest.mark.parametrize("field", ["observed_at", "draft_id"])
def test_receiver_rejects_non_string_datetime_and_draft_uuid(project, tmp_path, field):
    export_as_of = _export()
    from fixtures.receiver import Receiver

    _seed(project)
    original = tmp_path / "original"
    export_as_of(project.as_of(), load_rate_card(), original)

    def corrupt(rows):
        if field == "observed_at":
            rows[0]["observed_at"] = 123
        else:
            rows[0]["scope"]["item"] = {"kind": "draft", "id": 123}

    invalid = _changed_snapshot(original, tmp_path / "invalid", mutate_row=corrupt)
    with Receiver(tmp_path / "receiver.sqlite", PROJECT) as receiver:
        with pytest.raises(ValueError):
            receiver.import_snapshot(invalid)
        assert receiver.watermark is None
        assert receiver.accepted == {}


def test_exact_replay_resyncs_parent_after_interrupted_publication(
    project, tmp_path, monkeypatch
):
    export_as_of = _export()
    from aitm_usage.export import ExportError

    view = project.as_of()
    card = load_rate_card()
    destination = tmp_path / "destination"
    parent = tmp_path.stat()
    real_fsync = os.fsync
    parent_syncs = []

    def fsync(fd):
        if os.path.samestat(os.fstat(fd), parent):
            parent_syncs.append(fd)
            if len(parent_syncs) <= 2:
                raise OSError(5, "simulated parent sync failure")
        real_fsync(fd)

    monkeypatch.setattr(os, "fsync", fsync)
    with pytest.raises(ExportError):
        export_as_of(view, card, destination)
    complete = _snapshot(destination)
    # An exact retry must repeat the failed durability step before success.
    with pytest.raises(ExportError):
        export_as_of(view, card, destination)
    receipt = export_as_of(view, card, destination)
    assert len(parent_syncs) == 3
    assert _snapshot(destination) == complete
    assert receipt.sha256 == sha256(complete[1]).hexdigest()
    assert not list(tmp_path.glob(".export-*"))


@pytest.mark.parametrize(
    "kind", ["accepted-observation", "pending-observation", "scope", "price"]
)
def test_receiver_rejects_component_conflict_under_changed_provenance(
    project, tmp_path, kind
):
    export_as_of = _export()
    from fixtures.receiver import Receiver, ReceiverConflict

    first, second, marker = _seed(project)
    before = project.as_of()
    card = load_rate_card()
    original = tmp_path / "original"
    export_as_of(before, card, original)
    _correct(project, marker)
    after = project.as_of()
    # New scope provenance accompanies the price contradiction. New rate
    # provenance accompanies the unchanged observation and scope revisions.
    selected = card if kind == "price" else replace(card, version="2026-11-10")
    candidate = tmp_path / "candidate"
    export_as_of(after, selected, candidate)

    def contradict(rows):
        key = _public(
            second.key if kind in {"pending-observation", "scope"} else first.key
        )
        row = next(item for item in rows if item["source"] == key)
        if kind == "scope":
            row["scope"]["item"]["id"] = 123
        elif kind == "price":
            row["price"]["usd"] = "0.5"
        else:
            row["tokens"]["input_tokens"] = 501

    altered = _changed_snapshot(candidate, tmp_path / "altered", mutate_row=contradict)
    with Receiver(tmp_path / "receiver.sqlite", PROJECT) as receiver:
        assert receiver.import_snapshot(original) == "imported"
        accepted = receiver.accepted
        with pytest.raises(ReceiverConflict):
            receiver.import_snapshot(altered)
        assert receiver.watermark == before.sequence
        assert receiver.accepted == accepted
        assert receiver.pending == {_public(second.key)}
        assert receiver.reconciliation == {}
        assert receiver.import_snapshot(candidate) == "imported"


def test_receiver_checks_reconciled_observation_after_reopen(project, tmp_path):
    export_as_of = _export()
    from fixtures.receiver import Receiver, ReceiverConflict

    first, _, _ = _seed(project)
    card = load_rate_card()
    original = tmp_path / "original"
    export_as_of(project.as_of(), card, original)
    newer = replace(
        first,
        revision=2,
        record=replace(first.record, client_version=ClientVersion.UNKNOWN),
    )
    project.apply(LedgerBatch((newer,)))
    view = project.as_of()
    revision = tmp_path / "revision"
    export_as_of(view, card, revision)
    database = tmp_path / "receiver.sqlite"
    with Receiver(database, PROJECT) as receiver:
        receiver.import_snapshot(original)
        receiver.import_snapshot(revision)
        accepted = receiver.accepted
        assert receiver.reconciliation == {_public(first.key): 1}

    new_card = replace(card, version="2026-11-10")
    repriced = tmp_path / "repriced"
    export_as_of(view, new_card, repriced)

    def contradict(rows):
        row = next(item for item in rows if item["source"] == _public(first.key))
        row["tokens"]["input_tokens"] = 501

    # A later cutoff and a new card do not erase the remembered revision.
    altered = _changed_snapshot(
        repriced,
        tmp_path / "altered",
        mutate_row=contradict,
        mutate_manifest=lambda manifest: manifest.update(cutoff=view.sequence + 1),
    )
    with Receiver(database, PROJECT) as receiver:
        with pytest.raises(
            ReceiverConflict, match=r"source provenance \(observation\)"
        ):
            receiver.import_snapshot(altered)
        assert receiver.watermark == view.sequence
        assert receiver.accepted == accepted
        assert receiver.reconciliation == {_public(first.key): 1}
        assert receiver.import_snapshot(repriced) == "imported"
