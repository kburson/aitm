"""Scoped producer admission and the mixed monitor inbox."""

import json
import os
import shutil
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from monitor_inbox_cases import MonitorInboxFiles

from aitm_usage import cli, monitor_control, monitor_registry, scope_admission
from aitm_usage import ledger as ledger_module
from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.monitor_control import ControlInbox, ScopeInboxReader
from aitm_usage.monitor_registry import (
    AnchorRequest,
    ControlCommand,
    ControlStatus,
    ProjectRegistrationRequest,
    RegisteredProject,
    Registry,
    RegistryView,
    _PhysicalDirectory,
    _ServiceEvidence,
)
from aitm_usage.monitor_scope import Scope
from aitm_usage.scope_admission import MarkRequest

PROJECT, GRANT, COMMAND, CONTROL = (UUID(int=i) for i in range(1, 5))
NOW = datetime(2026, 11, 10, tzinfo=UTC)


@pytest.fixture(autouse=True)
def isolated_writer_guard(request, monkeypatch):
    if "tmp_path" in request.fixturenames:
        tmp_path = request.getfixturevalue("tmp_path")
        monkeypatch.setattr(
            "aitm_usage.ledger._control_root", lambda: tmp_path / "control"
        )


def _mark_document():
    return {
        "command_id": str(COMMAND),
        "grant_id": str(GRANT),
        "scope": {"project_id": str(PROJECT)},
    }


def _request_file(tmp_path):
    path = tmp_path / "scope.json"
    path.write_text(json.dumps(_mark_document()))
    path.chmod(0o600)
    return path


def _cli(monkeypatch, path):
    monkeypatch.setattr(
        sys,
        "argv",
        ["aitm-usage", "monitor", "scope", "mark", "--request", str(path), "--json"],
    )
    return cli.main()


def test_scope_cli_refuses_uninitialized_admission_without_creating_state(
    monkeypatch, capsys
):
    root = Path("/fixture/missing-monitor")
    path = Path("/fixture/scope.json")
    exists = Mock(return_value=False)
    owner_document = Mock(return_value=_mark_document())
    pin = Mock(side_effect=AssertionError("Missing admission reached a directory pin"))
    publish = Mock(side_effect=AssertionError("Missing admission reached publication"))
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    monkeypatch.setattr(cli, "version", lambda _: "0.1.0")
    monkeypatch.setattr(monitor_control, "_owner_document", owner_document)
    monkeypatch.setattr(scope_admission, "_path_exists", exists)
    monkeypatch.setattr(scope_admission, "_pin_directory", pin)
    monkeypatch.setattr(ControlInbox, "publication", publish)

    assert _cli(monkeypatch, path) == 1
    assert json.loads(capsys.readouterr().out) == {
        "command_id": str(COMMAND),
        "status": "unavailable",
    }
    owner_document.assert_called_once_with(path)
    exists.assert_called_once_with(root)
    pin.assert_not_called()
    publish.assert_not_called()


