import json
from hashlib import sha256
from uuid import UUID

import pytest
from test_grok import grok_source as grok_source

from aitm_usage import monitor_registry as registry
from aitm_usage import monitor_scope as scope
from aitm_usage._monitor_qualification import _LiveSourceTuple
from aitm_usage.monitor_types import NativeSurface
from aitm_usage.types import ItemKind, SourceRef, _decode, _encode

_REGISTRY_GOLDEN = (
    '{"epochs":[],"format":"aitm.usage.monitor-registry/v1","pending_capture":[{"arms":[{"gap'
    '_start":null,"ordinal":73,"position":{"anchor_ref":"hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaa'
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    'eeeeeeeeeeeeeeeee","incarnation_ref":"hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    "aaaaaaaaaaaaaaaaaaaaaaaaaa:ddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd"
    'ddd","locator_ref":"hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    'aaaaaaaa:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc","offset":73,"'
    'source_ref":"hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    'a:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}}],"change":{"enable'
    'd":false,"project_id":"00000000-0000-0000-0000-000000000001","source_id":"00000000-0000-'
    '0000-0000-000000000002"},"command_id":"00000000-0000-0000-0000-000000000003","digest":"2'
    '0f663f2cd2f023cce0ee51dedc8b13d25c99ebfaf17df11d5fde7c085ba7e41","progress":[]}],"permis'
    'sions":[{"enabled":true,"project_id":"00000000-0000-0000-0000-000000000001","source_id":'
    '"00000000-0000-0000-0000-000000000002"}],"projects":[{"adopted_key_id":null,"anchors":[]'
    ',"default_driver":null,"display_name":"Literal compatibility","project_id":"00000000-000'
    '0-0000-0000-000000000001","remote":null,"state":{"identity":[23,51],"path":"/synthetic/o'
    'ld-registry/project"}}],"receipts":[{"command_id":"00000000-0000-0000-0000-000000000004"'
    ',"payload_digest":"491d2e0625ed9634d7fdd47a654cd9b436dbcc0e1fd13d49972c5d73f963d789","re'
    'ason":null,"status":"applied"}],"source_key_id":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    'aaaaaaaaaaaaaaaaaaaaaaaaa","sources":[]}'
)

_SCOPE_GOLDEN = (
    '{"events":[{"affected":{"end":5,"observation_keys":["hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaa'
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:ffffffffffffffffffffffffffffffffffffffffffffff"
    'ffffffffffffffffff"],"start":4},"anchor_project":null,"before_generation":null,"checkout'
    '":null,"command_id":"00000000-0000-0000-0000-000000000005","current_project":null,"diges'
    't":"0000000000000000000000000000000000000000000000000000000000000000","eligible":true,"n'
    'ative_boundary":{"boundary_ref":"hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    'aaaaaaaaaaaaaaaaaaaaa:dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",'
    '"epoch_ref":null,"kind":"turn","ordinal":4,"provider":"codex","receipt_ref":"hmac-sha256'
    ":aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:eeeeeeeeeeeeeeeeeeeeee"
    'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee","session_ref":"hmac-sha256:aaaaaaaaaaaaaaaaa'
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:cccccccccccccccccccccccccccccccccccccccc"
    'cccccccccccccccccccccccc","stream_ref":"hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaa:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    'bbbbb"},"position":{"ordinal":4,"session_ref":"hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:cccccccccccccccccccccccccccccccccccccccccccccccccccc"
    'cccccccccccc","source_id":"00000000-0000-0000-0000-000000000002","stream_ref":"hmac-sha2'
    "56:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:bbbbbbbbbbbbbbbbbbbb"
    'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","surface":"codex-desktop-macos"},"reported'
    '":{"affected":{"end":5,"observation_keys":["hmac-sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:fffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    'fffffffff"],"start":4},"generation":1,"status":"applied"},"retained_checkout":null,"scop'
    'e":{"attempt_ref":null,"item":null,"participant_ref":null,"phase":null,"project_id":"000'
    '00000-0000-0000-0000-000000000001","review_ref":null,"role":null}}],"format":"aitm.usage'
    '.monitor-scope/v1","holds":[],"resolutions":[]}'
)


def _ref(digit):
    return SourceRef(f"hmac-sha256:{'a' * 64}:{digit * 64}")


