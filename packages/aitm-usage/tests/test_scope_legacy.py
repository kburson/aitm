import fcntl
import hmac
import json
import os
import sys
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from monitor_inbox_cases import MonitorInboxFiles
from test_ledger import _memory_ledger

from aitm_usage import (
    cli,
    monitor_control,
    monitor_registry,
    scope_admission,
    scopes,
    service,
)
from aitm_usage import ledger as ledger_module
from aitm_usage.ledger import Ledger
from aitm_usage.scope_admission import adopted_request, legacy_grant_id
from aitm_usage.service import CLAUDE_SESSIONS_NAME, register_project
from aitm_usage.types import (
    BoundaryKind,
    CommandReceipt,
    DevelopmentBinding,
    DraftAlias,
    InboxCommand,
    ItemKey,
    ItemKind,
    ItemParent,
    LedgerView,
    MarkerDisposition,
    Provider,
    Revision,
    ScopeCorrection,
    ScopeMarker,
    SourceBoundary,
    WorkPhase,
    _encode,
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


def _adoption_bytes(ledger, project, adoption_id, **binding_changes):
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
    return json.dumps(
        {"binding": binding, "tag": tag}, sort_keys=True, separators=(",", ":")
    ).encode()


def commit_adoption(ledger, adoption_id, **binding_changes):
    """Model the future writer's one-way commit under the actual legacy lock."""
    with scopes._inbox_publication(ledger) as (project, _):
        record = _adoption_bytes(ledger, project, adoption_id, **binding_changes)
        assert scopes._publish(project, ADOPTION_FILE, record)


def _cli_runner(root, monkeypatch, capsys):
    def run(args, *, as_json=True):
        flags = ["--json"] if as_json else []
        monkeypatch.setattr(
            sys, "argv", ["aitm-usage", "--project", str(root), *args, *flags]
        )
        code = cli.main()
        return code, capsys.readouterr()

    return run


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

    return (
        Ledger.open(root, PROJECT),
        monitor_root,
        _cli_runner(root, monkeypatch, capsys),
    )


@pytest.fixture
def memory_legacy(monkeypatch, capsys):
    return _memory_legacy(monkeypatch, capsys)


def _memory_legacy(monkeypatch, capsys, *, monitor_registered=None, claude_memo=False):
    monitor = None
    if monitor_registered is None:
        ledger = _memory_ledger(ledger_module, PROJECT, b"l" * 32)
    else:
        monitor = MonitorInboxFiles(monkeypatch, PROJECT)
        ledger = monitor.ledger
    project = SimpleNamespace(path=ledger.root, identities=((1, 2),), check=Mock())
    inbox = SimpleNamespace(fd=10)
    state_files = {}
    inbox_files = {}
    inputs = {}
    receipt_rows = {}
    receipt_reads = []

    def open_ledger(path, project_id):
        assert (path, project_id) == (ledger.root, PROJECT)
        return ledger

    def pin_project(path):
        assert path == ledger.root
        return nullcontext(project)

    def private_child(parent, name, *, create):
        assert parent is project and name == scopes.INBOX_NAME and create
        return nullcontext(inbox)

    def publication(directory):
        assert directory is inbox
        assert ADOPTION_FILE not in state_files, (
            "adoption must fence legacy publication"
        )
        return nullcontext()

    def read_private(directory, name):
        if getattr(directory, "path", None) == project.path:
            assert name == ADOPTION_FILE
            return state_files.get(name)
        assert directory is inbox
        return inbox_files.get(name)

    def publish(directory, name, data):
        assert directory is inbox
        assert name not in inbox_files, "legacy command publication is exclusive"
        inbox_files[name] = data
        return True

    def list_inbox(descriptor):
        assert descriptor == inbox.fd
        return list(inbox_files)

    def open_input(path, mode):
        assert mode == "rb"
        return BytesIO(inputs[path])

    def query_receipt(_query, params):
        (key,) = params
        receipt_reads.append(key)
        return SimpleNamespace(fetchone=lambda: receipt_rows.get(key))

    def store_receipt(receipt):
        key = ledger.pseudonymize("inbox-command", str(receipt.command.command_id))
        receipt_rows[key.value] = (1, _encode(Revision(key, 1, receipt), Revision))

    def publish_adoption():
        state_files[ADOPTION_FILE] = _adoption_bytes(ledger, project, ADOPTION)

    def unexpected_registry(*args, **kwargs):
        pytest.fail("Legacy receipt or publication reached the monitor registry")

    def unexpected_enqueue(*args, **kwargs):
        pytest.fail("Legacy receipt or publication forwarded to the monitor")

    def unexpected_memo(*args, **kwargs):
        pytest.fail("Legacy path wrote a Claude session memo")

    monkeypatch.setattr(Ledger, "open", staticmethod(open_ledger))
    monkeypatch.setattr(
        Ledger,
        "reader",
        lambda self: nullcontext(SimpleNamespace(execute=query_receipt)),
    )
    monkeypatch.setattr(cli, "open_project", lambda path: open_ledger(path, PROJECT))
    monkeypatch.setattr(cli, "version", lambda _: "0.0.0")
    monkeypatch.setattr(scopes, "_pin_directory", pin_project)
    monkeypatch.setattr(scopes, "_private_child", private_child)
    monkeypatch.setattr(scopes, "_publication", publication)
    monkeypatch.setattr(scopes, "_read_private", read_private)
    monkeypatch.setattr(scopes, "_publish", publish)
    monkeypatch.setattr(scopes, "os", SimpleNamespace(listdir=list_inbox))
    if not claude_memo:
        monkeypatch.setattr(service, "remember_claude_session", unexpected_memo)
    if monitor is None:
        monkeypatch.setattr(monitor_registry.Registry, "view", unexpected_registry)
        monkeypatch.setattr(
            monitor_control, "enqueue_adopted_scope", unexpected_enqueue
        )
    else:
        monkeypatch.setattr(
            monitor_registry, "default_monitor_root", lambda: monitor.root
        )
        if monitor_registered:
            view = monitor.writer.view()
            (registered,) = view.projects
            adopted = replace(registered, adopted_key_id=ledger.identity.key_id)

            def read_registry(registry, **_):
                assert registry.root == monitor.root
                return replace(view, projects=(adopted,))

            def pin_grant(path):
                return pin_project(path) if path == ledger.root else monitor.pin(path)

            monkeypatch.setattr(monitor_registry.Registry, "view", read_registry)
            monkeypatch.setattr(scope_admission, "_pin_directory", pin_grant)
        else:
            del monitor.files[monitor.root]
            monkeypatch.setattr(monitor_registry.Registry, "view", unexpected_registry)
    monkeypatch.setattr(Path, "open", open_input)
    monkeypatch.setenv("CODEX_THREAD_ID", str(CODEX))

    return SimpleNamespace(
        ledger=ledger,
        inputs=inputs,
        inbox=inbox_files,
        run=_cli_runner(ledger.root, monkeypatch, capsys),
        publish_adoption=publish_adoption,
        store_receipt=store_receipt,
        receipt_reads=receipt_reads,
        monitor=monitor,
    )


def invocation(
    ledger, action, *, provider=Provider.CODEX, write_input=Path.write_bytes
):
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
        write_input(input_file, encode_marker(marker))
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
        write_input(input_file, encode_binding(binding))
        return (
            ("development", "bind", "--binding", str(input_file), *session_args),
            binding,
            session if session_args else None,
        )
    correction = ScopeCorrection(
        COMMAND,
        PROJECT,
        replace(marker, marker_id=DRAFT, receipt_ref=ref("scope-receipt", str(DRAFT))),
        ref("fixture", "correction"),
    )
    write_input(input_file, encode_correction(correction))
    return ("scope", "correct", "--correction", str(input_file)), correction, None


def install_adopted_capture(monkeypatch, ledger, *, physical_lock=True):
    captured = []

    def enqueue_adopted(actual_ledger, adoption_id, command, claude_session):
        assert actual_ledger.identity == ledger.identity
        assert adoption_id == ADOPTION
        if physical_lock:
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
    request, monkeypatch, action, provider
):
    # Unclassifiable legacy bytes would halt relationship enqueue. Adoption
    # leaves those bytes in place and uses the monitor queue instead.
    memory = request.getfixturevalue("memory_legacy") if action != "mark" else None
    if memory is None:
        ledger, _, run = request.getfixturevalue("legacy")
        args, payload, session = invocation(ledger, action, provider=provider)
        commit_adoption(ledger, ADOPTION)
        (ledger.root / "inbox" / "old.json").write_bytes(b"legacy input")
    else:
        ledger, run = memory.ledger, memory.run
        args, payload, session = invocation(
            ledger, action, provider=provider, write_input=memory.inputs.__setitem__
        )
        memory.publish_adoption()
        memory.inbox["old.json"] = b"legacy input"
    captured = install_adopted_capture(
        monkeypatch, ledger, physical_lock=memory is None
    )

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
    if memory is None:
        assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
        assert [path.name for path in (ledger.root / "inbox").iterdir()] == ["old.json"]
    else:
        assert memory.inbox == {"old.json": b"legacy input"}

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
    request, monkeypatch, action
):
    memory = request.getfixturevalue("memory_legacy") if action == "alias" else None
    if memory is None:
        ledger, _, run = request.getfixturevalue("legacy")
    else:
        ledger, run = memory.ledger, memory.run
    args, payload, session = invocation(ledger, action, provider=Provider.CLAUDE)
    captured = install_adopted_capture(
        monkeypatch, ledger, physical_lock=memory is None
    )
    original_publication = scopes._publication
    committed = False

    @contextmanager
    def publication_after_adoption(inbox):
        nonlocal committed
        if memory is None and not committed:
            committed = True
            commit_adoption(ledger, ADOPTION)
        with original_publication(inbox):
            if memory is not None:
                assert not committed
                committed = True
                memory.publish_adoption()
            yield
            assert not captured

    monkeypatch.setattr(scopes, "_publication", publication_after_adoption)
    code, output = run(args)

    assert committed
    assert code == 0, output
    reported_id = UUID(json.loads(output.out)["command_id"])
    if action == "alias":
        payload = replace(payload, command_id=reported_id)
    else:
        assert reported_id == COMMAND
    assert captured == [
        (encode_command(InboxCommand(reported_id, PROJECT, payload)), session)
    ]
    if memory is None:
        assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
        assert list((ledger.root / "inbox").iterdir()) == []
    else:
        assert not memory.inbox


