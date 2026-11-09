import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest
from test_install import launch_control as launch_control
from test_install import project as project

from aitm_usage import cli

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
    tmp_path, monkeypatch, capsys
):
    path = tmp_path / "receipt.json"
    path.write_text('{"project_id": "/private/canary", "project_id": "two"}')
    assert _cli(monkeypatch, capsys, tmp_path, path) == (
        1,
        {"status": "invalid-receipt"},
    )


def test_cli_requires_installed_proof_for_actual_qualification(
    tmp_path, monkeypatch, capsys
):
    from aitm_usage import qualification

    monkeypatch.setattr(qualification, "_now", lambda: CHECKED)
    path = tmp_path / "actual-shaped.json"
    path.write_text(json.dumps(_receipt()))
    assert _cli(monkeypatch, capsys, tmp_path, path) == (
        1,
        {"status": "proof-required"},
    )


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


def test_running_witness_rejects_same_pid_different_start_and_same_version_wrong_wheel(
    project,
    tmp_path,
    launch_control,
):
    from dataclasses import replace
    from datetime import timedelta

    from test_install import _wheel
    from test_service import _fixtures

    from aitm_usage import install
    from aitm_usage.qualification import (
        QualificationError,
        _verify_running,
        decode_activation_receipt,
    )

    registration, ledger, _ = project
    _fixtures(registration.source_roots[0], registration.checkout_anchors[0])
    _unbound_claude_source(registration, tmp_path / "other-checkout")
    wheel, digest = _wheel(tmp_path, "qualification")
    lifecycle = install.install_wheel(
        ledger,
        wheel,
        Path(sys._base_executable).resolve(strict=True),
        launch_control,
        action="install",
        expected_sha256=digest,
    )
    sample = decode_activation_receipt(FIXTURE.read_bytes()).collector
    start = datetime.fromisoformat(lifecycle.producer_started)
    heartbeat = datetime.fromisoformat(lifecycle.heartbeat)
    collector = replace(
        sample,
        version=lifecycle.version,
        wheel_sha256=digest,
        interpreter_version=lifecycle.interpreter_version,
        producer_started=start,
        activation_heartbeat=heartbeat,
        heartbeat=heartbeat,
    )
    verified = _verify_running(ledger, collector, lifecycle, launch_control)
    assert verified["producer_mode"] == "service"
    assert verified["held_sources"] == 1
    assert sum(row["observed_through"] is not None for row in verified["sources"]) == 2

    reused_start = start - timedelta(seconds=1)
    with pytest.raises(QualificationError, match="process-incarnation"):
        _verify_running(
            ledger,
            replace(collector, producer_started=reused_start),
            replace(lifecycle, producer_started=reused_start.isoformat()),
            launch_control,
        )

    other_wheel, other_digest = _wheel(tmp_path, "same-version-other-wheel")
    assert other_wheel.name == wheel.name and other_digest != digest
    with pytest.raises(QualificationError, match="wheel-mismatch"):
        _verify_running(
            ledger,
            replace(collector, wheel_sha256=other_digest),
            replace(lifecycle, wheel_sha256=other_digest),
            launch_control,
        )
    assert len(launch_control.bootstraps) == 1


