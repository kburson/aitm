"""Private registry identity, native capture epochs and command custody."""

import json
import os
from dataclasses import replace
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pytest
from native_registry_cases import native_registry_policy
from qualification_policy_cases import CaptureInbox, CapturePolicy
from scanner_policy_cases import NativeDirectoryMetadata, NativeTranscriptFiles
from test_codex import AFTER, CUTOFF, SESSION, begin, counter, end, response, usage
from test_ledger import _memory_ledger
from test_monitor_adapters import CODEX_FIXTURE, _adapter, _restart_rows
from test_monitor_adapters import source as source

from aitm_usage._monitor_qualification import _InstallationProof
from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.types import Eligibility

pytestmark = pytest.mark.usefixtures("legacy_monitor_qualification")

PROJECT_A = UUID(int=116)
PROJECT_B = UUID(int=117)
SOURCE = UUID(int=118)
_CODEX_TRANSCRIPT = CODEX_FIXTURE.read_text()


def _module():
    from aitm_usage import monitor_registry

    return monitor_registry


def _directory(root, name, *, mode=0o700):
    path = root / name
    path.mkdir(mode=mode)
    return path


def _request(module, root, project=PROJECT_A, *, anchors=()):
    state = _directory(root, f"state-{project.int}")
    return module.ProjectRegistrationRequest(
        project, str(state), f"Project {project.int}", anchors=tuple(map(str, anchors))
    )


def test_monitor_registry_can_be_opened_without_creating_state(monkeypatch):
    from unittest.mock import Mock

    module = _module()
    missing = Path("/fixture/monitor")
    exists = Mock(return_value=False)
    pin = Mock(side_effect=AssertionError("absent monitor directory was opened"))
    create = Mock(side_effect=AssertionError("read-only registry created state"))
    monkeypatch.setattr(module, "_path_exists", exists)
    monkeypatch.setattr(module, "_pin_directory", pin)
    monkeypatch.setattr(module, "_ensure_private_directory", create)
    assert module.Registry(missing).view().projects == ()
    exists.assert_called_once_with(missing)
    pin.assert_not_called()
    create.assert_not_called()


def test_two_clones_share_identity_but_nested_foreign_anchor_fails(tmp_path):
    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    assert registry.view().projects == ()
    assert not registry.root.exists()
    first = _directory(tmp_path, "first")
    clone = _directory(tmp_path, "clone")
    nested = _directory(clone, "nested")
    request = _request(module, tmp_path, anchors=(first, clone))
    other = _request(module, tmp_path, PROJECT_B, anchors=(nested,))
    with registry.writer() as writer:
        project = writer.register_project(request)
        renamed = writer.register_project(
            replace(request, display_name="Renamed", remote="new-origin")
        )
        assert project.project_id == renamed.project_id == PROJECT_A
        assert project.anchors == renamed.anchors and len(project.anchors) == 2
        with pytest.raises(ConflictError):
            writer.register_project(other)
        with pytest.raises(ConflictError):
            writer.register_project(replace(other, anchors=(str(tmp_path),)))
        alias = tmp_path / "alias"
        alias.symlink_to(clone, target_is_directory=True)
        with pytest.raises(ConflictError):
            writer.register_project(replace(other, anchors=(str(alias),)))
    assert registry.view().projects == (renamed,)


class _DesktopLog:
    def __init__(self, path, checkout, *, session=SESSION, initial_rows=None):
        self.path = path
        self.checkout = checkout
        self.session = session
        self.turns = 2
        rows, _ = _restart_rows("desktop", checkout, initial_rows=initial_rows)
        self.total = rows[-2]["payload"]["info"]["total_token_usage"]
        self._emit(rows, mode="w")

    def _emit(self, rows, *, mode):
        with self.path.open(mode, encoding="utf-8") as stream:
            for row in rows:
                stream.write(json.dumps(row).replace(str(SESSION), str(self.session)))
                stream.write("\n")

    def read_bytes(self):
        return self.path.read_bytes()

    def write_bytes(self, data):
        self.path.write_bytes(data)

    def append(self, turns=1, *, complete=True):
        for _ in range(turns):
            self.turns += 1
            turn = UUID(int=0x200 + self.turns)
            time = AFTER + timedelta(seconds=self.turns)
            delta = usage(3, 2)
            self.total = usage(
                self.total["input_tokens"] + 3,
                self.total["output_tokens"] + 2,
                cache=self.total["cached_input_tokens"],
                reasoning=self.total["reasoning_output_tokens"],
            )
            self._emit(
                [
                    *begin(self.checkout, turn, time=time),
                    response(
                        f"response-{self.turns}",
                        self.total,
                        delta,
                        time=time,
                        turn=turn,
                    ),
                    counter(self.total, delta, time=time),
                    *([end(turn, time=time)] if complete else []),
                ],
                mode="a",
            )


def _native_fixture(tmp_path, monkeypatch, source):
    module = _module()
    _, reader, root = _adapter(monkeypatch, source)
    _, directory, checkout = source
    with module.Registry(tmp_path / "monitor").writer() as writer:
        root = replace(root, evidence=writer.source_evidence())
    return module, reader, root, _DesktopLog(directory / "live.jsonl", checkout)


def _locate(reader, root, stream_ref=None):
    (locator,) = (
        item
        for item in reader.discover(root)
        if stream_ref is None or item.stream_ref == stream_ref
    )
    return locator


def _boundaries(reader, locator):
    return tuple(
        item.usage.boundary for item in reader.read_delta(locator, None).observations
    )


def _advance(writer, change, log, reader, root, stream_ref=None):
    frontier = writer.capture_frontier(change, _locate(reader, root, stream_ref))
    log.append()
    return writer.verify_boundary(change, _locate(reader, root, stream_ref), frontier)


def _approve(writer, module, root):
    return writer.approve_source(
        module.SourceApprovalRequest(
            SOURCE,
            "codex",
            "codex-desktop-macos",
            "Darwin",
            "arm64",
            "0.167.0-alpha.3.2",
            1,
            str(root.path),
        )
    )


@pytest.fixture
def registry_policy(monkeypatch):
    return _registry_policy(monkeypatch)


def _registry_policy(monkeypatch, *, with_claude=False, projects=(PROJECT_A,)):
    module = _module()
    native = NativeTranscriptFiles(monkeypatch)
    evidence = module._ServiceEvidence(b"r" * 32)
    control_path = Path("/fixture/monitor")

    def directory(path):
        return module._PhysicalDirectory(str(path), native._identity(path))

    control = directory(control_path)
    transcripts = directory(native.root)
    registrations = tuple(
        module.RegisteredProject(
            project,
            directory(Path(f"/fixture/project-{project.int}")),
            f"Project {project.int}",
            None,
            (),
            None,
        )
        for project in projects
    )
    if with_claude:
        from conftest import install_legacy_monitor_qualification

        install_legacy_monitor_qualification(monkeypatch, lambda: control_path)
        provider, surface, version = "claude", "claude-code-macos", "2.1.318"
    else:
        provider, surface, version = "codex", "codex-desktop-macos", "0.167.0-alpha.3.2"
    installation = _InstallationProof(
        transcripts,
        module._LiveSourceTuple(provider, surface, "Darwin", "arm64", version, 1),
        evidence.pseudonymize("executable", provider),
    )
    _, reader, root = _adapter(monkeypatch, (evidence, native.root, native.checkout))
    state = native_registry_policy(
        monkeypatch,
        native,
        control=control,
        projects=registrations,
        installations=(installation,),
        evidence=evidence,
    )
    return SimpleNamespace(
        native=native,
        module=module,
        registry=state.registry,
        reader=reader,
        root=replace(root, evidence=evidence),
        inbox=state.inbox,
    )


