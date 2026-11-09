import importlib
import json
import shlex
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import pytest

from aitm_usage.cli import main
from aitm_usage.ledger import Ledger
from aitm_usage.rollup import rollup
from aitm_usage.scopes import drain_inbox, session_reference
from aitm_usage.sources.scan import discover, scan
from aitm_usage.types import (
    Availability,
    BoundaryKind,
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
    encode_marker,
)

PROJECT = UUID(int=0x200)
SESSION = UUID(int=0x201)
COMMAND = UUID(int=0x202)
ACCOUNT = UUID(int=0x300)
OTHER_ACCOUNT = UUID(int=0x301)
CUTOFF = datetime(2026, 11, 9, 16, tzinfo=UTC)
BEFORE = CUTOFF - timedelta(seconds=1)
AFTER = CUTOFF + timedelta(seconds=10)
FIXTURE = Path(__file__).parent / "fixtures/claude/usage.jsonl"
MODEL = "claude-opus-5-5"
STOP = "end_turn"


def adapter():
    name = "aitm_usage.sources.claude"
    assert importlib.util.find_spec(name) is not None, (
        "U05 must supply the Claude Code adapter"
    )
    return importlib.import_module(name)


@pytest.fixture
def project(tmp_path, monkeypatch):
    base = tmp_path.resolve()
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: base / "control")
    ledger = Ledger.initialize(base / "project", PROJECT)
    root, checkout, outside = (
        base / name for name in ("transcripts", "checkout", "outside")
    )
    for path in (root, checkout, outside):
        path.mkdir()
    return (
        ledger,
        Registration(PROJECT, ledger.root, (root,), (checkout,), CUTOFF),
        root / "local.jsonl",
        checkout,
        outside,
    )


def row(kind, cwd, time=AFTER, **fields):
    return {
        "type": kind,
        "cwd": str(cwd),
        "timestamp": time.isoformat(),
        "sessionId": str(SESSION),
        "version": "2.1.318",
        **fields,
    }


def usage(output=4, *, uncached=2, cached=5, write5=3, write1=4, reasoning=2):
    return {
        "input_tokens": uncached,
        "output_tokens": output,
        "cache_read_input_tokens": cached,
        "cache_creation_input_tokens": write5 + write1,
        "cache_creation": {
            "ephemeral_5m_input_tokens": write5,
            "ephemeral_1h_input_tokens": write1,
        },
        "output_tokens_details": {"thinking_tokens": reasoning},
        "service_tier": "standard",
        "speed": "standard",
        "inference_geo": "global",
    }


def request(
    cwd,
    *,
    req="req-first",
    msg="msg-first",
    counts=None,
    stop=STOP,
    model=MODEL,
    effort="high",
    time=AFTER,
    content=(),
    **extra,
):
    return row(
        "assistant",
        cwd,
        time,
        requestId=req,
        effort=effort,
        perTurnEffort=effort,
        message={
            "type": "message",
            "role": "assistant",
            "id": msg,
            "model": model,
            "usage": usage() if counts is None else counts,
            "stop_reason": stop,
            "content": list(content),
        },
        **extra,
    )


def user(cwd, time=AFTER, **extra):
    return row(
        "user", cwd, time, message={"role": "user", "content": "private"}, **extra
    )


def model_counts(output=4, uncached=2, cached=5, write5=3, write1=4):
    return {
        "inputTokens": uncached,
        "outputTokens": output,
        "cacheReadInputTokens": cached,
        "cacheCreationInputTokens": write5 + write1,
        "cacheCreationEphemeral5mInputTokens": write5,
        "cacheCreationEphemeral1hInputTokens": write1,
    }


def cost(**models):
    return {
        "type": "cost-state",
        "sessionId": str(SESSION),
        "modelUsage": models,
        "startTime": 1794240000000,
        "totalCostUSD": 42,
    }


def owner(account=ACCOUNT):
    return {
        "type": "session-owner",
        "sessionId": str(SESSION),
        "accountUuid": str(account),
    }


def rate_event(checkout):
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    return row(
        "rate_limit_event",
        checkout,
        rate_limit_info={
            "status": "allowed",
            "rateLimitType": "seven_day",
            "resetsAt": reset,
            "utilization": 0.2,
        },
    )


def write(path, rows, *, append=False):
    with path.open("a" if append else "w", encoding="utf-8") as stream:
        for entry in rows:
            stream.write(json.dumps(entry) + "\n")