def _write_private(path, data):
    path.write_bytes(data)
    path.chmod(0o600)
    return path


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
    tmp_path, monkeypatch, provider, arrival, withhold_target
):
    import shlex
    from dataclasses import replace
    from hashlib import sha256

    import test_claude as claude
    import test_codex as codex
    from test_service_process import (
        CL_CHILD,
        CX_CHILD,
        CX_EPIC,
        PROJECT,
        _codex_rows,
        _mark_args,
        _marker,
        _queued,
    )

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
    from aitm_usage.types import InboxCommand, Provider, UsageObservation

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
    source = sources / f"{provider}.jsonl"
    kind = Provider(provider)
    target = CX_EPIC if kind is Provider.CODEX else CL_CHILD
    marker = _marker(ledger, kind, target, 1, 83)
    args = _mark_args(tmp_path, marker)
    command = InboxCommand(target, PROJECT, marker)
    if kind is Provider.CODEX:
        other = _mark_args(tmp_path, _marker(ledger, kind, CX_CHILD, 2, 95))
        rows = _codex_rows(
            ledger, checkout, args, other, _queued(target), _queued(CX_CHILD)
        )[:-8]
        write = codex.write
    else:
        shell = shlex.join(("aitm-usage", "--project", str(root), *args))
        rows = [
            claude.user(checkout),
            *claude._native_tool_turn(checkout, shell, _queued(target).decode()),
        ]
        write = claude.write
        remember_claude_session(ledger, marker.session_ref)

    assert enqueue_command(root, command) is None
    queued = root / INBOX_NAME / f"{target}.json"
    saved = _write_private(tmp_path / "original-publication.json", queued.read_bytes())
    if arrival == "boundary-first":
        queued.unlink()
        write(source, rows[:-2] if withhold_target else rows)
        source.chmod(0o600)
    before_prefix = source.read_bytes() if source.exists() else b""
    before_source = _write_private(tmp_path / "prior-source.jsonl", before_prefix)
    before_captured_at = datetime.now(UTC)
    before = collect_once(registration, ledger)
    snapshot = _write_private(
        tmp_path / "prior-status.json", (root / STATUS_NAME).read_bytes()
    )
    assert (source.read_bytes() if source.exists() else b"") == before_prefix
    before_confirmed_at = datetime.now(UTC)
    released_at = None
    if arrival == "marker-first":
        write(source, rows)
        source.chmod(0o600)
    else:
        assert before.held_sources == 1
        _write_private(queued, saved.read_bytes())
        released_at = datetime.now(UTC)
        if withhold_target:
            write(source, rows)
    collect_once(registration, ledger)
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
    if withhold_target:
        with pytest.raises(QualificationError, match="processing-order"):
            _verify_order(entry, proof, load_rate_card())
        return
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


def test_fixed_export_uses_actual_ledger_and_replay_bytes(project, tmp_path):
    from dataclasses import replace

    from test_export import _observation

    from aitm_usage.export import export_as_of
    from aitm_usage.pricing import load_rate_card
    from aitm_usage.qualification import QualificationError, _verify_exports
    from aitm_usage.types import LedgerBatch

    _, ledger, _ = project
    usage, _ = _observation(ledger, "first")
    ledger.apply(LedgerBatch((usage,)))
    view = ledger.as_of()
    card = load_rate_card()
    before, after = tmp_path / "before", tmp_path / "after"
    receipt = export_as_of(view, card, before)
    export_as_of(view, card, after)
    _verify_exports(view, card, receipt.sha256, 1, (str(before), str(after)))
    with pytest.raises(QualificationError, match="export-parity"):
        _verify_exports(view, card, "0" * 64, 1, (str(before), str(after)))
    with pytest.raises(QualificationError, match="export-parity"):
        _verify_exports(view, card, receipt.sha256, 1, (str(before), str(before)))

    duplicate = replace(usage, key=ledger.pseudonymize("activation-test", "duplicate"))
    ledger.apply(LedgerBatch((duplicate,)))
    with pytest.raises(QualificationError, match="duplicate-observation"):
        _verify_exports(
            ledger.as_of(), card, receipt.sha256, 1, (str(before), str(after))
        )


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
    ],
)
def test_workflow_is_bound_to_shared_session_overlap_and_graduation(
    project, scope_case
):
    from dataclasses import replace
    from datetime import timedelta
    from uuid import UUID

    from test_export import _observation
    from test_install import _add_anchor

    from aitm_usage.qualification import (
        QualificationError,
        _usage,
        _verify_catchup,
        _verify_workflow,
        _Workflow,
        decode_activation_receipt,
    )
    from aitm_usage.scopes import BoundaryEvidence, drain_inbox, enqueue_command
    from aitm_usage.sources.scan import checkout_anchor_reference
    from aitm_usage.types import (
        ClientVersion,
        DevelopmentBinding,
        DraftAlias,
        InboxCommand,
        ItemKey,
        ItemKind,
        ItemParent,
        LedgerBatch,
        MarkerDisposition,
        Provider,
        ReviewRole,
        WorkPhase,
    )

    registration, ledger, _ = project
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
    _add_anchor(registration, ledger, ledger.root.parent, 998)
    dev_checkout = checkout_anchor_reference(ledger, ledger.root.parent / "anchor-998")
    planning_checkout = checkout_anchor_reference(
        ledger, registration.checkout_anchors[0]
    )
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
        if new_marker:
            assert (
                enqueue_command(
                    ledger.root, InboxCommand(command_id, project_id, payload)
                )
                is None
            )
        with ledger.writer() as writer:
            if new_marker:
                drain = drain_inbox(writer, (BoundaryEvidence(boundary, anchor),))
                assert drain.receipts[0].disposition is MarkerDisposition.ACCEPTED
            writer.apply(LedgerBatch((replace(template, key=key, record=observation),)))
        return key.value.split(":")[1]

    def relationship(payload):
        assert (
            enqueue_command(
                ledger.root, InboxCommand(payload.command_id, project_id, payload)
            )
            is None
        )
        with ledger.writer() as writer:
            assert (
                drain_inbox(writer, ()).receipts[0].disposition
                is MarkerDisposition.ACCEPTED
            )
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
    else:
        _verify_catchup(receipt, view, after)


