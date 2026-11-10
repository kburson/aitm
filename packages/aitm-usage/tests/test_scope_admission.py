"""Scoped producer admission and the mixed monitor inbox."""

import json
import shutil
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from aitm_usage import cli, monitor_control, monitor_registry
from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.monitor_control import ControlInbox, ScopeInboxReader
from aitm_usage.monitor_registry import (
    AnchorRequest,
    ControlCommand,
    ProjectRegistrationRequest,
    Registry,
)
from aitm_usage.monitor_scope import Scope
from aitm_usage.scope_admission import MarkRequest

PROJECT, GRANT, COMMAND, CONTROL = (UUID(int=i) for i in range(1, 5))
NOW = datetime(2026, 11, 10, tzinfo=UTC)


def _request_file(tmp_path):
    path = tmp_path / "scope.json"
    path.write_text(
        json.dumps(
            {
                "command_id": str(COMMAND),
                "grant_id": str(GRANT),
                "scope": {"project_id": str(PROJECT)},
            }
        )
    )
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
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "monitor"
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    assert _cli(monkeypatch, _request_file(tmp_path)) == 1
    assert json.loads(capsys.readouterr().out) == {
        "command_id": str(COMMAND),
        "status": "unavailable",
    }
    assert not root.exists()


def test_scope_witness_renewal_preserves_exact_bytes_and_mixed_control_drain(
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "monitor"
    ledger = Ledger.initialize(tmp_path / "project", PROJECT)
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    inbox = ControlInbox(root)
    path = _request_file(tmp_path)
    request = MarkRequest(COMMAND, GRANT, Scope(PROJECT))
    anchor = tmp_path / "checkout"
    anchor.mkdir()
    monkeypatch.setattr(monitor_control, "_scope_now", lambda: NOW)
    with Registry(root).writer() as writer:
        writer.register_project(
            ProjectRegistrationRequest(PROJECT, str(ledger.root), "Project")
        )
        writer.source_evidence()
        registry_path = root / "registry-v1.json"
        original_registry = registry_path.read_bytes()
        reader = ScopeInboxReader(writer, inbox)
        reader.register(GRANT, PROJECT, ("mark",))
        assert _cli(monkeypatch, path) == 1
        assert json.loads(capsys.readouterr().out)["status"] == "unavailable"
        proof = reader.probe(request)
        reader.advertise(proof)
        assert _cli(monkeypatch, path) == 0
        assert capsys.readouterr().out == (
            f'{{"command_id": "{COMMAND}", "status": "queued"}}\n'
        )
        publication = root / "inbox" / f"{COMMAND}.json"
        original = publication.read_bytes()
        monkeypatch.setattr(
            monitor_control, "_scope_now", lambda: NOW + timedelta(seconds=10)
        )
        reader.advertise(reader.probe(request))
        assert registry_path.read_bytes() == original_registry
        assert _cli(monkeypatch, path) == 0
        assert publication.read_bytes() == original
        assert str(PROJECT) in original.decode()

        control = ControlCommand(CONTROL, AnchorRequest(PROJECT, str(anchor)))
        inbox.enqueue(control)
        expected = {
            "command": {
                "command_id": str(CONTROL),
                "format": control.format,
                "payload": {"project_id": str(PROJECT), "anchor": str(anchor)},
            },
            "order": 2,
        }
        assert (root / "inbox" / f"{CONTROL}.json").read_bytes() == json.dumps(
            expected, sort_keys=True, separators=(",", ":")
        ).encode()
        with inbox.publication() as locked:
            proposals = tuple(reader.iter_verified(locked))
        assert len(proposals) == 1
        assert proposals[0].command_id == COMMAND
        (applied,) = writer.apply_pending(inbox, writer.lease, None)
        assert applied.command_id == CONTROL
        assert applied.status == "applied"
        assert publication.read_bytes() == original
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


def test_witness_issuance_requires_exact_capability_from_same_reader(ready):
    writer, inbox, reader, request = ready
    proof = reader.probe(request)
    with pytest.raises(LedgerError):
        reader.advertise(replace(proof))
    with pytest.raises(LedgerError):
        ScopeInboxReader(writer, inbox).advertise(proof)
    reader.advertise(proof)
    with pytest.raises(LedgerError):
        reader.advertise(proof)


@pytest.mark.parametrize("offset", [60, 61, -6])
def test_stale_or_future_witness_cannot_publish(ready, offset, monkeypatch):
    _, inbox, _, request = ready
    monkeypatch.setattr(
        monitor_control, "_scope_now", lambda: NOW + timedelta(seconds=offset)
    )
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_revocation_winning_between_lookup_and_publish_refuses(ready, monkeypatch):
    _, inbox, reader, request = ready
    preliminary = monitor_control.preliminary_grant

    def revoke_after_lookup(*args):
        admitted = preliminary(*args)
        reader.revoke(GRANT)
        return admitted

    monkeypatch.setattr(monitor_control, "preliminary_grant", revoke_after_lookup)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not tuple(inbox.root.glob("inbox/*.json"))
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
    ready, tmp_path, monkeypatch
):
    writer, inbox, _, request = ready
    monkeypatch.setattr(monitor_control, "_MAX_SCOPE_PENDING", 1)
    assert inbox.enqueue_scope(request)
    assert inbox.enqueue_scope(request)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(replace(request, command_id=UUID(int=17)))
    anchor = tmp_path / "checkout"
    anchor.mkdir()
    control_payload = AnchorRequest(PROJECT, str(anchor))
    with pytest.raises(ConflictError):
        inbox.enqueue(ControlCommand(COMMAND, control_payload))
    inbox.enqueue(ControlCommand(CONTROL, control_payload))
    with pytest.raises(ConflictError):
        inbox.enqueue_scope(replace(request, command_id=CONTROL))
    assert tuple(
        item.command_id for item in writer.apply_pending(inbox, writer.lease, None)
    ) == (CONTROL,)


