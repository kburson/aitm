import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from test_monitor_scope import SOURCE, NativeScopeFixture

from aitm_usage._monitor_qualification import (
    _LiveSourceTuple,
    _LiveSourceUnavailable,
)
from aitm_usage.ledger import LedgerError, _pin_directory
from aitm_usage.monitor_journal import RoutingJournal
from aitm_usage.monitor_registry import Registry
from aitm_usage.monitor_scope import ScopeState


@pytest.fixture
def installed(tmp_path, monkeypatch):
    from aitm_usage import _isolated_qualification as pilot

    with monkeypatch.context() as setup:
        setup.setattr(Registry, "_require_live_source", lambda *_, **__: object())
        native = NativeScopeFixture(tmp_path, monkeypatch)
    native.transcripts.chmod(0o700)
    for name in ("control", "provider", "workspace", "image"):
        (tmp_path / name).mkdir(mode=0o700)
    native.append()
    binary = tmp_path / "candidate"
    binary.write_bytes(b"exact installed image")
    expected = _LiveSourceTuple(
        "codex", "codex-desktop-macos", "Darwin", "arm64", "0.167.0-alpha.3.2", 1
    )
    key = tmp_path / "control" / "owner"
    subprocess.run(
        ["/usr/bin/ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
        check=True,
        capture_output=True,
    )
    layout = pilot._PilotLayout.create(
        tmp_path / "control",
        tmp_path / "provider",
        tmp_path / "workspace",
        tmp_path / "image",
        native.transcripts,
    )
    monkeypatch.setattr(pilot, "_collect_host_installation", lambda *_: "a" * 64)

    def sign(payload):
        return subprocess.run(
            [
                "/usr/bin/ssh-keygen",
                "-Y",
                "sign",
                "-n",
                "aitm-isolated-owner-proposal-v1",
                "-f",
                str(key),
            ],
            input=payload,
            check=True,
            capture_output=True,
        ).stdout

    from hashlib import sha256

    digest = sha256(binary.read_bytes()).hexdigest()
    monkeypatch.setattr(
        pilot,
        "_approved_pilot_tuple",
        lambda candidate: expected if candidate == digest else None,
    )
    with (
        native.registry.writer() as writer,
        pilot._OpenedExecutable.copy(binary, tmp_path / "image" / "candidate") as image,
    ):
        owner = key.with_suffix(".pub").read_bytes()
        issuer = pilot._install_isolated_profile(writer, layout, image, None, owner)
        now = datetime.now(UTC)

        def activate():
            payload = issuer.proposal("activate", 1, now + timedelta(minutes=5))
            issuer.commit(payload, sign(payload))

        def revoke():
            payload = issuer.proposal("revoke", 2, now + timedelta(minutes=5))
            issuer.commit(payload, sign(payload))

        yield native, writer, issuer, activate, revoke, sign


def _durable(journal, native):
    return (
        journal.as_of(),
        journal.cursor_for(SOURCE, native.locator()),
        journal.coverage_changes(0),
    )


@pytest.mark.parametrize("admitted", (True, False))
@pytest.mark.parametrize("retry", (True, False))
def test_admission_drives_private_denial_without_a_journal_change(
    installed, monkeypatch, admitted, retry
):
    native, writer, _, activate, revoke, _ = installed
    activate()
    scopes = ScopeState(writer)
    journal = RoutingJournal(writer, scopes)
    locator = native.locator()
    healthy = journal.prepare(SOURCE, locator)
    assert healthy.candidates and healthy._read.batch._admitted
    if admitted:
        prepared = healthy
    else:
        find_readers = scopes._admitted_readers

        def verify_then_remove(*args):
            assert find_readers(*args)
            return frozenset()

        with monkeypatch.context() as patch:
            patch.setattr(scopes, "_admitted_readers", verify_then_remove)
            prepared = journal.prepare(SOURCE, locator)
        assert not prepared.candidates and not prepared._read.batch._admitted
    assert prepared.progress == healthy.progress
    if retry:
        journal.reserve_batch(healthy)
        assert journal.cursor_for(SOURCE, locator) == prepared.progress
    else:
        assert journal.cursor_for(SOURCE, locator) is None

    before = _durable(journal, native)
    original_view = writer.view()
    revoke()
    assert writer.view() == original_view
    routes = [lambda: journal.reserve_batch(prepared)]
    if admitted:
        candidate = prepared.candidates[0]
        routes.append(lambda: journal.reserve(candidate, prepared.progress))
    for reserve in routes:
        with pytest.raises(_LiveSourceUnavailable) as captured:
            reserve()
        if admitted:
            decision = captured.value.decision
            assert decision is not None and decision.source_id == SOURCE
            writer.source_evidence().validate_source_ref(decision.installation)
            writer.source_evidence().validate_source_ref(decision.generation)
        else:
            assert captured.value.decision is None
        assert _durable(journal, native) == before
        assert _durable(RoutingJournal(writer, ScopeState(writer)), native) == before


@pytest.mark.parametrize("fault", (TypeError, KeyError))
def test_reader_exceptions_fail_closed_and_fresh_writer_starts_closed(
    installed, monkeypatch, fault
):
    from aitm_usage import _isolated_qualification as pilot

    native, writer, _, activate, _, _ = installed
    assert writer._live_profile is None
    activate()
    journal = RoutingJournal(writer, ScopeState(writer))
    prepared = journal.prepare(SOURCE, native.locator())

    def unreadable(*_):
        raise fault("protected reader failure")

    monkeypatch.setattr(pilot, "_read_private", unreadable)
    with pytest.raises(_LiveSourceUnavailable) as captured:
        journal.reserve_batch(prepared)
    assert captured.value.decision is not None
    assert Registry(writer.root)._live_profile is None


def test_valid_owner_signature_is_bound_to_revision_and_lease(installed):
    native, writer, issuer, activate, _, sign = installed
    expires = datetime.now(UTC) + timedelta(minutes=5)
    proposal = issuer.proposal("activate", 1, expires)
    bogus = issuer.proposal("activate", 1, expires + timedelta(seconds=1))
    with pytest.raises(LedgerError):
        issuer.commit(bogus, sign(proposal))
    assert writer._live_profile is None
    activate()
    with pytest.raises(LedgerError):
        issuer.commit(proposal, sign(proposal))
    assert RoutingJournal(writer, ScopeState(writer)).prepare(SOURCE, native.locator())
    saved_view = writer.view()
    with _pin_directory(writer.root) as root:
        Path(root.path, "isolated-qualification.json").write_bytes(b"{}")
    journal = RoutingJournal(writer, ScopeState(writer))
    with pytest.raises(_LiveSourceUnavailable):
        journal.prepare(SOURCE, native.locator())
    assert writer.view() == saved_view
    assert journal.coverage_changes(0) == ()


@pytest.mark.parametrize("phase", ("prepare", "staged"))
def test_late_recheck_refusal_is_private_and_rolls_back(installed, monkeypatch, phase):
    native, writer, _, activate, revoke, _ = installed
    activate()
    journal = RoutingJournal(writer, ScopeState(writer))
    locator = native.locator()
    before = _durable(journal, native)
    if phase == "prepare":
        verify = journal._fresh_view

        def lose_currentness(*args, **kwargs):
            revoke()
            return verify(*args, **kwargs)

        monkeypatch.setattr(journal, "_fresh_view", lose_currentness)

        def operation():
            return journal.prepare(SOURCE, locator)

    else:
        prepared = journal.prepare(SOURCE, locator)
        write = journal._write_progress

        def lose_currentness(*args):
            write(*args)
            revoke()

        monkeypatch.setattr(journal, "_write_progress", lose_currentness)

        def operation():
            return journal.reserve_batch(prepared)

    with pytest.raises(_LiveSourceUnavailable) as caught:
        operation()
    assert caught.value.decision is not None
    assert _durable(journal, native) == before
    assert _durable(RoutingJournal(writer, ScopeState(writer)), native) == before


def test_product_issuer_and_exclusion_consumers_have_fixed_entry_points():
    import ast
    import tomllib

    repo = Path(__file__).resolve().parents[3]
    package = repo / "packages" / "aitm-usage"
    source = package / "src"
    runner = repo / "tools" / "qualification" / "isolated_grok_pilot.py"
    imported = []
    installers = []
    consumers = []
    confirmation_calls = []
    recorder_calls = []
    for path in [*source.rglob("*.py"), *sorted((repo / "tools").rglob("*.py"))]:
        if "tests" in path.parts:
            continue
        module = ast.parse(path.read_bytes())
        for node in ast.walk(module):
            if isinstance(node, (ast.Import, ast.ImportFrom)) and (
                "_isolated_qualification" in ast.unparse(node)
                or "_install_isolated_profile" in ast.unparse(node)
            ):
                imported.append(path)
            if not isinstance(node, ast.FunctionDef):
                continue
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    name = getattr(child.func, "id", getattr(child.func, "attr", None))
                    if name == "_install_isolated_profile":
                        installers.append(path)
                    elif name == "_confirm_live_exclusion":
                        confirmation_calls.append((path.name, node.name))
                    elif name == "_record_live_exclusion":
                        recorder_calls.append((path.name, node.name))
                if isinstance(child, ast.ExceptHandler) and any(
                    isinstance(item, ast.Attribute)
                    and item.attr == "decision"
                    and isinstance(item.ctx, ast.Load)
                    for item in ast.walk(child)
                ):
                    consumers.append((path.name, node.name))
    assert imported == [runner]
    assert installers == [runner]
    assert sorted(consumers) == [
        ("monitor_journal.py", "prepare"),
        ("monitor_scope.py", "_confirm_live_exclusion"),
    ]
    assert confirmation_calls == [
        ("monitor_journal.py", "_record_live_exclusion"),
        ("monitor_journal.py", "_record_live_exclusion"),
    ]
    assert recorder_calls == [("monitor_journal.py", "prepare")]
    scripts = tomllib.loads((package / "pyproject.toml").read_text())["project"][
        "scripts"
    ]
    assert all("qualification" not in entry for entry in scripts.values())


def test_signed_supersession_invalidates_the_prior_generation(installed):
    native, writer, issuer, activate, _, sign = installed
    activate()
    locator = native.locator()
    scope = ScopeState(writer)
    old = scope.read_source(SOURCE, locator)
    profile = writer._live_profile
    (installation,) = profile.installations
    assert profile.current(installation)
    proposal = issuer.proposal("replace", 2, datetime.now(UTC) + timedelta(minutes=2))
    issuer.commit(proposal, sign(proposal))
    assert not profile.current(installation)
    assert writer._live_profile.current(installation)
    with pytest.raises(_LiveSourceUnavailable):
        scope.view(old)
    assert scope.read_source(SOURCE, locator).observations


def test_currentness_preserves_cancellation(installed, monkeypatch):
    from aitm_usage import _isolated_qualification as pilot

    native, writer, _, activate, _, _ = installed
    activate()
    journal = RoutingJournal(writer, ScopeState(writer))
    prepared = journal.prepare(SOURCE, native.locator())

    def cancelled(*_):
        raise KeyboardInterrupt

    monkeypatch.setattr(pilot, "_read_private", cancelled)
    with pytest.raises(KeyboardInterrupt):
        journal.reserve_batch(prepared)
