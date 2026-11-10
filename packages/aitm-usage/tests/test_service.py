import json
import os
import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest

from aitm_usage import cli
from aitm_usage.ledger import Ledger
from aitm_usage.types import Provider, UsageObservation

PROJECT = UUID(int=920)
CUTOFF = "2026-11-09T16:00:00+00:00"
FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def project(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    root = tmp_path / "state"
    sources, checkout = tmp_path / "sources", tmp_path / "checkout-private"
    sources.mkdir()
    checkout.mkdir()
    config = tmp_path / "registration-input.json"
    config.write_text(
        json.dumps(
            {
                "project_id": str(PROJECT),
                "source_roots": [str(sources)],
                "checkout_anchors": [str(checkout)],
                "cutoff": CUTOFF,
            }
        )
    )

    def command(*args, expected=0):
        monkeypatch.setattr(sys, "argv", ["aitm-usage", "--project", str(root), *args])
        result = cli.main()
        output = capsys.readouterr()
        assert result == expected, output.err
        return json.loads(output.out) if output.out else output.err

    return root, sources, checkout, config, command


def _fixtures(sources, checkout, *, partial=False):
    for provider in ("codex", "claude"):
        data = (FIXTURES / provider / "usage.jsonl").read_bytes()
        data = data.replace(b"CHECKOUT", os.fsencode(checkout))
        (sources / f"{provider}.jsonl").write_bytes(
            data + (b'{"private":"unfinished' if partial else b"")
        )


def test_service_commands_and_coverage(project):
    root, sources, checkout, config, command = project
    _fixtures(sources, checkout, partial=True)
    result = command("register", "--config", str(config), "--json")
    assert result["cutoff"] == CUTOFF
    ledger = Ledger.open(root, PROJECT)
    assert not ledger.as_of().checkpoints

    with ledger.writer():
        refused = command("collect-once", "--json", expected=1)
        assert "writer-active" in json.dumps(refused)
        before = command("status", "--json")
        assert before["heartbeat"] is None
        assert before["producer_mode"] is None
        assert before["producer_pid"] is None
    command("collect-once", "--json")
    status = command("status", "--json")
    assert status["heartbeat"] is not None
    assert status["producer_mode"] == "one-shot"
    assert status["producer_pid"] == os.getpid()
    assert not status["read_gap"]
    assert set(status["coverage"]) == {"codex", "claude"}
    assert status["coverage"]["codex"]["quota"] == "unknown"
    assert status["coverage"]["claude"]["quota"] == "unknown"
    assert status["coverage"]["claude"]["actual_spend"] == "unknown"
    assert status["task_quota"] == "unknown"
    assert len(status["sources"]) == 2
    for source in status["sources"]:
        path = sources / f"{source['provider']}.jsonl"
        assert source["offset"] == path.stat().st_size - len(b'{"private":"unfinished')
        assert source["observed_through"] < status["heartbeat"]
        assert source["lag_seconds"] > 0
        assert source["retention_seconds"] is None
    current = ledger.as_of().current
    assert {
        r.record.boundary.provider
        for r in current
        if isinstance(r.record, UsageObservation)
    } == set(Provider)
    assert str(checkout) not in json.dumps(status)

    rollup = command("rollup", "--item", "83", "--json")
    assert rollup["direct"]["observation_count"] == 0
    assert rollup["unattributed"]["tokens"]["output_tokens"] == 8
    assert rollup["unattributed"]["unknown_price_count"] > 0

    sources.chmod(0o000)
    try:
        command("collect-once", "--json")
        unavailable = command("status", "--json")
    finally:
        sources.chmod(0o700)
    assert unavailable["root_gaps"] == 1
    assert unavailable["missing_sources"] == 2
    assert [entry["offset"] for entry in unavailable["sources"]] == [
        entry["offset"] for entry in status["sources"]
    ]


def test_registration_retry_requires_exact_private_and_typed_authority(
    project, monkeypatch
):
    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)

    def interrupted(self, batch):
        raise OSError("synthetic interrupted registration")

    with monkeypatch.context() as patch:
        patch.setattr(Ledger, "apply", interrupted)
        command("register", "--config", str(config), "--json", expected=1)
    ledger = Ledger.open(root, PROJECT)
    assert ledger.as_of().sequence == 0
    command("collect-once", "--json", expected=1)
    assert ledger.as_of().sequence == 0

    data = json.loads(config.read_text())
    config.write_text(json.dumps({**data, "cutoff": "2026-11-09T15:00:00+00:00"}))
    command("register", "--config", str(config), "--json", expected=1)
    config.write_text(json.dumps(data))
    command("register", "--config", str(config), "--json")
    sequence = ledger.as_of().sequence
    assert sequence == 1
    command("register", "--config", str(config), "--json")
    assert ledger.as_of().sequence == sequence
    stored = root / "registration.json"
    assert stored.stat().st_mode & 0o777 == 0o600
    stored.write_text(json.dumps({**data, "cutoff": "2026-11-09T15:00:00+00:00"}))
    command("collect-once", "--json", expected=1)
    assert ledger.as_of().sequence == sequence


def _json_file(directory, name, payload):
    path = directory / name
    path.write_text(json.dumps(payload))
    return path


