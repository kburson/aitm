import hashlib
import json
import os
import plistlib
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from contextlib import closing
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Event
from uuid import UUID
from zipfile import ZipFile

import pytest

import aitm_usage
from aitm_usage import cli, install, scopes, service
from aitm_usage.export import export_as_of
from aitm_usage.ledger import KEY_NAME, Ledger, LedgerIdentity
from aitm_usage.pricing import load_rate_card
from aitm_usage.types import (
    Diagnostic,
    DiagnosticCode,
    InboxCommand,
    ItemKey,
    ItemKind,
    ItemParent,
    LedgerBatch,
    Provider,
    Revision,
)

PROJECT = UUID(int=940)
CUTOFF = "2026-11-09T16:00:00+00:00"


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
        plist_directory = tmp_path / "LaunchAgents"

        def job(self, label):
            return None

    monkeypatch.setattr(install, "LaunchControl", StoppedLaunchControl)

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

    return registration, ledger, command


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


def _durable_bytes(path):
    # SQLite read-only transactions can update reader marks in its shared index.
    return {
        name: data
        for name, data in _bundle_bytes(path).items()
        if name.suffix != ".sqlite3-shm"
    }


def test_fixed_snapshot_restores_exact_authority_key_and_export(project, tmp_path):
    from aitm_usage.backup import backup, restore

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


def test_restore_refuses_ahead_ack_and_preserves_files(project, tmp_path):
    from aitm_usage.backup import BackupError, backup, restore

    registration, ledger, _ = project
    bundle = tmp_path / "backup"
    backup(ledger, bundle)
    assert scopes.enqueue_command(ledger.root, _parent(943)) is None
    service.collect_once(registration, ledger)
    before = _durable_bytes(ledger.root)
    with pytest.raises(BackupError, match="acknowledgment"):
        restore(bundle, ledger.root, ledger.identity)
    assert _durable_bytes(ledger.root) == before


def test_public_restore_refuses_a_loaded_job_before_store_swap(
    project, tmp_path, monkeypatch
):
    from aitm_usage.backup import BackupError, backup, restore

    _, ledger, _ = project
    source = tmp_path / "backup"
    backup(ledger, source)
    before = ledger.database_path.parent.stat().st_ino
    control = install.LaunchControl()
    monkeypatch.setattr(control, "job", lambda label: object())
    monkeypatch.setattr(install, "LaunchControl", lambda: control)
    with pytest.raises(BackupError):
        restore(source, ledger.root, ledger.identity)
    assert ledger.database_path.parent.stat().st_ino == before


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


def test_restore_refuses_mismatched_private_proof_or_identity(project, tmp_path):
    from aitm_usage.backup import BackupError, backup, restore

    registration, ledger, _ = project
    _add_anchor(registration, ledger, tmp_path, 941)
    target = tmp_path / "backup"
    backup(ledger, target)
    for expected in (
        LedgerIdentity(UUID(int=941), ledger.identity.key_id),
        LedgerIdentity(PROJECT, "sha256:" + "1" * 64),
    ):
        with pytest.raises(BackupError):
            restore(target, ledger.root, expected)
    proof = next((ledger.root / "source-anchors").glob("*.attested"))
    proof.write_bytes(b"mismatched")
    before = _bundle_bytes(ledger.root)
    with pytest.raises(BackupError, match="authority"):
        restore(target, ledger.root, ledger.identity)
    assert _bundle_bytes(ledger.root) == before


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
    project, tmp_path, monkeypatch
):
    from aitm_usage import backup as recovery
    from aitm_usage.ledger import DATABASE_NAME, STORE_NAME

    _, ledger, _ = project
    target = tmp_path / "backup"
    recovery.backup(ledger, target)
    before = _bundle_bytes(ledger.root)

    def interrupt(*args):
        raise OSError("injected staging failure")

    with monkeypatch.context() as patch:
        patch.setattr(recovery, "_swap_store", interrupt)
        with pytest.raises(recovery.BackupError):
            recovery.restore(target, ledger.root, ledger.identity)
    assert _bundle_bytes(ledger.root) == before
    with closing(sqlite3.connect(target / STORE_NAME / DATABASE_NAME)) as database:
        database.execute("PRAGMA user_version=94")
    with pytest.raises(recovery.BackupError):
        recovery.restore(target, ledger.root, ledger.identity)
    assert _bundle_bytes(ledger.root) == before


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


