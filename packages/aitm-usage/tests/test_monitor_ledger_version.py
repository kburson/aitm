import hashlib
import json
import sqlite3
import sys
from contextlib import closing, nullcontext
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock
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


@pytest.fixture
def catalog_policy(monkeypatch):
    """Feed only metadata SELECT results to real ledger admission and upgrade."""
    key = b"v" * 32
    root = Path("/fixture/project-state")
    base_catalog = (
        (
            "table",
            "checkpoints",
            "checkpoints",
            "CREATE TABLE checkpoints (payload TEXT) STRICT",
        ),
        (
            "table",
            "commits",
            "commits",
            "CREATE TABLE commits (sequence INTEGER PRIMARY KEY) STRICT",
        ),
    )
    v2_catalog = (
        ("table", "monitor_revisions", "monitor_revisions", ledger._MONITOR_SCHEMA[0]),
        (
            "index",
            "monitor_revision_sequence",
            "monitor_revisions",
            ledger._MONITOR_SCHEMA[1],
        ),
    )
    v3_catalog = (
        (
            "table",
            "monitor_delivery_receipts",
            "monitor_delivery_receipts",
            ledger._DELIVERY_SCHEMA,
        ),
    )

    def supported(version):
        if version == 1:
            return base_catalog
        if version == 2:
            return tuple(sorted((*base_catalog, *v2_catalog), key=lambda row: row[1]))
        assert version == 3
        return tuple(
            sorted((*base_catalog, *v2_catalog, *v3_catalog), key=lambda row: row[1])
        )

    def observed(version, *, reported=None, catalog=None):
        identity = ledger._identity(PROJECT, key, version)
        store = ledger.Ledger(root, identity, key)
        queries = []
        openings = []
        metadata = {
            "PRAGMA user_version": (version if reported is None else reported,),
            "PRAGMA journal_mode": ("wal",),
            "PRAGMA application_id": (ledger.APPLICATION_ID,),
            "SELECT project_id, key_id FROM identity WHERE singleton = 1": (
                str(PROJECT),
                identity.key_id,
            ),
            "SELECT COALESCE(MAX(sequence), 0) FROM commits": (1,),
        }

        def connection(path, *, write):
            assert path == store.database_path
            openings.append(write)

            def execute(statement):
                sql = " ".join(statement.split())
                queries.append(sql)
                if sql == ("BEGIN IMMEDIATE" if write else "BEGIN"):
                    return None
                if (
                    sql
                    == "SELECT type, name, tbl_name, sql FROM sqlite_schema ORDER BY name"
                ):
                    return supported(version) if catalog is None else catalog
                assert sql in metadata, f"Unexpected ledger query: {sql}"
                return SimpleNamespace(fetchone=lambda: metadata[sql])

            conn = MagicMock(spec=sqlite3.Connection)
            conn.execute.side_effect = execute
            return nullcontext(conn)

        monkeypatch.setattr(ledger, "_connection", connection)
        return store, queries, openings

    def read_storage(path, project_id):
        assert (path, project_id) == (root, PROJECT)
        return key

    pins = Mock()
    state_files = ((1, 2), (1, 3), (1, 4), (1, 5))

    def read_key(path, project_id, identity):
        assert (path, project_id, identity) == (root, PROJECT, state_files[-1])
        return key

    monkeypatch.setattr(ledger, "_supported_schema", supported)
    monkeypatch.setattr(ledger, "_validate_storage", read_storage)
    monkeypatch.setattr(ledger, "_read_key", read_key)
    monkeypatch.setattr(ledger, "_state_files", lambda path: state_files)
    monkeypatch.setattr(
        ledger, "project_guard", lambda path, project: nullcontext(pins)
    )
    monkeypatch.setattr(ledger, "_lease", lambda path: nullcontext(pins))
    monkeypatch.setattr(ledger, "_pin_directory", lambda path: nullcontext(pins))
    return observed, supported


def test_schema_upgrade_preserves_legacy_identity_and_export_bytes(project, tmp_path):
    before = project.as_of()
    key = project.key_path.read_bytes()
    legacy_backup = tmp_path / "legacy-backup"
    receipt = backup.backup(project, legacy_backup)
    assert receipt.schema_version == 1
    assert backup.verify_backup(legacy_backup, project) == receipt
    assert json.loads((legacy_backup / "manifest.json").read_bytes())["format"] == (
        "aitm-usage.backup/v1"
    )
    assert ledger.Ledger.open(project.root, PROJECT).as_of() == before
    canonical = json.dumps(ledger._supported_schema(1), separators=(",", ":")).encode()
    assert hashlib.sha256(canonical).hexdigest() == LEGACY_FINGERPRINT
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
def test_schema_tag_requires_its_exact_tables(catalog_policy, version):
    observed, supported = catalog_policy
    if version == 2:
        catalog = supported(1)
    else:
        unexpected = (
            "table",
            "monitor_revisions",
            "monitor_revisions",
            "CREATE TABLE monitor_revisions (payload TEXT)",
        )
        catalog = (*supported(1), unexpected)
    project, queries, openings = observed(1, reported=version, catalog=catalog)
    with pytest.raises(ledger.LedgerError, match="Invalid ledger table schema"):
        ledger.Ledger.open(project.root, PROJECT)
    _assert_rejected_catalog_read(queries, openings)


