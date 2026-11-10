import json
import sqlite3
import sys
from contextlib import closing
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

import pytest

from aitm_usage import backup, cli, install, ledger, service
from aitm_usage.export import export_as_of
from aitm_usage.pricing import load_rate_card
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    LedgerBatch,
    ModelLabel,
    Provider,
    Revision,
    SourceBoundary,
    TokenCounts,
    UsageObservation,
    _encode,
)

PROJECT = UUID(int=113)
LEGACY_FINGERPRINT = "3ee836684b5f5ca48469f3abde2779cd317c58df883f8520a8fb3c64dbcfdfe2"
MOMENT = datetime(2026, 11, 9, 17, tzinfo=UTC)


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(ledger, "_control_root", lambda: tmp_path / "control")
    checkout, sources = tmp_path / "checkout", tmp_path / "sources"
    checkout.mkdir(mode=0o700)
    sources.mkdir(mode=0o700)
    config = tmp_path / "configuration.json"
    config.write_text(
        json.dumps(
            {
                "project_id": str(PROJECT),
                "source_roots": [str(sources)],
                "checkout_anchors": [str(checkout)],
                "cutoff": "2026-11-09T16:00:00Z",
            }
        )
    )
    root = tmp_path / "project"
    service.register_project(root, config)
    store = ledger.Ledger.open(root, PROJECT)

    def ref(name):
        return store.pseudonymize("fixture", name)

    boundary = SourceBoundary(
        Provider.CODEX,
        ref("stream"),
        ref("session"),
        1,
        BoundaryKind.REQUEST,
        ref("boundary"),
    )
    observation = UsageObservation(
        boundary,
        MOMENT,
        ClientVersion.CODEX_0_167_0_ALPHA_3_2,
        1,
        TokenCounts(input_tokens=20, output_tokens=2, total_tokens=22),
        Availability.COMPLETE,
        request_ref=ref("request"),
        model=ModelLabel.GPT_6_1_SOL,
    )
    store.apply(LedgerBatch((Revision(ref("usage"), 1, observation),)))
    return store


def _durable_bytes(project):
    return tuple(
        path.read_bytes()
        for path in (
            project.database_path,
            project.database_path.with_suffix(".sqlite3-wal"),
            project.key_path,
        )
    )


def test_schema_upgrade_preserves_legacy_identity_and_export_bytes(project, tmp_path):
    before = project.as_of()
    key = project.key_path.read_bytes()
    legacy_export = tmp_path / "legacy"
    card = load_rate_card()
    expected_receipt = export_as_of(before, card, legacy_export)
    upgraded = project.upgrade_monitor_schema(before.sequence)
    from aitm_usage.monitor_types import (
        MonitorModel,
        MonitorObservation,
        MonitorProvider,
        MonitorRevision,
        NativeSurface,
        ObservationTimeBasis,
        ProviderCostEvidence,
    )

    store = ledger.Ledger.open(project.root, PROJECT)
    assert store.identity == upgraded
    assert (upgraded.project_id, upgraded.key_id, upgraded.schema_version) == (
        PROJECT,
        project.identity.key_id,
        2,
    )
    assert store.key_path.read_bytes() == key
    assert store.as_of() == before
    assert store.upgrade_monitor_schema(before.sequence) == upgraded
    with pytest.raises(ledger.LedgerError):
        project.as_of()
    frozen = store.monitor_as_of(before.sequence)
    assert frozen.legacy == before
    assert frozen.revisions == ()
    record = MonitorRevision(
        key=store.pseudonymize("fixture", "monitor-usage"),
        revision=1,
        observation=MonitorObservation(
            provider=MonitorProvider.CODEX,
            native_surface=NativeSurface.CODEX_DESKTOP_MACOS,
            observed_at=MOMENT,
            time_basis=ObservationTimeBasis.NATIVE_COMPLETION,
            tokens=TokenCounts(input_tokens=12, output_tokens=3, total_tokens=15),
            coverage=Availability.COMPLETE,
            model=MonitorModel.GPT_6_1_SOL,
            provider_cost=ProviderCostEvidence(ticks=7),
        ),
    )
    sequence = before.sequence + 1
    with store.writer() as writer, writer._write_transaction() as conn:
        conn.execute("INSERT INTO commits VALUES (?)", (sequence,))
        conn.execute(
            "INSERT INTO monitor_revisions VALUES (?, ?, ?, ?)",
            (
                record.key.value,
                record.revision,
                sequence,
                _encode(record, MonitorRevision),
            ),
        )
    assert store.monitor_as_of(before.sequence) == frozen
    assert store.monitor_as_of(sequence).revisions == (record,)
    after = tmp_path / "after"
    assert export_as_of(store.as_of(before.sequence), card, after) == expected_receipt
    assert {p.name: p.read_bytes() for p in after.iterdir()} == {
        p.name: p.read_bytes() for p in legacy_export.iterdir()
    }
    target = tmp_path / "v2-backup"
    receipt = backup.backup(store, target)
    assert backup.verify_backup(target, store) == receipt
    assert json.loads((target / "manifest.json").read_bytes())["format"] == (
        "aitm-usage.backup/v2"
    )