def test_anchor_staging_retry_requires_a_matching_receipt_and_effect(
    project, monkeypatch
):
    from aitm_usage import scopes
    from aitm_usage.sources.scan import checkout_anchor_reference
    from aitm_usage.types import (
        LedgerBatch,
        Revision,
        SourceAnchor,
        SourceAnchorCommand,
    )

    root, sources, checkout, config, command = project
    added = checkout.with_name("add-secret")
    added.mkdir()
    _fixtures(sources, added)
    command("register", "--config", str(config), "--json")
    ledger = Ledger.open(root, PROJECT)
    anchor_id = UUID(int=921)
    anchor = _json_file(
        root.parent,
        "add.json",
        {
            "command_id": str(anchor_id),
            "project_id": str(PROJECT),
            "checkout": str(added),
        },
    )

    def interrupted(*args):
        raise OSError("interrupted after private publication")

    publish = scopes._publish

    def interrupted_inbox(directory, *args, **kwargs):
        if directory.path == root / "inbox":
            interrupted()
        return publish(directory, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(scopes, "_publish", interrupted_inbox)
        command("source", "add-anchor", "--anchor", str(anchor), "--json", expected=1)
    assert (root / "source-anchors" / f"{anchor_id}.json").is_file()
    command("collect-once", "--json")
    assert not any(
        isinstance(r.record, UsageObservation) for r in ledger.as_of().current
    )

    registration = next(
        r.record
        for r in ledger.as_of().current
        if hasattr(r.record, "configuration_ref")
    )
    payload = SourceAnchorCommand(
        anchor_id,
        PROJECT,
        registration.configuration_ref,
        checkout_anchor_reference(ledger, added),
    )
    with ledger.writer() as writer:
        writer.apply(
            LedgerBatch(
                (
                    Revision(
                        writer.pseudonymize("fixture", "fake-effect"),
                        1,
                        SourceAnchor(
                            payload.command_id,
                            payload.project_id,
                            payload.configuration_ref,
                            payload.anchor_ref,
                        ),
                    ),
                )
            )
        )
    command("collect-once", "--json")
    assert not any(
        isinstance(r.record, UsageObservation) for r in ledger.as_of().current
    )
    assert (
        command("source", "add-anchor", "--anchor", str(anchor), "--json")["status"]
        == "queued"
    )
    assert (
        str(added).encode() not in (root / "inbox" / f"{anchor_id}.json").read_bytes()
    )
    with monkeypatch.context() as patch:
        patch.setattr(scopes, "_acknowledge", interrupted)
        command("collect-once", "--json", expected=1)
    # A fresh poll reconstructs authority from the exact accepted pair and
    # retires the already committed queue item.
    command("collect-once", "--json")
    assert (
        command("source", "add-anchor", "--anchor", str(anchor), "--json")["status"]
        == "accepted"
    )
    assert not (root / "inbox" / f"{anchor_id}.json").exists()
    assert any(isinstance(r.record, UsageObservation) for r in ledger.as_of().current)
    assert str(added).encode() not in ledger.database_path.read_bytes()
    config_cutoff = command("status", "--json")["cutoff"]
    assert config_cutoff == CUTOFF


def test_collection_does_not_scan_after_the_qualifying_drain(project, monkeypatch):
    from test_codex import (
        SESSION,
        begin,
        counter,
        response,
        startup,
        tool_call,
        tool_output,
        usage,
        write,
    )

    from aitm_usage import scopes, service
    from aitm_usage.sources.codex import codex_request_boundary_reference
    from aitm_usage.types import (
        BoundaryKind,
        ItemKey,
        ItemKind,
        ScopeMarker,
        WorkPhase,
        encode_marker,
    )

    root, sources, checkout, config, command = project
    command("register", "--config", str(config), "--json")
    ledger = Ledger.open(root, PROJECT)
    monkeypatch.setenv("CODEX_THREAD_ID", str(SESSION))
    source = sources / "codex.jsonl"
    marker_id = UUID(int=922)
    session = scopes.session_reference(ledger, Provider.CODEX, str(SESSION))
    marker = ScopeMarker(
        marker_id,
        Provider.CODEX,
        session,
        1,
        BoundaryKind.REQUEST,
        codex_request_boundary_reference(ledger, session, marker_id),
        datetime.fromisoformat(CUTOFF),
        ItemKey(ItemKind.ISSUE, 83),
        WorkPhase.PLANNING,
        ledger.pseudonymize("test-participant", "private"),
        PROJECT,
        receipt_ref=ledger.pseudonymize("scope-receipt", str(marker_id)),
    )
    marker_path = root.parent / "scope.json"
    marker_path.write_bytes(encode_marker(marker))
    write(source, [startup(checkout)])
    observed_size = source.stat().st_size
    before = service.drain_inbox

    def race(writer, evidence):
        outcome = before(writer, evidence)
        reply = command("scope", "mark", "--marker", str(marker_path), "--json")
        prior_usage, counts, total = usage(8, 2), usage(9, 3), usage(17, 5)
        write(
            source,
            [
                *begin(checkout),
                tool_call(ledger, marker_path),
                response("private-before-snapshot", prior_usage, prior_usage),
                tool_output(marker_id, stdout=json.dumps(reply)),
                counter(prior_usage, prior_usage),
                response("private-after-snapshot", total, counts),
                counter(total, counts),
            ],
            append=True,
        )
        return outcome

    with monkeypatch.context() as patch:
        patch.setattr(service, "drain_inbox", race)
        command("collect-once", "--json")
    first = ledger.as_of()
    assert first.checkpoints[0].cursor.offset == observed_size
    assert not any(isinstance(r.record, UsageObservation) for r in first.current)

    command("collect-once", "--json")
    # The admitted selector changed in the qualifying drain. Discard the
    # pre-change projection and defer until a new pre-drain selected scan.
    assert ledger.as_of().checkpoints == first.checkpoints
    command("collect-once", "--json")
    totals = command("rollup", "--item", "83", "--json")
    assert totals["direct"]["tokens"]["output_tokens"] == 3
    assert totals["direct"]["observation_count"] == 1


def test_status_interruption_does_not_claim_new_observed_time_and_busy_keeps_heartbeat(
    project, monkeypatch
):
    import sqlite3

    from aitm_usage import service

    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    first = command("status", "--json")
    old = next(source for source in first["sources"] if source["provider"] == "codex")
    path = sources / "codex.jsonl"
    with path.open("ab") as transcript:
        transcript.write(
            b'{"type":"event_msg","timestamp":"2026-11-09T16:00:06Z",'
            b'"payload":{"type":"task_complete",'
            b'"turn_id":"00000000-0000-0000-0000-000000000102"}}\n'
        )

    def fail_publish(*args, **kwargs):
        raise OSError("synthetic status interruption")

    with monkeypatch.context() as patch:
        patch.setattr(service, "_publish", fail_publish)
        command("collect-once", "--json", expected=1)
    status = command("status", "--json")
    changed = next(
        source for source in status["sources"] if source["provider"] == "codex"
    )
    assert status["heartbeat"] == first["heartbeat"]
    assert changed["offset"] > old["offset"]
    assert changed["observed_through"] is None
    assert changed["lag_seconds"] is None

    def busy(self, *args):
        raise sqlite3.OperationalError("database is locked")

    with monkeypatch.context() as patch:
        patch.setattr(Ledger, "as_of", busy)
        status = command("status", "--json")
    assert status["read_gap"]
    assert status["heartbeat"] == first["heartbeat"]
    assert status["sources"] == []


def test_continuous_writer_acknowledges_binding_correction_and_anchor(
    project, monkeypatch
):
    import shlex
    from dataclasses import replace
    from decimal import Decimal

    import test_claude as claude
    import test_codex as codex

    from aitm_usage import service
    from aitm_usage.scopes import session_reference
    from aitm_usage.sources.claude import claude_request_boundary_reference
    from aitm_usage.sources.codex import codex_request_boundary_reference
    from aitm_usage.sources.scan import checkout_anchor_reference
    from aitm_usage.types import (
        BoundaryKind,
        DevelopmentBinding,
        ItemKey,
        ItemKind,
        ScopeCorrection,
        ScopeMarker,
        WorkPhase,
        encode_binding,
        encode_correction,
        encode_marker,
    )

    root, sources, checkout, config, command = project
    added = checkout.with_name("added-private-worktree")
    added.mkdir()
    command("register", "--config", str(config), "--json")
    ledger = Ledger.open(root, PROJECT)
    anchor_id, bind_id, mark_id, correct_id = (
        UUID(int=n) for n in (923, 924, 925, 926)
    )
    anchor = _json_file(
        root.parent,
        "anchor.json",
        {
            "command_id": str(anchor_id),
            "project_id": str(PROJECT),
            "checkout": str(added),
        },
    )
    child = ItemKey(ItemKind.ISSUE, 85)
    other = ItemKey(ItemKind.ISSUE, 86)
    cl_session = session_reference(ledger, Provider.CLAUDE, str(claude.SESSION))
    cx_session = session_reference(ledger, Provider.CODEX, str(codex.SESSION))
    mark = ScopeMarker(
        mark_id,
        Provider.CLAUDE,
        cl_session,
        1,
        BoundaryKind.REQUEST,
        claude_request_boundary_reference(ledger, cl_session, mark_id),
        claude.AFTER,
        child,
        WorkPhase.PLANNING,
        ledger.pseudonymize("participant", "cl"),
        PROJECT,
        receipt_ref=ledger.pseudonymize("scope-receipt", str(mark_id)),
    )
    bind_marker = ScopeMarker(
        bind_id,
        Provider.CODEX,
        cx_session,
        1,
        BoundaryKind.REQUEST,
        codex_request_boundary_reference(ledger, cx_session, bind_id),
        codex.AFTER,
        child,
        WorkPhase.DEVELOPMENT,
        ledger.pseudonymize("participant", "cx"),
        PROJECT,
        receipt_ref=ledger.pseudonymize("scope-receipt", str(bind_id)),
        attempt_ref=ledger.pseudonymize("attempt", "attempt-1"),
    )
    mark_path, binding_path, correction_path = (
        root.parent / name
        for name in ("marker.json", "binding.json", "correction.json")
    )
    mark_path.write_bytes(encode_marker(mark))
    binding_path.write_bytes(
        encode_binding(
            DevelopmentBinding(
                bind_marker, checkout_anchor_reference(ledger, checkout), 1
            )
        )
    )
    correction_path.write_bytes(
        encode_correction(
            ScopeCorrection(
                correct_id,
                PROJECT,
                replace(mark, item=other),
                ledger.pseudonymize("evidence", "repair"),
            )
        )
    )
    mark_args = (
        "scope",
        "mark",
        "--marker",
        str(mark_path),
        "--session-id",
        str(claude.SESSION),
        "--json",
    )
    bind_args = ("development", "bind", "--binding", str(binding_path), "--json")
    polls = 0
    monkeypatch.setenv("CODEX_THREAD_ID", str(codex.SESSION))

    def between_polls(interval):
        nonlocal polls
        assert interval == 15
        status = command("status", "--json")
        assert status["producer_mode"] == "service"
        assert status["producer_pid"] == os.getpid()
        polls += 1
        assert (
            command("collect-once", "--json", expected=1)["status"] == "writer-active"
        )
        if polls == 1:
            assert (
                command("source", "add-anchor", "--anchor", str(anchor), "--json")[
                    "status"
                ]
                == "queued"
            )
            for item in ("85", "86"):
                assert (
                    command(
                        "item", "parent", "--child", item, "--epic", "83", "--json"
                    )["status"]
                    == "queued"
                )
            marked = command(*mark_args)
            bound = command(*bind_args)
            assert marked["status"] == bound["status"] == "queued"
            shell = shlex.join(("aitm-usage", "--project", str(root), *mark_args))
            claude.write(
                sources / "claude.jsonl",
                [
                    claude.user(added),
                    *claude._native_tool_turn(added, shell, json.dumps(marked)),
                ],
            )
            first, last, total = (
                codex.usage(8, 2),
                codex.usage(9, 3),
                codex.usage(17, 5),
            )
            codex.write(
                sources / "codex.jsonl",
                [
                    codex.startup(checkout),
                    *codex.begin(checkout),
                    codex.event(
                        "thread_settings_applied",
                        thread_id=str(codex.SESSION),
                        thread_settings={
                            "model": "gpt-6-astra",
                            "model_provider_id": "openai",
                            "service_tier": "default",
                        },
                    ),
                    codex.tool_call(ledger, binding_path, bind=True),
                    codex.response("before-bind", first, first),
                    codex.tool_output(bind_id, stdout=json.dumps(bound)),
                    codex.counter(first, first),
                    codex.response("after-bind", total, last),
                    codex.counter(total, last),
                    codex.end(),
                ],
            )
        elif polls == 2:
            assert (
                command("source", "add-anchor", "--anchor", str(anchor), "--json")[
                    "status"
                ]
                == "accepted"
            )
            assert command(*bind_args)["status"] == "accepted"
            assert command(*mark_args)["status"] == "accepted"
            assert not ledger.as_of().checkpoints
        elif polls == 3:
            direct = command("rollup", "--item", "85", "--json")["direct"]
            assert direct["tokens"]["output_tokens"] == 7
            assert direct["observation_count"] == 2
            assert Decimal(direct["known_usd"]) > 0
            assert direct["unknown_price_count"] == 1
            assert (
                command(
                    "scope", "correct", "--correction", str(correction_path), "--json"
                )["status"]
                == "queued"
            )
        elif polls == 4:
            assert (
                command(
                    "scope", "correct", "--correction", str(correction_path), "--json"
                )["status"]
                == "accepted"
            )
            totals = command("rollup", "--item", "83", "--json")
            assert totals["direct"]["observation_count"] == 0
            assert totals["inclusive"]["observation_count"] == 2
            assert totals["inclusive"]["tokens"]["output_tokens"] == 7
            assert (
                command("rollup", "--item", "86", "--json")["direct"]["tokens"][
                    "output_tokens"
                ]
                == 4
            )
            raise KeyboardInterrupt

    monkeypatch.setattr(service.time, "sleep", between_polls)
    assert command("service", "run") == ""
    assert polls == 4
    for path in (root / "claude-sessions").iterdir():
        assert str(claude.SESSION).encode() not in path.read_bytes()


@pytest.mark.parametrize("account_provider", ["codex", "claude"])
def test_quota_authority_is_exact_stream_and_provider(project, account_provider):
    from aitm_usage.scopes import session_reference

    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)
    ledger = Ledger.initialize(root, PROJECT)
    session_ref = session_reference(ledger, Provider.CODEX, str(UUID(int=0x101)))
    stream = ledger.pseudonymize("codex-stream", session_ref.value)
    account = ledger.pseudonymize("account", "private-confirmed-account")
    data = json.loads(config.read_text())
    data["account_refs"] = [
        {
            "provider": account_provider,
            "stream_ref": stream.value,
            "account_ref": account.value,
        }
    ]
    data["retention_limits"] = [{"provider": "codex", "seconds": 604800}]
    config.write_text(json.dumps(data))
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    status = command("status", "--json")
    expected = "observed" if account_provider == "codex" else "unknown"
    assert status["coverage"]["codex"]["quota"] == expected
    assert status["coverage"]["claude"]["quota"] == "unknown"
    assert status["task_quota"] == "unknown"
    assert status["coverage"]["codex"]["actual_spend"] == "unknown"
    assert {
        source["provider"]: source["retention_seconds"] for source in status["sources"]
    } == {
        "codex": 604800,
        "claude": None,
    }


