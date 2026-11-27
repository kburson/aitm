from contextlib import nullcontext
from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from io import BytesIO
from types import SimpleNamespace
from uuid import UUID

import pytest
from test_effort_trail import effort_snapshot, ref
from test_ledger import _QueryRows

from aitm_usage.effort.receipts import (
    NativeTurn,
    Outcome,
    Role,
    UsageReceipt,
    UsageScope,
)
from aitm_usage.effort.store import Disposition, EffortError
from aitm_usage.types import Availability, TokenCounts

PROJECT = UUID(int=1)
SESSION = UUID(int=2)
OWNER = UUID(int=3)
CHILD = UUID(int=4)
STAMP = datetime(2026, 11, 25, tzinfo=UTC)
REMOTE = "https://example.invalid/owner/project.git"


@pytest.fixture
def session_api():
    from aitm_usage.effort import session

    return session


def layout(session_api, path):
    store = session_api.SessionStore(path, PROJECT)
    store.select(SESSION, 457, REMOTE, epic=456)
    launch = store.reference("launch", "private-canary")
    turn = NativeTurn(
        "codex",
        "0.171.0-alpha.13.2",
        "desktop",
        *(store.reference("test", item) for item in ("account", "session", "turn")),
    )
    store.expect(SESSION, OWNER, Role.ORCHESTRATOR, launch)
    store.expect(SESSION, CHILD, Role.WORKER, launch, parent=OWNER)
    return store, launch, turn


def test_switch_restart_and_replay_keep_the_dispatch_story(session_api, tmp_path):
    database = tmp_path / "effort.db"
    store, launch, turn = layout(session_api, database)
    store.select(SESSION, 458, REMOTE, epic=456)
    reopened = session_api.SessionStore(database, PROJECT)
    with pytest.raises(EffortError, match="project"):
        session_api.SessionStore(database, UUID(int=99))
    with pytest.raises(EffortError, match="session"):
        reopened.bind(UUID(int=99), OWNER, launch, turn)
    assert (
        reopened.expect(
            SESSION, CHILD, Role.WORKER, launch, parent=OWNER
        ).enrollment.story
        == 457
    )
    with pytest.raises(EffortError, match="launch"):
        reopened.bind(SESSION, CHILD, reopened.reference("launch", "wrong"), turn)
    reopened.bind(SESSION, CHILD, launch, turn)
    with pytest.raises(EffortError, match="binding"):
        reopened.bind(SESSION, CHILD, launch, replace(turn, turn=launch))
    assert reopened.status(SESSION)[CHILD] == "pending-evidence"
    assert (
        reopened.expect(SESSION, UUID(int=5), Role.REVIEWER, launch).enrollment.story
        == 458
    )
    with pytest.raises(EffortError, match="remote"):
        reopened.select(SESSION, 458, "https://example.invalid/other.git")

    unknown_usage = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "b" * 64,
        STAMP,
        1,
        Availability.UNKNOWN,
        Outcome.INTERRUPTED,
        TokenCounts(),
        scope=UsageScope.BOUNDED,
    )
    assert reopened.accept(SESSION, unknown_usage) is Disposition.INSERTED
    assert reopened.status(SESSION)[CHILD] == "unavailable"
    (payload,) = reopened.public_receipts(SESSION)
    data = session_api.validate_public_receipt(payload)
    assert data["model"] is None and data["rate_inputs"] is None


