import importlib
import json
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from aitm_usage.ledger import Ledger
from aitm_usage.scopes import drain_inbox, enqueue_command, session_reference
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    DiagnosticCode,
    Eligibility,
    InboxCommand,
    ItemKey,
    ItemKind,
    LedgerBatch,
    MarkerDisposition,
    Provider,
    Registration,
    ReviewRole,
    Revision,
    ScopeEnrollment,
    ScopeMarker,
    SourceBoundary,
    SourceCheckpoint,
    TokenCounts,
    UsageObservation,
    WorkPhase,
)

PROJECT = UUID(int=110)
SESSION = UUID(int=111)
CUTOFF = datetime(2026, 11, 9, 16, tzinfo=UTC)
BEFORE = CUTOFF - timedelta(seconds=1)
AFTER = CUTOFF + timedelta(seconds=1)


def _scanner():
    assert importlib.util.find_spec("aitm_usage.sources") is not None, (
        "U03 must provide the approved-root scanner"
    )
    return importlib.import_module("aitm_usage.sources.scan")


@pytest.fixture
def project(tmp_path, monkeypatch):
    tmp_path = tmp_path.resolve()
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    store = Ledger.initialize(tmp_path / "project", PROJECT)
    roots = tmp_path / "transcripts"
    checkout = tmp_path / "checkout-secret"
    roots.mkdir()
    checkout.mkdir()
    return Registration(PROJECT, store.root, (roots,), (checkout,), CUTOFF), store


def _row(kind, payload, time=AFTER):
    return (
        json.dumps(
            {"type": kind, "timestamp": time.isoformat(), "payload": payload}
        ).encode()
        + b"\n"
    )


def _header(cwd, *, session=SESSION, version="0.167.0-alpha.3.2", **extra):
    return _row(
        "session_meta",
        {
            "id": str(session),
            "cwd": str(cwd),
            "cli_version": version,
            "git": {"branch": "branch-secret"},
            **extra,
        },
        BEFORE,
    )


def _usage(tokens, time=AFTER):
    return _row(
        "event_msg",
        {
            "type": "token_count",
            "info": {"total_token_usage": {"output_tokens": tokens}},
        },
        time,
    )


def _turn(cwd):
    return _row("turn_context", {"cwd": str(cwd), "turn_id": str(UUID(int=112))})


def _fixture_debits(batch):
    """An adapter stand-in that can debit only commit-safe eligible frames."""
    return [
        (frame, frame.row["payload"]["info"]["total_token_usage"]["output_tokens"])
        for frame in batch.commit_frames
        if frame.eligibility is Eligibility.ELIGIBLE
        and frame.row["type"] == "event_msg"
        and frame.row["payload"]["type"] == "token_count"
    ]


def _checkpoint(batch):
    return SourceCheckpoint(batch.cursor, batch.provider_checkpoint)


def _codes(batch):
    return {record.code for record in batch.diagnostics}


def test_activation_cutoff_and_archive_continuity(project):
    scanner = _scanner()
    registration, store = project
    live = registration.source_roots[0] / "live-secret.jsonl"
    archived = registration.source_roots[0] / "archived-secret.jsonl"
    header = _header(registration.checkout_anchors[0])
    complete = header + _usage(12, BEFORE) + _usage(15, CUTOFF)
    partial = _usage(19)
    live.write_bytes(complete + partial[:-1])

    (source,) = scanner.discover(registration)
    first = scanner.scan(source, None, CUTOFF)
    assert first.cursor.offset == len(complete)
    assert [frame.ordinal for frame in first.frames] == [0, 1, 2]
    assert [tokens for _, tokens in _fixture_debits(first)] == [15]
    assert first.frames[1].pre_cutoff
    assert (
        first.provider_checkpoint.client_version
        is ClientVersion.CODEX_0_167_0_ALPHA_3_2
    )
    assert first.provider_checkpoint.format_version == 1
    prior = _checkpoint(first)
    store.apply(LedgerBatch(checkpoint=prior))

    archived.write_bytes(complete + partial)
    live.unlink()
    restored = Ledger.open(store.root, PROJECT).as_of().checkpoints[0]
    (archive_source,) = scanner.discover(registration)
    archive = scanner.scan(archive_source, restored, CUTOFF)
    assert archive.cursor.offset == len(complete + partial)
    assert archive.cursor.source_ref == first.cursor.source_ref
    assert archive.cursor.locator_ref != first.cursor.locator_ref
    assert archive.cursor.incarnation_ref != first.cursor.incarnation_ref
    assert archive.cursor.anchor_ref != archive.frames[0].anchor_ref
    assert [(frame.ordinal, tokens) for frame, tokens in _fixture_debits(archive)] == [
        (3, 19)
    ]
    advanced = _checkpoint(archive)
    store.apply(LedgerBatch(checkpoint=advanced, prior_checkpoint=restored))
    assert scanner.scan(archive_source, advanced, CUTOFF).frames == ()

    overlap = registration.source_roots[0] / "overlap-secret.jsonl"
    overlap.write_bytes(header + _usage(66, BEFORE) + _usage(99, CUTOFF) + partial)
    bad = next(
        candidate
        for candidate in scanner.discover(registration)
        if candidate.locator_ref != archive.cursor.locator_ref
    )
    rejected = scanner.scan(bad, advanced, CUTOFF)
    assert _codes(rejected) == {DiagnosticCode.OVERLAP_UNVERIFIED}
    assert rejected.cursor is None
    assert rejected.frames == rejected.commit_frames == ()
    assert "overlap-secret" not in repr(rejected)


@pytest.mark.parametrize("swap_parent", [False, True])
def test_escape_after_discovery_cannot_read_unapproved_source(project, swap_parent):
    scanner = _scanner()
    registration, _ = project
    source_dir = registration.source_roots[0] / "live"
    source_dir.mkdir()
    path = source_dir / "rollout-secret.jsonl"
    contents = _header(registration.checkout_anchors[0]) + _usage(17)
    path.write_bytes(contents)
    (candidate,) = scanner.discover(registration)

    outside = source_dir.parent.parent / "private-unapproved"
    outside.mkdir()
    (outside / path.name).write_bytes(contents)
    path.unlink()
    if swap_parent:
        source_dir.rmdir()
        source_dir.symlink_to(outside, target_is_directory=True)
    else:
        path.symlink_to(outside / path.name)

    assert tuple(scanner.discover(registration)) == ()
    scan = scanner.scan(candidate, None, CUTOFF)
    assert scan.frames == ()
    assert scan.cursor is None
    assert _codes(scan) == {DiagnosticCode.SOURCE_REPLACED}
    assert "rollout-secret" not in repr(scan)