def provision_legacy_reader(writer, inbox, ledger):
    registered = writer.register_project(
        monitor_registry.ProjectRegistrationRequest(PROJECT, str(ledger.root), "Legacy")
    )
    adopted = replace(registered, adopted_key_id=ledger.identity.key_id)
    with inbox.publication():
        writer._save(replace(writer.view(), projects=(adopted,)))
    writer.source_evidence()
    reader = monitor_control.ScopeInboxReader(writer, inbox)
    reader.register(
        legacy_grant_id(PROJECT, ADOPTION), PROJECT, ("legacy",), adoption_id=ADOPTION
    )
    return reader


def legacy_boundary(ledger, marker, anchor=None):
    return scopes.BoundaryEvidence(
        SourceBoundary(
            marker.provider,
            ledger.pseudonymize("fixture", "stream"),
            marker.session_ref,
            1,
            marker.boundary_kind,
            marker.boundary_ref,
            receipt_ref=marker.receipt_ref,
        ),
        anchor,
    )


def _legacy_outcome_inputs(ledger, command, status):
    payload = command.payload
    conflict = status is MarkerDisposition.CONFLICT
    evidence = ()
    prior = None
    prior_evidence = ()
    if isinstance(payload, ScopeCorrection):
        original = replace(payload.replacement, item=ItemKey(ItemKind.ISSUE, 3))
        if conflict:
            original = replace(
                original, boundary_ref=ledger.pseudonymize("fixture", "other-boundary")
            )
        prior = InboxCommand(original.marker_id, PROJECT, original)
        prior_evidence = (legacy_boundary(ledger, original),)
    elif isinstance(payload, (DraftAlias, ItemParent)):
        if conflict:
            conflicting = (
                replace(payload, command_id=DRAFT, issue=ItemKey(ItemKind.ISSUE, 3))
                if isinstance(payload, DraftAlias)
                else replace(
                    payload,
                    command_id=DRAFT,
                    child=payload.parent,
                    parent=payload.child,
                )
            )
            prior = InboxCommand(DRAFT, PROJECT, conflicting)
            prior_evidence = ()
    else:
        marker = payload.marker if isinstance(payload, DevelopmentBinding) else payload
        anchor = payload.anchor_ref if isinstance(payload, DevelopmentBinding) else None
        if status is not MarkerDisposition.PENDING:
            proof = legacy_boundary(ledger, marker, anchor)
            evidence = (proof,)
            if conflict:
                evidence += (
                    replace(proof, boundary=replace(proof.boundary, ordinal=2)),
                )

    return prior, prior_evidence, evidence