def _identity():
    return registry._GrokCaptureIdentity(
        UUID(int=1),
        UUID(int=2),
        _LiveSourceTuple("grok", "grok-build-macos", "Darwin", "arm64", "1.0.77", 1),
        NativeSurface.GROK_BUILD_MACOS,
        _ref("b"),
        _ref("c"),
        _ref("d"),
        _ref("e"),
        _ref("f"),
        _ref("9"),
    )


def test_literal_native_registry_and_scope_bytes_are_stable():
    prior = registry._decode_registry(_REGISTRY_GOLDEN.encode())
    assert type(prior) is registry.RegistryView
    assert registry._encode_registry(prior) == _REGISTRY_GOLDEN.encode()
    assert sha256(registry._encode_registry(prior)).hexdigest() == (
        "626314e3a9b303238fa9a720e025c8e78290f8f624e11bea0325a4a2e562cbd8"
    )
    assert (
        prior.pending_capture[0].digest
        == registry.ControlCommand(
            prior.pending_capture[0].command_id, prior.pending_capture[0].change
        ).payload_digest
    )
    assert (
        prior.receipts[0].payload_digest
        == registry.ControlCommand(
            prior.receipts[0].command_id, prior.permissions[0]
        ).payload_digest
    )
    state = _decode(_SCOPE_GOLDEN, scope._ScopeSnapshot)
    assert _encode(state, scope._ScopeSnapshot) == _SCOPE_GOLDEN
    assert sha256(_SCOPE_GOLDEN.encode()).hexdigest() == (
        "7e56be80b8a9c9fbbded48c699640696422c36cee4cf27a7a8f8ec77bed5dcf7"
    )


def test_grok_epoch_round_trips_and_extended_empty_is_refused():
    identity = _identity()
    start = registry._GrokCut(12, 12, _ref("1"), _ref("2"))
    stop = registry._GrokCut(25, 43, _ref("3"), _ref("4"))
    record = registry._GrokEpoch(identity, 1, start, stop)
    view = registry._RegistryWithGrok(grok_records=(record,))
    encoded = registry._encode_registry(view)
    assert registry._decode_registry(encoded) == view
    with pytest.raises(ValueError):
        _decode(encoded, registry.RegistryView)
    empty = json.loads(registry._encode_registry(registry.RegistryView()))
    empty["grok_records"] = []
    with pytest.raises(ValueError):
        registry._decode_registry(json.dumps(empty).encode())


def test_grok_intervals_bind_entire_span_incarnation_and_live_generation():
    identity = _identity()
    start = registry._GrokCut(12, 12, _ref("1"), _ref("2"))
    stop = registry._GrokCut(25, 43, _ref("3"), _ref("4"))
    record = registry._GrokEpoch(identity, 1, start, stop)
    view = registry._RegistryWithGrok(grok_records=(record,))
    assert registry._grok_span_disposition(view, identity, 12, 25).value == "eligible"
    assert registry._grok_span_disposition(view, identity, 25, 30).value == "excluded"
    assert registry._grok_span_disposition(view, identity, 11, 13).value == "unknown"
    assert registry._grok_span_disposition(view, identity, 24, 26).value == "unknown"


def test_grok_command_without_callback_holds_only_its_edge(tmp_path):
    from dataclasses import replace

    from aitm_usage.monitor_control import ControlInbox

    private = tmp_path / "monitor"
    project, grok, codex = (UUID(int=n) for n in range(1, 4))
    project_dir = tmp_path / "project"
    project_dir.mkdir(mode=0o700)
    source_dirs = (tmp_path / "grok", tmp_path / "codex")
    for root in source_dirs:
        root.mkdir(mode=0o700)
    with registry.Registry(private).writer() as writer:
        writer.register_project(
            registry.ProjectRegistrationRequest(project, str(project_dir), "Test")
        )
        grok_approval = registry.SourceApprovalRequest(
            grok,
            "grok",
            "grok-build-macos",
            "Darwin",
            "arm64",
            "1.0.77",
            1,
            str(source_dirs[0]),
        )
        codex_approval = registry.SourceApprovalRequest(
            codex,
            "codex",
            "codex-desktop-macos",
            "Darwin",
            "arm64",
            "0.167.0-alpha.3.2",
            1,
            str(source_dirs[1]),
        )
        writer._save(
            replace(
                writer.view(),
                sources=tuple(
                    registry.ApprovedSource(
                        approval, registry._directory(approval.root)
                    )
                    for approval in (grok_approval, codex_approval)
                ),
            )
        )
        inbox = ControlInbox(private)
        grok_on, grok_off, codex_off = tuple(
            registry.ControlCommand(
                UUID(int=n), registry.CaptureChange(project, source, enabled)
            )
            for n, source, enabled in (
                (4, grok, True),
                (5, grok, False),
                (6, codex, False),
            )
        )
        for command in (grok_on, grok_off, codex_off):
            inbox.enqueue(command)
        assert [
            receipt.command_id
            for receipt in writer.apply_pending(inbox, writer.lease, None)
        ] == [codex_off.command_id]
        assert writer.command_status(grok_on.command_id) is None
        assert writer.command_status(grok_off.command_id) is None
        assert (
            writer.command_status(codex_off.command_id).status
            is registry.ControlStatus.APPLIED
        )


