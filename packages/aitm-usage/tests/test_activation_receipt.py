import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

import pytest
from test_accounting import reference_rates as reference_rates
from test_install import activation_policy as activation_policy
from test_install import install_policy_ledger as install_policy_ledger
from test_install import launch_control as launch_control
from test_install import project as project
from test_install import runtime_receipt as runtime_receipt
from test_service import collector_policy as collector_policy

from aitm_usage import cli, qualification

FIXTURE = Path(__file__).parent / "fixtures" / "activation" / "receipt.json"
CHECKED = datetime(2026, 11, 9, 15, 0, 5, tzinfo=UTC)


def _receipt():
    data = json.loads(FIXTURE.read_text())
    data["basis"] = "real-controlled"
    return data


def _validate(data, now=CHECKED):
    from aitm_usage.qualification import (
        decode_activation_receipt,
        validate_activation_receipt,
    )

    return validate_activation_receipt(
        decode_activation_receipt(json.dumps(data)), now=now
    )


def test_activation_requires_live_both_providers_and_parity():
    assert _validate(_receipt()).status == "qualified"
    assert _validate(json.loads(FIXTURE.read_text())).status == "fixture-only"


@pytest.mark.parametrize(
    ("path", "value", "status"),
    [
        (("basis",), "fixture-only", "fixture-only"),
        (("collector", "heartbeat"), "2026-11-09T14:57:55+00:00", "stale-heartbeat"),
        (("collector", "same_process"), False, "service-evidence"),
        (
            ("collector", "producer_started"),
            "2026-11-09T14:59:56+00:00",
            "service-evidence",
        ),
        (("providers", 0, "offset"), 0, "provider-evidence"),
        (("providers", 0, "route"), "claude-code-native", "provider-evidence"),
        (("providers", 0, "client_version"), "unknown", "provider-evidence"),
        (
            ("providers", 0, "observed_through"),
            "2026-11-09T13:59:51+00:00",
            "source-watermark",
        ),
        (("workflow", "inclusive"), 3, "workflow-evidence"),
        (("workflow", "graduation_sequence"), 58, "workflow-evidence"),
        (("orders", 0, "order"), "boundary-first", "processing-order"),
        (("orders", 0, "after_sequence"), 1, "processing-order"),
        (("export", "replay_rows"), 13, "export-parity"),
        (("export", "replay_sha256"), "f" * 64, "export-parity"),
        (("recovery", "restored_sha256"), "f" * 64, "recovery-parity"),
        (("recovery", "restored_at"), "2026-11-09T13:21:00+00:00", "recovery-evidence"),
    ],
)
def test_qualification_refuses_contradictory_evidence(path, value, status):
    data = _receipt()
    node = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    assert _validate(data).status == status


def test_qualification_refuses_missing_provider():
    data = _receipt()
    data["providers"].pop()
    assert _validate(data).status == "provider-evidence"


def test_qualification_refuses_missing_scope():
    data = _receipt()
    del data["workflow"]["child_a"]
    with pytest.raises(ValueError):
        _validate(data)


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("workflow", "child_a"), "hmac-sha256:" + "a" * 64 + ":" + "f" * 64),
        (("providers", 0, "stream"), "/private/operator/provider.jsonl"),
        (("providers", 0, "client_version"), "token=never-publish-this"),
        (("providers", 0, "coverage", "retry"), "account-id"),
        (("collector", "cwd"), "/private/operator"),
        (("export", "replay_rows"), True),
        (("registration_cutoff",), "2026-11-09T12:00:00-01:00"),
        (("project_id",), "3F32952E-83EA-4427-98F4-121BF30263E0"),
    ],
)
def test_receipt_rejects_unapproved_fields_and_values(path, value):
    data = _receipt()
    node = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValueError):
        _validate(data)


def test_receipt_refuses_stale_or_future_observation():
    assert (
        _validate(_receipt(), datetime(2026, 11, 9, 15, 10, tzinfo=UTC)).status
        == "stale-receipt"
    )
    assert (
        _validate(_receipt(), datetime(2026, 11, 9, 14, 59, tzinfo=UTC)).status
        == "stale-receipt"
    )


def _cli(monkeypatch, capsys, root, receipt, *extra):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aitm-usage",
            "--project",
            str(root),
            "qualify",
            "--receipt",
            str(receipt),
            "--json",
            *map(str, extra),
        ],
    )
    code = cli.main()
    output = capsys.readouterr()
    assert not output.err
    return code, json.loads(output.out)


def test_cli_sanitizes_malformed_input_and_disallows_duplicate_fields(
    monkeypatch, capsys
):
    root = Path("/fixture/project")
    path = root / "receipt.json"
    reader = Mock(
        return_value=b'{"project_id": "/private/canary", "project_id": "two"}'
    )
    monkeypatch.setattr(qualification, "_read_owned", reader)

    assert _cli(monkeypatch, capsys, root, path) == (1, {"status": "invalid-receipt"})
    reader.assert_called_once_with(
        path, private=False, limit=qualification._MAX_EVIDENCE_BYTES
    )


def test_cli_requires_installed_proof_for_actual_qualification(monkeypatch, capsys):
    root = Path("/fixture/project")
    path = root / "receipt.json"
    monkeypatch.setattr(qualification, "_now", lambda: CHECKED)
    monkeypatch.setattr(
        qualification, "_read_owned", Mock(return_value=json.dumps(_receipt()).encode())
    )
    exists = Mock(return_value=False)
    open_project = Mock()
    monkeypatch.setattr(Path, "exists", lambda path: exists(path))
    monkeypatch.setattr(cli, "open_project", open_project)

    assert _cli(monkeypatch, capsys, root, path) == (1, {"status": "proof-required"})
    exists.assert_called_once_with(root / qualification.PROOF_NAME)
    open_project.assert_not_called()