def test_recovery_proves_exact_retained_bundle_and_fixed_parity(
    project,
    tmp_path,
    launch_control,
):
    from dataclasses import replace
    from datetime import timedelta
    from hashlib import sha256
    from zipfile import ZipFile

    from test_export import _observation
    from test_install import _wheel

    from aitm_usage import install
    from aitm_usage.backup import backup
    from aitm_usage.export import export_as_of
    from aitm_usage.pricing import load_rate_card
    from aitm_usage.qualification import (
        QualificationError,
        _BackupProof,
        _RecoveryEvidence,
        _RecoveryProof,
        _verify_recovery,
        decode_activation_receipt,
    )
    from aitm_usage.types import LedgerBatch

    _, ledger, _ = project
    sample = decode_activation_receipt(FIXTURE.read_bytes()).collector
    wheel, digest = _wheel(tmp_path, "primary")
    sibling = tmp_path / "aitm_usage-0.1.1-py3-none-any.whl"
    with ZipFile(wheel) as old, ZipFile(sibling, "w") as new:
        for name in old.namelist():
            content = old.read(name)
            if name.endswith(("METADATA", "RECORD")):
                content = content.replace(b"0.1.0", b"0.1.1")
            new.writestr(
                name.replace(
                    "aitm_usage-0.1.0.dist-info", "aitm_usage-0.1.1.dist-info"
                ),
                content,
            )
    sibling_digest = sha256(sibling.read_bytes()).hexdigest()
    interpreter = Path(sys._base_executable).resolve(strict=True)

    def activate(path, expected, action):
        return install.install_wheel(
            ledger,
            path,
            interpreter,
            launch_control,
            action=action,
            expected_sha256=expected,
        )

    def snapshot(label):
        path = tmp_path / label
        return str(path), export_as_of(ledger.as_of(saved.sequence), card, path)

    card = load_rate_card()
    usage, _ = _observation(ledger, "first")
    ledger.apply(LedgerBatch((usage,)))
    initial = activate(wheel, digest, "install")
    bundle = tmp_path / "bundle"
    saved = backup(ledger, bundle)
    backup_at = datetime.now(UTC)
    before, export = snapshot("before")
    stop = install.stop_agent(ledger, launch_control)
    restored = install.restore_for_agent(ledger, bundle, launch_control)
    restore_at = datetime.now(UTC)
    restored_path, _ = snapshot("restored")
    resumed = activate(wheel, digest, "install")
    upgraded = activate(sibling, sibling_digest, "upgrade")
    upgraded_path, _ = snapshot("upgraded")
    rollback = activate(wheel, digest, "upgrade")
    rollback_path, _ = snapshot("rolled-back")
    collector = replace(
        sample,
        version=initial.version,
        wheel_sha256=digest,
        interpreter_version=initial.interpreter_version,
    )
    evidence = _RecoveryEvidence(
        ledger.identity.project_id,
        saved.sequence,
        1,
        saved.manifest_sha256,
        export.sha256,
        export.sha256,
        export.sha256,
        export.sha256,
        upgraded.version,
        sibling_digest,
        datetime.fromisoformat(initial.producer_started),
        backup_at,
        restore_at,
        datetime.fromisoformat(upgraded.heartbeat),
        datetime.fromisoformat(rollback.heartbeat),
    )
    proof = _RecoveryProof(
        str(ledger.root),
        str(bundle),
        initial,
        stop,
        _BackupProof("backed-up", **saved.as_dict()),
        _BackupProof("restored", **restored.as_dict()),
        resumed,
        upgraded,
        rollback,
        before,
        restored_path,
        upgraded_path,
        rollback_path,
    )
    _verify_recovery(evidence, proof, collector, card)
    with pytest.raises(QualificationError, match="recovery-evidence"):
        _verify_recovery(
            replace(evidence, restored_at=restore_at - timedelta(days=1)),
            proof,
            collector,
            card,
        )
    (bundle / "manifest.json").write_bytes(b"{}")
    with pytest.raises(QualificationError, match="recovery-parity"):
        _verify_recovery(evidence, proof, collector, card)


