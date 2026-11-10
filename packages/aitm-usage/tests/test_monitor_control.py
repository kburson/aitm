import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import pytest

from aitm_usage import cli, ledger, monitor_control, monitor_registry
from aitm_usage.monitor_registry import CaptureChange, ControlCommand, Registry

PROJECT = UUID("1a65f88f-3825-4a7b-9689-c7fbd9eaf36d")
SOURCE = UUID("bc6bb0a1-f29d-4ca6-9cf1-65b4b645d318")
REQUEST = UUID("c586044a-d0b0-4200-a226-c129344af29f")


def _run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["aitm-usage", "monitor", *args, "--json"])
    return cli.main()


def _capture(action):
    return ("capture", action, "--project", str(PROJECT), "--source", str(SOURCE))


def _status(monkeypatch):
    return _run(monkeypatch, "command", "status", "--id", str(REQUEST))


def test_monitor_cli_queues_capture_exactly_once_and_status_reads_it(
    monitor, monkeypatch, capsys
):
    args = (*_capture("enable"), "--request-id", str(REQUEST))
    assert _run(monkeypatch, *args) == 0
    queued = {"command_id": str(REQUEST), "status": "queued"}
    assert json.loads(capsys.readouterr().out) == queued
    assert _run(monkeypatch, *args) == 0
    assert json.loads(capsys.readouterr().out) == queued
    assert _status(monkeypatch) == 0
    assert json.loads(capsys.readouterr().out) == queued
    assert len(list(monitor.root.glob("inbox/*.json"))) == 1
    assert _run(monkeypatch, *_capture("disable"), "--request-id", str(REQUEST)) == 1
    assert json.loads(capsys.readouterr().out) == {
        "command_id": str(REQUEST),
        "status": "command-conflict",
    }


@pytest.fixture
def monitor(tmp_path, monkeypatch):
    root = tmp_path / "monitor"
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    return monitor_control.ControlInbox(root)


def test_command_status_missing_root_is_unavailable_and_does_not_create_it(
    monitor, monkeypatch, capsys
):
    assert _status(monkeypatch) == 1
    assert json.loads(capsys.readouterr().out) == {
        "command_id": str(REQUEST),
        "status": "unavailable",
    }
    assert not monitor.root.exists()


def test_exact_enqueues_from_concurrent_producers_converge(monitor):
    command = ControlCommand(REQUEST, CaptureChange(PROJECT, SOURCE, True))
    with ThreadPoolExecutor(max_workers=4) as workers:
        receipts = list(workers.map(monitor.enqueue, [command] * 8))

    assert len(set(receipts)) == 1
    assert receipts[0].status.value == "queued"
    with monitor.publication() as locked:
        assert list(monitor.iter_pending(locked)) == [command]


@pytest.mark.parametrize(
    "unsafe", ["mode", "symlink", "hardlink", "duplicate", "extra"]
)
def test_project_cli_rejects_unsafe_or_untyped_owner_config(
    unsafe, monitor, tmp_path, monkeypatch, capsys
):
    config = tmp_path / "private-config.json"
    private_state = str(tmp_path / "secret-state")
    document = {
        "project_id": str(PROJECT),
        "state_dir": private_state,
        "display_name": "owner",
    }
    raw = json.dumps(document)
    if unsafe == "duplicate":
        raw = raw[:-1] + ', "display_name": "another"}'
    if unsafe == "extra":
        raw = json.dumps({**document, "unexpected": "private"})
    config.write_text(raw)
    config.chmod(0o644 if unsafe == "mode" else 0o600)
    if unsafe in {"symlink", "hardlink"}:
        target = config
        config = tmp_path / "alias.json"
        if unsafe == "symlink":
            config.symlink_to(target)
        else:
            config.hardlink_to(target)

    assert _run(monkeypatch, "project", "register", "--config", str(config)) == 1
    output = capsys.readouterr()
    assert json.loads(output.out)["status"] == "invalid-config"
    assert str(config) not in output.out + output.err
    assert private_state not in output.out + output.err
    assert not monitor.root.exists()