def test_qualification_reads_owned_receipt_on_disk(monkeypatch, capsys):
    import stat
    from contextlib import nullcontext
    from io import BytesIO
    from types import SimpleNamespace

    from aitm_usage import install

    monkeypatch.setattr(qualification, "_now", lambda: CHECKED)
    root = Path("/fixture/project")
    path = root / "actual-shaped.json"
    expected = json.dumps(_receipt()).encode()
    original_os = install.os
    file_info = SimpleNamespace(
        st_dev=2,
        st_ino=8,
        st_mode=stat.S_IFREG | 0o644,
        st_uid=501,
        st_mtime_ns=10,
        st_ctime_ns=12,
    )
    open_file = Mock(return_value=8)
    open_parent = Mock(return_value=nullcontext(7))
    reopen = Mock(return_value=file_info)
    check_acl = Mock()
    monkeypatch.setattr(install, "_open_parent", open_parent)
    monkeypatch.setattr(install, "_check_acl", check_acl)
    monkeypatch.setattr(
        install,
        "os",
        SimpleNamespace(
            O_RDONLY=original_os.O_RDONLY,
            O_NONBLOCK=original_os.O_NONBLOCK,
            O_NOFOLLOW=original_os.O_NOFOLLOW,
            open=open_file,
            fdopen=lambda descriptor, mode: BytesIO(expected),
            fstat=lambda descriptor: file_info,
            geteuid=lambda: file_info.st_uid,
            stat=reopen,
            path=original_os.path,
        ),
    )
    exists = Mock(return_value=False)
    monkeypatch.setattr(Path, "exists", lambda candidate: exists(candidate))
    assert _cli(monkeypatch, capsys, root, path) == (
        1,
        {"status": "proof-required"},
    )
    open_parent.assert_called_once_with(path)
    open_file.assert_called_once_with(
        path.name,
        original_os.O_RDONLY | original_os.O_NONBLOCK | original_os.O_NOFOLLOW,
        dir_fd=7,
    )
    check_acl.assert_called_once_with(8)
    reopen.assert_called_once_with(path.name, dir_fd=7, follow_symlinks=False)
    exists.assert_called_once_with(root / qualification.PROOF_NAME)


def _unbound_claude_source(
    registration, cwd, *, session="00000000-0000-4000-8000-00000000aaaa"
):
    from test_claude import request, usage, user, write

    cwd.mkdir()
    rows = [user(cwd), request(cwd, counts=usage())]
    for row in rows:
        row["sessionId"] = session
    path = registration.source_roots[0] / "unrelated.jsonl"
    write(path, rows)
    return path


def _collector_for_lifecycle(lifecycle):
    from datetime import timedelta

    start = datetime.fromisoformat(lifecycle.producer_started)
    heartbeat = datetime.fromisoformat(lifecycle.heartbeat)
    return qualification._CollectorEvidence(
        version=lifecycle.version,
        interpreter_version=lifecycle.interpreter_version,
        wheel_sha256=lifecycle.wheel_sha256,
        previous_started=start - timedelta(minutes=2),
        previous_heartbeat=start - timedelta(minutes=1),
        producer_started=start,
        activation_heartbeat=heartbeat,
        heartbeat=heartbeat,
        poll_interval_seconds=lifecycle.poll_interval_seconds,
        owned_unattended=True,
        same_process=True,
        private_state=True,
    )


def _assert_running_qualification(registration, ledger, lifecycle, control, tmp_path):
    from aitm_usage.pricing import load_rate_card

    verified = qualification._verify_running(
        ledger, _collector_for_lifecycle(lifecycle), lifecycle, control
    )
    assert verified["producer_mode"] == "service"
    assert verified["held_sources"] == 1
    assert sum(row["observed_through"] is not None for row in verified["sources"]) == 2

    selected = _selected_source_evidence(verified)
    view = ledger.as_of()
    rates = load_rate_card()
    qualification._verify_selected_sources(ledger, view, selected, rates)
    source = registration.source_roots[0] / "claude.jsonl"
    relocated = source.rename(tmp_path / "no-longer-approved.jsonl")
    try:
        with pytest.raises(
            qualification.QualificationError, match="selected-source-gap"
        ):
            qualification._verify_selected_sources(ledger, view, selected, rates)
    finally:
        relocated.rename(source)


def test_running_witness_rejects_same_pid_different_start_and_same_version_wrong_wheel(
    activation_policy,
    monkeypatch,
):
    from dataclasses import replace
    from datetime import timedelta

    from aitm_usage.install import InstallReceipt
    from aitm_usage.qualification import (
        QualificationError,
        _verify_running,
    )

    case = activation_policy
    wheel = case.runtime_files.wheel
    lifecycle = InstallReceipt(
        **case.command(
            "service",
            "install",
            "--wheel",
            Path("/fixture/candidate.whl"),
            "--wheel-sha256",
            wheel.digest,
            "--interpreter",
            case.runtime_files.interpreter,
        )
    )
    collector = _collector_for_lifecycle(lifecycle)
    monkeypatch.setattr(
        qualification, "_now", lambda: collector.heartbeat + timedelta(seconds=1)
    )
    monkeypatch.setattr(qualification, "_path_exists", Mock(return_value=False))
    verified = _verify_running(case.ledger, collector, lifecycle, case.control)
    assert verified["producer_mode"] == "service"
    assert verified["producer_pid"] == case.process.pid

    reused_start = collector.producer_started - timedelta(seconds=1)
    with pytest.raises(QualificationError, match="process-incarnation"):
        _verify_running(
            case.ledger,
            replace(collector, producer_started=reused_start),
            replace(lifecycle, producer_started=reused_start.isoformat()),
            case.control,
        )

    other_digest = "b" * 64
    with pytest.raises(QualificationError, match="wheel-mismatch"):
        _verify_running(
            case.ledger,
            replace(collector, wheel_sha256=other_digest),
            replace(lifecycle, wheel_sha256=other_digest),
            case.control,
        )
    assert len(case.control.bootstraps) == 1


def _write_private(path, data):
    path.write_bytes(data)
    path.chmod(0o600)
    return path


def _processing_order_transcript(ledger, checkout, provider, mark_args):
    import shlex
    from dataclasses import replace

    import test_claude as claude
    from test_service_process import (
        CL_CHILD,
        CX_CHILD,
        CX_EPIC,
        _codex_rows,
        _marker,
        _queued,
    )

    from aitm_usage.types import InboxCommand, Provider

    kind = Provider(provider)
    target = CX_EPIC if kind is Provider.CODEX else CL_CHILD
    marker = replace(
        _marker(ledger, kind, target, 1, 83), project_id=ledger.identity.project_id
    )
    command = InboxCommand(target, marker.project_id, marker)

    args = mark_args(marker)
    if kind is Provider.CODEX:
        rows = _codex_rows(
            ledger,
            checkout,
            args,
            mark_args(_marker(ledger, kind, CX_CHILD, 2, 95)),
            _queued(target),
            _queued(CX_CHILD),
        )[:-8]
    else:
        shell = shlex.join(
            (
                "aitm-usage",
                "--project",
                str(ledger.root),
                *args,
            )
        )
        rows = [
            claude.user(checkout),
            *claude._native_tool_turn(checkout, shell, _queued(target).decode()),
        ]
    return command, rows


def _reserve_processing_order_session(monkeypatch, marker):
    from contextlib import nullcontext

    from aitm_usage import service

    sessions = object()
    private_child, read_private = service._private_child, service._read_private

    def child(directory, name, *, create):
        if name == service.CLAUDE_SESSIONS_NAME:
            assert not create
            return nullcontext(sessions)
        return private_child(directory, name, create=create)

    def read(directory, name):
        if directory is sessions:
            assert name == service._session_filename(marker.session_ref)
            return json.dumps(marker.session_ref.value).encode()
        return read_private(directory, name)

    monkeypatch.setattr(service, "_private_child", child)
    monkeypatch.setattr(service, "_read_private", read)