def establish_legacy_outcome(ledger, command, status):
    prior, prior_evidence, evidence = _legacy_outcome_inputs(ledger, command, status)
    with ledger.writer() as writer:
        if prior is not None:
            scopes.enqueue_command(ledger.root, prior)
            (receipt,) = scopes.drain_inbox(writer, prior_evidence).receipts
            assert receipt.disposition is MarkerDisposition.ACCEPTED
        scopes.enqueue_command(ledger.root, command)
        (receipt,) = scopes.drain_inbox(writer, evidence).receipts
    assert receipt.disposition is status
    return receipt


def _evaluate_replayed_receipt(ledger, command, status):
    prior, prior_evidence, evidence = _legacy_outcome_inputs(ledger, command, status)

    def evaluate(command, view, evidence, receipts):
        disposition, proof, effects = scopes._evaluate(
            ledger, command, view, evidence, receipts
        )
        receipt = CommandReceipt(
            command,
            ledger.validate_command(command),
            disposition,
            None if proof is None else proof.boundary,
            None if proof is None else proof.anchor_ref,
        )
        return receipt, effects

    view = LedgerView(PROJECT, 0, (), ())
    receipts = {}
    if prior is not None:
        accepted, effects = evaluate(prior, view, prior_evidence, receipts)
        assert accepted.disposition is MarkerDisposition.ACCEPTED
        view = LedgerView(PROJECT, 1, effects, ())
        receipts[prior.command_id] = accepted
    receipt, _ = evaluate(command, view, evidence, receipts)
    assert receipt.disposition is status
    return receipt


