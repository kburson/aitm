import importlib
import json
import shlex
import sys
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest
from adapter_frame_cases import AdapterFrames
from scanner_policy_cases import NativeTranscriptFiles, TranscriptReplay
from scanner_policy_cases import transcript_ledger as transcript_ledger
from test_accounting import reference_rates  # noqa: F401, F811
from test_ledger import (
    ledger_path_metadata as ledger_path_metadata,
)
from test_ledger import (
    modules as modules,
)
from test_ledger import (
    observe_ledger_rows as observe_ledger_rows,
)

from aitm_usage.accounting import account_observations
from aitm_usage.cli import main
from aitm_usage.ledger import Ledger
from aitm_usage.rollup import rollup
from aitm_usage.scopes import attest_marker, drain_inbox, session_reference
from aitm_usage.sources import adapter as native
from aitm_usage.sources.scan import discover, scan
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    DiagnosticCode,
    Effort,
    Eligibility,
    ItemKey,
    ItemKind,
    LedgerBatch,
    MarkerDisposition,
    ModelLabel,
    ProcessingTier,
    Provider,
    QuotaBucket,
    QuotaSource,
    Registration,
    Revision,
    ScopeEnrollment,
    ScopeMarker,
    SourceCheckpoint,
    TokenCounts,
    WorkPhase,
    _encode,
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
def adapter_frames():
    return AdapterFrames(Provider.CLAUDE, ClientVersion.CLAUDE_2_1_318, SESSION, CUTOFF)


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


@pytest.fixture
def memory_replay(request, monkeypatch):
    return TranscriptReplay(request, monkeypatch, PROJECT, CUTOFF, durable=False)


def diagnostics(result):
    return {entry.code for entry in result.diagnostics}


def test_claude_revisions_terminal_and_nested_usage(transcript_ledger):
    claude = adapter()
    files, registration, ledger, persisted_rows = transcript_ledger(PROJECT, CUTOFF)
    checkout = files.checkout
    path = files.root / "usage.jsonl"
    rows = [
        json.loads(line)
        for line in FIXTURE.read_text().replace("CHECKOUT", str(checkout)).splitlines()
    ]
    files.write(path, rows[:2])
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

    files.write(path, [rows[2], rows[2]], append=True)
    ledger = Ledger.open(ledger.root, PROJECT)
    second_batch, second = read(claude, candidate, claude.ClaudeState(ledger), prior)
    (r2,) = second.revisions
    assert (r2.key, r2.revision) == (r1.key, 2)
    assert r2.record.boundary == r1.record.boundary
    assert r2.record.observed_at == r1.record.observed_at
    assert r2.record.tokens == TokenCounts(7, 5, 3, 4, 4, 2, 18)
    assert r2.record.availability is Availability.PARTIAL
    prior2 = commit(ledger, second_batch, second, prior)

    files.write(path, [cost(**{MODEL: model_counts()})], append=True)
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
    files.contents[archive] = files.contents.pop(path)
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
        assert all(marker not in row[-1].encode() for row in persisted_rows.history[1])


@pytest.mark.parametrize(
    "mismatch", ["model", "categories", "missing-category", "unfinished"]
)
def test_cost_state_requires_exact_model_categories_and_stop_reason(
    adapter_frames, mismatch
):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    counters = model_counts()
    if mismatch == "categories":
        counters = model_counts(uncached=3, cached=4)
    elif mismatch == "missing-category":
        del counters["cacheCreationEphemeral1hInputTokens"]
    rows = [
        user(checkout),
        request(checkout, stop=None if mismatch == "unfinished" else STOP),
        cost(**{"other-model" if mismatch == "model" else MODEL: counters}),
    ]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(batch, claude.ClaudeState(ledger), Eligibility.ELIGIBLE)
    assert len(result.revisions) == 1
    assert result.revisions[0].record.availability is Availability.PARTIAL
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(result)


def test_stream_conflicts_keep_accepted_prior_and_retry_keeps_own_effort(
    adapter_frames,
):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    rows = [
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
    ]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(batch, claude.ClaudeState(ledger), Eligibility.ELIGIBLE)
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