@pytest.mark.parametrize("explicit", [False, True])
def test_unresolved_earlier_segment_holds_frontier_unless_positively_excluded(
    project, explicit
):
    from test_claude import request, usage, user, write

    from aitm_usage.sources.scan import discover, scan
    from aitm_usage.types import Registration

    root, sources, checkout, config, command = project
    unrelated = checkout.with_name("unrelated-private")
    unrelated.mkdir()
    write(
        sources / "claude.jsonl",
        [
            user(unrelated),
            request(
                unrelated, req="outside-req", msg="outside-msg", counts=usage(output=50)
            ),
            user(checkout),
            request(
                checkout, req="inside-req", msg="inside-msg", counts=usage(output=4)
            ),
        ],
    )
    if explicit:
        Ledger.initialize(root, PROJECT)
        registration = Registration(
            PROJECT, root, (sources,), (checkout,), datetime.fromisoformat(CUTOFF)
        )
        (candidate,) = discover(registration)
        batch = scan(candidate, None, registration.cutoff)
        data = json.loads(config.read_text())
        data["excluded_segments"] = [batch.frames[0].segment_ref.value]
        config.write_text(json.dumps(data))
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    view = Ledger.open(root, PROJECT).as_of()
    measured = [
        r.record.tokens.output_tokens
        for r in view.current
        if isinstance(r.record, UsageObservation)
    ]
    assert measured == ([4] if explicit else [])
    assert command("status", "--json")["held_sources"] == (0 if explicit else 1)