def test_revision_publication_whitelists_and_waits_for_predecessor(
    session_api, tmp_path
):
    store, launch, turn = layout(session_api, tmp_path / "effort.db")
    store.bind(SESSION, CHILD, launch, turn)
    first = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "a" * 64,
        STAMP,
        1,
        Availability.PARTIAL,
        Outcome.COMPLETED,
        TokenCounts(input_tokens=12),
        scope=UsageScope.BOUNDED,
    )
    second = replace(
        first,
        revision=2,
        previous_digest=first.digest,
        coverage=Availability.COMPLETE,
        tokens=TokenCounts(input_tokens=12, output_tokens=3),
    )
    assert store.accept(SESSION, second) is Disposition.PENDING
    assert store.public_receipts(SESSION) == ()
    assert store.accept(SESSION, first) is Disposition.REFINED
    public = store.public_receipts(SESSION)
    assert len(public) == 2
    rows = [session_api.validate_public_receipt(payload) for payload in public]
    assert [row["revision"] for row in rows] == [1, 2]
    assert rows[1]["story"] == 457 and rows[1]["tokens"]["output_tokens"] == 3
    assert rows[0]["identity"] == rows[1]["identity"]
    assert all(
        turn.account.value.encode() not in payload and CHILD.hex.encode() not in payload
        for payload in public
    )
    with pytest.raises(EffortError, match="exact"):
        store.accept(SESSION, replace(first, turn=replace(turn, turn=launch)))
    assert store.status(SESSION)[CHILD] == "observed"
    assert store.status(SESSION)[OWNER] == "pending-binding"


def test_store_refuses_cross_project_and_hides_unknown_usage(
    session_api, public_revisions, monkeypatch
):
    from aitm_usage.effort import Enrollment

    store = session_api.SessionStore.__new__(session_api.SessionStore)
    store.project_id = PROJECT
    turn = NativeTurn(
        "codex",
        "0.171.0-alpha.13.2",
        "desktop",
        ref("account"),
        ref("session"),
        ref("turn"),
    )
    receipt = UsageReceipt(
        PROJECT,
        OWNER,
        turn,
        "b" * 64,
        STAMP,
        1,
        Availability.UNKNOWN,
        Outcome.INTERRUPTED,
        TokenCounts(),
        scope=UsageScope.BOUNDED,
    )
    enrollment = Enrollment(PROJECT, SESSION, OWNER, Role.ORCHESTRATOR, 457)

    def mismatched_project(query):
        if query == "PRAGMA application_id":
            from aitm_usage.effort.store import _APPLICATION_ID

            return _QueryRows([(_APPLICATION_ID,)])
        assert query == "SELECT project, schema_version, generation FROM metadata"
        return _QueryRows([(str(UUID(int=99)), 1, 0)])

    with pytest.raises(EffortError, match="project"):
        store._generation(SimpleNamespace(execute=mismatched_project))

    def read_session(query, arguments):
        if query.startswith("SELECT launch, native"):
            assert arguments == (str(UUID(int=99)), str(enrollment.attempt_id))
            return _QueryRows([])
        assert "FROM session_expectations s" in query and arguments == (str(SESSION),)
        return [(str(OWNER), turn, receipt.to_json())]

    monkeypatch.setattr(
        store,
        "_transaction",
        lambda **_: nullcontext(SimpleNamespace(execute=read_session)),
    )
    with pytest.raises(EffortError, match="session"):
        store.bind(UUID(int=99), OWNER, ref("launch"), turn)
    assert store.status(SESSION)[OWNER] == "unavailable"
    (payload,) = public_revisions([(receipt, receipt)])
    data = session_api.validate_public_receipt(payload)
    assert data["model"] is None and data["rate_inputs"] is None
    with pytest.raises(ValueError):
        session_api.validate_public_receipt(
            payload[:-1] + b',"private_path":"/tmp/canary"}'
        )


def test_session_cli_registers_expectation_before_provider(monkeypatch, capsys):
    import json
    from pathlib import Path
    from unittest.mock import Mock, call

    from aitm_usage.effort.cli import main

    database = Path("/fixture/effort.db")
    store = Mock()
    launch = object()
    store.reference.return_value = launch
    store.status.return_value = {OWNER: "pending-binding"}

    def open_store(path, project):
        assert (path, project) == (database, PROJECT)
        return store

    monkeypatch.setattr("aitm_usage.effort.session_cli.SessionStore", open_store)
    args = ["--database", str(database), "--project", str(PROJECT)]
    assert main(args + ["session-select", str(SESSION), "457", REMOTE]) == 0
    assert (
        main(
            args
            + ["session-expect", str(SESSION), str(OWNER), "orchestrator", "launch"]
        )
        == 0
    )
    assert main(args + ["session-status", str(SESSION)]) == 0
    assert json.loads(capsys.readouterr().out) == {str(OWNER): "pending-binding"}
    assert store.method_calls[:2] == [
        call.select(SESSION, 457, REMOTE, epic=None),
        call.reference("launch", "launch"),
    ]
    assert [entry[0] for entry in store.method_calls] == [
        "select",
        "reference",
        "expect",
        "status",
    ]


