"""An owned Grok UserPromptSubmit must carry one exact sealed scope proposal."""

import json
import os
import stat
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from grok_capture_policy_cases import grok_capture_policy as grok_capture_policy
from test_grok import PROMPT_A, PROMPT_B, SESSION
from test_monitor_grok_capture import isolated_grok_capture  # noqa: F401, F811

from aitm_usage import process_identity, scope_admission
from aitm_usage.ledger import ConflictError, LedgerError
from aitm_usage.monitor_control import ControlInbox, ScopeInboxReader
from aitm_usage.monitor_registry import _ServiceEvidence
from aitm_usage.monitor_scope import HandoffStatus, Scope, resolve_route
from aitm_usage.types import DiagnosticCode, ItemKey, ItemKind, WorkPhase


def _scope_proposal(f):
    inbox = ControlInbox(f.writer.root)
    reader = ScopeInboxReader(f.writer, inbox)
    grant = UUID(int=33501)
    reader.register(grant, f.project, ("mark",))
    command = scope_admission.MarkRequest(
        UUID(int=33502),
        grant,
        Scope(f.project, ItemKey(ItemKind.ISSUE, 335), WorkPhase.PLANNING),
    )
    reader.advertise(reader.probe(command))
    assert inbox.enqueue_scope(command)
    return reader, command


@pytest.fixture
def staged_scope(
    isolated_grok_capture,  # noqa: F811
    tmp_path,
    monkeypatch,
):
    f = isolated_grok_capture
    reader, command = _scope_proposal(f)
    checkout = tmp_path / "checkout"
    process = process_identity.ProcessIdentity(
        33503,
        datetime.now(UTC),
        tmp_path / "image" / "candidate",
    )
    monkeypatch.setattr(
        process_identity,
        "read_process_identity",
        lambda pid: process if pid == process.pid else None,
    )
    return f, reader, command, checkout, process


@pytest.fixture
def staged_scope_policy(grok_capture_policy, monkeypatch):
    from hashlib import sha256
    from io import BytesIO

    from monitor_inbox_cases import MonitorInboxFiles

    f = grok_capture_policy
    initial = f.writer.view()
    files = MonitorInboxFiles(
        monkeypatch, f.project, writer=f.writer, initial_view=initial
    )
    f.scope_files = files
    (project,) = initial.projects
    (checkout,) = project.anchors
    files.identities[checkout.path] = checkout
    files.files[f.writer.root][scope_admission._GROK_QUALIFICATION_RECORD] = (
        b"fixture qualification revision"
    )

    def publish(directory, name, data, *, replace_pending=False, before_commit=None):
        if not replace_pending:
            return files.publish(directory, name, data, before_commit=before_commit)
        assert directory.path.name == scope_admission._GROK_RECEIPTS
        before_commit()
        files.files[directory.path][name] = data
        return True

    monkeypatch.setattr(scope_admission, "_publish", publish)
    monkeypatch.setattr(
        scope_admission,
        "_read_state",
        lambda directory, name, _limit: files.read(directory, name),
    )
    image = Path("/fixture/image/candidate")
    image_bytes = b"bounded executable fixture"
    image_stat = SimpleNamespace(
        st_mode=stat.S_IFREG | 0o700,
        st_dev=3,
        st_ino=17,
        st_size=len(image_bytes),
        st_mtime_ns=71,
    )
    profile = f.writer._live_profile
    (installation,) = profile.installations
    executable = f.writer.source_evidence().pseudonymize(
        "isolated-executable-v1", sha256(image_bytes).hexdigest()
    )
    f.writer._live_profile = replace(
        profile, installations=(replace(installation, executable=executable),)
    )

    def revise(operation, generation):
        assert operation in ("replace", "revoke") and generation == 2
        files.files[f.writer.root][scope_admission._GROK_QUALIFICATION_RECORD] = (
            f"{operation} qualification revision {generation}".encode()
        )
        profile = f.writer._live_profile
        f.writer._live_profile = (
            None
            if operation == "revoke"
            else replace(
                profile,
                generation=f.writer.source_evidence().pseudonymize(
                    "generation", str(generation)
                ),
            )
        )

    f.revise = revise
    path_stat, path_open = Path.stat, Path.open

    def stat_file(path, **options):
        if path == image:
            assert options == {"follow_symlinks": False}
            return image_stat
        return path_stat(path, **options)

    def open_file(path, *args, **options):
        if path == image:
            assert args == ("rb",) and not options
            return BytesIO(image_bytes)
        return path_open(path, *args, **options)

    monkeypatch.setattr(Path, "stat", stat_file)
    monkeypatch.setattr(Path, "open", open_file)
    process = process_identity.ProcessIdentity(33503, datetime.now(UTC), image)
    monkeypatch.setattr(
        process_identity, "process_reference_domain", lambda: "scope-fixture:"
    )
    monkeypatch.setattr(
        process_identity,
        "read_process_identity",
        lambda pid: process if pid == process.pid else None,
    )
    reader, command = _scope_proposal(f)
    return f, reader, command, Path(checkout.path), process