def test_scope_witness_renewal_preserves_exact_bytes_and_mixed_control_drain(
    monkeypatch, capsys
):
    state, anchor = _admission_control_files(monkeypatch)
    writer, inbox = state.writer, state.inbox
    _, reader, request = _admit_mark(state, monkeypatch, advertise=False)
    path = state.root / "mark-input.json"
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: state.root)
    monkeypatch.setattr(
        monitor_control, "_owner_document", {path: _mark_document()}.__getitem__
    )
    monkeypatch.setattr(cli, "version", lambda _: "0.1.0")
    original_registry = state.files[state.root][monitor_registry._STATE_FILE]
    name = f"{COMMAND}.json"
    assert _cli(monkeypatch, path) == 1
    assert json.loads(capsys.readouterr().out) == {
        "command_id": str(COMMAND),
        "status": "unavailable",
    }
    assert not state.inbox_files
    reader.advertise(reader.probe(request))
    assert _cli(monkeypatch, path) == 0
    assert capsys.readouterr().out == (
        f'{{"command_id": "{COMMAND}", "status": "queued"}}\n'
    )
    original = state.inbox_files[name]
    monkeypatch.setattr(
        monitor_control, "_scope_now", lambda: NOW + timedelta(seconds=10)
    )
    reader.advertise(reader.probe(request))
    assert state.files[state.root][monitor_registry._STATE_FILE] == original_registry
    assert _cli(monkeypatch, path) == 0
    assert state.inbox_files[name] == original
    assert str(PROJECT) in original.decode()

    control = ControlCommand(CONTROL, AnchorRequest(PROJECT, anchor))
    inbox.enqueue(control)
    expected = {
        "command": {
            "command_id": str(CONTROL),
            "format": control.format,
            "payload": {"project_id": str(PROJECT), "anchor": anchor},
        },
        "order": 2,
    }
    assert (
        state.inbox_files[f"{CONTROL}.json"]
        == json.dumps(expected, sort_keys=True, separators=(",", ":")).encode()
    )
    with inbox.publication() as locked:
        (proposal,) = reader.iter_verified(locked)
    assert proposal.command_id == COMMAND
    (applied,) = writer.apply_pending(inbox, writer.lease, None)
    assert (applied.command_id, applied.status) == (CONTROL, ControlStatus.APPLIED)
    assert state.inbox_files == {name: original}
    assert writer.command_status(COMMAND) is None


@pytest.fixture
def ready(tmp_path, monkeypatch):
    root = tmp_path / "monitor"
    ledger = Ledger.initialize(tmp_path / "project", PROJECT)
    inbox = ControlInbox(root)
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    monkeypatch.setattr(monitor_control, "_scope_now", lambda: NOW)
    with Registry(root).writer() as writer:
        writer.register_project(
            ProjectRegistrationRequest(PROJECT, str(ledger.root), "Project")
        )
        writer.source_evidence()
        reader = ScopeInboxReader(writer, inbox)
        reader.register(GRANT, PROJECT, ("mark",))
        request = MarkRequest(COMMAND, GRANT, Scope(PROJECT))
        reader.advertise(reader.probe(request))
        yield writer, inbox, reader, request


@pytest.fixture
def admission_policy(monkeypatch):
    state = MonitorInboxFiles(monkeypatch, PROJECT)
    return _admit_mark(state, monkeypatch)


def _admit_mark(state, monkeypatch, *, advertise=True):
    monkeypatch.setattr(monitor_control, "_scope_now", lambda: NOW)
    reader = ScopeInboxReader(state.writer, state.inbox)
    reader.register(GRANT, PROJECT, ("mark",))
    request = MarkRequest(COMMAND, GRANT, Scope(PROJECT))
    if advertise:
        reader.advertise(reader.probe(request))
    return state, reader, request


@pytest.fixture
def admission_control_policy(monkeypatch):
    state, anchor = _admission_control_files(monkeypatch)
    return (*_admit_mark(state, monkeypatch), anchor)


def _admission_control_files(monkeypatch):
    root = Path("/fixture/monitor")
    state_directory = _PhysicalDirectory("/fixture/project", (1, 10))
    anchor = _PhysicalDirectory("/fixture/checkout", (1, 11))
    directories = {directory.path: directory for directory in (state_directory, anchor)}
    evidence = _ServiceEvidence(b"a" * 32)
    writer = Registry(root, Mock())
    monkeypatch.setattr(writer, "source_evidence", lambda: evidence)
    monkeypatch.setattr(
        monitor_registry, "_directory", lambda path, **_: directories[path]
    )
    ancestors = {Path("/"): (1, 1), Path("/fixture"): (1, 9)}
    monkeypatch.setattr(monitor_registry, "_identity", ancestors.__getitem__)
    initial = RegistryView(
        projects=(
            RegisteredProject(PROJECT, state_directory, "Project", None, (), None),
        ),
        source_key_id=evidence.key_id,
    )
    state = MonitorInboxFiles(monkeypatch, PROJECT, writer=writer, initial_view=initial)
    return state, anchor.path


def test_witness_issuance_requires_exact_capability_from_same_reader(admission_policy):
    state, reader, request = admission_policy
    proof = reader.probe(request)
    with pytest.raises(LedgerError):
        reader.advertise(replace(proof))
    with pytest.raises(LedgerError):
        ScopeInboxReader(state.writer, state.inbox).advertise(proof)
    reader.advertise(proof)
    with pytest.raises(LedgerError):
        reader.advertise(proof)