@pytest.fixture
def supervised_dispatch(session_api, monkeypatch):
    from aitm_usage.effort import Enrollment
    from aitm_usage.effort.capture import (
        CaptureResult,
        DescendantState,
        ProcessState,
        ProcessStatus,
    )
    from aitm_usage.types import _decode

    store = session_api.SessionStore.__new__(session_api.SessionStore)
    store.project_id = PROJECT
    launch = ref("launch")
    turn = NativeTurn(
        "codex",
        "0.171.0-alpha.13.2",
        "desktop",
        ref("account"),
        ref("session"),
        ref("turn"),
    )
    enrollment = Enrollment(PROJECT, SESSION, CHILD, Role.WORKER, 457)
    bound = None
    dispatched = False
    observed = None

    def execute(query, arguments):
        nonlocal bound, dispatched
        if query.startswith("SELECT 1 FROM session_dispatches"):
            assert arguments == (str(CHILD),)
            return _QueryRows([(1,)] if dispatched else [])
        if query.startswith("INSERT INTO session_dispatches"):
            assert arguments == (str(CHILD),) and not dispatched
            dispatched = True
            return None
        if query.startswith("SELECT 1 FROM session_expectations"):
            assert arguments == (turn.identity,)
            return _QueryRows([])
        if query.startswith("UPDATE session_expectations"):
            raw, identity, attempt = arguments
            assert (identity, attempt) == (turn.identity, str(CHILD))
            bound = _decode(raw, NativeTurn)
            return None
        assert "FROM session_expectations s" in query and arguments == (str(SESSION),)
        payload = None if observed is None else observed.to_json()
        return [(str(CHILD), bound, payload)]

    def expected(db, session, attempt):
        assert (session, attempt) == (SESSION, CHILD)
        return session_api.Expectation(enrollment, launch, bound)

    def ingest(db, receipt):
        nonlocal observed
        assert receipt.turn == bound == turn and dispatched
        observed = receipt
        return Disposition.INSERTED

    async def capture(adapter, *, enrollment, command, limits):
        assert dispatched and bound == turn and enrollment.attempt_id == CHILD
        status = ProcessStatus(ProcessState.EXITED, 0, DescendantState.UNKNOWN)
        return CaptureResult(
            status, adapter.observe(SimpleNamespace(stdout=b"finished\n"))
        )

    monkeypatch.setattr(
        store, "_transaction", lambda **_: nullcontext(SimpleNamespace(execute=execute))
    )
    monkeypatch.setattr(store, "_expected", expected)
    monkeypatch.setattr(store, "_ingest", ingest)
    monkeypatch.setattr(session_api, "capture", capture)
    return store, launch, turn


@pytest.mark.parametrize("prebind", [False, True])
def test_supervised_launch_settles_automatically_and_will_not_repeat(
    session_api, request, prebind
):
    import asyncio
    import sys
    from pathlib import Path

    from aitm_usage.effort.capture import HarnessCommand, Observation

    if prebind:
        store, launch, turn = request.getfixturevalue("supervised_dispatch")
    else:
        tmp_path = request.getfixturevalue("tmp_path")
        store, launch, turn = layout(session_api, tmp_path / "effort.db")

    class Observes:
        def observe(self, event):
            assert event.stdout.splitlines() == [b"finished"]
            assert store.status(SESSION)[CHILD] == (
                "pending-evidence" if prebind else "pending-binding"
            )
            return Observation(
                Outcome.COMPLETED,
                UsageReceipt(
                    PROJECT,
                    CHILD,
                    turn,
                    "e" * 64,
                    STAMP,
                    1,
                    Availability.COMPLETE,
                    Outcome.COMPLETED,
                    TokenCounts(total_tokens=12),
                    scope=UsageScope.BOUNDED,
                ),
            )

    command = HarnessCommand((sys.executable, "-c", "print('finished')"), Path.cwd())
    assert asyncio.run(
        store.run_owned(
            SESSION,
            CHILD,
            launch,
            Observes(),
            command,
            expected_turn=turn if prebind else None,
        )
    ).observation.receipt
    assert store.status(SESSION)[CHILD] == "observed"
    with pytest.raises(EffortError, match="already dispatched"):
        asyncio.run(store.run_owned(SESSION, CHILD, launch, Observes(), command))