def test_root_symlink_is_never_implicitly_approved(project):
    scanner = _scanner()
    registration, _ = project
    (root,) = registration.source_roots
    outside = root.parent / "private-unapproved"
    outside.mkdir()
    (outside / "rollout.jsonl").write_bytes(
        _header(registration.checkout_anchors[0]) + _usage(12)
    )
    root.rmdir()
    root.symlink_to(outside, target_is_directory=True)

    assert tuple(scanner.discover(registration)) == ()


@pytest.mark.parametrize(
    "mutation", ["rename", "delete", "overwrite", "rewrite-and-grow", "append"]
)
def test_scanner_revalidates_open_snapshot(project, monkeypatch, mutation):
    scanner = _scanner()
    registration, _ = project
    path = registration.source_roots[0] / "replacement-secret.jsonl"
    header = _header(registration.checkout_anchors[0])
    contents = header + _usage(11)
    path.write_bytes(contents)
    (candidate,) = scanner.discover(registration)

    decode = scanner._decode_row
    changed = False

    def change_after_read(raw):
        nonlocal changed
        row = decode(raw)
        if row and row["type"] == "event_msg" and not changed:
            changed = True
            if mutation == "rename":
                path.rename(path.with_suffix(".old"))
                path.write_bytes(contents)
            elif mutation == "delete":
                path.unlink()
            elif mutation == "overwrite":
                path.write_bytes(header + _usage(99))
            elif mutation == "rewrite-and-grow":
                path.write_bytes(header + _usage(99) + _usage(22))
            else:
                with path.open("ab") as output:
                    output.write(_usage(22))
        return row

    monkeypatch.setattr(scanner, "_decode_row", change_after_read)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert changed
    if mutation == "append":
        assert _codes(batch) == set()
        assert [tokens for _, tokens in _fixture_debits(batch)] == [11]
        assert batch.cursor.offset == len(contents)
        resumed = scanner.scan(candidate, _checkpoint(batch), CUTOFF)
        assert [tokens for _, tokens in _fixture_debits(resumed)] == [22]
    else:
        assert batch.frames == ()
        assert batch.cursor is None
        assert _codes(batch) == {DiagnosticCode.SOURCE_REPLACED}
        assert "replacement-secret" not in repr(batch)


@pytest.mark.parametrize(
    "header_changes",
    [
        {"format_version": 48},
        {"version": "unknown-version-secret"},
    ],
)
def test_unsupported_format_never_yields_boundary_proof(project, header_changes):
    scanner = _scanner()
    registration, _ = project
    path = registration.source_roots[0] / "unsupported.jsonl"
    path.write_bytes(
        _header(registration.checkout_anchors[0], **header_changes) + _usage(20)
    )
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert batch.frames == ()
    assert batch.cursor is None
    assert _codes(batch) == {DiagnosticCode.UNSUPPORTED_FORMAT}
    assert "unknown-version-secret" not in repr(batch)


def test_malformed_row_diagnostics_are_closed_and_checkpointable(project):
    scanner = _scanner()
    registration, store = project
    path = registration.source_roots[0] / "malformed-path-secret.jsonl"
    (cwd,) = registration.checkout_anchors
    path.write_bytes(
        _header(cwd)
        + b'{"type":"event_msg", "payload": "malformed-payload-secret"\n'
        + _turn(cwd)
        + _usage(19)
    )
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert _codes(batch) == {DiagnosticCode.MALFORMED_USAGE}
    assert [frame.ordinal for frame in batch.frames] == [0, 2, 3]
    assert [tokens for _, tokens in _fixture_debits(batch)] == [19]
    revisions = tuple(
        Revision(store.pseudonymize("diagnostic", str(index)), 1, diagnostic)
        for index, diagnostic in enumerate(batch.diagnostics)
    )
    store.apply(LedgerBatch(revisions, _checkpoint(batch)))
    for state in store.root.glob("usage.sqlite3*"):
        contents = state.read_bytes()
        assert b"malformed-payload-secret" not in contents
        assert b"malformed-path-secret" not in contents
        assert b"checkout-secret" not in contents
        assert b"branch-secret" not in contents
        assert str(SESSION).encode() not in contents


def test_coverage_projects_classifications_for_committable_frames(project):
    scanner = _scanner()
    registration, store = project
    path = registration.source_roots[0] / "source.jsonl"
    (cwd,) = registration.checkout_anchors
    path.write_bytes(
        _header(cwd)
        + _turn(cwd)
        + _usage(2)
        + _turn(cwd)
        + _usage(3)
        + _turn(cwd)
        + _usage(4)
    )
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)

    kind = scanner.CoverageKind
    classified = scanner.FrameClassification
    missing = store.pseudonymize("turn", "closed-without-usage")
    open_turn = store.pseudonymize("turn", "still-open")
    seen = store.pseudonymize("turn", "closed-with-usage")
    coverage = batch.coverage(
        (
            classified(1, kind.CLOSED_TURN, missing),
            classified(2, kind.UNFAMILIAR_USAGE),
            classified(3, kind.RECOGNIZED_USAGE, seen),
            classified(4, kind.CLOSED_TURN, seen),
            classified(5, kind.RECOGNIZED_USAGE, open_turn),
            classified(6, kind.IN_FLIGHT_CUTOFF, open_turn),
            classified(99, kind.UNFAMILIAR_USAGE),
        )
    )

    assert {(gap.code, gap.ordinal) for gap in coverage} == {
        (DiagnosticCode.COVERAGE_GAP, 1),
        (DiagnosticCode.UNKNOWN_USAGE, 2),
        (DiagnosticCode.COVERAGE_GAP, 6),
    }