def _stage(f, command, checkout, process, session=SESSION):
    return scope_admission.stage_grok_attempt(
        f.writer, f.source_id, command.command_id, session, checkout, process.pid
    )


def test_one_use_receipt_routes_only_the_original_verified_mark(
    staged_scope, monkeypatch
):
    from aitm_usage.sources import grok_scope_hook

    f, _, command, checkout, process = staged_scope
    monkeypatch.setattr(grok_scope_hook, "_has_process_ancestor", lambda *_: True)
    staged = _stage(f, command, checkout, process)
    assert _stage(f, command, checkout, process) == staged
    lookup = scope_admission.grok_receipt_lookup(f.writer, f.source_id, checkout)
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    f.reader.verify_receipt = lookup
    f.submit(33504, True)
    assert f.evaluate()
    assert scope_admission.bind_grok_prompt(
        f.writer.root, staged, SESSION, PROMPT_A, checkout
    )
    assert scope_admission.bind_grok_prompt(
        f.writer.root, staged, SESSION, PROMPT_A, checkout
    )
    with pytest.raises((ConflictError, LedgerError)):
        scope_admission.bind_grok_prompt(
            f.writer.root, staged, SESSION, PROMPT_B, checkout
        )
    f.write([*f.rows[:6], *f.rows[7:]], 2)
    batch = f.state.read_source(f.source_id, f.locator())
    (boundary,) = batch.boundaries
    with scope_admission.grok_mark(f.writer, command, f.source_id, checkout) as mark:
        owner = f.state.operator(f.project)
        f.state.authorize(mark, owner)
        proof = f.state.verify_boundary(mark, owner, batch, boundary)
        assert f.state.apply_mark(mark, proof).status is HandoffStatus.APPLIED
    view = f.state.view(batch)
    marked, hookless = (
        resolve_route(row, f.writer.view(), view) for row in batch.observations
    )
    assert marked.scope == command.scope
    assert hookless.project_id == f.project and hookless.scope is None


def test_exact_command_cannot_be_reused_in_another_session(staged_scope_policy):
    f, _, command, checkout, process = staged_scope_policy
    _stage(f, command, checkout, process)
    with pytest.raises((ConflictError, LedgerError)):
        _stage(f, command, checkout, process, "10000000-0000-4000-8000-000000000335")


def test_original_owner_and_live_process_are_required(staged_scope_policy):
    from aitm_usage.monitor_registry import _PhysicalDirectory

    f, _, command, checkout, process = staged_scope_policy
    rival = checkout.with_name("rival")
    f.scope_files.identities[str(rival)] = _PhysicalDirectory(str(rival), (2, 11))
    with pytest.raises(LedgerError, match="checkout"):
        _stage(f, command, rival, process)
    with pytest.raises(LedgerError):
        _stage(f, replace(command, command_id=UUID(int=33510)), checkout, process)
    with pytest.raises(LedgerError, match="native process is unavailable"):
        _stage(f, command, checkout, replace(process, pid=process.pid + 1))
    assert _stage(f, command, checkout, process)


def _ready_scope(staged_scope, monkeypatch):
    from aitm_usage.sources import grok_scope_hook

    f, reader, request, checkout, process = staged_scope
    monkeypatch.setattr(grok_scope_hook, "_has_process_ancestor", lambda *_: True)
    attempt = _stage(f, request, checkout, process)
    lookup = scope_admission.grok_receipt_lookup(f.writer, f.source_id, checkout)
    f.reader.verify_receipt = lookup
    f.submit(33505, True)
    assert f.evaluate()
    bind = scope_admission.bind_grok_prompt
    return f, reader, request, checkout, attempt, lookup, bind


def test_read_only_native_lookup_survives_renewal_and_refuses_rotated_or_revoked_scope(
    staged_scope,
    monkeypatch,
):
    f, reader, request, checkout, attempt, lookup, bind = _ready_scope(
        staged_scope, monkeypatch
    )
    original = bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)

    def tree_metadata():
        return {
            path.relative_to(f.writer.root): (
                entry.st_ino,
                entry.st_mtime_ns,
                entry.st_size,
            )
            for path in f.writer.root.rglob("*")
            if (entry := path.stat())
        }

    snapshot = tree_metadata()
    with ControlInbox(f.writer.root).publication():
        assert lookup(SESSION, PROMPT_A, "native-event") == original
    assert tree_metadata() == snapshot
    reader.advertise(reader.probe(request))
    assert lookup(SESSION, PROMPT_A, "native-event") == original
    reader.revoke(request.grant_id)
    assert lookup(SESSION, PROMPT_A, "native-event") is None
    with pytest.raises(LedgerError):
        bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)


