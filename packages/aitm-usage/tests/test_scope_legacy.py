import fcntl
import hmac
import json
import os
import sys
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

from aitm_usage import cli, monitor_control, monitor_registry, scopes
from aitm_usage.ledger import Ledger
from aitm_usage.scope_admission import adopted_request, legacy_grant_id
from aitm_usage.service import CLAUDE_SESSIONS_NAME, register_project
from aitm_usage.types import (
    BoundaryKind,
    DevelopmentBinding,
    DraftAlias,
    InboxCommand,
    ItemKey,
    ItemKind,
    ItemParent,
    MarkerDisposition,
    Provider,
    ScopeCorrection,
    ScopeMarker,
    SourceBoundary,
    WorkPhase,
    encode_binding,
    encode_command,
    encode_correction,
    encode_marker,
)

PROJECT = UUID(int=110)
CODEX = UUID(int=111)
CLAUDE = UUID(int=112)
ADOPTION = UUID(int=113)
DRAFT = UUID(int=114)
COMMAND = UUID(int=115)
ITEM = ItemKey(ItemKind.ISSUE, 2)
NOW = datetime(2026, 11, 9, 16, tzinfo=UTC)
ADOPTION_FILE = "monitor-adoption-v1.json"


def commit_adoption(ledger, adoption_id, **binding_changes):
    """Model the future writer's one-way commit under the actual legacy lock."""
    with scopes._inbox_publication(ledger) as (project, _):
        binding = {
            "project_id": str(ledger.identity.project_id),
            "ledger_key_id": ledger.identity.key_id,
            "state_path": str(project.path),
            "state_identity": list(project.identities[-1]),
            "adoption_id": str(adoption_id),
        } | binding_changes
        encoded = json.dumps(binding, sort_keys=True, separators=(",", ":")).encode()
        tag = hmac.digest(
            ledger._key, b"aitm-usage/monitor-adoption/v1\0" + encoded, "sha256"
        ).hex()
        record = json.dumps(
            {"binding": binding, "tag": tag}, sort_keys=True, separators=(",", ":")
        ).encode()
        assert scopes._publish(project, ADOPTION_FILE, record)


@pytest.fixture
def legacy(tmp_path, monkeypatch, capsys):
    monitor_root = tmp_path / "monitor"
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: monitor_root)
    monkeypatch.setenv("CODEX_THREAD_ID", str(CODEX))

    root = tmp_path / "project"
    source = tmp_path / "source"
    checkout = tmp_path / "checkout"
    source.mkdir()
    checkout.mkdir()
    config = tmp_path / "registration-input.json"
    config.write_text(
        json.dumps(
            {
                "project_id": str(PROJECT),
                "source_roots": [str(source)],
                "checkout_anchors": [str(checkout)],
                "cutoff": NOW.isoformat(),
            }
        )
    )
    register_project(root, config)

    def run(args, *, as_json=True):
        flags = ["--json"] if as_json else []
        monkeypatch.setattr(
            sys, "argv", ["aitm-usage", "--project", str(root), *args, *flags]
        )
        code = cli.main()
        return code, capsys.readouterr()

    return Ledger.open(root, PROJECT), monitor_root, run