def _assert_processing_order_in_memory(
    case, monkeypatch, provider, arrival, withhold_target
):
    from dataclasses import replace
    from datetime import timedelta
    from hashlib import sha256
    from types import SimpleNamespace

    from aitm_usage import scopes, service
    from aitm_usage.ledger import Ledger
    from aitm_usage.types import (
        CommandReceipt,
        MarkerDisposition,
        Provider,
        Revision,
        UsageObservation,
    )

    ledger, native = case.ledger, case.native
    case.configure(checkout_anchors=())

    def mark_args(marker):
        from test_claude import SESSION

        args = ("scope", "mark", "--marker", f"/fixture/marker-{marker.marker_id}.json")
        if marker.provider is Provider.CLAUDE:
            args += ("--session-id", str(SESSION))
        return (*args, "--json")

    command, rows = _processing_order_transcript(
        ledger, native.checkout, provider, mark_args
    )
    marker = command.payload
    if marker.provider is Provider.CLAUDE:
        _reserve_processing_order_session(monkeypatch, marker)
    publication = scopes._publication_bytes(command, None)
    key = ledger.pseudonymize("inbox-command", str(command.command_id))
    queued = arrival == "marker-first"

    def receipt_in(view):
        return next((row for row in view.current if row.key == key), None)

    def drain(writer, boundaries):
        assert writer is ledger
        if not queued:
            return scopes.InboxDrain()
        view = writer.as_of()
        previous = receipt_in(view)
        if (
            previous is not None
            and previous.record.disposition is not MarkerDisposition.PENDING
        ):
            return scopes.InboxDrain()
        receipts = {} if previous is None else {command.command_id: previous.record}
        disposition, proof, effects = scopes._evaluate(
            writer, command, view, boundaries, receipts
        )
        receipt = CommandReceipt(
            command,
            writer.validate_command(command),
            disposition,
            None if proof is None else proof.boundary,
            None if proof is None else proof.anchor_ref,
        )
        if previous is None or receipt != previous.record:
            revision = 1 if previous is None else previous.revision + 1
            case.commit_revisions(*effects, Revision(key, revision, receipt))
        return scopes.InboxDrain((receipt,))

    def status_bytes():
        with service._pin_directory(ledger.root) as pinned:
            return service._read_private(pinned, service.STATUS_NAME)

    monkeypatch.setattr(service, "drain_inbox", drain)
    source = native.root / f"{provider}.jsonl"
    if not queued:
        native.write(source, rows[:-2] if withhold_target else rows)
    before_prefix = native.contents.get(source, b"")
    before_captured_at = marker.published_at + timedelta(seconds=30)
    case.clock.now.return_value = before_captured_at + timedelta(seconds=1)
    prior_status = case.collect()
    before, before_status = ledger.as_of(), status_bytes()
    assert native.contents.get(source, b"") == before_prefix
    before_confirmed_at = before_captured_at + timedelta(seconds=2)
    released_at = None
    if not queued:
        assert prior_status["held_sources"] == 1
        released_at = before_confirmed_at + timedelta(seconds=1)
        queued = True
    native.write(source, rows)
    case.clock.now.return_value = before_confirmed_at + timedelta(seconds=2)
    case.collect()
    case.collect()
    after, after_status = ledger.as_of(), status_bytes()
    accepted = receipt_in(after).record
    assert (
        accepted.disposition is MarkerDisposition.ACCEPTED
        and accepted.boundary is not None
    )
    (first,) = (
        row.key.value.split(":")[1]
        for row in after.current
        if isinstance(row.record, UsageObservation)
        and row.record.boundary == accepted.boundary
    )

    saved, snapshot, settled, captured, late_capture = (
        Path("/fixture") / name
        for name in (
            "original-publication.json",
            "prior-status.json",
            "settled-status.json",
            "prior-source.jsonl",
            "late-capture.jsonl",
        )
    )
    artifacts = {
        saved: publication,
        snapshot: before_status,
        settled: after_status,
        captured: before_prefix,
        late_capture: before_prefix,
    }

    def read_owned(path, *, private, limit):
        assert private
        raw = native.contents[path] if path == source else artifacts[path]
        assert len(raw) <= limit
        return raw

    def stat_for(identity, when):
        device, inode = identity
        stamp = when.timestamp()
        return SimpleNamespace(
            st_dev=device,
            st_ino=inode,
            st_mtime=stamp,
            st_ctime=stamp,
            st_birthtime=stamp,
        )

    stat = Path.stat
    stats = {
        source: stat_for(native.identities[source], marker.published_at),
        captured: stat_for((2, 1), before_captured_at - timedelta(seconds=1)),
        late_capture: stat_for((2, 2), before_confirmed_at + timedelta(seconds=1)),
    }
    fixed_views = {view.sequence: view for view in (before, after)}
    monkeypatch.setattr(
        Ledger,
        "as_of",
        lambda self, sequence=None: (
            after if sequence is None else fixed_views[sequence]
        ),
    )
    monkeypatch.setattr(
        Path,
        "stat",
        lambda path, **kw: stats[path] if path in stats else stat(path, **kw),
    )
    monkeypatch.setattr(qualification, "_read_owned", read_owned)
    verified_at = case.clock.now.return_value + timedelta(seconds=1)
    monkeypatch.setattr(qualification, "_now", lambda: verified_at)

    prefix = native.contents[source]
    entry = qualification._OrderEvidence(
        marker.project_id,
        marker.provider,
        qualification._Order(arrival),
        key.value.split(":")[1],
        sha256(publication).hexdigest(),
        sha256(before_prefix).hexdigest(),
        sha256(prefix).hexdigest(),
        first,
        before.sequence,
        after.sequence,
    )
    proof = qualification._OrderProof(
        str(ledger.root),
        str(saved),
        str(source),
        len(prefix),
        str(snapshot),
        str(settled),
        str(captured),
        len(before_prefix),
        before_captured_at,
        before_confirmed_at,
        released_at,
    )
    card = service.load_rate_card()
    if withhold_target:
        assert accepted.boundary.ordinal >= before_prefix.count(b"\n")
        with pytest.raises(qualification.QualificationError, match="processing-order"):
            qualification._verify_order(entry, proof, card)
        artifacts[captured] = prefix
        qualification._verify_order(
            replace(entry, before_prefix_sha256=entry.prefix_sha256),
            replace(proof, before_prefix_bytes=len(prefix)),
            card,
        )
        return
    qualification._verify_order(entry, proof, card)
    for altered in (
        replace(proof, before_source=str(late_capture)),
        replace(proof, before_captured_at=before_confirmed_at),
    ):
        with pytest.raises(qualification.QualificationError, match="processing-order"):
            qualification._verify_order(entry, altered, card)
    artifacts[saved] += b" "
    with pytest.raises(qualification.QualificationError, match="processing-order"):
        qualification._verify_order(entry, proof, card)