def _marker_and_boundary(store, frame, *, marker_number=120, sequence=1):
    marker_id = UUID(int=marker_number)
    marker = ScopeMarker(
        marker_id,
        frame.provider,
        frame.session_ref,
        sequence,
        BoundaryKind.REQUEST,
        store.pseudonymize("request", f"enrolled-reviewer-first:{marker_id}"),
        BEFORE,
        ItemKey(ItemKind.ISSUE, 87),
        WorkPhase.SOURCE_REVIEW,
        store.pseudonymize("participant", "reviewer"),
        PROJECT,
        ReviewRole.REVIEWER,
        store.pseudonymize("scope-receipt", str(marker_id)),
    )
    boundary = SourceBoundary(
        frame.provider,
        frame.stream_ref,
        frame.session_ref,
        frame.ordinal,
        marker.boundary_kind,
        marker.boundary_ref,
        receipt_ref=marker.receipt_ref,
    )
    return marker, boundary


def test_scope_join_requires_unique_exact_frame_and_verified_checkout(project):
    scanner = _scanner()
    registration, store = project
    path = registration.source_roots[0] / "rollout.jsonl"
    (cwd,) = registration.checkout_anchors
    path.write_bytes(_header(cwd) + _turn(cwd) + _usage(14))
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    frame = batch.frames[1]
    _, boundary = _marker_and_boundary(store, frame)
    evidence = batch.scope_evidence(boundary)

    assert evidence.boundary == boundary
    assert evidence.anchor_ref == frame.anchor_ref
    assert evidence.anchor_ref is not None
    other_ref = store.pseudonymize("fixture", "other")
    for mismatch in (
        replace(boundary, provider=Provider.CLAUDE),
        replace(boundary, session_ref=other_ref),
        replace(boundary, stream_ref=other_ref),
        replace(boundary, ordinal=99),
    ):
        assert batch.scope_evidence(mismatch) is None
    assert (
        replace(batch, frames=(*batch.frames, frame)).scope_evidence(boundary) is None
    )


def test_verified_enrollment_holds_candidate_then_replays_first_eligible_after_restart(
    project,
):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    review = root.parent / "review-private"
    unrelated = root.parent / "unrelated-private"
    review.mkdir()
    unrelated.mkdir()
    path = root / "review-source.jsonl"
    before_candidate = _header(checkout) + _usage(5, BEFORE)
    path.write_bytes(
        before_candidate
        + _turn(review)
        + _usage(7)
        + _usage(11)
        + _usage(14)
        + _turn(unrelated)
        + _usage(39)
    )

    (candidate,) = scanner.discover(registration)
    first = scanner.scan(candidate, None, CUTOFF)
    assert first.cursor.offset == len(before_candidate)
    assert [frame.ordinal for frame in first.commit_frames] == [0, 1]
    assert _fixture_debits(first) == []
    assert first.frames[4].boundary_only
    marker, boundary = _marker_and_boundary(store, first.frames[4])
    proof = first.scope_evidence(boundary)
    assert proof.boundary == boundary
    assert proof.anchor_ref is None
    with pytest.raises(ValueError, match="verified enrollment"):
        candidate.with_enrollment(ScopeEnrollment(marker, boundary))

    # Simulate a real adapter's sanitized prior counters, then restart.
    held = SourceCheckpoint(
        first.cursor,
        replace(
            first.provider_checkpoint, ordinal=1, baseline=TokenCounts(output_tokens=5)
        ),
    )
    store.apply(LedgerBatch(checkpoint=held))
    enqueue_command(store.root, InboxCommand(marker.marker_id, PROJECT, marker))
    with store.writer() as writer:
        drained = drain_inbox(writer, (proof,))
    assert drained.receipts[0].disposition is MarkerDisposition.ACCEPTED

    reopened = Ledger.open(store.root, PROJECT)
    view = reopened.as_of()
    assert view.checkpoints == (held,)
    accepted = next(
        r.record for r in view.current if isinstance(r.record, ScopeEnrollment)
    )
    (rediscovered,) = scanner.discover(registration)
    unproven = scanner.scan(rediscovered.with_enrollment(accepted), held, CUTOFF)
    assert unproven.cursor == held.cursor
    assert unproven.commit_frames == ()
    assert _codes(unproven) == {DiagnosticCode.BOUNDARY_UNVERIFIED}

    lookahead = scanner.scan(rediscovered, held, CUTOFF)
    frame = next(frame for frame in lookahead.frames if frame.ordinal == 4)
    _, fresh_boundary = _marker_and_boundary(reopened, frame)
    fresh_proof = lookahead.scope_evidence(fresh_boundary)
    wrong_proof = replace(
        fresh_proof, boundary=replace(fresh_boundary, receipt_ref=None)
    )
    with pytest.raises(ValueError, match="fresh evidence"):
        rediscovered.with_enrollment(accepted, batch=lookahead, evidence=wrong_proof)
    enrolled = rediscovered.with_enrollment(
        accepted, batch=lookahead, evidence=fresh_proof
    )
    original = path.read_bytes()
    path.write_bytes(original.replace(_usage(11), _usage(81)))
    stale = scanner.scan(enrolled, held, CUTOFF)
    assert stale.cursor == held.cursor
    assert stale.commit_frames == ()
    assert _codes(stale) == {DiagnosticCode.BOUNDARY_UNVERIFIED}
    path.write_bytes(before_candidate + _turn(review) + _usage(7))
    missing = scanner.scan(enrolled, held, CUTOFF)
    assert missing.cursor is None
    assert missing.commit_frames == ()
    assert _codes(missing) == {DiagnosticCode.BOUNDARY_UNVERIFIED}
    path.write_bytes(original)
    second = scanner.scan(enrolled, held, CUTOFF)
    assert second.provider_checkpoint.baseline == TokenCounts(output_tokens=5)
    assert [frame.eligibility for frame in second.commit_frames[:2]] == [
        Eligibility.EXCLUDED,
        Eligibility.EXCLUDED,
    ]
    assert [(frame.ordinal, tokens) for frame, tokens in _fixture_debits(second)] == [
        (4, 11),
        (5, 14),
    ]
    assert second.cursor.offset == len(path.read_bytes()) - len(
        _turn(unrelated) + _usage(39)
    )
    assert second.frames[-1].boundary_only

    # U08 explicitly designates a resolved unrelated segment before advancing it.
    excluded = enrolled.with_exclusion(second.frames[-1])
    final = scanner.scan(excluded, held, CUTOFF)
    assert final.cursor.offset == path.stat().st_size
    assert final.commit_frames[-1].eligibility is Eligibility.EXCLUDED
    revisions = tuple(
        Revision(
            store.pseudonymize("fixture-observation", str(frame.ordinal)),
            1,
            UsageObservation(
                replace(boundary, ordinal=frame.ordinal),
                frame.observed_at,
                frame.client_version,
                frame.format_version,
                TokenCounts(output_tokens=tokens),
                Availability.COMPLETE,
            ),
        )
        for frame, tokens in _fixture_debits(final)
    )
    committed = SourceCheckpoint(
        final.cursor,
        replace(
            final.provider_checkpoint, ordinal=7, baseline=TokenCounts(output_tokens=39)
        ),
    )
    reopened.apply(LedgerBatch(revisions, committed, held))
    reopened = Ledger.open(store.root, PROJECT)
    final_view = reopened.as_of()
    assert final_view.checkpoints == (committed,)
    assert sorted(
        revision.record.tokens.output_tokens
        for revision in final_view.current
        if isinstance(revision.record, UsageObservation)
    ) == [11, 14]
    (last,) = scanner.discover(registration)
    replay = scanner.scan(last.with_enrollment(accepted), committed, CUTOFF)
    assert replay.commit_frames == ()
    assert replay.cursor == committed.cursor


