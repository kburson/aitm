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


def _marker_and_boundary(store, frame):
    marker_id = UUID(int=120)
    marker = ScopeMarker(
        marker_id,
        frame.provider,
        frame.session_ref,
        1,
        BoundaryKind.REQUEST,
        store.pseudonymize("request", "enrolled-reviewer-first"),
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