class _MemoryDesktopLog(_DesktopLog):
    def __init__(self, native, path, *, session=SESSION):
        self.contents = native.contents
        rows = [
            json.loads(line)
            for line in _CODEX_TRANSCRIPT.replace(
                "CHECKOUT", str(native.checkout)
            ).splitlines()
        ]
        rows[0]["payload"]["originator"] = "Codex Desktop"
        super().__init__(path, native.checkout, session=session, initial_rows=rows)

    def _emit(self, rows, *, mode):
        data = b"".join(
            json.dumps(row).replace(str(SESSION), str(self.session)).encode() + b"\n"
            for row in rows
        )
        prior = self.contents[self.path] if mode == "a" else b""
        self.contents[self.path] = prior + data

    def read_bytes(self):
        return self.contents[self.path]

    def write_bytes(self, data):
        self.contents[self.path] = data


def test_disable_reenable_excludes_late_disabled_interval(registry_policy):
    policy = registry_policy
    module, reader, root, registry = (
        policy.module,
        policy.reader,
        policy.root,
        policy.registry,
    )
    log = _MemoryDesktopLog(policy.native, root.path / "live.jsonl")
    stream = _locate(reader, root).stream_ref
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)

    def decide(start, end):
        return registry.span_disposition(PROJECT_A, SOURCE, stream, start, end)

    with registry.writer() as writer:
        _approve(writer, module, root)
        start = _advance(writer, enable, log, reader, root)
        first = writer.set_permission(enable, start)
        assert writer.set_permission(enable, start) == first
        with pytest.raises(LedgerError):
            writer.set_permission(enable, replace(start))
        with pytest.raises(LedgerError):
            writer.set_permission(enable, replace(start, ordinal=start.ordinal + 1))

        stop = _advance(writer, disable, log, reader, root)
        writer.set_permission(disable, stop)

        log.append(2)
        first_disabled, last_disabled = _boundaries(reader, _locate(reader, root))[-2:]
        reenable = writer.capture_frontier(enable, _locate(reader, root))
        with pytest.raises(module.BoundaryUnavailable):
            writer.verify_boundary(enable, _locate(reader, root), reenable)

        log.append(2)
        first_fresh, later_fresh = _boundaries(reader, _locate(reader, root))[-2:]
        restart = writer.verify_boundary(enable, _locate(reader, root), reenable)
        assert restart.boundary_ref == first_fresh.boundary_ref
        assert last_disabled.ordinal < restart.ordinal < later_fresh.ordinal
        writer.set_permission(enable, restart)
        with pytest.raises(LedgerError):
            writer.set_permission(enable, start)

    assert decide(start.ordinal, stop.ordinal) is Eligibility.ELIGIBLE
    assert decide(stop.ordinal, restart.ordinal) is Eligibility.EXCLUDED
    assert (
        decide(first_disabled.ordinal, last_disabled.ordinal + 1)
        is Eligibility.EXCLUDED
    )
    assert decide(stop.ordinal - 1, stop.ordinal + 1) is Eligibility.UNKNOWN
    assert decide(restart.ordinal, restart.ordinal + 1) is Eligibility.ELIGIBLE


def test_revoked_root_is_not_reread_for_prior_revision(registry_policy, monkeypatch):
    policy = registry_policy
    module, reader, root, registry = (
        policy.module,
        policy.reader,
        policy.root,
        policy.registry,
    )
    log = _MemoryDesktopLog(policy.native, root.path / "live.jsonl")
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    with registry.writer() as writer:
        _approve(writer, module, root)
        start = _advance(writer, enable, log, reader, root)
        writer.set_permission(enable, start)
    locator = _locate(reader, root)
    assert registry.source_read_allowed(PROJECT_A, SOURCE)
    directory = module._directory

    def replaced_source(path, **options):
        observed = directory(path, **options)
        if path == str(root.path):
            return replace(observed, identity=(1, 999))
        return observed

    monkeypatch.setattr(module, "_directory", replaced_source)
    assert not registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, locator.stream_ref, start.ordinal, start.ordinal + 1
        )
        is Eligibility.ELIGIBLE
    )

    def forbidden_read(*args, **kwargs):
        pytest.fail("The replaced native source was read")

    monkeypatch.setattr(type(reader), "read_delta", forbidden_read)
    with registry.writer() as writer, pytest.raises(LedgerError):
        writer.capture_frontier(enable, locator)


def test_shared_installation_keeps_project_permissions_independent(monkeypatch):
    module = _module()
    capture = CapturePolicy(monkeypatch, SOURCE, CUTOFF, (PROJECT_A, PROJECT_B))
    writer, locator = capture.writer, capture.first
    enable_a = module.CaptureChange(PROJECT_A, SOURCE, True)
    enable_b = replace(enable_a, project_id=PROJECT_B)
    disable_a = replace(enable_a, enabled=False)
    front_a = writer.capture_frontier(enable_a, locator)
    front_b = writer.capture_frontier(enable_b, locator)
    capture.append(locator)
    start_a = writer.verify_boundary(enable_a, locator, front_a)
    start_b = writer.verify_boundary(enable_b, locator, front_b)
    assert start_a.boundary_ref == start_b.boundary_ref
    writer.set_permission(enable_a, start_a)
    writer.set_permission(enable_b, start_b)
    stop = capture.advance(disable_a, locator)
    with pytest.raises(LedgerError, match="verified boundary"):
        writer.set_permission(replace(disable_a, project_id=PROJECT_B), stop)
    writer.set_permission(disable_a, stop)
    assert not writer.source_read_allowed(PROJECT_A, SOURCE)
    assert writer.source_read_allowed(PROJECT_B, SOURCE)


def test_destination_key_cannot_issue_a_native_capture_boundary(registry_policy):
    from aitm_usage import ledger

    policy = registry_policy
    module = policy.module
    foreign = _memory_ledger(ledger, PROJECT_A, b"d" * 32)
    root = replace(policy.root, evidence=foreign)
    _MemoryDesktopLog(policy.native, root.path / "live.jsonl")
    change = module.CaptureChange(PROJECT_A, SOURCE, True)
    with policy.registry.writer() as writer:
        _approve(writer, module, root)
        with pytest.raises(LedgerError, match="monitor source namespace"):
            writer.capture_frontier(change, _locate(policy.reader, root))


