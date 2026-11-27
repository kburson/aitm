"""Check retained records, event ownership and quarantine from pinned tree facts."""

import json
from hashlib import sha256
from types import SimpleNamespace

import pytest

from aitm_core.models.common import LocalOutcome
from aitm_core.store.validation import ValidationReport, validate_history
from tests.support.c06 import planning_history

STORE = ".aitm/store.json"
README = ".aitm/README.md"
REPAIR = ".aitm/repairs/verify.json"
EVENTS = ".aitm/stories/000/9/events.jsonl"
OPERATION_ID = "record-before-numbering"
OPERATION = f".aitm/operations/{sha256(OPERATION_ID.encode()).hexdigest()}.json"


@pytest.fixture
def history():
    return planning_history()


def encode(record):
    return json.dumps(record, separators=(",", ":")).encode()


def operation_record(before):
    return {
        "schema_version": "aitm.operation-record/v1",
        "base": before.revision,
        "request_digest": "a" * 64,
        "command": {"operation_id": OPERATION_ID, "local": "completed"},
    }


def event(*, story=9, sequence=1, previous=b"", kind="vendor.test.observed"):
    return encode(
        {
            "v": 1,
            "id": f"event-{sequence}",
            "ts": "2026-11-27T08:00:00Z",
            "type": kind,
            "story": story,
            "operation_id": f"operation-{sequence}",
            "actor": {"kind": "agent", "harness": "history-fixture"},
            "sequence": sequence,
            "prior_log_digest": sha256(previous).hexdigest(),
            "data": {"observation": sequence},
        }
    )


def assert_rejected(report, candidate, prefix, reason):
    assert report.outcome == LocalOutcome.INTEGRITY_ERROR
    assert report.tip == candidate.revision
    assert report.valid_prefix == prefix.revision
    assert report.first_invalid == candidate.revision
    assert reason in report.reason


def test_anchored_store_record_validates(history):
    repo, anchor = history
    candidate = repo.create_commit(
        repo.root,
        {STORE: encode({"schema": "aitm.store/v1", "store_uuid": anchor.store_uuid})},
        "store metadata",
    )
    assert validate_history(
        anchor, candidate.revision, repository=repo
    ) == ValidationReport(
        LocalOutcome.COMPLETED, candidate.revision, valid_prefix=candidate.revision
    )


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        pytest.param(
            b'{"schema":"aitm.store/v1","store_uuid":"other"}',
            "identity or schema disagrees",
            id="unanchored-uuid",
        ),
        pytest.param(
            b'{"schema":"aitm.alternate-store/v1","store_uuid":"c06-fixture"}',
            "identity or schema disagrees",
            id="other-v1-schema",
        ),
        pytest.param(
            b'{"schema":"aitm.store/v1","store_uuid":"other","store_uuid":"c06-fixture"}',
            "duplicate planning field: store_uuid",
            id="ambiguous-identity",
        ),
        pytest.param(
            b'[{"schema":"aitm.store/v1","store_uuid":"c06-fixture"}]',
            "expected a planning object",
            id="array-instead-of-record",
        ),
    ],
)
def test_store_record_refusal_retains_last_valid_tree(history, content, reason):
    repo, anchor = history
    before = repo.create_commit(repo.root, {README: b"anchored documentation"}, "valid")
    candidate = repo.create_commit(before, {STORE: content}, "malformed store record")
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        before,
        reason,
    )


def test_pre_story_operation_record_can_bind_current_parent(history):
    repo, anchor = history
    before = repo.create_commit(repo.root, {README: b"planned"}, "start")
    candidate = repo.create_commit(
        before, {OPERATION: encode(operation_record(before))}, "record"
    )
    assert validate_history(
        anchor, candidate.revision, repository=repo
    ) == ValidationReport(
        LocalOutcome.COMPLETED, candidate.revision, valid_prefix=candidate.revision
    )


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        pytest.param(
            {"base": "root"}, "unbound transaction record", id="valid-but-stale-parent"
        ),
        pytest.param(
            {"request_digest": "g" * 64},
            "unbound transaction record",
            id="nonhex-request-digest",
        ),
        pytest.param(
            {"story": 9},
            "requires its owning story path",
            id="story-claimed-in-store-record",
        ),
        pytest.param(
            {"command": {"operation_id": OPERATION_ID, "local": "success"}},
            "Input should be",
            id="unknown-command-outcome",
        ),
    ],
)
def test_operation_record_requires_its_independent_bindings(history, changes, reason):
    repo, anchor = history
    before = repo.create_commit(repo.root, {README: b"planned"}, "start")
    candidate = repo.create_commit(
        before,
        {OPERATION: encode(operation_record(before) | changes)},
        "unbound record",
    )
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        before,
        reason,
    )