@pytest.mark.parametrize("offset", [60, 61, -6])
def test_stale_or_future_witness_cannot_publish(admission_policy, offset, monkeypatch):
    state, _, request = admission_policy
    monkeypatch.setattr(
        monitor_control, "_scope_now", lambda: NOW + timedelta(seconds=offset)
    )
    with pytest.raises(LedgerError):
        state.inbox.enqueue_scope(request)
    assert not state.inbox_files


def test_revocation_winning_between_lookup_and_publish_refuses(
    admission_policy, monkeypatch
):
    state, reader, request = admission_policy
    preliminary = monitor_control.preliminary_grant

    def revoke_after_lookup(*args):
        admitted = preliminary(*args)
        reader.revoke(GRANT)
        return admitted

    monkeypatch.setattr(monitor_control, "preliminary_grant", revoke_after_lookup)
    with pytest.raises(LedgerError):
        state.inbox.enqueue_scope(request)
    assert not state.inbox_files
    with pytest.raises(ConflictError):
        reader.register(GRANT, PROJECT, ("mark",))
    reader.register(GRANT, PROJECT, ("mark",), generation=2)


def test_copied_account_and_wrong_project_do_not_grant_authority(ready, tmp_path):
    _, inbox, _, request = ready
    other = tmp_path / "copied-monitor"
    shutil.copytree(inbox.root, other)
    with pytest.raises(LedgerError):
        ControlInbox(other).enqueue_scope(request)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(replace(request, scope=Scope(CONTROL)))
    assert not tuple(other.glob("inbox/*.json"))
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_scope_capacity_and_cross_format_conflicts_leave_controls_available(
    admission_control_policy, monkeypatch
):
    state, _, request, anchor = admission_control_policy
    writer, inbox = state.writer, state.inbox
    monkeypatch.setattr(monitor_control, "_MAX_SCOPE_PENDING", 1)
    assert inbox.enqueue_scope(request)
    assert inbox.enqueue_scope(request)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(replace(request, command_id=UUID(int=17)))
    control_payload = AnchorRequest(PROJECT, anchor)
    with pytest.raises(ConflictError):
        inbox.enqueue(ControlCommand(COMMAND, control_payload))
    inbox.enqueue(ControlCommand(CONTROL, control_payload))
    with pytest.raises(ConflictError):
        inbox.enqueue_scope(replace(request, command_id=CONTROL))
    (receipt,) = writer.apply_pending(inbox, writer.lease, None)
    assert (receipt.command_id, receipt.status) == (CONTROL, ControlStatus.APPLIED)


@pytest.mark.parametrize("bad_seal", ["f" * 64, "not-a-mac"])
def test_invalid_scope_seal_cannot_block_unrelated_control(
    admission_control_policy, bad_seal
):
    state, reader, mark, anchor = admission_control_policy
    writer, inbox = state.writer, state.inbox
    name = f"{COMMAND}.json"
    assert inbox.enqueue_scope(mark)
    with inbox.publication() as locked:
        (original,) = reader.iter_verified(locked)
    assert original.body.request == mark and original.seal != bad_seal
    tampered = json.loads(state.inbox_files[name])
    tampered["command"]["seal"] = bad_seal
    data = json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode()
    state.inbox_files[name] = data
    inbox.enqueue(ControlCommand(CONTROL, AnchorRequest(PROJECT, anchor)))
    with (
        inbox.publication() as locked,
        pytest.raises(LedgerError, match="Scope envelope seal does not match"),
    ):
        tuple(reader.iter_verified(locked))
    (receipt,) = writer.apply_pending(inbox, writer.lease, None)
    assert (receipt.command_id, receipt.status) == (CONTROL, ControlStatus.APPLIED)
    assert state.inbox_files == {name: data}