def source(registration):
    (candidate,) = discover(registration)
    return candidate


def read(claude, candidate, state, prior=None, eligibility=Eligibility.ELIGIBLE):
    batch = scan(candidate, prior, CUTOFF)
    return batch, claude.read_claude(batch, state, eligibility)


def commit(ledger, batch, result, prior=None):
    checkpoint = SourceCheckpoint(batch.cursor, result.provider_checkpoint)
    ledger.apply(LedgerBatch(result.revisions, checkpoint, prior))
    return checkpoint


def diagnostics(result):
    return {entry.code for entry in result.diagnostics}


def test_claude_revisions_terminal_and_nested_usage(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    rows = [
        json.loads(line)
        for line in FIXTURE.read_text().replace("CHECKOUT", str(checkout)).splitlines()
    ]
    write(path, rows[:2])
    candidate = source(registration)
    first_batch, first = read(claude, candidate, claude.ClaudeState(ledger))
    (r1,) = first.revisions
    assert r1.record.availability is Availability.PARTIAL
    assert r1.record.tokens == TokenCounts(7, 5, 3, 4, 1, 1, 15)
    assert r1.record.context_tokens == 14
    assert r1.record.boundary.ordinal == 1
    assert r1.record.model is ModelLabel.CLAUDE_OPUS_5_5
    assert r1.record.effort is Effort.HIGH
    assert r1.record.processing_tier is ProcessingTier.STANDARD
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(first)
    prior = commit(ledger, first_batch, first)

    write(path, [rows[2], rows[2]], append=True)
    ledger = Ledger.open(ledger.root, PROJECT)
    second_batch, second = read(claude, candidate, claude.ClaudeState(ledger), prior)
    (r2,) = second.revisions
    assert (r2.key, r2.revision) == (r1.key, 2)
    assert r2.record.boundary == r1.record.boundary
    assert r2.record.observed_at == r1.record.observed_at
    assert r2.record.tokens == TokenCounts(7, 5, 3, 4, 4, 2, 18)
    assert r2.record.availability is Availability.PARTIAL
    prior2 = commit(ledger, second_batch, second, prior)

    write(path, [cost(**{MODEL: model_counts()})], append=True)
    ledger = Ledger.open(ledger.root, PROJECT)
    third_batch, third = read(claude, candidate, claude.ClaudeState(ledger), prior2)
    assert third_batch.frames == ()
    assert third_batch.observed_through is None
    assert len(third_batch.commit_sideband) == 1
    (r3,) = third.revisions
    assert (r3.key, r3.revision) == (r1.key, 3)
    assert r3.record.boundary == r1.record.boundary
    assert r3.record.tokens == r2.record.tokens
    assert r3.record.observed_at == r1.record.observed_at
    assert r3.record.availability is Availability.COMPLETE
    prior3 = commit(ledger, third_batch, third, prior2)

    archive = path.with_name("verified-copy.jsonl")
    archive.write_bytes(path.read_bytes())
    path.unlink()
    _, replay = read(claude, source(registration), claude.ClaudeState(ledger), prior3)
    assert not replay.revisions
    assert replay.provider_checkpoint == prior3.provider
    assert ledger.as_of(1).current == (r1,)
    assert ledger.as_of().current == (r3,)
    for marker in (
        b"synthetic-private",
        b"req_synthetic",
        b"msg_synthetic",
        b"totalCostUSD",
        str(checkout).encode(),
    ):
        assert marker not in ledger.database_path.read_bytes()


@pytest.mark.parametrize(
    "mismatch", ["model", "categories", "missing-category", "unfinished"]
)
def test_cost_state_requires_exact_model_categories_and_stop_reason(project, mismatch):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    counters = model_counts()
    if mismatch == "categories":
        counters = model_counts(uncached=3, cached=4)
    elif mismatch == "missing-category":
        del counters["cacheCreationEphemeral1hInputTokens"]
    write(
        path,
        [
            user(checkout),
            request(checkout, stop=None if mismatch == "unfinished" else STOP),
            cost(**{"other-model" if mismatch == "model" else MODEL: counters}),
        ],
    )
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert len(result.revisions) == 1
    assert result.revisions[0].record.availability is Availability.PARTIAL
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(result)


def test_stream_conflicts_keep_accepted_prior_and_retry_keeps_own_effort(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(
        path,
        [
            user(checkout),
            request(checkout),
            request(checkout, msg="msg-conflict"),
            request(checkout, req="req-conflict"),
            request(checkout, counts=usage(3)),
            request(checkout, counts=usage(5), model="unsupported-model"),
            request(
                checkout,
                req="req-retry",
                msg="msg-retry",
                model="unapproved-model",
                effort="max",
            ),
        ],
    )
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert [r.record.boundary.ordinal for r in result.revisions] == [1, 6]
    assert [r.record.model for r in result.revisions] == [
        ModelLabel.CLAUDE_OPUS_5_5,
        ModelLabel.UNKNOWN,
    ]
    assert [r.record.effort for r in result.revisions] == [Effort.HIGH, Effort.MAX]
    assert {
        DiagnosticCode.IDENTITY_CONFLICT,
        DiagnosticCode.COUNTER_REGRESSION,
    } <= diagnostics(result)


def test_committed_excluded_and_pre_cutoff_tombstones_survive_reopen(project):
    claude = adapter()
    ledger, registration, path, checkout, outside = project
    write(
        path,
        [
            user(checkout, BEFORE),
            request(checkout, time=BEFORE),
            request(outside, req="req-outside", msg="msg-outside", counts=usage(61)),
            request(checkout, req="req-allowed", msg="msg-allowed", counts=usage(11)),
        ],
    )
    candidate = source(registration)
    before = scan(candidate, None, CUTOFF)
    candidate = candidate.with_exclusion(before.frames[2])
    first_batch, first = read(claude, candidate, claude.ClaudeState(ledger))
    (allowed,) = first.revisions
    assert allowed.record.tokens.output_tokens == 11
    tombstones = [
        p for p in first.provider_checkpoint.request_prefix if p.ordinal in (1, 2)
    ]
    assert len(tombstones) == 2
    assert all(p.tokens == TokenCounts() for p in tombstones)
    prior = commit(ledger, first_batch, first)

    write(
        path,
        [
            request(checkout, counts=usage(71)),
            request(checkout, req="req-outside", msg="msg-outside", counts=usage(81)),
            cost(
                **{
                    MODEL: model_counts(
                        output=163, uncached=6, cached=15, write5=9, write1=12
                    )
                }
            ),
        ],
        append=True,
    )
    ledger = Ledger.open(ledger.root, PROJECT)
    _, second = read(claude, candidate, claude.ClaudeState(ledger), prior)
    assert second.revisions == ()
    assert second.provider_checkpoint.baseline is None
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(second)


def test_known_excluded_aggregate_baseline_can_reconcile_single_model(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(
        path,
        [
            user(checkout, BEFORE),
            request(checkout, time=BEFORE),
            request(checkout, req="post", msg="post-message"),
            cost(
                **{
                    MODEL: model_counts(
                        output=8, uncached=4, cached=10, write5=6, write1=8
                    )
                }
            ),
        ],
    )
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert result.revisions[-1].record.availability is Availability.COMPLETE
    assert result.revisions[-1].record.tokens.output_tokens == 4
    assert result.provider_checkpoint.baseline == TokenCounts(7, 5, 3, 4, 4, None, 18)
    assert result.provider_checkpoint.request_prefix[0].tokens == TokenCounts()


def test_unadmitted_lookahead_cannot_change_checkpoint_or_usage(project):
    claude = adapter()
    ledger, registration, path, checkout, outside = project
    write(
        path,
        [
            user(checkout),
            request(checkout),
            request(outside, counts=usage(8)),
            cost(**{MODEL: model_counts(output=8)}),
        ],
    )
    batch, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert len(batch.sideband) == 1
    assert batch.commit_sideband == ()
    assert result.provider_checkpoint.ordinal == 1
    assert [r.record.tokens.output_tokens for r in result.revisions] == [4]
    assert result.revisions[0].record.availability is Availability.PARTIAL


@pytest.mark.parametrize("account", [True, False])
def test_structured_quota_requires_authenticated_account(project, account):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    ref = ledger.pseudonymize("claude-account", str(ACCOUNT)) if account else None
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    write(
        path,
        [
            user(checkout),
            owner(),
            row(
                "rate_limit_event",
                checkout,
                rate_limit_info={
                    "status": "allowed",
                    "rateLimitType": "five_hour",
                    "resetsAt": reset,
                    "utilization": 0.6725,
                },
            ),
            row(
                "rate_limit_event",
                checkout,
                rate_limit_info={
                    "status": "allowed",
                    "rateLimitType": "seven_day_opus",
                    "resetsAt": reset,
                    "utilization": 0.2,
                },
            ),
            row(
                "rate_limit_event",
                checkout,
                rate_limit_info={
                    "status": "allowed",
                    "rateLimitType": "seven_day",
                    "resetsAt": reset,
                    "utilization": True,
                },
            ),
        ],
    )
    _, result = read(
        claude, source(registration), claude.ClaudeState(ledger, account_ref=ref)
    )
    assert result.revisions == ()
    if account:
        (evidence,) = result.quota
        assert (evidence.account_ref, evidence.bucket, evidence.source) == (
            ref,
            QuotaBucket.FIVE_HOUR,
            QuotaSource.CLAUDE_RATE_LIMIT_EVENT,
        )
        assert (
            evidence.percent_milli,
            evidence.precision,
            evidence.window_seconds,
        ) == (67250, 2, 18000)
        assert evidence.reset_at == datetime.fromtimestamp(reset, UTC)
    else:
        assert result.quota == ()
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


def _native_tool_turn(checkout, command, output, *, case="valid"):
    call_id = "toolu-private-serial"
    assistant_uuid, output_uuid, next_uuid = (
        str(UUID(int=i)) for i in (0x210, 0x211, 0x212)
    )
    call = request(
        checkout,
        uuid=assistant_uuid,
        isSidechain=False,
        stop="tool_use",
        content=[
            {
                "type": "tool_use",
                "id": call_id,
                "name": "Bash",
                "input": {"command": command},
            }
        ],
    )
    result = row(
        "user",
        checkout,
        uuid=output_uuid,
        parentUuid=assistant_uuid,
        sourceToolAssistantUUID=assistant_uuid,
        isSidechain=False,
        message={
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": "unrelated" if case == "unrelated" else call_id,
                    "content": output,
                }
            ],
        },
        toolUseResult={"stdout": output, "stderr": "", "interrupted": False},
    )
    target = request(
        checkout,
        uuid=next_uuid,
        parentUuid=output_uuid,
        isSidechain=False,
        req="req-next",
        msg="msg-next",
        requestRef="native-client-request",
    )
    if case == "wrong-session":
        result["sessionId"] = str(UUID(int=0x999))
    if case == "missing":
        return [call, target]
    if case == "late":
        return [call, target, result]
    if case == "next-turn":
        return [call, result, user(checkout), target]
    attachment_uuid = str(UUID(int=0x213))
    target["parentUuid"] = attachment_uuid
    attachment = row(
        "attachment",
        checkout,
        uuid=attachment_uuid,
        parentUuid=output_uuid,
        isSidechain=False,
        attachment={"type": "output_style", "style": "private"},
    )
    telemetry = row(
        "api-request",
        checkout,
        id="unrelated-client-request"
        if case == "wrong-api-request"
        else "native-client-request",
    )
    if case == "missing-api-session":
        del telemetry["sessionId"]
    if case == "invalid-json":
        bad = "[3, 4]"
        result["message"]["content"][0]["content"] = bad
        result["toolUseResult"]["stdout"] = bad
    if case == "parallel":
        sibling = request(
            checkout,
            uuid=str(UUID(int=0x214)),
            isSidechain=False,
            stop="tool_use",
            content=[
                {"type": "tool_use", "id": "another-tool", "name": "Read", "input": {}}
            ],
        )
        return [sibling, call, result, attachment, telemetry, target]
    return [call, result, attachment, telemetry, target]


@pytest.mark.parametrize(
    "case",
    [
        "valid",
        "missing",
        "unrelated",
        "wrong-api-request",
        "missing-api-session",
        "parallel",
        "invalid-json",
        "outside",
        "observation-first",
        "split",
        "late",
        "wrong-session",
        "next-turn",
        "unreserved",
        "shell",
    ],
)
def test_controlled_native_bash_receipt_sets_exact_next_request(
    project, monkeypatch, capsys, case
):
    claude = adapter()
    ledger, registration, path, checkout, outside = project
    if case == "outside":
        checkout = outside
    session = session_reference(ledger, Provider.CLAUDE, str(SESSION))
    marker_path = ledger.root / "marker.json"
    marker = ScopeMarker(
        COMMAND,
        Provider.CLAUDE,
        session,
        1,
        BoundaryKind.REQUEST,
        claude.claude_request_boundary_reference(ledger, session, COMMAND),
        AFTER,
        ItemKey(ItemKind.DRAFT, UUID(int=0x203)),
        WorkPhase.PLANNING,
        ledger.pseudonymize("participant", "fixture-reviewer"),
        PROJECT,
        receipt_ref=claude.claude_receipt_reference(ledger, session, COMMAND),
    )
    marker_path.write_bytes(encode_marker(marker))
    marker_path.chmod(0o600)
    arguments = [
        "aitm-usage",
        "--project",
        str(ledger.root),
        "scope",
        "mark",
        "--marker",
        str(marker_path),
        "--session-id",
        str(SESSION),
        "--json",
    ]
    monkeypatch.setattr(sys, "argv", arguments)
    assert main() == 0
    output = capsys.readouterr().out.strip()
    assert json.loads(output) == {"command_id": str(COMMAND), "status": "queued"}
    command = shlex.join(arguments) + ("; printf forged" if case == "shell" else "")
    rows = [user(checkout), *_native_tool_turn(checkout, command, output, case=case)]
    write(path, rows[:-1] if case == "split" else rows)
    candidate = source(registration)
    state = claude.ClaudeState(
        ledger, reserved_session_id=None if case == "unreserved" else SESSION
    )
    prior = None
    if case == "split":
        prefix, partial = read(claude, candidate, state)
        with pytest.raises(ValueError):
            claude.advance_claude_state(state, prefix, partial)
        prior = commit(ledger, prefix, partial)
        state = claude.advance_claude_state(state, prefix, partial)
        write(path, rows[-1:], append=True)
    batch, result = read(claude, candidate, state, prior)
    boundaries = [b for b in result.boundaries if b.receipt_ref is not None]
    if case not in ("valid", "outside", "observation-first", "split"):
        assert boundaries == []
        return
    (boundary,) = boundaries
    assert boundary.ordinal == 5
    assert boundary.boundary_ref == marker.boundary_ref
    assert boundary.receipt_ref == marker.receipt_ref
    evidence = batch.scope_evidence(boundary)
    assert evidence is not None
    if case == "observation-first":
        commit(ledger, batch, result)
        before = rollup(marker.item, ledger.as_of())
        assert before.direct.observation_count == 0
        assert before.unattributed.observation_count == 2
    with ledger.writer() as writer:
        drained = drain_inbox(writer, [evidence])
        assert len(drained.receipts) == 1
        assert drained.receipts[0].boundary == boundary
    if case == "outside":
        assert result.revisions == ()
        (enrollment,) = [
            entry.record
            for entry in ledger.as_of().current
            if isinstance(entry.record, ScopeEnrollment)
        ]
        candidate = candidate.with_enrollment(
            enrollment, batch=batch, evidence=evidence
        )
        batch, result = read(claude, candidate, state)
        assert len(result.revisions) == 1
    assert result.revisions[-1].record.boundary == boundary
    if case != "observation-first":
        commit(ledger, batch, result, prior)
    projection = rollup(marker.item, ledger.as_of())
    assert projection.direct.observation_count == 1
    assert projection.unattributed.observation_count == (0 if case == "outside" else 1)


@pytest.mark.parametrize("child", ["matching", "absent", "other-tool", "unlinked"])
def test_nested_agent_report_does_not_double_count_or_inherit_scope(project, child):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    call_id = "toolu-private-agent"
    parent, completed = str(UUID(int=0x220)), str(UUID(int=0x221))
    rows = [
        user(checkout),
        request(
            checkout,
            uuid=parent,
            stop="tool_use",
            isSidechain=False,
            content=[
                {
                    "type": "tool_use",
                    "id": call_id,
                    "name": "Agent",
                    "input": {"description": "private", "prompt": "private"},
                }
            ],
        ),
    ]
    if child != "absent":
        rows.append(
            request(
                checkout,
                req="req-child",
                msg="msg-child",
                counts=usage(6 if child == "other-tool" else 8),
                isSidechain=True,
                parent_tool_use_id={
                    "matching": call_id,
                    "other-tool": "toolu-other-child",
                    "unlinked": None,
                }[child],
            )
        )
    rows.append(
        row(
            "user",
            checkout,
            uuid=completed,
            parentUuid=parent,
            sourceToolAssistantUUID=parent,
            isSidechain=False,
            message={
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": call_id,
                        "content": "private-child-output",
                    }
                ],
            },
            toolUseResult={
                "status": "completed",
                "agentId": "private-agent-id",
                "totalTokens": 22,
                "usage": usage(8),
            },
        )
    )
    write(path, rows)
    batch, result = read(claude, source(registration), claude.ClaudeState(ledger))
    outputs = [4, 6, 8] if child == "other-tool" else [4, 8]
    assert sorted(r.record.tokens.output_tokens for r in result.revisions) == outputs
    if child != "matching":
        assert DiagnosticCode.OVERLAP_UNVERIFIED in diagnostics(result)
    commit(ledger, batch, result)
    projection = rollup(ItemKey(ItemKind.DRAFT, UUID(int=0x203)), ledger.as_of())
    assert projection.inclusive.observation_count == 0
    assert projection.unattributed.observation_count == len(outputs)
    assert all(b.ordinal != len(rows) - 1 for b in result.boundaries)
    if child in ("absent", "other-tool"):
        aggregate = result.revisions[-1].record
        assert aggregate.boundary.stream_ref != batch.cursor.source_ref
        assert aggregate.request_ref is None
        assert aggregate.availability is Availability.PARTIAL