@pytest.mark.parametrize(
    "args",
    [("capture", "disable"), ("project", "anchor", "add")],
)
def test_legacy_global_state_and_monitor_project_flags_cannot_mix(
    args, monitor, tmp_path, monkeypatch, capsys
):
    inputs = (
        ("--source", str(SOURCE))
        if args[0] == "capture"
        else ("--config", str(tmp_path / "config.json"))
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aitm-usage",
            "--project",
            str(tmp_path / "legacy"),
            "monitor",
            *args,
            "--project",
            str(PROJECT),
            *inputs,
        ],
    )
    with pytest.raises(SystemExit) as rejected:
        cli.main()
    assert rejected.value.code == 2
    assert "cannot combine" in capsys.readouterr().err
    assert not monitor.root.exists()


def test_pending_commands_keep_enqueue_order_when_request_ids_sort_backwards(monitor):
    enable = ControlCommand(
        UUID("ffffffff-ffff-4fff-8fff-ffffffffffff"),
        CaptureChange(PROJECT, SOURCE, True),
    )
    disable = ControlCommand(
        UUID("00000000-0000-4000-8000-000000000001"),
        CaptureChange(PROJECT, SOURCE, False),
    )
    monitor.enqueue(enable)
    monitor.enqueue(disable)

    with monitor.publication() as locked:
        assert list(monitor.iter_pending(locked)) == [enable, disable]


def _private_config(path, payload):
    path.write_text(json.dumps(payload))
    path.chmod(0o600)
    return path


def _registration(tmp_path, monkeypatch):
    state = tmp_path / "private-project-state"
    monkeypatch.setattr(ledger, "_control_root", lambda: tmp_path / "control")
    ledger.Ledger.initialize(state, PROJECT)
    return _private_config(
        tmp_path / "private-owner-declaration.json",
        {
            "project_id": str(PROJECT),
            "state_dir": str(state),
            "display_name": "Private project",
        },
    )


def test_normal_cli_reports_durable_application_and_retries_after_cleanup(
    monitor, tmp_path, monkeypatch, capsys
):
    config = _registration(tmp_path, monkeypatch)
    args = (
        "project",
        "register",
        "--config",
        str(config),
        "--request-id",
        str(REQUEST),
    )
    assert _run(monkeypatch, *args) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "queued"
    registry = Registry(monitor.root)
    with registry.writer() as writer:
        writer.apply_pending(monitor, writer.lease, None)
        # Status also works while the coordinator is already held.
        assert _status(monkeypatch) == 0

    applied = {"command_id": str(REQUEST), "status": "applied"}
    assert json.loads(capsys.readouterr().out) == applied
    assert not list(monitor.root.glob("inbox/*.json"))
    assert _run(monkeypatch, *args) == 0
    assert json.loads(capsys.readouterr().out) == applied
    assert not list(monitor.root.glob("inbox/*.json"))
    assert _run(monkeypatch, *_capture("disable"), "--request-id", str(REQUEST)) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "command-conflict"


def test_status_rereads_durable_receipt_when_queue_is_retired_mid_lookup(
    monitor, tmp_path, monkeypatch, capsys
):
    config = _registration(tmp_path, monkeypatch)
    assert (
        _run(
            monkeypatch,
            "project",
            "register",
            "--config",
            str(config),
            "--request-id",
            str(REQUEST),
        )
        == 0
    )
    capsys.readouterr()
    registry = Registry(monitor.root)
    read_private = monitor_control._read_private

    def read_after_retirement(directory, name):
        monkeypatch.setattr(monitor_control, "_read_private", read_private)
        with registry.writer() as writer:
            writer.apply_pending(monitor, writer.lease, None)
        # Model the reader's open descriptor surviving an unlink between
        # open() and stat() on the queued name.
        raise FileNotFoundError

    monkeypatch.setattr(monitor_control, "_read_private", read_after_retirement)
    assert _status(monkeypatch) == 0
    assert json.loads(capsys.readouterr().out) == {
        "command_id": str(REQUEST),
        "status": "applied",
    }