def test_adopted_path_and_key_are_pinned(tmp_path, monkeypatch):
    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    monkeypatch.setattr(module, "default_monitor_root", lambda: registry.root)
    monkeypatch.setattr(
        "aitm_usage.ledger._control_root", lambda: tmp_path / "legacy-guard"
    )
    request = _request(module, tmp_path)
    state = Path(request.state_dir)
    ledger = Ledger.initialize(state, PROJECT_A)
    with registry.writer() as writer:
        registered = writer.register_project(request)
        module.check_legacy_mutation(state)
        view = writer.view()
        writer._save(
            replace(
                view,
                projects=(replace(registered, adopted_key_id=ledger.identity.key_id),),
            )
        )
    with pytest.raises(module.ProjectAdopted):
        module.check_legacy_mutation(state)
    state.rename(state.with_name("moved-state"))
    os.mkdir(state, 0o700)
    with pytest.raises(LedgerError) as caught:
        module.check_legacy_mutation(state)
    assert not isinstance(caught.value, module.ProjectAdopted)


def test_lease_free_snapshot_read_survives_atomic_replacement(tmp_path, monkeypatch):
    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    request = _request(module, tmp_path)
    with registry.writer() as writer:
        old = writer.register_project(request)
        next_view = replace(writer.view(), projects=(replace(old, display_name="New"),))
        open_file = os.open

        def replace_after_open(path, *args, **kwargs):
            fd = open_file(path, *args, **kwargs)
            if path == module._STATE_FILE:
                writer._save(next_view)
            return fd

        with monkeypatch.context() as patch:
            patch.setattr(os, "open", replace_after_open)
            assert registry.view().projects == (old,)
        assert registry.view() == next_view


def _physical_ordinal(log):
    return log.read_bytes().count(b"\n")


class _QueuedDisable:
    def __init__(
        self, module, reader, root, registry, inbox, log, log_factory, project
    ):
        self.module, self.reader, self.root, self.log = module, reader, root, log
        self.registry, self.inbox = registry, inbox
        self.log_factory = log_factory
        self.enable = self.module.CaptureChange(PROJECT_A, SOURCE, True)
        self.disable = replace(self.enable, enabled=False)
        self.command = self.module.ControlCommand(UUID(int=300), self.disable)
        self.stream = _locate(self.reader, self.root).stream_ref
        with self.registry.writer() as writer:
            if project is not None:
                writer.register_project(project)
            _approve(writer, self.module, self.root)
            self.start = _advance(writer, self.enable, self.log, self.reader, self.root)
            writer.set_permission(self.enable, self.start)
        self.streams = {self.stream}

    def enroll_second(self):
        first = _locate(self.reader, self.root, self.stream)
        log = self.log_factory(self.root.path / "second.jsonl", session=UUID(int=999))
        (second,) = (
            item
            for item in self.reader.discover(self.root)
            if item.stream_ref != first.stream_ref
        )
        with self.registry.writer() as writer:
            proof = _advance(
                writer, self.enable, log, self.reader, self.root, second.stream_ref
            )
            writer.enroll_stream(PROJECT_A, SOURCE, proof)
        self.streams.add(second.stream_ref)
        return log, proof

    def locate(self, change, known):
        assert change == self.disable
        assert known == frozenset(self.streams)
        return tuple(self.reader.discover(self.root))

    def submit(self):
        return self.inbox.enqueue(self.command)

    def poll(self, locate=None, *, progress=()):
        registry = self.module.Registry(self.registry.root)
        with registry.writer() as writer:
            return writer.apply_pending(
                self.inbox,
                writer.lease,
                self.locate if locate is None else locate,
                progress=progress,
            )

    def status(self):
        return self.inbox.status(self.command.command_id).status

    def decide(self, stream, start, end):
        return self.registry.span_disposition(PROJECT_A, SOURCE, stream, start, end)


@pytest.fixture
def queued_disable(tmp_path, monkeypatch, source):
    from aitm_usage.monitor_control import ControlInbox

    module, reader, root, log = _native_fixture(tmp_path, monkeypatch, source)
    registry = module.Registry(tmp_path / "monitor")

    def log_factory(path, *, session):
        return _DesktopLog(path, log.checkout, session=session)

    return _QueuedDisable(
        module,
        reader,
        root,
        registry,
        ControlInbox(registry.root),
        log,
        log_factory,
        _request(module, tmp_path),
    )


@pytest.fixture
def queued_disable_policy(registry_policy):
    return _queue_on_registry_policy(registry_policy)


@pytest.fixture
def queued_disable_metadata(registry_policy, monkeypatch):
    policy = registry_policy
    NativeDirectoryMetadata(policy.native, policy.root.path).install(monkeypatch)
    return _queue_on_registry_policy(policy), policy.native


def _queue_on_registry_policy(policy):
    def log_factory(path, *, session):
        return _MemoryDesktopLog(policy.native, path, session=session)

    return _QueuedDisable(
        policy.module,
        policy.reader,
        policy.root,
        policy.registry,
        policy.inbox,
        log_factory(policy.root.path / "live.jsonl", session=SESSION),
        log_factory,
        None,
    )


def _observe_locator(monkeypatch, scenario, native, source, observe):
    """Supply a filesystem observation for the exact previously enrolled file."""

    def presence(root, evidence, locator, incarnation, *, root_identity, prior):
        assert (root, evidence) == (scenario.root.path, scenario.root.evidence)
        assert root_identity == native._identity(root)
        assert (locator, incarnation) == (source.locator_ref, source.incarnation_ref)
        assert (prior.locator_ref, prior.incarnation_ref) == (locator, incarnation)
        return observe()

    monkeypatch.setattr(scenario.module, "_capture_locator_presence", presence)


