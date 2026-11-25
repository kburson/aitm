from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

import pytest

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
        "1.0",
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


def test_store_refuses_cross_project_and_hides_unknown_usage(session_api, tmp_path):
    database = tmp_path / "effort.db"
    store, launch, turn = layout(session_api, database)
    with pytest.raises(EffortError, match="project"):
        session_api.SessionStore(database, UUID(int=99))
    with pytest.raises(EffortError, match="session"):
        store.bind(UUID(int=99), OWNER, launch, turn)
    store.bind(SESSION, OWNER, launch, turn)
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
    store.accept(SESSION, receipt)
    assert store.status(SESSION)[OWNER] == "unavailable"
    (payload,) = store.public_receipts(SESSION)
    data = session_api.validate_public_receipt(payload)
    assert data["model"] is None and data["rate_inputs"] is None
    with pytest.raises(ValueError):
        session_api.validate_public_receipt(
            payload[:-1] + b',"private_path":"/tmp/canary"}'
        )


def test_session_cli_registers_expectation_before_provider(
    session_api, tmp_path, capsys
):
    import json

    from aitm_usage.effort.cli import main

    database = tmp_path / "effort.db"
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


def test_supervised_launch_settles_automatically_and_will_not_repeat(
    session_api, tmp_path
):
    import asyncio
    import sys
    from pathlib import Path

    from aitm_usage.effort.capture import HarnessCommand, Observation

    store, launch, turn = layout(session_api, tmp_path / "effort.db")

    class Observes:
        def observe(self, event):
            assert event.stdout == b"finished\n"
            assert store.status(SESSION)[CHILD] == "pending-binding"
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
        store.run_owned(SESSION, CHILD, launch, Observes(), command)
    ).observation.receipt
    assert store.status(SESSION)[CHILD] == "observed"
    with pytest.raises(EffortError, match="already dispatched"):
        asyncio.run(store.run_owned(SESSION, CHILD, launch, Observes(), command))
