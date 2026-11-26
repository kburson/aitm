import json
from dataclasses import replace
from hashlib import sha256
from io import BytesIO
from uuid import UUID

from aitm_usage.effort import Enrollment, Outcome, Role
from aitm_usage.effort.adapters.claude import ClaudeAdapter
from aitm_usage.effort.capture import CaptureEvent, CaptureGap, recover
from aitm_usage.types import Availability, SourceRef, TokenCounts

SESSION = str(UUID(int=20))
PROMPT = str(UUID(int=21))
ROOT = str(UUID(int=22))
ASSISTANT = str(UUID(int=23))
INTERRUPTION = str(UUID(int=24))
ENROLLMENT = Enrollment(UUID(int=1), UUID(int=2), UUID(int=3), Role.WORKER)
VERSION = "2.1.331"
MODEL = "claude-sonnet-5-5"


def ref(namespace, value):
    digest = sha256(f"{namespace}:{value}".encode()).hexdigest()
    return SourceRef(f"hmac-sha256:{digest}:{'0' * 64}")


def lines(*rows):
    return b"".join(json.dumps(row).encode() + b"\n" for row in rows)


def user():
    return {
        "type": "user",
        "sessionId": SESSION,
        "version": VERSION,
        "entrypoint": "sdk-cli",
        "isSidechain": False,
        "uuid": ROOT,
        "parentUuid": None,
        "promptId": PROMPT,
        "turnPromptId": PROMPT,
        "timestamp": "2026-11-24T18:00:00Z",
    }


def assistant(*, identifier=ASSISTANT, output=11, stop="end_turn"):
    return {
        "type": "assistant",
        "sessionId": SESSION,
        "version": VERSION,
        "entrypoint": "sdk-cli",
        "isSidechain": False,
        "uuid": identifier,
        "parentUuid": ROOT,
        "timestamp": "2026-11-24T18:00:01Z",
        "requestId": "req_fixture",
        "message": {
            "id": "msg_fixture",
            "model": MODEL,
            "stop_reason": stop,
            "usage": {
                "input_tokens": 2,
                "cache_read_input_tokens": 658,
                "cache_creation_input_tokens": 2050,
                "cache_creation": {
                    "ephemeral_5m_input_tokens": 0,
                    "ephemeral_1h_input_tokens": 2050,
                },
                "output_tokens": output,
                "output_tokens_details": {"thinking_tokens": 0},
            },
        },
    }


def interruption():
    return {
        **user(),
        "uuid": INTERRUPTION,
        "parentUuid": ROOT,
        "turnPromptId": None,
        "message": {
            "content": [{"type": "text", "text": "[Request interrupted by user]"}]
        },
    }


def stream(*, row=None, terminal="completed", output=11, user_interrupt=False):
    row = row or assistant()
    witness = (
        {
            "type": "user",
            "session_id": SESSION,
            "uuid": INTERRUPTION,
            "parent_tool_use_id": None,
        }
        if user_interrupt
        else {
            "type": "assistant",
            "session_id": SESSION,
            "uuid": row["uuid"],
            "request_id": row["requestId"],
            "message": row["message"],
            "parent_tool_use_id": None,
        }
    )
    return lines(
        {
            "type": "system",
            "subtype": "init",
            "session_id": SESSION,
            "claude_code_version": VERSION,
        },
        witness,
        {
            "type": "result",
            "session_id": SESSION,
            "terminal_reason": terminal,
            "subtype": "success",
            "is_error": False,
            "usage": {"output_tokens": 0},
            "modelUsage": {MODEL: {"outputTokens": 999}},
            "model_usage_since_last_result": {
                MODEL: {
                    "inputTokens": 2,
                    "cacheReadInputTokens": 658,
                    "cacheCreationInputTokens": 2050,
                    "cacheCreationEphemeral5mInputTokens": 0,
                    "cacheCreationEphemeral1hInputTokens": 2050,
                    "outputTokens": output,
                    "thinkingTokens": 0,
                }
            },
        },
    )


