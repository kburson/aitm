import json
import sys
from contextlib import contextmanager
from dataclasses import replace
from uuid import UUID

import pytest

from aitm_usage import cli, monitor_registry, scopes
from aitm_usage.ledger import Ledger

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


@pytest.mark.parametrize("command", ["register", "source add-anchor"])
def test_legacy_mutation_reports_adoption_before_opening_input(legacy, adopt, command):
    root, _, _, run = legacy
    ledger = Ledger.open(root, PROJECT)
    before = ledger.as_of().sequence
    adopt()
    missing = str(root.parent / "missing-private-input")
    input_option = "--config" if command == "register" else "--anchor"

    with ledger.writer():
        status, output = run(*command.split(), input_option, missing, "--json")

    assert status == 1
    assert json.loads(output.out) == {"status": "project-adopted-use-monitor"}
    assert output.err == ""
    assert ledger.as_of().sequence == before
    assert not (root / "source-anchors").exists()
    assert not (root / "inbox").exists()


def test_legacy_register_rechecks_after_entering_writer(legacy, adopt, monkeypatch):
    root, config, _, run = legacy
    ledger = Ledger.open(root, PROJECT)
    before = ledger.as_of().sequence
    registration = root / "registration.json"
    registration.unlink()
    original_writer = Ledger.writer

    @contextmanager
    def writer_after_cutover(self):
        with original_writer(self) as writer:
            adopt()
            yield writer

    monkeypatch.setattr(Ledger, "writer", writer_after_cutover)
    status, output = run("register", "--config", str(config), "--json")

    assert status == 1
    assert json.loads(output.out) == {"status": "project-adopted-use-monitor"}
    assert ledger.as_of().sequence == before
    assert not registration.exists()


def test_legacy_register_rereads_adoption_on_writer_refusal(legacy, adopt, monkeypatch):
    root, config, _, run = legacy
    ledger = Ledger.open(root, PROJECT)
    original_writer = Ledger.writer

    def writer_after_cutover(self):
        adopt()
        return original_writer(self)

    with ledger.writer():
        monkeypatch.setattr(Ledger, "writer", writer_after_cutover)
        status, output = run("register", "--config", str(config), "--json")

    assert status == 1
    assert json.loads(output.out) == {"status": "project-adopted-use-monitor"}


def test_legacy_register_uses_read_only_opener_for_existing_store(legacy, monkeypatch):
    _, config, _, run = legacy

    def initialize(*args):
        pytest.fail("registration of an existing store reached the initializer")

    monkeypatch.setattr(Ledger, "initialize", initialize)
    assert run("register", "--config", str(config), "--json")[0] == 0


def test_legacy_anchor_rechecks_under_publication_lock_before_staging(
    legacy, adopt, monkeypatch
):
    root, _, anchor, run = legacy
    (root / "inbox").mkdir(mode=0o700)
    original_publication = scopes._publication

    @contextmanager
    def publication_after_cutover(inbox):
        with original_publication(inbox):
            adopt()
            yield

    monkeypatch.setattr(scopes, "_publication", publication_after_cutover)
    status, output = run("source", "add-anchor", "--anchor", str(anchor))

    assert not (root / "source-anchors").exists()
    assert not (root / "inbox" / f"{ANCHOR_COMMAND}.json").exists()
    assert status == 1
    assert output.err.strip() == "aitm-usage: project-adopted-use-monitor"


def test_pre_adoption_legacy_anchor_enqueues_while_collector_holds_writer(legacy):
    root, _, anchor, run = legacy
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


def test_invalid_legacy_anchor_input_leaves_inbox_untouched(legacy):
    root, _, anchor, run = legacy
    anchor.write_text("{}")
    status, output = run("source", "add-anchor", "--anchor", str(anchor))

    assert status == 1
    assert output.err.strip() == "aitm-usage: invalid private inbox command or project"
    assert not (root / "source-anchors").exists()
    assert not (root / "inbox").exists()