@pytest.mark.parametrize(
    ("provider", "arrival", "withhold_target"),
    [
        ("codex", "marker-first", False),
        ("claude", "marker-first", False),
        ("codex", "boundary-first", False),
        ("claude", "boundary-first", False),
        pytest.param("claude", "boundary-first", True, id="held-without-target"),
    ],
)
def test_processing_orders_require_native_prefix_and_fixed_ledger(
    request, monkeypatch, provider, arrival, withhold_target
):
    from dataclasses import replace
    from functools import partial
    from hashlib import sha256

    import test_claude as claude
    from test_service_process import PROJECT, _mark_args

    from aitm_usage.ledger import Ledger
    from aitm_usage.pricing import load_rate_card
    from aitm_usage.qualification import (
        QualificationError,
        _Order,
        _OrderEvidence,
        _OrderProof,
        _verify_order,
    )
    from aitm_usage.scopes import INBOX_NAME, enqueue_command
    from aitm_usage.service import (
        STATUS_NAME,
        collect_once,
        register_project,
        remember_claude_session,
    )
    from aitm_usage.types import UsageObservation

    if (provider, arrival, withhold_target) != ("claude", "boundary-first", False):
        _assert_processing_order_in_memory(
            request.getfixturevalue("collector_policy"),
            monkeypatch,
            provider,
            arrival,
            withhold_target,
        )
        return

    tmp_path = request.getfixturevalue("tmp_path")
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    root = tmp_path / "private state"
    sources = tmp_path / "sources"
    checkout = tmp_path / "unanchored qualification checkout"
    for directory in (sources, checkout):
        directory.mkdir(mode=0o700)
    config = tmp_path / "config.json"
    config.write_text(
        json.dumps(
            {
                "project_id": str(PROJECT),
                "source_roots": [str(sources)],
                "checkout_anchors": [],
                "cutoff": claude.CUTOFF.isoformat(),
            }
        )
    )
    registration = register_project(root, config)
    ledger = Ledger.open(root, PROJECT)
    public_receipt = tmp_path / "qualification-receipt.json"
    public_receipt.write_text(json.dumps(_receipt()))
    public_receipt.chmod(0o644)
    assert qualification.read_activation_receipt(
        public_receipt
    ) == qualification.decode_activation_receipt(public_receipt.read_bytes())
    source = sources / f"{provider}.jsonl"
    command, rows = _processing_order_transcript(
        ledger, checkout, provider, partial(_mark_args, tmp_path)
    )
    from test_scan import _native_startup_rows, _startup_bytes

    startup = _native_startup_rows(checkout)
    for row in startup:
        row["sessionId"] = str(claude.SESSION)
    rows = [*startup, *rows[1:]]
    marker = command.payload
    target, kind = command.command_id, marker.provider
    remember_claude_session(ledger, marker.session_ref)

    assert enqueue_command(root, command) is None
    queued = root / INBOX_NAME / f"{target}.json"
    saved = _write_private(tmp_path / "original-publication.json", queued.read_bytes())
    queued.unlink()
    claude.write(source, rows)
    source.chmod(0o600)
    before_prefix = source.read_bytes()
    before_source = _write_private(tmp_path / "prior-source.jsonl", before_prefix)
    before_captured_at = datetime.now(UTC)
    before = collect_once(registration, ledger)
    snapshot = _write_private(
        tmp_path / "prior-status.json", (root / STATUS_NAME).read_bytes()
    )
    assert source.read_bytes() == before_prefix
    before_confirmed_at = datetime.now(UTC)
    assert before.held_sources == 1
    (checkpoint,) = ledger.as_of().checkpoints
    assert checkpoint.cursor.offset == len(_startup_bytes(startup[:4]))
    assert not any(
        isinstance(row.record, UsageObservation) for row in ledger.as_of().current
    )
    _write_private(queued, saved.read_bytes())
    released_at = datetime.now(UTC)
    admitted = collect_once(registration, ledger)
    assert admitted.deferred_sources == 1
    assert not any(
        isinstance(row.record, UsageObservation) for row in ledger.as_of().current
    )
    after = collect_once(registration, ledger)
    settled = _write_private(
        tmp_path / "settled-status.json", (root / STATUS_NAME).read_bytes()
    )
    accepted = ledger.command_receipt(command)
    assert accepted is not None and accepted.boundary is not None
    (first,) = [
        row.key.value.split(":")[1]
        for row in ledger.as_of().current
        if isinstance(row.record, UsageObservation)
        and row.record.boundary == accepted.boundary
    ]
    entry = _OrderEvidence(
        PROJECT,
        kind,
        _Order(arrival),
        ledger.pseudonymize("inbox-command", str(target)).value.split(":")[1],
        sha256(saved.read_bytes()).hexdigest(),
        sha256(before_prefix).hexdigest(),
        sha256(source.read_bytes()).hexdigest(),
        first,
        before.sequence,
        after.sequence,
    )
    proof = _OrderProof(
        str(root),
        str(saved),
        str(source),
        source.stat().st_size,
        str(snapshot),
        str(settled),
        str(before_source),
        len(before_prefix),
        before_captured_at,
        before_confirmed_at,
        released_at,
    )
    _verify_order(entry, proof, load_rate_card())
    late_capture = _write_private(tmp_path / "late-capture.jsonl", before_prefix)
    with pytest.raises(QualificationError, match="processing-order"):
        _verify_order(
            entry, replace(proof, before_source=str(late_capture)), load_rate_card()
        )
    with pytest.raises(QualificationError, match="processing-order"):
        _verify_order(
            entry,
            replace(proof, before_captured_at=before_confirmed_at),
            load_rate_card(),
        )
    saved.write_bytes(saved.read_bytes() + b" ")
    with pytest.raises(QualificationError, match="processing-order"):
        _verify_order(entry, proof, load_rate_card())


