import json
from dataclasses import replace
from hashlib import sha256
from io import BytesIO
from uuid import UUID

import pytest

from aitm_usage.effort import (
    EffortStore,
    Enrollment,
    Outcome,
    Role,
    UsageReceipt,
)
from aitm_usage.effort.adapters.grok import GrokAdapter
from aitm_usage.effort.capture import CaptureEvent, CaptureGap, recover
from aitm_usage.types import Availability, SourceRef

SESSION = str(UUID(int=10))
ENROLLMENT = Enrollment(UUID(int=1), UUID(int=2), UUID(int=3), Role.WORKER)
MODEL = "grok-4.7-build-fast"
TICKS = 170544001


def ref(kind, value):
    return SourceRef(
        f"hmac-sha256:{sha256(f'{kind}:{value}'.encode()).hexdigest()}:{'0' * 64}"
    )


def row(turn=17, *, ticks=TICKS):
    metrics = dict(
        inputTokens=18639,
        cachedReadTokens=8832,
        cacheCreationTokens=9,
        outputTokens=175,
        reasoningTokens=168,
        totalTokens=18814,
        modelCalls=1,
        costUsdTicks=ticks,
    )
    return dict(
        metrics,
        turnNumber=turn,
        endedAt="2026-11-24T19:52:49.760511+00:00",
        turnCount=1,
        primaryModelId=MODEL,
        modelUsage={MODEL: metrics},
    )


def retained(*turns, session=SESSION):
    return json.dumps({"sessionId": session, "turns": turns}).encode()


def terminal(*, ticks=TICKS, cancelled=False):
    end = {"type": "end", "sessionId": SESSION, "requestId": str(UUID(int=19))}
    if cancelled:
        end.update(stopReason="cancelled", requestId="", usage_is_incomplete=True)
    else:
        end.update(
            stopReason="end_turn",
            num_turns=1,
            total_cost_usd_ticks=ticks,
            usage=dict(
                input_tokens=9798,
                cache_read_input_tokens=8832,
                cache_creation_input_tokens=9,
                output_tokens=175,
                reasoning_tokens=168,
                total_tokens=18814,
            ),
            modelUsage={
                MODEL: {
                    "inputTokens": 9798,
                    "cacheReadInputTokens": 8832,
                    "cacheCreationInputTokens": 9,
                    "outputTokens": 175,
                    "modelCalls": 1,
                }
            },
        )
    return json.dumps(end).encode() + b"\n"


def adapter(current, *, baseline=None):
    return GrokAdapter(
        ENROLLMENT,
        ref("account", "fixture"),
        ref,
        SESSION,
        "1.0.92",
        open_usage=lambda _: BytesIO(current),
        baseline=baseline,
    )


def observe(grok, stdout):
    return grok.observe(CaptureEvent(ENROLLMENT, stdout, b"", frozenset()))


def exact(grok, turn, evidence):
    return recover(
        grok,
        enrollment=ENROLLMENT,
        expected_turn=grok.native_turn(turn),
        evidence=BytesIO(evidence),
    )


def test_fresh_and_configured_exact_recovery_preserve_native_units():
    source = retained(row())
    grok = adapter(source)
    live = observe(grok, terminal())

    assert live == exact(grok, 17, source)
    assert live.model == MODEL
    assert live.request_usage == (live.receipt.tokens,)
    assert live.outcome is Outcome.COMPLETED
    assert live.receipt.coverage is Availability.COMPLETE
    assert live.receipt.tokens.input_tokens == 18639
    assert live.receipt.tokens.total_tokens == 18814
    assert live.receipt.tokens.reasoning_output_tokens == 168
    assert live.receipt.grok_cost_usd_ticks == TICKS
    assert live.receipt.grok_cache_creation_tokens == 9
    assert UsageReceipt.from_json(live.receipt.to_json()) == live.receipt
    assert SESSION not in live.receipt.to_json()


def test_resume_uses_the_only_new_opaque_ordinal_even_with_identical_usage():
    previous, added = row(4), row(17)
    after = retained(previous, added)
    grok = adapter(after, baseline=retained(previous))
    assert observe(grok, terminal()) == exact(grok, 17, retained(added))
    assert observe(grok, terminal()).receipt.turn != grok.native_turn(4)