@pytest.mark.parametrize("bad_seal", ["f" * 64, "not-a-mac"])
def test_invalid_scope_seal_cannot_block_unrelated_control(ready, tmp_path, bad_seal):
    writer, inbox, reader, request = ready
    assert inbox.enqueue_scope(request)
    proposal = inbox.root / "inbox" / f"{COMMAND}.json"
    tampered = json.loads(proposal.read_bytes())
    tampered["command"]["seal"] = bad_seal
    proposal.write_bytes(
        json.dumps(tampered, sort_keys=True, separators=(",", ":")).encode()
    )
    anchor = tmp_path / "checkout"
    anchor.mkdir()
    inbox.enqueue(ControlCommand(CONTROL, AnchorRequest(PROJECT, str(anchor))))
    with inbox.publication() as locked, pytest.raises(LedgerError):
        tuple(reader.iter_verified(locked))
    assert tuple(
        item.command_id for item in writer.apply_pending(inbox, writer.lease, None)
    ) == (CONTROL,)
    assert proposal.exists()


def test_explicit_cli_no_abbreviations_or_separate_request_id(tmp_path, monkeypatch):
    for args in (
        ("--req", str(_request_file(tmp_path))),
        ("--request", str(_request_file(tmp_path)), "--request-id", str(COMMAND)),
    ):
        monkeypatch.setattr(
            sys, "argv", ["aitm-usage", "monitor", "scope", "mark", *args]
        )
        with pytest.raises(SystemExit) as stopped:
            cli.main()
        assert stopped.value.code == 2


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
    tmp_path, monkeypatch, capsys
):
    from aitm_usage.scope_admission import DispositionRequest, HandoffRequest
    from aitm_usage.types import _encode

    root = tmp_path / "monitor"
    inbox = ControlInbox(root)
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    handoff = HandoffRequest(COMMAND, GRANT, PROJECT, Scope(CONTROL), 0)
    dispose = DispositionRequest(UUID(int=9), GRANT, PROJECT, COMMAND, True)
    with Registry(root).writer() as writer:
        for project in (PROJECT, CONTROL):
            state = Ledger.initialize(tmp_path / f"project-{project}", project)
            writer.register_project(
                ProjectRegistrationRequest(project, str(state.root), "Project")
            )
        writer.source_evidence()
        reader = ScopeInboxReader(writer, inbox)
        reader.register(GRANT, PROJECT, ("handoff", "dispose"))
        reader.advertise(reader.probe(handoff))
        for action, request in (("handoff", handoff), ("dispose", dispose)):
            path = tmp_path / f"{action}.json"
            path.write_text(_encode(request, type(request)))
            path.chmod(0o600)
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

        with inbox.publication() as locked:
            assert tuple(
                item.body.request for item in reader.iter_verified(locked)
            ) == (
                handoff,
                dispose,
            )


def _active_grant_file(inbox):
    directory = inbox.root / "scope-admission-v1" / str(GRANT)
    return sorted(directory.glob("*.json"))[-1]