def _observe_export_snapshots(snapshots, monkeypatch):
    import os
    import stat
    from contextlib import nullcontext
    from io import BytesIO
    from types import SimpleNamespace

    from aitm_usage import export

    folders = dict(enumerate(snapshots, 1))
    entries = {
        (parent, name): (index, snapshots[folder][name])
        for parent, folder in folders.items()
        for index, name in enumerate(snapshots[folder], 10 * parent)
    }
    by_descriptor = {fd: data for fd, data in entries.values()}

    def file_status(fd):
        data = by_descriptor[fd]
        return os.stat_result(
            (stat.S_IFREG | 0o600, fd, 1, 1, os.geteuid(), 0, len(data), 0, 0, 0)
        )

    def file_open(name, flags, *, dir_fd):
        assert flags == os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        return entries[dir_fd, name][0]

    def file_stat(name, *, dir_fd, follow_symlinks):
        assert not follow_symlinks
        return file_status(entries[dir_fd, name][0])

    pins = {
        folder: SimpleNamespace(fd=fd, identities=((1, fd),), check=Mock())
        for fd, folder in folders.items()
    }
    monkeypatch.setattr(
        qualification, "_pin_directory", lambda path: nullcontext(pins[path])
    )
    monkeypatch.setattr(export, "_check_acl", Mock())
    monkeypatch.setattr(
        export,
        "os",
        SimpleNamespace(
            O_RDONLY=os.O_RDONLY,
            O_NOFOLLOW=os.O_NOFOLLOW,
            O_NONBLOCK=os.O_NONBLOCK,
            listdir=lambda fd: tuple(snapshots[folders[fd]]),
            open=file_open,
            fdopen=lambda fd, mode: BytesIO(by_descriptor[fd]),
            fstat=file_status,
            stat=file_stat,
            path=os.path,
        ),
    )
    return pins


def test_fixed_export_uses_actual_ledger_and_replay_bytes(reference_rates, monkeypatch):
    from dataclasses import replace

    from test_export import _observation
    from test_install import PROJECT
    from test_ledger import _LedgerRows, _memory_ledger

    from aitm_usage import export
    from aitm_usage import ledger as store
    from aitm_usage.ledger import Ledger
    from aitm_usage.qualification import QualificationError, _verify_exports
    from aitm_usage.types import LedgerBatch

    ledger = replace(_memory_ledger(store, PROJECT, b"q" * 32), _writer=object())
    rows = _LedgerRows(ledger.identity, store.APPLICATION_ID, ())
    monkeypatch.setattr(Ledger, "require_writer", lambda _: None)
    monkeypatch.setattr(Ledger, "reader", lambda _: rows.connect(write=False))
    monkeypatch.setattr(
        Ledger, "_write_transaction", lambda _: rows.connect(write=True)
    )
    usage, _ = _observation(ledger, "first")
    ledger.apply(LedgerBatch((usage,)))
    view = ledger.as_of()
    card = reference_rates
    receipt, serialized = export._render(view, card)
    snapshots = {ledger.root / name: dict(serialized) for name in ("before", "after")}
    pins = _observe_export_snapshots(snapshots, monkeypatch)
    before, after = map(str, snapshots)
    _verify_exports(view, card, receipt.sha256, 1, (before, after))
    assert all(pin.check.call_count == 1 for pin in pins.values())
    with pytest.raises(QualificationError, match="export-parity"):
        _verify_exports(view, card, "0" * 64, 1, (before, after))
    with pytest.raises(QualificationError, match="export-parity"):
        _verify_exports(view, card, receipt.sha256, 1, (before, before))

    duplicate = replace(usage, key=ledger.pseudonymize("activation-test", "duplicate"))
    ledger.apply(LedgerBatch((duplicate,)))
    with pytest.raises(QualificationError, match="duplicate-observation"):
        _verify_exports(ledger.as_of(), card, receipt.sha256, 1, (before, after))