def test_a_competing_pending_mark_cannot_replace_the_session_or_publisher(
    staged_scope_policy,
    monkeypatch,
):
    from aitm_usage.sources import grok_scope_hook

    f, reader, request, checkout, process = staged_scope_policy
    attempt = _stage(f, request, checkout, process)
    other = replace(request, command_id=UUID(int=33512))
    reader.advertise(reader.probe(other))
    assert ControlInbox(f.writer.root).enqueue_scope(other)
    with pytest.raises(ConflictError, match="already pending"):
        _stage(f, other, checkout, process)
    other_session = "10000000-0000-4000-8000-000000000335"
    assert _stage(f, other, checkout, process, other_session) != attempt

    monkeypatch.setattr(grok_scope_hook, "_has_process_ancestor", lambda *_: False)
    with pytest.raises(LedgerError, match="custody changed"):
        scope_admission.bind_grok_prompt(
            f.writer.root, attempt, SESSION, PROMPT_A, checkout
        )


def test_preempted_attempt_never_binds_an_unmarked_or_different_native_prompt(
    staged_scope_policy,
    monkeypatch,
):
    f, _, _, checkout, attempt, lookup, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_B, checkout)
    with pytest.raises(ConflictError, match="another prompt"):
        bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    f.write(f.rows[:5], 1)
    batch = f.state.read_source(f.source_id, f.locator())
    assert not batch.boundaries and not batch.observations
    assert batch.diagnostics


def test_original_envelope_and_sealed_prompt_record_cannot_be_substituted(
    staged_scope_policy,
    monkeypatch,
):
    f, _, request, checkout, attempt, lookup, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    receipt_ref = scope_admission.scope_receipt_ref(
        f.writer.source_evidence(), request.command_id
    )
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") == receipt_ref
    name = scope_admission._filename(request.command_id)
    publications = f.scope_files.inbox_files
    original = publications[name]
    envelope = json.loads(original)
    envelope["command"]["body"]["request"]["scope"]["item"]["identifier"] = 121
    publications[name] = json.dumps(
        envelope, separators=(",", ":"), sort_keys=True
    ).encode()
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    publications[name] = original
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") == receipt_ref

    receipts = f.scope_files.files[f.writer.root / scope_admission._GROK_RECEIPTS]
    ((receipt, retained),) = receipts.items()
    process = staged_scope_policy[-1]
    for raw in (SESSION, PROMPT_A, str(checkout), str(process.executable)):
        assert raw.encode() not in retained
    changed = json.loads(retained)
    attempt_fields = changed["attempts"][0]
    assert "pid" not in attempt_fields
    assert process.pid not in attempt_fields.values()
    assert str(process.pid) not in attempt_fields.values()
    changed["seal"] = "0" * 64
    receipts[receipt] = json.dumps(
        changed, separators=(",", ":"), sort_keys=True
    ).encode()
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None


def test_wrong_pilot_receipt_or_rewritten_verified_event_cannot_apply_scope(
    staged_scope_policy,
    monkeypatch,
):
    from aitm_usage.monitor_scope import ScopeState

    f, _, request, checkout, attempt, _, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    f.write(f.rows[:5], 1)
    batch = f.state.read_source(f.source_id, f.locator())
    (boundary,) = batch.boundaries
    evidence = f.writer.source_evidence()
    with scope_admission.grok_mark(f.writer, request, f.source_id, checkout) as mark:
        pass
    wrong = replace(
        mark,
        receipt_ref=evidence.pseudonymize(
            "isolated-grok-prompt-v1", str(request.command_id)
        ),
    )
    wrong_owner = f.state.operator(f.project)
    f.state.authorize(wrong, wrong_owner)
    with pytest.raises(LedgerError):
        f.state.verify_boundary(wrong, wrong_owner, batch, boundary)

    fresh = ScopeState(f.writer, grok_reader=f.reader)
    batch = fresh.read_source(f.source_id, f.locator())
    owner = fresh.operator(f.project)
    fresh.authorize(mark, owner)
    old = b"synthetic-event-1"
    altered = [row.replace(old, b"substituted-event") for row in f.rows[:5]]
    assert altered != f.rows[:5]
    f.write(altered, 1)
    with pytest.raises(LedgerError, match="prefix changed"):
        fresh.verify_boundary(mark, owner, batch, batch.boundaries[0])
    with pytest.raises(LedgerError):
        fresh.read_source(f.source_id, f.locator(), cursor=batch.cursor)


def test_native_duplicate_hook_and_later_unbound_prompt_do_not_get_the_receipt(
    grok_capture_policy,  # noqa: F811
):
    f = grok_capture_policy
    receipt = scope_admission.scope_receipt_ref(
        f.writer.source_evidence(), UUID(int=33502)
    )

    def verify(session, prompt, _event):
        return receipt if (session, prompt) == (SESSION, PROMPT_A) else None

    f.reader.verify_receipt = verify
    f.submit(33505, True)
    assert f.evaluate()
    f.write([f.rows[0], *f.rows[:5]], 1)
    duplicate = f.state.read_source(f.source_id, f.locator())
    assert duplicate.boundaries == ()
    assert any(
        diagnostic.code is DiagnosticCode.OVERLAP_UNVERIFIED
        for diagnostic in duplicate.diagnostics
    )
    f.write(f.rows, 2)
    later = f.state.read_source(f.source_id, f.locator())
    (boundary,) = later.boundaries
    assert boundary.boundary.receipt_ref == receipt
    assert len(later.observations) == 1
    assert later.diagnostics