def test_old_binary_refuses_monitor_schema(project):
    # Frozen v1 admission branch. The delivery rehearsal also runs the exact v1 wheel.
    def legacy_admission():
        with closing(
            sqlite3.connect(f"{project.database_path.as_uri()}?mode=ro", uri=True)
        ) as conn:
            if conn.execute("PRAGMA user_version").fetchone() != (1,):
                raise ledger.LedgerError("Unsupported ledger schema")

    legacy_admission()
    project.upgrade_monitor_schema(project.as_of().sequence)
    before = _durable_bytes(project)
    with pytest.raises(ledger.LedgerError, match="Unsupported ledger schema"):
        legacy_admission()
    assert _durable_bytes(project) == before


def test_mixed_or_interrupted_upgrade_rolls_back(project, monkeypatch, tmp_path):
    view = project.as_of()
    with pytest.raises(ledger.ConflictError):
        project.upgrade_monitor_schema(view.sequence - 1)
    assert project.as_of() == view
    original = ledger._validate_identity

    def interrupted(conn, identity):
        original(conn, identity)
        if identity.schema_version == 2:
            assert conn.execute(
                "SELECT name FROM sqlite_schema WHERE name = 'monitor_revisions'"
            ).fetchone() == ("monitor_revisions",)
            raise ledger.LedgerError("simulated interruption")

    with monkeypatch.context() as patch:
        patch.setattr(ledger, "_validate_identity", interrupted)
        with pytest.raises(ledger.LedgerError, match="simulated interruption"):
            project.upgrade_monitor_schema(view.sequence)
    assert project.as_of() == view
    assert ledger.Ledger.open(project.root, PROJECT).identity == project.identity
    old_bundle = tmp_path / "old-bundle"
    backup.backup(project, old_bundle)
    project.upgrade_monitor_schema(view.sequence)
    migrated = ledger.Ledger.open(project.root, PROJECT)
    with pytest.raises(backup.BackupError):
        backup.verify_backup(old_bundle, migrated)


@pytest.mark.parametrize("version", [1, 2])
def test_schema_tag_requires_its_exact_tables(project, version):
    if version == 1:
        statement = "CREATE TABLE monitor_revisions (payload TEXT)"
    else:
        statement = "PRAGMA user_version = 2"
    with project.writer() as writer, writer._write_transaction() as conn:
        conn.execute(statement)
    with pytest.raises(ledger.LedgerError):
        ledger.Ledger.open(project.root, PROJECT)


def test_new_runtime_accepts_unmodified_legacy_store_backup_and_installer_probe(
    project, tmp_path, monkeypatch
):
    old_view = project.as_of()
    saved = tmp_path / "backup"
    receipt = backup.backup(project, saved)
    assert receipt.schema_version == 1
    assert backup.verify_backup(saved, project) == receipt
    assert json.loads((saved / "manifest.json").read_bytes())["format"] == (
        "aitm-usage.backup/v1"
    )
    assert ledger.Ledger.open(project.root, PROJECT).as_of() == old_view

    executable = tmp_path / "aitm-usage"
    observed = {
        "version": "0.1.0",
        "interpreter_version": "3.13.9",
        "interpreter": str(executable.with_name("python")),
        "packages": ["aitm-usage"],
        "schema": [1095324757, 1, LEGACY_FINGERPRINT],
        "entry_points": [["console_scripts", "aitm-usage", "aitm_usage.cli:main"]],
        "witness_capable": True,
    }
    monkeypatch.setattr(install, "_inspect_surface", lambda *args: tmp_path)
    monkeypatch.setattr(install, "_run_python", lambda *args: json.dumps(observed))
    monkeypatch.setattr(
        install.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout="aitm-usage 0.1.0\n"
        ),
    )
    wheel = install._Wheel("0.1.0", "1" * 64, b"", {})
    args = (executable, tmp_path / "python3", "3.13.9", wheel)
    assert install._probe_runtime(*args, schema_version=1).witness_capable
    with pytest.raises(install.InstallError):
        install._probe_runtime(*args, schema_version=2)
    observed["schema"][1] = True
    with pytest.raises(install.InstallError):
        install._probe_runtime(*args, schema_version=1)
    observed["schema"][1:] = [1, "0" * 64]
    with pytest.raises(install.InstallError):
        install._probe_runtime(*args, schema_version=1)


def test_legacy_global_state_and_report_project_uuid_are_separate(
    project, monkeypatch, capsys
):
    monkeypatch.setattr(
        sys, "argv", ["aitm-usage", "--project", str(project.root), "status", "--json"]
    )
    assert cli.main() == 0
    assert isinstance(json.loads(capsys.readouterr().out), dict)

    command = ["monitor", "report", "--project", str(PROJECT)]
    monkeypatch.setattr(sys, "argv", ["aitm-usage", *command])
    assert cli.main() == 1
    assert "monitor-report-unavailable" in capsys.readouterr().err

    monkeypatch.setattr(
        sys, "argv", ["aitm-usage", "--project", str(project.root), *command]
    )
    with pytest.raises(SystemExit) as rejected:
        cli.main()
    assert rejected.value.code == 2
    assert "cannot combine" in capsys.readouterr().err
