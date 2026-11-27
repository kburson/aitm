"""Check the typed transaction boundary before a backend receives a write."""

from hashlib import sha256

import pytest
from pydantic import ValidationError

from aitm_core.models.operations import (
    BlobWrite,
    EventAppend,
    FinalizationIntent,
    Operation,
    OperationCategory,
    OperationOwner,
    PreflightOutcome,
    PreflightResult,
    ReadExpectation,
    RelatedWriteSet,
    story_event_path,
)
from tests.unit.test_c04 import BODY, OWNER, POLICY

ATTEMPT_PATH = story_event_path(9)
READ_BODY = ReadExpectation(path=BODY, digest=None)
READ_ATTEMPT = ReadExpectation(path=ATTEMPT_PATH, digest=None)


@pytest.mark.parametrize(
    "binding,generation",
    [
        pytest.param("binding", None, id="no-generation"),
        pytest.param(None, 1, id="no-binding"),
    ],
)
def test_operation_owner_does_not_accept_half_a_binding(binding, generation):
    with pytest.raises(ValidationError, match="binding identity and generation"):
        OperationOwner(actor=OWNER.actor, binding=binding, generation=generation)


def test_passing_preflight_cannot_claim_authority_without_provenance():
    with pytest.raises(ValidationError, match="passing preflight requires"):
        PreflightResult(outcome=PreflightOutcome.PASSED)


def test_two_expectations_for_same_path_cannot_define_a_pinned_view():
    different = READ_BODY.model_copy(update={"digest": POLICY})
    with pytest.raises(ValidationError, match="duplicate read expectation"):
        RelatedWriteSet(read_set=(READ_BODY, different))


def test_two_blob_writes_cannot_compete_for_one_destination():
    with pytest.raises(ValidationError, match="duplicate write destination"):
        RelatedWriteSet(
            read_set=(READ_BODY, READ_ATTEMPT),
            writes=(
                BlobWrite(path=BODY, content=b"add"),
                BlobWrite(path=BODY, content=None),
            ),
        )


def test_multiple_append_batches_cannot_compete_for_one_stream():
    with pytest.raises(ValidationError, match="duplicate write destination"):
        RelatedWriteSet(
            read_set=(READ_ATTEMPT,),
            events=(
                EventAppend(story=9, records=(b"first",)),
                EventAppend(story=9, records=(b"second",)),
            ),
        )


def test_appending_to_a_stream_requires_its_read_precondition():
    with pytest.raises(
        ValidationError, match="each write requires a pinned precondition"
    ):
        RelatedWriteSet(read_set=(), events=(EventAppend(story=9, records=(b"fact",)),))


def test_blob_delete_requires_the_same_pinned_precondition_as_a_write():
    with pytest.raises(
        ValidationError, match="each write requires a pinned precondition"
    ):
        RelatedWriteSet(
            read_set=(), writes=(BlobWrite(path=".aitm/README.md", content=None),)
        )


def test_tracking_the_story_file_does_not_replace_the_attempt_stream_precondition():
    with pytest.raises(
        ValidationError, match="story writes require the pinned attempt stream"
    ):
        RelatedWriteSet(
            read_set=(READ_BODY,), writes=(BlobWrite(path=BODY, content=b"change"),)
        )


def test_blob_write_cannot_replace_an_event_stream():
    with pytest.raises(ValidationError, match="story events require an append"):
        RelatedWriteSet(
            read_set=(READ_ATTEMPT,),
            writes=(BlobWrite(path=ATTEMPT_PATH, content=b"replace"),),
        )


def test_empty_append_batches_are_invalid():
    with pytest.raises(ValidationError, match="records"):
        EventAppend(story=9, records=())


@pytest.fixture
def operation_fields():
    return {
        "operation_id": "edit-9",
        "owner": OWNER,
        "policy_digest": POLICY,
        "category": OperationCategory.NORMAL,
        "intent": FinalizationIntent(
            kind="story.update", version=1, related_preconditions=(), payload=b"{}"
        ),
        "change": RelatedWriteSet(read_set=(READ_BODY, READ_ATTEMPT)),
    }


@pytest.mark.parametrize(
    "related",
    [
        pytest.param(
            ReadExpectation(path=".aitm/stories/000/10/story.md", digest=None),
            id="unread-related-story",
        ),
        pytest.param(
            ReadExpectation(path=BODY, digest=POLICY),
            id="different-version-of-read-blob",
        ),
    ],
)
def test_related_intent_preconditions_must_agree_with_operation_read_set(
    operation_fields, related
):
    operation_fields["intent"] = operation_fields["intent"].model_copy(
        update={"related_preconditions": (related,)}
    )
    with pytest.raises(ValidationError, match="related precondition is not pinned"):
        Operation(**operation_fields)


def test_intent_preserves_explicitly_pinned_related_scope(operation_fields):
    operation_fields["intent"] = operation_fields["intent"].model_copy(
        update={"related_preconditions": (READ_ATTEMPT,)}
    )
    assert Operation(**operation_fields).intent.related_preconditions == (READ_ATTEMPT,)


def test_one_pending_action_identity_cannot_be_enqueued_twice(operation_fields):
    with pytest.raises(ValidationError, match="duplicate pending action identity"):
        Operation(**operation_fields, pending_actions=("readback", "readback"))


def test_read_scope_digest_depends_on_evidence_not_read_order():
    assert (
        RelatedWriteSet(read_set=(READ_BODY, READ_ATTEMPT)).read_set_digest
        == RelatedWriteSet(read_set=(READ_ATTEMPT, READ_BODY)).read_set_digest
    )


def test_read_scope_digest_distinguishes_absent_blob_from_empty_blob():
    empty = READ_BODY.model_copy(update={"digest": sha256(b"").hexdigest()})
    assert (
        RelatedWriteSet(read_set=(READ_BODY,)).read_set_digest
        != RelatedWriteSet(read_set=(empty,)).read_set_digest
    )


@pytest.mark.parametrize(
    "change",
    [
        pytest.param({"policy_digest": "b" * 64}, id="policy-pin"),
        pytest.param({"pending_actions": ("project.readback",)}, id="pending-action"),
        pytest.param(
            {"change": RelatedWriteSet(read_set=(READ_ATTEMPT,))}, id="consulted-scope"
        ),
    ],
)
def test_operation_request_identity_covers_durable_inputs(operation_fields, change):
    original = Operation(**operation_fields)
    updated = Operation(**(operation_fields | change))
    assert updated.request_digest != original.request_digest