@contextmanager
def adopted_with_witness(ledger, monitor_root):
    commit_adoption(ledger, ADOPTION)
    inbox = monitor_control.ControlInbox(monitor_root)
    with monitor_registry.Registry(monitor_root).writer() as writer:
        reader = provision_legacy_reader(writer, inbox, ledger)
        _, example, _ = invocation(ledger, "alias")
        probe_id = UUID(int=116)
        probe = InboxCommand(probe_id, PROJECT, replace(example, command_id=probe_id))
        reader.advertise(reader.probe(adopted_request(probe, ADOPTION, None)))
        yield inbox


def _assert_adopted_receipt_replay(monkeypatch, capsys, action, provider, status):
    memory = _memory_legacy(monkeypatch, capsys)
    ledger = memory.ledger
    args, payload, session = invocation(
        ledger, action, provider=provider, write_input=memory.inputs.__setitem__
    )
    command = InboxCommand(COMMAND, PROJECT, payload)
    expected = _evaluate_replayed_receipt(ledger, command, status)
    memory.store_receipt(expected)
    memory.publish_adoption()
    if memory.inputs:
        code, output = memory.run(args)
        assert code == 0, output
        assert (
            output.out == f'{{"command_id": "{COMMAND}", "status": "{status.value}"}}\n'
        )
        assert output.err == ""
    assert (
        scopes.enqueue_command(ledger.root, command, claude_session=session) == expected
    )
    key = ledger.pseudonymize("inbox-command", str(COMMAND)).value
    assert memory.receipt_reads == [key] * (1 + bool(memory.inputs))
    assert not memory.inbox