@pytest.mark.parametrize(
    "updated",
    [
        pytest.param(None, id="delete"),
        pytest.param(b'{"schema_version":"aitm.operation-record/v1"}', id="overwrite"),
    ],
)
def test_operation_record_remains_immutable(history, updated):
    repo, anchor = history
    recorded = repo.create_commit(
        repo.root, {OPERATION: encode(operation_record(repo.root))}, "retain"
    )
    candidate = repo.create_commit(recorded, {OPERATION: updated}, "mutate receipt")
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        recorded,
        f"retained planning record changed: {OPERATION}",
    )


def test_story_stream_accepts_causal_append_after_unterminated_prior_line(history):
    repo, anchor = history
    first = event()
    before = repo.create_commit(repo.root, {EVENTS: first}, "record event")
    prefix = first + b"\n"
    candidate = repo.create_commit(
        before,
        {EVENTS: prefix + event(sequence=2, previous=prefix) + b"\n"},
        "append event",
    )
    report = validate_history(anchor, candidate.revision, repository=repo)
    assert report == ValidationReport(
        LocalOutcome.COMPLETED, candidate.revision, valid_prefix=candidate.revision
    )


def test_story_stream_rejects_another_story_even_when_event_is_well_formed(history):
    repo, anchor = history
    candidate = repo.create_commit(
        repo.root, {EVENTS: event(story=10)}, "misrouted event"
    )
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        repo.root,
        "event stream belongs to a different story",
    )


@pytest.mark.parametrize(
    ("update", "reason"),
    [
        pytest.param(None, "event stream removed", id="remove-stream"),
        pytest.param(b"", "event stream is not append-only", id="truncate-stream"),
    ],
)
def test_story_stream_does_not_drop_retained_bytes(history, update, reason):
    repo, anchor = history
    recorded = repo.create_commit(repo.root, {EVENTS: event() + b"\n"}, "retain event")
    candidate = repo.create_commit(recorded, {EVENTS: update}, "discard evidence")
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        recorded,
        reason,
    )


def test_required_core_event_without_reducer_is_unavailable(history):
    repo, anchor = history
    candidate = repo.create_commit(
        repo.root, {EVENTS: event(kind="core.unknown.observed")}, "unavailable event"
    )
    report = validate_history(anchor, candidate.revision, repository=repo)
    assert report.outcome == LocalOutcome.UNAVAILABLE
    assert report.tip == candidate.revision
    assert "core.unknown.observed" in report.reason


def test_clean_final_tree_cannot_hide_invalid_ancestor(history):
    repo, anchor = history
    accepted = repo.create_commit(repo.root, {README: b"known"}, "valid")
    invalid = repo.create_commit(accepted, {"outside.txt": b"invalid"}, "invalid")
    tip = repo.create_commit(invalid, {"outside.txt": None}, "ordinary cleanup")
    report = validate_history(anchor, tip.revision, repository=repo)
    assert report.outcome == LocalOutcome.INTEGRITY_ERROR
    assert report.tip == tip.revision
    assert report.valid_prefix == accepted.revision
    assert report.first_invalid == invalid.revision
    assert "outside.txt" in report.reason


def test_repair_receipt_cannot_nominate_a_clean_history(history):
    repo, anchor = history
    tip = repo.create_commit(
        repo.root, {REPAIR: b'{"schema":"aitm.forward-repair/v1"}'}, "unsolicited proof"
    )

    def must_not_verify(*_args):
        pytest.fail("repair verifier requires a diagnosed invalid prefix")

    report = validate_history(
        anchor, tip.revision, repository=repo, forward_repair_verifier=must_not_verify
    )
    assert_rejected(
        report, tip, repo.root, "forward repair requires a diagnosed invalid history"
    )