@pytest.mark.parametrize("quiet", ["idle", "removed", "removed-after-arm"])
def test_source_wide_disable_reaches_a_quiet_stream_after_restart(
    request, monkeypatch, quiet
):
    if quiet == "removed-after-arm":
        scenario, native = request.getfixturevalue("queued_disable_metadata")
    else:
        scenario = request.getfixturevalue("queued_disable_policy")
        native = request.getfixturevalue("registry_policy").native
    second_log, second_start = scenario.enroll_second()
    second_prefix = _physical_ordinal(second_log)
    scenario.log.append(2)
    first_history_end = _physical_ordinal(scenario.log)
    scenario.log.write_bytes(scenario.log.read_bytes() + b"malformed physical row\n")
    first_fence = _physical_ordinal(scenario.log)
    first_bytes = len(scenario.log.read_bytes())
    second_log.append(2)
    second_fence = _physical_ordinal(second_log)
    if quiet == "removed":
        from scanner_policy_cases import scanner

        source = _locate(
            scenario.reader, scenario.root, second_start.stream_ref
        )._source
        del native.contents[second_log.path]
        _observe_locator(
            monkeypatch,
            scenario,
            native,
            source,
            lambda: scanner._CaptureLocatorPresence(False, False, None, False, False),
        )

    status = scenario.module.ControlStatus
    assert scenario.submit().status is status.QUEUED
    assert scenario.poll() == ()
    assert scenario.status() is status.QUEUED
    assert scenario.registry.source_read_allowed(PROJECT_A, SOURCE)

    # The first arm survives writer restart and additional rows on only one stream.
    scenario.log.append(2)
    if quiet == "removed-after-arm":
        del native.contents[second_log.path]
    bound = scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream)
    assert (bound.ordinal, bound.cursor.offset) == (first_fence, first_bytes)
    second_limit = second_prefix if quiet == "removed" else second_fence
    assert (
        scenario.registry.capture_read_limit(
            PROJECT_A, SOURCE, second_start.stream_ref
        ).ordinal
        == second_limit
    )
    (receipt,) = scenario.poll()
    assert receipt.status is status.APPLIED
    assert scenario.status() is status.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream).ordinal
        == 0
    )
    fences = {
        epoch.stream_ref: epoch.ordinal
        for epoch in scenario.registry.view().epochs
        if not epoch.enabled
    }
    assert fences[scenario.stream] == first_fence
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, first_history_end)
        is Eligibility.ELIGIBLE
    )
    assert (
        scenario.decide(scenario.stream, first_fence, first_fence + 1)
        is Eligibility.EXCLUDED
    )

    second_stream = second_start.stream_ref
    end = second_prefix if quiet == "removed" else second_fence
    assert (
        scenario.decide(second_stream, second_start.ordinal, end)
        is Eligibility.ELIGIBLE
    )
    if quiet != "idle":
        assert scenario.decide(second_stream, end, end + 1) is Eligibility.UNKNOWN
    else:
        assert fences[second_stream] == second_fence
        assert scenario.decide(second_stream, end, end + 1) is Eligibility.EXCLUDED


def test_returning_original_stream_needs_prospective_enrollment(
    queued_disable_policy, registry_policy, monkeypatch
):
    from scanner_policy_cases import scanner

    scenario = queued_disable_policy
    native = registry_policy.native
    log, start = scenario.enroll_second()
    stream = start.stream_ref
    prefix = _physical_ordinal(log)
    log.append(2)
    source = _locate(scenario.reader, scenario.root, stream)._source
    stored = native.contents.pop(log.path)

    def observe():
        current = native.contents.get(log.path)
        return scanner._CaptureLocatorPresence(
            current is not None,
            current is not None,
            None if current is None else len(current),
            current is not None,
            False,
        )

    _observe_locator(monkeypatch, scenario, native, source, observe)
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED

    native.contents[log.path] = stored
    assert _locate(scenario.reader, scenario.root, stream).stream_ref == stream
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    repeated_disable = scenario.module.ControlCommand(UUID(int=199), scenario.disable)
    scenario.inbox.enqueue(repeated_disable)
    assert scenario.poll() == ()
    (repeat,) = scenario.poll()
    assert repeat.status is scenario.module.ControlStatus.APPLIED

    scenario.log.append()
    reenable = scenario.module.ControlCommand(UUID(int=200), scenario.enable)
    assert (
        scenario.inbox.enqueue(reenable).status is scenario.module.ControlStatus.QUEUED
    )

    def locate_enable(change, known):
        assert change == scenario.enable
        assert known == frozenset(scenario.streams)
        return (_locate(scenario.reader, scenario.root, scenario.stream),)

    assert scenario.poll(locate_enable) == ()
    (receipt,) = scenario.poll(locate_enable)
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert scenario.registry.capture_read_limit(PROJECT_A, SOURCE, stream).ordinal == 0
    assert scenario.decide(stream, prefix, prefix + 1) is Eligibility.UNKNOWN

    with scenario.registry.writer() as writer:
        fresh = _advance(
            writer, scenario.enable, log, scenario.reader, scenario.root, stream
        )
        writer.enroll_stream(PROJECT_A, SOURCE, fresh)
    assert scenario.decide(stream, start.ordinal, prefix) is Eligibility.ELIGIBLE
    assert scenario.decide(stream, prefix, fresh.ordinal) is Eligibility.UNKNOWN
    assert (
        scenario.decide(stream, fresh.ordinal, fresh.ordinal + 1)
        is Eligibility.ELIGIBLE
    )


def _queued_capture_policy(monkeypatch):
    module = _module()
    capture = CapturePolicy(monkeypatch, SOURCE, CUTOFF, (PROJECT_A,))
    capture.stub_native_reads(monkeypatch)
    writer = capture.writer
    change = module.CaptureChange(PROJECT_A, SOURCE, True)
    writer.set_permission(change, capture.advance(change, capture.first))
    inbox = CaptureInbox(writer)
    disable = module.ControlCommand(UUID(int=300), replace(change, enabled=False))
    inbox.pending.append(disable)
    return capture, inbox, change, disable


@pytest.mark.parametrize("locators", ["omitted", "duplicate"])
def test_ambiguous_current_locator_keeps_existing_stream_queued(monkeypatch, locators):
    capture, inbox, enable, command = _queued_capture_policy(monkeypatch)
    writer, first = capture.writer, capture.first
    second = capture.new_stream()
    writer.enroll_stream(PROJECT_A, SOURCE, capture.advance(enable, second))
    assert writer.apply_pending(inbox, writer.lease, lambda *_: (first, second)) == ()
    admitted = capture.view.epochs
    ends = (first,) if locators == "omitted" else (first, second, first)
    assert writer.apply_pending(inbox, writer.lease, lambda *_: ends) == ()
    assert inbox.pending == [command]
    assert capture.view.epochs == admitted
    (receipt,) = writer.apply_pending(inbox, writer.lease, lambda *_: (first, second))
    assert receipt.status is _module().ControlStatus.APPLIED
    assert inbox.pending == []


def test_pending_disable_prevents_new_enrollment_and_ignores_unrelated_locator(
    monkeypatch,
):
    capture, inbox, enable, command = _queued_capture_policy(monkeypatch)
    writer, first = capture.writer, capture.first
    assert writer.apply_pending(inbox, writer.lease, lambda *_: (first,)) == ()
    second = capture.new_stream()
    assert writer.capture_read_limit(PROJECT_A, SOURCE, second.stream_ref).ordinal == 0
    proof = capture.advance(enable, second)
    with pytest.raises(ConflictError, match="ordered capture command"):
        writer.enroll_stream(PROJECT_A, SOURCE, proof)
    (receipt,) = writer.apply_pending(inbox, writer.lease, lambda *_: (first, second))
    assert receipt.command_id == command.command_id
    assert receipt.status is _module().ControlStatus.APPLIED
    assert {epoch.stream_ref for epoch in capture.view.epochs} == {first.stream_ref}
    assert (
        writer.span_disposition(
            PROJECT_A, SOURCE, second.stream_ref, proof.ordinal, proof.ordinal + 1
        )
        is Eligibility.EXCLUDED
    )