def test_cli_cannot_use_receipt_from_another_registered_project(
    project,
    tmp_path,
    monkeypatch,
    capsys,
):
    from aitm_usage import qualification

    _, ledger, _ = project
    monkeypatch.setattr(qualification, "_now", lambda: CHECKED)
    _write_private(ledger.root / "activation-proof.json", b"{}")
    path = tmp_path / "actual-shaped.json"
    path.write_text(json.dumps(_receipt()))
    assert _cli(monkeypatch, capsys, ledger.root, path) == (
        1,
        {"status": "project-mismatch"},
    )
    receipt = _receipt()
    receipt["project_id"] = str(ledger.identity.project_id)
    receipt["registration_cutoff"] = "2026-11-09T16:00:00+00:00"
    path.write_text(json.dumps(receipt))
    assert _cli(monkeypatch, capsys, ledger.root, path) == (
        1,
        {"status": "service-evidence"},
    )


def test_watermarks_bind_historical_authenticated_offsets_and_current_progress(
    project,
    monkeypatch,
):
    from dataclasses import replace
    from datetime import timedelta

    from test_service import _fixtures

    from aitm_usage import qualification, service
    from aitm_usage.types import Provider, _decode

    registration, ledger, _ = project
    _fixtures(registration.source_roots[0], registration.checkout_anchors[0])
    service.collect_once(registration, ledger)
    view = ledger.as_of()
    raw = (ledger.root / service.STATUS_NAME).read_bytes()
    captured = _decode(raw, service._Status, validate_ref=ledger.validate_source_ref)
    current = service.status_report(ledger.root, ledger)
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
        for source in current["sources"]
    )
    check_at = max(entry.observed_through for entry in evidence) + timedelta(seconds=10)
    monkeypatch.setattr(qualification, "_now", lambda: check_at)
    qualification._verify_watermarks(ledger, view, captured, current, evidence)

    wrong_capture = (replace(evidence[0], offset=evidence[0].offset - 1), evidence[1])
    with pytest.raises(qualification.QualificationError, match="source-watermark"):
        qualification._verify_watermarks(ledger, view, captured, current, wrong_capture)

    current["sources"][0]["observed_through"] = None
    with pytest.raises(qualification.QualificationError, match="source-watermark"):
        qualification._verify_watermarks(ledger, view, captured, current, evidence)


def test_retry_and_nested_observations_cannot_be_claimed_without_evidence(project):
    from dataclasses import replace

    from test_service import _fixtures

    from aitm_usage import qualification, service

    registration, ledger, _ = project
    _fixtures(registration.source_roots[0], registration.checkout_anchors[0])
    service.collect_once(registration, ledger)
    view = ledger.as_of()
    snapshot = service.status_report(ledger.root, ledger)
    evidence = qualification.decode_activation_receipt(FIXTURE.read_bytes()).providers[
        0
    ]
    source = next(row for row in snapshot["sources"] if row["provider"] == "codex")
    evidence = replace(
        evidence,
        stream=source["source_ref"].split(":")[1],
        coverage=replace(evidence.coverage, model_switch=qualification._Metric.GAP),
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


def test_selected_source_gap_refuses_missing_live_file_without_penalizing_unrelated_hold(
    project,
    tmp_path,
):
    from dataclasses import replace

    from test_service import _fixtures

    from aitm_usage import qualification, service
    from aitm_usage.pricing import load_rate_card
    from aitm_usage.types import Provider

    registration, ledger, _ = project
    approved = registration.source_roots[0]
    _fixtures(approved, registration.checkout_anchors[0])
    _unbound_claude_source(registration, tmp_path / "unbound")
    service.collect_once(registration, ledger)
    status = service.status_report(ledger.root, ledger)
    assert status["held_sources"] == 1
    fixture = qualification.decode_activation_receipt(FIXTURE.read_bytes())
    providers = {entry.provider: entry for entry in fixture.providers}
    entries = tuple(
        replace(
            providers[Provider(row["provider"])], stream=row["source_ref"].split(":")[1]
        )
        for row in status["sources"]
        if row["observed_through"] is not None
    )
    assert len(entries) == 2
    view = ledger.as_of()
    card = load_rate_card()
    qualification._verify_selected_sources(ledger, view, entries, card)

    (approved / "claude.jsonl").rename(tmp_path / "no-longer-approved.jsonl")
    with pytest.raises(qualification.QualificationError, match="selected-source-gap"):
        qualification._verify_selected_sources(ledger, view, entries, card)