@pytest.fixture
def repair_history(history):
    repo, anchor = history
    prefix = repo.create_commit(repo.root, {README: b"last valid"}, "valid prefix")
    bad = repo.create_commit(prefix, {"outside.txt": b"invalid"}, "first bad commit")
    bad_tip = repo.create_commit(bad, {README: b"unvalidated change"}, "invalid tail")
    candidate = repo.create_commit(
        bad_tip,
        {
            "outside.txt": None,
            README: b"last valid",
            REPAIR: b'{"schema":"aitm.forward-repair/v1"}',
        },
        "repair candidate",
    )
    return repo, anchor, prefix, bad, bad_tip, candidate


@pytest.mark.parametrize("proof", ["wrong-tip", "refused-outcome", "untyped-result"])
def test_forward_repair_proof_must_complete_for_exact_candidate(repair_history, proof):
    repo, anchor, prefix, bad, bad_tip, candidate = repair_history

    def verify(bound_anchor, diagnosis, requested_tip):
        assert (bound_anchor, requested_tip) == (anchor, candidate)
        assert diagnosis.valid_prefix == prefix
        assert diagnosis.first_invalid == bad.revision
        assert diagnosis.bad_tip == bad_tip
        if proof == "wrong-tip":
            return ValidationReport(LocalOutcome.COMPLETED, bad_tip.revision)
        if proof == "refused-outcome":
            return ValidationReport(LocalOutcome.REFUSED, candidate.revision)
        return {"outcome": "completed", "tip": candidate.revision}

    report = validate_history(
        anchor, candidate.revision, repository=repo, forward_repair_verifier=verify
    )
    assert report == ValidationReport(
        LocalOutcome.INTEGRITY_ERROR,
        candidate.revision,
        "forward-repair-proof-refused",
        prefix.revision,
        bad.revision,
    )


def test_passed_repair_seam_does_not_make_accepted_receipt_mutable(repair_history):
    repo, anchor, _, _, _, candidate = repair_history
    after = repo.create_commit(candidate, {REPAIR: None}, "remove proof")

    def verify(_anchor, _diagnosis, requested_tip):
        assert requested_tip == candidate
        return ValidationReport(LocalOutcome.COMPLETED, requested_tip.revision)

    report = validate_history(
        anchor, after.revision, repository=repo, forward_repair_verifier=verify
    )
    assert_rejected(
        report, after, candidate, f"retained planning record changed: {REPAIR}"
    )


def test_shallow_history_is_unavailable_before_anchoring(history, monkeypatch):
    repo, anchor = history

    def shallow(command, *args):
        assert (command, args) == ("rev-parse", ("--is-shallow-repository",))
        return b"true\n"

    monkeypatch.setattr(repo, "_git", shallow)
    report = validate_history(anchor, repo.root.revision, repository=repo)
    assert report == ValidationReport(
        LocalOutcome.UNAVAILABLE,
        repo.root.revision,
        "complete-planning-history-required",
    )


def test_inaccessible_code_ancestry_is_unavailable(history, monkeypatch):
    repo, anchor = history

    def ancestry_failed(command, *args):
        assert (command, args) == ("merge-base", (repo.root.revision, "code-root"))
        return SimpleNamespace(returncode=128, stderr=b"object database unavailable")

    monkeypatch.setattr(repo, "_run", ancestry_failed)
    report = validate_history(anchor, repo.root.revision, repository=repo)
    assert report == ValidationReport(
        LocalOutcome.UNAVAILABLE,
        repo.root.revision,
        "git merge-base failed: object database unavailable",
    )


def test_history_uses_anchored_planning_ref_identity(history):
    repo, anchor = history
    other_target = anchor.model_copy(
        update={"planning_ref": "refs/heads/other-records"}
    )
    report = validate_history(other_target, repo.root.revision, repository=repo)
    assert report == ValidationReport(
        LocalOutcome.INTEGRITY_ERROR,
        repo.root.revision,
        "anchor does not identify the configured planning and code refs",
    )