def test_committed_excluded_and_pre_cutoff_tombstones_survive_reopen(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout, outside = replay.ledger, replay.checkout, replay.outside
    replay.write(
        [
            user(checkout, BEFORE),
            request(checkout, time=BEFORE),
            request(outside, req="req-outside", msg="msg-outside", counts=usage(61)),
            request(checkout, req="req-allowed", msg="msg-allowed", counts=usage(11)),
        ],
    )
    candidate = replay.candidate()
    before = replay.scan(candidate)
    candidate = candidate.with_exclusion(before.frames[2])
    first_batch, first = replay.read(
        claude.read_claude, candidate, claude.ClaudeState(ledger)
    )
    (allowed,) = first.revisions
    assert allowed.record.tokens.output_tokens == 11
    tombstones = [
        p for p in first.provider_checkpoint.request_prefix if p.ordinal in (1, 2)
    ]
    assert len(tombstones) == 2
    assert all(p.tokens == TokenCounts() for p in tombstones)
    prior = replay.commit(first_batch, first)

    replay.write(
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
    ledger = replay.reopen()
    assert ledger.as_of().checkpoints == (prior,)
    _, second = replay.read(
        claude.read_claude, candidate, claude.ClaudeState(ledger), prior
    )
    assert second.revisions == ()
    assert second.provider_checkpoint.baseline is None
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(second)


def test_known_excluded_aggregate_baseline_can_reconcile_single_model(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    replay.write(
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
    _, result = replay.read(
        claude.read_claude, replay.candidate(), claude.ClaudeState(ledger)
    )
    assert result.revisions[-1].record.availability is Availability.COMPLETE
    assert result.revisions[-1].record.tokens.output_tokens == 4
    assert result.provider_checkpoint.baseline == TokenCounts(7, 5, 3, 4, 4, None, 18)
    assert result.provider_checkpoint.request_prefix[0].tokens == TokenCounts()


def test_unadmitted_lookahead_cannot_change_checkpoint_or_usage(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout, outside = replay.ledger, replay.checkout, replay.outside
    replay.write(
        [
            user(checkout),
            request(checkout),
            request(outside, counts=usage(8)),
            cost(**{MODEL: model_counts(output=8)}),
        ],
    )
    batch, result = replay.read(
        claude.read_claude, replay.candidate(), claude.ClaudeState(ledger)
    )
    assert len(batch.sideband) == 1
    assert batch.commit_sideband == ()
    assert result.provider_checkpoint.ordinal == 1
    assert [r.record.tokens.output_tokens for r in result.revisions] == [4]
    assert result.revisions[0].record.availability is Availability.PARTIAL


@pytest.mark.parametrize("account", [True, False])
def test_structured_quota_requires_authenticated_account(adapter_frames, account):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    ref = ledger.pseudonymize("claude-account", str(ACCOUNT)) if account else None
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    rows = [
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
    ]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(
        batch, claude.ClaudeState(ledger, account_ref=ref), Eligibility.ELIGIBLE
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
        "mark",
        "handoff",
        "dispose",
        "trimmed-result",
        "trimmed-native",
        "padded-native",
        "legacy",
        "quoted-flag",
        "wrong-status",
        "duplicate-key",
        "compact-json",
        "extra-lf",
        "mismatched-stdout",
        "not-bash",
        "background",
        "tool-error",
        "stderr",
        "interrupted",
        "missing-call-session",
        "missing-result-session",
        "wrong-result-session",
        "unlinked-request",
    ],
)
def test_monitor_scope_receipt_at_first_claude_request(
    adapter_frames, memory_replay, monkeypatch, case
):
    files = None
    if case in {
        "mark",
        "missing-call-session",
        "missing-result-session",
        "wrong-result-session",
    }:
        files = NativeTranscriptFiles(monkeypatch)
        ledger, transcript_root, checkout = files.source
        path = transcript_root / "native.jsonl"
        if case == "mark":
            ledger = memory_replay.ledger
    elif case == "legacy":
        ledger, checkout = memory_replay.ledger, memory_replay.checkout
    else:
        ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    if files is not None:
        monkeypatch.setattr(native.platform, "system", lambda: "Darwin")
        monkeypatch.setattr(native.platform, "machine", lambda: "arm64")
    action = case if case in {"mark", "handoff", "dispose"} else "mark"
    command = (
        f"aitm-usage monitor scope {action} --request '/private/tmp/a b.json' --json"
    )
    if case == "quoted-flag":
        command = command.replace("--json", "'--json'")
    receipt_id = UUID("00000000-0000-0000-0000-000000000abc")
    receipt = (
        '{"command_id": "00000000-0000-0000-0000-000000000abc", "status": "queued"}\n'
    )
    receipts = {
        "wrong-status": receipt.replace('"queued"', '"unavailable"'),
        "duplicate-key": receipt.replace('"status"', '"status": "queued", "status"'),
        "compact-json": receipt.replace(" ", ""),
        "extra-lf": receipt + "\n",
        "trimmed-native": receipt.removesuffix("\n"),
        "padded-native": " " + receipt.removesuffix("\n"),
    }
    call, output, attachment, telemetry, target = _native_tool_turn(
        checkout, command, receipts.get(case, receipt)
    )
    tool = call["message"]["content"][0]
    result_block = output["message"]["content"][0]
    details = output["toolUseResult"]
    if case == "trimmed-result":
        result_block["content"] = receipt.removesuffix("\n")
    elif case == "mismatched-stdout":
        details["stdout"] = receipt.replace("abc", "abd")
    elif case == "not-bash":
        tool["name"] = "Read"
    elif case == "background":
        tool["input"]["run_in_background"] = True
    elif case == "tool-error":
        result_block["is_error"] = True
    elif case == "stderr":
        details["stderr"] = "failed"
    elif case == "interrupted":
        details["interrupted"] = True
    elif case == "missing-call-session":
        del call["sessionId"]
    elif case == "missing-result-session":
        del output["sessionId"]
    elif case == "wrong-result-session":
        output["sessionId"] = str(UUID(int=0x999))
    elif case == "unlinked-request":
        target["requestRef"] = "unlinked"
    rows = [
        user(checkout),
        call,
        output,
        attachment,
        telemetry,
        target,
        request(
            checkout,
            uuid=str(UUID(int=0x219)),
            parentUuid=target["uuid"],
            isSidechain=False,
            req="req-second",
            msg="msg-second",
        ),
    ]
    if files is not None:
        files.write(path, rows)
    if case == "legacy":
        claude = adapter()
        memory_replay.write(rows)
        _, result = memory_replay.read(
            claude.read_claude,
            memory_replay.candidate(),
            claude.ClaudeState(ledger, SESSION),
        )
        assert not any(boundary.receipt_ref for boundary in result.boundaries)
        assert len(result.revisions) == 3
        return

    if files is None:
        result = adapter_frames.read_monitor(rows, monkeypatch)
    else:
        provider = native.ProviderAdapter()
        root = native.SourceRoot(path.parent, CUTOFF, (checkout,), ledger)
        (locator,) = provider.discover(root)
        result = provider.read_delta(locator, None)
    linked = [item.boundary for item in result.boundaries if item.boundary.receipt_ref]
    if case not in {"mark", "handoff", "dispose", "trimmed-result", "trimmed-native"}:
        assert linked == []
        return
    assert len(linked) == 1
    (boundary,) = linked
    session = session_reference(ledger, Provider.CLAUDE, str(SESSION))
    assert (boundary.kind, boundary.ordinal) == (BoundaryKind.REQUEST, 5)
    assert boundary.receipt_ref == ledger.pseudonymize("scope-receipt", str(receipt_id))
    assert boundary.boundary_ref == ledger.pseudonymize(
        "claude-scope-next-request", f"{session.value}:{receipt_id}"
    )
    assert len(result.observations) == 3
    if case == "mark":
        assert not ledger.as_of().current


@pytest.fixture
def controlled_bash_project(request):
    if request.node.callspec.params["case"] == "valid":
        return request.getfixturevalue("project")
    return None


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
    controlled_bash_project, adapter_frames, request, monkeypatch, capsys, case
):
    claude = adapter()
    project = controlled_bash_project
    replay = None
    policy_admission = case in {"outside", "observation-first", "split"}
    if policy_admission or case in {"wrong-session", "missing-api-session"}:
        replay = request.getfixturevalue("memory_replay")
        ledger = replay.ledger
        checkout = replay.outside if case == "outside" else replay.checkout
    elif project is None:
        ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    else:
        ledger, registration, path, checkout, _ = project
    marker_path = ledger.root / "marker.json"
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
    command = shlex.join(arguments)
    state = claude.ClaudeState(
        ledger, reserved_session_id=None if case == "unreserved" else SESSION
    )
    if project is None and not policy_admission:
        output = json.dumps({"command_id": str(COMMAND), "status": "queued"})

        def read_receipt(command, disproof, state):
            rows = [
                user(checkout),
                *_native_tool_turn(checkout, command, output, case=disproof),
            ]
            if replay is not None:
                replay.write(rows)
                _, result = replay.read(claude.read_claude, replay.candidate(), state)
                return result
            return claude.read_claude(
                adapter_frames.batch(rows), state, Eligibility.ELIGIBLE
            )

        valid_state = claude.ClaudeState(ledger, reserved_session_id=SESSION)
        valid = read_receipt(command, "valid", valid_state)
        assert [b.ordinal for b in valid.boundaries if b.receipt_ref is not None] == [5]
        if case == "shell":
            command += "; printf forged"
        result = read_receipt(command, case, state)
        assert not any(b.receipt_ref is not None for b in result.boundaries)
        return

    session = session_reference(ledger, Provider.CLAUDE, str(SESSION))
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
    queued = {"command_id": str(COMMAND), "status": "queued"}
    if policy_admission:
        output = json.dumps(queued)
    else:
        marker_path.write_bytes(encode_marker(marker))
        marker_path.chmod(0o600)
        monkeypatch.setattr(sys, "argv", arguments)
        assert main() == 0
        output = capsys.readouterr().out.strip()
        assert json.loads(output) == queued

    def load(candidate, state, prior=None):
        if replay is not None:
            return replay.read(claude.read_claude, candidate, state, prior)
        return read(claude, candidate, state, prior)

    rows = [user(checkout), *_native_tool_turn(checkout, command, output, case=case)]
    if policy_admission:
        replay.write(rows[:-1] if case == "split" else rows)
        candidate = replay.candidate()
    else:
        write(path, rows)
        candidate = source(registration)
    prior = None
    if case == "split":
        prefix, partial = load(candidate, state)
        with pytest.raises(ValueError):
            claude.advance_claude_state(state, prefix, partial)
        prior = commit(ledger, prefix, partial)
        state = claude.advance_claude_state(state, prefix, partial)
        replay.write(rows[-1:], append=True)
    batch, result = load(candidate, state, prior)
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
    if policy_admission:
        from test_codex import _admit_replayed_scope

        accepted = _admit_replayed_scope(replay, marker, evidence)
        assert accepted.boundary == boundary
    else:
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
        batch, result = load(candidate, state)
        assert len(result.revisions) == 1
    assert result.revisions[-1].record.boundary == boundary
    if case != "observation-first":
        commit(ledger, batch, result, prior)
    projection = rollup(marker.item, ledger.as_of())
    assert projection.direct.observation_count == 1
    assert projection.unattributed.observation_count == (0 if case == "outside" else 1)


@pytest.mark.parametrize("child", ["matching", "absent", "other-tool", "unlinked"])
def test_nested_agent_report_does_not_double_count_or_inherit_scope(
    memory_replay, child
):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
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
    replay.write(rows)
    batch, result = replay.read(
        claude.read_claude, replay.candidate(), claude.ClaudeState(ledger)
    )
    outputs = [4, 6, 8] if child == "other-tool" else [4, 8]
    assert sorted(r.record.tokens.output_tokens for r in result.revisions) == outputs
    if child != "matching":
        assert DiagnosticCode.OVERLAP_UNVERIFIED in diagnostics(result)
    replay.commit(batch, result)
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
    memory_replay, excluded
):
    claude = adapter()
    replay = memory_replay
    ledger, checkout, outside = replay.ledger, replay.checkout, replay.outside
    call_id = "toolu-agent-late-child"
    parent, completed = str(UUID(int=0x230)), str(UUID(int=0x231))
    replay.write(
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
    candidate = replay.candidate()
    batch, result = replay.read(
        claude.read_claude, candidate, claude.ClaudeState(ledger)
    )
    prior = replay.commit(batch, result)
    replay.write(
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
    ledger = replay.reopen()
    if excluded:
        held = replay.scan(candidate, prior)
        assert held.commit_frames == ()
        candidate = candidate.with_exclusion(held.frames[0])
    batch, result = replay.read(
        claude.read_claude, candidate, claude.ClaudeState(ledger), prior
    )
    if excluded:
        assert len(result.revisions) == 1
        child_prefix = next(
            entry
            for entry in result.provider_checkpoint.request_prefix
            if entry.ordinal == 3
        )
        assert child_prefix.tokens == TokenCounts()
    replay.commit(batch, result, prior=prior)
    item = ItemKey(ItemKind.DRAFT, UUID(int=0x232))
    assert rollup(item, ledger.as_of(1)).unattributed.tokens["output_tokens"] == 12
    assert rollup(item, ledger.as_of()).unattributed.tokens["output_tokens"] == (
        4 if excluded else 12
    )
    assert any(
        revision.revision == 2 and revision.record.tokens == TokenCounts()
        for revision in result.revisions
    )


def test_excluded_streamed_prefix_uses_latest_qualified_counts_once(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    replay.write(
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
    _, result = replay.read(
        claude.read_claude, replay.candidate(), claude.ClaudeState(ledger)
    )
    assert result.provider_checkpoint.baseline == TokenCounts(7, 5, 3, 4, 4, None, 18)
    assert result.revisions[-1].record.availability is Availability.COMPLETE
    assert result.revisions[-1].record.tokens.output_tokens == 4


def test_wrong_provider_model_stays_unknown(adapter_frames):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    rows = [user(checkout), request(checkout, model="gpt-6-astra")]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(batch, claude.ClaudeState(ledger), Eligibility.ELIGIBLE)
    assert result.revisions[0].record.model is ModelLabel.UNKNOWN


def test_incomplete_later_content_does_not_crash_or_change_tool_order(adapter_frames):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
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
    rows = [user(checkout), first, malformed]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(batch, claude.ClaudeState(ledger), Eligibility.ELIGIBLE)
    assert len(result.revisions) == 1


def test_session_pseudonym_is_never_a_quota_account(adapter_frames):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    rows = [
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
    ]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(
        batch,
        claude.ClaudeState(ledger, account_ref=batch.frames[0].session_ref),
        Eligibility.ELIGIBLE,
    )
    assert not result.quota
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


def test_missing_terminal_stays_visible_when_quota_is_present(adapter_frames):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    rows = [
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
    ]
    account = ledger.pseudonymize("claude-account", str(ACCOUNT))
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(
        batch, claude.ClaudeState(ledger, account_ref=account), Eligibility.ELIGIBLE
    )
    assert result.quota
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(result)


@pytest.mark.parametrize("success", [True, False])
def test_structured_result_requires_a_successful_exact_request_prefix(
    memory_replay, success
):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    replay.write(
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
        ]
    )
    batch, result = replay.read(
        claude.read_claude, replay.candidate(), claude.ClaudeState(ledger)
    )
    last = result.revisions[-1]
    assert last.record.availability is (
        Availability.COMPLETE if success else Availability.PARTIAL
    )
    assert last.record.boundary.ordinal == 1
    assert last.revision == (2 if success else 1)
    checkpoint = replay.commit(batch, result)
    assert ledger.as_of().current == (last,)
    payload = _encode(
        LedgerBatch(result.revisions, checkpoint),
        LedgerBatch,
        validate_ref=ledger.validate_source_ref,
    )
    assert "never-persist-result" not in payload


def test_reopen_uses_exact_fixed_prior_view(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    replay.write([user(checkout), request(checkout)])
    candidate = replay.candidate()
    empty = ledger.as_of()
    batch, result = replay.read(
        claude.read_claude, candidate, claude.ClaudeState(ledger, prior_view=empty)
    )
    prior = replay.commit(batch, result)
    replay.write([cost(**{MODEL: model_counts()})], append=True)
    batch = replay.scan(candidate, prior)
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


def test_account_owner_sideband_cannot_change_the_verified_quota_account(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    approved = ledger.pseudonymize("claude-account", str(UUID(int=0x300)))
    reset = int((AFTER + timedelta(hours=1)).timestamp())
    replay.write(
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
    _, result = replay.read(
        claude.read_claude,
        replay.candidate(),
        claude.ClaudeState(ledger, account_ref=approved),
    )
    assert result.quota == ()
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


def test_native_api_start_before_cutoff_cannot_enter_after_restart(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    replay.write(
        [
            user(checkout, BEFORE),
            row("api-request", checkout, BEFORE, id="native-api-before-cutoff"),
        ],
    )
    candidate = replay.candidate()
    first, result = replay.read(
        claude.read_claude, candidate, claude.ClaudeState(ledger)
    )
    assert result.revisions == ()
    prior = replay.commit(first, result)
    replay.write(
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
    ledger = replay.reopen()
    assert ledger.as_of().checkpoints == (prior,)
    _, resumed = replay.read(
        claude.read_claude, candidate, claude.ClaudeState(ledger), prior
    )
    (new,) = resumed.revisions
    assert new.record.boundary.ordinal == 4
    assert all(
        p.tokens == TokenCounts()
        for p in resumed.provider_checkpoint.request_prefix
        if p.ordinal < 4
    )
    payload = _encode(prior, SourceCheckpoint, validate_ref=ledger.validate_source_ref)
    assert "native-api-before-cutoff" not in payload


def test_unknown_model_labels_do_not_merge_conflicting_revisions(memory_replay):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    replay.write(
        [
            user(checkout),
            request(checkout, model="unknown-model-one", counts=usage(3)),
            request(checkout, model="unknown-model-one", counts=usage(4)),
            request(checkout, model="unknown-model-two", counts=usage(5)),
        ]
    )
    batch, result = replay.read(
        claude.read_claude, replay.candidate(), claude.ClaudeState(ledger)
    )
    assert [r.record.tokens.output_tokens for r in result.revisions] == [3, 4]
    assert DiagnosticCode.IDENTITY_CONFLICT in diagnostics(result)
    checkpoint = replay.commit(batch, result)
    payload = _encode(
        LedgerBatch(result.revisions, checkpoint),
        LedgerBatch,
        validate_ref=ledger.validate_source_ref,
    )
    assert "unknown-model-one" not in payload
    assert "unknown-model-two" not in payload


@pytest.mark.parametrize("reopen", [False, True])
@pytest.mark.parametrize("old_owner", [None, ACCOUNT, OTHER_ACCOUNT])
def test_quota_requires_owner_in_current_committed_prefix(
    memory_replay, reopen, old_owner
):
    claude = adapter()
    quota_replay = memory_replay
    ledger, checkout = quota_replay.ledger, quota_replay.checkout
    account = ledger.pseudonymize("claude-account", str(ACCOUNT))
    state = claude.ClaudeState(ledger, account_ref=account)
    quota_replay.write(
        [user(checkout), *([owner(old_owner)] if old_owner is not None else [])]
    )
    candidate = quota_replay.candidate()
    first, result = quota_replay.read(claude.read_claude, candidate, state)
    prior = quota_replay.commit(first, result)
    if reopen:
        state = claude.ClaudeState(quota_replay.reopen(), account_ref=account)
    else:
        state = claude.advance_claude_state(state, first, result)
    quota_replay.write([rate_event(checkout)], append=True)
    batch, result = quota_replay.read(claude.read_claude, candidate, state, prior)
    assert batch.commit_sideband == ()
    assert result.quota == ()
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


def test_later_owner_conflict_invalidates_earlier_quota_in_same_prefix(adapter_frames):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    account = ledger.pseudonymize("claude-account", str(ACCOUNT))
    rows = [user(checkout), owner(), rate_event(checkout), owner(OTHER_ACCOUNT)]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(
        batch, claude.ClaudeState(ledger, account_ref=account), Eligibility.ELIGIBLE
    )
    assert len(batch.commit_sideband) == 2
    assert result.quota == ()
    assert DiagnosticCode.COVERAGE_GAP in diagnostics(result)


@pytest.mark.parametrize("bad_value", [-1, True, None, "0"])
def test_terminal_cannot_convert_an_explicit_invalid_ttl_to_zero(
    adapter_frames, bad_value
):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    counters = model_counts(write5=0, write1=0)
    counters["cacheCreationEphemeral5mInputTokens"] = bad_value
    del counters["cacheCreationEphemeral1hInputTokens"]
    rows = [
        user(checkout),
        request(checkout, counts=usage(write5=0, write1=0)),
        row(
            "result",
            checkout,
            subtype="success",
            is_error=False,
            modelUsage={MODEL: counters},
        ),
    ]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(batch, claude.ClaudeState(ledger), Eligibility.ELIGIBLE)
    (revision,) = result.revisions
    assert revision.record.availability is Availability.PARTIAL
    assert DiagnosticCode.UNRECONCILED_USAGE in diagnostics(result)


def test_terminal_can_infer_both_zero_ttls_from_explicit_zero_write_total(
    adapter_frames,
):
    claude = adapter()
    ledger, checkout = adapter_frames.ledger, adapter_frames.checkout
    counters = model_counts(write5=0, write1=0)
    del counters["cacheCreationEphemeral5mInputTokens"]
    del counters["cacheCreationEphemeral1hInputTokens"]
    rows = [
        user(checkout),
        request(checkout, counts=usage(write5=0, write1=0)),
        row(
            "result",
            checkout,
            subtype="success",
            is_error=False,
            modelUsage={MODEL: counters},
        ),
    ]
    batch = adapter_frames.batch(rows)
    result = claude.read_claude(batch, claude.ClaudeState(ledger), Eligibility.ELIGIBLE)
    assert result.revisions[-1].record.availability is Availability.COMPLETE


def _accounted_replay(claude, replay, candidate, rates, prior=None, *, marker=None):
    ledger = replay.ledger
    state = claude.ClaudeState(ledger, reserved_session_id=SESSION if marker else None)
    batch, result = replay.read(claude.read_claude, candidate, state, prior)
    accounting = account_observations(result, rates, ledger=ledger)
    revisions = accounting.revisions
    if marker is not None:
        (boundary,) = (
            boundary
            for boundary in result.boundaries
            if boundary.receipt_ref == marker.receipt_ref
        )
        evidence = batch.scope_evidence(boundary)
        assert evidence is not None and evidence.anchor_ref is not None
        assert attest_marker(marker, evidence.boundary) is MarkerDisposition.ACCEPTED
        # Supply the accepted scope evidence that the coordinator commits separately.
        enrollment = ScopeEnrollment(marker, evidence.boundary, evidence.anchor_ref)
        key = ledger.pseudonymize("scope-enrollment", str(marker.marker_id))
        revisions = (Revision(key, 1, enrollment), *revisions)
    checkpoint = replay.commit(batch, result, revisions=revisions, prior=prior)
    return result, checkpoint, ledger.as_of().sequence


def _with_processing(counts, metadata):
    counts = counts.copy()
    for key in ("service_tier", "speed", "inference_geo"):
        del counts[key]
    counts.update(metadata)
    return counts


@pytest.mark.parametrize(
    ("processing", "expected_tier", "expected_price"),
    [
        ({"speed": "fast", "inference_geo": "us"}, None, Decimal(0)),
        ({"service_tier": "priority"}, None, Decimal(0)),
        ({"speed": None}, None, Decimal(0)),
        ({"inference_geo": {"unsupported": "private-field"}}, None, Decimal(0)),
        ({}, ProcessingTier.STANDARD, Decimal("0.000136")),
        ({"inference_geo": "global"}, ProcessingTier.STANDARD, Decimal("0.000136")),
    ],
    ids=[
        "fast-us",
        "other-tier",
        "explicit-null",
        "malformed",
        "omitted",
        "sparse-confirmed",
    ],
)
def test_streamed_processing_evidence_controls_accounting_across_restart(
    memory_replay,
    processing,
    expected_tier,
    expected_price,
    reference_rates,  # noqa: F811
):
    claude = adapter()
    transcript = memory_replay
    ledger, checkout = transcript.ledger, transcript.checkout
    transcript.write([user(checkout), request(checkout, counts=usage(3), stop=None)])
    candidate = transcript.candidate()

    def accounted(prior=None):
        return _accounted_replay(claude, transcript, candidate, reference_rates, prior)

    initial, prior, first_sequence = accounted()
    (r1,) = initial.revisions
    assert r1.record.availability is Availability.PARTIAL
    assert r1.record.processing_tier is ProcessingTier.STANDARD

    ledger = transcript.reopen()
    transcript.write(
        [request(checkout, counts=_with_processing(usage(), processing))],
        append=True,
    )
    changed, prior, _ = accounted(prior)
    (r2,) = changed.revisions
    assert (r2.key, r2.revision) == (r1.key, 2)
    assert r2.record.processing_tier is expected_tier
    assert r2.record.boundary == r1.record.boundary
    assert r2.record.tokens == TokenCounts(7, 5, 3, 4, 4, 2, 18)

    ledger = transcript.reopen()
    transcript.write([cost(**{MODEL: model_counts()})], append=True)
    terminal, prior, _ = accounted(prior)
    (r3,) = terminal.revisions
    assert (r3.key, r3.revision) == (r1.key, 3)
    assert r3.record.availability is Availability.COMPLETE
    assert r3.record.processing_tier is expected_tier

    ledger = transcript.reopen()
    transcript.write([request(checkout)], append=True)
    replay, _, _ = accounted(prior)
    assert replay.revisions == ()
    item = ItemKey(ItemKind.DRAFT, UUID(int=0x310))
    before = rollup(item, ledger.as_of(first_sequence)).unattributed
    current = rollup(item, ledger.as_of()).unattributed
    assert before.unknown_price_count == 1
    assert current.tokens["output_tokens"] == 4
    assert current.known_usd == expected_price
    assert current.unknown_price_count == (expected_tier is None)


def test_initial_unproven_processing_stays_unknown_after_standard_revision(
    memory_replay,
    reference_rates,  # noqa: F811
):
    claude = adapter()
    replay = memory_replay
    checkout = replay.checkout
    replay.write(
        [
            user(checkout),
            request(checkout, counts=_with_processing(usage(3), {}), stop=None),
        ]
    )
    candidate = replay.candidate()
    initial, prior, _ = _accounted_replay(claude, replay, candidate, reference_rates)
    assert initial.revisions[0].record.processing_tier is None

    ledger = replay.reopen()
    replay.write([request(checkout), cost(**{MODEL: model_counts()})], append=True)
    result, _, _ = _accounted_replay(claude, replay, candidate, reference_rates, prior)
    assert result.revisions[-1].record.availability is Availability.COMPLETE
    assert all(revision.record.processing_tier is None for revision in result.revisions)
    item = ItemKey(ItemKind.DRAFT, UUID(int=0x310))
    assert rollup(item, ledger.as_of()).unattributed.unknown_price_count == 1


@pytest.mark.parametrize(
    "late_output", [4, 5, 3, True], ids=["unchanged", "increase", "decrease", "invalid"]
)
def test_late_processing_contradiction_revokes_price_with_original_scope(
    memory_replay,
    late_output,
    reference_rates,  # noqa: F811
):
    claude = adapter()
    replay = memory_replay
    ledger, checkout = replay.ledger, replay.checkout
    session = session_reference(ledger, Provider.CLAUDE, str(SESSION))
    item = ItemKey(ItemKind.DRAFT, UUID(int=0x310))
    marker_path = ledger.root / "marker.json"
    marker = ScopeMarker(
        COMMAND,
        Provider.CLAUDE,
        session,
        1,
        BoundaryKind.REQUEST,
        claude.claude_request_boundary_reference(ledger, session, COMMAND),
        AFTER,
        item,
        WorkPhase.PLANNING,
        ledger.pseudonymize("participant", "fixture"),
        PROJECT,
        receipt_ref=claude.claude_receipt_reference(ledger, session, COMMAND),
    )
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
    output = json.dumps({"command_id": str(COMMAND), "status": "queued"})
    rows = _native_tool_turn(checkout, shlex.join(arguments), output)
    replay.write([user(checkout), *rows, cost(**{MODEL: model_counts(8, 4, 10, 6, 8)})])
    candidate = replay.candidate()

    def accounted(prior=None):
        return _accounted_replay(
            claude,
            replay,
            candidate,
            reference_rates,
            prior,
            marker=marker if prior is None else None,
        )

    first, prior, priced_sequence = accounted()
    priced = first.revisions[-1]
    assert priced.record.boundary.receipt_ref == marker.receipt_ref
    assert priced.record.availability is Availability.COMPLETE
    assert rollup(item, ledger.as_of(priced_sequence)).direct.known_usd == Decimal(
        "0.000136"
    )

    ledger = replay.reopen()
    counts = _with_processing(usage(late_output), {"speed": "fast"})
    replay.write(
        [
            request(
                checkout, req="req-next", msg="msg-next", counts=counts, effort="max"
            )
        ],
        append=True,
    )
    result, prior, _ = accounted(prior)
    (downgraded,) = result.revisions
    assert (downgraded.key, downgraded.revision) == (priced.key, priced.revision + 1)
    assert downgraded.record == replace(priced.record, processing_tier=None)
    current = rollup(item, ledger.as_of())
    assert current.direct.known_usd == 0
    assert current.direct.unknown_price_count == 1
    assert current.direct.tokens["output_tokens"] == 4
    assert rollup(item, ledger.as_of(priced_sequence)).direct.known_usd == Decimal(
        "0.000136"
    )

    ledger = replay.reopen()
    replay.write([request(checkout, req="req-next", msg="msg-next")], append=True)
    ordinary, _, _ = accounted(prior)
    assert ordinary.revisions == ()
    assert rollup(item, ledger.as_of()).direct.unknown_price_count == 1