def test_status_matches_producer_runtime_and_authenticates_observed_time(project):
    from importlib.metadata import version
    from platform import python_version

    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    first = command("status", "--json")
    assert first["collector_version"] == version("aitm-usage")
    assert first["collector_interpreter_version"] == python_version()
    path = root / "status.json"
    data = json.loads(path.read_text())
    ref = data["observed"][0]["source_ref"]
    data["observed"][0]["through"] = "2026-11-09T16:01:00+00:00"
    path.write_text(json.dumps(data, separators=(",", ":"), sort_keys=True))
    status = command("status", "--json")
    source = next(source for source in status["sources"] if source["source_ref"] == ref)
    assert source["observed_through"] is None
    assert source["lag_seconds"] is None
    assert source["offset"] > 0


@pytest.mark.parametrize("owner_matches", [True, False])
def test_claude_quota_still_requires_native_same_segment_owner(project, owner_matches):
    from datetime import timedelta

    from test_claude import ACCOUNT, AFTER, SESSION, owner, request, row, user, write

    from aitm_usage.scopes import session_reference
    from aitm_usage.types import AccountObservation

    root, sources, checkout, config, command = project
    ledger = Ledger.initialize(root, PROJECT)
    session_ref = session_reference(ledger, Provider.CLAUDE, str(SESSION))
    stream = ledger.pseudonymize("claude-stream", session_ref.value)
    account = ledger.pseudonymize(
        "claude-account", str(ACCOUNT if owner_matches else UUID(int=987))
    )
    write(
        sources / "claude.jsonl",
        [
            user(checkout),
            request(checkout),
            owner(),
            row(
                "rate_limit_event",
                checkout,
                rate_limit_info={
                    "status": "allowed",
                    "rateLimitType": "seven_day",
                    "resetsAt": int((AFTER + timedelta(hours=1)).timestamp()),
                    "utilization": 0.2,
                },
            ),
        ],
    )
    data = json.loads(config.read_text())
    data["account_refs"] = [
        {
            "provider": "claude",
            "stream_ref": stream.value,
            "account_ref": account.value,
        }
    ]
    config.write_text(json.dumps(data))
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    status = command("status", "--json")
    assert status["coverage"]["claude"]["quota"] == (
        "observed" if owner_matches else "unknown"
    )
    assert status["task_quota"] == "unknown"
    quota = [
        r.record
        for r in ledger.as_of().current
        if isinstance(r.record, AccountObservation)
    ]
    if owner_matches:
        (reading,) = quota
        assert reading.account_ref == account
        assert reading.percent_milli == 20000
    else:
        assert not quota


