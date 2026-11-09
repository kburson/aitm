import importlib
import json
import shlex
import subprocess
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest

from aitm_usage.cli import main
from aitm_usage.ledger import Ledger
from aitm_usage.rollup import rollup
from aitm_usage.scopes import drain_inbox, enqueue_marker, session_reference
from aitm_usage.sources.scan import checkout_anchor_reference, discover, scan
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    DevelopmentBinding,
    DiagnosticCode,
    Effort,
    Eligibility,
    ItemKey,
    ItemKind,
    LedgerBatch,
    ModelLabel,
    ProcessingTier,
    Provider,
    QuotaBucket,
    QuotaSource,
    Registration,
    ScopeEnrollment,
    ScopeMarker,
    SourceCheckpoint,
    TokenCounts,
    WorkPhase,
    encode_binding,
    encode_marker,
)

PROJECT = UUID(int=0x100)
SESSION = UUID(int=0x101)
TURN = UUID(int=0x102)
CHILD = UUID(int=0x103)
COMMAND = UUID(int=0x104)
CUTOFF = datetime(2026, 11, 9, 16, tzinfo=UTC)
BEFORE = CUTOFF - timedelta(seconds=1)
AFTER = CUTOFF + timedelta(seconds=10)
FIXTURE = Path(__file__).parent / "fixtures/codex/usage.jsonl"


def adapter():
    name = "aitm_usage.sources.codex"
    assert importlib.util.find_spec(name) is not None, (
        "U04 must supply the Codex adapter"
    )
    return importlib.import_module(name)


@pytest.fixture
def project(tmp_path, monkeypatch):
    base = tmp_path.resolve()
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: base / "control")
    ledger = Ledger.initialize(base / "project", PROJECT)
    roots = base / "transcripts"
    checkout = base / "checkout-secret"
    outside = base / "unrelated-secret"
    for path in (roots, checkout, outside):
        path.mkdir()
    registration = Registration(PROJECT, ledger.root, (roots,), (checkout,), CUTOFF)
    return ledger, registration, roots / "live-secret.jsonl", checkout, outside


def row(kind, payload, time=AFTER):
    return {"type": kind, "timestamp": time.isoformat(), "payload": payload}


def event(kind, time=AFTER, **payload):
    return row("event_msg", {"type": kind, **payload}, time)


def startup(cwd, time=AFTER, **extra):
    return row(
        "session_meta",
        {
            "id": str(SESSION),
            "session_id": str(SESSION),
            "cwd": str(cwd),
            "cli_version": "0.167.0-alpha.3.2",
            "model_provider": "openai",
            "source": "vscode",
            **extra,
        },
        time,
    )


def begin(cwd, turn=TURN, time=AFTER, model="gpt-6-astra", effort="xhigh"):
    return [
        event("task_started", time, turn_id=str(turn)),
        row(
            "turn_context",
            {"cwd": str(cwd), "turn_id": str(turn), "model": model, "effort": effort},
            time,
        ),
    ]


def end(turn=TURN, time=AFTER):
    return event("task_complete", time, turn_id=str(turn))


def usage(input_tokens, output_tokens, cache=0, reasoning=0, writes=0):
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cache,
        "cache_write_input_tokens": writes,
        "output_tokens": output_tokens,
        "reasoning_output_tokens": reasoning,
        "total_tokens": input_tokens + output_tokens,
    }


def counter(total, last, time=AFTER, **extra):
    return event(
        "token_count",
        time,
        info={"total_token_usage": total, "last_token_usage": last},
        **extra,
    )


def response(name, total, last, time=AFTER, turn=TURN, thread=SESSION, root=SESSION):
    return row(
        "token_usage_record",
        {
            "thread_id": str(thread),
            "session_id": str(root),
            "turn_id": str(turn),
            "root_turn_id": str(turn),
            "response_id": name,
            "usage": last,
            "turn_token_usage": last,
            "thread_token_usage": total,
        },
        time,
    )


def write(path, rows, append=False):
    with path.open("a" if append else "w", encoding="utf-8") as stream:
        for entry in rows:
            stream.write(json.dumps(entry) + "\n")


def source(registration):
    (candidate,) = discover(registration)
    return candidate


def read(codex, candidate, state, prior=None):
    batch = scan(candidate, prior, CUTOFF)
    return batch, codex.read_codex(batch, state, Eligibility.ELIGIBLE)


def commit(ledger, batch, result, prior=None):
    checkpoint = SourceCheckpoint(batch.cursor, result.provider_checkpoint)
    ledger.apply(
        LedgerBatch(
            revisions=result.revisions, checkpoint=checkpoint, prior_checkpoint=prior
        )
    )
    return checkpoint


def observations(result):
    return [revision.record for revision in result.revisions]


def codes(result):
    return {(entry.ordinal, entry.code) for entry in result.diagnostics}