def test_history_checks_commit_parent_independent_of_rev_list(history, monkeypatch):
    repo, anchor = history
    candidate = repo.create_commit(repo.root, {README: b"planning"}, "candidate")
    git = repo._git

    def divergent_parent(command, *args):
        if (command, args) == ("cat-file", ("commit", candidate.revision)):
            return b"parent unrelated\n\n"
        return git(command, *args)

    monkeypatch.setattr(repo, "_git", divergent_parent)
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        repo.root,
        "planning-history-must-be-linear",
    )


def test_tree_inventory_cannot_silently_overwrite_duplicate_path(history, monkeypatch):
    repo, anchor = history
    candidate = repo.create_commit(repo.root, {README: b"planning"}, "candidate")
    git = repo._git

    def duplicate_path(command, *args):
        ordinary = git(command, *args)
        if (command, args) == ("ls-tree", ("-r", "-z", "--full-tree", candidate.tree)):
            return (
                ordinary + b"100644 blob " + b"a" * 40 + b"\t" + README.encode() + b"\0"
            )
        return ordinary

    monkeypatch.setattr(repo, "_git", duplicate_path)
    report = validate_history(anchor, candidate.revision, repository=repo)
    assert report.outcome == LocalOutcome.INTEGRITY_ERROR
    assert report.tip == candidate.revision
    assert report.reason == f"duplicate planning path: {README}"


def test_typed_entry_without_blob_content_is_integrity_error(history, monkeypatch):
    repo, anchor = history
    candidate = repo.create_commit(repo.root, {STORE: b"unreadable"}, "typed metadata")

    def missing_blob(tree, paths):
        if paths:
            assert (tree, paths) == (candidate.tree, (STORE,))
        return dict.fromkeys(paths)

    monkeypatch.setattr(repo, "read_blobs", missing_blob)
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        repo.root,
        f"missing planning blob: {STORE}",
    )


def test_repair_proof_does_not_bypass_planning_data_policy(repair_history):
    repo, anchor, _, _, bad_tip, _ = repair_history
    candidate = repo.create_commit(
        bad_tip,
        {
            "outside.txt": None,
            REPAIR: b'{"schema":"aitm.forward-repair/v1"}',
            "unrelated.py": b"source",
        },
        "proof over a still-invalid tree",
    )

    def verify(_anchor, _history, target):
        assert target == candidate
        return ValidationReport(LocalOutcome.COMPLETED, target.revision)

    report = validate_history(
        anchor, candidate.revision, repository=repo, forward_repair_verifier=verify
    )
    assert report.outcome == LocalOutcome.INTEGRITY_ERROR
    assert report.tip == candidate.revision
    assert report.reason == "outside planning data paths: unrelated.py"


def test_story_record_does_not_coerce_boolean_to_story_one(history):
    repo, anchor = history
    record = operation_record(repo.root) | {"story": True}
    path = OPERATION.replace(".aitm/operations/", ".aitm/stories/000/1/operations/")
    candidate = repo.create_commit(
        repo.root, {path: encode(record)}, "incorrect story owner type"
    )
    assert_rejected(
        validate_history(anchor, candidate.revision, repository=repo),
        candidate,
        repo.root,
        "operation record does not match its owning story",
    )


def test_git_path_without_utf8_identity_cannot_be_treated_as_planning_data(
    history, monkeypatch
):
    repo, anchor = history
    candidate = repo.create_commit(
        repo.root, {README: b"known path"}, "ambiguous path bytes"
    )
    git = repo._git

    def invalid_path(command, *args):
        raw = git(command, *args)
        if (command, args) == ("ls-tree", ("-r", "-z", "--full-tree", candidate.tree)):
            raw = raw.replace(README.encode(), b".aitm/\xff.md")
        return raw

    monkeypatch.setattr(repo, "_git", invalid_path)
    report = validate_history(anchor, candidate.revision, repository=repo)
    assert report.outcome == LocalOutcome.INTEGRITY_ERROR
    assert report.tip == candidate.revision
    assert "invalid start byte" in report.reason