@pytest.fixture
def public_revisions(session_api, monkeypatch):
    from aitm_usage.effort import Enrollment
    from aitm_usage.types import _encode

    store = session_api.SessionStore.__new__(session_api.SessionStore)
    store.project_id = PROJECT
    store._pseudonym = lambda domain, value: sha256(
        f"{domain}:{value}".encode()
    ).hexdigest()

    def publication(rows, markers=()):
        marker_rows = [
            (row.turn.identity, row.kind, _encode(row, type(row))) for row in markers
        ]
        revision_rows = [
            (
                native.to_json(),
                _encode(
                    Enrollment(PROJECT, SESSION, native.attempt_id, Role.WORKER, 457),
                    Enrollment,
                ),
                None,
                effective.to_json(),
            )
            for native, effective in rows
        ]

        def execute(query, params=()):
            if "FROM scope_markers" in query:
                assert not params
                return marker_rows
            assert "FROM revisions" in query and params == (str(SESSION),)
            return revision_rows

        monkeypatch.setattr(
            store, "_transaction", lambda: nullcontext(SimpleNamespace(execute=execute))
        )
        return store.public_receipts(SESSION)

    return publication


def test_unknown_scope_and_open_markers_withhold_publication(
    session_api, public_revisions
):

    from aitm_usage.effort.assignments import MarkerKind, ScopeMarker

    turn = NativeTurn(
        "codex",
        "0.171.0-alpha.13.2",
        "desktop",
        ref("account"),
        ref("session"),
        ref("turn"),
    )
    unknown = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "e" * 64,
        STAMP,
        1,
        Availability.PARTIAL,
        Outcome.COMPLETED,
        TokenCounts(input_tokens=12),
    )
    assert public_revisions([(unknown, unknown)]) == ()
    owner_turn = replace(turn, turn=ref("owner"))
    start = ScopeMarker(
        PROJECT,
        OWNER,
        owner_turn,
        MarkerKind.START,
        ref("clock"),
        STAMP,
        turn.account,
    )
    bounded = replace(
        unknown, attempt_id=OWNER, turn=owner_turn, scope=UsageScope.BOUNDED
    )
    rows = [(unknown, unknown), (bounded, bounded)]
    assert public_revisions(rows, [start]) == ()
    (payload,) = public_revisions(rows, [start, replace(start, kind=MarkerKind.END)])
    for value in ("desktop", "0.171.0-alpha.13.2"):
        with pytest.raises(ValueError):
            session_api.validate_public_receipt(
                payload.replace(value.encode(), b"CANARY_PRIVATE_VALUE")
            )


def test_frozen_batch_survives_story_and_revision_changes():
    from test_effort_session_publication import PROJECT as publication_project
    from test_effort_session_publication import receipt

    from aitm_usage.effort.session_cli import _batch, _read_batch

    first = receipt()
    rows = (first.data,)

    def public_receipts(session):
        assert session == SESSION
        return rows

    store = SimpleNamespace(
        project_id=publication_project, public_receipts=public_receipts
    )
    frozen = _batch(store, SESSION, 457)
    rows += (
        receipt(revision=2, previous=sha256(first.data).hexdigest()).data,
        receipt("b" * 64, story=458).data,
    )
    assert _batch(store, SESSION, 457) != frozen
    handoff = SimpleNamespace(open=lambda mode: BytesIO(frozen))
    other_writer = SimpleNamespace(project_id=publication_project)
    (entry,) = _read_batch(handoff, other_writer, 457)
    assert entry.revision == 1
    assert entry.data == rows[0]
    with pytest.raises(EffortError, match="batch"):
        _read_batch(handoff, other_writer, 458)