def test_claude_uses_provider_qualified_session_and_real_checkout_metadata(project):
    scanner = _scanner()
    registration, store = project
    path = registration.source_roots[0] / "claude-secret.jsonl"
    (cwd,) = registration.checkout_anchors
    common = {
        "sessionId": str(SESSION),
        "cwd": str(cwd),
        "version": "2.1.318",
        "timestamp": AFTER.isoformat(),
    }
    path.write_text(
        json.dumps(dict(common, type="user", message={"content": "prompt-secret"}))
        + "\n"
        + json.dumps(
            dict(
                common,
                type="assistant",
                requestId="req-secret",
                message={"id": "msg-secret", "usage": {"output_tokens": 6}},
            )
        )
        + "\n",
        encoding="utf-8",
    )
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    expected = session_reference(store, Provider.CLAUDE, str(SESSION))
    assert candidate.session_ref == expected
    assert candidate.session_ref != session_reference(
        store, Provider.CODEX, str(SESSION)
    )
    assert [frame.eligibility for frame in batch.commit_frames] == [
        Eligibility.ELIGIBLE
    ] * 2
    assert batch.provider_checkpoint.client_version is ClientVersion.CLAUDE_2_1_318
    assert not any(
        secret in repr((candidate, batch))
        for secret in (
            "prompt-secret",
            "req-secret",
            "msg-secret",
            "claude-secret",
            str(SESSION),
            str(cwd),
        )
    )


def test_in_place_origin_change_cannot_hide_behind_append(project, monkeypatch):
    scanner = _scanner()
    registration, _ = project
    path = registration.source_roots[0] / "rollout.jsonl"
    (cwd,) = registration.checkout_anchors
    path.write_bytes(_header(cwd) + _usage(12))
    (candidate,) = scanner.discover(registration)
    decode = scanner._decode_row
    changed = False

    def change_origin(raw):
        nonlocal changed
        row = decode(raw)
        if row and row["type"] == "session_meta" and not changed:
            changed = True
            path.write_bytes(
                _header(cwd, session=UUID(int=404)) + _usage(12) + _usage(15)
            )
        return row

    monkeypatch.setattr(scanner, "_decode_row", change_origin)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert changed
    assert batch.frames == ()
    assert batch.cursor is None
    assert _codes(batch) == {DiagnosticCode.SOURCE_REPLACED}


def test_zero_cursor_cannot_verify_copy_of_unknown_prefix(project):
    scanner = _scanner()
    registration, _ = project
    (root,) = registration.source_roots
    (cwd,) = registration.checkout_anchors
    unanchored = root.parent / "unanchored"
    unanchored.mkdir()
    original = root / "original.jsonl"
    original.write_bytes(_header(unanchored) + _usage(10))
    (candidate,) = scanner.discover(registration)
    held = scanner.scan(candidate, None, CUTOFF)
    assert held.cursor.offset == 0
    assert held.commit_frames == ()

    copied = root / "different.jsonl"
    copied.write_bytes(_header(cwd) + _usage(21))
    other = next(item for item in scanner.discover(registration) if item != candidate)
    rejected = scanner.scan(other, _checkpoint(held), CUTOFF)
    assert rejected.cursor is None
    assert _codes(rejected) == {DiagnosticCode.OVERLAP_UNVERIFIED}


@pytest.mark.parametrize("invalid_cwd", ["symlink", "unicode"])
def test_checkout_anchor_requires_a_real_confined_directory(project, invalid_cwd):
    scanner = _scanner()
    registration, _ = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    external = root.parent / "external"
    external.mkdir()
    spoofed = checkout / "symlink"
    spoofed.symlink_to(external, target_is_directory=True)
    cwd = spoofed if invalid_cwd == "symlink" else checkout / "\ud800"
    path = root / "source.jsonl"
    path.write_bytes(_header(cwd) + _usage(11))
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert batch.cursor.offset == 0
    assert batch.commit_frames == ()
    assert batch.frames[1].anchor_ref is None


def test_checkout_anchor_is_rechecked_after_read(project, monkeypatch):
    scanner = _scanner()
    registration, _ = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    path = root / "rollout.jsonl"
    path.write_bytes(_header(checkout) + _usage(27))
    (candidate,) = scanner.discover(registration)

    decode = scanner._decode_row

    def move_checkout(raw):
        row = decode(raw)
        if row and row["type"] == "event_msg":
            displaced = checkout.with_name("displaced")
            checkout.rename(displaced)
            checkout.symlink_to(displaced, target_is_directory=True)
        return row

    monkeypatch.setattr(scanner, "_decode_row", move_checkout)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert batch.frames == batch.commit_frames == ()
    assert batch.cursor is None
    assert _codes(batch) == {DiagnosticCode.BOUNDARY_UNVERIFIED}