def _assert_rejected_catalog_read(queries, openings):
    assert openings == [False]
    assert (
        queries[-1]
        == "SELECT type, name, tbl_name, sql FROM sqlite_schema ORDER BY name"
    )


@pytest.mark.parametrize(
    ("version", "mutation"),
    [
        (3, "PRAGMA user_version = 4"),
        (3, "DROP TABLE monitor_delivery_receipts"),
        (2, "CREATE TABLE monitor_delivery_receipts (wrong TEXT)"),
        (3, None),
    ],
    ids=["future-version", "missing-table", "incompatible-v2-layout", "stale-head"],
)
def test_delivery_upgrade_refuses_unknown_or_incomplete_catalog(
    catalog_policy, version, mutation
):
    observed, supported = catalog_policy
    if mutation is None:
        store, queries, openings = observed(version)
        with pytest.raises(
            ledger.ConflictError,
            match="Ledger changed before delivery schema upgrade",
        ):
            store.upgrade_delivery_schema(2)
        assert openings == [False, True]
        assert queries[-1] == "SELECT COALESCE(MAX(sequence), 0) FROM commits"
        return
    if mutation == "PRAGMA user_version = 4":
        store, queries, openings = observed(version, reported=4)
        with pytest.raises(ledger.LedgerError, match="Unsupported ledger schema"):
            store.upgrade_delivery_schema(1)
        assert openings == [False]
        assert queries == ["BEGIN", "PRAGMA user_version"]
        return

    if mutation == "DROP TABLE monitor_delivery_receipts":
        catalog = tuple(
            row for row in supported(version) if row[1] != "monitor_delivery_receipts"
        )
    else:
        extra = (
            "table",
            "monitor_delivery_receipts",
            "monitor_delivery_receipts",
            mutation,
        )
        catalog = tuple(sorted((*supported(version), extra), key=lambda row: row[1]))
    store, queries, openings = observed(version, catalog=catalog)
    with pytest.raises(ledger.LedgerError, match="Invalid ledger table schema"):
        store.upgrade_delivery_schema(1)
    _assert_rejected_catalog_read(queries, openings)


def test_v3_restore_authenticates_delivery_rows(project, tmp_path, monkeypatch):
    from aitm_usage.monitor_types import (
        MonitorModel,
        MonitorObservation,
        MonitorProvider,
        MonitorRevision,
        NativeSurface,
        ObservationTimeBasis,
    )

    class StoppedLaunchControl:
        def __init__(self, _ledger):
            pass

        plist_directory = tmp_path / "LaunchAgents"

        def job(self, label):
            return None

    monkeypatch.setattr(install, "ServiceSupervisor", StoppedLaunchControl)
    sequence = project.as_of().sequence
    project.upgrade_monitor_schema(sequence)
    store = ledger.Ledger.open(project.root, PROJECT)
    store.upgrade_delivery_schema(sequence)
    store = ledger.Ledger.open(project.root, PROJECT)
    before = _durable_bytes(store)
    with pytest.raises(
        ledger.ConflictError, match="Ledger changed before delivery schema upgrade"
    ):
        store.upgrade_delivery_schema(sequence + 1)
    assert _durable_bytes(store) == before

    def revision(number):
        return MonitorRevision(
            store.pseudonymize("fixture", f"delivery-{number}"),
            1,
            MonitorObservation(
                MonitorProvider.CODEX,
                NativeSurface.CODEX_DESKTOP_MACOS,
                MOMENT,
                ObservationTimeBasis.NATIVE_COMPLETION,
                TokenCounts(input_tokens=20, output_tokens=2, total_tokens=22),
                Availability.COMPLETE,
                MonitorModel.GPT_6_1_SOL,
            ),
        )

    saved = tmp_path / "v3-backup"
    first, later = revision(1), revision(2)
    with store.writer() as writer:
        receipt = writer._commit_monitor_delivery(first, 1, "a" * 64)
    saved_receipt = backup.backup(store, saved)
    with store.writer() as writer:
        writer._commit_monitor_delivery(later, 2, "b" * 64)
    restored = backup.restore(saved, store.root, store.identity)
    assert restored.sequence == saved_receipt.sequence == receipt.sequence
    assert restored.schema_version == 3
    assert store.monitor_as_of(receipt.sequence).revisions == (first,)
    assert store._monitor_delivery_receipt(receipt.key, receipt.revision) == receipt

    copy = saved / ledger.STORE_NAME / ledger.DATABASE_NAME
    with closing(sqlite3.connect(copy)) as conn, conn:
        conn.execute("UPDATE monitor_delivery_receipts SET seal=?", ("forged",))
    with closing(sqlite3.connect(copy)) as conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    # Preserve the public bundle shape and verify that the staged receipt itself
    # fails while the original live store remains available.
    for suffix in ("-wal", "-shm"):
        copy.with_name(copy.name + suffix).unlink(missing_ok=True)
    check = ledger.Ledger._validate_delivery_receipts
    invoked = []

    def verify_receipts(candidate):
        try:
            check(candidate)
        except ledger.LedgerError as exc:
            invoked.append((candidate.root, str(exc)))
            raise

    monkeypatch.setattr(ledger.Ledger, "_validate_delivery_receipts", verify_receipts)
    before = _durable_bytes(store)
    with pytest.raises(backup.BackupError):
        backup.restore(saved, store.root, store.identity)
    ((staged, reason),) = invoked
    assert staged != store.root
    assert reason == "Invalid committed project delivery receipt"
    assert _durable_bytes(store) == before
    assert store._monitor_delivery_receipt(receipt.key, receipt.revision) == receipt

    with store.writer() as writer, writer._write_transaction() as conn:
        conn.execute("DROP TABLE monitor_delivery_receipts")
    incomplete = _durable_bytes(store)
    with pytest.raises(ledger.LedgerError, match="Invalid ledger table schema"):
        store.upgrade_delivery_schema(restored.sequence)
    assert _durable_bytes(store) == incomplete