def test_review_companion_keeps_sealed_decision_independent(session_api, monkeypatch):

    from aitm_usage.effort.receipts import Enrollment, ReviewBinding
    from aitm_usage.effort.review_receipts import (
        ReviewAttempt,
        ReviewIdentity,
        SealedDecision,
        Verdict,
    )

    store = session_api.SessionStore.__new__(session_api.SessionStore)
    attempt_id = UUID(int=7)
    turn = NativeTurn(
        "codex",
        "0.171.0-alpha.13.2",
        "desktop",
        ref("account"),
        ref("session"),
        ref("turn"),
    )
    enrollment = Enrollment(
        PROJECT,
        SESSION,
        attempt_id,
        Role.REVIEWER,
        457,
        review=ReviewBinding(turn.account, 1),
    )
    expected = SimpleNamespace(enrollment=enrollment, native=turn)

    def expectation(session, attempt):
        assert (session, attempt) == (SESSION, attempt_id)
        return expected

    monkeypatch.setattr(store, "expected", expectation)
    snapshot = effort_snapshot(pending_enrollments=(enrollment,))
    monkeypatch.setattr(store, "snapshot", lambda: snapshot)
    identity = ReviewIdentity(enrollment, turn.session, "a" * 64)
    attempt = ReviewAttempt(identity, turn.identity)
    decision = SealedDecision(identity, Verdict.ACCEPTED, "b" * 64, turn.turn)
    assert store.review_companion(SESSION, attempt, decision).usage is None
    usage = UsageReceipt(
        PROJECT,
        attempt_id,
        turn,
        "c" * 64,
        STAMP,
        1,
        Availability.COMPLETE,
        Outcome.COMPLETED,
        TokenCounts(total_tokens=12),
        scope=UsageScope.BOUNDED,
    )
    snapshot = effort_snapshot((enrollment, usage))
    result = store.review_companion(SESSION, attempt, decision)
    assert result.decision == decision and result.usage == usage
    with pytest.raises(EffortError, match="exact session"):
        store.review_companion(SESSION, replace(attempt, observation_id="e" * 64), None)


def test_late_scope_proof_redacts_historical_usage_without_losing_lineage(
    session_api, public_revisions
):
    from datetime import timedelta

    from aitm_usage.effort.assignments import MarkerKind, ScopeMarker
    from aitm_usage.effort.receipts import TimeBasis

    turn = NativeTurn(
        "codex",
        "0.171.0-alpha.13.2",
        "desktop",
        ref("account"),
        ref("session"),
        ref("turn"),
    )
    marker = ScopeMarker(
        PROJECT,
        CHILD,
        turn,
        MarkerKind.START,
        ref("clock"),
        STAMP,
        turn.account,
    )
    markers = [
        marker,
        replace(marker, kind=MarkerKind.END, at=STAMP + timedelta(seconds=2)),
    ]
    first = UsageReceipt(
        PROJECT,
        CHILD,
        turn,
        "e" * 64,
        STAMP,
        1,
        Availability.PARTIAL,
        Outcome.COMPLETED,
        TokenCounts(input_tokens=12),
        started_at=STAMP - timedelta(seconds=1),
        ended_at=STAMP,
        time_basis=TimeBasis.NATIVE,
    )
    future = replace(
        first,
        revision=2,
        previous_digest=first.digest,
        scope=UsageScope.BOUNDED,
        started_at=STAMP,
    )
    assert public_revisions([], markers) == ()
    redacted, final = public_revisions([(first, future), (future, future)], markers)
    assert all(
        value is None
        for value in session_api.validate_public_receipt(redacted)["tokens"].values()
    )
    row = session_api.validate_public_receipt(final)
    assert row["tokens"]["input_tokens"] == 12
    assert row["previous_receipt_sha256"] == sha256(redacted).hexdigest()