def test_missing_turn_checkout_does_not_inherit_admission(project):
    scanner = _scanner()
    registration, _ = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    path = root / "rollout.jsonl"
    header = _header(checkout)
    path.write_bytes(
        header + _row("turn_context", {"turn_id": str(UUID(int=113))}) + _usage(27)
    )
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert batch.cursor.offset == len(header)
    assert _fixture_debits(batch) == []
    assert batch.frames[-1].boundary_only
    assert batch.frames[-1].anchor_ref is None


def test_scan_rejects_candidate_from_another_approved_root_set(project):
    scanner = _scanner()
    registration, _ = project
    outside = registration.source_roots[0].parent / "unapproved"
    outside.mkdir()
    path = outside / "rollout.jsonl"
    path.write_bytes(_header(registration.checkout_anchors[0]) + _usage(77))
    external_registration = replace(registration, source_roots=(outside,))
    (candidate,) = scanner.discover(external_registration)

    stale_candidate = replace(candidate, _registration=registration)
    batch = scanner.scan(stale_candidate, None, CUTOFF)
    assert batch.frames == ()
    assert batch.cursor is None
    assert _codes(batch) == {DiagnosticCode.SOURCE_REPLACED}


def test_zero_cursor_detects_a_rewritten_origin_after_rediscovery(project):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    unanchored = root.parent / "unanchored"
    unanchored.mkdir()
    path = root / "rollout.jsonl"
    path.write_bytes(_header(unanchored) + _usage(7))
    (candidate,) = scanner.discover(registration)
    held = scanner.scan(candidate, None, CUTOFF)
    assert held.cursor.offset == 0
    store.apply(LedgerBatch(checkpoint=_checkpoint(held)))

    # Retain the same inode and provider session, but replace the origin bytes.
    path.write_bytes(_header(checkout) + _usage(71))
    (updated,) = scanner.discover(registration)
    assert updated.incarnation_ref == candidate.incarnation_ref
    prior = Ledger.open(store.root, PROJECT).as_of().checkpoints[0]
    changed = scanner.scan(updated, prior, CUTOFF)
    assert changed.cursor is None
    assert changed.frames == ()
    assert _codes(changed) == {DiagnosticCode.SOURCE_REPLACED}


def test_exact_archive_duplicate_does_not_churn_checkpoint(project):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    live = root / "rollout.jsonl"
    contents = _header(registration.checkout_anchors[0]) + _usage(23)
    live.write_bytes(contents)
    (candidate,) = scanner.discover(registration)
    first = _checkpoint(scanner.scan(candidate, None, CUTOFF))
    head = store.apply(LedgerBatch(checkpoint=first))

    archive = root / "archive.jsonl"
    archive.write_bytes(contents)
    duplicate = next(
        item for item in scanner.discover(registration) if item != candidate
    )
    batch = scanner.scan(duplicate, first, CUTOFF)
    assert batch.frames == ()
    assert _codes(batch) == set()
    assert batch.cursor == first.cursor
    assert (
        store.apply(LedgerBatch(checkpoint=_checkpoint(batch), prior_checkpoint=first))
        == head
    )


def test_later_enrollment_keeps_earlier_pending_segment_replayable(project):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    first_review = root.parent / "first-review"
    second_review = root.parent / "second-review"
    first_review.mkdir()
    second_review.mkdir()
    path = root / "review.jsonl"
    baseline = _header(checkout) + _usage(5, BEFORE)
    path.write_bytes(
        baseline
        + _turn(first_review)
        + _usage(7)
        + _usage(11)
        + _turn(second_review)
        + _usage(15)
        + _usage(17)
    )

    (candidate,) = scanner.discover(registration)
    lookahead = scanner.scan(candidate, None, CUTOFF)
    held = SourceCheckpoint(
        lookahead.cursor,
        replace(
            lookahead.provider_checkpoint,
            ordinal=1,
            baseline=TokenCounts(output_tokens=5),
        ),
    )
    store.apply(LedgerBatch(checkpoint=held))
    first, first_boundary = _marker_and_boundary(store, lookahead.frames[4])
    second, second_boundary = _marker_and_boundary(
        store, lookahead.frames[7], marker_number=121, sequence=2
    )
    first_hint = lookahead.scope_evidence(replace(first_boundary, receipt_ref=None))
    second_proof = lookahead.scope_evidence(second_boundary)
    for marker in (first, second):
        enqueue_command(store.root, InboxCommand(marker.marker_id, PROJECT, marker))
    with store.writer() as writer:
        outcome = drain_inbox(writer, (first_hint, second_proof))
    assert [receipt.disposition for receipt in outcome.receipts] == [
        MarkerDisposition.PENDING,
        MarkerDisposition.ACCEPTED,
    ]

    (accepted_second,) = (
        revision.record
        for revision in store.as_of().current
        if isinstance(revision.record, ScopeEnrollment)
    )
    selected = candidate.with_enrollment(
        accepted_second, batch=lookahead, evidence=second_proof
    )
    still_held = scanner.scan(selected, held, CUTOFF)
    assert still_held.cursor == held.cursor
    assert still_held.commit_frames == ()
    assert still_held.provider_checkpoint == held.provider
    store.apply(LedgerBatch(checkpoint=_checkpoint(still_held), prior_checkpoint=held))

    reopened = Ledger.open(store.root, PROJECT)
    (durable,) = reopened.as_of().checkpoints
    assert durable == held
    (fresh,) = scanner.discover(registration)
    replay = scanner.scan(fresh, durable, CUTOFF)
    assert [frame.ordinal for frame in replay.frames] == [2, 3, 4, 5, 6, 7]
    first_proof = replay.scope_evidence(first_boundary)
    assert first_proof is not None
    with reopened.writer() as writer:
        drained = drain_inbox(writer, (first_proof,))
    assert drained.receipts[0].disposition is MarkerDisposition.ACCEPTED

    accepted = {
        revision.record.marker.marker_id: revision.record
        for revision in reopened.as_of().current
        if isinstance(revision.record, ScopeEnrollment)
    }
    selected = fresh.with_enrollment(
        accepted[first.marker_id], batch=replay, evidence=first_proof
    ).with_enrollment(
        accepted[second.marker_id],
        batch=replay,
        evidence=replay.scope_evidence(second_boundary),
    )
    resumed = scanner.scan(selected, durable, CUTOFF)
    assert [(frame.ordinal, tokens) for frame, tokens in _fixture_debits(resumed)] == [
        (4, 11),
        (7, 17),
    ]
    assert resumed.cursor.offset == path.stat().st_size