def test_module_accepts_exact_native_input_and_prints_nothing(monkeypatch, capsys):
    import io

    from aitm_usage.sources import grok_scope_hook

    evidence = _ServiceEvidence(b"g" * 32)
    monitor = Path("/fixture/monitor")
    checkout = Path("/fixture/checkout")
    attempt = evidence.pseudonymize("grok-scope-attempt", "fixture")
    event = {
        "hookEventName": "user_prompt_submit",
        "sessionId": SESSION,
        "promptId": PROMPT_A,
        "workspaceRoot": str(checkout),
    }
    monkeypatch.setattr(grok_scope_hook, "default_monitor_root", lambda: monitor)
    monkeypatch.setattr(grok_scope_hook.sys, "argv", ["grok_scope_hook", attempt.value])
    bind = Mock()
    monkeypatch.setattr(grok_scope_hook, "bind_grok_prompt", bind)

    def invoke(payload):
        monkeypatch.setattr(
            grok_scope_hook.sys, "stdin", io.TextIOWrapper(io.BytesIO(payload))
        )
        assert grok_scope_hook.main() == 0
        captured = capsys.readouterr()
        assert captured.out == captured.err == ""

    payload = json.dumps(event).encode()
    monkeypatch.delenv("GROK_HOOK_EVENT", raising=False)
    invoke(payload)
    bind.assert_not_called()
    monkeypatch.setenv("GROK_HOOK_EVENT", "user_prompt_submit")
    monkeypatch.setenv("GROK_SESSION_ID", "mismatch")
    invoke(payload)
    bind.assert_not_called()
    monkeypatch.setenv("GROK_SESSION_ID", SESSION)
    invoke(b'{"sessionId":"duplicate",' + payload[1:])
    invoke(payload + b" " * grok_scope_hook._MAX_HOOK_BYTES)
    bind.assert_not_called()

    bind.side_effect = RuntimeError("native process inspection failed")
    invoke(payload)
    bind.assert_called_once_with(monitor, attempt, SESSION, PROMPT_A, checkout)
    bind.reset_mock(side_effect=True)
    invoke(payload)
    bind.assert_called_once_with(monitor, attempt, SESSION, PROMPT_A, checkout)


