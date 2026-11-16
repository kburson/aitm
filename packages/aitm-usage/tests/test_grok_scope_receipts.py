"""An owned Grok UserPromptSubmit must carry one exact sealed scope proposal."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from test_grok import PROMPT_A, PROMPT_B, SESSION
from test_monitor_grok_capture import isolated_grok_capture  # noqa: F401, F811

from aitm_usage import install, scope_admission
from aitm_usage.ledger import ConflictError, LedgerError
from aitm_usage.monitor_control import ControlInbox, ScopeInboxReader
from aitm_usage.monitor_scope import HandoffStatus, Scope, resolve_route
from aitm_usage.types import DiagnosticCode, ItemKey, ItemKind, WorkPhase


@pytest.fixture
def staged_scope(
    isolated_grok_capture,  # noqa: F811
    tmp_path,
    monkeypatch,
):
    f = isolated_grok_capture
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
    checkout = tmp_path / "checkout"
    process = install._ProcessIdentity(
        33503,
        datetime.now(UTC),
        tmp_path / "image" / "candidate",
    )
    monkeypatch.setattr(
        install,
        "_process_identity",
        lambda pid: process if pid == process.pid else None,
    )
    return f, reader, command, checkout, process


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


def test_exact_command_cannot_be_reused_in_another_session(staged_scope):
    f, _, command, checkout, process = staged_scope
    _stage(f, command, checkout, process)
    with pytest.raises((ConflictError, LedgerError)):
        _stage(f, command, checkout, process, "10000000-0000-4000-8000-000000000335")


def test_original_owner_and_live_process_are_required(staged_scope, tmp_path):
    f, _, command, checkout, process = staged_scope
    rival = tmp_path / "rival"
    rival.mkdir()
    with pytest.raises(LedgerError, match="checkout"):
        _stage(f, command, rival, process)
    with pytest.raises(LedgerError):
        _stage(f, replace(command, command_id=UUID(int=33510)), checkout, process)
    with pytest.raises(LedgerError, match="native process is unavailable"):
        _stage(f, command, checkout, replace(process, pid=process.pid + 1))


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
    staged_scope,
    monkeypatch,
):
    from aitm_usage.sources import grok_scope_hook

    f, reader, request, checkout, process = staged_scope
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
    staged_scope,
    monkeypatch,
):
    f, _, _, checkout, attempt, lookup, bind = _ready_scope(staged_scope, monkeypatch)
    assert bind(f.writer.root, attempt, SESSION, PROMPT_B, checkout)
    with pytest.raises(ConflictError, match="another prompt"):
        bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    f.write(f.rows[:5], 1)
    batch = f.state.read_source(f.source_id, f.locator())
    assert not batch.boundaries and not batch.observations
    assert batch.diagnostics


def test_original_envelope_and_sealed_prompt_record_cannot_be_substituted(
    staged_scope,
    monkeypatch,
):
    import json

    f, _, request, checkout, attempt, lookup, bind = _ready_scope(
        staged_scope, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    queue = ControlInbox(f.writer.root)
    name = scope_admission._filename(request.command_id)
    with queue.publication() as locked:
        publication = locked.directory.path / name
    original = publication.read_bytes()
    envelope = json.loads(original)
    envelope["command"]["body"]["request"]["scope"]["item"]["identifier"] = 121
    publication.write_text(json.dumps(envelope, separators=(",", ":"), sort_keys=True))
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    publication.write_bytes(original)

    (receipt,) = (f.writer.root / scope_admission._GROK_RECEIPTS).glob("*.json")
    retained = receipt.read_bytes()
    for raw in (SESSION, PROMPT_A, str(checkout)):
        assert raw.encode() not in retained
    changed = json.loads(retained)
    assert "pid" not in changed["attempts"][0]
    changed["seal"] = "0" * 64
    receipt.write_text(json.dumps(changed, separators=(",", ":"), sort_keys=True))
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None


def test_wrong_pilot_receipt_or_rewritten_verified_event_cannot_apply_scope(
    staged_scope,
    monkeypatch,
):
    from aitm_usage.monitor_scope import ScopeState

    f, _, request, checkout, attempt, _, bind = _ready_scope(staged_scope, monkeypatch)
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
    staged_scope,
    monkeypatch,
):
    f, _, _, checkout, attempt, _, bind = _ready_scope(staged_scope, monkeypatch)
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    f.write([f.rows[0], *f.rows[:5]], 1)
    duplicate = f.state.read_source(f.source_id, f.locator())
    assert duplicate.boundaries == ()
    assert any(
        diagnostic.code is DiagnosticCode.OVERLAP_UNVERIFIED
        for diagnostic in duplicate.diagnostics
    )
    f.write(f.rows, 2)
    later = f.state.read_source(f.source_id, f.locator())
    assert len(later.boundaries) == 1 and len(later.observations) == 1
    assert later.diagnostics


def test_module_accepts_exact_native_input_and_prints_nothing(
    staged_scope,
    monkeypatch,
    capsys,
):
    import io
    import json

    from aitm_usage.sources import grok_scope_hook

    f, _, _, checkout, attempt, lookup, _ = _ready_scope(staged_scope, monkeypatch)
    event = {
        "hookEventName": "user_prompt_submit",
        "sessionId": SESSION,
        "promptId": PROMPT_A,
        "workspaceRoot": str(checkout),
    }
    monkeypatch.setattr(grok_scope_hook, "default_monitor_root", lambda: f.writer.root)
    monkeypatch.setattr(grok_scope_hook.sys, "argv", ["grok_scope_hook", attempt.value])

    def invoke(payload):
        monkeypatch.setattr(
            grok_scope_hook.sys, "stdin", io.TextIOWrapper(io.BytesIO(payload))
        )
        assert grok_scope_hook.main() == 0
        captured = capsys.readouterr()
        assert captured.out == captured.err == ""

    invoke(json.dumps(event).encode())
    assert lookup(SESSION, PROMPT_A, "native") is None
    monkeypatch.setenv("GROK_HOOK_EVENT", "user_prompt_submit")
    monkeypatch.setenv("GROK_SESSION_ID", "mismatch")
    invoke(json.dumps(event).encode())
    assert lookup(SESSION, PROMPT_A, "native") is None
    monkeypatch.setenv("GROK_SESSION_ID", SESSION)
    invoke(b'{"sessionId":"duplicate","sessionId":"bad"}')
    invoke(b"x" * (grok_scope_hook._MAX_HOOK_BYTES + 1))

    def fail_binding(*args):
        raise RuntimeError("native process inspection failed")

    with monkeypatch.context() as trial:
        trial.setattr(grok_scope_hook, "bind_grok_prompt", fail_binding)
        invoke(json.dumps(event).encode())
    assert lookup(SESSION, PROMPT_A, "native") is None

    invoke(json.dumps(event).encode())
    assert lookup(SESSION, PROMPT_A, "native") is not None


def test_darwin_walk_rechecks_parent_incarnation_and_image(staged_scope, monkeypatch):
    import os

    from aitm_usage.sources import grok_scope_hook

    f, _, _, _, process = staged_scope
    evidence = f.writer.source_evidence()
    start = process.started.replace(microsecond=0)

    class Proc:
        def proc_pidinfo(self, pid, _flavor, _arg, pointer, size):
            row = pointer._obj
            row.pid = pid
            row.uid = os.geteuid()
            row.parent_pid = process.pid if pid == 33540 else 1
            row.start_seconds = int(start.timestamp())
            return size

    proc = Proc()
    expected = replace(process, started=start)
    name = scope_admission._grok_process_ref(evidence, process.pid, start)
    image = scope_admission._grok_image_ref(evidence, process.executable)
    monkeypatch.setattr(install, "_libproc", lambda: proc)
    monkeypatch.setattr(install, "_process_identity", lambda _: expected)
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


def test_darwin_walk_refuses_invalid_parent_depth_and_birth_order(
    staged_scope, monkeypatch
):
    from aitm_usage.sources import grok_scope_hook

    f, _, _, _, process = staged_scope
    evidence = f.writer.source_evidence()
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


def test_platform_native_process_custody_has_no_provider_request(
    isolated_grok_capture,  # noqa: F811
    monkeypatch,
):
    import io
    import json
    import os
    import sys

    from aitm_usage.sources import grok_scope_hook

    f = isolated_grok_capture
    evidence = f.writer.source_evidence()
    if sys.platform == "darwin":
        parent = install._process_identity(os.getppid())
        assert parent is not None
        assert grok_scope_hook._has_process_ancestor(
            evidence,
            scope_admission._grok_process_ref(evidence, parent.pid, parent.started),
            scope_admission._grok_image_ref(evidence, parent.executable),
        )
        return
    assert install._process_identity(os.getppid()) is None
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


def test_source_approval_profile_and_command_witness_do_not_transfer(
    staged_scope,
    monkeypatch,
):
    f, reader, request, checkout, attempt, lookup, bind = _ready_scope(
        staged_scope, monkeypatch
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
        _stage(f, request, checkout, staged_scope[-1])
    reader.register(request.grant_id, f.project, ("mark",), generation=2)
    reader.advertise(reader.probe(request))
    assert lookup(SESSION, PROMPT_A, "synthetic-event-1") is None
    with pytest.raises(LedgerError, match="seal changed"):
        bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)


@pytest.mark.parametrize("operation", ["replace", "revoke"])
def test_profile_revision_before_first_bind_preserves_unbound_attempt(
    staged_scope, monkeypatch, operation
):
    f, _, _, checkout, selector, lookup, bind = _ready_scope(staged_scope, monkeypatch)
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


def test_ordinary_checkout_mode_can_be_physically_identified(tmp_path):
    from aitm_usage.monitor_registry import _directory

    checkout = tmp_path / "ordinary-checkout"
    checkout.mkdir()
    checkout.chmod(0o755)
    physical = checkout.stat()
    assert _directory(str(checkout)).identity == (physical.st_dev, physical.st_ino)


def test_expired_first_bind_keeps_exact_original_scope_unpublished(
    staged_scope, monkeypatch
):
    f, _, request, checkout, process = staged_scope
    attempt = _stage(f, request, checkout, process)
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


def test_grant_revoked_after_native_read_refuses_first_application(
    staged_scope, monkeypatch
):
    f, reader, request, checkout, attempt, _, bind = _ready_scope(
        staged_scope, monkeypatch
    )
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    f.write(f.rows[:5], 1)
    batch = f.state.read_source(f.source_id, f.locator())
    (boundary,) = batch.boundaries
    reader.revoke(request.grant_id)
    before = f.state._snapshot()
    with pytest.raises(LedgerError, match="producer grant is unavailable"):
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
    staged_scope,
    monkeypatch,
    tmp_path,
):
    from aitm_usage.ledger import Ledger
    from aitm_usage.monitor_registry import ProjectRegistrationRequest

    f, _, request, checkout, attempt, _, bind = _ready_scope(staged_scope, monkeypatch)
    assert bind(f.writer.root, attempt, SESSION, PROMPT_A, checkout)
    rival = UUID(int=33543)
    rival_state = tmp_path / "rival-state"
    Ledger.initialize(rival_state, rival)
    f.writer.register_project(
        ProjectRegistrationRequest(rival, str(rival_state), "Rival")
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