def invocation(ledger, action, *, provider=Provider.CODEX):
    def ref(namespace, name):
        return ledger.pseudonymize(namespace, name)

    if action == "alias":
        return (
            ("item", "alias", "--draft", str(DRAFT), "--issue", "2"),
            DraftAlias(COMMAND, PROJECT, ItemKey(ItemKind.DRAFT, DRAFT), ITEM),
            None,
        )
    if action == "parent":
        return (
            ("item", "parent", "--child", "2", "--epic", "1"),
            ItemParent(COMMAND, PROJECT, ITEM, ItemKey(ItemKind.ISSUE, 1)),
            None,
        )
    session = (
        ref("claude-session", str(CLAUDE))
        if provider is Provider.CLAUDE
        else ref("codex-session", str(CODEX))
    )
    marker = ScopeMarker(
        COMMAND,
        provider,
        session,
        1,
        BoundaryKind.REQUEST,
        ref("fixture", "boundary"),
        NOW,
        ITEM,
        WorkPhase.PLANNING,
        ref("fixture", "participant"),
        PROJECT,
        receipt_ref=ref("scope-receipt", str(COMMAND)),
    )
    input_file = ledger.root.parent / "scope-input.json"
    session_args = ("--session-id", str(CLAUDE)) if provider is Provider.CLAUDE else ()
    if action == "mark":
        input_file.write_bytes(encode_marker(marker))
        return (
            ("scope", "mark", "--marker", str(input_file), *session_args),
            marker,
            session if session_args else None,
        )
    if action == "bind":
        owner = replace(
            marker, phase=WorkPhase.DEVELOPMENT, attempt_ref=ref("fixture", "attempt")
        )
        binding = DevelopmentBinding(owner, ref("fixture", "anchor"), 1)
        input_file.write_bytes(encode_binding(binding))
        return (
            ("development", "bind", "--binding", str(input_file), *session_args),
            binding,
            session if session_args else None,
        )
    correction = ScopeCorrection(
        COMMAND,
        PROJECT,
        replace(marker, marker_id=DRAFT, receipt_ref=None),
        ref("fixture", "correction"),
    )
    input_file.write_bytes(encode_correction(correction))
    return ("scope", "correct", "--correction", str(input_file)), correction, None