@pytest.mark.parametrize(
    "problem", ["size", "foreign_pid", "init", "uid", "zombie", "no_start", "usec"]
)
def test_process_info_refuses_invalid_custody(monkeypatch, problem):
    pid = 1 if problem == "init" else 33500

    class Proc:
        def proc_pidinfo(self, given, _flavor, _arg, pointer, size):
            row = pointer._obj
            row.pid = given + int(problem == "foreign_pid")
            row.parent_pid = 33501
            row.uid = os.geteuid() + int(problem == "uid")
            row.status = 5 if problem == "zombie" else 1
            row.start_seconds = 0 if problem == "no_start" else 10000
            row.start_microseconds = 1_000_000 if problem == "usec" else 37
            return size - int(problem == "size")

    monkeypatch.setattr(process_identity, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(process_identity, "_libproc", Proc)
    assert process_identity.read_process_hop(pid) is None


@pytest.mark.parametrize(
    "problem", ["truncated", "length", "path-changed", "image-changed"]
)
def test_darwin_process_identity_refuses_ambiguous_executable(monkeypatch, problem):
    inspect_path = Mock(side_effect=AssertionError("invalid path reached inspection"))
    malformed = problem in {"truncated", "length"}
    uid = 501
    root = Path("/fixture")
    image = root / "candidate"
    replacement = root / "replacement"
    paths = {
        str(image): _observed_executable(17),
        str(replacement): _observed_executable(18),
    }
    if malformed:
        monkeypatch.setattr(process_identity, "Path", inspect_path)
    else:
        monkeypatch.setattr(process_identity, "Path", paths.__getitem__)
    monkeypatch.setattr(
        process_identity,
        "os",
        SimpleNamespace(geteuid=lambda: uid, fsdecode=os.fsdecode),
    )

    class Proc:
        path_reads = 0

        def proc_pidinfo(self, pid, _flavor, _arg, pointer, size):
            row = pointer._obj
            row.pid = pid
            row.parent_pid = 1
            row.uid = uid
            row.start_seconds = 10000
            return size

        def proc_pidpath(self, _pid, buffer, size):
            self.path_reads += 1
            path = image
            if self.path_reads == 2:
                if problem == "path-changed":
                    path = replacement
                if problem == "image-changed":
                    paths[str(image)].stat.return_value = paths[
                        str(replacement)
                    ].stat.return_value
            buffer.value = os.fsencode(path)
            if problem == "truncated":
                return size
            return len(buffer.value) + int(problem == "length")

    proc = Proc()
    monkeypatch.setattr(process_identity, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(process_identity, "_libproc", lambda: proc)
    assert process_identity.read_process_identity(33500) is None
    if malformed:
        assert proc.path_reads == 1
        inspect_path.assert_not_called()
    else:
        assert proc.path_reads == 2


def _observed_executable(inode):
    executable = Mock(spec=Path)
    executable.is_absolute.return_value = True
    executable.resolve.return_value = executable
    executable.stat.return_value = SimpleNamespace(
        st_mode=stat.S_IFREG | 0o700,
        st_dev=3,
        st_ino=inode,
        st_size=4096,
        st_mtime_ns=71,
    )
    return executable


def test_darwin_walk_rechecks_parent_incarnation_and_image(monkeypatch):
    from aitm_usage.sources import grok_scope_hook

    evidence = _ServiceEvidence(b"g" * 32)
    start = datetime(2026, 11, 9, 12, tzinfo=UTC)
    process = process_identity.ProcessIdentity(33503, start, _observed_executable(17))
    monkeypatch.setattr(process_identity, "sys", SimpleNamespace(platform="darwin"))
    monkeypatch.setattr(process_identity, "os", SimpleNamespace(geteuid=lambda: 501))

    class Proc:
        def proc_pidinfo(self, pid, _flavor, _arg, pointer, size):
            row = pointer._obj
            row.pid = pid
            row.uid = 501
            row.parent_pid = process.pid if pid == 33540 else 1
            row.start_seconds = int(start.timestamp())
            return size

    proc = Proc()
    name = scope_admission._grok_process_ref(evidence, process.pid, start)
    image = scope_admission._grok_image_ref(evidence, process.executable)
    monkeypatch.setattr(process_identity, "_libproc", lambda: proc)
    monkeypatch.setattr(process_identity, "read_process_identity", lambda _: process)
    monkeypatch.setattr(grok_scope_hook.os, "getpid", lambda: 33540)
    monkeypatch.setattr(grok_scope_hook.os, "getppid", lambda: process.pid)
    assert grok_scope_hook._has_process_ancestor(evidence, name, image)
    forged = evidence.pseudonymize("fixture", "other-image")
    assert not grok_scope_hook._has_process_ancestor(evidence, name, forged)
    original = proc.proc_pidinfo
    invoked = iter((0, 1))

    def unstable(pid, flavor, arg, pointer, size):
        count = original(pid, flavor, arg, pointer, size)
        if pid == 33540:
            pointer._obj.start_microseconds = next(invoked)
        return count

    monkeypatch.setattr(proc, "proc_pidinfo", unstable)
    assert not grok_scope_hook._has_process_ancestor(evidence, name, image)


def test_darwin_walk_refuses_invalid_parent_depth_and_birth_order(monkeypatch):
    from aitm_usage.sources import grok_scope_hook

    evidence = _ServiceEvidence(b"g" * 32)
    start = datetime(2026, 11, 9, 12, tzinfo=UTC)
    process = process_identity.ProcessIdentity(33503, start, _observed_executable(17))
    monkeypatch.setattr(process_identity, "sys", SimpleNamespace(platform="darwin"))
    name = scope_admission._grok_process_ref(evidence, process.pid, process.started)
    image = scope_admission._grok_image_ref(evidence, process.executable)
    caller = process.pid + 9
    monkeypatch.setattr(grok_scope_hook.os, "getpid", lambda: caller)
    monkeypatch.setattr(grok_scope_hook.os, "getppid", lambda: caller - 1)

    def chain(pid):
        return pid - 1, process.started

    assert not grok_scope_hook._has_process_ancestor(
        evidence, name, image, read_hop=chain
    )

    def born_too_late(pid):
        if pid == caller:
            return process.pid, process.started - timedelta(seconds=1)
        return 1, process.started

    monkeypatch.setattr(grok_scope_hook.os, "getppid", lambda: process.pid)
    assert not grok_scope_hook._has_process_ancestor(
        evidence, name, image, read_hop=born_too_late
    )

    monkeypatch.setattr(grok_scope_hook.os, "getppid", lambda: 1)

    def no_parent(pid):
        assert pid == caller
        return 1, process.started

    assert not grok_scope_hook._has_process_ancestor(
        evidence, name, image, read_hop=no_parent
    )


@pytest.mark.parametrize("same_path", [False, True], ids=["new-path", "same-path"])
def test_hook_refuses_executable_change_during_final_ancestry_check(
    request, monkeypatch, same_path
):
    from aitm_usage.sources import grok_scope_hook

    evidence = _ServiceEvidence(b"g" * 32)
    start = datetime(2026, 11, 9, 12, tzinfo=UTC)
    if same_path:
        root = request.getfixturevalue("tmp_path")
        image_path = root / "candidate"
        replacement = root / "replacement"
        image_path.write_bytes(b"original executable image")
        replacement.write_bytes(b"new executable image")
    else:
        image_path = _observed_executable(17)
        replacement = _observed_executable(18)
        monkeypatch.setattr(process_identity, "process_reference_domain", lambda: "")
    process = process_identity.ProcessIdentity(33503, start, image_path)
    name = scope_admission._grok_process_ref(evidence, process.pid, process.started)
    image = scope_admission._grok_image_ref(evidence, process.executable)
    caller = process.pid + 1
    observed = process
    image_read = False
    changed = False

    def read_identity(pid):
        nonlocal image_read
        assert pid == process.pid
        image_read = True
        return observed

    def read_hop(pid):
        nonlocal changed, observed
        if image_read and not changed:
            if same_path:
                replacement.replace(process.executable)
            else:
                observed = replace(process, executable=replacement)
            changed = True
        return (process.pid if pid == caller else 1), process.started

    monkeypatch.setattr(grok_scope_hook.os, "getpid", lambda: caller)
    monkeypatch.setattr(grok_scope_hook.os, "getppid", lambda: process.pid)
    monkeypatch.setattr(process_identity, "read_process_identity", read_identity)
    assert not grok_scope_hook._has_process_ancestor(
        evidence, name, image, read_hop=read_hop
    )
    assert changed


def test_platform_native_process_custody_has_no_provider_request(
    isolated_grok_capture,  # noqa: F811
    monkeypatch,
):
    import io

    from aitm_usage.sources import grok_scope_hook

    f = isolated_grok_capture
    evidence = f.writer.source_evidence()
    if sys.platform in ("darwin", "linux") and os.getppid() > 1:
        parent = process_identity.read_process_identity(os.getppid())
        assert parent is not None
        if parent.executable.stat().st_size > 256 * 1024 * 1024:
            with pytest.raises(LedgerError, match="bounded regular file"):
                scope_admission._grok_image_ref(evidence, parent.executable)
            return
        assert grok_scope_hook._has_process_ancestor(
            evidence,
            scope_admission._grok_process_ref(evidence, parent.pid, parent.started),
            scope_admission._grok_image_ref(evidence, parent.executable),
        )
        return
    if sys.platform not in ("darwin", "linux"):
        assert process_identity.read_process_identity(os.getppid()) is None
    event = {
        "hookEventName": "user_prompt_submit",
        "sessionId": SESSION,
        "promptId": PROMPT_A,
        "workspaceRoot": str(f.root.path),
    }
    selector = evidence.pseudonymize("fixture", "unapproved-selector")
    monkeypatch.setattr(grok_scope_hook, "default_monitor_root", lambda: f.writer.root)
    monkeypatch.setattr(sys, "argv", ["grok_scope_hook", selector.value])
    monkeypatch.setattr(
        sys, "stdin", io.TextIOWrapper(io.BytesIO(json.dumps(event).encode()))
    )
    monkeypatch.setenv("GROK_HOOK_EVENT", "user_prompt_submit")
    monkeypatch.setenv("GROK_SESSION_ID", SESSION)
    assert grok_scope_hook.main() == 0
    assert not (f.writer.root / scope_admission._GROK_RECEIPTS).exists()


@pytest.mark.skipif(
    sys.platform != "linux", reason="Requires the Linux proc filesystem"
)
@pytest.mark.parametrize("isolated_grok_capture", ["/bin/sh"], indirect=True)
@pytest.mark.parametrize("stale_incarnation", [False, True], ids=["live", "stale"])
def test_linux_scope_staging_and_hook_recheck_external_process_incarnation(
    isolated_grok_capture,  # noqa: F811
    tmp_path,
    monkeypatch,
    stale_incarnation,
):
    f = isolated_grok_capture
    _, request = _scope_proposal(f)
    checkout = tmp_path / "checkout"
    f.submit(33505, True)
    assert f.evaluate()
    event = {
        "hookEventName": "user_prompt_submit",
        "sessionId": SESSION,
        "promptId": PROMPT_A,
        "workspaceRoot": str(checkout),
    }
    with subprocess.Popen(
        [
            str(f.executable),
            "-c",
            'IFS= read -r selector || exit 1; "$@" "$selector"; exit $?',
            "grok-fixture",
            sys.executable,
            "-c",
            "import sys; from pathlib import Path; "
            "from aitm_usage import ledger; "
            "from aitm_usage.sources import grok_scope_hook as hook; "
            "root = Path(sys.argv.pop(1)); hook.default_monitor_root = lambda: root; "
            "ledger._control_root = lambda: root.parent / 'control'; "
            "raise SystemExit(hook.main())",
            str(f.writer.root),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            **os.environ,
            "GROK_HOOK_EVENT": event["hookEventName"],
            "GROK_SESSION_ID": SESSION,
        },
    ) as external:
        try:
            with monkeypatch.context() as stage:
                if stale_incarnation:
                    process_ref = scope_admission._grok_process_ref
                    stage.setattr(
                        scope_admission,
                        "_grok_process_ref",
                        lambda evidence, pid, started: process_ref(
                            evidence, pid, started - timedelta(seconds=1)
                        ),
                    )
                selector = scope_admission.stage_grok_attempt(
                    f.writer,
                    f.source_id,
                    request.command_id,
                    SESSION,
                    checkout,
                    external.pid,
                )
            stdout, stderr = external.communicate(
                f"{selector.value}\n{json.dumps(event)}\n".encode(), timeout=15
            )
            assert external.returncode == 0 and stdout == stderr == b"", stderr.decode()
        finally:
            if external.poll() is None:
                external.kill()
                external.communicate()
    lookup = scope_admission.grok_receipt_lookup(f.writer, f.source_id, checkout)
    expected = (
        None
        if stale_incarnation
        else scope_admission.scope_receipt_ref(
            f.writer.source_evidence(), request.command_id
        )
    )
    assert lookup(SESSION, PROMPT_A, "native") == expected


def test_source_approval_profile_and_command_witness_do_not_transfer(
    staged_scope_policy,
    monkeypatch,
):
    f, reader, request, checkout, attempt, lookup, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    with pytest.raises(LedgerError):
        bind(
            f.writer.root,
            attempt,
            "10000000-0000-4000-8000-000000000335",
            PROMPT_A,
            checkout,
        )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    f.revise("replace", 2)
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    with pytest.raises(ConflictError, match="another attempt"):
        _stage(f, request, checkout, staged_scope_policy[-1])
    reader.register(request.grant_id, f.project, ("mark",), generation=2)
    reader.advertise(reader.probe(request))
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    with pytest.raises(LedgerError, match="seal changed"):
        bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)


@pytest.mark.parametrize("operation", ["replace", "revoke"])
def test_profile_revision_before_first_bind_preserves_unbound_attempt(
    staged_scope_policy, monkeypatch, operation
):
    f, _, _, checkout, selector, lookup, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    f.revise(operation, 2)
    with pytest.raises(LedgerError, match="qualification revision changed"):
        bind(f.writer.root, selector, SESSION, PROMPT_A, checkout)
    with scope_admission._pin_directory(f.writer.root) as root:
        with scope_admission._private_child(
            root, scope_admission._GROK_RECEIPTS, create=False
        ) as directory:
            assert directory is not None
            (attempt,) = scope_admission._grok_receipts(
                directory, f.writer.source_evidence()
            )
    assert attempt.selector == selector and attempt.prompt is None
    assert lookup(SESSION, PROMPT_A, "native") is None


def test_rotation_between_bind_validation_and_publication_refuses_commit(
    staged_scope_policy, monkeypatch
):
    f, _, _, checkout, selector, lookup, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    original = scope_admission._publish
    invoked = []
    saved = f.scope_files.files[f.writer.root / scope_admission._GROK_RECEIPTS].copy()

    def publish(*args, **kwargs):
        invoked.append(True)
        f.revise("replace", 2)
        return original(*args, **kwargs)

    monkeypatch.setattr(scope_admission, "_publish", publish)
    with pytest.raises(LedgerError, match="qualification revision changed"):
        bind(f.writer.root, selector, SESSION, PROMPT_A, checkout)
    assert invoked == [True]
    assert f.scope_files.files[f.writer.root / scope_admission._GROK_RECEIPTS] == saved
    with (
        scope_admission._pin_directory(f.writer.root) as root,
        scope_admission._private_child(
            root, scope_admission._GROK_RECEIPTS, create=False
        ) as directory,
    ):
        assert directory is not None
        (attempt,) = scope_admission._grok_receipts(
            directory, f.writer.source_evidence()
        )
    assert attempt.selector == selector and attempt.prompt is None
    assert lookup(SESSION, PROMPT_A, "exact-event") is None


def test_ordinary_checkout_mode_can_be_physically_identified(monkeypatch):
    from aitm_usage import monitor_registry

    physical = os.stat_result((stat.S_IFDIR | 0o755, 17, 3, 1, 501, 0, 0, 0, 0, 0))

    class Checkout(type(Path())):
        def resolve(self, *, strict):
            assert strict
            return self

        def stat(self, *, follow_symlinks=True):
            return physical

    monkeypatch.setattr(monitor_registry, "Path", Checkout)
    private_check = Mock(side_effect=AssertionError("Checkout required private modes"))
    monkeypatch.setattr(monitor_registry, "validate_private_path", private_check)
    path = "/fixture/ordinary-checkout"
    observed = monitor_registry._directory(path)
    assert observed == monitor_registry._PhysicalDirectory(path, (3, 17))
    private_check.assert_not_called()


def test_expired_first_bind_keeps_exact_original_scope_unpublished(
    staged_scope_policy, monkeypatch
):
    f, _, request, checkout, process = staged_scope_policy
    attempt = _stage(f, request, checkout, process)
    receipts = f.scope_files.files[f.writer.root / scope_admission._GROK_RECEIPTS]
    before = receipts.copy()
    after = datetime.now(UTC) + scope_admission.WITNESS_LIFETIME + timedelta(seconds=1)

    class FutureClock(datetime):
        @classmethod
        def now(cls, tz=None):
            return after

    monkeypatch.setattr(scope_admission, "datetime", FutureClock)
    with pytest.raises(LedgerError, match="Staged Grok scope attempt is unavailable"):
        scope_admission.bind_grok_prompt(
            f.writer.root, attempt, SESSION, PROMPT_A, checkout
        )
    callback = scope_admission.grok_receipt_lookup(f.writer, f.source_id, checkout)
    assert callback(SESSION, PROMPT_A, "native") is None
    assert receipts == before


@pytest.mark.parametrize(
    ("operation", "refusal"),
    [("revoke", "producer grant is unavailable"), ("rotate", "seal changed")],
)
def test_grant_change_after_native_read_refuses_first_application(
    staged_scope_policy, monkeypatch, operation, refusal
):
    f, reader, request, checkout, attempt, lookup, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    f.write(f.rows[:5], 1)
    batch = f.state.read_source(f.source_id, f.locator())
    (boundary,) = batch.boundaries
    if operation == "revoke":
        reader.revoke(request.grant_id)
    else:
        reader.register(request.grant_id, f.project, ("mark",), generation=2)
        reader.advertise(reader.probe(request))
    assert lookup(SESSION, PROMPT_A, "native") is None
    before = f.state._snapshot()
    with pytest.raises(LedgerError, match=refusal):
        with scope_admission.grok_mark(
            f.writer, request, f.source_id, checkout
        ) as mark:
            owner = f.state.operator(f.project)
            f.state.authorize(mark, owner)
            f.state.apply_mark(
                mark, f.state.verify_boundary(mark, owner, batch, boundary)
            )
    assert f.state._snapshot() == before


def test_first_application_holds_the_revocation_publication_lock(
    staged_scope, monkeypatch
):
    import fcntl

    from aitm_usage.monitor_control import INBOX_NAME

    f, reader, request, checkout, attempt, _, bind = _ready_scope(
        staged_scope, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    f.write(f.rows[:5], 1)
    batch = f.state.read_source(f.source_id, f.locator())
    (boundary,) = batch.boundaries
    with (
        scope_admission._pin_directory(f.writer.root / INBOX_NAME) as competing,
        scope_admission.grok_mark(f.writer, request, f.source_id, checkout) as mark,
    ):
        with pytest.raises(BlockingIOError):
            fcntl.flock(competing.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        owner = f.state.operator(f.project)
        f.state.authorize(mark, owner)
        verdict = f.state.apply_mark(
            mark, f.state.verify_boundary(mark, owner, batch, boundary)
        )
        assert verdict.status is HandoffStatus.APPLIED
    reader.revoke(request.grant_id)


def test_native_marker_cannot_be_applied_by_a_different_scope_owner(
    staged_scope_policy,
    monkeypatch,
):
    from test_ledger import _memory_ledger

    from aitm_usage import ledger as ledger_module
    from aitm_usage import monitor_registry
    from aitm_usage.ledger import STORE_NAME, Ledger

    f, _, request, checkout, attempt, _, bind = _ready_scope(
        staged_scope_policy, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    rival = UUID(int=33543)
    rival_state = Path("/fixture/rival-state")
    destination = monitor_registry._PhysicalDirectory(str(rival_state), (2, 11))
    rival_ledger = replace(
        _memory_ledger(ledger_module, rival, b"r" * 32), root=rival_state
    )
    open_ledger = Ledger.open
    directory = monitor_registry._directory

    def open_project(path, project):
        if path == rival_state:
            assert project == rival
            return rival_ledger
        return open_ledger(path, project)

    def identify_project(path, **options):
        if path == destination.path:
            return destination
        return directory(path, **options)

    monkeypatch.setattr(Ledger, "open", open_project)
    monkeypatch.setattr(monitor_registry, "_directory", identify_project)
    f.scope_files.ensure(rival_state / STORE_NAME)
    f.writer.register_project(
        monitor_registry.ProjectRegistrationRequest(rival, str(rival_state), "Rival")
    )
    f.write(f.rows[:5], 1)
    batch = f.state.read_source(f.source_id, f.locator())
    (boundary,) = batch.boundaries
    before = f.state._snapshot()
    with scope_admission.grok_mark(f.writer, request, f.source_id, checkout) as mark:
        authority = f.state.operator(rival)
        with pytest.raises(LedgerError):
            f.state.authorize(mark, authority)
        with pytest.raises(LedgerError):
            f.state.verify_boundary(mark, authority, batch, boundary)
    forged_scope = replace(request, scope=replace(request.scope, project_id=rival))
    with pytest.raises(LedgerError, match="proposal is unavailable"):
        with scope_admission.grok_mark(f.writer, forged_scope, f.source_id, checkout):
            pytest.fail("foreign owner converted the original receipt")
    assert f.state._snapshot() == before
