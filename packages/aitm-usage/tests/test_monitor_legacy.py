import json
import sys
from contextlib import contextmanager, nullcontext
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from test_scope_legacy import memory_legacy as memory_legacy

from aitm_usage import cli, monitor_registry, scopes, service
from aitm_usage.ledger import Ledger, WriterActive

PROJECT = UUID(int=116)
ANCHOR_COMMAND = UUID(int=117)


@pytest.fixture
def legacy(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    monkeypatch.setattr(
        monitor_registry, "default_monitor_root", lambda: tmp_path / "monitor"
    )
    root = tmp_path / "project"
    sources = tmp_path / "sources"
    checkout = tmp_path / "checkout"
    added_checkout = tmp_path / "added-checkout"
    for directory in (sources, checkout, added_checkout):
        directory.mkdir()

    config = tmp_path / "project.json"
    config.write_text(
        json.dumps(
            {
                "project_id": str(PROJECT),
                "source_roots": [str(sources)],
                "checkout_anchors": [str(checkout)],
                "cutoff": "2026-11-09T16:00:00+00:00",
            }
        )
    )
    anchor = tmp_path / "anchor.json"
    anchor.write_text(
        json.dumps(
            {
                "command_id": str(ANCHOR_COMMAND),
                "project_id": str(PROJECT),
                "checkout": str(added_checkout),
            }
        )
    )

    def run(*args):
        monkeypatch.setattr(sys, "argv", ["aitm-usage", "--project", str(root), *args])
        status = cli.main()
        output = capsys.readouterr()
        return status, output

    assert run("register", "--config", str(config), "--json")[0] == 0
    return root, config, anchor, run


@pytest.fixture
def adopt(legacy):
    root, _, _, _ = legacy
    ledger = Ledger.open(root, PROJECT)
    registry = monitor_registry.Registry(monitor_registry.default_monitor_root())
    with registry.writer() as writer:
        project = writer.register_project(
            monitor_registry.ProjectRegistrationRequest(PROJECT, str(root), "Legacy")
        )

    def commit():
        with registry.writer() as writer:
            # Model the snapshot a later cutover commits while it holds the legacy lock.
            updated = replace(project, adopted_key_id=ledger.identity.key_id)
            writer._save(replace(writer.view(), projects=(updated,)))

    return commit


@pytest.fixture
def legacy_policy(memory_legacy, monkeypatch):
    ledger = memory_legacy.ledger
    monitor = Path("/fixture/monitor")
    directory = monitor_registry._PhysicalDirectory(str(ledger.root), (1, 2))
    project = monitor_registry.RegisteredProject(
        ledger.identity.project_id, directory, "Legacy", None, (), None
    )
    current = monitor_registry.RegistryView(projects=(project,))

    def view(registry):
        assert registry.root == monitor
        return current

    monkeypatch.setattr(monitor_registry, "default_monitor_root", lambda: monitor)
    monkeypatch.setattr(monitor_registry.Registry, "view", view)
    monkeypatch.setattr(
        monitor_registry, "_path_exists", lambda path: path == ledger.root
    )

    def physical(path, *, private):
        assert private and path == directory.path
        return directory

    monkeypatch.setattr(monitor_registry, "_directory", physical)

    def adopt_current():
        nonlocal current
        adopted = replace(project, adopted_key_id=ledger.identity.key_id)
        current = replace(current, projects=(adopted,))

    memory_legacy.adopt_current = adopt_current
    return memory_legacy


@pytest.mark.parametrize("command", ["register", "source add-anchor"])
def test_legacy_mutation_reports_adoption_before_opening_input(
    legacy_policy, monkeypatch, command
):
    legacy_policy.adopt_current()
    open_input = Mock(
        side_effect=AssertionError("adopted legacy command opened its input")
    )
    open_writer = Mock(
        side_effect=AssertionError("adopted legacy command tried to write")
    )
    monkeypatch.setattr(Path, "open", open_input)
    monkeypatch.setattr(Ledger, "writer", open_writer)
    missing = "/fixture/missing-private-input"
    input_option = "--config" if command == "register" else "--anchor"

    status, output = legacy_policy.run((*command.split(), input_option, missing))

    assert status == 1
    assert json.loads(output.out) == {"status": "project-adopted-use-monitor"}
    assert output.err == ""
    open_input.assert_not_called()
    open_writer.assert_not_called()
    assert legacy_policy.inbox == {}


def test_legacy_register_rechecks_after_entering_writer(legacy_policy, monkeypatch):
    ledger = legacy_policy.ledger
    config = _existing_registration_input(legacy_policy, monkeypatch)
    enter = Mock()
    pin = Mock(return_value=nullcontext(SimpleNamespace(path=ledger.root)))
    observe = Mock(side_effect=AssertionError("Adopted registration read ledger rows"))
    publish = Mock(
        side_effect=AssertionError("Adopted registration reached publication")
    )
    apply = Mock(side_effect=AssertionError("Adopted registration tried to commit"))

    @contextmanager
    def writer_after_cutover(actual):
        assert actual is ledger
        enter()
        legacy_policy.adopt_current()
        yield actual

    monkeypatch.setattr(Ledger, "writer", writer_after_cutover)
    monkeypatch.setattr(Ledger, "as_of", observe)
    monkeypatch.setattr(Ledger, "apply", apply)
    monkeypatch.setattr(service, "_pin_directory", pin)
    monkeypatch.setattr(service, "_publish_exact", publish)
    status, output = legacy_policy.run(("register", "--config", str(config)))

    assert status == 1
    assert json.loads(output.out) == {"status": "project-adopted-use-monitor"}
    enter.assert_called_once_with()
    pin.assert_called_once_with(ledger.root)
    observe.assert_not_called()
    publish.assert_not_called()
    apply.assert_not_called()


def test_legacy_register_rereads_adoption_on_writer_refusal(legacy_policy, monkeypatch):
    ledger = legacy_policy.ledger
    config = _existing_registration_input(legacy_policy, monkeypatch)

    def writer_after_cutover(actual):
        assert actual is ledger
        legacy_policy.adopt_current()
        raise WriterActive("fixture collector holds the writer")

    monkeypatch.setattr(Ledger, "writer", writer_after_cutover)
    status, output = legacy_policy.run(("register", "--config", str(config)))

    assert status == 1
    assert json.loads(output.out) == {"status": "project-adopted-use-monitor"}


def _existing_registration_input(legacy_policy, monkeypatch):
    ledger = legacy_policy.ledger
    config = Path("/fixture/project.json")
    sources, checkout = Path("/fixture/sources"), Path("/fixture/checkout")
    legacy_policy.inputs[config] = json.dumps(
        {
            "project_id": str(ledger.identity.project_id),
            "source_roots": [str(sources)],
            "checkout_anchors": [str(checkout)],
            "cutoff": "2026-11-09T16:00:00+00:00",
        }
    ).encode()
    monkeypatch.setattr(
        service, "_directory_available", {sources, checkout}.__contains__
    )
    monkeypatch.setattr(
        service, "_path_exists", lambda path: path == ledger.root / service.STORE_NAME
    )
    return config


def test_legacy_register_uses_read_only_opener_for_existing_store(
    legacy_policy, monkeypatch
):
    from test_ledger import _LedgerRows

    from aitm_usage.ledger import APPLICATION_ID

    ledger = legacy_policy.ledger
    config = _existing_registration_input(legacy_policy, monkeypatch)
    open_existing = Mock(wraps=Ledger.open)
    initialize = Mock(
        side_effect=AssertionError("Registration of an existing store initializes it")
    )
    pin = SimpleNamespace(path=ledger.root)
    writer = replace(ledger, _writer=Mock(), _write_paths=Mock())
    acquire_writer = Mock(return_value=nullcontext(writer))
    rows = _LedgerRows(ledger.identity, APPLICATION_ID, ())
    files = {}

    def publish(directory, name, data):
        assert directory is pin and name == service.REGISTRATION_NAME
        assert name not in files
        files[name] = data
        return True

    monkeypatch.setattr(Ledger, "open", open_existing)
    monkeypatch.setattr(Ledger, "initialize", initialize)
    monkeypatch.setattr(Ledger, "writer", acquire_writer)
    monkeypatch.setattr(Ledger, "reader", lambda _: rows.connect(write=False))
    monkeypatch.setattr(
        Ledger, "_write_transaction", lambda _: rows.connect(write=True)
    )
    monkeypatch.setattr(service, "_pin_directory", lambda _: nullcontext(pin))
    monkeypatch.setattr(service, "_read_private", lambda parent, name: files.get(name))
    monkeypatch.setattr(service, "_publish", publish)

    args = ("register", "--config", str(config))
    assert legacy_policy.run(args)[0] == 0
    snapshot = writer.as_of()
    assert snapshot.sequence == len(snapshot.revisions) == 1
    published = files.copy()
    open_existing.reset_mock()
    acquire_writer.reset_mock()
    status, output = legacy_policy.run(args)
    assert status == 0
    assert json.loads(output.out)["project_id"] == str(ledger.identity.project_id)
    open_existing.assert_called_once_with(ledger.root, ledger.identity.project_id)
    initialize.assert_not_called()
    acquire_writer.assert_called_once_with()
    assert writer.as_of() == snapshot
    assert files == published


def test_legacy_anchor_rechecks_under_publication_lock_before_staging(
    legacy_policy, monkeypatch
):
    anchor = Path("/fixture/anchor.json")
    command_id = UUID(int=118)
    legacy_policy.inputs[anchor] = json.dumps(
        {
            "command_id": str(command_id),
            "project_id": str(legacy_policy.ledger.identity.project_id),
            "checkout": "/fixture/new-checkout",
        }
    ).encode()
    original_publication = scopes._publication
    locked = Mock()

    @contextmanager
    def publication_after_cutover(inbox):
        with original_publication(inbox):
            locked(inbox)
            legacy_policy.adopt_current()
            yield

    stage = Mock(side_effect=AssertionError("Adopted anchor reached staging"))
    monkeypatch.setattr(service, "_stage_source_anchor", stage)
    monkeypatch.setattr(scopes, "_publication", publication_after_cutover)
    status, output = legacy_policy.run(
        ("source", "add-anchor", "--anchor", str(anchor)), as_json=False
    )
    locked.assert_called_once()
    stage.assert_not_called()
    assert not legacy_policy.inbox
    assert status == 1
    assert output.err.strip() == "aitm-usage: project-adopted-use-monitor"


def test_pre_adoption_legacy_anchor_enqueues_while_collector_holds_writer(
    legacy, request, monkeypatch
):
    from test_scope_legacy import ADOPTION_FILE, invocation

    from aitm_usage.types import Provider, encode_marker

    root, _, anchor, run = legacy
    project = Ledger.open(root, PROJECT)
    scope, marker, _ = invocation(project, "mark", provider=Provider.CLAUDE)
    assert scope[2] == "--marker"
    Path(scope[3]).write_bytes(encode_marker(replace(marker, project_id=PROJECT)))
    target = root.parent / "alternate-adoption"
    target.write_bytes(b"alternate private adoption")
    record = root / ADOPTION_FILE
    record.symlink_to(target)
    present = set(root.iterdir())
    status, output = run(*scope, "--json")
    assert status == 1 and output.out == '{"status": "unavailable"}\n'
    assert not output.err
    assert set(root.iterdir()) == present
    assert not monitor_registry.default_monitor_root().exists()
    assert target.read_bytes() == b"alternate private adoption"
    record.unlink()
    _assert_native_receipt_at_local_cutover(project, run, monkeypatch)
    record.unlink()
    _assert_native_fresh_mark_at_local_cutover(project, run, monkeypatch)
    record.unlink()

    with Ledger.open(root, PROJECT).writer():
        status, output = run("source", "add-anchor", "--anchor", str(anchor), "--json")

    assert status == 0
    assert json.loads(output.out) == {
        "status": "queued",
        "command_id": str(ANCHOR_COMMAND),
    }
    assert (root / "source-anchors" / f"{ANCHOR_COMMAND}.json").is_file()
    assert (root / "inbox" / f"{ANCHOR_COMMAND}.json").is_file()
    assert not monitor_registry.default_monitor_root().exists()

    adopt = request.getfixturevalue("adopt")
    new_id = UUID(int=118)
    anchor_data = json.loads(anchor.read_bytes())
    anchor.write_text(json.dumps(anchor_data | {"command_id": str(new_id)}))
    before = {
        path: path.read_bytes()
        for directory in (root / "source-anchors", root / "inbox")
        for path in directory.rglob("*")
        if path.is_file()
    }
    original_publication = scopes._publication

    @contextmanager
    def publication_after_cutover(inbox):
        with original_publication(inbox):
            adopt()
            yield

    monkeypatch.setattr(scopes, "_publication", publication_after_cutover)
    status, output = run("source", "add-anchor", "--anchor", str(anchor))
    assert status == 1
    assert output.err.strip() == "aitm-usage: project-adopted-use-monitor"
    assert {
        path: path.read_bytes()
        for directory in (root / "source-anchors", root / "inbox")
        for path in directory.rglob("*")
        if path.is_file()
    } == before


def _assert_native_receipt_at_local_cutover(ledger, run, monkeypatch):
    from test_scope_legacy import (
        ADOPTION,
        CODEX,
        commit_adoption,
        invocation,
        legacy_boundary,
    )

    from aitm_usage.types import InboxCommand, MarkerDisposition, encode_marker

    args, payload, _ = invocation(ledger, "mark")
    payload = replace(payload, project_id=ledger.identity.project_id)
    Path(args[3]).write_bytes(encode_marker(payload))
    command = InboxCommand(payload.marker_id, payload.project_id, payload)
    assert scopes.enqueue_command(ledger.root, command) is None
    proof = legacy_boundary(ledger, payload)
    original_publication = scopes._publication
    receipts = []

    @contextmanager
    def publication_after_commit(inbox):
        assert not receipts
        with monkeypatch.context() as original:
            original.setattr(scopes, "_publication", original_publication)
            with ledger.writer() as writer:
                receipts.extend(scopes.drain_inbox(writer, (proof,)).receipts)
            commit_adoption(ledger, ADOPTION)
        with original_publication(inbox):
            yield

    with monkeypatch.context() as cutover:
        cutover.setenv("CODEX_THREAD_ID", str(CODEX))
        cutover.setattr(scopes, "_publication", publication_after_commit)
        code, output = run(*args, "--json")
    (accepted,) = receipts
    assert code == 0 and not output.err
    assert json.loads(output.out) == {
        "command_id": str(command.command_id),
        "status": "accepted",
    }
    assert accepted.disposition is MarkerDisposition.ACCEPTED
    assert ledger.command_receipt(command) == accepted
    before = ledger.as_of()
    assert scopes.enqueue_command(ledger.root, command) == accepted
    assert ledger.as_of() == before
    assert not monitor_registry.default_monitor_root().exists()


def _assert_native_fresh_mark_at_local_cutover(ledger, run, monkeypatch):
    from test_scope_legacy import (
        ADOPTION,
        commit_adoption,
        install_adopted_capture,
        invocation,
    )

    from aitm_usage.service import CLAUDE_SESSIONS_NAME
    from aitm_usage.types import InboxCommand, Provider, encode_command, encode_marker

    args, payload, session = invocation(ledger, "mark", provider=Provider.CLAUDE)
    command_id = UUID(int=119)
    payload = replace(
        payload,
        marker_id=command_id,
        project_id=ledger.identity.project_id,
        receipt_ref=ledger.pseudonymize("scope-receipt", str(command_id)),
    )
    Path(args[3]).write_bytes(encode_marker(payload))
    command = InboxCommand(command_id, payload.project_id, payload)
    assert ledger.command_receipt(command) is None
    inbox = ledger.root / scopes.INBOX_NAME

    def snapshot():
        return {path: path.read_bytes() for path in inbox.rglob("*") if path.is_file()}

    before = snapshot()
    original_publication = scopes._publication
    with monkeypatch.context() as cutover:
        captured = install_adopted_capture(cutover, ledger)
        committed = False

        @contextmanager
        def publication_after_adoption(directory):
            nonlocal committed
            if not committed:
                committed = True
                commit_adoption(ledger, ADOPTION)
            with original_publication(directory):
                yield
                assert not captured

        cutover.setattr(scopes, "_publication", publication_after_adoption)
        code, output = run(*args, "--json")

    assert committed
    assert code == 0 and not output.err
    assert json.loads(output.out) == {
        "command_id": str(command_id),
        "status": "queued",
    }
    assert captured == [(encode_command(command), session)]
    assert snapshot() == before
    assert ledger.command_receipt(command) is None
    assert not (ledger.root / CLAUDE_SESSIONS_NAME).exists()


def test_invalid_legacy_anchor_input_leaves_inbox_untouched(legacy_policy, monkeypatch):
    anchor = Path("/fixture/anchor.json")
    legacy_policy.inputs[anchor] = b"{}"
    publish = Mock(
        side_effect=AssertionError("invalid anchor reached inbox publication")
    )
    monkeypatch.setattr(service, "_inbox_publication", publish)
    status, output = legacy_policy.run(
        ("source", "add-anchor", "--anchor", str(anchor)), as_json=False
    )

    assert status == 1
    assert output.err.strip() == "aitm-usage: invalid private inbox command or project"
    publish.assert_not_called()
    assert legacy_policy.inbox == {}