def test_codex_deltas_exclusion_and_epochs(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    path.write_text(FIXTURE.read_text().replace("CHECKOUT", str(checkout)))
    account = ledger.pseudonymize("codex-account", "private-account-secret")
    state = codex.CodexState(ledger, account_ref=account)
    candidate = source(registration)
    batch, first = read(codex, candidate, state)
    (record,) = observations(first)
    assert record.boundary.ordinal == 3
    assert record.boundary.session_ref == candidate.session_ref
    assert record.boundary.stream_ref == candidate.stream_ref
    assert record.tokens == TokenCounts(12, 8, 0, 0, 4, 2, 16)
    assert (record.model, record.effort, record.availability) == (
        ModelLabel.GPT_6_ASTRA,
        Effort.XHIGH,
        Availability.COMPLETE,
    )
    (quota,) = first.quota
    assert (quota.account_ref, quota.bucket, quota.source) == (
        account,
        QuotaBucket.SEVEN_DAY,
        QuotaSource.CODEX_INLINE,
    )
    assert (quota.percent_milli, quota.precision, quota.window_seconds) == (
        6250,
        2,
        604800,
    )
    assert quota.reset_at == datetime.fromtimestamp(1794758400, UTC)
    prior = commit(ledger, batch, first)

    archive = path.with_name("archive-secret.jsonl")
    archive.write_bytes(path.read_bytes())
    path.unlink()
    reopened = Ledger.open(ledger.root, PROJECT)
    (stored,) = reopened.as_of().checkpoints
    assert stored == prior
    archived, replay = read(
        codex, source(registration), codex.CodexState(reopened), stored
    )
    assert replay.revisions == ()
    assert archived.cursor == prior.cursor
    assert replay.provider_checkpoint == prior.provider

    # The provider's child starts independent counters while retaining a root
    # session ID and a parent relationship in the metadata.
    path = archive.with_name("child-secret.jsonl")
    amount = usage(12, 4, 8, 2)
    write(
        path,
        [
            startup(
                checkout,
                id=str(CHILD),
                parent_thread_id=str(SESSION),
                source={
                    "subagent": {
                        "thread_spawn": {"parent_thread_id": str(SESSION), "depth": 1}
                    }
                },
                thread_source="subagent",
                history_mode="paginated",
            ),
            *begin(checkout),
            response("resp_secret", amount, amount, thread=CHILD),
            counter(amount, amount),
            end(),
        ],
    )
    child_source = next(
        entry
        for entry in discover(registration)
        if entry.stream_ref != candidate.stream_ref
    )
    child_batch, child = read(codex, child_source, codex.CodexState(reopened))
    (child_record,) = observations(child)
    assert child_record.tokens == record.tokens
    assert child_record.boundary.epoch_ref != record.boundary.epoch_ref
    assert child_record.boundary.session_ref != record.boundary.session_ref
    assert child.revisions[0].key != first.revisions[0].key
    commit(reopened, child_batch, child)
    for canary in (
        b"resp_secret",
        b"account-secret",
        b"branch-secret",
        b"credits-secret",
        b"checkout-secret",
    ):
        assert canary not in reopened.database_path.read_bytes()


@pytest.mark.parametrize("excluded_counter", [True, False])
def test_excluded_work_cannot_spill_through_fresh_sqlite_restart(
    project, excluded_counter
):
    codex = adapter()
    ledger, registration, path, checkout, outside = project
    other_turn = UUID(int=0x120)
    resumed_turn = UUID(int=0x121)
    rows = [
        startup(checkout),
        *begin(checkout),
        counter(usage(8, 2), usage(8, 2)),
        end(),
        *begin(outside, other_turn),
    ]
    if excluded_counter:
        rows += [counter(usage(60, 10), usage(52, 8))]
    rows += [end(other_turn)]
    write(path, rows)
    candidate = source(registration)
    held = scan(candidate, None, CUTOFF)
    held_frame = next(frame for frame in held.frames if frame.boundary_only)
    candidate = candidate.with_exclusion(held_frame)
    batch, result = read(codex, candidate, codex.CodexState(ledger))
    assert [record.tokens.total_tokens for record in observations(result)] == [10]
    prior = commit(ledger, batch, result)

    new_total, last = usage(66, 11), usage(6, 1)
    write(
        path,
        [
            *begin(checkout, resumed_turn, model="gpt-6.1-sol", effort="low"),
            response("resume-secret", new_total, last, turn=resumed_turn),
            counter(new_total, last),
            end(resumed_turn),
        ],
        append=True,
    )
    reopened = Ledger.open(ledger.root, PROJECT)
    (stored,) = reopened.as_of().checkpoints
    assert stored == prior
    candidate = source(registration)
    held = scan(candidate, stored, CUTOFF)
    candidate = candidate.with_exclusion(held.frames[0])
    resumed, result = read(codex, candidate, codex.CodexState(reopened), stored)
    if excluded_counter:
        (record,) = observations(result)
        assert record.tokens.total_tokens == 7
        assert (record.model, record.effort) == (ModelLabel.GPT_6_1_SOL, Effort.LOW)
    else:
        assert result.revisions == ()
        assert DiagnosticCode.COVERAGE_GAP in {code for _, code in codes(result)}
    commit(reopened, resumed, result, stored)
    assert result.provider_checkpoint.baseline.total_tokens == 77


def test_cutoff_uses_preceding_counter_but_rejects_inflight(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    crossing, later = UUID(int=0x140), UUID(int=0x141)
    write(
        path,
        [
            startup(checkout, BEFORE),
            *begin(checkout, time=BEFORE),
            counter(usage(8, 2), usage(8, 2), BEFORE),
            end(time=BEFORE),
            *begin(checkout, crossing, time=BEFORE),
            counter(usage(16, 4), usage(8, 2)),
            end(crossing),
            *begin(checkout, later),
            counter(usage(24, 6), usage(8, 2)),
            end(later),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    (record,) = observations(result)
    assert record.tokens.total_tokens == 10
    assert (7, DiagnosticCode.COVERAGE_GAP) in codes(result)


def test_truncation_decline_conflicting_response_and_retry_are_gaps(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(12, 4, 8, 2)
    delta = usage(3, 1)
    write(
        path,
        [
            startup(checkout, forked_from_id=str(CHILD)),
            *begin(checkout),
            counter(amount, amount),
            counter(usage(5, 1), usage(5, 1)),
            response("duplicate-secret", usage(15, 5, 8, 2), delta),
            counter(usage(15, 5, 8, 2), delta),
            response("duplicate-secret", usage(18, 6, 8, 2), delta),
            counter(usage(18, 6, 8, 2), delta),
            event("stream_error", message="retry-secret"),
            response("retry-response-secret", usage(21, 7, 8, 2), delta),
            counter(usage(21, 7, 8, 2), delta),
            end(),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    assert [
        (record.tokens.total_tokens, record.availability)
        for record in observations(result)
    ] == [
        (4, Availability.COMPLETE),
        (4, Availability.PARTIAL),
    ]
    assert {
        (3, DiagnosticCode.COVERAGE_GAP),
        (4, DiagnosticCode.COUNTER_REGRESSION),
        (7, DiagnosticCode.IDENTITY_CONFLICT),
        (9, DiagnosticCode.COVERAGE_GAP),
    } <= codes(result)
    assert result.provider_checkpoint.baseline.total_tokens == 28


def marker(codex, ledger, kind=BoundaryKind.REQUEST):
    session = session_reference(ledger, Provider.CODEX, str(SESSION))
    receipt = codex.codex_receipt_reference(ledger, session, COMMAND)
    target = (
        codex.codex_request_boundary_reference(ledger, session, COMMAND)
        if kind is BoundaryKind.REQUEST
        else codex.codex_turn_boundary_reference(ledger, session, str(TURN))
    )
    return ScopeMarker(
        COMMAND,
        Provider.CODEX,
        session,
        1,
        kind,
        target,
        AFTER,
        ItemKey(ItemKind.ISSUE, 88),
        WorkPhase.PLANNING,
        ledger.pseudonymize("participant", "agent-secret"),
        PROJECT,
        receipt_ref=receipt,
    )


def tool_call(ledger, marker_path="/private/tmp/marker.json", *, bind=False):
    cmd = shlex.join(
        [
            "aitm-usage",
            "--project",
            str(ledger.root),
            *(
                ("development", "bind", "--binding")
                if bind
                else ("scope", "mark", "--marker")
            ),
            str(marker_path),
            "--json",
        ]
    )
    args = json.dumps(
        {"cmd": cmd},
        separators=(",", ":"),
    )
    return row(
        "response_item",
        {
            "type": "custom_tool_call",
            "name": "exec",
            "call_id": "call-secret",
            "input": f"const marker = await tools.exec_command({args}); text(marker.output);",
        },
    )


def tool_output(command_id=COMMAND, *, stdout=None):
    receipt = (
        stdout or json.dumps({"command_id": str(command_id), "status": "queued"}) + "\n"
    )
    return row(
        "response_item",
        {
            "type": "custom_tool_call_output",
            "call_id": "call-secret",
            "output": [
                {
                    "type": "input_text",
                    "text": "Script completed\nWall time 0.1 seconds\nOutput:\n",
                },
                {"type": "input_text", "text": receipt},
            ],
        },
    )


@pytest.mark.parametrize(
    "native_output,aligned",
    [
        ("message", True),
        ("reasoning", True),
        ("next-tool", True),
        (None, True),
        ("message", False),
        (None, False),
    ],
)
def test_lookahead_receipt_enrolls_exact_request_and_aggregate_stays_unassigned(
    project,
    monkeypatch,
    capsys,
    native_output,
    aligned,
):
    codex = adapter()
    ledger, registration, path, _, outside = project
    first, last = usage(8, 2), usage(6, 2)
    scope = marker(codex, ledger)
    marker_path = ledger.root / "marker-secret.json"
    marker_path.write_bytes(encode_marker(scope))
    monkeypatch.setenv("CODEX_THREAD_ID", str(SESSION))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aitm-usage",
            "--project",
            str(ledger.root),
            "scope",
            "mark",
            "--marker",
            str(marker_path),
            "--json",
        ],
    )
    assert main() == 0
    stdout = capsys.readouterr().out
    assert json.loads(stdout) == {"command_id": str(COMMAND), "status": "queued"}
    output = {
        "message": {"type": "message", "role": "assistant", "content": []},
        "reasoning": {"type": "reasoning", "summary": []},
        "next-tool": {
            "type": "function_call",
            "call_id": "next-tool-secret",
            "name": "exec_command",
            "arguments": "{}",
        },
    }.get(native_output)
    display_total = usage(14, 4) if aligned else usage(22, 6)
    later_total = usage(22, 6) if aligned else usage(30, 8)
    rows = [
        startup(outside),
        *begin(outside),
        tool_call(ledger, marker_path),
        response("before-marker-secret", first, first),
        tool_output(stdout=stdout),
        counter(first, first),
        *([] if output is None else [row("response_item", output)]),
        response("after-marker-secret", usage(14, 4), last),
        counter(display_total, last),
        counter(later_total, last),
        end(),
    ]
    write(path, rows)
    candidate = source(registration)
    state = codex.CodexState(ledger)
    lookahead, result = read(codex, candidate, state)
    (boundary,) = tuple(
        entry for entry in result.boundaries if entry.receipt_ref == scope.receipt_ref
    )
    assert boundary.ordinal == (7 if output is None else 8)
    assert boundary.boundary_ref == scope.boundary_ref
    assert result.revisions == ()
    assert lookahead.commit_frames == ()
    assert result.provider_checkpoint.baseline is None
    with ledger.writer() as writer:
        drain_inbox(writer, [lookahead.scope_evidence(boundary)])
    view = ledger.as_of()
    (enrollment,) = [
        entry.record
        for entry in view.current
        if isinstance(entry.record, ScopeEnrollment)
    ]
    selected = candidate.with_enrollment(
        enrollment, batch=lookahead, evidence=lookahead.scope_evidence(boundary)
    )
    batch, result = read(codex, selected, state)
    if aligned:
        (request, aggregate) = observations(result)
        assert request.boundary == boundary
        assert request.tokens.total_tokens == 8
    else:
        (aggregate,) = observations(result)
        assert (boundary.ordinal + 1, DiagnosticCode.COVERAGE_GAP) in codes(result)
    assert aggregate.availability is Availability.PARTIAL
    assert aggregate.tokens.total_tokens == 10
    assert aggregate.boundary.stream_ref != boundary.stream_ref
    assert aggregate.boundary.session_ref == boundary.session_ref
    assert aggregate.boundary.receipt_ref is None
    assert aggregate.boundary not in result.boundaries
    commit(ledger, batch, result)
    usage_rollup = rollup(scope.item, ledger.as_of())
    assert usage_rollup.direct.tokens.get("total_tokens", 0) == (8 if aligned else 0)
    assert usage_rollup.inclusive.tokens.get("total_tokens", 0) == (8 if aligned else 0)
    assert usage_rollup.unattributed.tokens["total_tokens"] == 10


@pytest.mark.parametrize("fresh", [True, False])
def test_split_turn_and_tool_receipt_only_survive_post_commit_advance(project, fresh):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    first, second = usage(8, 2), usage(6, 2)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            tool_call(ledger),
            response("before-marker-secret", first, first),
            counter(first, first),
        ],
    )
    state = codex.CodexState(ledger)
    candidate = source(registration)
    batch, result = read(codex, candidate, state)
    prior = commit(ledger, batch, result)
    context = codex.advance_codex_state(state, batch, result)
    write(
        path,
        [
            tool_output(),
            response("after-marker-secret", usage(14, 4), second),
            counter(usage(14, 4), second),
            end(),
        ],
        append=True,
    )
    reopened = Ledger.open(ledger.root, PROJECT)
    (restored,) = reopened.as_of().checkpoints
    assert restored == prior
    if fresh:
        context = codex.CodexState(reopened)
    batch, continuation = read(codex, source(registration), context, restored)
    receipt = marker(codex, reopened).receipt_ref
    if fresh:
        assert not any(
            entry.receipt_ref == receipt for entry in continuation.boundaries
        )
        assert continuation.revisions == ()
        assert DiagnosticCode.COVERAGE_GAP in {code for _, code in codes(continuation)}
    else:
        (record,) = observations(continuation)
        assert record.model is ModelLabel.GPT_6_ASTRA
        assert record.effort is Effort.XHIGH
        assert record.boundary.receipt_ref == receipt
        assert record.tokens.total_tokens == 8
    assert continuation.provider_checkpoint.baseline.total_tokens == 18
    commit(reopened, batch, continuation, restored)


@pytest.mark.parametrize("invalid", [True, 2**63, -1, "12", None])
def test_bad_counter_is_a_bounded_gap(project, invalid):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(12, 4, 8, 2)
    bad = dict(amount, input_tokens=invalid, unrecognized="payload-secret")
    write(path, [startup(checkout), *begin(checkout), counter(bad, amount), end()])
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    assert result.revisions == ()
    assert (3, DiagnosticCode.MALFORMED_USAGE) in codes(result)
    assert "payload-secret" not in repr(result)


def test_decline_inside_excluded_segment_cannot_rebase_eligible_usage(project):
    codex = adapter()
    ledger, registration, path, checkout, outside = project
    other = UUID(int=0x151)
    back = UUID(int=0x152)
    first, lower, repeated = usage(12, 4), usage(6, 2), usage(12, 4)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            counter(first, first),
            end(),
            *begin(outside, other),
            counter(lower, lower),
            end(other),
            *begin(checkout, back),
            counter(repeated, lower),
            end(back),
        ],
    )
    candidate = source(registration)
    batch = scan(candidate, None, CUTOFF)
    held = next(frame for frame in batch.frames if frame.boundary_only)
    _, result = read(codex, candidate.with_exclusion(held), codex.CodexState(ledger))
    assert [record.tokens.total_tokens for record in observations(result)] == [16]
    assert result.provider_checkpoint.baseline == TokenCounts(12, 0, 0, 0, 4, 0)


def test_verified_child_epoch_authenticates_response_after_restart(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    write(
        path,
        [
            startup(
                checkout,
                id=str(CHILD),
                parent_thread_id=str(SESSION),
                source={
                    "subagent": {
                        "thread_spawn": {"parent_thread_id": str(SESSION), "depth": 1}
                    }
                },
                thread_source="subagent",
                history_mode="paginated",
            ),
            *begin(checkout),
            response("child-before", amount, amount, thread=CHILD),
            counter(amount, amount),
            end(),
        ],
    )
    candidate = source(registration)
    batch, result = read(codex, candidate, codex.CodexState(ledger))
    prior = commit(ledger, batch, result)
    later = UUID(int=0x153)
    total = usage(16, 4)
    write(
        path,
        [
            *begin(checkout, later),
            response("child-after", total, amount, turn=later, thread=CHILD),
            counter(total, amount),
            end(later),
        ],
        append=True,
    )
    reopened = Ledger.open(ledger.root, PROJECT)
    _, resumed = read(codex, candidate, codex.CodexState(reopened), prior)
    (record,) = observations(resumed)
    assert record.tokens.total_tokens == 10
    assert record.boundary.epoch_ref == prior.provider.epoch_ref


def test_caller_exclusion_keeps_post_commit_context_advanceable(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    path.write_text(FIXTURE.read_text().replace("CHECKOUT", str(checkout)))
    state = codex.CodexState(ledger)
    batch = scan(source(registration), None, CUTOFF)
    result = codex.read_codex(batch, state, Eligibility.EXCLUDED)
    assert result.revisions == result.quota == ()
    commit(ledger, batch, result)
    advanced = codex.advance_codex_state(state, batch, result)
    assert isinstance(advanced, codex.CodexState)


def test_restarted_repeat_response_is_not_a_second_observation(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            response("duplicated-response", amount, amount),
            counter(amount, amount),
            end(),
        ],
    )
    candidate = source(registration)
    batch, result = read(codex, candidate, codex.CodexState(ledger))
    prior = commit(ledger, batch, result)
    later = UUID(int=0x154)
    total = usage(16, 4)
    write(
        path,
        [
            *begin(checkout, later),
            response("duplicated-response", total, amount, turn=later),
            counter(total, amount),
            end(later),
        ],
        append=True,
    )
    reopened = Ledger.open(ledger.root, PROJECT)
    _, resumed = read(codex, candidate, codex.CodexState(reopened), prior)
    assert resumed.revisions == ()
    assert (8, DiagnosticCode.IDENTITY_CONFLICT) in codes(resumed)


@pytest.mark.parametrize(
    "disproof",
    [
        "unrecognized",
        "mismatched",
        "unpaired",
        "parallel",
        "wrong-owner",
        "wrong-root-turn",
    ],
)
def test_lookahead_cannot_use_unverified_tool_receipt(project, disproof):
    codex = adapter()
    ledger, registration, path, _, outside = project
    amount = usage(8, 2)
    total = usage(16, 4)
    call = tool_call(ledger)
    before = response("before-response", amount, amount)
    after = response("after-response", total, amount)
    output = tool_output()
    intervening = []
    if disproof == "unrecognized":
        call["payload"]["input"] += " text('another action');"
    elif disproof == "mismatched":
        output["payload"]["call_id"] = "wrong-call"
    elif disproof == "unpaired":
        before = event("item_completed")
    elif disproof == "parallel":
        intervening = [
            row("response_item", {"type": "function_call", "call_id": "other-call"})
        ]
    elif disproof == "wrong-owner":
        after["payload"]["thread_id"] = str(CHILD)
    elif disproof == "wrong-root-turn":
        after["payload"]["root_turn_id"] = str(CHILD)
    write(
        path,
        [
            startup(outside),
            *begin(outside),
            call,
            *intervening,
            before,
            output,
            counter(amount, amount),
            after,
            counter(total, amount),
            end(),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    assert result.revisions == ()
    assert not any(boundary.receipt_ref is not None for boundary in result.boundaries)


def test_turn_receipt_requires_the_next_verified_start_in_the_same_segment(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    previous = UUID(int=0x155)
    amount = usage(8, 2)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout, previous),
            tool_call(ledger),
            response("previous", amount, amount, turn=previous),
            tool_output(),
            counter(amount, amount),
            end(previous),
            *begin(checkout),
            counter(usage(16, 4), amount),
            end(),
        ],
    )
    batch, result = read(codex, source(registration), codex.CodexState(ledger))
    scope = marker(codex, ledger, BoundaryKind.TURN)
    (boundary,) = [
        boundary
        for boundary in result.boundaries
        if boundary.kind is BoundaryKind.TURN and boundary.receipt_ref is not None
    ]
    assert boundary.ordinal == 8
    assert boundary.boundary_ref == scope.boundary_ref
    assert batch.scope_evidence(boundary).anchor_ref is not None


@pytest.mark.parametrize(
    "case",
    [
        "missing-account",
        "malformed",
        "malformed-envelope",
        "foreign-id",
        "absent",
        "credits-only",
    ],
)
def test_inline_quota_reports_invalid_or_unverifiable_retained_evidence(project, case):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    rows = [json.loads(line) for line in FIXTURE.read_text().splitlines()]
    rows[0]["payload"]["cwd"] = rows[2]["payload"]["cwd"] = str(checkout)
    counter_payload = rows[4]["payload"]
    account = (
        None
        if case == "missing-account"
        else ledger.pseudonymize("codex-account", "configured")
    )
    if case == "malformed":
        counter_payload["rate_limits"]["primary"]["resets_at"] = 0
    elif case == "malformed-envelope":
        counter_payload["rate_limits"] = "malformed-quota-secret"
    elif case == "foreign-id":
        counter_payload["rate_limits"] = {"limit_id": "foreign-quota-secret"}
    elif case == "absent":
        del counter_payload["rate_limits"]
    elif case == "credits-only":
        counter_payload["rate_limits"]["primary"] = None
    rows.insert(
        3,
        event(
            "thread_settings_applied",
            thread_id=str(SESSION),
            thread_settings={
                "model": "gpt-6-astra",
                "model_provider_id": "openai",
                "service_tier": "default",
            },
        ),
    )
    write(path, rows)
    candidate = source(registration)
    _, result = read(codex, candidate, codex.CodexState(ledger, account))
    (record,) = observations(result)
    assert record.tokens == TokenCounts(12, 8, 0, 0, 4, 2, 16)
    assert record.availability is Availability.COMPLETE
    assert record.processing_tier is ProcessingTier.STANDARD
    assert result.quota == ()
    if case not in ("absent", "credits-only"):
        (gap,) = result.diagnostics
        assert (gap.code, gap.ordinal, gap.provider, gap.source_ref) == (
            DiagnosticCode.COVERAGE_GAP,
            5,
            Provider.CODEX,
            candidate.stream_ref,
        )
        for canary in (
            "credits-secret",
            "malformed-quota-secret",
            "foreign-quota-secret",
        ):
            assert canary not in repr(gap)
    else:
        assert result.diagnostics == ()


@pytest.mark.parametrize("excluded", [False, True])
def test_inline_quota_does_not_leak_from_unadmitted_source(project, excluded):
    codex = adapter()
    ledger, registration, path, _, outside = project
    path.write_text(FIXTURE.read_text().replace("CHECKOUT", str(outside)))
    candidate = source(registration)
    if excluded:
        batch = scan(candidate, None, CUTOFF)
        candidate = candidate.with_exclusion(batch.frames[0])
    batch, result = read(codex, candidate, codex.CodexState(ledger))
    assert bool(batch.commit_frames) is excluded
    assert result.revisions == result.quota == result.diagnostics == ()


def test_usage_remains_measured_when_model_context_is_missing(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    write(
        path,
        [
            startup(checkout),
            event("task_started", turn_id=str(TURN)),
            response("model-unavailable", amount, amount),
            counter(amount, amount),
            end(),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    (record,) = observations(result)
    assert record.availability is Availability.COMPLETE
    assert record.tokens.total_tokens == 10
    assert (record.model, record.effort) == (ModelLabel.UNKNOWN, None)
    assert (3, DiagnosticCode.COVERAGE_GAP) in codes(result)


def test_stored_unqualified_baseline_cannot_establish_a_delta(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    write(path, [startup(checkout), *begin(checkout), counter(amount, amount), end()])
    candidate = source(registration)
    batch, result = read(codex, candidate, codex.CodexState(ledger))
    provider = replace(
        result.provider_checkpoint, baseline=TokenCounts(output_tokens=2)
    )
    prior = SourceCheckpoint(batch.cursor, provider)
    ledger.apply(LedgerBatch(checkpoint=prior))
    later = UUID(int=0x156)
    write(
        path,
        [
            *begin(checkout, later),
            counter(usage(16, 4), amount),
            end(later),
        ],
        append=True,
    )
    _, result = read(codex, candidate, codex.CodexState(ledger), prior)
    assert result.revisions == ()
    assert (7, DiagnosticCode.COVERAGE_GAP) in codes(result)
    assert result.provider_checkpoint.baseline.total_tokens == 20


def test_fresh_process_continuation_checks_only_current_verified_context(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            tool_call(ledger),
            response("before-process-exit", amount, amount),
            counter(amount, amount),
        ],
    )
    candidate = source(registration)
    batch, result = read(codex, candidate, codex.CodexState(ledger))
    commit(ledger, batch, result)
    write(
        path,
        [
            tool_output(),
            response("after-process-exit", usage(16, 4), amount),
            counter(usage(16, 4), amount),
            end(),
        ],
        append=True,
    )
    program = """
import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID
from aitm_usage import ledger as storage
from aitm_usage.ledger import Ledger
from aitm_usage.sources.codex import CodexState, read_codex
from aitm_usage.sources.scan import checkout_anchor_reference, discover, scan
from aitm_usage.types import Eligibility, LedgerBatch, Registration, SourceCheckpoint

state_root, root, anchor = (Path(arg) for arg in sys.argv[1:4])
project_id = UUID(sys.argv[4])
cutoff = datetime.fromisoformat(sys.argv[5])
storage._control_root = lambda: state_root.parent / "control"
ledger = Ledger.open(state_root, project_id)
reg = Registration(project_id, state_root, (root,), (anchor,), cutoff)
source, = discover(reg)
checkpoint, = ledger.as_of().checkpoints
batch = scan(source, checkpoint, cutoff)
result = read_codex(batch, CodexState(ledger), Eligibility.ELIGIBLE)
assert result.revisions == ()
assert all(boundary.receipt_ref is None for boundary in result.boundaries)
assert result.provider_checkpoint.baseline.total_tokens == 20
ledger.apply(LedgerBatch(
    checkpoint=SourceCheckpoint(batch.cursor, result.provider_checkpoint),
    prior_checkpoint=checkpoint,
))
"""
    subprocess.run(
        [
            sys.executable,
            "-c",
            program,
            str(ledger.root),
            str(registration.source_roots[0]),
            str(checkout),
            str(PROJECT),
            CUTOFF.isoformat(),
        ],
        check=True,
    )
    (stored,) = Ledger.open(ledger.root, PROJECT).as_of().checkpoints
    assert stored.provider.baseline.total_tokens == 20
    assert stored.cursor.offset == path.stat().st_size


def test_owner_binding_uses_the_same_serial_cli_proof(project, monkeypatch, capsys):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    scope = replace(
        marker(codex, ledger),
        phase=WorkPhase.DEVELOPMENT,
        attempt_ref=ledger.pseudonymize("attempt", "owner-attempt"),
    )
    binding = DevelopmentBinding(scope, checkout_anchor_reference(ledger, checkout), 1)
    binding_file = ledger.root / "binding-secret.json"
    binding_file.write_bytes(encode_binding(binding))
    monkeypatch.setenv("CODEX_THREAD_ID", str(SESSION))
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "aitm-usage",
            "--project",
            str(ledger.root),
            "development",
            "bind",
            "--binding",
            str(binding_file),
            "--json",
        ],
    )
    assert main() == 0
    stdout = capsys.readouterr().out
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            tool_call(ledger, binding_file, bind=True),
            response("before-bind", amount, amount),
            tool_output(stdout=stdout),
            counter(amount, amount),
            response("after-bind", usage(16, 4), amount),
            counter(usage(16, 4), amount),
            end(),
        ],
    )
    candidate = source(registration)
    state = codex.CodexState(ledger)
    batch, result = read(codex, candidate, state)
    (proof,) = [
        batch.scope_evidence(entry)
        for entry in result.boundaries
        if entry.receipt_ref == scope.receipt_ref
    ]
    assert proof.anchor_ref == binding.anchor_ref
    with ledger.writer() as writer:
        drain_inbox(writer, [proof])
    (enrollment,) = [
        entry.record
        for entry in ledger.as_of().current
        if isinstance(entry.record, ScopeEnrollment)
    ]
    selected = candidate.with_enrollment(enrollment, batch=batch, evidence=proof)
    batch, result = read(codex, selected, state)
    commit(ledger, batch, result)
    totals = rollup(scope.item, ledger.as_of())
    assert totals.direct.tokens["total_tokens"] == 10
    assert totals.unattributed.observation_count == 0


def test_unreconciled_first_snapshot_is_a_baseline_not_an_aggregate(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            counter(usage(80, 20), usage(8, 2)),
            counter(usage(88, 22), usage(8, 2)),
            end(),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    (record,) = observations(result)
    assert record.tokens.total_tokens == 10
    assert (3, DiagnosticCode.COVERAGE_GAP) in codes(result)


def test_repeat_after_unmeasured_excluded_work_reports_coverage(project):
    codex = adapter()
    ledger, registration, path, checkout, outside = project
    outside_turn, returned_turn = UUID(int=0x161), UUID(int=0x162)
    amount = usage(8, 2)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            counter(amount, amount),
            end(),
            *begin(outside, outside_turn),
            end(outside_turn),
            *begin(checkout, returned_turn),
            counter(amount, amount),
            end(returned_turn),
        ],
    )
    candidate = source(registration)
    held = scan(candidate, None, CUTOFF)
    exclude = next(frame for frame in held.frames if frame.boundary_only)
    _, result = read(codex, candidate.with_exclusion(exclude), codex.CodexState(ledger))
    assert [record.tokens.total_tokens for record in observations(result)] == [10]
    assert (10, DiagnosticCode.COVERAGE_GAP) in codes(result)