def test_new_runtime_accepts_unmodified_legacy_store_backup_and_installer_probe(
    catalog_policy, monkeypatch
):
    _, supported = catalog_policy
    root = Path("/fixture/runtime")
    executable = root / "aitm-usage"

    def fingerprint(version):
        data = json.dumps(supported(version), separators=(",", ":"))
        return [
            ledger.APPLICATION_ID,
            version,
            hashlib.sha256(data.encode()).hexdigest(),
        ]

    observed = {
        "version": "0.1.0",
        "interpreter_version": "3.13.9",
        "interpreter": str(executable.with_name("python")),
        "packages": ["aitm-usage"],
        "schema": fingerprint(1),
        "entry_points": [["console_scripts", "aitm-usage", "aitm_usage.cli:main"]],
        "witness_capable": True,
    }
    monkeypatch.setattr(install, "_supported_schema", supported)
    monkeypatch.setattr(install, "_inspect_surface", lambda *args: root)
    monkeypatch.setattr(install, "_run_python", lambda *args: json.dumps(observed))
    monkeypatch.setattr(
        install.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout="aitm-usage 0.1.0\n"
        ),
    )
    wheel = install._Wheel("0.1.0", "1" * 64, b"", {})
    args = (executable, root / "python3", "3.13.9", wheel, b"pinned launcher")
    assert install._probe_runtime(*args, schema_version=1).witness_capable
    with pytest.raises(install.InstallError):
        install._probe_runtime(*args, schema_version=2)
    observed["schema"][1] = True
    with pytest.raises(install.InstallError):
        install._probe_runtime(*args, schema_version=1)
    observed["schema"][1:] = [1, "0" * 64]
    with pytest.raises(install.InstallError):
        install._probe_runtime(*args, schema_version=1)

    observed["schema"] = [fingerprint(1), fingerprint(2)]
    for version in (1, 2):
        assert install._probe_runtime(*args, schema_version=version).witness_capable
    with pytest.raises(install.InstallError, match="schema is incompatible"):
        install._probe_runtime(*args, schema_version=3)
    observed["schema"].append(fingerprint(3))
    for version in (1, 2, 3):
        assert install._probe_runtime(*args, schema_version=version).witness_capable


def test_legacy_global_state_and_report_project_uuid_are_separate(monkeypatch, capsys):
    key = b"c" * 32
    project = ledger.Ledger(
        Path("/fixture/legacy"), ledger._identity(PROJECT, key), key
    )
    open_project = Mock(return_value=project)
    status_report = Mock(return_value={"heartbeat": None})
    monkeypatch.setattr(cli, "open_project", open_project)
    monkeypatch.setattr(cli, "status_report", status_report)
    monkeypatch.setattr(cli, "version", lambda _: "0.1.0")
    monkeypatch.setattr(
        sys, "argv", ["aitm-usage", "--project", str(project.root), "status", "--json"]
    )
    assert cli.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "heartbeat": None,
        "heartbeat_age_seconds": None,
    }

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
    open_project.assert_called_once_with(project.root)
    status_report.assert_called_once_with(project.root, project)