@pytest.mark.skipif(sys.platform != "darwin", reason="uses macOS inherited ACL")
def test_backup_and_restore_reject_inherited_acl(project, tmp_path):
    from aitm_usage.backup import BackupError, backup, restore

    _, ledger, _ = project
    blocked = tmp_path / "inheriting"
    blocked.mkdir(mode=0o700)
    subprocess.run(
        [
            "/bin/chmod",
            "+a",
            "everyone allow list,read,file_inherit,directory_inherit",
            blocked,
        ],
        check=True,
    )
    try:
        target = blocked / "refused"
        with pytest.raises(BackupError):
            backup(ledger, target)
        assert not target.exists()

        bundle = tmp_path / "backup"
        backup(ledger, bundle)
        target.mkdir(mode=0o700)
        assert "inherited" in subprocess.check_output(
            ["/bin/ls", "-lde", target], text=True
        )
        bundle.rename(target / "backup")
        with pytest.raises(BackupError):
            restore(target / "backup", ledger.root, ledger.identity)
    finally:
        subprocess.run(["/bin/chmod", "-RN", blocked], check=True)


def _wheel(parent, suffix, *, incompatible=False, legacy=False):
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
                    ).encode(),
                )
            if incompatible and name == "aitm_usage/ledger.py":
                data = data.replace(b"SCHEMA_VERSION = 1", b"SCHEMA_VERSION = 94")
            if legacy and name == "aitm_usage/service.py":
                start = data.index(b"class _Status(_LegacyStatus):")
                end = data.index(b"def _read_status", start)
                data = (
                    data[:start]
                    + b"class _Status(_LegacyStatus):\n    pass\n\n\n"
                    + data[end:]
                )
                data = data.replace(
                    b"            self.mode,\n            os.getpid(),\n", b""
                )
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
        self.after_service_poll = None

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
        return install._process_identity(pid)

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

    def bootstrap(self, path):
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
        self.child = subprocess.Popen(
            argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        self.loaded = install.LaunchJob(
            label, path, Path(program), tuple(value["ProgramArguments"]), self.child.pid
        )
        if mode == "one-shot":
            result = subprocess.run(
                [program, "--project", str(self.ledger.root), "collect-once", "--json"],
                capture_output=True,
                timeout=10,
            )
            assert result.returncode == 0, result.stderr
            witness = service.status_report(self.ledger.root, self.ledger)
            assert witness["producer_mode"] == "one-shot"
            assert witness["producer_pid"] != self.child.pid
        elif mode == "fresh":
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                witness = service.status_report(self.ledger.root, self.ledger)
                if witness["producer_pid"] == self.child.pid:
                    assert witness["producer_mode"] == "service"
                    if self.after_service_poll is not None:
                        self.after_service_poll(Path(program))
                    return
                assert self.child.poll() is None
                time.sleep(0.02)
            pytest.fail("The actual service subprocess did not publish its witness")


@pytest.fixture
def launch_control(project, tmp_path, monkeypatch):
    control = _FakeLaunchControl(tmp_path / "LaunchAgents", project[1])
    monkeypatch.setattr(cli, "LaunchControl", lambda: control)
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
    process = install._process_identity(control.loaded.pid)
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


def test_one_shot_from_other_pid_cannot_certify_install(
    project, tmp_path, launch_control
):
    _, _, command = project
    wheel, digest = _wheel(tmp_path, "one-shot")
    launch_control.startup = "one-shot"
    launch_control.fail_digest = digest
    result = command(
        "service",
        "install",
        "--wheel",
        wheel,
        "--wheel-sha256",
        digest,
        "--interpreter",
        Path(sys._base_executable).resolve(strict=True),
        expected=1,
    )
    assert result["status"] == "activation-rolled-back"
    assert launch_control.loaded is None
    assert not list(launch_control.plist_directory.iterdir())


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
    project, tmp_path, launch_control
):
    _, _, command = project
    wheel, digest = _wheel(tmp_path, "changed-after-start")

    def replace_launcher(program):
        program.write_bytes(b"#!/bin/sh\nexit 1\n")

    launch_control.after_service_poll = replace_launcher
    result = command(
        "service",
        "install",
        "--wheel",
        wheel,
        "--wheel-sha256",
        digest,
        "--interpreter",
        Path(sys._base_executable).resolve(strict=True),
        expected=1,
    )
    assert result["status"] == "activation-rolled-back"
    assert launch_control.loaded is None
    assert not list(launch_control.plist_directory.iterdir())


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
    project, tmp_path, launch_control
):
    _, ledger, command = project
    wheel, digest = _wheel(tmp_path, "legacy", legacy=True)
    interpreter = Path(sys._base_executable).resolve(strict=True)
    prior = install._prepare(ledger, install._wheel(wheel, digest), interpreter)
    agent = install._Agent(ledger, launch_control)
    plist = plistlib.dumps(agent.payload(prior.executable))
    agent.write(plist, b"")
    args = tuple(plistlib.loads(plist)["ProgramArguments"])
    child = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    launch_control.child = child
    launch_control.loaded = install.LaunchJob(
        agent.label, agent.plist, prior.executable, args, child.pid
    )
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        status = service.status_report(ledger.root, ledger)
        if status["heartbeat"] is not None:
            break
        assert child.poll() is None
        time.sleep(0.02)
    assert status["heartbeat"] is not None
    assert status["producer_mode"] is status["producer_pid"] is None
    candidate, next_digest = _wheel(tmp_path, "next")
    result = command(
        "service",
        "upgrade",
        "--wheel",
        candidate,
        "--wheel-sha256",
        next_digest,
        "--interpreter",
        interpreter,
        expected=1,
    )
    assert result["status"] == "witness-unavailable"
    assert child.poll() is None and not launch_control.disabled
    assert agent.plist.read_bytes() == plist
    assert not launch_control.bootstraps

    # Simulate an older interrupted upgrade whose record predates the refusal.
    launch_control.close()
    prepared = install._prepare(
        ledger, install._wheel(candidate, next_digest), interpreter
    )
    pending_plist = plistlib.dumps(agent.payload(prepared.executable))
    agent.write(pending_plist, plist)
    pending = install._Operation(plist, pending_plist, True, False, "", "")
    record = tmp_path / "control" / f"{PROJECT}.service-recovery.plist"
    record.write_bytes(pending.encode())
    record.chmod(0o600)
    assert command("service", "stop", expected=1)["status"] == "recovery-required"
    assert agent.plist.read_bytes() == plist
    assert record.read_bytes() == pending.encode()
    assert launch_control.disabled and not launch_control.bootstraps