def test_progress_without_a_response_cannot_skip_duplicate_detection_after_restart(
    project,
):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            response("published-once", amount, amount),
            counter(amount, amount),
            end(),
        ],
    )
    candidate = source(registration)
    batch, result = read(codex, candidate, codex.CodexState(ledger))
    prior = commit(ledger, batch, result)
    later = UUID(int=0x163)
    write(path, begin(checkout, later), append=True)
    reopened = Ledger.open(ledger.root, PROJECT)
    state = codex.CodexState(reopened)
    batch, result = read(codex, candidate, state, prior)
    assert result.revisions == ()
    prior = commit(reopened, batch, result, prior)
    state = codex.advance_codex_state(state, batch, result)
    total = usage(16, 4)
    write(
        path,
        [
            response("published-once", total, amount, turn=later),
            counter(total, amount),
            end(later),
        ],
        append=True,
    )
    _, result = read(codex, candidate, state, prior)
    assert result.revisions == ()
    assert (8, DiagnosticCode.IDENTITY_CONFLICT) in codes(result)


@pytest.mark.parametrize("split", ["new-context", "restart", "unknown-tier"])
def test_configured_processing_tier_is_bound_to_current_context(project, split):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    settings = {
        "thread_id": str(SESSION),
        "thread_settings": {
            "model_provider_id": "openai",
            "model": "gpt-6-astra",
            "service_tier": "default",
        },
    }
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            event("thread_settings_applied", **settings),
            response("standard-config", amount, amount),
            counter(amount, amount),
        ],
    )
    candidate = source(registration)
    state = codex.CodexState(ledger)
    if split == "restart":
        write(path, [end()], append=True)
    batch, first = read(codex, candidate, state)
    (record,) = observations(first)
    assert record.processing_tier is ProcessingTier.STANDARD
    prior = commit(ledger, batch, first)
    later = TURN
    if split == "restart":
        state = codex.CodexState(Ledger.open(ledger.root, PROJECT))
        later = UUID(int=0x164)
        context = begin(checkout, later)
    else:
        state = codex.advance_codex_state(state, batch, first)
        if split == "new-context":
            context = [begin(checkout, model="gpt-6.1-sol", effort="high")[1]]
        else:
            settings["thread_settings"]["service_tier"] = "experimental"
            context = [event("thread_settings_applied", **settings)]
    total = usage(16, 4)
    write(
        path,
        [
            *context,
            response("next-config", total, amount, turn=later),
            counter(total, amount),
            end(later),
        ],
        append=True,
    )
    _, second = read(codex, candidate, state, prior)
    (record,) = observations(second)
    assert record.tokens.total_tokens == 10
    assert record.processing_tier is None