@pytest.mark.parametrize(
    "scope_case",
    [
        "controlled",
        "real-96",
        "core-graduation",
        "core-child-b",
        "core-ancestor",
        "core-epic-parent",
        "core-catchup",
        "late-alias",
        "late-ancestor",
        "late-live-alias",
    ],
)
def test_workflow_is_bound_to_shared_session_overlap_and_graduation(
    monkeypatch, scope_case
):
    from dataclasses import replace
    from datetime import timedelta
    from uuid import UUID

    from test_export import _observation
    from test_install import PROJECT
    from test_ledger import _memory_ledger

    from aitm_usage import ledger as store
    from aitm_usage import scopes
    from aitm_usage.qualification import (
        QualificationError,
        _usage,
        _verify_catchup,
        _verify_relationship_continuity,
        _verify_workflow,
        _Workflow,
        decode_activation_receipt,
    )
    from aitm_usage.scopes import BoundaryEvidence
    from aitm_usage.sources.scan import checkout_anchor_reference
    from aitm_usage.types import (
        ClientVersion,
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
        Registration,
        ReviewRole,
        Revision,
        WorkPhase,
    )

    ledger = _memory_ledger(store, PROJECT, b"q" * 32)
    planning_path = Path("/fixture/planning")
    dev_path = Path("/fixture/development")
    history = [LedgerView(PROJECT, 0, (), ())]
    registration = Registration(
        PROJECT,
        ledger.root,
        (Path("/fixture/transcripts"),),
        (planning_path, dev_path),
        CHECKED,
    )
    monkeypatch.setattr(
        qualification,
        "_effective_registration",
        lambda ledger, view: (registration, ()),
    )
    monkeypatch.setattr(
        store.Ledger,
        "as_of",
        lambda self, sequence=None: history[-1 if sequence is None else sequence],
    )

    def put(*revisions):
        prior = history[-1]
        history.append(
            replace(
                prior,
                sequence=prior.sequence + 1,
                revisions=(*prior.revisions, *revisions),
            )
        )

    def admit(command, evidence=()):
        disposition, matched, effects = scopes._evaluate(
            ledger, command, history[-1], evidence, {}
        )
        assert disposition is MarkerDisposition.ACCEPTED
        receipt = CommandReceipt(
            command,
            ledger.validate_command(command),
            disposition,
            None if matched is None else matched.boundary,
            None if matched is None else matched.anchor_ref,
        )
        key = ledger.pseudonymize("inbox-command", str(command.command_id))
        put(*effects, Revision(key, 1, receipt))

    project_id = ledger.identity.project_id
    template, marker = _observation(ledger, "first")
    start = template.record.observed_at
    epic = ItemKey(ItemKind.ISSUE, 83)
    child_a = ItemKey(ItemKind.DRAFT, UUID(int=812))
    child_b = ItemKey(ItemKind.DRAFT, UUID(int=813))
    core = ItemKey(ItemKind.ISSUE, 2)
    delivery = ItemKey(ItemKind.ISSUE, 96)
    graduated = (
        core
        if scope_case == "core-graduation"
        else ItemKey(ItemKind.ISSUE, 1_000_000_095)
    )
    dev_checkout = checkout_anchor_reference(ledger, dev_path)
    planning_checkout = checkout_anchor_reference(ledger, planning_path)
    author = ledger.pseudonymize("activation-test", "author")
    reviewer = ledger.pseudonymize("activation-test", "reviewer")
    attempt = ledger.pseudonymize("activation-test", "attempt")

    def append(index, scope_sequence, item, phase, group, when, *, new_marker=True):
        provider = Provider.CODEX if group == "author" else Provider.CLAUDE
        version = (
            ClientVersion.CODEX_0_167_0_ALPHA_3_2
            if provider is Provider.CODEX
            else ClientVersion.CLAUDE_2_1_318
        )
        command_id = UUID(int=900 + index)
        session = ledger.pseudonymize("activation-test", f"session-{group}")
        stream = ledger.pseudonymize("activation-test", f"stream-{group}")
        target = ledger.pseudonymize("activation-test", f"boundary-{index}")
        moment = start + timedelta(seconds=when)
        boundary = replace(
            template.record.boundary,
            provider=provider,
            stream_ref=stream,
            session_ref=session,
            ordinal=index,
            boundary_ref=target,
            receipt_ref=ledger.pseudonymize("scope-receipt", str(command_id))
            if new_marker
            else None,
        )
        claim = replace(
            marker,
            marker_id=command_id,
            provider=provider,
            session_ref=session,
            scope_sequence=scope_sequence,
            boundary_ref=target,
            item=item,
            phase=phase,
            project_id=project_id,
            published_at=moment - timedelta(seconds=1),
            receipt_ref=boundary.receipt_ref,
            participant_ref=reviewer if group == "review" else author,
            role=ReviewRole.REVIEWER if group == "review" else ReviewRole.AUTHOR,
            attempt_ref=attempt if group == "development" else None,
            review_ref=ledger.pseudonymize("activation-test", "review")
            if group == "review"
            else None,
        )
        anchor = dev_checkout if group == "development" else planning_checkout
        payload = (
            DevelopmentBinding(claim, anchor, 1)
            if phase is WorkPhase.DEVELOPMENT
            else claim
        )
        observation = replace(
            template.record,
            boundary=boundary,
            observed_at=moment,
            client_version=version,
            request_ref=target,
        )
        key = ledger.pseudonymize("activation-test", f"usage-{index}")
        revision = replace(template, key=key, record=observation)
        command = InboxCommand(command_id, project_id, payload)
        evidence = (BoundaryEvidence(boundary, anchor),)
        if new_marker:
            admit(command, evidence)
        put(revision)
        return key.value.split(":")[1]

    def relationship(payload):
        command = InboxCommand(payload.command_id, project_id, payload)
        admit(command)
        return ledger.as_of().sequence

    relationship(ItemParent(UUID(int=920), project_id, child_a, epic))
    relationship(ItemParent(UUID(int=921), project_id, child_b, epic))
    batch = append(1, 1, epic, WorkPhase.PLANNING, "author", 1)
    review_start = append(2, 1, child_b, WorkPhase.DOCUMENT_REVIEW, "review", 2)
    focus_a = append(3, 2, child_a, WorkPhase.PLANNING, "author", 3)
    focus_b = append(4, 3, child_b, WorkPhase.PLANNING, "author", 4)
    review_end = append(
        5, 1, child_b, WorkPhase.DOCUMENT_REVIEW, "review", 5, new_marker=False
    )
    returned = append(6, 4, epic, WorkPhase.PLANNING, "author", 6)
    graduation = relationship(DraftAlias(UUID(int=922), project_id, child_a, graduated))
    owner_item = graduated
    if scope_case == "core-child-b":
        relationship(DraftAlias(UUID(int=923), project_id, child_b, core))
    elif scope_case == "core-epic-parent":
        relationship(ItemParent(UUID(int=924), project_id, epic, core))
    elif scope_case in ("core-ancestor", "real-96"):
        owner_item = delivery
        if scope_case == "core-ancestor":
            relationship(ItemParent(UUID(int=925), project_id, core, epic))
        relationship(
            ItemParent(
                UUID(int=926),
                project_id,
                delivery,
                core if scope_case == "core-ancestor" else epic,
            )
        )
    development = append(7, 1, owner_item, WorkPhase.DEVELOPMENT, "development", 7)
    housekeeping = append(8, 5, epic, WorkPhase.HOUSEKEEPING, "author", 8)
    workflow = _Workflow(
        batch,
        focus_a,
        focus_b,
        returned,
        review_start,
        review_end,
        development,
        housekeeping,
        graduation,
        3,
        8,
        2 if owner_item == graduated else 1,
        3,
    )
    view = ledger.as_of()
    if scope_case.startswith("core-") and scope_case != "core-catchup":
        with pytest.raises(QualificationError, match="workflow-evidence"):
            _verify_workflow(
                ledger, view, workflow, start, start + timedelta(seconds=9)
            )
        return
    _verify_workflow(ledger, view, workflow, start, start + timedelta(seconds=9))
    for forged in (
        replace(workflow, review_start=review_end, review_end=review_start),
        replace(workflow, graduation_sequence=graduation - 1),
        replace(workflow, development=housekeeping, housekeeping=development),
        replace(workflow, child_a_direct=3),
    ):
        with pytest.raises(QualificationError, match="workflow-evidence"):
            _verify_workflow(ledger, view, forged, start, start + timedelta(seconds=9))

    if scope_case == "late-alias":
        relationship(DraftAlias(UUID(int=927), project_id, child_b, core))
    elif scope_case == "late-ancestor":
        relationship(ItemParent(UUID(int=928), project_id, core, epic))
        relationship(ItemParent(UUID(int=929), project_id, child_b, core))

    author_catchup = append(
        9,
        6,
        core if scope_case == "core-catchup" else epic,
        WorkPhase.PLANNING,
        "author",
        10,
        new_marker=scope_case == "core-catchup",
    )
    review_catchup = append(
        10,
        1,
        child_b,
        WorkPhase.DOCUMENT_REVIEW,
        "review",
        11,
        new_marker=False,
    )
    after = ledger.as_of()
    measurements = _usage(after)
    keys = {Provider.CODEX: author_catchup, Provider.CLAUDE: review_catchup}
    receipt = decode_activation_receipt(FIXTURE.read_bytes())
    receipt = replace(
        receipt,
        workflow=workflow,
        collector=replace(
            receipt.collector,
            previous_heartbeat=start + timedelta(seconds=9),
            producer_started=start + timedelta(seconds=12),
        ),
        export=replace(
            receipt.export, catchup_codex=author_catchup, catchup_claude=review_catchup
        ),
        providers=tuple(
            replace(
                provider,
                stream=measurements[
                    keys[provider.provider]
                ].boundary.stream_ref.value.split(":")[1],
            )
            for provider in receipt.providers
        ),
    )
    if scope_case == "core-catchup":
        with pytest.raises(QualificationError, match="replay-evidence"):
            _verify_catchup(receipt, view, after)
    elif scope_case in ("late-alias", "late-ancestor"):
        with pytest.raises(QualificationError, match="relationship-changed"):
            _verify_catchup(receipt, view, after)
    else:
        _verify_catchup(receipt, view, after)
    if scope_case == "late-live-alias":
        relationship(DraftAlias(UUID(int=930), project_id, child_b, core))
        with pytest.raises(QualificationError, match="relationship-changed"):
            _verify_relationship_continuity(after, ledger.as_of())