def adapter(transcript):
    return ClaudeAdapter(
        ENROLLMENT,
        ref("account", "fixture"),
        ref,
        SESSION,
        open_transcript=lambda _: BytesIO(transcript),
    )


def observe(claude, stdout):
    return claude.observe(CaptureEvent(ENROLLMENT, stdout, b"", frozenset()))


def test_headless_per_result_and_exact_recovery_are_identical():
    earlier = assistant(identifier=str(UUID(int=30)), output=1, stop=None)
    retained = lines(user(), earlier, assistant())
    claude = adapter(retained)
    completed = observe(claude, stream(row=earlier))
    replay = recover(
        claude,
        enrollment=ENROLLMENT,
        expected_turn=claude.native_turn(PROMPT, surface="print"),
        evidence=BytesIO(retained),
    )

    assert completed == replay
    assert completed.model == MODEL
    assert completed.request_usage == (completed.receipt.tokens,)
    assert completed.outcome is Outcome.COMPLETED
    assert completed.gap is None
    assert completed.receipt.coverage is Availability.COMPLETE
    assert completed.receipt.tokens == TokenCounts(660, 658, 0, 2050, 11, 0, 2721)


def test_headless_cancelled_result_retains_partial_usage():
    retained = lines(user(), assistant(output=8, stop=None), interruption())
    cancelled = observe(
        adapter(retained),
        stream(terminal="aborted_streaming", output=8),
    )

    assert cancelled.gap is None
    assert cancelled.outcome is Outcome.INTERRUPTED
    assert cancelled.receipt.coverage is Availability.PARTIAL
    assert cancelled.receipt.tokens == TokenCounts(660, 658, 0, 2050, 8, 0, 2718)


def test_headless_result_rejects_disagreement_with_final_retained_request():
    observation = observe(adapter(lines(user(), assistant())), stream(output=12))

    assert observation.receipt is None
    assert observation.gap is CaptureGap.MALFORMED


def test_exact_recovery_refuses_an_unrelated_prompt():
    retained = lines(user(), assistant())
    claude = adapter(retained)
    observation = recover(
        claude,
        enrollment=ENROLLMENT,
        expected_turn=claude.native_turn(str(UUID(int=99)), surface="print"),
        evidence=BytesIO(retained),
    )

    assert observation.receipt is None
    assert observation.gap is CaptureGap.WRONG_TURN


def test_cancelled_result_with_no_retained_request_keeps_only_live_numbers():
    retained = lines(user(), interruption())
    claude = adapter(retained)
    live = observe(
        claude, stream(terminal="aborted_streaming", output=8, user_interrupt=True)
    )
    later = recover(
        claude,
        enrollment=ENROLLMENT,
        expected_turn=claude.native_turn(PROMPT, surface="print"),
        evidence=BytesIO(retained),
    )

    assert live.receipt.tokens == TokenCounts(660, 658, 0, 2050, 8, 0, 2718)
    assert later.outcome is Outcome.INTERRUPTED
    assert later.receipt is None
    assert later.gap is CaptureGap.MISSING


def test_headless_unfinished_earlier_request_cannot_make_a_complete_receipt():
    unfinished = assistant(identifier=str(UUID(int=30)), output=2, stop=None)
    unfinished["requestId"] = "req_unfinished"
    unfinished["message"]["id"] = "msg_unfinished"
    unfinished["message"]["usage"].update(
        input_tokens=0,
        cache_read_input_tokens=0,
        cache_creation_input_tokens=0,
        cache_creation={"ephemeral_5m_input_tokens": 0, "ephemeral_1h_input_tokens": 0},
    )
    observation = observe(
        adapter(lines(user(), unfinished, assistant())),
        stream(output=13),
    )

    assert observation.receipt is None
    assert observation.gap is CaptureGap.MALFORMED


def test_armed_adapter_refuses_another_attempt_in_the_same_project():
    claude = adapter(lines(user(), assistant()))
    other = replace(ENROLLMENT, attempt_id=UUID(int=4))
    event = CaptureEvent(other, stream(), b"", frozenset())

    assert claude.observe(event).gap is CaptureGap.WRONG_ATTEMPT