@pytest.mark.parametrize("stale_in", ["excluded", "eligible"])
@pytest.mark.parametrize("restart", [False, True])
def test_stale_quota_counter_cannot_separate_unmeasured_exclusion(
    project, stale_in, restart
):
    codex = adapter()
    ledger, registration, path, checkout, outside = project
    unrelated, returned, later = (UUID(int=value) for value in (0x180, 0x181, 0x182))
    first = usage(8, 2)
    stale = counter(first, first, rate_limits={"limit_id": "codex", "primary": None})
    outside_rows = [*begin(outside, unrelated)]
    returned_rows = [*begin(checkout, returned)]
    (outside_rows if stale_in == "excluded" else returned_rows).append(stale)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            counter(first, first),
            end(),
            *outside_rows,
            end(unrelated),
            *returned_rows,
            end(returned),
        ],
    )
    candidate = source(registration)
    held = scan(candidate, None, CUTOFF)
    candidate = candidate.with_exclusion(
        next(frame for frame in held.frames if frame.boundary_only)
    )
    state = codex.CodexState(ledger)
    batch, result = read(codex, candidate, state)
    assert [record.tokens.total_tokens for record in observations(result)] == [10]
    prior = commit(ledger, batch, result)
    state = (
        codex.CodexState(Ledger.open(ledger.root, PROJECT))
        if restart
        else codex.advance_codex_state(state, batch, result)
    )
    write(
        path,
        [
            *begin(checkout, later),
            counter(first, first, rate_limits={"limit_id": "codex", "secondary": None}),
            counter(usage(14, 3), usage(6, 1)),
            counter(usage(21, 5), usage(7, 2)),
            end(later),
        ],
        append=True,
    )
    _, result = read(codex, candidate, state, prior)
    assert [record.tokens.total_tokens for record in observations(result)] == [9]