def test_explicit_cli_no_abbreviations_or_separate_request_id(monkeypatch):
    path = "/fixture/scope.json"
    owner_document = Mock(
        side_effect=AssertionError("invalid arguments read the request")
    )
    monkeypatch.setattr(monitor_control, "_owner_document", owner_document)
    for args in (
        ("--req", path),
        ("--request", path, "--request-id", str(COMMAND)),
    ):
        monkeypatch.setattr(
            sys, "argv", ["aitm-usage", "monitor", "scope", "mark", *args]
        )
        with pytest.raises(SystemExit) as stopped:
            cli.main()
        assert stopped.value.code == 2
    owner_document.assert_not_called()


def test_replaced_project_ledger_key_does_not_preserve_grant(ready, tmp_path):
    from aitm_usage.ledger import STORE_NAME

    _, inbox, _, request = ready
    replacement = Ledger.initialize(tmp_path / "replacement", PROJECT)
    state = tmp_path / "project"
    (state / STORE_NAME).rename(tmp_path / "old-store")
    (replacement.root / STORE_NAME).rename(state / STORE_NAME)
    assert Ledger.open(state, PROJECT).identity == replacement.identity
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_scope_cli_handoff_and_disposition_with_distinct_pinned_requests(
    monkeypatch, capsys
):
    from test_ledger import _memory_ledger

    from aitm_usage.scope_admission import DispositionRequest, HandoffRequest
    from aitm_usage.types import _encode

    root = Path("/fixture/monitor")
    origin = _PhysicalDirectory("/fixture/origin", (1, 10))
    destination = _PhysicalDirectory("/fixture/destination", (1, 11))
    evidence = _ServiceEvidence(b"a" * 32)
    writer = Registry(root, Mock())
    monkeypatch.setattr(writer, "source_evidence", lambda: evidence)
    initial = RegistryView(
        projects=(
            RegisteredProject(PROJECT, origin, "Origin", None, (), None),
            RegisteredProject(CONTROL, destination, "Destination", None, (), None),
        ),
        source_key_id=evidence.key_id,
    )
    state = MonitorInboxFiles(monkeypatch, PROJECT, writer=writer, initial_view=initial)
    target = replace(
        _memory_ledger(ledger_module, CONTROL, b"t" * 32), root=Path(destination.path)
    )
    state.identities[destination.path] = destination
    state.ensure(target.root)
    ledgers = {
        (state.ledger.root, PROJECT): state.ledger,
        (target.root, CONTROL): target,
    }
    monkeypatch.setattr(Ledger, "open", lambda path, project: ledgers[path, project])
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)

    handoff = HandoffRequest(COMMAND, GRANT, PROJECT, Scope(CONTROL), 0)
    dispose = DispositionRequest(UUID(int=9), GRANT, PROJECT, COMMAND, True)
    requests = (("handoff", handoff), ("dispose", dispose))
    inputs = {
        Path(f"/fixture/{action}.json"): (fd, _encode(request, type(request)).encode())
        for fd, (action, request) in enumerate(requests, start=20)
    }
    payloads = dict(inputs.values())

    def validate_path(path, *, directory):
        assert not directory
        return ((1, inputs[path][0]),)

    def open_input(path, flags):
        assert flags == os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        return inputs[path][0]

    def open_descriptor(fd, mode):
        assert mode == "rb"
        return BytesIO(payloads[fd])

    def pin_input(path, fd, directory, identities):
        assert fd == inputs[path][0]
        assert identities == validate_path(path, directory=directory)
        return SimpleNamespace(check=Mock())

    host = monitor_control.os
    monkeypatch.setattr(
        monitor_control,
        "os",
        SimpleNamespace(
            **vars(host),
            O_RDONLY=os.O_RDONLY,
            O_NOFOLLOW=os.O_NOFOLLOW,
            O_NONBLOCK=os.O_NONBLOCK,
            open=open_input,
            fdopen=open_descriptor,
        ),
    )
    monkeypatch.setattr(monitor_control, "_validated_path", validate_path)
    monkeypatch.setattr(monitor_control, "_PinnedPath", pin_input)
    reader = ScopeInboxReader(writer, state.inbox)
    reader.register(GRANT, PROJECT, ("handoff", "dispose"))
    reader.advertise(reader.probe(handoff))
    for action, request in requests:
        path = Path(f"/fixture/{action}.json")
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "aitm-usage",
                "monitor",
                "scope",
                action,
                "--request",
                str(path),
                "--json",
            ],
        )
        assert cli.main() == 0
        assert capsys.readouterr().out == (
            f'{{"command_id": "{request.command_id}", "status": "queued"}}\n'
        )

    with state.inbox.publication() as locked:
        assert tuple(item.body.request for item in reader.iter_verified(locked)) == (
            handoff,
            dispose,
        )