def test_unstaged_typed_anchor_command_cannot_enroll(project):
    from aitm_usage.scopes import enqueue_command
    from aitm_usage.sources.scan import checkout_anchor_reference
    from aitm_usage.types import (
        InboxCommand,
        MarkerDisposition,
        ProjectRegistration,
        SourceAnchorCommand,
    )

    root, sources, checkout, config, command = project
    added = checkout.with_name("private-unstaged")
    added.mkdir()
    _fixtures(sources, added)
    command("register", "--config", str(config), "--json")
    ledger = Ledger.open(root, PROJECT)
    (registration,) = [
        r.record
        for r in ledger.as_of().current
        if isinstance(r.record, ProjectRegistration)
    ]
    anchor_id = UUID(int=929)
    payload = SourceAnchorCommand(
        anchor_id,
        PROJECT,
        registration.configuration_ref,
        checkout_anchor_reference(ledger, added),
    )
    proposal = InboxCommand(anchor_id, PROJECT, payload)
    assert enqueue_command(root, proposal) is None
    command("collect-once", "--json")
    assert ledger.command_receipt(proposal).disposition is MarkerDisposition.CONFLICT
    checkpoints = ledger.as_of().checkpoints
    assert checkpoints and all(entry.cursor.offset == 0 for entry in checkpoints)
    assert not any(
        isinstance(r.record, UsageObservation) for r in ledger.as_of().current
    )