@pytest.mark.parametrize(
    ("evidence", "baseline"),
    [
        (retained(row(4), row(17)), None),
        (retained(row(4), row(17)), retained(row(4, ticks=TICKS - 1))),
        (retained(row(ticks=TICKS - 1)), None),
        (retained(row(), session=str(UUID(int=11))), None),
    ],
)
def test_conflicting_usage_cannot_create_a_receipt(evidence, baseline):
    assert observe(adapter(evidence, baseline=baseline), terminal()).receipt is None


def test_cancelled_output_without_retained_turn_keeps_a_gap():
    def forbidden(_):
        raise AssertionError("Cancellation cannot guess a retained ordinal")

    grok = replace(adapter(retained()), open_usage=forbidden)
    result = observe(grok, terminal(cancelled=True))
    assert result.outcome is Outcome.INTERRUPTED
    assert result.gap is CaptureGap.MISSING
    assert result.receipt is None


def test_exact_ordinal_refuses_a_different_native_turn():
    grok = adapter(retained(row(17)))
    assert exact(grok, 4, retained(row(17))).gap is CaptureGap.WRONG_TURN


def test_enrollment_authority_is_checked_before_usage_read():
    grok = adapter(retained(row()))
    event = CaptureEvent(
        replace(ENROLLMENT, attempt_id=UUID(int=9)), terminal(), b"", frozenset()
    )
    assert grok.observe(event).gap is CaptureGap.WRONG_ATTEMPT


def settled_grok_usage():
    receipt = observe(adapter(retained(row())), terminal()).receipt
    changed = replace(
        receipt,
        revision=2,
        previous_digest=receipt.digest,
        grok_cost_usd_ticks=TICKS + 1,
    )
    return receipt, changed


def test_reopening_store_preserves_native_ticks_and_refuses_changed_settled_ticks():
    receipt, changed = settled_grok_usage()
    decoded = UsageReceipt.from_json(receipt.to_json())
    assert decoded == receipt
    assert decoded.grok_cost_usd_ticks == TICKS
    assert EffortStore._revision_conflict(decoded, changed) == "revision-usage"


def test_headless_rejects_conflicting_model_breakdown():
    document = json.loads(terminal())
    document["modelUsage"][MODEL]["outputTokens"] = 176

    assert (
        observe(adapter(retained(row())), json.dumps(document).encode() + b"\n").gap
        is CaptureGap.MALFORMED
    )


@pytest.mark.parametrize("conflict", ["swapped", "invalid-retained"])
def test_matching_aggregates_do_not_hide_conflicting_per_model_usage(conflict):
    another = "grok-fixture-second"
    stored = row()
    original = stored["modelUsage"][MODEL]
    stored["modelCalls"] = 2
    stored["modelUsage"] = {
        MODEL: dict(original, outputTokens=100, reasoningTokens=98, totalTokens=18739),
        another: dict.fromkeys(original, 0)
        | {
            "outputTokens": 75,
            "reasoningTokens": 70,
            "totalTokens": 75,
            "modelCalls": 1,
        },
    }
    stdout = json.loads(terminal())
    first = stdout["modelUsage"][MODEL]
    stdout["modelUsage"] = {
        MODEL: dict(first, outputTokens=75),
        another: dict.fromkeys(first, 0) | {"outputTokens": 100, "modelCalls": 1},
    }

    if conflict == "invalid-retained":
        stdout["modelUsage"][MODEL]["outputTokens"] = 100
        stdout["modelUsage"][another]["outputTokens"] = 75
        stored["modelUsage"][MODEL]["reasoningTokens"] = 101
        stored["modelUsage"][another]["reasoningTokens"] = 67
    result = observe(adapter(retained(stored)), json.dumps(stdout).encode() + b"\n")

    assert result.gap is CaptureGap.MALFORMED
    assert result.receipt is None


def test_malformed_completeness_flag_cannot_settle_usage():
    document = json.loads(terminal())
    document["usage_is_incomplete"] = "true"

    result = observe(adapter(retained(row())), json.dumps(document).encode() + b"\n")

    assert result.gap is CaptureGap.MALFORMED
    assert result.receipt is None
