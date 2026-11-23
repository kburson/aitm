import hashlib
import json
import os
import plistlib
import socket
import sqlite3
import stat
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from contextlib import closing, nullcontext
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from io import BytesIO
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock
from uuid import UUID
from zipfile import ZipFile

import pytest
from test_ledger import _memory_ledger

import aitm_usage
from aitm_usage import cli, install, scopes, service
from aitm_usage import ledger as ledger_module
from aitm_usage.export import export_as_of
from aitm_usage.ledger import KEY_NAME, Ledger, LedgerIdentity
from aitm_usage.pricing import load_rate_card
from aitm_usage.types import (
    CommandAcknowledgment,
    CommandReceipt,
    Diagnostic,
    DiagnosticCode,
    InboxCommand,
    ItemKey,
    ItemKind,
    ItemParent,
    LedgerBatch,
    LedgerView,
    MarkerDisposition,
    Provider,
    Revision,
    SourceAnchorCommand,
    _encode,
)

PROJECT = UUID(int=940)
CUTOFF = "2026-11-09T16:00:00+00:00"


def _lifecycle_cli(root, monkeypatch, capsys):
    def command(*args, expected=0):
        monkeypatch.setattr(
            sys,
            "argv",
            ["aitm-usage", "--project", str(root), *map(str, args), "--json"],
        )
        result = cli.main()
        captured = capsys.readouterr()
        assert result == expected, captured.err
        return json.loads(captured.out)

    return command


@pytest.fixture
def project(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    root = tmp_path / "project state"
    sources, checkout = tmp_path / "sources", tmp_path / "checkout"
    sources.mkdir()
    checkout.mkdir()
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            dict(
                project_id=str(PROJECT),
                source_roots=[str(sources)],
                checkout_anchors=[str(checkout)],
                cutoff=CUTOFF,
            )
        )
    )
    registration = service.register_project(root, config)
    ledger = Ledger.open(root, PROJECT)

    class StoppedLaunchControl:
        def __init__(self, _ledger):
            pass

        plist_directory = tmp_path / "LaunchAgents"

        def job(self, label):
            return None

    monkeypatch.setattr(install, "ServiceSupervisor", StoppedLaunchControl)

    return registration, ledger, _lifecycle_cli(root, monkeypatch, capsys)


def _parent(number):
    command_id = UUID(int=number)
    return InboxCommand(
        command_id,
        PROJECT,
        ItemParent(
            command_id,
            PROJECT,
            ItemKey(ItemKind.ISSUE, number),
            ItemKey(ItemKind.ISSUE, 83),
        ),
    )


def _add_anchor(registration, ledger, directory, number, *, drain=True):
    anchor = directory / f"anchor-{number}"
    anchor.mkdir()
    request = directory / f"request-{number}.json"
    request.write_text(
        json.dumps(
            dict(
                command_id=str(UUID(int=number)),
                project_id=str(PROJECT),
                checkout=str(anchor),
            )
        )
    )
    command = service.stage_source_anchor(ledger, request)
    assert scopes.enqueue_command(ledger.root, command) is None
    if drain:
        service.collect_once(registration, ledger)
    return command


def _bundle_bytes(path):
    return {
        entry.relative_to(path): entry.read_bytes()
        for entry in path.rglob("*")
        if entry.is_file()
    }


def test_fixed_snapshot_restores_exact_authority_key_and_export(project, tmp_path):
    from aitm_usage.backup import BackupError, backup, restore
    from aitm_usage.ledger import DATABASE_NAME, STORE_NAME

    registration, ledger, command = project
    _add_anchor(registration, ledger, tmp_path, 941)
    sources = registration.source_roots[0]
    fixture = Path(__file__).parent / "fixtures/codex/usage.jsonl"
    (sources / "source.jsonl").write_bytes(
        fixture.read_bytes().replace(
            b"CHECKOUT", os.fsencode(registration.checkout_anchors[0])
        )
        + b'{"unexpected":"private-source-canary-94"}\n'
    )
    service.collect_once(registration, ledger)
    expected_view = ledger.as_of()
    assert expected_view.checkpoints
    key = ledger.key_path.read_bytes()
    pseudonym = ledger.pseudonymize("proof", "restore-pseudonym-canary-94")
    destination = tmp_path / "backup"
    with ledger.writer():
        saved = backup(ledger, destination)
    assert saved.sequence == expected_view.sequence
    assert str(registration.source_roots[0]) not in json.dumps(saved.as_dict())
    files = _bundle_bytes(destination)
    assert [p.name for p in files if p.suffix == ".attested"] == [
        f"{UUID(int=941)}.2.attested"
    ]
    for path, data in files.items():
        if path.name != KEY_NAME:
            assert key not in data
            for canary in (
                b"private-source-canary-94",
                b"restore-pseudonym-canary-94",
                b"account-secret",
                b"resp_secret",
                b"branch-secret",
                b"credits-secret",
                b"00000000-0000-0000-0000-000000000101",
            ):
                assert canary not in data

    before = tmp_path / "before"
    after = tmp_path / "after"
    expected_export = export_as_of(expected_view, load_rate_card(), before)
    with ledger.writer() as writer:
        writer.apply(
            LedgerBatch(
                (
                    Revision(
                        ledger.pseudonymize("proof", "after-backup"),
                        1,
                        Diagnostic(
                            DiagnosticCode.MALFORMED_USAGE,
                            datetime.fromisoformat(CUTOFF),
                            Provider.CODEX,
                        ),
                    ),
                )
            )
        )
    assert ledger.as_of().sequence > expected_view.sequence
    state_inode = ledger.database_path.parent.stat().st_ino
    restored = restore(destination, ledger.root, ledger.identity)
    assert restored.sequence == expected_view.sequence
    assert ledger.database_path.parent.stat().st_ino != state_inode
    assert ledger.key_path.read_bytes() == key
    assert ledger.database_path.with_name("usage.sqlite3-wal").stat().st_size == 0
    assert ledger.pseudonymize("proof", "restore-pseudonym-canary-94") == pseudonym
    assert ledger.as_of() == expected_view
    assert set(service.load_registration(ledger).checkout_anchors) == {
        registration.checkout_anchors[0],
        tmp_path / "anchor-941",
    }
    assert export_as_of(ledger.as_of(), load_rate_card(), after) == expected_export
    assert _bundle_bytes(before) == _bundle_bytes(after)
    assert (
        command("backup", "--output", tmp_path / "cli-backup")["sequence"]
        == saved.sequence
    )
    before_refusal = _bundle_bytes(ledger.root)
    with closing(sqlite3.connect(destination / STORE_NAME / DATABASE_NAME)) as database:
        database.execute("PRAGMA user_version=94")
    with pytest.raises(BackupError, match="Invalid private restore bundle or target"):
        restore(destination, ledger.root, ledger.identity)
    assert _bundle_bytes(ledger.root) == before_refusal


def test_backup_copies_only_authority_in_its_pinned_snapshot(
    project, tmp_path, monkeypatch
):
    from aitm_usage import backup as recovery

    registration, ledger, _ = project
    _add_anchor(registration, ledger, tmp_path, 941)
    late = _add_anchor(registration, ledger, tmp_path, 942, drain=False)
    original = recovery._copy_snapshot

    def copy_after_commit(reader, destination):
        service.collect_once(registration, ledger)
        assert ledger.command_receipt(late) is not None
        original(reader, destination)

    before = ledger.as_of().sequence
    monkeypatch.setattr(recovery, "_copy_snapshot", copy_after_commit)
    target = tmp_path / "backup"
    receipt = recovery.backup(ledger, target)
    assert before == receipt.sequence < ledger.as_of().sequence
    assert not any(str(late.command_id) in str(path) for path in _bundle_bytes(target))