@pytest.mark.parametrize(
    ("action", "provider"),
    [
        ("mark", Provider.CLAUDE),
        ("mark", Provider.CODEX),
        ("bind", Provider.CLAUDE),
        ("bind", Provider.CODEX),
        ("correct", Provider.CODEX),
        ("alias", Provider.CODEX),
        ("parent", Provider.CODEX),
    ],
)
@pytest.mark.parametrize(
    "status", [MarkerDisposition.ACCEPTED, MarkerDisposition.CONFLICT]
)
def test_adopted_replay_returns_the_exact_durable_legacy_outcome(
    request, monkeypatch, capsys, action, provider, status
):
    if (status, action, provider) != (
        MarkerDisposition.ACCEPTED,
        "mark",
        Provider.CLAUDE,
    ):
        _assert_adopted_receipt_replay(monkeypatch, capsys, action, provider, status)
        return

    legacy = request.getfixturevalue("legacy")
    ledger, monitor_root, run = legacy
    args, payload, session = invocation(ledger, action, provider=provider)
    command = InboxCommand(COMMAND, PROJECT, payload)
    expected = establish_legacy_outcome(ledger, command, status)
    before = ledger.as_of().sequence

    with adopted_with_witness(ledger, monitor_root) as inbox:
        code, output = run(args)
        assert code == 0, output
        assert (
            output.out == f'{{"command_id": "{COMMAND}", "status": "{status.value}"}}\n'
        )
        assert output.err == ""
        assert (
            scopes.enqueue_command(ledger.root, command, claude_session=session)
            == expected
        )
        with inbox.publication() as locked:
            assert list(inbox.iter_pending(locked)) == []
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()
    assert ledger.as_of().sequence == before


def test_adopted_replay_keeps_the_pending_legacy_receipt_without_monitor_state(
    memory_legacy,
):
    ledger = memory_legacy.ledger
    args, payload, _ = invocation(
        ledger,
        "mark",
        provider=Provider.CLAUDE,
        write_input=memory_legacy.inputs.__setitem__,
    )
    command = InboxCommand(COMMAND, PROJECT, payload)
    memory_legacy.store_receipt(
        _evaluate_replayed_receipt(ledger, command, MarkerDisposition.PENDING)
    )
    memory_legacy.publish_adoption()

    code, output = memory_legacy.run(args)

    assert code == 0, output
    assert output.out == f'{{"command_id": "{COMMAND}", "status": "pending"}}\n'
    assert output.err == ""
    assert memory_legacy.inbox == {}


def test_adopted_replay_preserves_legacy_conflict_for_changed_bytes(memory_legacy):
    ledger = memory_legacy.ledger
    args, payload, _ = invocation(
        ledger,
        "mark",
        provider=Provider.CLAUDE,
        write_input=memory_legacy.inputs.__setitem__,
    )
    command = InboxCommand(COMMAND, PROJECT, payload)
    memory_legacy.store_receipt(
        _evaluate_replayed_receipt(ledger, command, MarkerDisposition.ACCEPTED)
    )
    changed = replace(payload, item=ItemKey(ItemKind.ISSUE, 3))
    memory_legacy.inputs[ledger.root.parent / "scope-input.json"] = encode_marker(
        changed
    )
    memory_legacy.publish_adoption()

    code, output = memory_legacy.run(args)
    assert code == 1
    assert output.out == ""
    assert output.err == "aitm-usage: inbox command conflict\n"
    assert memory_legacy.inbox == {}


