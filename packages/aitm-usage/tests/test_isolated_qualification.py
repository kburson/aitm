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
    original_resolver = pilot._approved_pilot_tuple
    original_collector = pilot._collect_host_installation
    with monkeypatch.context() as host:
        host.setattr(pilot, "_collect_host_installation", lambda *_: "a" * 64)
        host.setattr(
            pilot,
            "_approved_pilot_tuple",
            lambda candidate: expected if candidate == digest else None,
        )
        with (
            native.registry.writer() as writer,
            pilot._OpenedExecutable.copy(
                binary, tmp_path / "image" / "candidate"
            ) as image,
        ):
            owner = key.with_suffix(".pub").read_bytes()
            issuer = pilot._prepare_isolated_issuer(writer, layout, image, None, owner)
            now = datetime.now(UTC)

            def activate():
                payload = issuer.proposal("activate", 1, now + timedelta(minutes=5))
                return pilot._install_isolated_profile(issuer, payload, sign(payload))

            def revoke():
                payload = issuer.proposal("revoke", 2, now + timedelta(minutes=5))
                issuer.revoke(payload, sign(payload))

            yield native, writer, issuer, activate, revoke, sign

    assert pilot._approved_pilot_tuple is original_resolver
    assert pilot._collect_host_installation is original_collector
    with native.registry.writer() as reopened:
        assert reopened._live_profile is None
        with pytest.raises(_LiveSourceUnavailable) as caught:
            ScopeState(reopened).read_source(SOURCE, native.locator())
        assert type(caught.value) is _LiveSourceUnavailable