@pytest.mark.parametrize("phase", ["excluded", "pre-cutoff", "suppressed"])
@pytest.mark.parametrize("restart", [False, True])
def test_unpublished_response_identity_is_deduplicated_after_commit(
    project, phase, restart
):
    codex = adapter()
    ledger, registration, path, checkout, outside = project
    time = BEFORE if phase == "pre-cutoff" else AFTER
    cwd = outside if phase == "excluded" else checkout
    first = usage(8, 2)
    write(
        path,
        [
            startup(cwd, time),
            *begin(cwd, time=time),
            response("already-observed-secret", first, first, time=time),
            counter(first, first, time=time),
            end(time=time),
        ],
    )
    candidate = source(registration)
    if phase == "excluded":
        batch = scan(candidate, None, CUTOFF)
        candidate = candidate.with_exclusion(batch.frames[0])
    state = codex.CodexState(ledger)
    batch = scan(candidate, None, CUTOFF)
    eligibility = (
        Eligibility.EXCLUDED if phase == "suppressed" else Eligibility.ELIGIBLE
    )
    result = codex.read_codex(batch, state, eligibility)
    assert result.revisions == ()
    (tombstone,) = result.provider_checkpoint.request_prefix
    assert tombstone.ordinal == 3
    assert tombstone.tokens == TokenCounts()
    assert b"already-observed-secret" not in repr(tombstone).encode()
    prior = commit(ledger, batch, result)
    state = (
        codex.CodexState(Ledger.open(ledger.root, PROJECT))
        if restart
        else codex.advance_codex_state(state, batch, result)
    )
    later = UUID(int=0x183)
    total = usage(16, 4)
    write(
        path,
        [
            *begin(checkout, later),
            response("already-observed-secret", total, first, turn=later),
            counter(total, first),
            end(later),
        ],
        append=True,
    )
    _, result = read(codex, candidate, state, prior)
    assert result.revisions == ()
    assert (8, DiagnosticCode.IDENTITY_CONFLICT) in codes(result)