def test_added_checkout_anchor_preserves_committed_outside_enrollment(project):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    review = root.parent / "newly-registered"
    review.mkdir()
    path = root / "review.jsonl"
    path.write_bytes(_header(checkout) + _turn(review) + _usage(7) + _usage(11))
    (candidate,) = scanner.discover(registration)
    lookahead = scanner.scan(candidate, None, CUTOFF)
    marker, boundary = _marker_and_boundary(store, lookahead.frames[-1])
    proof = lookahead.scope_evidence(boundary)
    assert proof.anchor_ref is None
    enqueue_command(store.root, InboxCommand(marker.marker_id, PROJECT, marker))
    with store.writer() as writer:
        outcome = drain_inbox(writer, (proof,))
    assert outcome.receipts[0].disposition is MarkerDisposition.ACCEPTED
    (accepted,) = (
        revision.record
        for revision in store.as_of().current
        if isinstance(revision.record, ScopeEnrollment)
    )

    expanded = replace(registration, checkout_anchors=(checkout, review))
    (new_candidate,) = scanner.discover(expanded)
    stale_selector = new_candidate.with_enrollment(
        accepted, batch=lookahead, evidence=proof
    )
    uncommitted = scanner.scan(stale_selector, _checkpoint(lookahead), CUTOFF)
    assert _codes(uncommitted) == {DiagnosticCode.BOUNDARY_UNVERIFIED}
    assert uncommitted.commit_frames == ()

    selected = candidate.with_enrollment(accepted, batch=lookahead, evidence=proof)
    first = scanner.scan(selected, None, CUTOFF)
    assert [tokens for _, tokens in _fixture_debits(first)] == [11]
    store.apply(LedgerBatch(checkpoint=_checkpoint(first)))
    with path.open("ab") as output:
        output.write(_usage(14))

    reopened = Ledger.open(store.root, PROJECT)
    (durable,) = reopened.as_of().checkpoints
    (new_candidate,) = scanner.discover(expanded)
    continued = scanner.scan(new_candidate.with_enrollment(accepted), durable, CUTOFF)
    assert _codes(continued) == set()
    assert [
        (frame.ordinal, tokens) for frame, tokens in _fixture_debits(continued)
    ] == [
        (4, 14),
    ]
    assert continued.commit_frames[0].anchor_ref == scanner.checkout_anchor_reference(
        reopened, review
    )
    assert continued.cursor.offset == path.stat().st_size


def test_directory_moved_outside_root_and_restored_during_read_is_quarantined(
    project,
    monkeypatch,
):
    scanner = _scanner()
    registration, _ = project
    (root,) = registration.source_roots
    directory = root / "source-parent"
    directory.mkdir()
    path = directory / "rollout.jsonl"
    path.write_bytes(_header(registration.checkout_anchors[0]) + _usage(22))
    (candidate,) = scanner.discover(registration)
    outside = root.parent / "outside"
    original_inode = directory.stat().st_ino
    original_lines = scanner._lines
    read_rows = []

    def read_while_displaced(stream, size):
        directory.rename(outside)
        try:
            for entry in original_lines(stream, size):
                assert not path.exists()
                read_rows.append(entry[0])
                yield entry
        finally:
            outside.rename(directory)

    with monkeypatch.context() as controlled:
        controlled.setattr(scanner, "_lines", read_while_displaced)
        rejected = scanner.scan(candidate, None, CUTOFF)
    assert read_rows == [0, 1]
    assert directory.stat().st_ino == original_inode
    assert rejected.frames == rejected.commit_frames == ()
    assert rejected.cursor is None
    assert _codes(rejected) == {DiagnosticCode.SOURCE_REPLACED}

    retry = scanner.scan(candidate, None, CUTOFF)
    assert _codes(retry) == set()
    assert [tokens for _, tokens in _fixture_debits(retry)] == [22]


@pytest.mark.parametrize("initially_anchored", [False, True])
def test_fresh_checkout_proof_for_uncommitted_enrollment_after_restart(
    project, initially_anchored
):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    reviewer_area = root.parent / "review-area"
    review = reviewer_area / "review"
    review.mkdir(parents=True)
    if initially_anchored:
        registration = replace(registration, checkout_anchors=(checkout, reviewer_area))

    path = root / "review.jsonl"
    baseline = _header(checkout) + _usage(5, BEFORE)
    path.write_bytes(baseline)
    (candidate,) = scanner.discover(registration)
    held = _checkpoint(scanner.scan(candidate, None, CUTOFF))
    store.apply(LedgerBatch(checkpoint=held))
    original = baseline + _turn(review) + _usage(7) + _usage(11) + _usage(14)
    path.write_bytes(original)
    lookahead = scanner.scan(candidate, held, CUTOFF)
    marker, boundary = _marker_and_boundary(store, lookahead.frames[2])
    old_proof = lookahead.scope_evidence(boundary)
    expected_old_anchor = (
        scanner.checkout_anchor_reference(store, reviewer_area)
        if initially_anchored
        else None
    )
    assert old_proof.anchor_ref == expected_old_anchor
    command = InboxCommand(marker.marker_id, PROJECT, marker)
    enqueue_command(store.root, command)
    with store.writer() as writer:
        (receipt,) = drain_inbox(writer, (old_proof,)).receipts
    assert receipt.disposition is MarkerDisposition.ACCEPTED
    assert receipt.anchor_ref == expected_old_anchor

    reopened = Ledger.open(store.root, PROJECT)
    view = reopened.as_of()
    assert view.checkpoints == (held,)
    (accepted,) = (
        revision.record
        for revision in view.current
        if isinstance(revision.record, ScopeEnrollment)
    )
    expanded = replace(
        registration, checkout_anchors=(*registration.checkout_anchors, review)
    )
    (updated,) = scanner.discover(expanded)
    fresh = scanner.scan(updated, held, CUTOFF)
    _, fresh_boundary = _marker_and_boundary(reopened, fresh.frames[2])
    assert fresh_boundary == accepted.boundary
    proof = fresh.scope_evidence(fresh_boundary)
    assert proof.anchor_ref == scanner.checkout_anchor_reference(reopened, review)

    if initially_anchored:
        with pytest.raises(ValueError, match="fresh evidence"):
            updated.with_enrollment(accepted, batch=fresh, evidence=proof)
        return

    no_proof = scanner.scan(updated.with_enrollment(accepted), held, CUTOFF)
    assert no_proof.cursor == held.cursor
    assert no_proof.commit_frames == ()
    assert _codes(no_proof) == {DiagnosticCode.BOUNDARY_UNVERIFIED}

    wrong_receipt = replace(proof, boundary=replace(fresh_boundary, receipt_ref=None))
    with pytest.raises(ValueError, match="fresh evidence"):
        updated.with_enrollment(accepted, batch=fresh, evidence=wrong_receipt)
    selected = updated.with_enrollment(accepted, batch=fresh, evidence=proof)
    path.write_bytes(original.replace(_usage(11), _usage(91)))
    stale = scanner.scan(selected, held, CUTOFF)
    assert stale.cursor == held.cursor
    assert stale.commit_frames == ()
    assert _codes(stale) == {DiagnosticCode.BOUNDARY_UNVERIFIED}

    path.write_bytes(original)
    admitted = scanner.scan(selected, held, CUTOFF)
    assert _codes(admitted) == set()
    assert [(frame.ordinal, tokens) for frame, tokens in _fixture_debits(admitted)] == [
        (4, 11),
        (5, 14),
    ]
    assert admitted.commit_frames[1].eligibility is Eligibility.EXCLUDED
    assert admitted.cursor.offset == path.stat().st_size
    reopened.apply(LedgerBatch(checkpoint=_checkpoint(admitted), prior_checkpoint=held))

    final = Ledger.open(store.root, PROJECT)
    assert final.command_receipt(command) == receipt
    assert accepted.anchor_ref is None
    assert accepted in [revision.record for revision in final.as_of().current]