@pytest.fixture
def restore_policy(lifecycle_policy, recovery_paths, monkeypatch):
    from aitm_usage import backup as recovery
    from aitm_usage.ledger import STORE_NAME

    ledger, supervisor = lifecycle_policy
    observe, _ = recovery_paths
    source = Path("/fixture/backup")
    staging = ledger.root / "staged"
    for path, inodes in (
        (ledger.root, (1, 2)),
        (ledger.root / STORE_NAME, (1, 2, 3)),
        (source, (1, 4)),
        (staging, (1, 2, 5)),
        (staging / STORE_NAME, (1, 2, 5, 6)),
    ):
        observe(path, *inodes)

    candidate = replace(ledger, root=staging)
    saved = recovery.BackupReceipt(
        PROJECT, ledger.identity.key_id, ledger.identity.schema_version, 1, "a" * 64
    )
    inbox, acknowledgments, anchors = (
        SimpleNamespace(fd=fd, check=Mock()) for fd in (10, 11, 12)
    )
    registration, configuration = _installation_registration(ledger)
    authority = {recovery.REGISTRATION_NAME: configuration}
    files = {
        ledger.root: dict(authority),
        inbox.fd: {},
        acknowledgments.fd: {},
        anchors.fd: {},
    }

    def child(parent, name, *, create):
        if name == scopes.INBOX_NAME:
            assert parent.path == ledger.root and create
            return nullcontext(inbox)
        if name == recovery.ANCHORS_NAME:
            assert parent.path == ledger.root and not create
            return nullcontext(anchors if files[anchors.fd] else None)
        assert parent is inbox and name == scopes.ACKS_NAME and not create
        return nullcontext(acknowledgments)

    def store_files(directory):
        assert directory in (ledger.root, staging)
        return directory

    def open_ledger(path, project_id):
        assert path == ledger.root and project_id == PROJECT
        return ledger

    def verify_bundle(bundle, directory, expected):
        assert (bundle, directory, expected) == (source, staging, ledger.identity)
        return (
            candidate,
            state.view,
            authority,
            replace(saved, sequence=state.view.sequence),
        )

    def read_private(pin, name):
        location = getattr(pin, "fd", None)
        if location is None:
            location = pin.path
        return files[location][name]

    swap = Mock(side_effect=AssertionError("invalid restore reached swap"))
    monkeypatch.setattr(install, "ServiceSupervisor", Mock(return_value=supervisor))
    monkeypatch.setattr(Ledger, "open", staticmethod(open_ledger))
    monkeypatch.setattr(recovery, "project_guard", lambda *_: nullcontext(Mock()))
    monkeypatch.setattr(recovery, "_lease", lambda _: nullcontext(Mock()))
    monkeypatch.setattr(
        recovery, "TemporaryDirectory", lambda **_: nullcontext(staging)
    )
    monkeypatch.setattr(recovery, "_verify_bundle", verify_bundle)
    monkeypatch.setattr(recovery, "_state_files", store_files)
    monkeypatch.setattr(recovery, "_private_child", child)
    monkeypatch.setattr(recovery, "_publication", lambda _: nullcontext())
    monkeypatch.setattr(recovery, "_swap_store", swap)
    host = SimpleNamespace(listdir=lambda fd: list(files[fd]))
    for module in (recovery, scopes):
        monkeypatch.setattr(module, "os", host)
        monkeypatch.setattr(module, "_read_private", read_private)

    state = SimpleNamespace(
        ledger=ledger,
        source=source,
        files=files,
        acknowledgments=files[acknowledgments.fd],
        anchors=files[anchors.fd],
        authority=authority,
        registration=registration,
        view=LedgerView(PROJECT, 1, (registration,), ()),
        swap=swap,
    )
    return state


def _installation_registration(ledger):
    config = service._Config(
        PROJECT,
        ("/fixture/source",),
        ("/fixture/checkout",),
        datetime.fromisoformat(CUTOFF),
        (),
        (),
        (),
    )
    registration = service._registration_revision(ledger, config)
    return registration, _encode(config, service._Config).encode()


def test_restore_refuses_ahead_ack_and_preserves_files(restore_policy):
    from aitm_usage import backup as recovery

    state = restore_policy
    ledger = state.ledger
    command = _parent(943)
    receipt = CommandReceipt(
        command, ledger.validate_command(command), MarkerDisposition.ACCEPTED
    )
    state.acknowledgments[f"{command.command_id}.json"] = _encode(
        receipt.acknowledgment, CommandAcknowledgment
    ).encode()
    before = {fd: dict(contents) for fd, contents in state.files.items()}
    with pytest.raises(recovery.BackupError, match="no exact backup receipt"):
        recovery.restore(state.source, ledger.root, ledger.identity)
    assert state.files == before
    state.swap.assert_not_called()


@pytest.fixture
def install_policy_ledger():
    return _memory_ledger(ledger_module, PROJECT, b"i" * 32)


@pytest.fixture
def lifecycle_policy(install_policy_ledger, monkeypatch):
    guard = Mock()
    supervisor = SimpleNamespace(
        plist_directory=Path("/fixture/services"), job=Mock(return_value=None)
    )
    monkeypatch.setattr(
        install, "_lifecycle", lambda agent: nullcontext((object(), guard))
    )
    monkeypatch.setattr(install, "_read_private", Mock(return_value=None))
    monkeypatch.setattr(install._Agent, "read", lambda agent: b"")
    return install_policy_ledger, supervisor


def test_public_restore_refuses_a_loaded_job_before_store_swap(
    lifecycle_policy, monkeypatch
):
    from aitm_usage.backup import BackupError, restore

    ledger, control = lifecycle_policy
    source = Path("/fixture/backup")
    control.job.return_value = object()
    open_ledger = Mock(return_value=ledger)
    swap = Mock(side_effect=AssertionError("running service reached restore"))
    monkeypatch.setattr(Ledger, "open", open_ledger)
    monkeypatch.setattr(install, "ServiceSupervisor", Mock(return_value=control))
    monkeypatch.setattr(install, "_restore_stopped", swap)
    with pytest.raises(BackupError, match="not a stopped compatible project"):
        restore(source, ledger.root, ledger.identity)
    open_ledger.assert_called_once_with(ledger.root, PROJECT)
    control.job.assert_called_once_with(f"org.aitm.usage.{PROJECT}")
    swap.assert_not_called()


def test_restore_replays_exact_pending_ack_after_final_anchor_commit(
    project, tmp_path, monkeypatch
):
    from aitm_usage.backup import backup, restore
    from aitm_usage.types import MarkerDisposition

    registration, ledger, _ = project
    command = _add_anchor(registration, ledger, tmp_path, 941, drain=False)
    anchor, hidden = tmp_path / "anchor-941", tmp_path / "held"
    anchor.rename(hidden)
    service.collect_once(registration, ledger)
    assert ledger.command_receipt(command).disposition is MarkerDisposition.PENDING
    hidden.rename(anchor)

    def interrupt(*args):
        raise OSError("injected after anchor commit")

    with monkeypatch.context() as patch:
        patch.setattr(scopes, "_acknowledge", interrupt)
        with pytest.raises(OSError, match="after anchor commit"):
            service.collect_once(registration, ledger)
    final = ledger.command_receipt(command)
    assert final.disposition is MarkerDisposition.ACCEPTED
    inbox = ledger.root / scopes.INBOX_NAME
    before = _bundle_bytes(inbox)
    bundle = tmp_path / "backup"
    saved = backup(ledger, bundle)
    assert restore(bundle, ledger.root, ledger.identity).sequence == saved.sequence
    assert _bundle_bytes(inbox) == before
    service.collect_once(registration, ledger)
    assert not (inbox / f"{command.command_id}.json").exists()
    assert ledger.command_receipt(command) == final
    assert ledger.as_of().sequence == saved.sequence


def test_restore_refuses_mismatched_private_proof_or_identity(
    restore_policy, monkeypatch
):
    from aitm_usage.backup import BackupError, restore

    state = restore_policy
    ledger = state.ledger
    open_ledger = Ledger.open

    def inspect_identity(path, project):
        if project == UUID(int=941):
            assert path == ledger.root
            return ledger
        return open_ledger(path, project)

    monkeypatch.setattr(Ledger, "open", staticmethod(inspect_identity))
    for expected in (
        LedgerIdentity(UUID(int=941), ledger.identity.key_id),
        LedgerIdentity(PROJECT, "sha256:" + "1" * 64),
    ):
        with pytest.raises(BackupError, match="target identity mismatch"):
            restore(state.source, ledger.root, expected)

    command_id = UUID(int=941)
    anchor = "/fixture/anchor-941"
    proposal = service._AnchorProposal(command_id, PROJECT, anchor)
    payload = SourceAnchorCommand(
        command_id,
        PROJECT,
        state.registration.record.configuration_ref,
        service.checkout_anchor_reference(ledger, Path(anchor)),
    )
    command = InboxCommand(command_id, PROJECT, payload)
    effect = service._anchor_revision(ledger, payload)
    receipt = CommandReceipt(
        command, ledger.validate_command(command), MarkerDisposition.ACCEPTED
    )
    receipt_key = ledger.pseudonymize("inbox-command", str(command_id))
    state.view = LedgerView(
        PROJECT, 2, (state.registration, effect, Revision(receipt_key, 1, receipt)), ()
    )
    proof, expected_bytes = service._anchor_attestation(ledger, command, effect, 2)
    proposal_name = f"{command_id}.json"
    proposal_bytes = _encode(proposal, service._AnchorProposal).encode()
    state.authority[f"{service.ANCHORS_NAME}/{proposal_name}"] = proposal_bytes
    state.authority[f"{service.ANCHORS_NAME}/{proof}"] = expected_bytes
    state.anchors.update({proposal_name: proposal_bytes, proof: b"mismatched"})
    before = {fd: dict(contents) for fd, contents in state.files.items()}
    with pytest.raises(BackupError, match="authority"):
        restore(state.source, ledger.root, ledger.identity)
    assert state.files == before
    state.swap.assert_not_called()


def test_restore_fences_publication_until_atomic_swap(project, tmp_path, monkeypatch):
    from aitm_usage import backup as recovery

    registration, ledger, _ = project
    target = tmp_path / "backup"
    recovery.backup(ledger, target)
    original = recovery._swap_store
    staged, proceed, publisher_entered = Event(), Event(), Event()
    inbox_path = ledger.root / "inbox"
    original_publication = scopes._publication

    def swap(*args):
        staged.set()
        assert proceed.wait(5)
        return original(*args)

    def publication(inbox):
        assert inbox.path == inbox_path
        publisher_entered.set()
        return original_publication(inbox)

    monkeypatch.setattr(recovery, "_swap_store", swap)
    monkeypatch.setattr(scopes, "_publication", publication)
    with ThreadPoolExecutor(max_workers=2) as workers:
        restoring = workers.submit(
            recovery.restore, target, ledger.root, ledger.identity
        )
        try:
            assert staged.wait(5)
            publish = workers.submit(scopes.enqueue_command, ledger.root, _parent(944))
            assert publisher_entered.wait(5)
            with pytest.raises(TimeoutError):
                publish.result(timeout=0.2)
        finally:
            proceed.set()
        assert restoring.result(timeout=5).sequence == 1
        assert publish.result(timeout=5) is None
    service.collect_once(registration, ledger)
    assert ledger.command_receipt(_parent(944)).disposition == "accepted"