def test_replayed_active_grant_file_cannot_reverse_revocation(admission_policy):
    state, reader, request = admission_policy
    commits = state.grant_files(GRANT)
    before = commits[max(commits)]
    reader.revoke(GRANT)
    commits[max(commits)] = before
    with pytest.raises(LedgerError):
        state.inbox.enqueue_scope(request)
    assert not state.inbox_files


def test_witness_expiring_during_queue_preparation_cannot_publish(
    admission_policy, monkeypatch
):
    state, _, request = admission_policy
    pending = monitor_control._pending

    def elapsed(directory):
        result = pending(directory)
        monkeypatch.setattr(
            monitor_control, "_scope_now", lambda: NOW + timedelta(seconds=60)
        )
        return result

    monkeypatch.setattr(monitor_control, "_pending", elapsed)
    with pytest.raises(LedgerError):
        state.inbox.enqueue_scope(request)
    assert not state.inbox_files


def test_withdrawn_witness_refuses_retry_then_renews_same_exact_proposal(
    admission_policy,
):
    state, reader, request = admission_policy
    inbox = state.inbox
    assert inbox.enqueue_scope(request)
    publication = f"{COMMAND}.json"
    original = state.inbox_files[publication]
    reader.withdraw(GRANT)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert state.inbox_files[publication] == original
    reader.advertise(reader.probe(request))
    assert inbox.enqueue_scope(request)
    assert state.inbox_files[publication] == original


def test_scope_credential_cannot_authenticate_reader_witness(admission_policy):
    from aitm_usage.scope_admission import _witness_tag, _write_grant, stored_grant

    state, _, request = admission_policy
    writer, inbox = state.writer, state.inbox
    record = stored_grant(inbox.root, GRANT)
    assert record is not None and record.witness is not None
    witness = record.witness
    forged = replace(
        witness,
        tag=_witness_tag(
            bytes.fromhex(record.credential),
            record,
            witness.issued,
            witness.expires,
            witness.probe_digest,
        ),
    )
    with inbox.publication():
        _write_grant(writer, replace(record, witness=forged), record)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not state.inbox_files


def test_modified_committed_grant_cannot_mint_producer_authority(admission_policy):
    state, _, request = admission_policy
    grants = state.grant_files(GRANT)
    active = max(grants)
    data = json.loads(grants[active])
    data["record"]["grant"]["actions"] = ["dispose", "mark"]
    data["record"]["credential"] = "a" * 64
    grants[active] = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    with pytest.raises(LedgerError):
        state.inbox.enqueue_scope(request)
    assert not state.inbox_files


def test_scope_request_refuses_noncanonical_selectors(monkeypatch, capsys):
    path = Path("/fixture/scope.json")
    default_root = Mock(
        side_effect=AssertionError("invalid request opened monitor state")
    )
    monkeypatch.setattr(monitor_registry, "default_monitor_root", default_root)
    owner_document = Mock()
    monkeypatch.setattr(monitor_control, "_owner_document", owner_document)
    data = {
        "command_id": str(COMMAND),
        "grant_id": str(GRANT),
        "scope": {"project_id": str(PROJECT)},
    }
    for field, value in (("command_id", COMMAND), ("grant_id", GRANT)):
        for noncanonical in (value.hex, value.urn, "{" + str(value) + "}"):
            owner_document.return_value = {**data, field: noncanonical}
            assert _cli(monkeypatch, path) == 1
            assert json.loads(capsys.readouterr().out) == {"status": "unavailable"}
    default_root.assert_not_called()