@pytest.mark.parametrize("excluded", [False, True])
def test_a_later_verified_child_removes_overlapping_report_quantities(
    project, excluded
):
    claude = adapter()
    ledger, registration, path, checkout, outside = project
    call_id = "toolu-agent-late-child"
    parent, completed = str(UUID(int=0x230)), str(UUID(int=0x231))
    write(
        path,
        [
            user(checkout),
            request(
                checkout,
                uuid=parent,
                stop="tool_use",
                isSidechain=False,
                content=[
                    {"type": "tool_use", "id": call_id, "name": "Agent", "input": {}}
                ],
            ),
            row(
                "user",
                checkout,
                uuid=completed,
                parentUuid=parent,
                sourceToolAssistantUUID=parent,
                isSidechain=False,
                message={
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": call_id,
                            "content": "private",
                        }
                    ],
                },
                toolUseResult={
                    "status": "completed",
                    "agentId": "private",
                    "usage": usage(8),
                },
            ),
        ],
    )
    candidate = source(registration)
    batch, result = read(claude, candidate, claude.ClaudeState(ledger))
    prior = commit(ledger, batch, result)
    write(
        path,
        [
            request(
                outside if excluded else checkout,
                req="child-late",
                msg="child-late-msg",
                counts=usage(8),
                isSidechain=True,
                parent_tool_use_id=call_id,
            )
        ],
        append=True,
    )
    ledger = Ledger.open(ledger.root, PROJECT)
    if excluded:
        held = scan(candidate, prior, CUTOFF)
        assert held.commit_frames == ()
        candidate = candidate.with_exclusion(held.frames[0])
    batch, result = read(claude, candidate, claude.ClaudeState(ledger), prior)
    if excluded:
        assert len(result.revisions) == 1
        child_prefix = next(
            entry
            for entry in result.provider_checkpoint.request_prefix
            if entry.ordinal == 3
        )
        assert child_prefix.tokens == TokenCounts()
    commit(ledger, batch, result, prior)
    item = ItemKey(ItemKind.DRAFT, UUID(int=0x232))
    assert rollup(item, ledger.as_of(1)).unattributed.tokens["output_tokens"] == 12
    assert rollup(item, ledger.as_of()).unattributed.tokens["output_tokens"] == (
        4 if excluded else 12
    )
    assert any(
        revision.revision == 2 and revision.record.tokens == TokenCounts()
        for revision in result.revisions
    )