def test_replayed_active_grant_file_cannot_reverse_revocation(ready):
    _, inbox, reader, request = ready
    before = _active_grant_file(inbox).read_bytes()
    reader.revoke(GRANT)
    _active_grant_file(inbox).write_bytes(before)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_witness_expiring_during_queue_preparation_cannot_publish(ready, monkeypatch):
    _, inbox, _, request = ready
    pending = monitor_control._pending

    def elapsed(directory):
        result = pending(directory)
        monkeypatch.setattr(
            monitor_control, "_scope_now", lambda: NOW + timedelta(seconds=60)
        )
        return result

    monkeypatch.setattr(monitor_control, "_pending", elapsed)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_withdrawn_witness_refuses_retry_then_renews_same_exact_proposal(ready):
    _, inbox, reader, request = ready
    assert inbox.enqueue_scope(request)
    publication = inbox.root / "inbox" / f"{COMMAND}.json"
    original = publication.read_bytes()
    reader.withdraw(GRANT)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert publication.read_bytes() == original
    reader.advertise(reader.probe(request))
    assert inbox.enqueue_scope(request)
    assert publication.read_bytes() == original


def test_scope_credential_cannot_authenticate_reader_witness(ready):
    from aitm_usage.scope_admission import _witness_tag, _write_grant, stored_grant

    writer, inbox, _, request = ready
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
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_modified_committed_grant_cannot_mint_producer_authority(ready):
    _, inbox, _, request = ready
    active = _active_grant_file(inbox)
    data = json.loads(active.read_bytes())
    data["record"]["grant"]["actions"] = ["dispose", "mark"]
    data["record"]["credential"] = "a" * 64
    active.write_bytes(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_scope_request_refuses_noncanonical_selectors(tmp_path, monkeypatch, capsys):
    path = _request_file(tmp_path)
    root = tmp_path / "monitor"
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: root)
    data = json.loads(path.read_bytes())
    for field, value in (("command_id", COMMAND), ("grant_id", GRANT)):
        for noncanonical in (value.hex, value.urn, "{" + str(value) + "}"):
            path.write_text(json.dumps({**data, field: noncanonical}))
            assert _cli(monkeypatch, path) == 1
            assert json.loads(capsys.readouterr().out) == {"status": "unavailable"}
    assert not root.exists()


def test_project_substitution_during_preparation_cannot_publish(
    ready, tmp_path, monkeypatch
):
    _, inbox, _, request = ready
    pending = monitor_control._pending
    state = tmp_path / "project"

    def substituted(directory):
        result = pending(directory)
        state.rename(tmp_path / "old-project")
        shutil.copytree(tmp_path / "old-project", state)
        return result

    monkeypatch.setattr(monitor_control, "_pending", substituted)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    assert not tuple(inbox.root.glob("inbox/*.json"))


def test_expiry_after_publication_withholds_ack_and_retry_reuses_exact_bytes(
    ready, monkeypatch
):
    _, inbox, reader, request = ready
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
    publication = inbox.root / "inbox" / f"{COMMAND}.json"
    original = publication.read_bytes()
    monkeypatch.setattr(monitor_control, "_publish", publish)
    reader.advertise(reader.probe(request))
    assert inbox.enqueue_scope(request)
    assert publication.read_bytes() == original


def test_reader_capability_cannot_restore_withdrawn_admission(ready):
    writer, inbox, reader, request = ready
    other = ScopeInboxReader(writer, inbox)
    old = reader.probe(request)
    other.withdraw(GRANT)
    with pytest.raises(LedgerError, match="proof is unavailable"):
        reader.advertise(old)
    with pytest.raises(LedgerError):
        inbox.enqueue_scope(request)
    other.advertise(other.probe(request))
    assert inbox.enqueue_scope(request)


def test_adopted_scope_shape_refuses_separate_source_anchor_command(tmp_path):
    from aitm_usage.scope_admission import adopted_request
    from aitm_usage.types import InboxCommand, SourceAnchorCommand

    ledger = Ledger.initialize(tmp_path / "project", PROJECT)
    command = InboxCommand(
        COMMAND,
        PROJECT,
        SourceAnchorCommand(
            COMMAND,
            PROJECT,
            ledger.pseudonymize("test", "configuration"),
            ledger.pseudonymize("test", "anchor"),
        ),
    )
    with pytest.raises(ValueError, match="legacy command"):
        adopted_request(command, UUID(int=92), None)