def test_exact_queued_anchor_retries_when_checkout_returns(project):
    root, sources, checkout, config, command = project
    added = checkout.with_name("temporarily-unavailable")
    added.mkdir()
    _fixtures(sources, added)
    command("register", "--config", str(config), "--json")
    anchor = _json_file(
        root.parent,
        "queued-anchor.json",
        {
            "command_id": str(UUID(int=930)),
            "project_id": str(PROJECT),
            "checkout": str(added),
        },
    )
    args = ("source", "add-anchor", "--anchor", str(anchor), "--json")
    assert command(*args)["status"] == "queued"
    elsewhere = added.with_suffix(".away")
    added.rename(elsewhere)
    command("collect-once", "--json")
    assert command(*args)["status"] == "pending"
    checkpoints = Ledger.open(root, PROJECT).as_of().checkpoints
    assert checkpoints and all(entry.cursor.offset == 0 for entry in checkpoints)
    elsewhere.rename(added)
    command("collect-once", "--json")
    assert command(*args)["status"] == "accepted"
    command("collect-once", "--json")
    assert Ledger.open(root, PROJECT).as_of().checkpoints


def test_reused_locator_keeps_previous_checkpoint_and_reports_missing_stream(project):
    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    ledger = Ledger.open(root, PROJECT)
    before = ledger.as_of()
    path = sources / "codex.jsonl"
    path.write_bytes(
        path.read_bytes().replace(
            str(UUID(int=0x101)).encode(), str(UUID(int=0x123)).encode()
        )
    )
    command("collect-once", "--json")
    after = ledger.as_of()
    assert after.checkpoints == before.checkpoints
    assert [r for r in after.current if isinstance(r.record, UsageObservation)] == [
        r for r in before.current if isinstance(r.record, UsageObservation)
    ]
    status = command("status", "--json")
    assert status["missing_sources"] == 1
    assert status["coverage"]["codex"]["diagnostics"] > 0


@pytest.mark.parametrize("layout", ["effect-first", "receipt-first", "same-commit"])
def test_generic_anchor_writes_cannot_replace_inbox_admission(
    project, monkeypatch, layout
):
    from aitm_usage import service
    from aitm_usage.ledger import LedgerError
    from aitm_usage.types import (
        CommandReceipt,
        Diagnostic,
        DiagnosticCode,
        LedgerBatch,
        MarkerDisposition,
        Revision,
        SourceAnchor,
    )

    root, sources, checkout, config, command = project
    added = checkout.with_name("new-private-anchor")
    added.mkdir()
    _fixtures(sources, added)
    command("register", "--config", str(config), "--json")
    ledger = Ledger.open(root, PROJECT)
    anchor_id = UUID(int=933)
    anchor = _json_file(
        root.parent,
        "new-anchor.json",
        {
            "command_id": str(anchor_id),
            "project_id": str(PROJECT),
            "checkout": str(added),
        },
    )
    staged = service.stage_source_anchor(ledger, anchor)
    payload = staged.payload
    effect = Revision(
        ledger.pseudonymize("collector-source-anchor", str(anchor_id)),
        1,
        SourceAnchor(
            payload.command_id,
            payload.project_id,
            payload.configuration_ref,
            payload.anchor_ref,
        ),
    )
    receipt = CommandReceipt(
        staged, ledger.validate_command(staged), MarkerDisposition.ACCEPTED
    )
    if layout != "same-commit":
        # A genuine dispatcher decision is interrupted before commit. A
        # private route proof must not turn split writes into an atomic pair.
        assert (
            command("source", "add-anchor", "--anchor", str(anchor), "--json")["status"]
            == "queued"
        )

        def interrupted(*args, **kwargs):
            assert (
                len(list((root / "source-anchors").glob(f"{anchor_id}.*.attested")))
                == 1
            )
            raise OSError("synthetic interruption before inbox commit")

        with monkeypatch.context() as patch:
            patch.setattr(Ledger, "commit_command", interrupted)
            command("collect-once", "--json", expected=1)
        if layout == "effect-first":
            ledger.apply(LedgerBatch((effect,)))
        effects = (
            Revision(
                ledger.pseudonymize("fixture", "unrelated-diagnostic"),
                1,
                Diagnostic(
                    DiagnosticCode.SOURCE_UNAVAILABLE, datetime.fromisoformat(CUTOFF)
                ),
            ),
        )
    else:
        # The two canonical revisions really share one commit here. No
        # collector inbox decision authorized that commit.
        effects = (effect,)
    with ledger.writer() as writer:
        writer.commit_command(
            receipt, effects, expected_sequence=writer.as_of().sequence
        )
        if layout == "receipt-first":
            writer.apply(LedgerBatch((effect,)))
    with pytest.raises(LedgerError):
        service.load_registration(ledger)
    assert command("collect-once", "--json", expected=1) == {
        "status": "collection-failed"
    }
    retry = command(
        "source", "add-anchor", "--anchor", str(anchor), "--json", expected=1
    )
    assert retry.strip() == "aitm-usage: invalid private inbox command or project"
    if layout != "same-commit":
        assert (root / "inbox" / f"{anchor_id}.json").exists()
    assert not (root / "inbox" / "acks" / f"{anchor_id}.json").exists()
    assert not any(
        isinstance(r.record, UsageObservation) for r in ledger.as_of().current
    )