def _durable(journal, native):
    view = journal.as_of()
    with journal._store.transaction() as conn:
        (tip,) = conn.execute(
            "SELECT COALESCE(MAX(sequence), 0) FROM commits"
        ).fetchone()
        assert view.sequence == tip
        assert conn.execute("SELECT count(*) FROM claims").fetchone() == (
            len(view.claims),
        )
    return (
        view,
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
    (source,) = original_view.sources
    original_profile = writer._live_profile
    expected_installation = writer.source_evidence().pseudonymize(
        "excluded-installation", f"{SOURCE}:{source.directory.identity}"
    )
    revoke()
    assert writer.view() == original_view
    routes = [lambda: journal.reserve_batch(prepared)]
    if admitted:
        candidate = prepared.candidates[0]
        routes.append(lambda: journal.reserve(candidate, prepared.progress))
    for reserve in routes:
        with pytest.raises(_LiveSourceUnavailable) as captured:
            reserve()
        assert type(captured.value) is _LiveSourceUnavailable
        if admitted:
            decision = captured.value.decision
            assert decision is not None and decision.source_id == SOURCE
            assert decision.installation == expected_installation
            assert decision.generation == original_profile.generation
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
    from aitm_usage import _isolated_qualification as pilot

    native, writer, issuer, activate, _, sign = installed
    expires = datetime.now(UTC) + timedelta(minutes=5)
    proposal = issuer.proposal("activate", 1, expires)
    bogus = issuer.proposal("activate", 1, expires + timedelta(seconds=1))
    with pytest.raises(LedgerError):
        pilot._install_isolated_profile(issuer, bogus, sign(proposal))
    assert writer._live_profile is None
    activate()
    with pytest.raises(LedgerError):
        pilot._install_isolated_profile(issuer, proposal, sign(proposal))
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
    assert type(caught.value) is _LiveSourceUnavailable
    assert caught.value.decision is not None
    assert _durable(journal, native) == before
    assert _durable(RoutingJournal(writer, ScopeState(writer)), native) == before


def test_product_issuer_and_exclusion_consumers_have_fixed_entry_points():
    import ast
    import tomllib

    repo = Path(__file__).resolve().parents[3]
    package = repo / "packages" / "aitm-usage"
    runner = repo / "tools" / "qualification" / "isolated_grok_pilot.py"
    issuer = package / "src" / "aitm_usage" / "_isolated_qualification.py"
    private_symbols = {
        "_isolated_qualification",
        "_install_isolated_profile",
        "_prepare_isolated_issuer",
    }
    excluded = {".git", ".venv", "tests", "node_modules", ".scratch", "build", "dist"}
    imports, activation_calls, prepare_calls = [], [], []
    consumers, confirmation_calls, recorder_calls = [], [], []
    for path in sorted(repo.rglob("*.py")):
        if excluded.intersection(path.relative_to(repo).parts) or path.is_symlink():
            continue
        module = ast.parse(path.read_bytes())
        parents = {
            child: parent
            for parent in ast.walk(module)
            for child in ast.iter_child_nodes(parent)
        }

        def enclosing_function(node):
            while node in parents:
                node = parents[node]
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    return node.name
            return "<module>"

        for node in ast.walk(module):
            if isinstance(node, (ast.Import, ast.ImportFrom)) and any(
                symbol in ast.unparse(node) for symbol in private_symbols
            ):
                imports.append(path)
            if isinstance(node, ast.Constant) and type(node.value) is str:
                assert not any(symbol in node.value for symbol in private_symbols)
            if isinstance(node, ast.Call):
                name = getattr(node.func, "id", getattr(node.func, "attr", None))
                if name == "_install_isolated_profile":
                    activation_calls.append(path)
                elif name == "_prepare_isolated_issuer":
                    prepare_calls.append(path)
                elif name == "_confirm_live_exclusion":
                    confirmation_calls.append((path.name, enclosing_function(node)))
                elif name == "_record_live_exclusion":
                    recorder_calls.append((path.name, enclosing_function(node)))
            if isinstance(node, ast.ExceptHandler) and any(
                isinstance(item, ast.Attribute)
                and item.attr == "decision"
                and isinstance(item.ctx, ast.Load)
                for item in ast.walk(node)
            ):
                consumers.append((path.name, enclosing_function(node)))
            if (
                path != issuer
                and isinstance(node, ast.Attribute)
                and node.attr in private_symbols
            ):
                pytest.fail("Private issuer reflection outside its defining module")
    assert imports == [runner]
    assert activation_calls == [runner]
    assert prepare_calls == [runner]
    assert sorted(consumers) == [
        ("monitor_journal.py", "prepare"),
        ("monitor_scope.py", "_confirm_live_exclusion"),
    ]
    assert confirmation_calls == [
        ("monitor_journal.py", "_record_live_exclusion"),
        ("monitor_journal.py", "_record_live_exclusion"),
    ]
    assert recorder_calls == [("monitor_journal.py", "prepare")]
    for path in repo.rglob("pyproject.toml"):
        if excluded.intersection(path.relative_to(repo).parts):
            continue
        project = tomllib.loads(path.read_text()).get("project", {})
        entry_points = project.get("entry-points", {})
        for group in (
            project.get("scripts", {}),
            project.get("gui-scripts", {}),
            *entry_points.values(),
        ):
            assert all("qualification" not in entry for entry in group.values())


def test_closed_resolver_cannot_copy_the_unpatched_codex_fixture(tmp_path):
    from hashlib import sha256

    from aitm_usage import _isolated_qualification as pilot

    binary = tmp_path / "unqualified"
    binary.write_bytes(b"exact installed image")
    digest = sha256(binary.read_bytes()).hexdigest()
    selected = pilot._approved_pilot_tuple(pilot._GROK_DIGEST)
    assert selected == _LiveSourceTuple(
        "grok", "grok-build-macos", "Darwin", "arm64", "1.0.77", 1
    )
    for unqualified in (digest, "0" * 64, "", pilot._GROK_DIGEST.upper()):
        assert pilot._approved_pilot_tuple(unqualified) is None
    with pytest.raises(
        LedgerError, match="Isolated source qualification is unavailable"
    ):
        with pilot._OpenedExecutable.copy(binary, tmp_path / "wrong"):
            pytest.fail("Unqualified binary could be copied")
    assert not (tmp_path / "wrong").exists()


def test_signed_supersession_invalidates_the_prior_generation(installed):
    from aitm_usage import _isolated_qualification as pilot

    native, writer, issuer, activate, _, sign = installed
    activate()
    locator = native.locator()
    scope = ScopeState(writer)
    old = scope.read_source(SOURCE, locator)
    profile = writer._live_profile
    (installation,) = profile.installations
    assert profile.current(installation)
    proposal = issuer.proposal("replace", 2, datetime.now(UTC) + timedelta(minutes=2))
    pilot._install_isolated_profile(issuer, proposal, sign(proposal))
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


def test_revocation_is_terminal_and_writer_thread_is_private(installed):
    from concurrent.futures import ThreadPoolExecutor

    from aitm_usage import _isolated_qualification as pilot

    native, writer, issuer, activate, revoke, sign = installed
    proof = activate()
    assert type(proof) is pilot._InstallationProof
    with ThreadPoolExecutor(max_workers=1) as task:
        assert task.submit(writer._live_profile.current, proof).result() is False
    revoke()
    next_proposal = issuer.proposal(
        "replace", 3, datetime.now(UTC) + timedelta(minutes=2)
    )
    with pytest.raises(LedgerError):
        pilot._install_isolated_profile(issuer, next_proposal, sign(next_proposal))
    with pytest.raises(_LiveSourceUnavailable):
        ScopeState(writer).read_source(SOURCE, native.locator())