@pytest.mark.parametrize("tail", ["open-turn", "partial", "completed-after-arm"])
def test_unfinished_codex_tail_fences_without_new_native_completion(request, tail):
    if tail == "partial":
        scenario, _ = request.getfixturevalue("queued_disable_metadata")
    else:
        scenario = request.getfixturevalue("queued_disable_policy")
    first_held = _physical_ordinal(scenario.log)
    if tail == "open-turn":
        scenario.log.append(complete=False)
        expected = _physical_ordinal(scenario.log)
    else:
        scenario.log.write_bytes(scenario.log.read_bytes() + b'{"type":"private-test"')
        expected = first_held + 1

    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    if tail == "completed-after-arm":
        scenario.log.write_bytes(scenario.log.read_bytes() + b"}\n")
        scenario.log.append()

    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    (epoch,) = (epoch for epoch in scenario.registry.view().epochs if not epoch.enabled)
    assert epoch.ordinal == expected
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, first_held)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, first_held, expected) is Eligibility.UNKNOWN
    assert (
        scenario.decide(scenario.stream, first_held - 1, expected + 1)
        is Eligibility.UNKNOWN
    )
    assert (
        scenario.decide(scenario.stream, expected, expected + 1) is Eligibility.EXCLUDED
    )


def test_replay_syncs_existing_registry_receipt_before_retiring_queue(
    tmp_path, monkeypatch
):
    from aitm_usage.monitor_control import ControlInbox

    module = _module()
    registry = module.Registry(tmp_path / "monitor")
    inbox = ControlInbox(registry.root)
    command = module.ControlCommand(UUID(int=301), _request(module, tmp_path))
    with registry.writer() as writer:
        inbox.enqueue(command)
        registry_identity = registry.root.stat()
        original_sync = os.fsync
        original_discard = inbox.discard
        synced = False

        def fail_after_replace(fd):
            if os.path.samestat(os.fstat(fd), registry_identity):
                raise OSError("injected registry directory sync failure")
            original_sync(fd)

        with monkeypatch.context() as patch:
            patch.setattr(os, "fsync", fail_after_replace)
            with pytest.raises(LedgerError, match="Private monitor publication failed"):
                writer.apply_pending(inbox, writer.lease, None)
        assert registry.view().receipts[0].status is module.ControlStatus.APPLIED

        def record_sync(fd):
            nonlocal synced
            original_sync(fd)
            if os.path.samestat(os.fstat(fd), registry_identity):
                synced = True

        def discard_after_sync(*args):
            assert synced
            return original_discard(*args)

        with monkeypatch.context() as patch:
            patch.setattr(os, "fsync", record_sync)
            patch.setattr(inbox, "discard", discard_after_sync)
            assert writer.apply_pending(inbox, writer.lease, None) == ()
    assert inbox.status(command.command_id).status is module.ControlStatus.APPLIED
    assert len(registry.view().projects) == 1


def test_new_stream_enrolls_only_while_source_permission_is_enabled(monkeypatch):
    module = _module()
    capture = CapturePolicy(monkeypatch, SOURCE, CUTOFF, (PROJECT_A,))
    writer, first = capture.writer, capture.first
    second = capture.new_stream()
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    another = capture.advance(enable, second)
    with pytest.raises(ConflictError, match="disabled"):
        writer.enroll_stream(PROJECT_A, SOURCE, another)
    wrong_stream = capture.advance(disable, second)
    with pytest.raises(ConflictError, match="unadmitted"):
        writer.set_permission(disable, wrong_stream)
    start = capture.advance(enable, first)
    writer.set_permission(enable, start)
    assert (
        writer.span_disposition(
            PROJECT_A, SOURCE, second.stream_ref, another.ordinal, another.ordinal + 1
        )
        is Eligibility.EXCLUDED
    )
    fresh = capture.advance(enable, second)
    epoch = writer.enroll_stream(PROJECT_A, SOURCE, fresh)
    assert writer.enroll_stream(PROJECT_A, SOURCE, fresh) == epoch
    assert (
        writer.span_disposition(
            PROJECT_A, SOURCE, second.stream_ref, fresh.ordinal, fresh.ordinal + 1
        )
        is Eligibility.ELIGIBLE
    )


def test_historical_boundary_cannot_disable_previously_admitted_usage(monkeypatch):
    module = _module()
    capture = CapturePolicy(monkeypatch, SOURCE, CUTOFF, (PROJECT_A,))
    writer, locator = capture.writer, capture.first
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    early = writer.capture_frontier(enable, locator)
    capture.append(locator)
    start = writer.verify_boundary(enable, locator, early)
    writer.set_permission(enable, start)

    admitted, newest = capture.append(locator, 2)
    frontier = writer.capture_frontier(disable, locator)
    with pytest.raises(LedgerError, match="current armed frontier"):
        writer.verify_boundary(disable, locator, early)
    with pytest.raises(module.BoundaryUnavailable):
        writer.verify_boundary(disable, locator, frontier)
    capture.append(locator)
    stop = writer.verify_boundary(disable, locator, frontier)
    assert newest.ordinal < stop.ordinal
    writer.set_permission(disable, stop)
    assert (
        writer.span_disposition(
            PROJECT_A, SOURCE, locator.stream_ref, admitted.ordinal, stop.ordinal
        )
        is Eligibility.ELIGIBLE
    )


@pytest.mark.parametrize("failure", ["io", "proof"])
def test_transient_native_read_failure_leaves_capture_command_queued(
    monkeypatch, failure
):
    capture, inbox, _, command = _queued_capture_policy(monkeypatch)
    writer = capture.writer
    module = _module()

    def unavailable(change, known):
        assert change == command.payload and known == {capture.first.stream_ref}
        if failure == "io":
            raise OSError("native file is temporarily unavailable")
        raise module.BoundaryUnavailable("native boundary is temporarily unavailable")

    before = capture.view
    assert writer.apply_pending(inbox, writer.lease, unavailable) == ()
    assert inbox.pending == [command]
    assert capture.view.receipts == before.receipts
    assert capture.view.epochs == before.epochs
    assert writer.source_read_allowed(PROJECT_A, SOURCE)


def test_capture_frontier_waits_for_complete_native_tail(registry_policy):
    policy = registry_policy
    module, reader, root = policy.module, policy.reader, policy.root
    log = _MemoryDesktopLog(policy.native, root.path / "live.jsonl")
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    with policy.registry.writer() as writer:
        _approve(writer, module, root)
        complete = log.contents[log.path]
        log.contents[log.path] = complete + b'{"type":"event_msg"'
        with pytest.raises(module.BoundaryUnavailable):
            writer.capture_frontier(enable, _locate(reader, root))
        log.contents[log.path] = complete
        proof = _advance(writer, enable, log, reader, root)
        assert writer.set_permission(enable, proof).enabled


def test_rearming_a_capture_change_invalidates_earlier_native_proof(monkeypatch):
    module = _module()
    capture = CapturePolicy(monkeypatch, SOURCE, CUTOFF, (PROJECT_A,))
    writer, locator = capture.writer, capture.first
    change = module.CaptureChange(PROJECT_A, SOURCE, True)
    old_proof = capture.advance(change, locator)
    capture.append(locator)
    current = writer.capture_frontier(change, locator)
    with pytest.raises(LedgerError, match="verified boundary"):
        writer.set_permission(change, old_proof)
    with pytest.raises(LedgerError, match="current armed frontier"):
        writer.verify_boundary(change, locator, replace(current))
    with pytest.raises(module.BoundaryUnavailable):
        writer.verify_boundary(change, locator, current)
    capture.append(locator)
    fresh = writer.verify_boundary(change, locator, current)
    assert fresh.ordinal > old_proof.ordinal
    assert writer.set_permission(change, fresh).enabled


