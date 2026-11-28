"""C57 policy consumes the already verified C24 byte chain in memory."""

from dataclasses import replace
from hashlib import sha256

import pytest

from aitm_core.documents import _parse
from aitm_core.reviews.policy import ReviewPolicy, ReviewRefusal, validate_review
from aitm_core.reviews.portable import (
    Original,
    PortableManifest,
    PortableResponse,
    ReconstructedReview,
    ReconstructedRound,
)
from aitm_core.reviews.topology import (
    IdentityBinding,
    IdentityMapping,
    IdentityRelation,
    Participant,
    compare_participants,
)

AUTHOR = Participant("recorded-session", "author", "openai")
REVIEWER = Participant("recorded-session", "reviewer", "openai")
FOREIGN = Participant("recorded-session", "foreign", "anthropic")
ALIAS = Participant("native-fingerprint", "reviewer-hash", "OpenAI")
MAPPING = IdentityMapping(
    "fixture session and provider registry",
    (
        IdentityBinding(AUTHOR, "session-a", "openai"),
        IdentityBinding(REVIEWER, "session-b", "openai"),
        IdentityBinding(FOREIGN, "session-c", "anthropic"),
        IdentityBinding(ALIAS, "session-b", "openai"),
    ),
)
POLICY = ReviewPolicy(("declared-manual",), MAPPING)
IDENTITY = b"\nstory: 2\nartifact_path: design.md\n"


def _response(level, role, index, content, claims, session, provider, namespace):
    digest = b"sha256:" + sha256(content).hexdigest().encode()
    header = (
        b"---\nschema: aitm.review-response/v0\nlevel: "
        + level.encode()
        + IDENTITY
        + f"role: {role}\nround: {index}\n".encode()
        + b"artifact_digest: "
        + digest
        + b"\n"
        + f"{role}_session: {session}\n".encode()
        + f"session_identity_kind: {namespace}\n".encode()
        + f"agent: {{host: fixture, provider: {provider}, model_id: model, effort: high}}\n".encode()
    )
    if role == "author":
        header += f"patch: patch-{index:03d}.diff\n".encode()
    attributes, _, body = claims.partition(b"---\n")

    raw = header + attributes + b"---\n" + body
    return PortableResponse.model_validate(_parse(raw).header), Original(
        f"{role}-response-{index}.md", raw
    )


def _record(
    *,
    level="spr",
    outcome="exhausted",
    manifest_claims=b"authority_assurance: declared-manual\n",
    first_reviewer=b"finding_ids: [F1]\n",
    first_author=b"answered_finding_ids: [F1]\n",
    final_reviewer=b"---\n## Decision\n\n**accepted**\n",
    reviewer=REVIEWER,
    final_actor=None,
    final_output=b"reviewed",
):
    base, revised = b"base", b"reviewed"
    manifest_raw = (
        b"---\nschema: aitm.review-manifest/v0\nlevel: "
        + level.encode()
        + IDENTITY
        + f"rounds: 2\noutcome: {outcome}\n".encode()
        + f"base_digest: sha256:{sha256(base).hexdigest()}\n".encode()
        + f"final_digest: sha256:{sha256(final_output).hexdigest()}\n".encode()
        + manifest_claims
        + b"---\n"
    )

    originals = [Original("review-manifest.md", manifest_raw)]
    rounds = []
    for index, input_bytes, output_bytes, review, answer, actor in (
        (1, base, revised, first_reviewer, first_author, reviewer),
        (2, revised, final_output, final_reviewer, b"", final_actor or reviewer),
    ):
        response, response_original = _response(
            level,
            "reviewer",
            index,
            input_bytes,
            review,
            actor.session,
            actor.provider,
            actor.namespace,
        )
        acknowledgement, author_original = _response(
            level,
            "author",
            index,
            output_bytes,
            answer,
            AUTHOR.session,
            AUTHOR.provider,
            AUTHOR.namespace,
        )
        originals.extend((response_original, author_original))
        rounds.append(
            ReconstructedRound(response, acknowledgement, input_bytes, output_bytes)
        )
    return ReconstructedReview(
        PortableManifest.model_validate(_parse(manifest_raw).header),
        base,
        final_output,
        tuple(rounds),
        tuple(originals),
    )


@pytest.mark.parametrize(
    "level, reviewer", [("sar", AUTHOR), ("spr", REVIEWER), ("xpr", FOREIGN)]
)
def test_exhausted_review_binds_the_exact_final_bytes(level, reviewer):
    record = _record(level=level, reviewer=reviewer)
    result = validate_review(record, POLICY)
    assert result.record is record
    assert result.level == level
    assert result.assurance == "declared-manual"