def test_anchor_route_retry_after_private_attestation_interruption(
    project, monkeypatch
):
    from aitm_usage import service
    from aitm_usage.types import Diagnostic, DiagnosticCode, LedgerBatch, Revision

    root, sources, checkout, config, command = project
    added = checkout.with_name("retry-after-attestation")
    added.mkdir()
    _fixtures(sources, added)
    command("register", "--config", str(config), "--json")
    ledger = Ledger.open(root, PROJECT)
    anchor_id = UUID(int=934)
    anchor = _json_file(
        root.parent,
        "retry-anchor.json",
        {
            "command_id": str(anchor_id),
            "project_id": str(PROJECT),
            "checkout": str(added),
        },
    )
    args = ("source", "add-anchor", "--anchor", str(anchor), "--json")
    assert command(*args)["status"] == "queued"
    proofs = root / "source-anchors"

    def interrupted(*args, **kwargs):
        assert len(list(proofs.glob(f"{anchor_id}.*.attested"))) == 1
        raise OSError("synthetic interruption after attestation")

    with monkeypatch.context() as patch:
        patch.setattr(Ledger, "commit_command", interrupted)
        command("collect-once", "--json", expected=1)
    assert service.load_registration(ledger).checkout_anchors == (checkout,)
    assert command(*args)["status"] == "queued"
    (orphan,) = proofs.glob(f"{anchor_id}.*.attested")
    original = orphan.read_bytes()

    # Retry after another legitimate commit moved the expected sequence.
    ledger.apply(
        LedgerBatch(
            (
                Revision(
                    ledger.pseudonymize("fixture", "intervening-diagnostic"),
                    1,
                    Diagnostic(
                        DiagnosticCode.SOURCE_UNAVAILABLE,
                        datetime.fromisoformat(CUTOFF),
                    ),
                ),
            )
        )
    )
    command("collect-once", "--json")
    assert command(*args)["status"] == "accepted"
    assert service.load_registration(ledger).checkout_anchors == tuple(
        sorted((checkout, added))
    )
    assert orphan.read_bytes() == original
    assert len(list(proofs.glob(f"{anchor_id}.*.attested"))) == 2
    command("collect-once", "--json")
    assert any(isinstance(r.record, UsageObservation) for r in ledger.as_of().current)


def test_zero_held_frontier_pins_identity_before_source_replacement(project):
    root, sources, checkout, config, command = project
    unapproved = checkout.with_name("unbound-private")
    unapproved.mkdir()
    source = sources / "codex.jsonl"
    fixture = (FIXTURES / "codex" / "usage.jsonl").read_bytes()
    source.write_bytes(fixture.replace(b"CHECKOUT", os.fsencode(unapproved)))
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    ledger = Ledger.open(root, PROJECT)
    (checkpoint,) = ledger.as_of().checkpoints
    assert checkpoint.cursor.offset == checkpoint.provider.ordinal == 0
    assert checkpoint.provider.baseline is None
    assert checkpoint.provider.epoch_ref is None
    assert not any(
        isinstance(r.record, UsageObservation) for r in ledger.as_of().current
    )

    replacement = sources / "replacement"
    replacement.write_bytes(fixture.replace(b"CHECKOUT", os.fsencode(checkout)))
    replacement.replace(source)
    command("collect-once", "--json")
    view = ledger.as_of()
    assert view.checkpoints == (checkpoint,)
    assert not any(isinstance(r.record, UsageObservation) for r in view.current)
    assert command("status", "--json")["coverage"]["codex"]["diagnostics"] > 0