@pytest.mark.parametrize(
    "interruption", ["root-replacement", "platform", "native-version", "truncated"]
)
def test_disable_commits_with_last_verified_prefix_when_source_changes(
    request, monkeypatch, interruption
):
    if interruption == "truncated":
        scenario, _ = request.getfixturevalue("queued_disable_metadata")
    else:
        fixture = (
            "queued_disable"
            if interruption == "root-replacement"
            else "queued_disable_policy"
        )
        scenario = request.getfixturevalue(fixture)
    prefix = _physical_ordinal(scenario.log)
    scenario.log.append(2)
    original = scenario.log.read_bytes()
    locator = _locate(scenario.reader, scenario.root)
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED

    def locate(_change, known):
        assert known == frozenset({scenario.stream})
        return (locator,)

    with monkeypatch.context() as patch:
        if interruption == "root-replacement":
            path = scenario.root.path
            moved = path.with_name("original-approved-root")
            path.rename(moved)
            path.mkdir()
            scenario.log.write_bytes(original)

            def unexpected_discovery(*args):
                pytest.fail("The replacement root was read")

            patch.setattr(type(scenario.reader), "discover", unexpected_discovery)
        elif interruption == "platform":
            patch.setattr(scenario.module.platform, "machine", lambda: "unsupported")
        elif interruption == "native-version":
            changed = original.replace(b"0.167.0-alpha.3.2", b"0.167.0-alpha.3.9", 1)
            assert changed != original
            scenario.log.write_bytes(changed)
        else:
            scenario.log.write_bytes(b"")

        applied = scenario.poll(locate)
        if not applied:
            applied = scenario.poll(locate)
        (receipt,) = applied
        assert receipt.status is scenario.module.ControlStatus.APPLIED
        assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)

    if interruption == "root-replacement":
        scenario.log.path.unlink()
        path.rmdir()
        moved.rename(path)
    if interruption in {"truncated", "native-version"}:
        scenario.log.write_bytes(original)

    assert scenario.status() is scenario.module.ControlStatus.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, prefix)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, prefix, prefix + 1) is Eligibility.UNKNOWN


def test_armed_prefix_mutation_gaps_only_the_unverified_tail(queued_disable_metadata):
    scenario, _ = queued_disable_metadata
    prefix = _physical_ordinal(scenario.log)
    scenario.log.append(2)
    before = scenario.log.read_bytes()
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()

    # Preserve inode, size, native startup, and session while changing bytes
    # covered by the persisted physical arm.
    after = before.replace(b"response-4", b"modified-4", 1)
    assert after != before and len(after) == len(before)
    scenario.log.write_bytes(after)
    (receipt,) = scenario.poll()

    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, prefix)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, prefix, prefix + 1) is Eligibility.UNKNOWN


@pytest.mark.parametrize("unfinished", ["quiet", "streamed", "tool", "abandoned"])
def test_queued_claude_disable_uses_the_physical_tail(request, monkeypatch, unfinished):
    from test_claude import request as claude_request
    from test_claude import user as claude_user
    from test_claude import write as write_claude

    from aitm_usage.monitor_control import ControlInbox

    module = _module()
    if unfinished == "tool":
        source = request.getfixturevalue("source")
        tmp_path = request.getfixturevalue("tmp_path")
        _, reader, root = _adapter(monkeypatch, source)
        _, directory, checkout = source
        registry = module.Registry(tmp_path / "monitor")
        inbox = ControlInbox(registry.root)
        path = directory / "claude.jsonl"

        def store(rows, *, append=False):
            write_claude(path, rows, append=append)

        def ordinal():
            return path.read_bytes().count(b"\n")
    else:
        policy = _registry_policy(monkeypatch, with_claude=True)
        registry, inbox = policy.registry, policy.inbox
        reader, root = policy.reader, policy.root
        checkout = policy.native.checkout
        path = root.path / "claude.jsonl"
        if unfinished == "abandoned":
            NativeDirectoryMetadata(policy.native, root.path).install(monkeypatch)

        def store(rows, *, append=False):
            policy.native.write(path, rows, append=append)

        def ordinal():
            return policy.native.contents[path].count(b"\n")

    rows, _ = _restart_rows("streamed", checkout)
    store(rows[:1])
    enable = module.CaptureChange(PROJECT_A, SOURCE, True)
    disable = replace(enable, enabled=False)
    command = module.ControlCommand(UUID(int=330), disable)

    def append_request(turn, *, stop, content=()):
        prompt = str(UUID(int=500 + 2 * turn))
        reply = str(UUID(int=501 + 2 * turn))
        time = AFTER + timedelta(seconds=10 + turn)
        store(
            [
                claude_user(checkout, time=time, uuid=prompt, isSidechain=False),
                claude_request(
                    checkout,
                    time=time,
                    uuid=reply,
                    parentUuid=prompt,
                    req=f"test-request-{turn}",
                    msg=f"test-message-{turn}",
                    stop=stop,
                    content=content,
                    isSidechain=False,
                ),
            ],
            append=True,
        )

    def locate(change, known):
        assert change in (disable, enable)
        assert known == frozenset({start.stream_ref})
        return tuple(reader.discover(root))

    with registry.writer() as writer:
        root = replace(root, evidence=writer.source_evidence())
        if unfinished == "tool":
            writer.register_project(_request(module, tmp_path))
        writer.approve_source(
            module.SourceApprovalRequest(
                SOURCE,
                "claude",
                "claude-code-macos",
                "Darwin",
                "arm64",
                "2.1.318",
                1,
                str(root.path),
            )
        )
        frontier = writer.capture_frontier(enable, _locate(reader, root))
        store(rows[1:], append=True)
        start = writer.verify_boundary(enable, _locate(reader, root), frontier)
        writer.set_permission(enable, start)
        append_request(2, stop="end_turn")
        admitted_end = ordinal()
        if unfinished in {"streamed", "abandoned"}:
            append_request(3, stop=None)
        if unfinished == "abandoned":
            completed_start = ordinal()
            append_request(4, stop="end_turn")
            append_request(5, stop="end_turn")
        if unfinished == "tool":
            append_request(
                3,
                stop="tool_use",
                content=[
                    {
                        "type": "tool_use",
                        "id": "agent-open",
                        "name": "Agent",
                        "input": {},
                    }
                ],
            )
        expected = ordinal()
        assert inbox.enqueue(command).status is module.ControlStatus.QUEUED
        assert writer.apply_pending(inbox, writer.lease, locate) == ()

    with registry.writer() as writer:
        (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
    assert receipt.status is module.ControlStatus.APPLIED
    assert registry.view().epochs[-1].ordinal == expected
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, start.stream_ref, start.ordinal, admitted_end
        )
        is Eligibility.ELIGIBLE
    )
    assert (
        registry.span_disposition(
            PROJECT_A, SOURCE, start.stream_ref, expected, expected + 1
        )
        is Eligibility.EXCLUDED
    )
    if unfinished in {"streamed", "tool"}:
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, admitted_end + 1, expected
            )
            is Eligibility.UNKNOWN
        )
    if unfinished == "abandoned":
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, completed_start, expected
            )
            is Eligibility.ELIGIBLE
        )
        append_request(6, stop="end_turn")
        append_request(7, stop=None)
        enabled_at = ordinal()
        resume = module.ControlCommand(UUID(int=331), enable)
        assert inbox.enqueue(resume).status is module.ControlStatus.QUEUED
        with registry.writer() as writer:
            assert writer.apply_pending(inbox, writer.lease, lambda *_: ()) == ()
        assert inbox.status(resume.command_id).status is module.ControlStatus.QUEUED
        with registry.writer() as writer:
            assert writer.apply_pending(inbox, writer.lease, locate) == ()
        with registry.writer() as writer:
            (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
        assert (receipt.command_id, receipt.status) == (
            resume.command_id,
            module.ControlStatus.APPLIED,
        )
        assert registry.view().epochs[-1].ordinal == enabled_at
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, completed_start, expected
            )
            is Eligibility.ELIGIBLE
        )
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, expected, enabled_at
            )
            is Eligibility.EXCLUDED
        )
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, enabled_at, enabled_at + 1
            )
            is Eligibility.ELIGIBLE
        )
        assert (
            registry.span_disposition(
                PROJECT_A, SOURCE, start.stream_ref, enabled_at - 1, enabled_at + 1
            )
            is Eligibility.UNKNOWN
        )