def test_capture_without_request_id_returns_a_stable_retry_key(
    monitor, monkeypatch, capsys
):
    assert _run(monkeypatch, *_capture("disable")) == 0
    original = json.loads(capsys.readouterr().out)
    chosen = UUID(original["command_id"])
    assert chosen.version == 4
    assert _run(monkeypatch, *_capture("disable"), "--request-id", str(chosen)) == 0
    assert json.loads(capsys.readouterr().out) == original
    assert len(list(monitor.root.glob("inbox/*.json"))) == 1


def test_source_and_anchor_cli_queue_typed_owner_declarations(
    monitor, tmp_path, monkeypatch, capsys
):
    from aitm_usage.monitor_registry import AnchorRequest, SourceApprovalRequest

    source_root = str(tmp_path / "private-source-root")
    anchor_path = str(tmp_path / "private-anchor")
    approval = _private_config(
        tmp_path / "source.json",
        {
            "source_id": str(SOURCE),
            "provider": "codex",
            "surface": "codex-desktop-macos",
            "platform": "darwin",
            "architecture": "arm64",
            "client_version": "1.2.3",
            "format_version": 1,
            "root": source_root,
        },
    )
    anchor = _private_config(tmp_path / "anchor.json", {"anchor": anchor_path})
    assert _run(monkeypatch, "source", "approve", "--config", str(approval)) == 0
    approval_output = capsys.readouterr().out
    assert (
        _run(
            monkeypatch,
            "project",
            "anchor",
            "add",
            "--project",
            str(PROJECT),
            "--config",
            str(anchor),
        )
        == 0
    )
    anchor_output = capsys.readouterr().out

    with monitor.publication() as locked:
        commands = list(monitor.iter_pending(locked))
    assert commands == [
        ControlCommand(
            UUID(json.loads(approval_output)["command_id"]),
            SourceApprovalRequest(
                SOURCE,
                "codex",
                "codex-desktop-macos",
                "darwin",
                "arm64",
                "1.2.3",
                1,
                source_root,
            ),
        ),
        ControlCommand(
            UUID(json.loads(anchor_output)["command_id"]),
            AnchorRequest(PROJECT, anchor_path),
        ),
    ]
    assert source_root not in approval_output
    assert anchor_path not in anchor_output


def test_enqueues_and_reads_while_coordinator_is_held(monitor):
    command = ControlCommand(REQUEST, CaptureChange(PROJECT, SOURCE, True))
    registry = Registry(monitor.root)
    with ThreadPoolExecutor(max_workers=1) as worker, registry.writer():
        queued = worker.submit(monitor.enqueue, command).result(timeout=3)
        assert queued.status.value == "queued"
        assert worker.submit(monitor.status, REQUEST).result(timeout=3) == queued


def test_duplicate_order_prevents_drain(monitor):
    from aitm_usage.ledger import LedgerError

    enable = ControlCommand(REQUEST, CaptureChange(PROJECT, SOURCE, True))
    disable = ControlCommand(SOURCE, CaptureChange(PROJECT, SOURCE, False))
    monitor.enqueue(enable)
    monitor.enqueue(disable)
    path = monitor.root / "inbox" / f"{SOURCE}.json"
    pending = json.loads(path.read_text())
    pending["order"] = 1
    path.write_text(json.dumps(pending, sort_keys=True, separators=(",", ":")))

    with monitor.publication() as locked:
        with pytest.raises(LedgerError, match="Duplicate monitor publication order"):
            next(monitor.iter_pending(locked))
    assert len(list(monitor.root.glob("inbox/*.json"))) == 2


def test_retirement_refuses_changed_publication_bytes(monitor):
    from aitm_usage.ledger import ConflictError

    command = ControlCommand(REQUEST, CaptureChange(PROJECT, SOURCE, True))
    monitor.enqueue(command)
    path = monitor.root / "inbox" / f"{REQUEST}.json"
    with monitor.publication() as locked:
        (pending,) = monitor.iter_pending(locked)
        replacement = json.loads(path.read_text())
        replacement["order"] = 2
        changed = json.dumps(replacement, sort_keys=True, separators=(",", ":"))
        path.write_text(changed)
        with pytest.raises(ConflictError):
            monitor.discard(locked, pending)
    assert path.read_text() == changed


