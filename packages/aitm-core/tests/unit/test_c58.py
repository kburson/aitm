"""Native timing and draft refusal do not need Git or a filesystem."""

import json
from dataclasses import replace

import pytest

from aitm_core.reviews.anchors import (
    PublicClaim,
    SourceReference,
    SubmittedTurn,
    derive_anchor,
)
from aitm_core.reviews.native import map_native
from aitm_core.reviews.portable import Original, ReviewError

FINGERPRINT = "sha256:" + "a" * 64
MANIFEST = SourceReference("native/review-c58-review-manifest.md", FINGERPRINT)
REVIEWER = SubmittedTurn(
    1, "reviewer", "fixture", FINGERPRINT, "2026-11-08T00:01:00Z", MANIFEST
)
CLAIM = PublicClaim(
    claim_id="claim-public",
    role="reviewer",
    host="fixture",
    session_fingerprint=FINGERPRINT,
    claimed_at="2026-11-08T00:00:30Z",
)


def test_legacy_first_turn_claim_cannot_be_reused_as_round_two_start():
    second = replace(REVIEWER, round=2, submitted_at="2026-11-08T00:02:00Z")
    first = derive_anchor(REVIEWER, None, (CLAIM,), MANIFEST)
    assert first.basis == "claim"
    assert first.claim_id == "claim-public"
    later = derive_anchor(second, REVIEWER, (CLAIM,), MANIFEST)
    assert later.basis == "prior-submit"
    assert later.started_at == REVIEWER.submitted_at
    assert later.source == REVIEWER.source


def test_claim_for_a_different_fingerprint_cannot_establish_start():
    foreign = CLAIM.model_copy(update={"session_fingerprint": "sha256:" + "b" * 64})
    assert derive_anchor(REVIEWER, None, (foreign,), MANIFEST).basis == "unknown"


def test_later_predecessor_cannot_establish_start():
    future = replace(REVIEWER, submitted_at="2026-11-08T00:02:00Z")
    assert derive_anchor(REVIEWER, future, (CLAIM,), MANIFEST).basis == "unknown"


@pytest.mark.parametrize("status", ["draft", "blocked", "round-cap"])
def test_native_nonaccepting_status_refuses_before_any_provenance_is_claimed(status):
    record = {
        "schema": "ai-peer-review.manifest/v1",
        "review_id": "review-c58",
        "status": status,
        "commit_mode": "normal",
        "acceptance_basis": "reviewer-consensus",
        "authority_assurance": "unavailable",
        "artifact_path": "design.md",
        "startup_commit": "a" * 40,
        "final_commit": "a" * 40,
        "artifact_history": [],
        "turns": [],
    }
    source = Original(MANIFEST.path, f"```json\n{json.dumps(record)}\n```\n".encode())
    with pytest.raises(ReviewError, match="unaccepted native manifest"):
        map_native((source,))


def test_ambiguous_exact_turn_claims_have_unknown_start():
    next_response = replace(REVIEWER, round=2, submitted_at="2026-11-08T00:05:00Z")
    first = CLAIM.model_copy(update={"turn": 2, "claimed_at": "2026-11-08T00:02:00Z"})
    second = first.model_copy(
        update={
            "claim_id": "claim-second",
            "claimed_at": "2026-11-08T00:03:00Z",
        }
    )
    result = derive_anchor(next_response, REVIEWER, (first, second), MANIFEST)
    assert (result.basis, result.started_at, result.source) == ("unknown", None, None)


def test_bound_claim_can_precede_another_participants_submit():
    author = replace(REVIEWER, role="author", submitted_at="2026-11-08T00:04:00Z")
    previous = replace(REVIEWER, submitted_at="2026-11-08T00:03:00Z")
    claim = CLAIM.model_copy(
        update={
            "role": "author",
            "turn": 1,
            "claimed_at": "2026-11-08T00:01:00Z",
        }
    )
    result = derive_anchor(author, previous, (claim,), MANIFEST)
    assert result.basis == "claim"
    assert result.started_at == claim.claimed_at


def _timed_turn(start_source, source_digest):
    from aitm_core.reviews.anchors import TimingAnchor
    from aitm_core.reviews.native import NativeTurn
    from aitm_core.reviews.portable import PortableResponse

    predecessor = SourceReference("native/review-c58-author-response-1.md", FINGERPRINT)
    raw_source = SourceReference(
        "native/review-c58-reviewer-response-2.md", FINGERPRINT
    )
    anchor = TimingAnchor("prior-submit", REVIEWER.submitted_at, predecessor)
    submission = replace(
        REVIEWER, round=2, submitted_at="2026-11-08T00:02:00Z", source=raw_source
    )
    header = {
        "schema": "aitm.review-response/v0",
        "level": "xpr",
        "story": 2,
        "role": "reviewer",
        "round": 2,
        "artifact_path": "design.md",
        "artifact_digest": FINGERPRINT,
        "reviewer_session": FINGERPRINT,
        "agent": {
            "provider": "fixture",
            "host": "fixture",
            "model_id": "fixture",
            "effort": "high",
        },
        "session_identity_kind": "native-fingerprint",
        "native_source": raw_source.path,
        "native_source_digest": raw_source.digest,
        "started_at": anchor.started_at,
        "submitted_at": submission.submitted_at,
        "start_basis": "prior-submit",
        "start_source": start_source,
        "start_source_digest": source_digest,
    }
    return (
        PortableResponse.model_validate(header),
        header,
        NativeTurn(
            submission,
            anchor,
            "fixture",
            "fixture",
            "b" * 40,
            "c" * 40,
            FINGERPRINT,
            (),
            (),
        ),
    )


def test_native_predecessor_path_with_exact_hash_qualifies():
    from aitm_core.reviews.native import _bind_turn

    _bind_turn(*_timed_turn("native/review-c58-author-response-1.md", FINGERPRINT))


def test_legacy_predecessor_path_cannot_hide_a_conflicting_hash():
    from aitm_core.reviews.native import _bind_turn

    with pytest.raises(ReviewError, match="start source"):
        _bind_turn(*_timed_turn("author-response-1.md", "sha256:" + "b" * 64))


def test_exact_claim_survives_an_unusable_predecessor_clock():
    future = replace(REVIEWER, submitted_at="2026-11-08T00:02:00Z")
    bound = CLAIM.model_copy(update={"turn": 1})
    result = derive_anchor(REVIEWER, future, (bound,), MANIFEST)
    assert (result.basis, result.started_at) == ("claim", bound.claimed_at)


def test_unqualified_timing_cannot_declare_an_unbound_start():
    from aitm_core.reviews.native import _bind_turn

    response, header, turn = _timed_turn("author-response-1.md", FINGERPRINT)
    response = response.model_copy(update={"start_basis": None})
    with pytest.raises(ReviewError, match="start basis"):
        _bind_turn(response, header, turn)
