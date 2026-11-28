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