def install_adopted_capture(monkeypatch, ledger):
    captured = []

    def enqueue_adopted(actual_ledger, adoption_id, command, claude_session):
        assert actual_ledger.identity == ledger.identity
        assert adoption_id == ADOPTION
        # A separate open file description can acquire this lock only once the
        # legacy producer has released it.
        fd = os.open(ledger.root / "inbox", os.O_RDONLY | os.O_DIRECTORY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            os.close(fd)
        captured.append((encode_command(command), claude_session))
        return True

    monkeypatch.setattr(
        monitor_control, "enqueue_adopted_scope", enqueue_adopted, raising=False
    )
    return captured


@pytest.mark.parametrize(
    ("action", "provider"),
    [
        ("mark", Provider.CLAUDE),
        ("bind", Provider.CLAUDE),
        ("correct", Provider.CODEX),
        ("alias", Provider.CODEX),
        ("parent", Provider.CODEX),
    ],
)
def test_adopted_legacy_invocations_preserve_command_and_receipt(
    legacy, monkeypatch, action, provider
):
    ledger, _, run = legacy
    args, payload, session = invocation(ledger, action, provider=provider)
    commit_adoption(ledger, ADOPTION)
    captured = install_adopted_capture(monkeypatch, ledger)
    # Unclassifiable legacy bytes would halt relationship enqueue. Adoption
    # leaves those bytes in place and uses the monitor queue instead.
    (ledger.root / "inbox" / "old.json").write_bytes(b"legacy input")

    code, output = run(args)

    assert code == 0, output
    reported_id = UUID(json.loads(output.out)["command_id"])
    assert output.out == f'{{"command_id": "{reported_id}", "status": "queued"}}\n'
    assert output.err == ""
    if isinstance(payload, (DraftAlias, ItemParent)):
        payload = replace(payload, command_id=reported_id)
    else:
        assert reported_id == COMMAND
    assert captured == [
        (encode_command(InboxCommand(reported_id, PROJECT, payload)), session)
    ]
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
    assert [path.name for path in (ledger.root / "inbox").iterdir()] == ["old.json"]

    repeated_code, repeated_output = run(args, as_json=False)
    assert repeated_code == 0
    repeated_id = UUID(repeated_output.out.split()[0])
    assert repeated_output.out == f"{repeated_id} queued\n"
    if isinstance(payload, (DraftAlias, ItemParent)):
        assert repeated_id != reported_id
    else:
        assert repeated_id == reported_id
        assert captured[0] == captured[1]


@pytest.mark.parametrize("action", ["mark", "alias"])
def test_adoption_wins_between_legacy_selection_and_publication(
    legacy, monkeypatch, action
):
    ledger, _, run = legacy
    args, payload, session = invocation(ledger, action, provider=Provider.CLAUDE)
    captured = install_adopted_capture(monkeypatch, ledger)
    original_publication = scopes._publication
    committed = False

    @contextmanager
    def publication_after_adoption(inbox):
        nonlocal committed
        if not committed:
            committed = True
            commit_adoption(ledger, ADOPTION)
        with original_publication(inbox):
            yield

    monkeypatch.setattr(scopes, "_publication", publication_after_adoption)
    code, output = run(args)

    assert code == 0, output
    reported_id = UUID(json.loads(output.out)["command_id"])
    if action == "alias":
        payload = replace(payload, command_id=reported_id)
    else:
        assert reported_id == COMMAND
    assert captured == [
        (encode_command(InboxCommand(reported_id, PROJECT, payload)), session)
    ]
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
    assert list((ledger.root / "inbox").iterdir()) == []


def test_adopted_legacy_requires_the_compatible_reader_witness(legacy):
    ledger, monitor_root, run = legacy
    args, payload, session = invocation(ledger, "mark", provider=Provider.CLAUDE)
    commit_adoption(ledger, ADOPTION)
    inbox = monitor_control.ControlInbox(monitor_root)
    grant_id = legacy_grant_id(PROJECT, ADOPTION)
    command = InboxCommand(COMMAND, PROJECT, payload)
    with monitor_registry.Registry(monitor_root).writer() as writer:
        registered = writer.register_project(
            monitor_registry.ProjectRegistrationRequest(
                PROJECT, str(ledger.root), "Legacy"
            )
        )
        adopted = replace(registered, adopted_key_id=ledger.identity.key_id)
        with inbox.publication():
            writer._save(replace(writer.view(), projects=(adopted,)))
        writer.source_evidence()
        reader = monitor_control.ScopeInboxReader(writer, inbox)
        reader.register(grant_id, PROJECT, ("legacy",), adoption_id=ADOPTION)

        code, output = run(args)

        assert code == 1
        assert output.out == '{"status": "unavailable"}\n'
        assert output.err == ""
        with inbox.publication() as locked:
            assert list(inbox.iter_pending(locked)) == []

        reader.advertise(reader.probe(adopted_request(command, ADOPTION, session)))
        code, output = run(args)
        assert code == 0
        assert output.out == f'{{"command_id": "{COMMAND}", "status": "queued"}}\n'
        with inbox.publication() as locked:
            (queued,) = reader.iter_verified(locked)
        assert queued.body.request.legacy_bytes.encode() == encode_command(command)
        assert queued.body.request.claude_session == session
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
    assert list((ledger.root / "inbox").iterdir()) == []


def test_committed_adoption_without_monitor_registration_fails_closed(legacy):
    ledger, monitor_root, run = legacy
    args, _, _ = invocation(ledger, "mark", provider=Provider.CLAUDE)
    commit_adoption(ledger, ADOPTION)

    code, output = run(args, as_json=False)

    assert code == 1
    assert output.out == ""
    assert output.err == "aitm-usage: unavailable\n"
    assert not monitor_root.exists()
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
    assert list((ledger.root / "inbox").iterdir()) == []


@pytest.mark.parametrize(
    "invalid", ["malformed", "tag", "project", "key", "path", "identity", "symlink"]
)
def test_invalid_local_adoption_refuses_without_any_legacy_or_monitor_write(
    legacy, monkeypatch, invalid
):
    ledger, monitor_root, run = legacy
    args, _, _ = invocation(ledger, "mark", provider=Provider.CLAUDE)
    record = ledger.root / ADOPTION_FILE
    if invalid == "malformed":
        record.write_bytes(b"private malformed canary")
        record.chmod(0o600)
    elif invalid == "symlink":
        target = ledger.root.parent / "substituted"
        target.write_text("private substituted canary")
        record.symlink_to(target)
    elif invalid == "tag":
        commit_adoption(ledger, ADOPTION)
        data = json.loads(record.read_bytes())
        data["tag"] = "0" * 64
        record.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")))
    else:
        change = {
            "project": ("project_id", str(DRAFT)),
            "key": ("ledger_key_id", "f" * 64),
            "path": ("state_path", str(ledger.root.parent / "other")),
            "identity": ("state_identity", [0, 0]),
        }
        key, value = change[invalid]
        commit_adoption(ledger, ADOPTION, **{key: value})
    inbox = ledger.root / "inbox"
    before = tuple(ledger.root.iterdir())

    def monitor_publication(*args):
        pytest.fail("invalid local adoption reached monitor publication")

    monkeypatch.setattr(
        monitor_control, "enqueue_adopted_scope", monitor_publication, raising=False
    )
    code, output = run(args)

    assert code == 1
    assert output.out == '{"status": "unavailable"}\n'
    assert output.err == ""
    assert not monitor_root.exists()
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
    assert not inbox.exists() or list(inbox.iterdir()) == []
    assert set(ledger.root.iterdir()) == set(before)


@pytest.mark.parametrize("monitor_corrupt", [False, True])
def test_pre_adoption_claude_records_memo_and_replays_receipt_despite_monitor_state(
    legacy, monkeypatch, monitor_corrupt
):
    ledger, monitor_root, run = legacy
    if monitor_corrupt:
        monitor_root.mkdir(mode=0o700)
        registry = monitor_root / "registry-v1.json"
        registry.write_bytes(b"private invalid registry")
        registry.chmod(0o600)

    def read_registry(*args, **kwargs):
        pytest.fail("pre-adoption command reached the unrelated monitor registry")

    monkeypatch.setattr(monitor_registry.Registry, "view", read_registry)
    args, marker, session = invocation(ledger, "mark", provider=Provider.CLAUDE)
    boundary = SourceBoundary(
        Provider.CLAUDE,
        ledger.pseudonymize("fixture", "stream"),
        session,
        1,
        BoundaryKind.REQUEST,
        marker.boundary_ref,
        receipt_ref=marker.receipt_ref,
    )

    with ledger.writer() as writer:
        code, output = run(args)
        assert code == 0, output
        assert output.out == f'{{"command_id": "{COMMAND}", "status": "queued"}}\n'
        sessions = ledger.root / CLAUDE_SESSIONS_NAME
        (memo,) = list(sessions.iterdir())
        assert memo.read_bytes() == json.dumps(session.value).encode()
        assert str(CLAUDE).encode() not in memo.read_bytes()

        drain = scopes.drain_inbox(writer, (scopes.BoundaryEvidence(boundary),))
        assert drain.receipts[0].disposition is MarkerDisposition.ACCEPTED
        code, output = run(args)
        assert code == 0, output
        assert output.out == f'{{"command_id": "{COMMAND}", "status": "accepted"}}\n'
    if not monitor_corrupt:
        assert not monitor_root.exists()


@pytest.mark.parametrize("action", ["bind", "correct", "alias", "parent"])
def test_other_pre_adoption_commands_use_legacy_inbox(legacy, monkeypatch, action):
    ledger, _, run = legacy

    def read_registry(*args, **kwargs):
        pytest.fail("pre-adoption command reached the unrelated monitor registry")

    monkeypatch.setattr(monitor_registry.Registry, "view", read_registry)
    args, payload, _ = invocation(ledger, action)
    code, output = run(args)
    assert code == 0, output
    reported_id = UUID(json.loads(output.out)["command_id"])
    assert output.out == f'{{"command_id": "{reported_id}", "status": "queued"}}\n'
    publication = ledger.root / "inbox" / f"{reported_id}.json"
    if isinstance(payload, (DraftAlias, ItemParent)):
        payload = replace(payload, command_id=reported_id)
        assert json.loads(publication.read_bytes())["order"] == 1
        repeated_code, repeated_output = run(args)
        assert repeated_code == 0, repeated_output
        repeated_id = UUID(json.loads(repeated_output.out)["command_id"])
        assert repeated_id != reported_id
        repeated_publication = ledger.root / "inbox" / f"{repeated_id}.json"
        assert json.loads(repeated_publication.read_bytes())["order"] == 2
    else:
        assert reported_id == COMMAND
        assert publication.read_bytes() == encode_command(
            InboxCommand(COMMAND, PROJECT, payload)
        )