@pytest.mark.parametrize("provider", [Provider.CLAUDE, Provider.CODEX])
def test_replay_finds_receipt_committed_while_adoption_wins_the_legacy_lock(
    request, monkeypatch, provider
):
    if provider is Provider.CLAUDE:
        memory = request.getfixturevalue("memory_legacy")
        _assert_replay_at_legacy_cutover(memory, monkeypatch)
        return

    legacy = request.getfixturevalue("legacy")
    ledger, monitor_root, run = legacy
    args, payload, _ = invocation(ledger, "mark", provider=provider)
    command = InboxCommand(COMMAND, PROJECT, payload)
    scopes.enqueue_command(ledger.root, command)
    proof = legacy_boundary(ledger, payload)
    original_publication = scopes._publication
    cutover_started = False

    @contextmanager
    def publication_after_legacy_commit(inbox):
        nonlocal cutover_started
        if not cutover_started:
            cutover_started = True
            with ledger.writer() as writer:
                (receipt,) = scopes.drain_inbox(writer, (proof,)).receipts
                assert receipt.disposition is MarkerDisposition.ACCEPTED
                commit_adoption(ledger, ADOPTION)
        with original_publication(inbox):
            yield

    monkeypatch.setattr(scopes, "_publication", publication_after_legacy_commit)
    code, output = run(args)

    assert cutover_started
    assert code == 0, output
    assert output.out == f'{{"command_id": "{COMMAND}", "status": "accepted"}}\n'
    assert output.err == ""
    assert not monitor_root.exists()
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()


def _assert_replay_at_legacy_cutover(memory, monkeypatch):
    ledger = memory.ledger
    args, payload, _ = invocation(
        ledger,
        "mark",
        provider=Provider.CLAUDE,
        write_input=memory.inputs.__setitem__,
    )
    command = InboxCommand(COMMAND, PROJECT, payload)
    assert scopes.enqueue_command(ledger.root, command) is None
    name = f"{COMMAND}.json"
    assert memory.inbox[name] == encode_command(command)
    accepted = _evaluate_replayed_receipt(ledger, command, MarkerDisposition.ACCEPTED)
    original_publication = scopes._publication
    locks = []

    def publication_after_legacy_commit(inbox):
        lock = original_publication(inbox)
        assert not locks
        locks.append(inbox)
        memory.store_receipt(accepted)
        memory.publish_adoption()
        del memory.inbox[name]
        return lock

    monkeypatch.setattr(scopes, "_publication", publication_after_legacy_commit)
    code, output = memory.run(args)
    assert len(locks) == 1
    assert code == 0, output
    assert output.out == f'{{"command_id": "{COMMAND}", "status": "accepted"}}\n'
    assert output.err == ""
    assert not memory.inbox


def test_adopted_legacy_requires_the_compatible_reader_witness(monkeypatch, capsys):
    memory = _memory_legacy(monkeypatch, capsys, monitor_registered=True)
    ledger = memory.ledger
    args, payload, session = invocation(
        ledger, "mark", provider=Provider.CLAUDE, write_input=memory.inputs.__setitem__
    )
    memory.publish_adoption()
    inbox = memory.monitor.inbox
    command = InboxCommand(COMMAND, PROJECT, payload)
    reader = monitor_control.ScopeInboxReader(memory.monitor.writer, inbox)
    reader.register(
        legacy_grant_id(PROJECT, ADOPTION), PROJECT, ("legacy",), adoption_id=ADOPTION
    )

    code, output = memory.run(args)

    assert code == 1
    assert output.out == '{"status": "unavailable"}\n'
    assert output.err == ""
    with inbox.publication() as locked:
        assert list(inbox.iter_pending(locked)) == []

    reader.advertise(reader.probe(adopted_request(command, ADOPTION, session)))
    code, output = memory.run(args)
    assert code == 0
    assert output.out == f'{{"command_id": "{COMMAND}", "status": "queued"}}\n'
    with inbox.publication() as locked:
        (queued,) = reader.iter_verified(locked)
    assert queued.body.request.legacy_bytes.encode() == encode_command(command)
    assert queued.body.request.claude_session == session
    assert not memory.inbox