def _claude_line(kind, *, session=SESSION, **fields):
    return (
        json.dumps(
            {"type": kind, "sessionId": str(session), **fields}, ensure_ascii=True
        ).encode()
        + b"\n"
    )


def _claude_timed(kind, cwd, *, time=AFTER, request=None):
    fields = {"cwd": str(cwd), "version": "2.1.318", "timestamp": time.isoformat()}
    if request is not None:
        fields.update(
            requestId=request,
            message={"id": f"message-{request}", "usage": {"output_tokens": 4}},
        )
    return _claude_line(kind, **fields)


def _claude_cost(**extra):
    model_usage = {
        "inputTokens": 3,
        "outputTokens": 4,
        "cacheReadInputTokens": 5,
        "cacheCreationInputTokens": 6,
        "cacheCreationEphemeral5mInputTokens": 2,
        "cacheCreationEphemeral1hInputTokens": 4,
        "thinkingTokens": 1,
        "webSearchRequests": 9,
        "costUSD": 123.45,
        "private": "model-private",
    }
    fields = {
        "startTime": 9_999_999_999_999,
        "totalCostUSD": 123.45,
        "modelUsage": {"claude-opus-5-5": model_usage},
        "private": "cost-private",
    }
    return _claude_line("cost-state", **(fields | extra))


def test_native_claude_bookkeeping_preserves_timed_segment_and_safe_sideband(project):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    path = root / "native.jsonl"
    owner_id = UUID(int=12345)
    owner = _claude_line(
        "session-owner",
        accountUuid=str(owner_id),
        organizationUuid="organization-private",
        arbitrary="owner-private",
    )
    later = AFTER + timedelta(seconds=1)
    path.write_bytes(
        owner
        + _claude_cost()
        + _claude_timed("user", checkout)
        + _claude_timed("assistant", checkout, request="first")
        + _claude_line(
            "api-request-blob",
            hash="blob-private",
            message={"value": "request-private"},
        )
        + _claude_line("atis-latch", atis="latch-private")
        + _claude_line(
            "last-prompt", lastPrompt="prompt-private", leafUuid="leaf-private"
        )
        + _claude_line("tools-used", tools=["tool-private"])
        + _claude_line("mode", mode="mode-private", cwd="/unrelated-private")
        + owner
        + _claude_timed("assistant", checkout, time=later, request="second")
        + _claude_cost()
    )

    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert _codes(batch) == set()
    assert [frame.ordinal for frame in batch.frames] == [2, 3, 10]
    assert batch.commit_frames == batch.frames
    assert [frame.row["requestId"] for frame in batch.frames[1:]] == ["first", "second"]
    assert len({frame.segment_ref for frame in batch.frames}) == 1
    assert [frame.eligibility for frame in batch.frames] == [Eligibility.ELIGIBLE] * 3
    assert batch.observed_through == later

    assert [frame.ordinal for frame in batch.sideband] == [0, 1, 9, 11]
    assert [frame.ordinal for frame in batch.commit_sideband] == [9, 11]
    assert [frame.timed_ordinal for frame in batch.sideband] == [None, None, 3, 10]
    assert [frame.segment_ref for frame in batch.sideband] == [
        None,
        None,
        batch.frames[0].segment_ref,
        batch.frames[0].segment_ref,
    ]
    owner_record, terminal = batch.commit_sideband
    assert owner_record.kind is scanner.SidebandKind.SESSION_OWNER
    assert owner_record.content == {
        "account_ref": store.pseudonymize("claude-account", str(owner_id)),
    }
    assert terminal.kind is scanner.SidebandKind.COST_STATE
    assert terminal.content == {
        "modelUsage": {
            "claude-opus-5-5": {
                "inputTokens": 3,
                "outputTokens": 4,
                "cacheReadInputTokens": 5,
                "cacheCreationInputTokens": 6,
                "cacheCreationEphemeral5mInputTokens": 2,
                "cacheCreationEphemeral1hInputTokens": 4,
            },
        },
    }
    assert terminal.provider is Provider.CLAUDE
    assert terminal.session_ref == candidate.session_ref
    assert terminal.stream_ref == candidate.stream_ref
    assert not hasattr(terminal, "observed_at")
    assert not hasattr(terminal, "eligibility")
    assert not hasattr(terminal, "pre_cutoff")
    _, invented = _marker_and_boundary(store, batch.frames[-1])
    assert batch.scope_evidence(replace(invented, ordinal=terminal.ordinal)) is None
    assert (
        batch.coverage(
            (
                scanner.FrameClassification(
                    terminal.ordinal, scanner.CoverageKind.UNFAMILIAR_USAGE
                ),
            )
        )
        == ()
    )
    assert batch.cursor.offset == path.stat().st_size
    assert "-private" not in repr(batch)
    assert str(owner_id) not in repr(batch)