def compaction(record):
    return row(
        "compacted",
        {
            "window_number": 2,
            "first_window_id": str(UUID(int=0x190)),
            "previous_window_id": str(UUID(int=0x190)),
            "window_id": str(UUID(int=0x191)),
            "compaction_response_id": record["payload"]["response_id"],
            "latest_token_usage_record": record["payload"],
            "replacement_history": [{"private_content": "compaction-secret"}],
        },
    )


@pytest.mark.parametrize("split", ["same-batch", "warm", "restart"])
def test_compaction_reconciles_separate_counter_windows(project, split):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    first, compact_amount, next_amount = usage(8, 2), usage(4, 1), usage(6, 1)
    compact_response = response("compaction-response", usage(12, 3), compact_amount)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            response("pre-compaction", first, first),
            counter(first, first),
            compact_response,
            compaction(compact_response),
            row("world_state", {"full": True, "state": {}}),
            begin(checkout)[1],
            event(
                "thread_settings_applied",
                thread_id=str(SESSION),
                thread_settings={
                    "model": "gpt-6-astra",
                    "model_provider_id": "openai",
                    "service_tier": "default",
                },
            ),
            counter(usage(10, 3), first),
            end(),
        ],
    )
    candidate = source(registration)
    state = codex.CodexState(ledger)
    prior = None
    if split != "same-batch":
        batch, result = read(codex, candidate, state)
        assert [
            (record.tokens.total_tokens, record.availability)
            for record in observations(result)
        ] == [(10, Availability.COMPLETE)]
        prior = commit(ledger, batch, result)
        state = (
            codex.CodexState(Ledger.open(ledger.root, PROJECT))
            if split == "restart"
            else codex.advance_codex_state(state, batch, result)
        )
    later = UUID(int=0x184)
    write(
        path,
        [
            *begin(checkout, later),
            response("post-compaction-first", usage(18, 4), next_amount, turn=later),
            counter(usage(16, 4), next_amount),
            response("post-compaction-second", usage(24, 5), next_amount, turn=later),
            counter(usage(22, 5), next_amount),
            end(later),
        ],
        append=True,
    )
    _, result = read(codex, candidate, state, prior)
    projected = [
        (record.tokens.total_tokens, record.availability)
        for record in observations(result)
    ]
    expected = [(7, Availability.COMPLETE), (7, Availability.COMPLETE)]
    if split == "same-batch":
        expected.insert(0, (10, Availability.COMPLETE))
    elif split == "restart":
        expected.pop(0)
    assert projected == expected
    assert "compaction-secret" not in repr(result)