def test_configured_stop_binds_exact_prompt_and_matches_delayed_recovery():
    retained = lines(
        {
            **user(),
            "entrypoint": "cli",
            "turnPosition": {"promptIndex": 1, "turnIndex": 1},
        },
        {**assistant(), "entrypoint": "cli"},
    )
    claude = adapter(retained)
    turn = claude.native_turn(PROMPT, surface="cli")
    notification = json.dumps(
        {
            "hook_event_name": "Stop",
            "session_id": SESSION,
            "prompt_id": PROMPT,
            "stop_hook_active": False,
            "transcript_path": "private-sample-path",
        }
    ).encode()

    live = claude.observe_stop(
        ENROLLMENT, expected_turn=turn, notification=notification
    )
    later = recover(
        claude, enrollment=ENROLLMENT, expected_turn=turn, evidence=BytesIO(retained)
    )

    assert live == later
    assert live.receipt.tokens == TokenCounts(660, 658, 0, 2050, 11, 0, 2721)


def test_stop_for_an_earlier_prompt_cannot_claim_the_armed_prompt():
    claude = adapter(lines(user(), assistant()))
    notification = json.dumps(
        {
            "hook_event_name": "Stop",
            "session_id": SESSION,
            "prompt_id": str(UUID(int=99)),
            "stop_hook_active": False,
        }
    ).encode()

    live = claude.observe_stop(
        ENROLLMENT,
        expected_turn=claude.native_turn(PROMPT, surface="cli"),
        notification=notification,
    )

    assert live.receipt is None
    assert live.gap is CaptureGap.WRONG_TURN


def previous_turn(*, cross_surface=False, reuse_identity=False):
    prompt = str(UUID(int=31))
    root = str(UUID(int=32))
    message = assistant(identifier=str(UUID(int=33)), output=333)
    if not reuse_identity:
        message["requestId"] = "req_prior"
        message["message"]["id"] = "msg_prior"
    profile = {"entrypoint": "cli", "version": "2.1.330"} if cross_surface else {}
    root_record = (
        user() | {"uuid": root, "promptId": prompt, "turnPromptId": prompt} | profile
    )
    return root_record, message | {"parentUuid": root} | profile


def test_resume_counts_only_selected_prompt_in_mixed_native_history():
    prior, prior_result = previous_turn(cross_surface=True)
    target = user() | {"parentUuid": prior_result["uuid"]}
    retained = lines(prior, prior_result, target, assistant())
    claude = adapter(retained)

    live = observe(claude, stream())
    later = recover(
        claude,
        enrollment=ENROLLMENT,
        expected_turn=claude.native_turn(PROMPT, surface="print"),
        evidence=BytesIO(retained),
    )

    assert live == later
    assert later.gap is None
    assert later.receipt.tokens.output_tokens == 11


def test_exact_recovery_rejects_message_claimed_by_two_requests():
    second = assistant(identifier=str(UUID(int=30)))
    second["requestId"] = "req_second"
    retained = lines(user(), assistant(), second)
    claude = adapter(retained)

    result = recover(
        claude,
        enrollment=ENROLLMENT,
        expected_turn=claude.native_turn(PROMPT, surface="print"),
        evidence=BytesIO(retained),
    )

    assert result.receipt is None
    assert result.gap is CaptureGap.WRONG_TURN


def test_exact_recovery_rejects_request_reused_by_two_prompts():
    prior, prior_result = previous_turn(reuse_identity=True)
    retained = lines(prior, prior_result, user(), assistant())
    claude = adapter(retained)

    result = recover(
        claude,
        enrollment=ENROLLMENT,
        expected_turn=claude.native_turn(PROMPT, surface="print"),
        evidence=BytesIO(retained),
    )

    assert result.receipt is None
    assert result.gap is CaptureGap.WRONG_TURN


def test_cancelled_result_cannot_conflict_with_retained_completion():
    result = observe(
        adapter(lines(user(), assistant())), stream(terminal="aborted_streaming")
    )

    assert result.receipt is None
    assert result.gap is CaptureGap.MALFORMED