def test_native_claude_sideband_respects_enrollment_frontier_and_restart(project):
    scanner = _scanner()
    registration, store = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    review = root.parent / "review"
    unrelated = root.parent / "unrelated"
    review.mkdir()
    unrelated.mkdir()
    path = root / "native.jsonl"
    before = _claude_timed("user", checkout, time=BEFORE) + _claude_cost()
    complete = (
        before
        + _claude_timed("user", review)
        + _claude_timed("assistant", review, request="unrelated-before-enrollment")
        + _claude_cost()
        + _claude_timed("assistant", review, request="first-eligible")
    )
    torn_terminal = _claude_cost()
    path.write_bytes(complete + torn_terminal[:-1])
    (candidate,) = scanner.discover(registration)
    lookahead = scanner.scan(candidate, None, CUTOFF)
    assert lookahead.cursor.offset == len(before)
    assert [entry.ordinal for entry in lookahead.sideband] == [1, 4]
    assert lookahead.commit_sideband == ()
    assert lookahead.observed_through == BEFORE

    marker, boundary = _marker_and_boundary(store, lookahead.frames[-1])
    proof = lookahead.scope_evidence(boundary)
    assert proof.anchor_ref is None
    held = _checkpoint(lookahead)
    store.apply(LedgerBatch(checkpoint=held))
    enqueue_command(store.root, InboxCommand(marker.marker_id, PROJECT, marker))
    with store.writer() as writer:
        (receipt,) = drain_inbox(writer, (proof,)).receipts
    assert receipt.disposition is MarkerDisposition.ACCEPTED

    reopened = Ledger.open(store.root, PROJECT)
    assert reopened.as_of().checkpoints == (held,)
    (accepted,) = (
        revision.record
        for revision in reopened.as_of().current
        if isinstance(revision.record, ScopeEnrollment)
    )
    (rediscovered,) = scanner.discover(registration)
    fresh = scanner.scan(rediscovered, held, CUTOFF)
    _, fresh_boundary = _marker_and_boundary(reopened, fresh.frames[-1])
    selected = rediscovered.with_enrollment(
        accepted, batch=fresh, evidence=fresh.scope_evidence(fresh_boundary)
    )
    admitted = scanner.scan(selected, held, CUTOFF)
    assert admitted.cursor.offset == len(complete)
    assert [frame.ordinal for frame in admitted.commit_frames] == [2, 3, 5]
    assert [frame.eligibility for frame in admitted.commit_frames] == [
        Eligibility.EXCLUDED,
        Eligibility.EXCLUDED,
        Eligibility.ELIGIBLE,
    ]
    assert admitted.commit_frames[-1].row["requestId"] == "first-eligible"
    assert [entry.ordinal for entry in admitted.sideband] == [4]
    assert admitted.commit_sideband == ()
    committed = _checkpoint(admitted)
    reopened.apply(LedgerBatch(checkpoint=committed, prior_checkpoint=held))

    with path.open("ab") as output:
        output.write(
            torn_terminal[-1:] + _claude_timed("user", unrelated) + _claude_cost()
        )
    reopened = Ledger.open(store.root, PROJECT)
    (durable,) = reopened.as_of().checkpoints
    (rediscovered,) = scanner.discover(registration)
    selected = rediscovered.with_enrollment(accepted)
    after_restart = scanner.scan(selected, durable, CUTOFF)
    assert [entry.ordinal for entry in after_restart.sideband] == [6, 8]
    assert [entry.ordinal for entry in after_restart.commit_sideband] == [6]
    assert after_restart.commit_sideband[0].timed_ordinal == 5
    assert after_restart.commit_frames == ()
    assert after_restart.observed_through is None
    assert after_restart.cursor.offset == len(complete + torn_terminal)
    assert _codes(after_restart) == set()

    excluded = scanner.scan(
        selected.with_exclusion(after_restart.frames[0]), durable, CUTOFF
    )
    assert [entry.ordinal for entry in excluded.commit_sideband] == [6]
    assert excluded.cursor.offset == path.stat().st_size


@pytest.mark.parametrize(
    ("bad_row", "gap"),
    [
        (
            _claude_line("unknown-sideband", arbitrary="private"),
            DiagnosticCode.MALFORMED_USAGE,
        ),
        (_claude_line("tools-used", tools="private"), DiagnosticCode.MALFORMED_USAGE),
        (
            _claude_cost(modelUsage={"claude-opus-5-5": {"outputTokens": -1}}),
            DiagnosticCode.MALFORMED_USAGE,
        ),
        (_claude_cost(timestamp=AFTER.isoformat()), DiagnosticCode.MALFORMED_USAGE),
        (b'{"type":"mode","mode":"private"}\n', DiagnosticCode.IDENTITY_CONFLICT),
        (
            _claude_line("mode", session=UUID(int=444), mode="private"),
            DiagnosticCode.IDENTITY_CONFLICT,
        ),
    ],
)
def test_native_claude_untimed_drift_or_identity_is_a_gap(project, bad_row, gap):
    scanner = _scanner()
    registration, _ = project
    (root,) = registration.source_roots
    (checkout,) = registration.checkout_anchors
    path = root / "native.jsonl"
    path.write_bytes(
        _claude_timed("user", checkout)
        + bad_row
        + _claude_cost()
        + _claude_timed("assistant", checkout, request="after-gap")
    )
    (candidate,) = scanner.discover(registration)
    batch = scanner.scan(candidate, None, CUTOFF)
    assert _codes(batch) == {gap}
    assert batch.commit_sideband == ()
    assert all(frame.ordinal != 1 for frame in batch.frames)
    if batch.cursor is not None:
        assert [entry.ordinal for entry in batch.sideband] == [2]
        assert batch.sideband[0].segment_ref is None
        assert batch.frames[0].segment_ref != batch.frames[-1].segment_ref
    assert "private" not in repr(batch)