@pytest.mark.parametrize(
    "left, right, expected",
    [
        (REVIEWER, ALIAS, IdentityRelation.SAME),
        (AUTHOR, REVIEWER, IdentityRelation.DISTINCT),
        (AUTHOR, replace(REVIEWER, namespace="unmapped"), IdentityRelation.UNKNOWN),
        (
            REVIEWER,
            replace(REVIEWER, provider="anthropic"),
            IdentityRelation.CONTRADICTORY,
        ),
    ],
)
def test_identity_relation(left, right, expected):
    assert compare_participants(left, right, MAPPING) is expected


@pytest.mark.parametrize(
    "kwargs, reason",
    [
        ({"outcome": "round-cap"}, "outcome"),
        ({"first_author": b""}, "findings"),
        ({"first_author": b"answered_finding_ids: [F1, F2]\n"}, "findings"),
        ({"first_reviewer": b"finding_ids: [F1, F1]\n"}, "findings"),
        ({"final_reviewer": b""}, "decision"),
        ({"final_reviewer": b"---\n## Decision\nrevisions-requested\n"}, "decision"),
        ({"final_reviewer": b"---\n```md\n## Decision\naccepted\n```\n"}, "decision"),
        ({"final_output": b"post-acceptance edit"}, "final bytes"),
        ({"reviewer": AUTHOR}, "SPR"),
        ({"level": "xpr"}, "XPR"),
        ({"level": "sar", "reviewer": FOREIGN}, "SAR"),
        ({"reviewer": replace(REVIEWER, provider="anthropic")}, "contradictory"),
        ({"reviewer": replace(REVIEWER, namespace="unmapped")}, "unknown"),
        ({"final_actor": AUTHOR, "level": "sar"}, "continuity"),
        ({"manifest_claims": b""}, "assurance"),
        (
            {"manifest_claims": b"authority_assurance: independently-attested\n"},
            "assurance",
        ),
        (
            {
                "manifest_claims": b"authority_assurance: declared-manual\ncommit_mode: no-commit\n"
            },
            "commit mode",
        ),
        (
            {
                "manifest_claims": b"authority_assurance: declared-manual\nreviewer_session: author\n"
            },
            "manifest",
        ),
    ],
)
def test_review_policy_refuses_unaccepted_evidence(kwargs, reason):
    with pytest.raises(ReviewRefusal, match=reason):
        validate_review(_record(**kwargs), POLICY)


def test_out_of_order_rounds_are_refused():
    record = _record()
    with pytest.raises(ReviewRefusal, match="round order"):
        validate_review(replace(record, rounds=record.rounds[::-1]), POLICY)


def test_native_unavailable_requires_explicit_policy():
    record = _record(
        level="xpr",
        reviewer=FOREIGN,
        manifest_claims=(
            b"authority_assurance: unavailable\nnative_status: accepted\ncommit_mode: normal\n"
        ),
    )
    with pytest.raises(ReviewRefusal, match="assurance"):
        validate_review(record, POLICY)
    permitted = replace(POLICY, assurances=("native-consensus-authority-unavailable",))
    assert validate_review(record, permitted).assurance == permitted.assurances[0]


def test_decision_hidden_in_a_comment_cannot_accept():
    record = _record(final_reviewer=b"---\n<!--\n## Decision\naccepted\n-->\n")
    with pytest.raises(ReviewRefusal, match="decision"):
        validate_review(record, POLICY)


def test_policy_permits_only_a_declared_replacement():
    record = _record(
        level="sar",
        final_actor=AUTHOR,
        manifest_claims=(
            b"authority_assurance: declared-manual\n"
            b"participant_replacements: [{role: reviewer, round: 2}]\n"
        ),
    )
    with pytest.raises(ReviewRefusal, match="continuity"):
        validate_review(record, POLICY)
    policy = replace(POLICY, allow_participant_replacements=True)
    assert validate_review(record, policy).record is record


def test_distinct_mapped_provider_claims_for_the_same_session_conflict():
    conflicting = replace(
        MAPPING,
        bindings=MAPPING.bindings
        + (IdentityBinding(FOREIGN, "session-b", "anthropic"),),
    )
    assert (
        compare_participants(REVIEWER, FOREIGN, conflicting)
        is IdentityRelation.CONTRADICTORY
    )


def test_typed_decision_cannot_override_a_conflicting_portable_decision():
    record = _record(
        final_reviewer=b"reviewer_decision: accepted\n---\n## Decision\nrevisions-requested\n",
    )
    with pytest.raises(ReviewRefusal, match="contradictory reviewer decision"):
        validate_review(record, POLICY)