def test_status_fails_closed_when_queued_file_is_substituted(monitor):
    from aitm_usage.ledger import LedgerError

    command = ControlCommand(REQUEST, CaptureChange(PROJECT, SOURCE, True))
    monitor.enqueue(command)
    path = monitor.root / "inbox" / f"{REQUEST}.json"
    displaced = path.with_suffix(".old")
    path.rename(displaced)
    path.symlink_to(displaced)

    with pytest.raises(LedgerError):
        monitor.status(REQUEST)
    assert path.is_symlink()


def test_rejected_command_status_contains_no_owner_paths(
    monitor, tmp_path, monkeypatch, capsys
):
    config = _private_config(
        tmp_path / "private-invalid-project.json",
        {
            "project_id": str(PROJECT),
            "state_dir": str(tmp_path / "missing-private-project-state"),
            "display_name": "Private project",
        },
    )
    args = (
        "project",
        "register",
        "--config",
        str(config),
        "--request-id",
        str(REQUEST),
    )
    assert _run(monkeypatch, *args) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "queued"
    with Registry(monitor.root).writer() as writer:
        writer.apply_pending(monitor, writer.lease, None)

    assert _status(monkeypatch) == 0
    output = capsys.readouterr()
    assert json.loads(output.out) == {
        "command_id": str(REQUEST),
        "status": "rejected",
    }
    assert str(tmp_path) not in output.out + output.err


def test_restart_retires_exact_queue_entry_after_durable_commit(
    monitor, tmp_path, monkeypatch, capsys
):
    config = _registration(tmp_path, monkeypatch)
    args = (
        "project",
        "register",
        "--config",
        str(config),
        "--request-id",
        str(REQUEST),
    )
    assert _run(monkeypatch, *args) == 0
    capsys.readouterr()

    def interrupted_retirement(*args):
        raise RuntimeError("simulated exit after registry commit")

    with monkeypatch.context() as failed_process:
        failed_process.setattr(monitor, "discard", interrupted_retirement)
        with Registry(monitor.root).writer() as writer:
            with pytest.raises(RuntimeError, match="simulated exit"):
                writer.apply_pending(monitor, writer.lease, None)

    queue_entry = monitor.root / "inbox" / f"{REQUEST}.json"
    assert queue_entry.is_file()
    assert _status(monkeypatch) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "applied"
    assert _run(monkeypatch, *args) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "applied"

    recovered = Registry(monitor.root)
    recorded = recovered.view()
    assert [project.project_id for project in recorded.projects] == [PROJECT]
    assert [receipt.command_id for receipt in recorded.receipts] == [REQUEST]
    with recovered.writer() as writer:
        assert writer.apply_pending(monitor, writer.lease, None) == ()
    assert recovered.view() == recorded
    assert not queue_entry.exists()


def test_exact_retry_resyncs_a_publication_after_directory_sync_fails(
    monitor, monkeypatch
):
    command = ControlCommand(REQUEST, CaptureChange(PROJECT, SOURCE, True))
    entry = monitor.root / "inbox" / f"{REQUEST}.json"
    real_sync = os.fsync
    queue_syncs = 0

    def interrupted_once(fd):
        nonlocal queue_syncs
        if entry.exists() and os.path.samestat(os.fstat(fd), entry.parent.stat()):
            queue_syncs += 1
            if queue_syncs == 1:
                raise OSError("simulated directory sync failure")
        real_sync(fd)

    monkeypatch.setattr(os, "fsync", interrupted_once)
    with pytest.raises(ledger.LedgerError):
        monitor.enqueue(command)
    assert entry.is_file()
    assert monitor.enqueue(command).status.value == "queued"
    assert queue_syncs == 2