def test_restore_refuses_incompatible_store_and_interrupted_staging(
    restore_policy, monkeypatch
):
    from aitm_usage import backup as recovery

    state = restore_policy
    ledger = state.ledger
    before = {path: files.copy() for path, files in state.files.items()}
    interrupted = Mock(side_effect=OSError("injected staging failure"))
    with monkeypatch.context() as patch:
        patch.setattr(recovery, "_swap_store", interrupted)
        with pytest.raises(
            recovery.BackupError, match="Invalid private restore bundle or target"
        ):
            recovery.restore(state.source, ledger.root, ledger.identity)
    interrupted.assert_called_once()
    assert state.files == before

    connection = Mock()
    connection.execute.return_value.fetchone.return_value = (94,)
    observed_database = Mock(return_value=nullcontext(connection))

    def verify_candidate(source, staged, expected):
        assert source == state.source and expected == ledger.identity
        recovery._candidate(staged, expected)

    monkeypatch.setattr(recovery, "_verify_bundle", verify_candidate)
    create_lock = Mock(return_value=nullcontext())
    check_path = Mock()
    monkeypatch.setattr(recovery, "_create_file", create_lock)
    monkeypatch.setattr(recovery, "_check_path", check_path)
    monkeypatch.setattr(recovery, "_connection", observed_database)
    with pytest.raises(
        recovery.BackupError, match="Invalid private restore bundle or target"
    ):
        recovery.restore(state.source, ledger.root, ledger.identity)
    staged = ledger.root / "staged"
    create_lock.assert_called_once_with(staged / recovery.LOCK_NAME)
    database = staged / recovery._DATABASE
    check_path.assert_called_once_with(database)
    observed_database.assert_called_once_with(database, write=True)
    connection.execute.assert_called_once_with("PRAGMA user_version")
    assert state.files == before
    state.swap.assert_not_called()


def test_restore_refuses_replaced_candidate_store(project, tmp_path, monkeypatch):
    from aitm_usage import backup as recovery

    _, ledger, _ = project
    target = tmp_path / "backup"
    recovery.backup(ledger, target)
    before = ledger.database_path.parent.stat().st_ino
    original = recovery._validate_queue

    def replace_stage(project, inbox, live, candidate, view):
        original(project, inbox, live, candidate, view)
        directory = candidate.database_path.parent
        directory.rename(directory.with_name("displaced"))
        directory.mkdir(mode=0o700)

    monkeypatch.setattr(recovery, "_validate_queue", replace_stage)
    with pytest.raises(recovery.BackupError):
        recovery.restore(target, ledger.root, ledger.identity)
    assert ledger.database_path.parent.stat().st_ino == before
    assert ledger.as_of().sequence == 1


def test_backup_and_restore_reject_inherited_acl(project, tmp_path, grant_extra_acl):
    from aitm_usage.backup import BackupError, backup, restore

    _, ledger, _ = project
    blocked = tmp_path / "inheriting"
    blocked.mkdir(mode=0o700)
    grant_extra_acl(blocked, "system.posix_acl_default")
    target = blocked / "refused"
    with pytest.raises(
        BackupError, match="Invalid private backup source or destination"
    ):
        backup(ledger, target)
    assert not target.exists()

    bundle = tmp_path / "backup"
    backup(ledger, bundle)
    bundle.rename(blocked / "backup")
    with pytest.raises(BackupError, match="Invalid private restore bundle or target"):
        restore(blocked / "backup", ledger.root, ledger.identity)


def _wheel(parent, suffix, *, incompatible=False):
    directory = parent / suffix
    directory.mkdir()
    distribution = "aitm_usage-0.1.0.dist-info"
    filename = directory / "aitm_usage-0.1.0-py3-none-any.whl"
    package = Path(aitm_usage.__file__).parent
    with ZipFile(filename, "w") as wheel:
        names = []
        for source in sorted(package.rglob("*")):
            if source.suffix not in {".py", ".json"}:
                continue
            name = f"aitm_usage/{source.relative_to(package)}"
            data = source.read_bytes()
            if name == "aitm_usage/cli.py":
                marker = b"def main() -> int:\n"
                assert marker in data
                data = data.replace(
                    marker,
                    marker
                    + (
                        "    from . import ledger as fixture_ledger\n"
                        f"    fixture_ledger._control_root = lambda: Path({str(parent / 'control')!r})\n"
                        "    monitor_registry._control_root = fixture_ledger._control_root\n"
                    ).encode(),
                )
            if incompatible and name == "aitm_usage/ledger.py":
                data = data.replace(b"SCHEMA_VERSION = 1", b"SCHEMA_VERSION = 94")
            wheel.writestr(name, data)
            names.append(name)
        metadata = {
            "METADATA": "Metadata-Version: 2.1\nName: aitm-usage\nVersion: 0.1.0\nRequires-Python: >=3.13\n",
            "WHEEL": "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
            "entry_points.txt": "[console_scripts]\naitm-usage = aitm_usage.cli:main\n\n",
        }
        for name, contents in metadata.items():
            wheel.writestr(f"{distribution}/{name}", contents)
            names.append(f"{distribution}/{name}")
        wheel.comment = suffix.encode("ascii")
        wheel.writestr(
            f"{distribution}/RECORD",
            "".join(f"{name},,\n" for name in names + [f"{distribution}/RECORD"]),
        )
    with filename.open("rb") as stream:
        return filename, hashlib.file_digest(stream, "sha256").hexdigest()


class _Interrupted(BaseException):
    pass