def _recovery_evidence(proof, export, backed_up_at, restored_at):
    from uuid import UUID

    return qualification._RecoveryEvidence(
        UUID(proof.backup.project_id),
        proof.backup.sequence,
        export.row_count,
        proof.backup.manifest_sha256,
        export.sha256,
        export.sha256,
        export.sha256,
        export.sha256,
        proof.upgrade.version,
        proof.upgrade.wheel_sha256,
        datetime.fromisoformat(proof.initial.producer_started),
        backed_up_at,
        restored_at,
        datetime.fromisoformat(proof.upgrade.heartbeat),
        datetime.fromisoformat(proof.rollback.heartbeat),
    )


def test_recovery_proves_exact_retained_bundle_and_fixed_parity(
    install_policy_ledger, reference_rates, monkeypatch
):
    from dataclasses import replace
    from datetime import timedelta
    from hashlib import sha256
    from types import SimpleNamespace
    from uuid import UUID

    from test_export import _observation

    from aitm_usage import export, install
    from aitm_usage.backup import BackupReceipt
    from aitm_usage.ledger import Ledger
    from aitm_usage.service import REGISTRATION_NAME
    from aitm_usage.types import LedgerView

    ledger = install_policy_ledger
    identity = ledger.identity
    project_id = str(identity.project_id)
    label = f"org.aitm.usage.{project_id}"
    usage, _ = _observation(ledger, "first")
    view = LedgerView(identity.project_id, 2, (usage,), ())
    result, files = export._render(view, reference_rates)
    snapshots = tuple(
        ledger.root / stage
        for stage in ("before", "restored", "upgraded", "rolled-back")
    )
    _observe_export_snapshots(dict.fromkeys(snapshots, files), monkeypatch)

    bundle = Path("/fixture/backup")
    upgrade_id, rollback_id = str(UUID(int=471)), str(UUID(int=472))
    observed = {}

    def observe_backup(path, database):
        contents = {
            qualification._KEY: b"owned key",
            qualification._DATABASE: database,
            REGISTRATION_NAME: b"owned registration",
        }
        manifest = {
            "format": "aitm-usage.backup/v1",
            "project_id": project_id,
            "key_id": identity.key_id,
            "schema_version": identity.schema_version,
            "sequence": view.sequence,
            "files": {
                name: sha256(data).hexdigest() for name, data in contents.items()
            },
        }
        proof = ledger.pseudonymize(
            "collector-backup-manifest", qualification._json(manifest).decode()
        )
        raw = qualification._json({**manifest, "proof": proof.value})
        observed.update({path / name: data for name, data in contents.items()})
        observed[path / "manifest.json"] = raw
        return BackupReceipt(
            identity.project_id,
            identity.key_id,
            identity.schema_version,
            view.sequence,
            sha256(raw).hexdigest(),
        )

    saved = observe_backup(bundle, b"snapshot sqlite bytes")
    upgrade_backup = observe_backup(
        ledger.root / "service-backups" / upgrade_id, b"upgrade sqlite bytes"
    )
    rollback_backup = observe_backup(
        ledger.root / "service-backups" / rollback_id, b"rollback sqlite bytes"
    )

    def lifecycle(status, seconds, *, sibling=False, backup=None, backup_id=None):
        started = CHECKED + timedelta(seconds=seconds)
        return install.InstallReceipt(
            project_id,
            label,
            status,
            "0.1.1" if sibling else "0.1.0",
            ("b" if sibling else "a") * 64,
            "3.13.9",
            heartbeat=(started + timedelta(seconds=1)).isoformat(),
            producer_mode="service",
            producer_pid=321,
            producer_started=started.isoformat(),
            backup=backup,
            backup_id=backup_id,
        )

    proof = qualification._RecoveryProof(
        str(ledger.root),
        str(bundle),
        lifecycle("installed", 0),
        install.InstallReceipt(project_id, label, "stopped"),
        qualification._BackupProof("backed-up", **saved.as_dict()),
        qualification._BackupProof("restored", **saved.as_dict()),
        lifecycle("installed", 4),
        lifecycle(
            "upgraded", 6, sibling=True, backup=upgrade_backup, backup_id=upgrade_id
        ),
        lifecycle("upgraded", 8, backup=rollback_backup, backup_id=rollback_id),
        *map(str, snapshots),
    )
    backed_up_at = CHECKED + timedelta(seconds=2)
    restored_at = CHECKED + timedelta(seconds=3)
    evidence = _recovery_evidence(proof, result, backed_up_at, restored_at)
    collector = _collector_for_lifecycle(proof.initial)
    wheels = {
        install._wheel_path(ledger, receipt.version, receipt.wheel_sha256): receipt
        for receipt in (proof.initial, proof.upgrade)
    }

    def read_wheel(path, digest, *, private):
        assert private and digest == wheels[path].wheel_sha256
        return SimpleNamespace(
            files={
                Path("aitm_usage/cli.py"): b"identical installed source",
                Path(
                    f"aitm_usage-{wheels[path].version}.dist-info/METADATA"
                ): b"distinct versions",
            }
        )

    open_ledger = Mock(return_value=ledger)
    registration = Mock()
    monkeypatch.setattr(Ledger, "open", open_ledger)

    def read_fixed_view(actual, cutoff):
        assert actual is ledger and cutoff == view.sequence
        return view

    monkeypatch.setattr(Ledger, "as_of", read_fixed_view)
    monkeypatch.setattr(qualification, "load_registration", registration)
    monkeypatch.setattr(qualification, "_wheel", read_wheel)
    monkeypatch.setattr(qualification, "_read_proof", lambda path, *_: observed[path])

    verify = qualification._verify_recovery
    verify(evidence, proof, collector, reference_rates)
    open_ledger.assert_called_once_with(ledger.root, identity.project_id)
    registration.assert_called_once_with(ledger)
    with pytest.raises(qualification.QualificationError, match="recovery-evidence"):
        verify(
            replace(evidence, restored_at=restored_at - timedelta(days=1)),
            proof,
            collector,
            reference_rates,
        )
    observed[bundle / "manifest.json"] = b"{}"
    with pytest.raises(qualification.QualificationError, match="recovery-parity"):
        verify(evidence, proof, collector, reference_rates)