def test_conflicting_reasoning_is_detected_when_last_omits_subset(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    first = usage(8, 2, reasoning=1)
    last = usage(6, 3)
    last.pop("reasoning_output_tokens")
    thread_total = usage(14, 5)
    thread_total.pop("reasoning_output_tokens")
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            response("before-reasoning", first, first),
            counter(first, first),
            response("conflicting-reasoning", thread_total, usage(6, 3, reasoning=2)),
            counter(usage(14, 5, reasoning=2), last),
            end(),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    first_request, second = observations(result)
    assert first_request.availability is Availability.COMPLETE
    assert second.availability is Availability.PARTIAL
    assert second.tokens.reasoning_output_tokens is None
    assert (6, DiagnosticCode.UNRECONCILED_USAGE) in codes(result)


def test_warm_scanner_frontier_keeps_provisional_first_request_output(project):
    codex = adapter()
    ledger, registration, path, _, outside = project
    first, second = usage(8, 2), usage(6, 2)
    write(
        path,
        [
            startup(outside),
            *begin(outside),
            tool_call(ledger),
            response("before-frontier", first, first),
            tool_output(),
            counter(first, first),
            row("response_item", {"type": "reasoning", "summary": []}),
        ],
    )
    candidate = source(registration)
    held = scan(candidate, None, CUTOFF)
    candidate = candidate.with_exclusion(held.frames[0])
    state = codex.CodexState(ledger)
    batch, result = read(codex, candidate, state)
    assert result.revisions == ()
    prior = commit(ledger, batch, result)
    state = codex.advance_codex_state(state, batch, result)
    write(
        path,
        [
            response("after-frontier", usage(14, 4), second),
            counter(usage(14, 4), second),
            end(),
        ],
        append=True,
    )
    scope = marker(codex, ledger)
    batch, result = read(codex, candidate, state, prior)
    (proof,) = [
        batch.scope_evidence(entry)
        for entry in result.boundaries
        if entry.receipt_ref == scope.receipt_ref
    ]
    with ledger.writer() as writer:
        enqueue_marker(ledger.root, scope)
        drain_inbox(writer, [proof])
    (enrollment,) = [
        entry.record
        for entry in ledger.as_of().current
        if isinstance(entry.record, ScopeEnrollment)
    ]
    candidate = candidate.with_enrollment(enrollment, batch=batch, evidence=proof)
    batch, result = read(codex, candidate, state, prior)
    (record,) = observations(result)
    assert record.tokens.total_tokens == 8
    assert record.boundary == proof.boundary


@pytest.mark.parametrize(
    "broken", ["missing-world-state", "contradictory-embedded-turn"]
)
@pytest.mark.parametrize("display", ["decline", "positive"])
def test_unproven_compaction_cannot_allocate_display_change(project, broken, display):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    amount = usage(8, 2)
    compact_record = response("possible-compaction", usage(16, 4), amount)
    witness = compaction(compact_record)
    followup = [row("world_state", {"full": True, "state": {}})]
    if broken == "missing-world-state":
        followup = []
    else:
        witness["payload"]["latest_token_usage_record"] = dict(
            compact_record["payload"], turn_token_usage=usage(1, 1)
        )
    total = usage(6, 1) if display == "decline" else usage(10, 3)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            response("first-display", amount, amount),
            counter(amount, amount),
            compact_record,
            witness,
            *followup,
            begin(checkout)[1],
            event(
                "thread_settings_applied",
                thread_id=str(SESSION),
                thread_settings={
                    "model": "gpt-6-astra",
                    "model_provider_id": "openai",
                    "service_tier": "default",
                },
            ),
            counter(total, amount),
            end(),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    assert [record.tokens.total_tokens for record in observations(result)] == [10]
    if display == "decline":
        assert result.provider_checkpoint.baseline.input_tokens == 8
        assert DiagnosticCode.COUNTER_REGRESSION in {code for _, code in codes(result)}
    else:
        assert DiagnosticCode.COVERAGE_GAP in {code for _, code in codes(result)}


def test_inconsistent_positive_counter_cannot_separate_excluded_activity(project):
    codex = adapter()
    ledger, registration, path, checkout, outside = project
    unrelated, returned = (UUID(int=value) for value in (0x195, 0x196))
    first = usage(8, 2)
    write(
        path,
        [
            startup(checkout),
            *begin(checkout),
            counter(first, first),
            end(),
            *begin(outside, unrelated),
            end(unrelated),
            *begin(checkout, returned),
            counter(usage(12, 3, cache=5), usage(4, 1)),
            counter(usage(18, 5, cache=5), usage(6, 2)),
            counter(usage(24, 7, cache=5), usage(6, 2)),
            end(returned),
        ],
    )
    candidate = source(registration)
    batch = scan(candidate, None, CUTOFF)
    candidate = candidate.with_exclusion(
        next(frame for frame in batch.frames if frame.boundary_only)
    )
    _, result = read(codex, candidate, codex.CodexState(ledger))
    assert [record.tokens.total_tokens for record in observations(result)] == [10, 8]


@pytest.mark.parametrize("aligned", [True, False])
@pytest.mark.parametrize("split", ["same-batch", "warm", "restart"])
def test_activation_frontier_requires_exact_first_eligible_delta(
    project, aligned, split
):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    first = usage(8, 2)
    write(
        path,
        [
            startup(checkout, BEFORE),
            *begin(checkout, time=BEFORE),
            response("before-activation", first, first, time=BEFORE),
            counter(first, first, time=BEFORE),
            end(time=BEFORE),
        ],
    )
    candidate = source(registration)
    state = codex.CodexState(ledger)
    prior = None
    if split != "same-batch":
        batch, result = read(codex, candidate, state)
        assert result.revisions == ()
        prior = commit(ledger, batch, result)
        state = (
            codex.CodexState(Ledger.open(ledger.root, PROJECT))
            if split == "restart"
            else codex.advance_codex_state(state, batch, result)
        )
    later = UUID(int=0x201)
    display = usage(16, 4) if aligned else usage(24, 6)
    wholly_eligible = usage(25, 5) if aligned else usage(33, 7)
    write(
        path,
        [
            *begin(checkout, later),
            response("first-after-activation", usage(16, 4), first, turn=later),
            counter(display, first),
            counter(wholly_eligible, first),
            end(later),
        ],
        append=True,
    )
    batch, result = read(codex, candidate, state, prior)
    expected = [(10, Availability.PARTIAL)]
    if aligned:
        expected.insert(0, (10, Availability.COMPLETE))
    else:
        assert (9, DiagnosticCode.COVERAGE_GAP) in codes(result)
    assert [
        (record.tokens.total_tokens, record.availability)
        for record in observations(result)
    ] == expected
    commit(ledger, batch, result, prior)


def test_delayed_display_increment_without_eligible_response_is_not_allocated(project):
    codex = adapter()
    ledger, registration, path, checkout, _ = project
    first = usage(8, 2)
    later = UUID(int=0x202)
    write(
        path,
        [
            startup(checkout, BEFORE),
            *begin(checkout, time=BEFORE),
            response("only-pre-cutoff-response", first, first, time=BEFORE),
            counter(first, first, time=BEFORE),
            end(time=BEFORE),
            *begin(checkout, later),
            counter(usage(16, 4), first),
            end(later),
        ],
    )
    _, result = read(codex, source(registration), codex.CodexState(ledger))
    assert result.revisions == ()
    assert (8, DiagnosticCode.COVERAGE_GAP) in codes(result)