def test_committed_adoption_without_monitor_registration_fails_closed(
    monkeypatch, capsys
):
    memory = _memory_legacy(monkeypatch, capsys, monitor_registered=False)
    args, _, _ = invocation(
        memory.ledger,
        "mark",
        provider=Provider.CLAUDE,
        write_input=memory.inputs.__setitem__,
    )
    memory.publish_adoption()

    code, output = memory.run(args, as_json=False)

    assert code == 1
    assert output.out == ""
    assert output.err == "aitm-usage: unavailable\n"
    assert memory.monitor.root not in memory.monitor.files
    assert not memory.inbox


def _assert_invalid_adoption_policy(monkeypatch, capsys, invalid):
    ledger = _memory_ledger(ledger_module, PROJECT, b"l" * 32)
    inputs = {}
    args, _, _ = invocation(
        ledger, "mark", provider=Provider.CLAUDE, write_input=inputs.__setitem__
    )
    project = SimpleNamespace(path=ledger.root, identities=((1, 2),), check=Mock())
    if invalid == "malformed":
        contents = b"private malformed canary"
    elif invalid == "tag":
        data = json.loads(_adoption_bytes(ledger, project, ADOPTION))
        data["tag"] = "0" * 64
        contents = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    else:
        key, value = {
            "project": ("project_id", str(DRAFT)),
            "key": ("ledger_key_id", "f" * 64),
            "path": ("state_path", str(ledger.root.parent / "other")),
            "identity": ("state_identity", [0, 0]),
        }[invalid]
        contents = _adoption_bytes(ledger, project, ADOPTION, **{key: value})

    def open_ledger(path, project_id):
        assert (path, project_id) == (ledger.root, PROJECT)
        return ledger

    def open_input(path, mode):
        assert mode == "rb"
        return BytesIO(inputs[path])

    def read_adoption(directory, name):
        assert directory is project and name == ADOPTION_FILE
        return contents

    legacy_write = Mock(
        side_effect=AssertionError("invalid adoption opened the legacy inbox")
    )
    monitor_write = Mock(
        side_effect=AssertionError("invalid adoption reached monitor publication")
    )
    monkeypatch.setattr(Ledger, "open", staticmethod(open_ledger))
    monkeypatch.setattr(Path, "open", open_input)
    monkeypatch.setattr(scopes, "_pin_directory", lambda path: nullcontext(project))
    monkeypatch.setattr(scopes, "_read_private", read_adoption)
    monkeypatch.setattr(scopes, "_inbox_publication", legacy_write)
    monkeypatch.setattr(monitor_control, "enqueue_adopted_scope", monitor_write)
    monkeypatch.setattr(cli, "version", lambda _: "0.0.0")
    monkeypatch.setattr(
        sys, "argv", ["aitm-usage", "--project", str(ledger.root), *args, "--json"]
    )
    assert cli.main() == 1
    output = capsys.readouterr()
    assert output.out == '{"status": "unavailable"}\n'
    assert output.err == ""
    legacy_write.assert_not_called()
    monitor_write.assert_not_called()


@pytest.mark.parametrize(
    "invalid", ["malformed", "tag", "project", "key", "path", "identity", "symlink"]
)
def test_invalid_local_adoption_refuses_without_any_legacy_or_monitor_write(
    request, monkeypatch, capsys, invalid
):
    if invalid != "symlink":
        _assert_invalid_adoption_policy(monkeypatch, capsys, invalid)
        return

    ledger, monitor_root, run = request.getfixturevalue("legacy")
    args, _, _ = invocation(ledger, "mark", provider=Provider.CLAUDE)
    record = ledger.root / ADOPTION_FILE
    target = ledger.root.parent / "substituted"
    target.write_text("private substituted canary")
    record.symlink_to(target)
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
    request, monkeypatch, capsys, monitor_corrupt
):
    if monitor_corrupt:
        _assert_pre_adoption_with_corrupt_monitor(monkeypatch, capsys)
        return

    legacy = request.getfixturevalue("legacy")
    ledger, monitor_root, run = legacy

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
    assert not monitor_root.exists()