def test_same_pid_with_different_start_cannot_certify_health(
    project, tmp_path, launch_control, monkeypatch
):
    _, ledger, command = project
    wheel, digest = _wheel(tmp_path, "incarnation")
    interpreter = Path(sys._base_executable).resolve(strict=True)
    command(
        "service",
        "install",
        "--wheel",
        wheel,
        "--wheel-sha256",
        digest,
        "--interpreter",
        interpreter,
    )
    agent = install._Agent(ledger, launch_control)
    program = launch_control.loaded.program
    runtime = install._runtime_for(agent, program)
    process = install._process_identity(launch_control.loaded.pid)
    changed = replace(process, started=process.started + timedelta(microseconds=1))
    inspections = iter([process, changed])
    monkeypatch.setattr(launch_control, "process", lambda pid: next(inspections))
    assert (
        agent.healthy(runtime, agent.read(), datetime.now(UTC) - timedelta(seconds=15))
        is None
    )


def test_backup_refuses_output_inside_replaceable_store(project):
    from aitm_usage.backup import BackupError, backup

    _, ledger, _ = project
    directory = ledger.database_path.parent / "nested-backup"
    with pytest.raises(BackupError):
        backup(ledger, directory)
    assert not directory.exists()


def test_backup_refuses_store_through_physical_path_alias(project):
    from aitm_usage.backup import BackupError, backup
    from aitm_usage.ledger import _validated_path

    _, ledger, _ = project
    store = ledger.database_path.parent
    alias = Path("/System/Volumes/Data") / store.relative_to("/")
    if not alias.is_dir() or not alias.samefile(store) or alias == store:
        pytest.skip("The host does not expose the matching APFS firmlink path")
    _validated_path(alias, directory=True)
    with pytest.raises(BackupError, match="overlaps"):
        backup(ledger, alias / "nested-backup")
    assert not (store / "nested-backup").exists()


def test_restore_preserves_backup_inside_replaceable_store(project, tmp_path):
    from aitm_usage.backup import BackupError, backup, restore

    _, ledger, _ = project
    bundle = tmp_path / "backup"
    backup(ledger, bundle)
    inside = ledger.database_path.parent / "nested-backup"
    bundle.rename(inside)
    before = _bundle_bytes(inside)
    with pytest.raises(BackupError):
        restore(inside, ledger.root, ledger.identity)
    assert _bundle_bytes(inside) == before


def test_prune_preserves_nested_recovery_material(
    project, tmp_path, launch_control, monkeypatch
):
    from aitm_usage.backup import backup

    _, ledger, command = project
    wheel, digest = _wheel(tmp_path, "prune")
    interpreter = Path(sys._base_executable).resolve(strict=True)
    runtime = install._prepare(ledger, install._wheel(wheel, digest), interpreter)
    version_dir = runtime.executable.parents[2]
    bundle = version_dir / "backup"
    backup(ledger, bundle)
    arguments = ("service", "prune", "--version", "0.1.0", "--wheel-sha256", digest)
    before = _bundle_bytes(bundle)
    assert (
        command(*arguments, "--backup", bundle, expected=1)["status"] == "prune-failed"
    )
    assert _bundle_bytes(bundle) == before
    external = tmp_path / "external"
    bundle.rename(external)
    retained = install._wheel_path(ledger, "0.1.0", digest)
    inside = version_dir / retained.name
    retained.rename(inside)
    monkeypatch.setattr(install, "_wheel_path", lambda *args: inside)
    assert (
        command(*arguments, "--backup", external, expected=1)["status"]
        == "prune-failed"
    )
    assert inside.exists() and runtime.executable.exists()