def test_reappearing_stream_invalidates_an_earlier_absence(queued_disable_metadata):
    scenario, native = queued_disable_metadata
    log, start = scenario.enroll_second()
    prefix = _physical_ordinal(log)
    log.append()
    returned_fence = _physical_ordinal(log)
    stored = native.contents.pop(log.path)
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()

    native.contents[log.path] = stored
    assert scenario.poll() == ()
    assert scenario.status() is scenario.module.ControlStatus.QUEUED
    assert (
        scenario.registry.capture_read_limit(
            PROJECT_A, SOURCE, start.stream_ref
        ).ordinal
        == returned_fence
    )

    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert (
        scenario.decide(start.stream_ref, start.ordinal, prefix) is Eligibility.ELIGIBLE
    )
    assert (
        scenario.decide(start.stream_ref, prefix, returned_fence) is Eligibility.UNKNOWN
    )
    assert (
        scenario.decide(start.stream_ref, returned_fence, returned_fence + 1)
        is Eligibility.EXCLUDED
    )


def test_native_parser_valueerror_keeps_disable_queued_with_prior_read_bound(
    queued_disable_policy, monkeypatch
):
    scenario = queued_disable_policy
    prefix = _physical_ordinal(scenario.log)
    scenario.log.append()
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED

    def failed_parse(*args, **kwargs):
        raise ValueError("native parse is temporarily unavailable")

    with monkeypatch.context() as patch:
        patch.setattr(type(scenario.reader), "_capture_gap_start", failed_parse)
        assert scenario.poll() == ()
    assert scenario.status() is scenario.module.ControlStatus.QUEUED
    assert (
        scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream).ordinal
        == prefix
    )

    scenario.log.append()
    late_fence = _physical_ordinal(scenario.log)
    assert scenario.poll() == ()
    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert scenario.decide(scenario.stream, prefix, late_fence) is Eligibility.UNKNOWN
    assert (
        scenario.decide(scenario.stream, late_fence, late_fence + 1)
        is Eligibility.EXCLUDED
    )


def test_later_enable_obeys_durable_submission_order(monkeypatch):
    capture, inbox, enable, disable = _queued_capture_policy(monkeypatch)
    module = _module()
    writer, first = capture.writer, capture.first
    reenable = module.ControlCommand(UUID(int=200), enable)
    inbox.pending.append(reenable)

    def locate(change, known):
        assert change in (disable.payload, enable)
        assert known == {first.stream_ref}
        return (first,)

    assert writer.apply_pending(inbox, writer.lease, locate) == ()
    (arm,) = capture.view.pending_capture[0].arms
    capture.append(first)
    (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
    assert (receipt.command_id, receipt.status) == (
        disable.command_id,
        module.ControlStatus.APPLIED,
    )
    assert not writer.source_read_allowed(PROJECT_A, SOURCE)
    assert inbox.pending == [reenable]

    (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
    assert (receipt.command_id, receipt.status) == (
        reenable.command_id,
        module.ControlStatus.APPLIED,
    )
    assert inbox.pending == []
    assert writer.source_read_allowed(PROJECT_A, SOURCE)
    enabled = capture.view.epochs[-1].ordinal
    assert enabled > arm.ordinal
    assert (
        writer.span_disposition(
            PROJECT_A, SOURCE, first.stream_ref, arm.ordinal, enabled
        )
        is Eligibility.EXCLUDED
    )
    assert (
        writer.span_disposition(
            PROJECT_A, SOURCE, first.stream_ref, enabled, enabled + 1
        )
        is Eligibility.ELIGIBLE
    )


def test_persisted_collection_progress_survives_a_later_truncation(
    queued_disable_metadata,
):
    scenario, _ = queued_disable_metadata
    scenario.log.append()
    retained = scenario.log.read_bytes()
    scenario.log.append(2)
    locator = _locate(scenario.reader, scenario.root, scenario.stream)
    checkpoint = scenario.reader.read_delta(locator, None).cursor.checkpoint
    with scenario.registry.writer() as writer:
        progress = writer.capture_progress(scenario.enable, locator, checkpoint)
    assert progress.ordinal == _physical_ordinal(scenario.log)
    scenario.log.write_bytes(retained)

    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    forged = replace(progress, ordinal=progress.ordinal + 1)
    assert scenario.poll(progress=(forged,)) == ()
    assert scenario.status() is scenario.module.ControlStatus.QUEUED
    assert scenario.poll(progress=(progress,)) == ()
    bound = scenario.registry.capture_read_limit(PROJECT_A, SOURCE, scenario.stream)
    assert (bound.ordinal, bound.cursor) == (progress.ordinal, progress.cursor)

    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, progress.ordinal)
        is Eligibility.ELIGIBLE
    )
    assert (
        scenario.decide(scenario.stream, progress.ordinal, progress.ordinal + 1)
        is Eligibility.UNKNOWN
    )