def test_excluded_streamed_prefix_uses_latest_qualified_counts_once(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(
        path,
        [
            user(checkout, BEFORE),
            request(checkout, time=BEFORE, counts=usage(3), stop=None),
            request(checkout, time=BEFORE),
            request(checkout, req="later-req", msg="later-msg"),
            cost(
                **{
                    MODEL: model_counts(
                        output=8, uncached=4, cached=10, write5=6, write1=8
                    )
                }
            ),
        ],
    )
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert result.provider_checkpoint.baseline == TokenCounts(7, 5, 3, 4, 4, None, 18)
    assert result.revisions[-1].record.availability is Availability.COMPLETE
    assert result.revisions[-1].record.tokens.output_tokens == 4


def test_wrong_provider_model_stays_unknown(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(path, [user(checkout), request(checkout, model="gpt-6-astra")])
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert result.revisions[0].record.model is ModelLabel.UNKNOWN


def test_incomplete_later_content_does_not_crash_or_change_tool_order(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    call_id = "toolu-genuine"
    first = request(
        checkout,
        uuid=str(UUID(int=0x241)),
        isSidechain=False,
        stop="tool_use",
        content=[{"type": "tool_use", "id": call_id, "name": "Agent", "input": {}}],
    )
    malformed = request(checkout, stop="tool_use")
    del malformed["message"]["content"]
    write(path, [user(checkout), first, malformed])
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert len(result.revisions) == 1


def test_session_pseudonym_is_never_a_quota_account(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    write(
        path,
        [
            user(checkout),
            row(
                "rate_limit_event",
                checkout,
                rate_limit_info={
                    "status": "allowed",
                    "rateLimitType": "seven_day",
                    "resetsAt": reset,
                    "utilization": 0.2,
                },
            ),
        ],
    )
    candidate = source(registration)
    _, result = read(
        claude, candidate, claude.ClaudeState(ledger, account_ref=candidate.session_ref)
    )
    assert not result.quota
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


def test_missing_terminal_stays_visible_when_quota_is_present(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    write(
        path,
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
                    "resetsAt": reset,
                    "utilization": 0.2,
                },
            ),
        ],
    )
    account = ledger.pseudonymize("claude-account", str(ACCOUNT))
    _, result = read(
        claude, source(registration), claude.ClaudeState(ledger, account_ref=account)
    )
    assert result.quota
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(result)


@pytest.mark.parametrize("success", [True, False])
def test_structured_result_requires_a_successful_exact_request_prefix(project, success):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(
        path,
        [
            user(checkout),
            request(checkout),
            row(
                "result",
                checkout,
                subtype="success" if success else "error_during_execution",
                is_error=not success,
                modelUsage={MODEL: model_counts()},
                total_cost_usd=100,
                result="never-persist-result",
            ),
        ],
    )
    batch, result = read(claude, source(registration), claude.ClaudeState(ledger))
    last = result.revisions[-1]
    assert last.record.availability is (
        Availability.COMPLETE if success else Availability.PARTIAL
    )
    assert last.record.boundary.ordinal == 1
    assert last.revision == (2 if success else 1)
    commit(ledger, batch, result)
    assert ledger.as_of().current == (last,)
    assert b"never-persist-result" not in ledger.database_path.read_bytes()


def test_reopen_uses_exact_fixed_prior_view(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(path, [user(checkout), request(checkout)])
    candidate = source(registration)
    empty = ledger.as_of()
    batch, result = read(
        claude, candidate, claude.ClaudeState(ledger, prior_view=empty)
    )
    prior = commit(ledger, batch, result)
    write(path, [cost(**{MODEL: model_counts()})], append=True)
    batch = scan(candidate, prior, CUTOFF)
    with pytest.raises(ValueError, match="fixed prior ledger view"):
        claude.read_claude(
            batch, claude.ClaudeState(ledger, prior_view=empty), Eligibility.ELIGIBLE
        )
    fixed = ledger.as_of()
    final = claude.read_claude(
        batch, claude.ClaudeState(ledger, prior_view=fixed), Eligibility.ELIGIBLE
    )
    assert final.revisions[0].record.availability is Availability.COMPLETE
    assert final.revisions[0].key == fixed.current[0].key
    assert fixed.current[0].record.availability is Availability.PARTIAL


def test_account_owner_sideband_cannot_change_the_verified_quota_account(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    approved = ledger.pseudonymize("claude-account", str(UUID(int=0x300)))
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    write(
        path,
        [
            user(checkout),
            {
                "type": "session-owner",
                "sessionId": str(SESSION),
                "accountUuid": str(UUID(int=0x301)),
            },
            row(
                "rate_limit_event",
                checkout,
                rate_limit_info={
                    "status": "allowed",
                    "unifiedWindows": {
                        "five_hour": {"utilization": 0.625, "resetsAt": reset}
                    },
                },
            ),
        ],
    )
    _, result = read(
        claude, source(registration), claude.ClaudeState(ledger, account_ref=approved)
    )
    assert result.quota == ()
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


def test_native_api_start_before_cutoff_cannot_enter_after_restart(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(
        path,
        [
            user(checkout, BEFORE),
            row("api-request", checkout, BEFORE, id="native-api-before-cutoff"),
        ],
    )
    candidate = source(registration)
    first, result = read(claude, candidate, claude.ClaudeState(ledger))
    assert result.revisions == ()
    prior = commit(ledger, first, result)
    write(
        path,
        [
            request(checkout, requestRef="native-api-before-cutoff"),
            row("api-request", checkout, id="native-api-after-cutoff"),
            request(
                checkout,
                req="req-new",
                msg="msg-new",
                requestRef="native-api-after-cutoff",
            ),
        ],
        append=True,
    )
    ledger = Ledger.open(ledger.root, PROJECT)
    _, resumed = read(claude, candidate, claude.ClaudeState(ledger), prior)
    (new,) = resumed.revisions
    assert new.record.boundary.ordinal == 4
    assert all(
        p.tokens == TokenCounts()
        for p in resumed.provider_checkpoint.request_prefix
        if p.ordinal < 4
    )
    assert b"native-api-before-cutoff" not in ledger.database_path.read_bytes()


def test_unknown_model_labels_do_not_merge_conflicting_revisions(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    write(
        path,
        [
            user(checkout),
            request(checkout, model="unknown-model-one", counts=usage(3)),
            request(checkout, model="unknown-model-one", counts=usage(4)),
            request(checkout, model="unknown-model-two", counts=usage(5)),
        ],
    )
    batch, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert [r.record.tokens.output_tokens for r in result.revisions] == [3, 4]
    assert DiagnosticCode.IDENTITY_CONFLICT in diagnostics(result)
    commit(ledger, batch, result)
    assert b"unknown-model-one" not in ledger.database_path.read_bytes()


@pytest.mark.parametrize("reopen", [False, True])
@pytest.mark.parametrize("old_owner", [None, ACCOUNT, OTHER_ACCOUNT])
def test_quota_requires_owner_in_current_committed_prefix(project, reopen, old_owner):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    account = ledger.pseudonymize("claude-account", str(ACCOUNT))
    state = claude.ClaudeState(ledger, account_ref=account)
    write(
        path, [user(checkout), *([owner(old_owner)] if old_owner is not None else [])]
    )
    candidate = source(registration)
    first, result = read(claude, candidate, state)
    prior = commit(ledger, first, result)
    if reopen:
        ledger = Ledger.open(ledger.root, PROJECT)
        state = claude.ClaudeState(ledger, account_ref=account)
    else:
        state = claude.advance_claude_state(state, first, result)
    write(path, [rate_event(checkout)], append=True)
    batch, result = read(claude, candidate, state, prior)
    assert batch.commit_sideband == ()
    assert result.quota == ()
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


def test_later_owner_conflict_invalidates_earlier_quota_in_same_prefix(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    account = ledger.pseudonymize("claude-account", str(ACCOUNT))
    write(path, [user(checkout), owner(), rate_event(checkout), owner(OTHER_ACCOUNT)])
    batch, result = read(
        claude, source(registration), claude.ClaudeState(ledger, account_ref=account)
    )
    assert len(batch.commit_sideband) == 2
    assert result.quota == ()
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


@pytest.mark.parametrize("bad_value", [-1, True, None, "0"])
def test_terminal_cannot_convert_an_explicit_invalid_ttl_to_zero(project, bad_value):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    counters = model_counts(write5=0, write1=0)
    counters["cacheCreationEphemeral5mInputTokens"] = bad_value
    del counters["cacheCreationEphemeral1hInputTokens"]
    write(
        path,
        [
            user(checkout),
            request(checkout, counts=usage(write5=0, write1=0)),
            row(
                "result",
                checkout,
                subtype="success",
                is_error=False,
                modelUsage={MODEL: counters},
            ),
        ],
    )
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    (revision,) = result.revisions
    assert revision.record.availability is Availability.PARTIAL
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(result)


def test_terminal_can_infer_both_zero_ttls_from_explicit_zero_write_total(project):
    claude = adapter()
    ledger, registration, path, checkout, _ = project
    counters = model_counts(write5=0, write1=0)
    del counters["cacheCreationEphemeral5mInputTokens"]
    del counters["cacheCreationEphemeral1hInputTokens"]
    write(
        path,
        [
            user(checkout),
            request(checkout, counts=usage(write5=0, write1=0)),
            row(
                "result",
                checkout,
                subtype="success",
                is_error=False,
                modelUsage={MODEL: counters},
            ),
        ],
    )
    _, result = read(claude, source(registration), claude.ClaudeState(ledger))
    assert result.revisions[-1].record.availability is Availability.COMPLETE