@pytest.mark.parametrize("loss", ["after-interrupted-ack", "before-first-ack"])
def test_unproven_accepted_anchor_preserves_queue_until_proof_restored(
    project, monkeypatch, loss
):
    from aitm_usage import scopes

    root, sources, checkout, config, command = project
    added = checkout.with_name("private-proof-lost")
    added.mkdir()
    _fixtures(sources, added)
    command("register", "--config", str(config), "--json")
    ledger = Ledger.open(root, PROJECT)
    anchor_id = UUID(int=935)
    anchor = _json_file(
        root.parent,
        "proof-lost.json",
        {
            "command_id": str(anchor_id),
            "project_id": str(PROJECT),
            "checkout": str(added),
        },
    )
    args = ("source", "add-anchor", "--anchor", str(anchor), "--json")
    assert command(*args)["status"] == "queued"
    queued = root / "inbox" / f"{anchor_id}.json"
    ack = root / "inbox" / "acks" / f"{anchor_id}.json"
    proof_dir = root / "source-anchors"
    saved = None

    def remove_proof():
        nonlocal saved
        (proof,) = proof_dir.glob(f"{anchor_id}.*.attested")
        saved = (proof, proof.read_bytes())
        proof.unlink()

    original_commit = Ledger.commit_command

    def commit_without_proof(*args, **kwargs):
        receipt = original_commit(*args, **kwargs)
        remove_proof()
        return receipt

    def interrupt_ack(*args, **kwargs):
        raise OSError("synthetic interruption before acknowledgment")

    with monkeypatch.context() as patch:
        if loss == "before-first-ack":
            patch.setattr(Ledger, "commit_command", commit_without_proof)
        else:
            patch.setattr(scopes, "_acknowledge", interrupt_ack)
        assert command("collect-once", "--json", expected=1) == {
            "status": "collection-failed"
        }
    assert queued.exists()
    assert not ack.exists()
    if loss == "after-interrupted-ack":
        remove_proof()
    sequence = ledger.as_of().sequence
    assert command("collect-once", "--json", expected=1) == {
        "status": "collection-failed"
    }
    retry = command(*args, expected=1)
    assert retry.strip() == "aitm-usage: invalid private inbox command or project"
    status = command("status", "--json")
    assert status["registration_gap"] is True
    assert status["read_gap"] is False
    assert str(added) not in json.dumps(status)
    assert queued.exists()
    assert not ack.exists()
    assert ledger.as_of().sequence == sequence
    assert not ledger.as_of().checkpoints

    proof, data = saved
    proof.write_bytes(data)
    proof.chmod(0o600)
    command("collect-once", "--json")
    assert command(*args)["status"] == "accepted"
    assert ack.exists()
    assert not queued.exists()
    assert command("status", "--json")["registration_gap"] is False
    assert any(isinstance(r.record, UsageObservation) for r in ledger.as_of().current)


def test_one_shot_status_uses_collecting_subprocess_pid(project, pytestconfig):
    import subprocess

    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)
    command("register", "--config", str(config), "--json")
    runner = FIXTURES / "service" / "run_cli.py"
    console = Path(sys.executable).with_name("aitm-usage")
    with subprocess.Popen(
        [
            sys.executable,
            str(runner),
            str(root.parent / "control"),
            str(console),
            "-",
            "-",
            "-",
            "--project",
            str(root),
            "collect-once",
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        output, error = process.communicate(timeout=15)
        if os.environ.get("AITM_CI_CHILD_EVIDENCE") == "1":
            observer = pytestconfig.pluginmanager.get_plugin("pytest_evidence")
            assert observer is not None, (
                "CI child evidence requires the pytest observer"
            )
            observer.record_child(
                pytestconfig, "service-one-shot", process.pid, process.returncode
            )
        assert process.returncode == 0, error
        assert json.loads(output)["sequence"] > 0
        child_pid = process.pid
    status = command("status", "--json")
    assert status["producer_mode"] == "one-shot"
    assert status["producer_pid"] == child_pid
    assert status["producer_pid"] != os.getpid()


def test_legacy_status_keeps_heartbeat_and_authenticated_watermarks(project):
    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    before = command("status", "--json")
    path = root / "status.json"
    payload = json.loads(path.read_text())
    payload.pop("producer_mode", None)
    payload.pop("producer_pid", None)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True))

    legacy = command("status", "--json")
    assert legacy["producer_mode"] is None
    assert legacy["producer_pid"] is None
    for key in (
        "heartbeat",
        "collector_version",
        "collector_interpreter_version",
        "sequence",
        "status_sequence",
        "read_gap",
        "registration_gap",
    ):
        assert legacy[key] == before[key]
    for previous, current in zip(before["sources"], legacy["sources"], strict=True):
        assert current["source_ref"] == previous["source_ref"]
        assert current["offset"] == previous["offset"]
        assert current["observed_through"] == previous["observed_through"]


@pytest.mark.parametrize(
    "invalid",
    [
        {"producer_mode": "service"},
        {"producer_pid": 123},
        {"producer_mode": "service", "producer_pid": 0},
        {"producer_mode": "service", "producer_pid": True},
        {"producer_mode": "service", "producer_pid": "123"},
        {"producer_mode": "unexpected-private-mode", "producer_pid": 123},
    ],
)
def test_status_refuses_malformed_or_half_producer_witness(project, invalid):
    root, sources, checkout, config, command = project
    _fixtures(sources, checkout)
    command("register", "--config", str(config), "--json")
    command("collect-once", "--json")
    before = command("status", "--json")
    path = root / "status.json"
    payload = json.loads(path.read_text())
    payload.pop("producer_mode", None)
    payload.pop("producer_pid", None)
    path.write_text(
        json.dumps({**payload, **invalid}, separators=(",", ":"), sort_keys=True)
    )

    status = command("status", "--json")
    assert status["producer_mode"] is None
    assert status["producer_pid"] is None
    assert status["heartbeat"] is None
    assert status["read_gap"] is False
    assert status["registration_gap"] is False
    assert [entry["offset"] for entry in status["sources"]] == [
        entry["offset"] for entry in before["sources"]
    ]
    assert all(entry["observed_through"] is None for entry in status["sources"])
    assert "unexpected-private-mode" not in json.dumps(status)