def test_capture_disable_detects_an_in_place_native_session_replacement(
    queued_disable_policy, registry_policy, monkeypatch
):
    from scanner_policy_cases import scanner

    scenario = queued_disable_policy
    native = registry_policy.native
    prefix = _physical_ordinal(scenario.log)
    original = scenario.log.read_bytes()
    source = _locate(scenario.reader, scenario.root)._source
    rewritten = original.replace(str(SESSION).encode(), str(UUID(int=999)).encode())
    assert len(rewritten) == len(original) and rewritten != original
    scenario.log.write_bytes(rewritten)
    assert _locate(scenario.reader, scenario.root).stream_ref != scenario.stream

    _observe_locator(
        monkeypatch,
        scenario,
        native,
        source,
        lambda: scanner._CaptureLocatorPresence(True, True, len(rewritten), True, True),
    )
    assert scenario.submit().status is scenario.module.ControlStatus.QUEUED
    assert scenario.poll() == ()
    (receipt,) = scenario.poll()
    assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert (
        scenario.decide(scenario.stream, scenario.start.ordinal, prefix)
        is Eligibility.ELIGIBLE
    )
    assert scenario.decide(scenario.stream, prefix, prefix + 1) is Eligibility.UNKNOWN


def test_disable_future_enrollment_while_approved_root_is_unavailable(monkeypatch):
    policy = _registry_policy(monkeypatch, projects=(PROJECT_A, PROJECT_B))
    scenario = _queue_on_registry_policy(policy)
    enable = replace(scenario.enable, project_id=PROJECT_B)
    disable = replace(enable, enabled=False)
    scenario.inbox.enqueue(scenario.module.ControlCommand(UUID(int=402), enable))
    with scenario.registry.writer() as writer:
        (enabled,) = writer.apply_pending(scenario.inbox, writer.lease, None)
    assert enabled.status is scenario.module.ControlStatus.APPLIED
    assert scenario.registry.source_read_allowed(PROJECT_B, SOURCE)

    directory = scenario.module._directory

    def unavailable(path, **options):
        if path == str(scenario.root.path):
            raise FileNotFoundError(path)
        return directory(path, **options)

    with monkeypatch.context() as patch:
        patch.setattr(scenario.module, "_directory", unavailable)
        scenario.inbox.enqueue(scenario.module.ControlCommand(UUID(int=403), disable))
        with scenario.registry.writer() as writer:
            (receipt,) = writer.apply_pending(scenario.inbox, writer.lease, None)
        assert receipt.status is scenario.module.ControlStatus.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_B, SOURCE)


@pytest.mark.parametrize("callback", ["supplied", "omitted"])
@pytest.mark.parametrize("timing", ["before-arm", "after-arm"])
@pytest.mark.parametrize("reuse_name", [False, True], ids=["vacant", "occupied"])
def test_moved_enrolled_stream_does_not_stall_disable(
    request, monkeypatch, callback, timing, reuse_name
):
    durable = (reuse_name, timing, callback) == (True, "after-arm", "omitted")
    fixture = "queued_disable" if durable else "queued_disable_policy"
    scenario = request.getfixturevalue(fixture)
    native = None if durable else request.getfixturevalue("registry_policy").native
    log, start = scenario.enroll_second()
    prefix = _physical_ordinal(log)
    stream = start.stream_ref
    scenario.log.append(2)
    log.append(2)
    healthy_fence = _physical_ordinal(scenario.log)
    archive = scenario.root.path / "archive"
    old_path = log.path

    if native is None:
        archive.mkdir()
        original = old_path.stat()

        def archive_stream():
            log.path = old_path.rename(archive / old_path.name)
            assert os.path.samestat(log.path.stat(), original)
            if reuse_name:
                replacement = _DesktopLog(
                    old_path, log.checkout, session=UUID(int=1000)
                )
                assert not os.path.samestat(replacement.path.stat(), original)
            assert (
                _locate(scenario.reader, scenario.root, stream)._source._path
                == log.path
            )

    else:
        from scanner_policy_cases import scanner

        original = native._identity(old_path)
        old = _locate(scenario.reader, scenario.root, stream)._source

        def transcripts(descriptor, root):
            assert native._identity(root) == descriptor
            return sorted(path for path in native.contents if path.is_relative_to(root))

        monkeypatch.setattr(scanner, "_transcripts", transcripts)
        monkeypatch.setattr(
            scanner,
            "_within_source_roots",
            lambda candidate: (
                candidate._path in native.contents
                and candidate._path.is_relative_to(scenario.root.path)
            ),
        )

        def archive_stream():
            log.path = archive / old_path.name
            native.contents[log.path] = native.contents.pop(old_path)
            native.identities[log.path] = native.identities.pop(old_path)
            assert native._identity(log.path) == original
            if reuse_name:
                _MemoryDesktopLog(native, old_path, session=UUID(int=1000))
                assert native._identity(old_path) != original
            assert (
                _locate(scenario.reader, scenario.root, stream)._source._path
                == log.path
            )

            _observe_locator(
                monkeypatch,
                scenario,
                native,
                old,
                lambda: scanner._CaptureLocatorPresence(
                    at_locator=reuse_name,
                    same_incarnation=True,
                    locator_size=len(native.contents[old_path]) if reuse_name else None,
                    locator_is_original=False,
                    prefix_changed=False,
                ),
            )

    def locate(change, known):
        assert change in (scenario.disable, scenario.enable)
        assert known == frozenset(scenario.streams)
        candidates = tuple(scenario.reader.discover(scenario.root))
        if callback == "supplied":
            return candidates
        return tuple(item for item in candidates if item.stream_ref != stream)

    if timing == "before-arm":
        archive_stream()
    status = scenario.module.ControlStatus
    assert scenario.submit().status is status.QUEUED
    if timing == "after-arm":
        assert scenario.poll() == ()
        archive_stream()
    else:
        assert scenario.poll(locate) == ()
    assert scenario.status() is status.QUEUED
    (disabled,) = scenario.poll(locate)
    assert disabled.status is status.APPLIED
    assert not scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert scenario.decide(stream, start.ordinal, prefix) is Eligibility.ELIGIBLE
    assert scenario.decide(stream, prefix, prefix + 1) is Eligibility.UNKNOWN

    scenario.log.append()
    enabled_at = _physical_ordinal(scenario.log)
    resume = scenario.module.ControlCommand(UUID(int=322), scenario.enable)
    assert scenario.inbox.enqueue(resume).status is status.QUEUED
    assert scenario.poll(locate) == ()
    (enabled,) = scenario.poll(locate)
    assert (enabled.command_id, enabled.status) == (resume.command_id, status.APPLIED)
    assert scenario.registry.source_read_allowed(PROJECT_A, SOURCE)
    assert scenario.registry.capture_read_limit(PROJECT_A, SOURCE, stream).ordinal == 0
    assert scenario.decide(scenario.stream, healthy_fence, enabled_at) is (
        Eligibility.EXCLUDED
    )
    assert scenario.decide(scenario.stream, enabled_at, enabled_at + 1) is (
        Eligibility.ELIGIBLE
    )

    with scenario.registry.writer() as writer, pytest.raises(LedgerError):
        moved_proof = _advance(
            writer, scenario.enable, log, scenario.reader, scenario.root, stream
        )
        writer.enroll_stream(PROJECT_A, SOURCE, moved_proof)
    assert scenario.decide(stream, start.ordinal, prefix) is Eligibility.ELIGIBLE
    assert (
        scenario.decide(stream, prefix, _physical_ordinal(log)) is Eligibility.UNKNOWN
    )