def test_cli_cannot_use_receipt_from_another_registered_project(
    collector_policy,
    monkeypatch,
    capsys,
):
    from aitm_usage import service

    case = collector_policy
    case.configure()
    ledger = case.ledger
    receipt = _receipt()
    path = Path("/fixture/actual-shaped.json")
    proof_path = ledger.root / qualification.PROOF_NAME
    real_exists = Path.exists

    def read_owned(requested, *, private, limit):
        assert requested == path and not private
        assert limit == qualification._MAX_EVIDENCE_BYTES
        return json.dumps(receipt).encode()

    monkeypatch.setattr(qualification, "_now", lambda: CHECKED)
    monkeypatch.setattr(qualification, "_read_owned", read_owned)
    monkeypatch.setattr(
        Path, "exists", lambda path: path == proof_path or real_exists(path)
    )
    open_project = Mock(return_value=ledger)
    supervisor = Mock()
    monkeypatch.setattr(cli, "open_project", open_project)
    monkeypatch.setattr(cli, "ServiceSupervisor", supervisor)
    assert receipt["project_id"] != str(ledger.identity.project_id)
    assert _cli(monkeypatch, capsys, ledger.root, path) == (
        1,
        {"status": "project-mismatch"},
    )
    receipt["project_id"] = str(ledger.identity.project_id)
    receipt["registration_cutoff"] = service.load_registration(
        ledger
    ).cutoff.isoformat()
    assert _cli(monkeypatch, capsys, ledger.root, path) == (
        1,
        {"status": "service-evidence"},
    )
    open_project.assert_called_once_with(ledger.root)
    supervisor.assert_called_once_with(ledger)


def _collect_activation_transcripts(case):
    from datetime import timedelta

    from test_claude import request, user
    from test_service import _codex_transcript

    native = case.native
    case.configure()
    native.write(native.root / "codex.jsonl", _codex_transcript(native.checkout))
    native.write(
        native.root / "claude.jsonl", [user(native.checkout), request(native.checkout)]
    )
    case.clock.now.return_value += timedelta(minutes=1)
    return case.collect()


def test_watermarks_bind_historical_authenticated_offsets_and_current_progress(
    collector_policy,
    monkeypatch,
):
    from dataclasses import replace
    from datetime import timedelta

    from test_codex import end

    from aitm_usage import qualification, service
    from aitm_usage.types import Provider

    case = collector_policy
    ledger, native = case.ledger, case.native
    historical = _collect_activation_transcripts(case)
    view = ledger.as_of()
    captured = service._read_status(ledger.root)
    assert isinstance(captured, service._Status)
    receipt = qualification.decode_activation_receipt(FIXTURE.read_bytes())
    expected = {entry.provider: entry for entry in receipt.providers}
    evidence = tuple(
        replace(
            expected[Provider(source["provider"])],
            stream=source["source_ref"].split(":")[1],
            offset=source["offset"],
            observed_through=datetime.fromisoformat(source["observed_through"]),
            retention_seconds=None,
        )
        for source in historical["sources"]
    )
    case.clock.now.return_value += timedelta(seconds=5)
    native.write(native.root / "codex.jsonl", [end()], append=True)
    current = case.collect()
    assert len(evidence) == len(current["sources"]) == 2
    assert any(
        source["offset"] > entry.offset
        for source, entry in zip(current["sources"], evidence, strict=True)
    )
    check_at = case.clock.now.return_value + timedelta(seconds=1)
    monkeypatch.setattr(qualification, "_now", lambda: check_at)
    qualification._verify_watermarks(ledger, view, captured, current, evidence)

    wrong_capture = (replace(evidence[0], offset=evidence[0].offset - 1), evidence[1])
    with pytest.raises(qualification.QualificationError, match="source-watermark"):
        qualification._verify_watermarks(ledger, view, captured, current, wrong_capture)

    forged = replace(
        captured,
        observed=(
            replace(
                captured.observed[0],
                proof=ledger.pseudonymize("fixture", "wrong-proof"),
            ),
            *captured.observed[1:],
        ),
    )
    with pytest.raises(qualification.QualificationError, match="source-watermark"):
        qualification._verify_watermarks(ledger, view, forged, current, evidence)

    current["sources"][0]["observed_through"] = None
    with pytest.raises(qualification.QualificationError, match="source-watermark"):
        qualification._verify_watermarks(ledger, view, captured, current, evidence)


def test_retry_and_nested_observations_cannot_be_claimed_without_evidence(
    collector_policy,
):
    from dataclasses import replace

    from aitm_usage import qualification, service

    case = collector_policy
    ledger = case.ledger
    snapshot = _collect_activation_transcripts(case)
    registration = service.load_registration(ledger)
    view = ledger.as_of()
    evidence = qualification.decode_activation_receipt(FIXTURE.read_bytes()).providers[
        0
    ]
    source = next(row for row in snapshot["sources"] if row["provider"] == "codex")
    evidence = replace(
        evidence,
        stream=source["source_ref"].split(":")[1],
        coverage=replace(evidence.coverage, model_switch=qualification._Metric.GAP),
    )
    assert any(
        usage.boundary.stream_ref.value == source["source_ref"]
        for usage in qualification._usage(view).values()
    )
    qualification._verify_live_coverage(ledger, view, evidence, registration.cutoff)
    for field in ("retry", "nested"):
        claimed = replace(
            evidence,
            coverage=replace(
                evidence.coverage, **{field: qualification._Metric.OBSERVED}
            ),
        )
        with pytest.raises(qualification.QualificationError, match="coverage-evidence"):
            qualification._verify_live_coverage(
                ledger, view, claimed, registration.cutoff
            )


def _selected_source_evidence(status):
    from dataclasses import replace

    from aitm_usage.types import Provider

    fixture = qualification.decode_activation_receipt(FIXTURE.read_bytes())
    providers = {entry.provider: entry for entry in fixture.providers}
    return tuple(
        replace(
            providers[Provider(row["provider"])], stream=row["source_ref"].split(":")[1]
        )
        for row in status["sources"]
        if row["observed_through"] is not None
    )


def test_selected_source_gap_refuses_missing_live_file_without_penalizing_unrelated_hold(
    collector_policy, reference_rates
):
    from datetime import timedelta

    from test_claude import request, usage, user
    from test_service import FIXTURES

    case = collector_policy
    ledger, native = case.ledger, case.native
    unrelated = native.checkout.with_name("unbound-checkout")
    rows = [user(unrelated), request(unrelated, counts=usage())]
    for row in rows:
        row["sessionId"] = "00000000-0000-4000-8000-00000000aaaa"
    native.write(native.root / "unrelated.jsonl", rows)
    case.configure()
    case.use_ledger_rows()
    for provider in ("codex", "claude"):
        data = (FIXTURES / provider / "usage.jsonl").read_bytes()
        native.contents[native.root / f"{provider}.jsonl"] = data.replace(
            b"CHECKOUT", str(native.checkout).encode()
        )
    case.clock.now.return_value += timedelta(minutes=1)
    status = case.collect()
    assert status["held_sources"] == 1
    entries = _selected_source_evidence(status)
    assert len(entries) == 2
    view = ledger.as_of()
    qualification._verify_selected_sources(ledger, view, entries, reference_rates)

    del native.contents[native.root / "claude.jsonl"]
    with pytest.raises(qualification.QualificationError, match="selected-source-gap"):
        qualification._verify_selected_sources(ledger, view, entries, reference_rates)
    assert ledger.as_of() == view