def _grok_reader(source, rows, verifier):
    from aitm_usage.sources.grok import GrokAdapter

    updates = source.directory / "updates.jsonl"
    updates.write_bytes(b"".join(rows))
    (source.directory / "usage.json").write_text(json.dumps(source.snapshot))
    reader = GrokAdapter(
        lambda path: source.origin if path == updates else None, verifier
    )
    (locator,) = reader.discover(source.root)
    return reader, locator


def test_strict_grok_proves_mark_and_hookless_separately_and_restarts(grok_source):
    from aitm_usage.sources import grok

    source = grok_source
    rows = [row for i, row in enumerate(source.rows) if i != 6]

    def verifier(*parts):
        return source.pending_receipts.get(parts)

    reader, locator = _grok_reader(source, rows, verifier)
    proofs = []
    batch = reader.read_delta(locator, None, _proofs=proofs, _receipt_verifier=verifier)
    marked, hookless = proofs
    assert type(marked) is grok._VerifiedGrokMark
    assert type(hookless) is grok._VerifiedGrokHookless
    assert marked.key == batch.observations[0].key
    assert hookless.key == batch.observations[1].key
    assert marked.start == 0
    assert marked.end == batch.observations[0].position.ordinal + 1
    assert hookless.start > marked.end
    assert hookless.end == batch.observations[1].position.ordinal + 1
    assert batch.cursor.checkpoint.offset == len(b"".join(rows))
    replay_proofs = []
    reloaded, new_locator = _grok_reader(source, rows, verifier)
    replay = reloaded.read_delta(
        new_locator, batch.cursor, _proofs=replay_proofs, _receipt_verifier=verifier
    )
    assert replay.cursor == batch.cursor
    assert replay.observations == () and replay_proofs == []
    observational = reloaded.read_delta(new_locator, None)
    refused = reloaded.read_delta(
        new_locator, observational.cursor, _proofs=[], _receipt_verifier=verifier
    )
    assert refused.observations == ()
    assert "source-replaced" in {row.code.value for row in refused.diagnostics}


@pytest.mark.parametrize(
    "receipt_case",
    [
        "missing",
        "invalid",
        "wrong-verifier",
        "failed",
        "no-issuer",
        "multi",
        "late",
        "mismatch",
    ],
)
def test_strict_grok_attempt_holds_at_start_and_can_retry(grok_source, receipt_case):
    from aitm_usage.sources import grok

    source = grok_source
    rows = source.rows.copy()

    def verifier(*parts):
        return source.pending_receipts.get(parts)

    selected = verifier
    if receipt_case == "missing":
        verifier = selected = lambda *parts: None
    elif receipt_case == "invalid":
        verifier = selected = lambda *parts: _ref("1")
    elif receipt_case == "wrong-verifier":

        def selected(*parts):
            return source.pending_receipts.get(parts)
    elif receipt_case == "no-issuer":
        verifier = selected = None
    else:
        hook = json.loads(rows[0])
        params = hook["params"]
        if receipt_case == "failed":
            params["update"]["runs"][0]["status"]["status"] = "failed"
        elif receipt_case == "multi":
            params["update"]["runs"].append(params["update"]["runs"][0])
        elif receipt_case == "late":
            hook["timestamp"] += 10
            params["_meta"]["agentTimestampMs"] += 10000
        else:
            params["_meta"]["eventId"] = "no-matching-native-receipt"
        rows[0] = json.dumps(hook).encode() + b"\n"
    reader, locator = _grok_reader(source, rows, verifier)
    proofs = []
    batch = reader.read_delta(locator, None, _proofs=proofs, _receipt_verifier=selected)
    (held,) = proofs
    assert type(held) is grok._GrokAttemptHeld
    assert held.start == 0
    assert batch.observations == () and batch.boundaries == ()
    assert batch.cursor.checkpoint.offset == 0

    def trusted(*parts):
        return source.pending_receipts.get(parts)

    reader, locator = _grok_reader(source, source.rows, trusted)
    corrected = reader.read_delta(
        locator, batch.cursor, _proofs=[], _receipt_verifier=trusted
    )
    assert len(corrected.observations) == 2