def test_project_substitution_during_preparation_cannot_publish(
    request, tmp_path, monkeypatch, capsys
):
    root = tmp_path / "monitor"
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    assert _cli(monkeypatch, _request_file(tmp_path)) == 1
    assert json.loads(capsys.readouterr().out) == {
        "command_id": str(COMMAND),
        "status": "unavailable",
    }
    assert not root.exists()

    _, inbox, _, mark = request.getfixturevalue("ready")
    pending = monitor_control._pending
    state = tmp_path / "project"

    def substituted(directory):
        result = pending(directory)
        state.rename(tmp_path / "old-project")
        shutil.copytree(tmp_path / "old-project", state)
        return result

    monkeypatch.setattr(monitor_control, "_pending", substituted)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(mark)
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_expiry_after_publication_withholds_ack_and_retry_reuses_exact_bytes(
    admission_policy, monkeypatch
):
    state, reader, request = admission_policy
    inbox = state.inbox
    publish = monitor_control._publish

    def elapsed(*args, **kwargs):
        committed = publish(*args, **kwargs)
        monkeypatch.setattr(
            monitor_control, "_scope_now", lambda: NOW + timedelta(seconds=60)
        )
        return committed

    monkeypatch.setattr(monitor_control, "_publish", elapsed)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    publication = f"{COMMAND}.json"
    original = state.inbox_files[publication]
    monkeypatch.setattr(monitor_control, "_publish", publish)
    reader.advertise(reader.probe(request))
    assert inbox.enqueue_scope(request)
    assert state.inbox_files[publication] == original


def test_reader_capability_cannot_restore_withdrawn_admission(admission_policy):
    state, reader, request = admission_policy
    inbox = state.inbox
    other = ScopeInboxReader(state.writer, inbox)
    old = reader.probe(request)
    other.withdraw(GRANT)
    with pytest.raises(LedgerError, match="proof is unavailable"):
        reader.advertise(old)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    other.advertise(other.probe(request))
    assert inbox.enqueue_scope(request)


def test_adopted_scope_shape_refuses_separate_source_anchor_command():
    from aitm_usage.monitor_registry import _ServiceEvidence
    from aitm_usage.scope_admission import adopted_request
    from aitm_usage.types import InboxCommand, SourceAnchorCommand

    evidence = _ServiceEvidence(b"scope-admission-test")
    command = InboxCommand(
        COMMAND,
        PROJECT,
        SourceAnchorCommand(
            COMMAND,
            PROJECT,
            evidence.pseudonymize("test", "configuration"),
            evidence.pseudonymize("test", "anchor"),
        ),
    )
    with pytest.raises(ValueError, match="legacy command"):
        adopted_request(command, UUID(int=92), None)


def test_typed_adopted_producer_cannot_republish_durable_legacy_command(
    monkeypatch, capsys
):
    from test_scope_legacy import ADOPTION, _memory_legacy

    from aitm_usage.scope_admission import adopted_request, legacy_grant_id
    from aitm_usage.types import (
        CommandReceipt,
        InboxCommand,
        ItemKey,
        ItemKind,
        ItemParent,
        MarkerDisposition,
    )

    memory = _memory_legacy(monkeypatch, capsys, monitor_registered=True)
    ledger = memory.ledger
    project = ledger.identity.project_id
    payload = ItemParent(
        COMMAND, project, ItemKey(ItemKind.ISSUE, 1), ItemKey(ItemKind.ISSUE, 2)
    )
    command = InboxCommand(COMMAND, project, payload)
    stored = CommandReceipt(
        command, ledger.validate_command(command), MarkerDisposition.ACCEPTED
    )
    memory.store_receipt(stored)
    memory.publish_adoption()
    inbox = memory.monitor.inbox
    reader = ScopeInboxReader(memory.monitor.writer, inbox)
    reader.register(
        legacy_grant_id(project, ADOPTION), project, ("legacy",), adoption_id=ADOPTION
    )
    request = adopted_request(command, ADOPTION, None)
    reader.advertise(reader.probe(request))

    with pytest.raises(LedgerError, match="legacy command already has a receipt"):
        inbox.enqueue_scope(request)
    assert not memory.monitor.inbox_files
    assert not memory.inbox
    assert ledger.command_receipt(command) == stored
