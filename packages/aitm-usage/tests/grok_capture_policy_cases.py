"""Supply controlled storage and installation inputs to Grok capture policy."""

import json
from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import UUID

import pytest
from monitor_inbox_cases import MonitorInboxFiles
from test_grok import FIXTURES, GROK_BINARY, PROMPT_A, PROMPT_B, SESSION

from aitm_usage import monitor_registry as registry
from aitm_usage import monitor_scope as scope
from aitm_usage._monitor_qualification import _InstallationProof, _LiveProfile
from aitm_usage.sources import grok
from aitm_usage.sources.scan import checkout_anchor_reference

_UPDATES = tuple((FIXTURES / "updates.jsonl").read_bytes().splitlines(keepends=True))
_ACCOUNTING = (FIXTURES / "usage.json").read_bytes()


@pytest.fixture
def grok_capture_policy(monkeypatch):
    project, source_id = UUID(int=11), UUID(int=12)
    evidence = registry._ServiceEvidence(b"g" * 32)
    control, state_dir, checkout, capture = (
        registry._PhysicalDirectory(f"/fixture/{name}", (1, index))
        for index, name in enumerate(("monitor", "project", "checkout", "capture"), 1)
    )
    directories = {item.path: item for item in (control, state_dir, checkout, capture)}
    monkeypatch.setattr(registry, "_directory", lambda path, **_: directories[path])

    lease = Mock()
    writer = registry.Registry(Path(control.path), lease)
    approved = registry.ApprovedSource(
        registry.SourceApprovalRequest(
            source_id,
            "grok",
            "grok-build-macos",
            "Darwin",
            "arm64",
            "1.0.77",
            1,
            capture.path,
        ),
        capture,
    )
    initial = registry.RegistryView(
        projects=(
            registry.RegisteredProject(
                project, state_dir, "Exact Grok project", None, (checkout,), None
            ),
        ),
        sources=(approved,),
        source_key_id=evidence.key_id,
    )
    writer._live_profile = _LiveProfile(
        control,
        lease,
        evidence.pseudonymize("generation", "fixture"),
        (
            _InstallationProof(
                capture,
                registry._LiveSourceTuple.from_approval(approved),
                evidence.pseudonymize("executable", "fixture"),
            ),
        ),
        lambda _: True,
    )
    monkeypatch.setattr(writer, "source_evidence", lambda: evidence)
    files = MonitorInboxFiles(monkeypatch, project, writer=writer, initial_view=initial)

    origin = grok.GrokOrigin(
        SESSION,
        "Darwin",
        "arm64",
        "1.0.77",
        "50ca579fa996",
        GROK_BINARY,
        1,
        SESSION,
        evidence.pseudonymize("grok-incarnation", "fixture"),
        checkout_anchor_reference(evidence, Path(checkout.path)),
    )
    root = grok.SourceRoot(
        Path(capture.path),
        datetime(2026, 1, 1, tzinfo=UTC),
        (Path(checkout.path),),
        evidence,
    )
    updates = root.path / SESSION / "updates.jsonl"
    contents = {}
    origins = {}
    identities = {}
    accounting = json.loads(_ACCOUNTING)
    refs = {
        (SESSION, PROMPT_A, "synthetic-event-1"): evidence.pseudonymize(
            "grok-receipt", "a"
        ),
        (SESSION, PROMPT_B, "synthetic-event-7"): evidence.pseudonymize(
            "grok-receipt", "b"
        ),
    }

    def install(path, source_origin):
        origins[path] = source_origin
        contents[path] = b""
        session_identity = (
            (1, 0, 1),
            (1, 1, 1),
            (*capture.identity, 1),
            (1, len(origins) + 10, 1),
        )
        identities[path] = (*session_identity, (1, 30, 1))
        identities[path.with_name("usage.json")] = (*session_identity, (1, 31, 1))

    install(updates, origin)

    def directory(path):
        assert path == root.path
        return nullcontext((object(), identities[updates][: len(path.parts)], None))

    def open_snapshot(path, *, identity_prefix):
        assert identities[path][: len(identity_prefix)] == identity_prefix
        if path not in contents:
            raise FileNotFoundError(path)
        data = contents[path]
        return nullcontext((BytesIO(data), snapshot(path)))

    def snapshot(path):
        return SimpleNamespace(
            identity=identities[path], stat=SimpleNamespace(st_size=len(contents[path]))
        )

    def verify_snapshot(_stream, path, observed, size, digest):
        assert snapshot(path) == observed
        assert sha256(contents[path][:size]).hexdigest() == digest

    monkeypatch.setattr(grok, "_directory", directory)
    monkeypatch.setattr(
        grok, "_transcripts", lambda _, path: iter(origins) if path == root.path else ()
    )
    monkeypatch.setattr(grok, "_probe", snapshot)
    monkeypatch.setattr(grok, "_open_snapshot", open_snapshot)
    monkeypatch.setattr(grok, "_verify_snapshot", verify_snapshot)

    def verify_receipt(*parts):
        return refs.get(parts)

    find_origin = origins.get
    reader = grok.GrokAdapter(find_origin, verify_receipt)
    scopes = scope.ScopeState(writer, grok_reader=reader)
    inbox = files.inbox

    def locator(path=updates):
        (selected,) = (
            item for item in reader.discover(root) if item._source.path == path
        )
        return selected

    def write(selected, turns, path=updates):
        sid = origins[path].session_id
        contents[path] = b"".join(selected).replace(SESSION.encode(), sid.encode())
        contents[path.with_name("usage.json")] = json.dumps(
            {**accounting, "sessionId": sid, "turns": accounting["turns"][:turns]}
        ).encode()

    def add_stream():
        sid = "10000000-0000-4000-8000-000000000331"
        path = root.path / sid / "updates.jsonl"
        install(
            path,
            replace(
                origin,
                session_id=sid,
                lineage_id=sid,
                incarnation=evidence.pseudonymize("grok-incarnation", "fixture-new"),
            ),
        )
        return lambda: locator(path), lambda selected, turns: write(
            selected, turns, path
        )

    def capture_evidence(change, active, pending):
        return scopes._grok_capture_evidence(
            change, tuple(reader.discover(root)), active, pending
        )

    def evaluate():
        return writer.apply_pending(
            inbox, writer.lease, None, grok_evidence=capture_evidence
        )

    def submit(number, enabled):
        command = registry.ControlCommand(
            UUID(int=number), registry.CaptureChange(project, source_id, enabled)
        )
        inbox.enqueue(command)
        return command

    return SimpleNamespace(
        writer=writer,
        state=scopes,
        reader=reader,
        project=project,
        source_id=source_id,
        locator=locator,
        evaluate=evaluate,
        submit=submit,
        rows=list(_UPDATES),
        write=write,
        verifier=verify_receipt,
        root=root,
        refs=refs,
        find_origin=find_origin,
        add_stream=add_stream,
    )