@pytest.fixture
def isolated_grok_capture(tmp_path, monkeypatch):
    import subprocess
    from dataclasses import replace
    from datetime import UTC, datetime, timedelta
    from types import SimpleNamespace

    from test_grok import FIXTURES, GROK_BINARY, PROMPT_A, PROMPT_B, SESSION

    from aitm_usage import _isolated_qualification as pilot
    from aitm_usage.ledger import Ledger
    from aitm_usage.monitor_control import ControlInbox
    from aitm_usage.sources.adapter import SourceRoot
    from aitm_usage.sources.grok import GrokAdapter, GrokOrigin
    from aitm_usage.sources.scan import checkout_anchor_reference

    for name in ("control", "provider", "checkout", "image", "capture"):
        (tmp_path / name).mkdir(mode=0o700)
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    monkeypatch.setattr(pilot, "_collect_host_installation", lambda *_: "a" * 64)
    expected = _LiveSourceTuple(
        "grok", "grok-build-macos", "Darwin", "arm64", "1.0.77", 1
    )
    binary = tmp_path / "candidate"
    binary.write_bytes(b"isolated Grok image for exact owner signature tests")
    digest = sha256(binary.read_bytes()).hexdigest()
    monkeypatch.setattr(
        pilot,
        "_approved_pilot_tuple",
        lambda candidate: expected if candidate == digest else None,
    )
    key = tmp_path / "control" / "owner"
    subprocess.run(
        ["/usr/bin/ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key)],
        check=True,
        capture_output=True,
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

    project, source_id = UUID(int=11), UUID(int=12)
    control = registry.Registry(tmp_path / "monitor")
    session_dir = tmp_path / "capture" / SESSION
    session_dir.mkdir(mode=0o700)
    updates, summary = (session_dir / name for name in ("updates.jsonl", "usage.json"))
    updates.touch()
    rows = (FIXTURES / "updates.jsonl").read_bytes().splitlines(keepends=True)
    accounting = json.loads((FIXTURES / "usage.json").read_text())
    cutoff = datetime(2026, 1, 1, tzinfo=UTC)
    Ledger.initialize(tmp_path / "project", project)

    with (
        control.writer() as writer,
        pilot._OpenedExecutable.copy(binary, tmp_path / "image" / "candidate") as image,
    ):
        layout = pilot._PilotLayout.create(
            tmp_path / "control",
            tmp_path / "provider",
            tmp_path / "checkout",
            tmp_path / "image",
            tmp_path / "capture",
        )
        issuer = pilot._prepare_isolated_issuer(
            writer, layout, image, None, key.with_suffix(".pub").read_bytes()
        )

        def revise(operation, generation):
            proposal = issuer.proposal(
                operation, generation, datetime.now(UTC) + timedelta(minutes=5)
            )
            if operation == "revoke":
                issuer.revoke(proposal, sign(proposal))
            else:
                pilot._install_isolated_profile(issuer, proposal, sign(proposal))

        revise("activate", 1)
        evidence = writer.source_evidence()
        writer.register_project(
            registry.ProjectRegistrationRequest(
                project,
                str(tmp_path / "project"),
                "Exact Grok project",
                anchors=(str(tmp_path / "checkout"),),
            )
        )
        writer.approve_source(
            registry.SourceApprovalRequest(
                source_id,
                "grok",
                "grok-build-macos",
                "Darwin",
                "arm64",
                "1.0.77",
                1,
                str(tmp_path / "capture"),
            )
        )
        checkout = checkout_anchor_reference(evidence, tmp_path / "checkout")
        origin = GrokOrigin(
            SESSION,
            "Darwin",
            "arm64",
            "1.0.77",
            "50ca579fa996",
            GROK_BINARY,
            1,
            SESSION,
            evidence.pseudonymize("grok-incarnation", "fixture"),
            checkout,
        )
        root = SourceRoot(
            tmp_path / "capture", cutoff, (tmp_path / "checkout",), evidence
        )
        refs = {
            (SESSION, PROMPT_A, "synthetic-event-1"): evidence.pseudonymize(
                "grok-receipt", "a"
            ),
            (SESSION, PROMPT_B, "synthetic-event-7"): evidence.pseudonymize(
                "grok-receipt", "b"
            ),
        }

        origins = {updates: origin}

        def find_origin(path):
            return origins.get(path)

        def verify_receipt(*parts):
            return refs.get(parts)

        reader = GrokAdapter(find_origin, verify_receipt)
        state = scope.ScopeState(writer, grok_reader=reader)
        inbox = ControlInbox(writer.root)

        def locator(path=updates):
            (selected,) = (
                item for item in reader.discover(root) if item._source.path == path
            )
            return selected

        def add_stream():
            sid = "10000000-0000-4000-8000-000000000331"
            path = root.path / sid / "updates.jsonl"
            path.parent.mkdir(mode=0o700)
            path.touch()
            origins[path] = replace(
                origin,
                session_id=sid,
                lineage_id=sid,
                incarnation=evidence.pseudonymize("grok-incarnation", "fixture-new"),
            )

            def write_new(selected, turns):
                path.write_bytes(
                    b"".join(selected).replace(SESSION.encode(), sid.encode())
                )
                snapshot = {
                    **accounting,
                    "sessionId": sid,
                    "turns": accounting["turns"][:turns],
                }
                path.with_name("usage.json").write_text(json.dumps(snapshot))

            return lambda: locator(path), write_new

        def capture(change, active, pending):
            return state._grok_capture_evidence(
                change, tuple(reader.discover(root)), active, pending
            )

        def evaluate():
            return writer.apply_pending(
                inbox, writer.lease, None, grok_evidence=capture
            )

        def submit(number, enabled):
            command = registry.ControlCommand(
                UUID(int=number), registry.CaptureChange(project, source_id, enabled)
            )
            inbox.enqueue(command)
            return command

        def write(selected, turns):
            updates.write_bytes(b"".join(selected))
            summary.write_text(
                json.dumps({**accounting, "turns": accounting["turns"][:turns]})
            )

        yield SimpleNamespace(
            writer=writer,
            state=state,
            reader=reader,
            project=project,
            source_id=source_id,
            locator=locator,
            evaluate=evaluate,
            submit=submit,
            rows=rows,
            write=write,
            receipt=refs[SESSION, PROMPT_A, "synthetic-event-1"],
            revise=revise,
            verifier=verify_receipt,
            root=root,
            refs=refs,
            find_origin=find_origin,
            add_stream=add_stream,
            replace_incarnation=lambda: origins.__setitem__(
                updates,
                replace(
                    origin,
                    incarnation=evidence.pseudonymize("grok-incarnation", "replaced"),
                ),
            ),
        )
    with control.writer() as reopened:
        if registry._grok_records(reopened.view()):
            with pytest.raises(scope._GrokCaptureHeld, match="authority"):
                scope.ScopeState(reopened, grok_reader=reader).read_source(
                    source_id, locator()
                )


def _routes(state, batch):
    view = state.view(batch)
    return tuple(
        scope.resolve_route(row, state.registry.view(), view)
        for row in batch.observations
    )


def test_queued_grok_enable_routes_exact_marker_and_project_only_hookless_then_reloads(
    isolated_grok_capture,
    monkeypatch,
):
    from aitm_usage.monitor_types import GrokCheckpoint
    from aitm_usage.sources.grok import GrokAdapter

    f = isolated_grok_capture
    # Both commands and marker proof go through persisted owner and writer authority.
    enable = f.submit(21, True)
    (applied,) = f.evaluate()
    assert (applied.command_id, applied.status) == (
        enable.command_id,
        registry.ControlStatus.APPLIED,
    )
    f.write([row for i, row in enumerate(f.rows) if i != 6], 2)
    batch = f.state.read_source(f.source_id, f.locator())
    assert len(batch.observations) == 2
    assert [row.status for row in _routes(f.state, batch)] == [
        scope.RouteStatus.HELD,
        scope.RouteStatus.ROUTED,
    ]
    marker = scope.Mark(
        UUID(int=22),
        scope.Scope(
            f.project,
            scope.ItemKey(ItemKind.ISSUE, 117),
            scope.WorkPhase.PLANNING,
        ),
        f.receipt,
    )
    owner = f.state.operator(f.project)
    f.state.authorize(marker, owner)
    (native,) = batch.boundaries
    verified = f.state.verify_boundary(marker, owner, batch, native)
    assert verified.eligible
    assert f.state.apply_mark(marker, verified).status is scope.HandoffStatus.APPLIED
    marked, hookless = _routes(f.state, batch)
    assert marked.status is scope.RouteStatus.ROUTED and marked.scope == marker.scope
    assert hookless.status is scope.RouteStatus.ROUTED and hookless.scope is None
    assert hookless.project_id == f.project == marked.project_id

    exact = GrokAdapter.read_delta
    seen = []

    def capture_read(reader, source, prior, **kwargs):
        seen.append(prior)
        return exact(reader, source, prior, **kwargs)

    monkeypatch.setattr(GrokAdapter, "read_delta", capture_read)
    reopened = scope.ScopeState(
        f.writer, grok_reader=GrokAdapter(f.find_origin, f.verifier)
    )
    resumed = reopened.read_source(f.source_id, f.locator(), cursor=batch.cursor)
    assert seen == [batch.cursor] and type(seen[0].checkpoint) is GrokCheckpoint
    assert resumed.cursor == batch.cursor and resumed.observations == ()
    assert reopened._snapshot().events[0].native_boundary == native.boundary

    f.revise("replace", 2)
    with pytest.raises(scope._GrokCaptureHeld, match="generation"):
        reopened.read_source(f.source_id, f.locator(), cursor=batch.cursor)
    f.revise("revoke", 3)
    with pytest.raises(scope._GrokCaptureHeld, match="authority"):
        reopened.read_source(f.source_id, f.locator())


def test_grok_open_disable_waits_then_cuts_before_next_turn(isolated_grok_capture):
    f = isolated_grok_capture
    f.submit(31, True)
    assert f.evaluate()[0].status is registry.ControlStatus.APPLIED
    f.write(f.rows[:2], 0)
    disable = f.submit(32, False)
    assert f.evaluate() == f.evaluate() == ()
    assert f.writer.command_status(disable.command_id) is None
    armed = f.writer.view()
    pending = next(
        item
        for item in registry._grok_records(armed)
        if type(item) is registry._GrokPending
    )
    assert len(pending.arms) == 1 and pending.cuts == ()
    assert f.state.read_source(f.source_id, f.locator()).observations == ()

    f.write([row for i, row in enumerate(f.rows) if i != 6], 2)
    (applied,) = f.evaluate()
    assert applied.command_id == disable.command_id
    batch = f.state.read_source(f.source_id, f.locator())
    assert len(batch.observations) == 1
    assert batch.cursor.checkpoint.offset == len(b"".join(f.rows[:5]))
    (epoch,) = registry._grok_records(f.writer.view())
    assert epoch.end.ordinal == batch.observations[0].position.ordinal + 1
    assert epoch.end.offset == batch.cursor.checkpoint.offset


def test_grok_duplicate_receipt_cannot_pass_as_a_later_completion(grok_source):
    from aitm_usage.sources import grok

    source = grok_source
    receipt = next(iter(source.pending_receipts.values()))

    def duplicate_receipt(*_):
        return receipt

    reader, locator = _grok_reader(source, source.rows, duplicate_receipt)
    notices = []
    result = reader.read_delta(
        locator, None, _proofs=notices, _receipt_verifier=duplicate_receipt
    )
    assert type(notices[0]) is grok._VerifiedGrokMark
    assert type(notices[1]) is grok._GrokAttemptHeld
    assert len(result.observations) == 1
    assert result.cursor.checkpoint.offset == len(b"".join(source.rows[:6]))

    reader, locator = _grok_reader(
        source, [*source.rows[:5], *source.rows[:5]], duplicate_receipt
    )
    notices = []
    retried = reader.read_delta(
        locator, None, _proofs=notices, _receipt_verifier=duplicate_receipt
    )
    assert type(notices[-1]) is grok._GrokAttemptHeld
    assert retried.cursor.checkpoint.offset == len(b"".join(source.rows[:5]))


def test_grok_quiet_enable_skips_preexisting_unverified_marker(isolated_grok_capture):
    f = isolated_grok_capture
    f.refs.clear()
    f.write(f.rows[:5], 1)
    unarmed = f.state.read_source(f.source_id, f.locator())
    assert unarmed.observations
    assert _routes(f.state, unarmed)[0].status is scope.RouteStatus.HELD
    enable = f.submit(41, True)
    assert f.evaluate()[0].command_id == enable.command_id
    f.write([row for i, row in enumerate(f.rows) if i != 6], 2)
    batch = f.state.read_source(f.source_id, f.locator())
    assert [decision.scope for decision in _routes(f.state, batch)] == [None]
    assert _routes(f.state, batch)[0].status is scope.RouteStatus.ROUTED
    assert batch.cursor.checkpoint.completions[0].observation is None


def test_grok_open_enable_excludes_open_turn_at_cut(isolated_grok_capture):
    f = isolated_grok_capture
    f.write(f.rows[:2], 0)
    enable = f.submit(51, True)
    assert f.evaluate() == ()
    f.write([row for i, row in enumerate(f.rows) if i != 6], 2)
    assert f.evaluate()[0].command_id == enable.command_id
    batch = f.state.read_source(f.source_id, f.locator())
    assert len(batch.observations) == 1
    assert _routes(f.state, batch)[0].project_id == f.project
    assert batch.cursor.checkpoint.completions[0].observation is None


@pytest.mark.parametrize("failure", ["receipt", "cancelled", "malformed"])
def test_grok_bad_open_terminal_closes_disable_at_verified_start(
    isolated_grok_capture, failure
):
    f = isolated_grok_capture
    f.submit(61, True)
    assert f.evaluate()
    f.write(f.rows[:2], 0)
    disable = f.submit(62, False)
    assert f.evaluate() == ()
    rows = f.rows.copy()
    if failure == "receipt":
        f.refs.clear()
    else:
        entry = json.loads(rows[4])
        native = entry["params"]["update"]
        if failure == "cancelled":
            native["stop_reason"] = "cancelled"
        else:
            native["usage"] = None
        rows[4] = json.dumps(entry).encode() + b"\n"
    f.write(rows, 2)
    assert f.evaluate()[0].command_id == disable.command_id
    batch = f.state.read_source(f.source_id, f.locator())
    assert batch.observations == ()
    assert batch.cursor.checkpoint.offset == 0


def test_new_grok_stream_does_not_inherit_present_stream_cut(isolated_grok_capture):
    f = isolated_grok_capture
    f.submit(71, True)
    assert f.evaluate()
    new_locator, write_new = f.add_stream()
    write_new(f.rows[1:5], 1)
    batch = f.state.read_source(f.source_id, new_locator())
    assert batch.observations
    assert _routes(f.state, batch)[0].status is scope.RouteStatus.HELD
    assert not batch._grok_strict


def test_grok_quiet_cut_is_frozen_while_other_stream_finishes(isolated_grok_capture):
    f = isolated_grok_capture
    new_locator, write_new = f.add_stream()
    f.submit(81, True)
    assert f.evaluate()
    write_new(f.rows[1:2], 0)
    disable = f.submit(82, False)
    assert f.evaluate() == ()
    pending = next(
        entry
        for entry in registry._grok_records(f.writer.view())
        if type(entry) is registry._GrokPending
    )
    assert len(pending.cuts) == len(pending.arms) == 1
    assert pending.cuts[0].cut.offset == 0
    f.write(f.rows[1:5], 1)
    write_new(f.rows[1:5], 1)
    assert f.evaluate()[0].command_id == disable.command_id
    quiet = f.state.read_source(f.source_id, f.locator())
    in_flight = f.state.read_source(f.source_id, new_locator())
    assert quiet.observations == () and quiet.cursor.checkpoint.offset == 0
    assert len(in_flight.observations) == 1
    assert _routes(f.state, in_flight)[0].status is scope.RouteStatus.ROUTED


def test_verified_grok_cut_refuses_a_rewritten_original_prefix(isolated_grok_capture):
    from aitm_usage.ledger import LedgerError

    f = isolated_grok_capture
    f.write(f.rows[:5], 1)
    f.submit(91, True)
    assert f.evaluate()
    prefix = f.rows[:5]
    prefix[2] = b" " + prefix[2]
    f.write(prefix, 1)
    with pytest.raises(LedgerError, match="proof is unavailable"):
        f.state.read_source(f.source_id, f.locator())


def test_unsupported_grok_surface_refuses_before_native_read(
    isolated_grok_capture, monkeypatch
):
    from dataclasses import replace

    from aitm_usage.sources.grok import GrokAdapter
    from aitm_usage.types import DiagnosticCode

    f = isolated_grok_capture
    view = f.writer.view()
    (original,) = view.sources
    linux = replace(original.approval, surface="grok-build-linux", platform="Linux")
    f.writer._save(replace(view, sources=(replace(original, approval=linux),)))
    monkeypatch.setattr(
        GrokAdapter, "read_delta", lambda *_: pytest.fail("unsupported payload read")
    )
    with pytest.raises(scope._GrokCaptureHeld) as refused:
        f.state.read_source(f.source_id, f.locator())
    assert refused.value.code is DiagnosticCode.UNSUPPORTED_FORMAT


def test_original_journal_remains_read_only_on_grok_prepare(isolated_grok_capture):
    from aitm_usage.ledger import LedgerError
    from aitm_usage.monitor_journal import RoutingJournal

    f = isolated_grok_capture
    f.write(f.rows, 2)
    batch = f.state.read_source(f.source_id, f.locator())
    assert len(batch.observations) == 2
    journal = RoutingJournal(f.writer, f.state)
    before = journal.as_of()
    with pytest.raises(LedgerError, match="no verified native session"):
        journal.prepare(f.source_id, f.locator())
    assert journal.as_of() == before


def test_prior_grok_offer_cannot_be_reused_by_another_command(
    isolated_grok_capture, monkeypatch
):
    f = isolated_grok_capture
    original = f.state._grok_capture_evidence
    saved = []

    def observe(*args):
        offers = original(*args)
        saved.extend(offers)
        return offers

    with monkeypatch.context() as patch:
        patch.setattr(f.state, "_grok_capture_evidence", observe)
        f.submit(101, True)
        assert f.evaluate()
    assert len(saved) == 1
    disable = f.submit(102, False)
    with monkeypatch.context() as patch:
        patch.setattr(f.state, "_grok_capture_evidence", lambda *_: tuple(saved))
        assert f.evaluate() == ()
        assert f.writer.command_status(disable.command_id) is None
    assert f.evaluate()[0].command_id == disable.command_id


def test_grok_pending_mixed_stream_reads_each_verified_bound(isolated_grok_capture):
    f = isolated_grok_capture
    new_locator, write_new = f.add_stream()
    f.submit(111, True)
    assert f.evaluate()
    f.write(f.rows[1:5], 1)
    write_new(f.rows[1:2], 0)
    f.submit(112, False)
    assert f.evaluate() == ()
    f.write([*f.rows[1:6], *f.rows[7:]], 2)
    quiet = f.state.read_source(f.source_id, f.locator())
    armed = f.state.read_source(f.source_id, new_locator())
    assert len(quiet.observations) == 1
    assert _routes(f.state, quiet)[0].project_id == f.project
    assert quiet.cursor.checkpoint.offset == len(b"".join(f.rows[1:5]))
    assert armed.observations == () and armed.cursor.checkpoint.offset == 0


def test_grok_replaced_incarnation_has_no_previous_capture_authority(
    isolated_grok_capture,
):
    f = isolated_grok_capture
    f.submit(121, True)
    assert f.evaluate()
    f.write(f.rows[1:5], 1)
    older = f.state.read_source(f.source_id, f.locator())
    assert older.observations
    f.replace_incarnation()
    with pytest.raises(scope._GrokCaptureHeld, match="incarnation"):
        f.state.read_source(f.source_id, f.locator(), cursor=older.cursor)


def test_another_scope_reader_cannot_change_current_grok_receipt_verifier(
    isolated_grok_capture,
):
    from aitm_usage.sources.grok import GrokAdapter
    from aitm_usage.types import DiagnosticCode

    f = isolated_grok_capture
    f.submit(131, True)
    assert f.evaluate()
    f.write(f.rows[:5], 1)

    def different_verifier(*parts):
        return f.verifier(*parts)

    alternate = scope.ScopeState(
        f.writer, grok_reader=GrokAdapter(f.find_origin, different_verifier)
    )
    held = alternate.read_source(f.source_id, f.locator())
    assert held.observations == () and held.cursor.checkpoint.offset == 0
    assert DiagnosticCode.BOUNDARY_UNVERIFIED in {
        entry.code for entry in held.diagnostics
    }
    assert f.state.read_source(f.source_id, f.locator()).observations