def _assert_pre_adoption_with_corrupt_monitor(monkeypatch, capsys):
    memory = _memory_legacy(
        monkeypatch, capsys, monitor_registered=False, claude_memo=True
    )
    ledger = memory.ledger
    registered = service._Config(
        PROJECT, ("/fixture/source",), ("/fixture/checkout",), NOW, (), (), ()
    )
    configuration = _encode(registered, service._Config).encode()
    view = LedgerView(
        PROJECT, 1, (service._registration_revision(ledger, registered),), ()
    )
    project, sessions = object(), object()
    files = {project: {service.REGISTRATION_NAME: configuration}, sessions: {}}
    monitor = memory.monitor
    broken = {"registry-v1.json": b"private invalid registry"}
    monitor.files[monitor.root] = broken.copy()

    def pin_project(path):
        assert path == ledger.root
        return nullcontext(project)

    def child(directory, name, *, create):
        assert directory is project and name == CLAUDE_SESSIONS_NAME and create
        return nullcontext(sessions)

    def publish(directory, name, data):
        assert directory is sessions and name not in files[sessions]
        files[sessions][name] = data
        return True

    monkeypatch.setattr(Ledger, "as_of", lambda _: view)
    monkeypatch.setattr(service, "_pin_directory", pin_project)
    monkeypatch.setattr(service, "_private_child", child)
    monkeypatch.setattr(
        service, "_read_private", lambda pin, name: files[pin].get(name)
    )
    monkeypatch.setattr(service, "_publish", publish)
    args, marker, session = invocation(
        ledger, "mark", provider=Provider.CLAUDE, write_input=memory.inputs.__setitem__
    )
    command = InboxCommand(COMMAND, PROJECT, marker)
    code, output = memory.run(args)
    assert code == 0, output
    assert output.out == f'{{"command_id": "{COMMAND}", "status": "queued"}}\n'
    assert memory.inbox == {f"{COMMAND}.json": encode_command(command)}
    (memo,) = files[sessions].values()
    assert memo == json.dumps(session.value).encode()
    assert str(CLAUDE).encode() not in memo

    accepted = _evaluate_replayed_receipt(ledger, command, MarkerDisposition.ACCEPTED)
    memory.store_receipt(accepted)
    memory.inbox.clear()
    code, output = memory.run(args)
    assert code == 0, output
    assert output.out == f'{{"command_id": "{COMMAND}", "status": "accepted"}}\n'
    assert not memory.inbox
    assert monitor.files[monitor.root] == broken


@pytest.mark.parametrize("action", ["bind", "correct", "alias", "parent"])
def test_other_pre_adoption_commands_use_legacy_inbox(
    memory_legacy, monkeypatch, action
):
    args, payload, _ = invocation(
        memory_legacy.ledger, action, write_input=memory_legacy.inputs.__setitem__
    )

    def read_registry(*args, **kwargs):
        pytest.fail("pre-adoption command reached the unrelated monitor registry")

    def publication_bytes(command_id):
        return memory_legacy.inbox[f"{command_id}.json"]

    monkeypatch.setattr(monitor_registry.Registry, "view", read_registry)
    code, output = memory_legacy.run(args)
    assert code == 0, output
    reported_id = UUID(json.loads(output.out)["command_id"])
    assert output.out == f'{{"command_id": "{reported_id}", "status": "queued"}}\n'
    if isinstance(payload, (DraftAlias, ItemParent)):
        payload = replace(payload, command_id=reported_id)
        assert json.loads(publication_bytes(reported_id))["order"] == 1
        repeated_code, repeated_output = memory_legacy.run(args)
        assert repeated_code == 0, repeated_output
        repeated_id = UUID(json.loads(repeated_output.out)["command_id"])
        assert repeated_id != reported_id
        assert json.loads(publication_bytes(repeated_id))["order"] == 2
    else:
        assert reported_id == COMMAND
        assert publication_bytes(reported_id) == encode_command(
            InboxCommand(COMMAND, PROJECT, payload)
        )