class _FakeLaunchControl:
    activation_timeout = 0

    def __init__(self, directory, ledger):
        self.plist_directory = directory
        directory.mkdir()
        self.ledger = ledger
        self.loaded = None
        self.disabled = False
        self.bootstraps = []
        self.child = None
        self.startup = "fresh"
        self.fail_digest = "never-match"
        self.defer_removal = False
        self.removal_requested = False

    def close(self):
        if self.child is not None:
            self.child.terminate()
            self.child.wait(timeout=5)
            self.child = None
        self.loaded = None

    def job(self, label):
        job = self.loaded
        if self.removal_requested:
            self.close()
            self.removal_requested = False
        return job

    def process(self, pid):
        if self.child is None or self.child.pid != pid or self.child.poll() is not None:
            return None
        return install.ManagedProcess(pid, self.started, self.interpreter)

    def is_disabled(self, label):
        return self.disabled

    def disable(self, label):
        self.disabled = True

    def enable(self, label):
        self.disabled = False

    def bootout(self, label):
        assert self.disabled
        if self.defer_removal:
            self.removal_requested = True
        else:
            self.close()

    def bootstrap(self, path, interpreter):
        from aitm_usage.ledger import WriterActive

        assert not self.disabled
        assert self.loaded is None
        value = plistlib.loads(path.read_bytes())
        program, *args = value["ProgramArguments"]
        label = f"org.aitm.usage.{PROJECT}"
        assert value["Label"] == label
        assert value["RunAtLoad"] is value["KeepAlive"] is True
        assert args == ["--project", str(self.ledger.root), "service", "run"]
        assert Path(program).is_absolute() and os.access(program, os.X_OK)
        self.bootstraps.append(program)
        if self.fail_digest in program and self.startup == "interrupt":
            raise _Interrupted
        with pytest.raises(WriterActive):
            install.stop_agent(self.ledger, self)
        mode = (
            self.startup
            if self.fail_digest in program or self.startup == "no-heartbeat"
            else "fresh"
        )
        argv = (
            value["ProgramArguments"]
            if mode == "fresh"
            else [sys._base_executable, "-I", "-S", "-c", "import time; time.sleep(60)"]
        )
        self.interpreter = interpreter
        self.started = datetime.now(UTC)
        self.child = subprocess.Popen(
            argv,
            env=install._ENVIRONMENT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.loaded = install.ServiceJob(
            label, path, Path(program), tuple(value["ProgramArguments"]), self.child.pid
        )
        if mode == "fresh":
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                witness = service.status_report(self.ledger.root, self.ledger)
                if witness["producer_pid"] == self.child.pid:
                    assert witness["producer_mode"] == "service"
                    return
                assert self.child.poll() is None
                time.sleep(0.02)
            pytest.fail("The actual service subprocess did not publish its witness")


@pytest.fixture
def launch_control(project, tmp_path, monkeypatch):
    control = _FakeLaunchControl(tmp_path / "LaunchAgents", project[1])
    monkeypatch.setattr(cli, "ServiceSupervisor", lambda _ledger: control)
    yield control
    control.close()


def test_owned_launchagent_and_recoverable_upgrade(project, tmp_path, launch_control):
    _, ledger, command = project
    first, first_digest = _wheel(tmp_path, "first")
    second, second_digest = _wheel(tmp_path, "second")
    incompatible, incompatible_digest = _wheel(
        tmp_path, "incompatible", incompatible=True
    )
    interpreter = Path(sys._base_executable).resolve(strict=True)
    control = launch_control
    control.fail_digest = second_digest
    launch = control.plist_directory

    def activate(action, wheel, digest, *, expected=0, flags=()):
        return command(
            "service",
            action,
            "--wheel",
            wheel,
            "--interpreter",
            interpreter,
            "--wheel-sha256",
            digest,
            *flags,
            expected=expected,
        )

    assert (
        activate("install", first, first_digest, flags=("--dry-run",))["status"]
        == "planned"
    )
    assert not list(launch.iterdir())
    assert (
        activate("install", first, "0" * 64, expected=1)["status"] == "install-failed"
    )
    assert not list(launch.iterdir())
    installed = activate("install", first, first_digest)
    assert installed["wheel_sha256"] == first_digest
    assert installed["poll_interval_seconds"] == 15
    assert len(control.bootstraps) == 1
    process = control.process(control.loaded.pid)
    assert process.pid == control.child.pid
    assert process.executable == interpreter
    assert process.started < datetime.fromisoformat(installed["heartbeat"])
    assert installed["producer_mode"] == "service"
    assert installed["producer_pid"] == process.pid
    assert installed["producer_started"] == process.started.isoformat()
    assert (
        command(
            "service",
            "prune",
            "--version",
            "0.1.0",
            "--wheel-sha256",
            first_digest,
            "--backup",
            tmp_path / "missing",
            expected=1,
        )["status"]
        == "prune-failed"
    )
    path = next(launch.iterdir())
    exact_plist = path.read_bytes()
    previous = control.loaded
    repeated = activate("install", first, first_digest)
    assert repeated["status"] == "already-active"
    assert repeated["producer_pid"] == installed["producer_pid"]
    assert repeated["producer_started"] == installed["producer_started"]
    assert len(control.bootstraps) == 1
    injected_plist = plistlib.loads(exact_plist)
    injected_plist["EnvironmentVariables"] = {"PYTHONPATH": str(tmp_path)}
    path.write_bytes(plistlib.dumps(injected_plist))
    assert (
        activate("install", first, first_digest, expected=1)["status"]
        == "install-failed"
    )
    assert control.loaded == previous
    path.write_bytes(exact_plist)
    rejected = activate("upgrade", incompatible, incompatible_digest, expected=1)
    assert rejected["status"] == "upgrade-failed"
    assert path.read_bytes() == exact_plist and control.loaded == previous
    assert len(control.bootstraps) == 1

    control.startup = "stale"
    failed = activate("upgrade", second, second_digest, expected=1)
    assert failed["status"] == "activation-rolled-back"
    assert path.read_bytes() == exact_plist
    assert replace(control.loaded, pid=None) == replace(previous, pid=None)
    assert control.loaded.pid != previous.pid
    assert len(control.bootstraps) == 3
    assert first_digest in control.bootstraps[0]
    assert second_digest in control.bootstraps[1]
    assert all(Path(item).exists() for item in control.bootstraps)

    control.startup = "no-heartbeat"
    blocked = activate("upgrade", second, second_digest, expected=1)
    assert blocked["status"] == "recovery-required"
    assert path.read_bytes() == exact_plist
    assert replace(control.loaded, pid=None) == replace(previous, pid=None)
    assert list((tmp_path / "control").glob("*.service-recovery.plist"))
    pending_bundle = tmp_path / "pending-backup"
    pending = command("backup", "--output", pending_bundle)
    assert (
        command(
            "service",
            "prune",
            "--version",
            "0.1.0",
            "--wheel-sha256",
            second_digest,
            "--backup",
            pending_bundle,
            expected=1,
        )["status"]
        == "prune-failed"
    )
    assert Path(control.bootstraps[-2]).exists()
    assert (
        hashlib.sha256((pending_bundle / "manifest.json").read_bytes()).hexdigest()
        == pending["manifest_sha256"]
    )

    control.startup = "interrupt"
    with pytest.raises(_Interrupted):
        activate("upgrade", second, second_digest)
    assert path.read_bytes() != exact_plist
    assert control.loaded is None

    control.startup = "fresh"
    success = activate("upgrade", second, second_digest)
    assert success["wheel_sha256"] == second_digest
    assert control.bootstraps[-2] == str(previous.program)
    assert control.bootstraps[-1] != str(previous.program)
    assert success["backup"]["sequence"] == ledger.as_of().sequence
    assert (
        ledger.root / "service-backups" / success["backup_id"] / "manifest.json"
    ).is_file()
    prune_bundle = tmp_path / "prune-backup"
    retained = command("backup", "--output", prune_bundle)
    pruned = command(
        "service",
        "prune",
        "--version",
        "0.1.0",
        "--wheel-sha256",
        first_digest,
        "--backup",
        prune_bundle,
    )
    assert pruned["status"] == "pruned"
    assert pruned["backup"]["manifest_sha256"] == retained["manifest_sha256"]
    assert not previous.program.exists()
    assert (ledger.root / "wheels" / first_digest / first.name).is_file()
    original_key = ledger.key_path.read_bytes()
    assert (
        command("restore", "--backup", prune_bundle, expected=1)["status"]
        == "restore-failed"
    )
    control.defer_removal = True
    assert command("service", "stop")["status"] == "stopped"
    assert control.disabled and control.loaded is None and path.exists()
    restored = command("restore", "--backup", prune_bundle)
    assert restored["status"] == "restored"
    assert restored["manifest_sha256"] == retained["manifest_sha256"]
    assert (
        hashlib.sha256((prune_bundle / "manifest.json").read_bytes()).hexdigest()
        == retained["manifest_sha256"]
    )
    assert command("service", "uninstall")["status"] == "uninstalled"
    assert not path.exists()
    assert ledger.key_path.read_bytes() == original_key
    assert ledger.as_of().sequence == success["backup"]["sequence"]


@pytest.fixture
def activation_policy(install_policy_ledger, runtime_receipt, monkeypatch, capsys):
    case = runtime_receipt
    ledger = replace(install_policy_ledger, root=case.ledger.root)
    runtime = case.runtime
    case.set_console(install._launcher(case.python, case.site))
    registration, configuration = _installation_registration(ledger)
    view = LedgerView(PROJECT, 1, (registration,), ())
    files = {service.REGISTRATION_NAME: configuration}
    service_files = {}
    recovery_records = {}
    pin = Mock(fd=73)
    control = SimpleNamespace(
        plist_directory=Path("/fixture/services"),
        activation_timeout=0,
        loaded=None,
        disabled=False,
        bootstraps=[],
        after_bootstrap=lambda: None,
    )
    after = datetime(2026, 11, 20, tzinfo=UTC)
    clock = Mock(wraps=datetime)
    clock.now.return_value = after
    process = install.ManagedProcess(5301, after, runtime.interpreter)
    status = service._Status(
        PROJECT,
        registration.record.configuration_ref,
        after + timedelta(seconds=1),
        runtime.version,
        runtime.interpreter_version,
        service.CollectionReport(view.sequence, 0, 0, 0, 0, 0, False),
        (),
        service._ProducerMode.SERVICE,
        process.pid,
    )
    control.status = status
    owned = install._Agent(ledger, control)

    def bootstrap(path, interpreter):
        assert (path, interpreter) == (owned.plist, runtime.interpreter)
        assert not control.disabled and control.loaded is None
        executable = owned.program(service_files[path])
        arguments = tuple(owned.payload(executable)["ProgramArguments"])
        control.loaded = install.ServiceJob(
            owned.label, path, executable, arguments, process.pid
        )
        files[service.STATUS_NAME] = _encode(control.status, service._Status).encode()
        clock.now.return_value = after + timedelta(seconds=2)
        control.bootstraps.append(path)
        control.after_bootstrap()

    def bootout(label):
        assert label == owned.label and control.disabled
        control.loaded = None

    control.job = lambda label: control.loaded if label == owned.label else None
    control.process = lambda pid: process if pid == process.pid else None
    control.is_disabled = lambda _: control.disabled
    control.disable = lambda _: setattr(control, "disabled", True)
    control.enable = lambda _: setattr(control, "disabled", False)
    control.bootstrap = bootstrap
    control.bootout = bootout

    def write_plist(agent, data, expected):
        assert agent.read() == expected
        if data:
            agent.program(data)
            service_files[agent.plist] = data
        else:
            del service_files[agent.plist]

    def publish_record(directory, name, data):
        assert directory is pin and name not in recovery_records
        recovery_records[name] = data
        return True

    def remove_record(name, *, dir_fd):
        assert dir_fd == pin.fd
        del recovery_records[name]

    read_owned = install._read_owned
    read_private = install._read_private
    pin_directory = install._pin_directory
    monkeypatch.setattr(install, "datetime", clock)
    monkeypatch.setattr(install, "_validated_path", Mock())
    monkeypatch.setattr(
        install, "_path_exists", lambda path: path == owned.plist.parent
    )
    monkeypatch.setattr(
        install,
        "_read_owned",
        lambda path, **kwargs: (
            service_files.get(path)
            if path == owned.plist
            else read_owned(path, **kwargs)
        ),
    )
    monkeypatch.setattr(
        install,
        "_read_private",
        lambda directory, name: (
            recovery_records.get(name)
            if directory is pin
            else read_private(directory, name)
        ),
    )
    monkeypatch.setattr(
        install,
        "_pin_directory",
        lambda path: nullcontext(pin) if path == ledger.root else pin_directory(path),
    )
    monkeypatch.setattr(install, "_lifecycle", lambda _: nullcontext((pin, pin)))
    monkeypatch.setattr(install, "project_guard", lambda *_: nullcontext(pin))
    monkeypatch.setattr(install, "_lease", lambda *_: nullcontext(pin))
    monkeypatch.setattr(install, "_publish", publish_record)
    monkeypatch.setattr(
        install, "os", SimpleNamespace(unlink=remove_record, fsync=Mock())
    )
    monkeypatch.setattr(install._Agent, "write", write_plist)
    monkeypatch.setattr(
        install,
        "_prepare",
        lambda actual, wheel, interpreter: install._read_runtime(
            actual, case.directory, interpreter=interpreter
        ),
    )
    monkeypatch.setattr(service, "_pin_directory", lambda _: nullcontext(pin))
    monkeypatch.setattr(service, "_read_private", lambda _, name: files.get(name))
    monkeypatch.setattr(service, "version", lambda _: runtime.version)
    monkeypatch.setattr(Ledger, "open", lambda *_: ledger)
    monkeypatch.setattr(Ledger, "as_of", lambda _: view)
    monkeypatch.setattr(cli, "open_project", lambda _: ledger)
    monkeypatch.setattr(cli, "ServiceSupervisor", lambda _: control)

    def invoke(action):
        return _lifecycle_cli(ledger.root, monkeypatch, capsys)(
            "service",
            action,
            "--wheel",
            Path("/fixture/candidate.whl"),
            "--wheel-sha256",
            case.wheel.digest,
            "--interpreter",
            runtime.interpreter,
            expected=1,
        )

    return SimpleNamespace(
        runtime_files=case,
        ledger=ledger,
        control=control,
        process=process,
        owned=owned,
        project_files=files,
        service_files=service_files,
        records=recovery_records,
        invoke=invoke,
        command=_lifecycle_cli(ledger.root, monkeypatch, capsys),
    )


def test_one_shot_from_other_pid_cannot_certify_install(activation_policy):
    case = activation_policy
    process = case.process
    control = case.control
    control.status = replace(
        control.status,
        producer_mode=service._ProducerMode.ONE_SHOT,
        producer_pid=process.pid + 1,
    )
    result = case.invoke("install")
    assert result["status"] == "activation-rolled-back"
    observed = service.status_report(case.ledger.root, case.ledger)
    assert observed["producer_mode"] == "one-shot"
    assert observed["producer_pid"] == control.status.producer_pid != process.pid
    assert observed["status_sequence"] == case.ledger.as_of().sequence
    assert control.loaded is None and not control.disabled
    assert not case.service_files and not case.records


def test_unapproved_runtime_hook_never_executes(project, tmp_path, launch_control):
    _, ledger, command = project
    wheel, digest = _wheel(tmp_path, "hook")
    interpreter = Path(sys._base_executable).resolve(strict=True)
    runtime = install._prepare(ledger, install._wheel(wheel, digest), interpreter)
    (site,) = runtime.executable.parents[1].glob("lib/python*/site-packages")
    marker = tmp_path / "unexpected-hook-ran"
    (site / "sitecustomize.py").write_text(f"open({str(marker)!r}, 'w').close()\n")
    result = command(
        "service",
        "install",
        "--wheel",
        wheel,
        "--wheel-sha256",
        digest,
        "--interpreter",
        interpreter,
        expected=1,
    )
    assert result["status"] == "install-failed"
    assert not marker.exists()
    assert not launch_control.bootstraps


def test_runtime_replaced_after_bootstrap_cannot_certify_readiness(
    activation_policy, monkeypatch
):
    case = activation_policy
    runtime = case.runtime_files
    tampered = b"#!/bin/sh\nexit 1\n"
    read_owned = install._read_owned
    launcher_reads = []

    def read_runtime_file(path, **options):
        data = read_owned(path, **options)
        if path == runtime.executable:
            launcher_reads.append(data)
        return data

    monkeypatch.setattr(install, "_read_owned", read_runtime_file)
    case.control.after_bootstrap = lambda: runtime.set_console(
        tampered, update_receipt=False
    )
    result = case.invoke("install")
    assert result["status"] == "activation-rolled-back"
    assert launcher_reads[-1] == tampered
    assert launcher_reads[0] == install._launcher(runtime.python, runtime.site)
    assert case.control.bootstraps == [case.owned.plist]
    assert case.control.loaded is None
    assert not case.service_files and not case.records


def test_installed_console_ignores_environment_and_working_directory_hooks(
    project, tmp_path
):
    _, ledger, _ = project
    wheel, digest = _wheel(tmp_path, "isolated-launch")
    interpreter = Path(sys._base_executable).resolve(strict=True)
    runtime = install._prepare(ledger, install._wheel(wheel, digest), interpreter)
    untrusted = tmp_path / "untrusted"
    untrusted.mkdir()
    marker = tmp_path / "startup-hook-ran"
    hook = f"open({str(marker)!r}, 'w').close()\n"
    (untrusted / "sitecustomize.py").write_text(hook)
    (untrusted / "aitm_usage").mkdir()
    (untrusted / "aitm_usage" / "__init__.py").write_text(hook)
    shell_hook = untrusted / "shell-init"
    shell_hook.write_text(f"touch '{marker}'\n")
    result = subprocess.run(
        [runtime.executable, "--version"],
        env={
            **os.environ,
            "PYTHONPATH": str(untrusted),
            "PYTHONHOME": str(untrusted),
            "PYTHONUSERBASE": str(untrusted),
            "BASH_ENV": str(shell_hook),
            "ENV": str(shell_hook),
        },
        cwd=untrusted,
        capture_output=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == b"aitm-usage 0.1.0\n"
    assert not marker.exists()


def test_upgrade_refuses_witness_incapable_running_prior(
    activation_policy, monkeypatch
):
    case = activation_policy
    ledger, control, agent = case.ledger, case.control, case.owned
    candidate = case.runtime_files.runtime
    prior_digest = "b" * 64
    prior_directory = (
        ledger.root / install._VERSIONS / f"{candidate.version}-{prior_digest}"
    )
    prior = replace(
        candidate,
        executable=prior_directory
        / candidate.executable.relative_to(case.runtime_files.directory),
        wheel_sha256=prior_digest,
        witness_capable=False,
    )
    read_runtime = install._read_runtime

    def observe_runtime(actual, directory, **options):
        if directory == prior_directory:
            assert actual is ledger
            return prior
        return read_runtime(actual, directory, **options)

    monkeypatch.setattr(install, "_read_runtime", observe_runtime)
    plist = plistlib.dumps(agent.payload(prior.executable))
    case.service_files[agent.plist] = plist
    args = tuple(plistlib.loads(plist)["ProgramArguments"])
    job = install.ServiceJob(
        agent.label, agent.plist, prior.executable, args, case.process.pid
    )
    control.loaded = job
    observed = control.status
    heartbeat = service._LegacyStatus(
        observed.project_id,
        observed.configuration_ref,
        observed.heartbeat,
        prior.version,
        prior.interpreter_version,
        observed.report,
        (),
    )
    case.project_files[service.STATUS_NAME] = _encode(
        heartbeat, service._LegacyStatus
    ).encode()
    status = service.status_report(ledger.root, ledger)
    assert status["heartbeat"] is not None
    assert status["producer_mode"] is status["producer_pid"] is None
    result = case.invoke("upgrade")
    assert result["status"] == "witness-unavailable"
    assert control.loaded == job and not control.disabled
    assert agent.read() == plist
    assert not control.bootstraps and not case.records

    # Simulate an older interrupted upgrade whose record predates the refusal.
    control.loaded = None
    pending_plist = plistlib.dumps(agent.payload(candidate.executable))
    case.service_files[agent.plist] = pending_plist
    pending = install._Operation(plist, pending_plist, True, False, "", "")
    record = install._record_name(agent)
    case.records[record] = pending.encode()
    assert case.command("service", "stop", expected=1)["status"] == "recovery-required"
    assert agent.read() == plist
    assert case.records[record] == pending.encode()
    assert control.disabled and not control.bootstraps


def test_same_pid_with_different_start_cannot_certify_health(
    runtime_receipt, monkeypatch
):
    from aitm_usage.supervisor import ManagedProcess, ServiceJob

    case = runtime_receipt
    runtime = case.runtime
    case.ledger.identity.project_id = PROJECT
    case.set_console(install._launcher(case.python, case.site))
    control = SimpleNamespace(
        plist_directory=Path("/fixture/services"), job=Mock(), process=Mock()
    )
    agent = install._Agent(case.ledger, control)
    registration = agent.payload(runtime.executable)
    plist = plistlib.dumps(registration)
    pid = 5301
    control.job.return_value = ServiceJob(
        agent.label,
        agent.plist,
        runtime.executable,
        tuple(registration["ProgramArguments"]),
        pid,
    )
    started = datetime(2026, 11, 20, tzinfo=UTC)
    heartbeat = started + timedelta(seconds=1)
    clock = Mock(wraps=datetime)
    clock.now.return_value = heartbeat
    monkeypatch.setattr(install, "datetime", clock)
    monkeypatch.setattr(install._Agent, "read", lambda agent: plist)
    monkeypatch.setattr(
        install,
        "status_report",
        Mock(
            return_value={
                "read_gap": False,
                "registration_gap": False,
                "status_sequence": 1,
                "collector_version": runtime.version,
                "collector_interpreter_version": runtime.interpreter_version,
                "producer_mode": "service",
                "producer_pid": pid,
                "heartbeat": heartbeat.isoformat(),
            }
        ),
    )
    process = ManagedProcess(pid, started, runtime.interpreter)
    control.process.return_value = process
    assert agent.healthy(runtime, plist, started).process == process
    changed = replace(process, started=process.started + timedelta(microseconds=1))
    control.process.reset_mock()
    control.process.side_effect = (process, changed)
    assert agent.healthy(runtime, plist, started) is None
    assert control.process.call_count == 2


def test_backup_refuses_output_inside_replaceable_store(
    install_policy_ledger, monkeypatch
):
    from aitm_usage import backup as recovery

    ledger = install_policy_ledger
    store = ledger.database_path.parent
    directory = store / "nested-backup"
    identities = ((1, 1), (1, 2), (1, 3))
    pin = Mock(return_value=nullcontext(Mock(path=store, identities=identities)))
    ancestry = Mock(return_value=identities)
    stage = Mock(side_effect=AssertionError("contained output reached backup staging"))
    monkeypatch.setattr(recovery, "_pin_directory", pin)
    monkeypatch.setattr(recovery, "_validated_path", ancestry)
    monkeypatch.setattr(recovery, "TemporaryDirectory", stage)
    with pytest.raises(recovery.BackupError, match="overlaps"):
        recovery.backup(ledger, directory)
    pin.assert_called_once_with(store)
    ancestry.assert_called_once_with(directory, directory=True, allow_missing=True)
    stage.assert_not_called()


def test_backup_refuses_store_through_physical_path_alias(
    install_policy_ledger, monkeypatch
):
    from aitm_usage import backup as recovery

    ledger = install_policy_ledger
    store = ledger.database_path.parent
    alias = ledger.root.parent / "alias"
    destination = alias / "nested-backup"
    inodes = {
        ancestor: inode for inode, ancestor in enumerate(reversed(store.parents), 1)
    }
    inodes[store] = inodes[alias] = len(inodes) + 1

    def lstat(path):
        if path not in inodes:
            raise FileNotFoundError(path)
        return os.stat_result(
            (stat.S_IFDIR | 0o700, inodes[path], 1, 1, os.geteuid(), 0, 0, 0, 0, 0)
        )

    monkeypatch.setattr(Path, "lstat", lstat)
    monkeypatch.setattr(ledger_module, "_check_acl", Mock())
    pin = SimpleNamespace(
        path=store,
        identities=ledger_module._validated_path(store, directory=True),
        check=Mock(),
    )
    stage = Mock(side_effect=AssertionError("aliased store reached backup staging"))
    monkeypatch.setattr(recovery, "_pin_directory", Mock(return_value=nullcontext(pin)))
    monkeypatch.setattr(recovery, "TemporaryDirectory", stage)
    with pytest.raises(recovery.BackupError, match="overlaps"):
        recovery.backup(ledger, destination)
    assert not destination.exists()
    stage.assert_not_called()


@pytest.fixture
def recovery_paths(monkeypatch):
    from aitm_usage import backup as recovery

    pins = {}

    def observe(path, *inodes):
        pins[path] = SimpleNamespace(
            path=path, identities=tuple((1, inode) for inode in inodes), check=Mock()
        )

    def pin(path):
        return nullcontext(pins[path])

    ancestry = Mock(side_effect=lambda path, **kwargs: pins[path].identities)
    monkeypatch.setattr(recovery, "_pin_directory", pin)
    monkeypatch.setattr(install, "_pin_directory", pin)
    monkeypatch.setattr(recovery, "_validated_path", ancestry)
    return observe, ancestry


def test_restore_preserves_backup_inside_replaceable_store(
    lifecycle_policy, recovery_paths, monkeypatch
):
    from aitm_usage import backup as recovery

    ledger, control = lifecycle_policy
    observe, ancestry = recovery_paths
    store = ledger.database_path.parent
    inside = store / "nested-backup"
    staged = ledger.root / ".restore-staging"
    observe(ledger.root, 1, 2, 3)
    observe(store, 1, 2, 3, 4)
    observe(inside, 1, 2, 3, 4, 5)
    observe(staged, 1, 2, 3, 6)
    verify = Mock(side_effect=AssertionError("nested backup reached restore staging"))
    swap = Mock(side_effect=AssertionError("nested backup reached the store swap"))
    monkeypatch.setattr(Ledger, "open", Mock(return_value=ledger))
    monkeypatch.setattr(install, "ServiceSupervisor", Mock(return_value=control))
    monkeypatch.setattr(recovery, "project_guard", lambda *_: nullcontext(object()))
    monkeypatch.setattr(recovery, "_lease", lambda *_: nullcontext(object()))
    monkeypatch.setattr(recovery, "TemporaryDirectory", lambda **_: nullcontext(staged))
    monkeypatch.setattr(recovery, "_verify_bundle", verify)
    monkeypatch.setattr(recovery, "_swap_store", swap)

    with pytest.raises(recovery.BackupError, match="overlaps"):
        recovery.restore(inside, ledger.root, ledger.identity)

    ancestry.assert_called_once_with(inside, directory=True, allow_missing=False)
    verify.assert_not_called()
    swap.assert_not_called()


def test_prune_preserves_nested_recovery_material(
    lifecycle_policy, recovery_paths, monkeypatch, capsys
):
    ledger, control = lifecycle_policy
    observe, ancestry = recovery_paths
    digest = "a" * 64
    version_dir = ledger.root / install._VERSIONS / f"0.1.0-{digest}"
    bundle = version_dir / "backup"
    external = ledger.root / "external-backup"
    observe(version_dir, 1, 2, 3, 4, 5)
    observe(bundle, 1, 2, 3, 4, 5, 6)
    observe(external, 1, 2, 3, 7)
    verify = Mock(
        side_effect=AssertionError("nested recovery material reached verification")
    )
    remove = Mock(
        side_effect=AssertionError("prune would delete nested recovery material")
    )
    read_wheel = Mock(side_effect=AssertionError("prune opened a retained wheel"))
    monkeypatch.setattr(cli, "open_project", Mock(return_value=ledger))
    monkeypatch.setattr(cli, "ServiceSupervisor", Mock(return_value=control))
    monkeypatch.setattr(cli, "version", lambda _: "0.1.0")
    monkeypatch.setattr(install, "verify_backup", verify)
    monkeypatch.setattr(install, "_wheel", read_wheel)
    monkeypatch.setattr(install, "shutil", SimpleNamespace(rmtree=remove))
    command = _lifecycle_cli(ledger.root, monkeypatch, capsys)
    arguments = ("service", "prune", "--version", "0.1.0", "--wheel-sha256", digest)

    assert (
        command(*arguments, "--backup", bundle, expected=1)["status"] == "prune-failed"
    )
    ancestry.assert_called_once_with(bundle, directory=True, allow_missing=False)
    ancestry.reset_mock()

    retained = install._wheel_path(ledger, "0.1.0", digest)
    inside = version_dir / retained.name
    observe(inside, 1, 2, 3, 4, 5, 8)
    monkeypatch.setattr(install, "_wheel_path", lambda *args: inside)
    assert (
        command(*arguments, "--backup", external, expected=1)["status"]
        == "prune-failed"
    )
    assert ancestry.call_count == 2
    ancestry.assert_called_with(inside, directory=False, allow_missing=False)
    verify.assert_not_called()
    read_wheel.assert_not_called()
    remove.assert_not_called()


@pytest.mark.parametrize("case", ["matching", "wrong", "unset", "empty", "hostile"])
def test_scope_launcher_forwards_only_exact_optional_thread_candidate(tmp_path, case):
    side_effect = tmp_path / "unexpected-shell-execution"
    hostile = (
        f'- spaces "quoted" and \'single\' $(touch "{side_effect}") '
        f'`touch "{side_effect}"`\nsecond line'
    )
    candidate = {
        "matching": str(UUID(int=1201)),
        "wrong": str(UUID(int=1202)),
        "unset": None,
        "empty": "",
        "hostile": hostile,
    }[case]
    site = tmp_path / "fixture site"
    package = site / "aitm_usage"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("")
    (package / "cli.py").write_text(
        "import json, os\n"
        "def main():\n"
        "    print(json.dumps([\n"
        "        'CODEX_THREAD_ID' in os.environ,\n"
        "        os.environ.get('CODEX_THREAD_ID'),\n"
        "        os.environ.get('UNRELATED_TEST_VARIABLE'),\n"
        "    ]))\n"
        "    return 0\n"
    )
    executable = tmp_path / "fixture launcher"
    executable.write_bytes(install._launcher(Path(sys._base_executable), site))
    executable.chmod(0o700)
    environment = {"UNRELATED_TEST_VARIABLE": "must be cleared"}
    if candidate is not None:
        environment["CODEX_THREAD_ID"] = candidate
    observed = subprocess.run(
        [executable], env=environment, capture_output=True, text=True, timeout=10
    )
    assert observed.returncode == 0, observed.stderr
    assert json.loads(observed.stdout) == [candidate is not None, candidate, None]
    assert not side_effect.exists()


def test_legacy_scope_launcher_matches_golden_bytes_and_digest():
    python = Path("/pinned/python 3")
    site = Path("/pinned/site packages")
    original = (
        b"#!/bin/sh\n"
        b"exec /usr/bin/env -i LC_ALL=C PATH=/usr/bin:/bin '/pinned/python 3' "
        b"-I -S -B -c '\n"
        b"import sys\n"
        b"sys.path.insert(0, sys.argv.pop(1))\n"
        b"from aitm_usage.cli import main\n"
        b"raise SystemExit(main())\n"
        b"' '/pinned/site packages' \"$@\"\n"
    )
    assert install._launcher(python, site, legacy=True) == original
    assert hashlib.sha256(original).hexdigest() == (
        "272cbc70638f983a30eceae7be3cb7a2e1bf9768ce3dcb94d0dea5c37e75045c"
    )


@pytest.fixture
def runtime_receipt(monkeypatch):
    ledger = SimpleNamespace(
        root=Path("/ledger"), identity=SimpleNamespace(schema_version=4)
    )
    version, digest, python_version = "0.1.0", "a" * 64, "3.13.9"
    interpreter = Path("/pinned/python3")
    directory = ledger.root / install._VERSIONS / f"{version}-{digest}"
    environment = directory / ("venv-" + "b" * 32)
    executable = environment / "bin" / "aitm-usage"
    site = install._site(environment, python_version)
    python = executable.with_name("python")
    wheel = install._Wheel(version, digest, b"retained wheel", {})
    runtime = install._Runtime(
        executable, version, digest, python_version, interpreter, True
    )
    receipt = {
        "format": install._RUNTIME_FORMAT,
        "environment": environment.name,
        "interpreter": str(interpreter),
        "interpreter_sha256": hashlib.sha256(b"interpreter").hexdigest(),
    }
    files = {interpreter: b"interpreter"}
    pinned = object()

    def read_receipt(parent, name):
        assert (parent, name) == (pinned, install._RUNTIME)
        return json.dumps(receipt, sort_keys=True).encode()

    pin = Mock(return_value=nullcontext(pinned))
    inspect_interpreter = Mock(return_value=python_version)
    probe = Mock(return_value=runtime)
    read_wheel = Mock(return_value=wheel)
    monkeypatch.setattr(install, "_pin_directory", pin)
    monkeypatch.setattr(install, "_read_private", read_receipt)
    monkeypatch.setattr(install, "_read_owned", lambda path, **_options: files[path])
    monkeypatch.setattr(install, "_wheel", read_wheel)
    monkeypatch.setattr(install, "_interpreter", inspect_interpreter)
    monkeypatch.setattr(install, "_probe_runtime", probe)

    def set_console(data, *, update_receipt=True):
        files[executable] = data
        if update_receipt:
            receipt["console_sha256"] = hashlib.sha256(data).hexdigest()

    return SimpleNamespace(
        ledger=ledger,
        directory=directory,
        executable=executable,
        interpreter=interpreter,
        python=python,
        python_version=python_version,
        site=site,
        wheel=wheel,
        runtime=runtime,
        receipt=receipt,
        set_console=set_console,
        pin=pin,
        read_wheel=read_wheel,
        inspect_interpreter=inspect_interpreter,
        probe=probe,
    )


@pytest.mark.parametrize("legacy", [False, True])
def test_launcher_verification_selects_exact_receipt_variant(runtime_receipt, legacy):
    case = runtime_receipt
    launcher = install._launcher(case.python, case.site, legacy=legacy)
    case.set_console(launcher)
    assert install._read_runtime(case.ledger, case.directory) == case.runtime
    case.pin.assert_called_once_with(case.directory)
    case.read_wheel.assert_called_once_with(
        case.ledger.root
        / install._WHEELS
        / case.wheel.digest
        / "aitm_usage-0.1.0-py3-none-any.whl",
        case.wheel.digest,
        private=True,
    )
    case.probe.assert_called_once_with(
        case.executable,
        case.interpreter,
        case.python_version,
        case.wheel,
        launcher,
        schema_version=case.ledger.identity.schema_version,
    )

    case.probe.reset_mock()
    case.set_console(
        install._launcher(case.python, case.site, legacy=not legacy),
        update_receipt=False,
    )
    with pytest.raises(install.InstallError, match="Verified runtime files changed"):
        install._read_runtime(case.ledger, case.directory)

    case.set_console(b"#!/bin/sh\nexit 99\n")
    with pytest.raises(install.InstallError, match="unknown launcher"):
        install._read_runtime(case.ledger, case.directory)
    case.probe.assert_not_called()


def test_installed_runtime_checks_interpreter_digest_before_any_execution(
    runtime_receipt,
):
    case = runtime_receipt
    case.set_console(install._launcher(case.python, case.site))
    case.receipt["interpreter_sha256"] = "0" * 64

    with pytest.raises(install.InstallError, match="Verified runtime files changed"):
        install._read_runtime(case.ledger, case.directory)

    case.inspect_interpreter.assert_not_called()
    case.probe.assert_not_called()


def test_installed_runtime_detects_changed_launcher_on_disk(runtime_receipt):
    case = runtime_receipt
    case.set_console(install._launcher(case.python, case.site))
    assert install._read_runtime(case.ledger, case.directory) == case.runtime

    case.inspect_interpreter.reset_mock()
    case.probe.reset_mock()
    case.set_console(b"#!/bin/sh\nexit 99\n", update_receipt=False)
    with pytest.raises(install.InstallError, match="Verified runtime files changed"):
        install._read_runtime(case.ledger, case.directory)
    case.inspect_interpreter.assert_not_called()
    case.probe.assert_not_called()


def test_installed_scope_launcher_upgrade_preserves_old_receipt_and_queues(
    project, tmp_path, monkeypatch, launch_control
):
    from aitm_usage import monitor_registry
    from aitm_usage.monitor_control import ControlInbox, ScopeInboxReader
    from aitm_usage.monitor_scope import Scope
    from aitm_usage.scope_admission import MarkRequest
    from aitm_usage.types import BoundaryKind, ScopeMarker, WorkPhase, encode_marker

    _, ledger, command = project
    interpreter = Path(sys._base_executable).resolve(strict=True)
    first, first_digest = _wheel(tmp_path, "old-launcher")
    second, second_digest = _wheel(tmp_path, "new-launcher")
    assert first_digest != second_digest and first.name == second.name
    generator = install._launcher

    def activate(action, wheel, digest, *, expected=0):
        return command(
            "service",
            action,
            "--wheel",
            wheel,
            "--wheel-sha256",
            digest,
            "--interpreter",
            interpreter,
            expected=expected,
        )

    with monkeypatch.context() as old:
        old.setattr(
            install,
            "_launcher",
            lambda python, site, **kwargs: generator(python, site, legacy=True),
        )
        assert activate("install", first, first_digest)["status"] == "installed"
    previous = launch_control.loaded.program
    previous_directory = previous.parents[2]
    old_receipt = previous_directory / install._RUNTIME
    old_receipt_bytes = old_receipt.read_bytes()
    old_launcher_bytes = previous.read_bytes()
    assert activate("install", first, first_digest)["status"] == "already-active"
    assert old_receipt.read_bytes() == old_receipt_bytes
    assert previous.read_bytes() == old_launcher_bytes

    launch_control.startup = "stale"
    launch_control.fail_digest = second_digest
    failed = activate("upgrade", second, second_digest, expected=1)
    assert failed["status"] == "activation-rolled-back"
    assert launch_control.loaded.program == previous
    assert install._read_runtime(ledger, previous_directory).executable == previous
    assert old_receipt.read_bytes() == old_receipt_bytes

    launch_control.startup = "fresh"
    upgraded = activate("upgrade", second, second_digest)
    assert upgraded["status"] == "upgraded"
    executable = launch_control.loaded.program
    assert executable != previous
    assert command("service", "stop")["status"] == "stopped"
    assert launch_control.loaded is None

    legacy_id, thread_id = UUID(int=1201), UUID(int=1202)
    item = ItemKey(ItemKind.ISSUE, 194)
    marker = ScopeMarker(
        legacy_id,
        Provider.CODEX,
        scopes.session_reference(ledger, Provider.CODEX, str(thread_id)),
        1,
        BoundaryKind.REQUEST,
        ledger.pseudonymize("fixture", "native-boundary"),
        datetime.fromisoformat(CUTOFF) + timedelta(seconds=1),
        item,
        WorkPhase.PLANNING,
        ledger.pseudonymize("fixture", "participant"),
        PROJECT,
        receipt_ref=ledger.pseudonymize("scope-receipt", str(legacy_id)),
    )
    legacy_file = tmp_path / "legacy marker.json"
    legacy_file.write_bytes(encode_marker(marker))
    legacy_file.chmod(0o600)
    legacy_args = [
        "--project",
        str(ledger.root),
        "scope",
        "mark",
        "--marker",
        str(legacy_file),
        "--json",
    ]

    def invoke(program, args, thread=None):
        env = {"UNRELATED_TEST_VARIABLE": "never forward"}
        if thread is not None:
            env["CODEX_THREAD_ID"] = thread
        return subprocess.run(
            [program, *args], env=env, capture_output=True, timeout=10
        )

    assert invoke(previous, legacy_args, str(thread_id)).returncode == 1
    for candidate in (None, "", str(UUID(int=1203))):
        denied = invoke(executable, legacy_args, candidate)
        assert denied.returncode == 1
        assert not (ledger.root / "inbox" / f"{legacy_id}.json").exists()
    accepted = invoke(executable, legacy_args, str(thread_id))
    assert accepted.returncode == 0, accepted.stderr
    assert (
        accepted.stdout
        == f'{{"command_id": "{legacy_id}", "status": "queued"}}\n'.encode()
    )
    assert (ledger.root / "inbox" / f"{legacy_id}.json").exists()

    monitor_root = tmp_path / "control" / "monitor"
    inbox = ControlInbox(monitor_root)
    command_id, grant_id = UUID(int=1204), UUID(int=1205)
    request = tmp_path / "monitor scope request.json"
    request.write_text(
        json.dumps(
            {
                "command_id": str(command_id),
                "grant_id": str(grant_id),
                "scope": {"project_id": str(PROJECT)},
            }
        )
    )
    request.chmod(0o600)
    with monitor_registry.Registry(monitor_root).writer() as writer:
        writer.register_project(
            monitor_registry.ProjectRegistrationRequest(
                PROJECT, str(ledger.root), "Fixture"
            )
        )
        writer.source_evidence()
        reader = ScopeInboxReader(writer, inbox)
        reader.register(grant_id, PROJECT, ("mark",))
        proposal = MarkRequest(command_id, grant_id, Scope(PROJECT))
        reader.advertise(reader.probe(proposal))
        queued = invoke(
            executable,
            ["monitor", "scope", "mark", "--request", str(request), "--json"],
        )
        assert queued.returncode == 0, queued.stderr
        assert (
            queued.stdout
            == f'{{"command_id": "{command_id}", "status": "queued"}}\n'.encode()
        )
        with inbox.publication() as locked:
            (envelope,) = reader.iter_verified(locked)
        assert envelope.body.request == proposal
        assert writer.command_status(command_id) is None
        assert not (monitor_root / "scope-v1.json").exists()


def test_portable_supervisor_reaps_owned_service_across_controllers(
    project, tmp_path, monkeypatch
):
    from aitm_usage import supervisor as managed_service
    from aitm_usage.ledger import LedgerError, _pin_directory
    from aitm_usage.scopes import _publish
    from aitm_usage.supervisor import ServiceSupervisor

    _, ledger, command = project
    wheel, digest = _wheel(tmp_path, "supervised")
    supervisor = ServiceSupervisor(ledger)
    interpreter = Path(sys._base_executable).resolve(strict=True)
    label = f"org.aitm.usage.{ledger.identity.project_id}"

    try:
        receipt = install.install_wheel(
            ledger,
            wheel,
            interpreter,
            supervisor,
            action="install",
            expected_sha256=digest,
        )
        assert receipt.status == "installed"
        observer = ServiceSupervisor(ledger)
        job = observer.job(label)
        assert job.pid == receipt.producer_pid
        assert observer.process(job.pid).executable == interpreter
        pid_record = supervisor.plist_directory / f"{label}.pid.json"
        assert pid_record.stat().st_mode & 0o777 == 0o600
        saved = pid_record.read_bytes()
        assert (ledger.root / service.STATUS_NAME).stat().st_mode & 0o777 == 0o600

        with _pin_directory(supervisor.plist_directory) as directory:
            _publish(directory, f"{label}.stop", b"previous-incarnation")
        assert observer.process(job.pid) is not None

        for transient in (None, LedgerError("record replaced while reading")):
            read = managed_service._read_private
            calls = []

            def read_during_transition(directory, name):
                if name == pid_record.name and not calls:
                    calls.append(name)
                    if transient is not None:
                        raise transient
                    return None
                return read(directory, name)

            with monkeypatch.context() as patch:
                patch.setattr(managed_service, "_read_private", read_during_transition)
                assert observer.job(label) == job
                assert calls == [pid_record.name]
    finally:
        assert install.stop_agent(ledger, ServiceSupervisor(ledger)).status == "stopped"

    assert not pid_record.exists()
    assert observer.job(label) is None
    assert observer.is_disabled(label)
    with pytest.raises(ProcessLookupError):
        os.kill(job.pid, 0)

    try:
        restarted = command("service", "start")
        assert restarted["status"] == "started"
        status = command("status")
        assert status["producer_pid"] == restarted["producer_pid"]
        assert status["heartbeat_age_seconds"] >= 0
        assert command("service", "start")["status"] == "already-active"
    finally:
        assert command("service", "stop")["status"] == "stopped"

    unrelated = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        stale = json.loads(saved)
        stale["pid"] = unrelated.pid
        raw = json.dumps(stale, sort_keys=True, separators=(",", ":")).encode()
        pid_record.write_bytes(raw)
        pid_record.chmod(0o600)
        with pytest.raises(install.InstallError, match="stale"):
            install.stop_agent(ledger, ServiceSupervisor(ledger))
        assert pid_record.read_bytes() == raw
        assert unrelated.poll() is None
    finally:
        unrelated.terminate()
        unrelated.wait(timeout=5)


def test_portable_supervisor_holds_existing_legacy_registration(
    install_policy_ledger, monkeypatch
):
    from aitm_usage import supervisor as managed_service

    ledger = install_policy_ledger
    legacy = Path("/fixture/legacy.plist")
    monkeypatch.setattr(
        managed_service, "_guard_path", lambda *_: Path("/fixture/writer.lock")
    )
    supervisor = managed_service.ServiceSupervisor(ledger)
    monkeypatch.setattr(supervisor, "_legacy_registration", lambda: legacy)
    path_exists = Mock(return_value=True)
    monkeypatch.setattr(managed_service, "_path_exists", path_exists)
    monkeypatch.setattr(install._Agent, "read", lambda agent: b"")
    lifecycle = Mock(side_effect=AssertionError("dry run mutated service state"))
    monkeypatch.setattr(install, "_lifecycle", lifecycle)
    with pytest.raises(install.InstallError, match="legacy LaunchAgent"):
        install.stop_agent(ledger, supervisor, dry_run=True)
    path_exists.assert_called_once_with(legacy)
    lifecycle.assert_not_called()


def test_portable_supervisor_refuses_stop_without_writer_exclusion(
    lifecycle_policy, monkeypatch
):
    from aitm_usage.ledger import WriterActive

    ledger, supervisor = lifecycle_policy
    guard = Mock(side_effect=WriterActive("project writer is active"))
    lease = Mock(side_effect=AssertionError("busy writer reached local lease"))
    sleep = Mock(side_effect=AssertionError("zero timeout entered another retry"))
    monkeypatch.setattr(install, "project_guard", guard)
    monkeypatch.setattr(install, "_lease", lease)
    monkeypatch.setattr(
        install, "time", SimpleNamespace(monotonic=lambda: 0, sleep=sleep)
    )
    monkeypatch.setattr(install, "_STOP_TIMEOUT", 0)
    with pytest.raises(WriterActive, match="project writer is active"):
        install.stop_agent(ledger, supervisor)
    guard.assert_called_once_with(ledger.root, PROJECT)
    lease.assert_not_called()
    sleep.assert_not_called()


def test_portable_supervisor_owner_refuses_a_reaped_child(monkeypatch):
    from aitm_usage import supervisor

    directory = Path("/fixture/service-owner")
    endpoint = directory / "owner"
    record = supervisor._Launch(
        "a" * 32,
        ("/fixture/aitm-usage", "--project", str(directory), "service", "run"),
        "/fixture/python",
        str(endpoint),
        5302,
        datetime(2026, 11, 20, tzinfo=UTC),
    )
    uid = 501
    metadata = SimpleNamespace(
        st_mode=stat.S_IFSOCK | 0o600, st_uid=uid, st_dev=1, st_ino=17
    )

    class ObservedEndpoint:
        parent = directory

        def __str__(self):
            return str(endpoint)

        def lstat(self):
            return metadata

    observed_endpoint = ObservedEndpoint()
    child = SimpleNamespace(poll=Mock(side_effect=(None, 0)))
    pinned = SimpleNamespace(check=Mock())
    buffer = bytearray()
    peer = MagicMock()
    peer.sendall.side_effect = buffer.extend
    server = SimpleNamespace(accept=lambda: (peer, None))

    def connect(address):
        assert address == str(endpoint)
        buffer.clear()
        supervisor._respond(server, child, record)

    client = SimpleNamespace(
        connect=connect,
        settimeout=Mock(),
        makefile=lambda _: BytesIO(bytes(buffer)),
    )
    socket_factory = Mock(return_value=nullcontext(client))
    monkeypatch.setattr(
        supervisor,
        "socket",
        SimpleNamespace(
            AF_UNIX=socket.AF_UNIX,
            SOCK_STREAM=socket.SOCK_STREAM,
            socket=socket_factory,
        ),
    )
    monkeypatch.setattr(
        supervisor,
        "os",
        SimpleNamespace(geteuid=lambda: uid, path=os.path),
    )
    monkeypatch.setattr(
        supervisor, "Path", {record.endpoint: observed_endpoint}.__getitem__
    )
    monkeypatch.setattr(supervisor, "_pin_directory", lambda _: nullcontext(pinned))
    monkeypatch.setattr(supervisor, "_check_acl", Mock())
    monkeypatch.setattr(supervisor, "_peer_uid", lambda _: uid)

    assert supervisor._confirms_live_child(record)
    assert not supervisor._confirms_live_child(record)
    peer.sendall.assert_called_once_with(_encode(record, supervisor._Launch).encode())
    assert child.poll.call_count == 2
