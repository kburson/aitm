import json
import os
import stat
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime
from threading import Barrier, Event
from uuid import UUID

import pytest

from aitm_usage import (
    ledger as store,
)
from aitm_usage import (
    scopes,
)
from aitm_usage.ledger import (
    ConflictError,
    Ledger,
    LedgerError,
    WriterActive,
    _pin_directory,
)
from aitm_usage.scopes import (
    BoundaryEvidence,
    _publication,
    attest_marker,
    drain_inbox,
    enqueue_command,
    enqueue_marker,
    resolve_scope,
    session_reference,
)
from aitm_usage.types import (
    Availability,
    BoundaryKind,
    ClientVersion,
    DevelopmentBinding,
    Diagnostic,
    DiagnosticCode,
    InboxCommand,
    ItemKey,
    ItemKind,
    LedgerBatch,
    MarkerDisposition,
    Provider,
    ReviewRole,
    Revision,
    ScopeCorrection,
    ScopeMarker,
    SourceBoundary,
    SourceRef,
    TokenCounts,
    UsageObservation,
    WorkPhase,
    decode_command,
    encode_binding,
    encode_command,
    encode_correction,
    encode_marker,
)

PROJECT = UUID(int=100)
OTHER_PROJECT = UUID(int=200)
CODEX = UUID(int=101)
CLAUDE = UUID(int=102)
NOW = datetime(2026, 11, 9, 16, tzinfo=UTC)
EPIC = ItemKey(ItemKind.ISSUE, 83)
CHILD = ItemKey(ItemKind.ISSUE, 85)
OTHER_CHILD = ItemKey(ItemKind.ISSUE, 86)


@pytest.fixture
def project(tmp_path, monkeypatch):
    # The real console script needs to discover the same project guard. Tests
    # use isolated controls via a child entry point in the ordinary pytest run.
    control = tmp_path / "control"
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: control)
    return Ledger.initialize(tmp_path / "project", PROJECT)


class Fixture:
    def __init__(self, ledger):
        self.ledger = ledger

    def ref(self, name):
        return self.ledger.pseudonymize("fixture", name)

    def marker(
        self,
        marker_id,
        sequence,
        item,
        boundary,
        *,
        provider=Provider.CODEX,
        session=CODEX,
        kind=BoundaryKind.REQUEST,
        **changes,
    ):

        marker = ScopeMarker(
            UUID(int=marker_id),
            provider,
            session_reference(self.ledger, provider, str(session)),
            sequence,
            kind,
            self.ref(boundary),
            NOW,
            item,
            WorkPhase.PLANNING,
            self.ref("author"),
            PROJECT,
            receipt_ref=self.ledger.pseudonymize(
                "scope-receipt", str(UUID(int=marker_id))
            ),
        )
        return replace(marker, **changes)

    def boundary(self, marker, position, *, proven=True, anchor=None, **changes):

        boundary = SourceBoundary(
            marker.provider,
            self.ref(f"stream:{marker.session_ref.value}"),
            marker.session_ref,
            position,
            marker.boundary_kind,
            marker.boundary_ref,
            receipt_ref=marker.receipt_ref if proven else None,
        )
        return BoundaryEvidence(replace(boundary, **changes), anchor)

    def observe(self, writer, evidence):
        boundary = evidence.boundary
        usage = UsageObservation(
            boundary,
            NOW,
            ClientVersion.UNKNOWN,
            1,
            TokenCounts(output_tokens=7),
            Availability.COMPLETE,
        )
        writer.apply(
            LedgerBatch(
                (Revision(self.ref(f"obs:{boundary.boundary_ref.value}"), 1, usage),)
            )
        )
        return usage


def test_planning_scope_and_development_owner(project):

    f = Fixture(project)
    epic = f.marker(1, 1, EPIC, "epic")
    child = f.marker(2, 2, CHILD, "first-child-request")
    second = f.marker(3, 3, OTHER_CHILD, "next-child-turn", kind=BoundaryKind.TURN)
    back = f.marker(4, 4, EPIC, "back")
    first, serial, turn, returned = (
        f.boundary(epic, 10),
        f.boundary(child, 11),
        f.boundary(second, 20),
        f.boundary(back, 21),
    )

    with project.writer() as writer:
        # Marker first. Neither an exact request ID nor an observation's time
        # authorizes a scope before source-ordered proof.
        assert enqueue_marker(project.root, epic) == epic.marker_id
        assert (
            drain_inbox(writer, ()).receipts[0].disposition is MarkerDisposition.PENDING
        )
        epic_usage = f.observe(writer, first)
        pending_view = writer.as_of()
        assert resolve_scope(epic_usage, pending_view).scope is None
        assert (
            drain_inbox(writer, (first,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )

        # Observation first. A receipt that precedes the first child model
        # request is honored even when its observation arrived earlier.
        child_usage = f.observe(writer, serial)
        assert resolve_scope(child_usage, writer.as_of()).scope.marker.item == EPIC
        enqueue_marker(project.root, child)
        assert (
            drain_inbox(writer, (serial,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )

        enqueue_marker(project.root, second)
        turn_usage = f.observe(writer, turn)
        assert (
            drain_inbox(writer, (f.boundary(second, 20, proven=False),))
            .receipts[0]
            .disposition
            is MarkerDisposition.PENDING
        )
        assert resolve_scope(turn_usage, writer.as_of()).scope is None
        between = f.observe(writer, f.boundary(f.marker(8, 5, CHILD, "between"), 19))
        assert resolve_scope(between, writer.as_of()).scope.marker.item == CHILD
        drain_inbox(writer, (turn,))

        back_usage = f.observe(writer, returned)
        enqueue_marker(project.root, back)
        drain_inbox(writer, (returned,))
        assert [
            resolve_scope(obs, writer.as_of()).scope.marker.item
            for obs in (epic_usage, child_usage, turn_usage, back_usage)
        ] == [EPIC, CHILD, OTHER_CHILD, EPIC]
        assert resolve_scope(epic_usage, pending_view).scope is None

        anchor, attempt = f.ref("checkout-anchor"), f.ref("story-attempt")
        owner_session = UUID(int=300)
        owner = f.marker(
            5,
            1,
            CHILD,
            "develop",
            session=owner_session,
            phase=WorkPhase.DEVELOPMENT,
            role=ReviewRole.AUTHOR,
            attempt_ref=attempt,
        )
        owner_boundary = f.boundary(owner, 6, anchor=anchor)
        before = f.observe(
            writer,
            f.boundary(
                owner,
                5,
                anchor=anchor,
                boundary_ref=f.ref("owner-setup"),
                receipt_ref=None,
            ),
        )
        stranger = f.marker(10, 1, CHILD, "stranger", session=UUID(int=301))
        stranger_usage = f.observe(writer, f.boundary(stranger, 30, anchor=anchor))
        enqueue_command(
            project.root,
            InboxCommand(
                owner.marker_id, PROJECT, DevelopmentBinding(owner, anchor, 1)
            ),
        )
        assert (
            drain_inbox(writer, (owner_boundary,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )
        owner_followup = f.observe(
            writer,
            f.boundary(
                owner,
                7,
                anchor=anchor,
                boundary_ref=f.ref("owner-followup"),
                receipt_ref=None,
            ),
        )
        owner_scope = resolve_scope(owner_followup, writer.as_of()).scope
        assert owner_scope.marker.participant_ref == f.ref("author")
        assert owner_scope.marker.attempt_ref == attempt
        assert owner_scope.anchor_ref == anchor
        assert owner_scope.generation == 1
        assert resolve_scope(before, writer.as_of()).scope is None
        assert resolve_scope(stranger_usage, writer.as_of()).scope is None

        reviews = [
            f.marker(
                number,
                1,
                CHILD,
                f"review-{role}",
                provider=provider,
                session=session,
                phase=WorkPhase.SOURCE_REVIEW,
                role=role,
                attempt_ref=attempt,
                participant_ref=f.ref(f"participant-{role}"),
                review_ref=f.ref("review"),
            )
            for number, provider, session, role in (
                (6, Provider.CLAUDE, CLAUDE, ReviewRole.SAR),
                (7, Provider.CODEX, UUID(int=302), ReviewRole.XPR),
            )
        ]
        for marker, checkout in zip(reviews, (None, anchor), strict=True):
            evidence = f.boundary(marker, 4, anchor=checkout)
            enqueue_marker(project.root, marker)
            drain_inbox(writer, (evidence,))
            review = resolve_scope(f.observe(writer, evidence), writer.as_of()).scope
            assert review.marker.role == marker.role
            assert review.marker.participant_ref == marker.participant_ref
            assert review.marker.review_ref == f.ref("review")

        housekeeping = f.marker(
            12,
            5,
            ItemKey(ItemKind.PROJECT),
            "housekeeping",
            phase=WorkPhase.HOUSEKEEPING,
        )
        clean = f.boundary(housekeeping, 30)
        enqueue_marker(project.root, housekeeping)
        drain_inbox(writer, (clean,))
        scope = resolve_scope(f.observe(writer, clean), writer.as_of()).scope
        assert scope.marker.item == ItemKey(ItemKind.PROJECT)
        assert scope.marker.phase is WorkPhase.HOUSEKEEPING

        contradiction = f.marker(
            13,
            2,
            OTHER_CHILD,
            "contradiction",
            session=owner_session,
            phase=WorkPhase.DEVELOPMENT,
            role=ReviewRole.AUTHOR,
            attempt_ref=attempt,
        )
        conflict = f.boundary(contradiction, 8, anchor=anchor)
        enqueue_marker(project.root, contradiction)
        assert (
            drain_inbox(writer, (conflict,)).receipts[0].disposition
            is MarkerDisposition.CONFLICT
        )
        assert resolve_scope(f.observe(writer, conflict), writer.as_of()).scope is None
        assert resolve_scope(owner_followup, writer.as_of()).scope.marker.item == CHILD


@pytest.mark.parametrize(
    "changes",
    [
        {"receipt_ref": None},
        {"ordinal": 2, "boundary_ref": "later"},
        {"session_ref": "wrong-session"},
        {"provider": Provider.CLAUDE},
        {"receipt_ref": "unrelated"},
        {"kind": BoundaryKind.REQUEST},
        {"stream_ref": "different-stream", "receipt_ref": None},
    ],
)
def test_only_matching_source_proof_attests_pre_turn(project, changes):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "claimed-next-turn", kind=BoundaryKind.TURN)
    changes = {
        name: f.ref(value) if type(value) is str else value
        for name, value in changes.items()
    }
    proof = f.boundary(marker, 1, **changes)
    assert attest_marker(marker, proof.boundary) is MarkerDisposition.PENDING
    enqueue_marker(project.root, marker)
    with project.writer() as writer:
        assert (
            drain_inbox(writer, (proof,)).receipts[0].disposition
            is MarkerDisposition.PENDING
        )
        assert (
            drain_inbox(writer, (f.boundary(marker, 1),)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )


def test_scope_correction_preserves_prior_view_and_final_receipts(project):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "correctable")
    effective = f.boundary(marker, 8)
    enqueue_marker(project.root, marker)
    with project.writer() as writer:
        drain_inbox(writer, (effective,))
        usage = f.observe(writer, effective)
        before = writer.as_of().sequence
        correction = ScopeCorrection(
            UUID(int=90),
            PROJECT,
            replace(marker, item=OTHER_CHILD),
            f.ref("correction-evidence"),
        )
        command = InboxCommand(correction.correction_id, PROJECT, correction)
        enqueue_command(project.root, command)
        result = drain_inbox(writer, ()).receipts[0]
        assert result.disposition is MarkerDisposition.ACCEPTED
        committed = writer.as_of()
        assert resolve_scope(usage, writer.as_of(before)).scope.marker.item == CHILD
        fixed = resolve_scope(usage, committed)
        assert fixed.scope.marker.item == OTHER_CHILD
        assert fixed.revision.revision == 2
        assert enqueue_command(project.root, command) == result
        assert drain_inbox(writer, ()).receipts == ()
        assert writer.as_of() == committed
        with pytest.raises(ConflictError):
            enqueue_command(
                project.root,
                replace(
                    command,
                    payload=replace(correction, replacement=replace(marker, item=EPIC)),
                ),
            )
        assert writer.as_of() == committed

        invalid = ScopeCorrection(
            UUID(int=91),
            PROJECT,
            replace(marker, boundary_ref=f.ref("earlier")),
            f.ref("invalid"),
        )
        enqueue_command(
            project.root, InboxCommand(invalid.correction_id, PROJECT, invalid)
        )
        assert (
            drain_inbox(writer, ()).receipts[0].disposition
            is MarkerDisposition.CONFLICT
        )
        assert resolve_scope(usage, writer.as_of()).scope.marker.item == OTHER_CHILD


@pytest.mark.parametrize("sequence, ordinal", [(1, 9), (2, 7), (2, 8)])
def test_quarantines_duplicate_sequence_and_retroactive_boundary(
    project, sequence, ordinal
):

    f = Fixture(project)
    original = f.marker(1, 1, EPIC, "valid")
    conflicting = f.marker(2, sequence, CHILD, "different")
    known, proposed = f.boundary(original, 8), f.boundary(conflicting, ordinal)
    with project.writer() as writer:
        enqueue_marker(project.root, original)
        drain_inbox(writer, (known,))
        enqueue_marker(project.root, conflicting)
        assert (
            drain_inbox(writer, (proposed,)).receipts[0].disposition
            is MarkerDisposition.CONFLICT
        )
        usage = f.observe(writer, proposed)
        assert resolve_scope(usage, writer.as_of()).scope is None


def test_binding_checks_anchor_session_and_monotonic_generation(project):

    f = Fixture(project)
    anchor, attempt = f.ref("approved-checkout"), f.ref("attempt")
    owner = f.marker(
        1, 1, CHILD, "owner", phase=WorkPhase.DEVELOPMENT, attempt_ref=attempt
    )
    proven = f.boundary(owner, 1, anchor=anchor)
    command = InboxCommand(
        owner.marker_id, PROJECT, DevelopmentBinding(owner, anchor, 1)
    )
    with project.writer() as writer:
        enqueue_command(project.root, command)
        wrong_source = replace(proven, anchor_ref=f.ref("other-checkout"))
        assert (
            drain_inbox(writer, (wrong_source,)).receipts[0].disposition
            is MarkerDisposition.PENDING
        )
        assert resolve_scope(f.observe(writer, proven), writer.as_of()).scope is None
        assert (
            drain_inbox(writer, (proven,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )

        impostor = f.marker(
            2,
            1,
            CHILD,
            "other-owner",
            session=UUID(int=300),
            phase=WorkPhase.DEVELOPMENT,
            attempt_ref=attempt,
        )
        enqueue_command(
            project.root,
            InboxCommand(
                impostor.marker_id, PROJECT, DevelopmentBinding(impostor, anchor, 1)
            ),
        )
        replay_generation = f.boundary(impostor, 1, anchor=anchor)
        assert (
            drain_inbox(writer, (replay_generation,)).receipts[0].disposition
            is MarkerDisposition.CONFLICT
        )
        assert (
            resolve_scope(f.observe(writer, replay_generation), writer.as_of()).scope
            is None
        )


def test_cli_publication_is_private_authenticated_and_lease_free(project, tmp_path):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "cli")
    proof = f.boundary(marker, 8)
    marker_file = tmp_path / "marker.json"
    marker_file.write_bytes(encode_marker(marker))
    env = dict(os.environ, CODEX_THREAD_ID=str(CODEX))
    # Invoke the installed console script in a separate interpreter using
    # the same isolated project guard.
    entry = (
        "import runpy, sys; from pathlib import Path; from aitm_usage import ledger;"
        f"ledger._control_root = lambda: Path({str(tmp_path / 'control')!r});"
        "runpy.run_path(str(Path(sys.executable).with_name('aitm-usage')), run_name='__main__')"
    )

    def cli(group, command, option, input_file, *extra, **overrides):
        return subprocess.run(
            [
                sys.executable,
                "-c",
                entry,
                "--project",
                str(project.root),
                group,
                command,
                option,
                str(input_file),
                "--json",
                *extra,
            ],
            env=env | overrides,
            capture_output=True,
            text=True,
            check=False,
        )

    with project.writer() as writer:
        with pytest.raises(WriterActive), project.writer():
            pass
        wrong_session = cli(
            "scope", "mark", "--marker", marker_file, CODEX_THREAD_ID=str(CLAUDE)
        )
        assert wrong_session.returncode != 0
        assert str(CLAUDE) not in wrong_session.stderr
        assert not (project.root / "inbox").exists()
        result = cli("scope", "mark", "--marker", marker_file)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout) == {
            "command_id": str(marker.marker_id),
            "status": "queued",
        }
        inbox = project.root / "inbox"
        assert stat.S_IMODE(inbox.stat().st_mode) == 0o700
        command_file = inbox / f"{marker.marker_id}.json"
        assert stat.S_IMODE(command_file.stat().st_mode) == 0o600
        original_bytes = command_file.read_bytes()
        changed = tmp_path / "changed.json"
        changed.write_bytes(encode_marker(replace(marker, item=OTHER_CHILD)))
        assert cli("scope", "mark", "--marker", changed).returncode != 0
        assert command_file.read_bytes() == original_bytes

        assert (
            drain_inbox(writer, ()).receipts[0].disposition is MarkerDisposition.PENDING
        )
        assert (
            json.loads(cli("scope", "mark", "--marker", marker_file).stdout)["status"]
            == "pending"
        )
        assert (
            drain_inbox(writer, (proof,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )
        assert (
            json.loads(cli("scope", "mark", "--marker", marker_file).stdout)["status"]
            == "accepted"
        )
        assert not command_file.exists()
        ack = inbox / "acks" / command_file.name
        assert stat.S_IMODE(ack.stat().st_mode) == 0o600
        assert json.loads(ack.read_text())["disposition"] == "accepted"

        owner = f.marker(
            2,
            2,
            CHILD,
            "cli-bind",
            phase=WorkPhase.DEVELOPMENT,
            attempt_ref=f.ref("attempt"),
        )
        anchor = f.ref("anchor")
        binding = tmp_path / "binding.json"
        binding.write_bytes(encode_binding(DevelopmentBinding(owner, anchor, 1)))
        result = cli("development", "bind", "--binding", binding)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["status"] == "queued"
        assert (
            drain_inbox(writer, (f.boundary(owner, 9, anchor=anchor),))
            .receipts[0]
            .disposition
            is MarkerDisposition.ACCEPTED
        )

        correction = tmp_path / "correction.json"
        correction.write_bytes(
            encode_correction(
                ScopeCorrection(
                    UUID(int=90),
                    PROJECT,
                    replace(marker, item=OTHER_CHILD),
                    f.ref("correction"),
                )
            )
        )
        result = cli("scope", "correct", "--correction", correction)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)["status"] == "queued"
        assert (
            drain_inbox(writer, ()).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )

        review = f.marker(
            3,
            1,
            CHILD,
            "claude-review",
            provider=Provider.CLAUDE,
            session=CLAUDE,
            phase=WorkPhase.SOURCE_REVIEW,
            role=ReviewRole.SAR,
            participant_ref=f.ref("reviewer"),
            review_ref=f.ref("review"),
        )
        review_file = tmp_path / "review.json"
        review_file.write_bytes(encode_marker(review))
        assert cli("scope", "mark", "--marker", review_file).returncode != 0
        assert (
            cli(
                "scope", "mark", "--marker", review_file, "--session-id", str(CODEX)
            ).returncode
            != 0
        )
        result = cli(
            "scope", "mark", "--marker", review_file, "--session-id", str(CLAUDE)
        )
        assert result.returncode == 0, result.stderr
        assert (
            drain_inbox(writer, (f.boundary(review, 1),)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )

        extras = tmp_path / "extra.json"
        raw = json.loads(encode_marker(marker))
        extras.write_text(json.dumps(raw | {"credential": "raw-tool-input-canary"}))
        failure = cli("scope", "mark", "--marker", extras)
        assert failure.returncode != 0
        assert "raw-tool-input-canary" not in failure.stderr
        for path in project.root.rglob("*"):
            if path.is_file():
                contents = path.read_bytes()
                assert str(CODEX).encode() not in contents
                assert str(CLAUDE).encode() not in contents
                assert b"raw-tool-input-canary" not in contents


def test_publication_and_consumption_reject_unsafe_or_untyped_inputs(project, tmp_path):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "valid")
    foreign = Ledger.initialize(tmp_path / "foreign", OTHER_PROJECT)
    fabricated = SourceRef(f"hmac-sha256:{'a' * 64}:{'b' * 64}")
    for bad in (
        replace(marker, project_id=OTHER_PROJECT),
        replace(marker, participant_ref=foreign.pseudonymize("fixture", "foreign")),
        replace(marker, participant_ref=fabricated),
        replace(marker, receipt_ref=f.ref("other-receipt")),
        replace(marker, phase="raw-phase-canary"),
    ):
        with pytest.raises((LedgerError, ValueError)):
            enqueue_marker(project.root, bad)
    assert not (project.root / "inbox").exists()

    enqueue_marker(project.root, marker)
    inbox = project.root / "inbox"
    complete = (inbox / f"{marker.marker_id}.json").read_bytes()
    (inbox / ".partial-command").write_bytes(complete[:40])
    malformed_id = UUID(int=4)
    malformed = inbox / f"{malformed_id}.json"
    malformed.write_bytes(complete + b"\n")
    malformed.chmod(0o600)
    forged = inbox / f"{UUID(int=5)}.json"
    forged.write_bytes(
        encode_command(
            InboxCommand(
                UUID(int=5),
                PROJECT,
                replace(marker, marker_id=UUID(int=5), participant_ref=fabricated),
            )
        )
    )
    forged.chmod(0o600)
    linked = inbox / f"{UUID(int=6)}.json"
    linked.symlink_to(malformed)
    deeply_nested = inbox / f"{UUID(int=7)}.json"
    deeply_nested.write_bytes(b"[" * 10000 + b"]" * 10000)
    deeply_nested.chmod(0o600)
    with project.writer() as writer:
        report = drain_inbox(writer, (f.boundary(marker, 8),))
        assert len(report.receipts) == 1
        assert report.invalid_publications == 4
        assert (inbox / ".partial-command").exists()
    assert len(project.as_of().revisions) == 2


def test_local_commit_rolls_back_effect_and_replays_before_ack(project, monkeypatch):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "retry")
    scopes.enqueue_marker(project.root, marker)
    proof = f.boundary(marker, 8)
    append = store._append_revisions

    def fail_after_first_insert(conn, sequence, revisions):
        append(conn, sequence, revisions[:1])
        raise OSError("controlled append interruption")

    def fail_before_ack(*_args, **_kwargs):
        raise OSError("controlled ack interruption")

    with project.writer() as writer:
        with monkeypatch.context() as m:
            m.setattr(store, "_append_revisions", fail_after_first_insert)
            with pytest.raises(OSError, match="append interruption"):
                scopes.drain_inbox(writer, (proof,))
        assert writer.as_of().sequence == 0
        assert writer.as_of().revisions == ()

        with monkeypatch.context() as m:
            m.setattr(scopes, "_acknowledge", fail_before_ack)
            with pytest.raises(OSError, match="ack interruption"):
                scopes.drain_inbox(writer, (proof,))
        committed = writer.as_of()
        assert committed.sequence == 1
        assert len(committed.revisions) == 2
        assert not (
            project.root / "inbox" / "acks" / f"{marker.marker_id}.json"
        ).exists()

    with Ledger.open(project.root, PROJECT).writer() as writer:
        report = scopes.drain_inbox(writer, ())
        assert report.receipts[0].disposition is MarkerDisposition.ACCEPTED
        assert writer.as_of() == committed
        assert scopes.drain_inbox(writer, ()).receipts == ()


def test_correction_can_recover_quarantined_scope_with_recorded_proof(project):

    f = Fixture(project)
    anchor, attempt = f.ref("anchor"), f.ref("attempt")
    owner = f.marker(
        1, 1, CHILD, "bind", phase=WorkPhase.DEVELOPMENT, attempt_ref=attempt
    )
    claim = f.marker(2, 2, OTHER_CHILD, "wrong-item", attempt_ref=attempt)
    proof = f.boundary(claim, 2, anchor=anchor)
    enqueue_command(
        project.root,
        InboxCommand(owner.marker_id, PROJECT, DevelopmentBinding(owner, anchor, 1)),
    )
    enqueue_marker(project.root, claim)
    with project.writer() as writer:
        report = drain_inbox(writer, (f.boundary(owner, 1, anchor=anchor), proof))
        assert [receipt.disposition for receipt in report.receipts] == [
            MarkerDisposition.ACCEPTED,
            MarkerDisposition.CONFLICT,
        ]
        usage = f.observe(writer, proof)
        before = writer.as_of()
        assert resolve_scope(usage, before).reason is MarkerDisposition.CONFLICT

    correction = ScopeCorrection(
        UUID(int=90), PROJECT, replace(claim, item=CHILD), f.ref("conflict-decision")
    )
    enqueue_command(
        project.root, InboxCommand(correction.correction_id, PROJECT, correction)
    )
    with Ledger.open(project.root, PROJECT).writer() as writer:
        assert (
            drain_inbox(writer, ()).receipts[-1].disposition
            is MarkerDisposition.ACCEPTED
        )
        assert resolve_scope(usage, writer.as_of()).scope.marker.item == CHILD
        assert resolve_scope(usage, writer.as_of(before.sequence)).scope is None


def test_bound_owner_cannot_claim_development_in_an_unproven_stream(project):

    f = Fixture(project)
    anchor, attempt = f.ref("anchor"), f.ref("attempt")
    owner = f.marker(
        1, 1, CHILD, "bind", phase=WorkPhase.DEVELOPMENT, attempt_ref=attempt
    )
    other = f.marker(2, 2, OTHER_CHILD, "contradictory", attempt_ref=attempt)
    enqueue_command(
        project.root,
        InboxCommand(owner.marker_id, PROJECT, DevelopmentBinding(owner, anchor, 1)),
    )
    enqueue_marker(project.root, other)
    unknown_stream = f.boundary(other, 1, stream_ref=f.ref("other-stream"))
    with project.writer() as writer:
        outcomes = drain_inbox(
            writer, (f.boundary(owner, 1, anchor=anchor), unknown_stream)
        )
        assert [receipt.disposition for receipt in outcomes.receipts] == [
            MarkerDisposition.ACCEPTED,
            MarkerDisposition.CONFLICT,
        ]
        usage = f.observe(writer, unknown_stream)
        assert resolve_scope(usage, writer.as_of()).reason is MarkerDisposition.CONFLICT


def test_exclusive_publication_keeps_one_concurrent_command(project):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "shared-command-id")
    barrier = Barrier(2)
    first = InboxCommand(marker.marker_id, PROJECT, marker)
    second = replace(first, payload=replace(marker, item=OTHER_CHILD))

    def publish(command):
        barrier.wait(timeout=5)
        try:
            enqueue_command(project.root, command)
        except ConflictError:
            return False
        return True

    with project.writer() as writer, ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(publish, (first, second))) == [False, True]
        path = project.root / "inbox" / f"{first.command_id}.json"
        winner = decode_command(path.read_bytes())
        outcomes = drain_inbox(writer, (f.boundary(marker, 1),))
        assert outcomes.receipts[0].command == winner
        assert outcomes.receipts[0].disposition is MarkerDisposition.ACCEPTED
        assert not path.exists()


def test_final_commit_cannot_race_conflicting_publication(project, monkeypatch):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "shared-command-id")
    command = InboxCommand(marker.marker_id, PROJECT, marker)
    conflicting = replace(command, payload=replace(marker, item=OTHER_CHILD))
    scopes.enqueue_command(project.root, command)
    publisher_read = Event()
    retirement_done = Event()
    original_read = Ledger.command_receipt

    def delay_first_receipt_read(ledger, proposed):
        previous = original_read(ledger, proposed)
        if proposed == conflicting and previous is None and not publisher_read.is_set():
            publisher_read.set()
            assert retirement_done.wait(timeout=10)
        return previous

    monkeypatch.setattr(Ledger, "command_receipt", delay_first_receipt_read)
    with project.writer() as writer, ThreadPoolExecutor(max_workers=1) as pool:
        retry = pool.submit(scopes.enqueue_command, project.root, conflicting)
        try:
            assert publisher_read.wait(timeout=5)
            outcome = scopes.drain_inbox(writer, (f.boundary(marker, 1),)).receipts[0]
            assert outcome.disposition is MarkerDisposition.ACCEPTED
        finally:
            retirement_done.set()
        with pytest.raises(ConflictError):
            retry.result(timeout=5)
        assert not (project.root / "inbox" / f"{command.command_id}.json").exists()
        assert writer.command_receipt(command) == outcome
        assert scopes.drain_inbox(writer, ()).receipts == ()


def test_inbox_directory_refuses_symlink_destination(project, tmp_path):

    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "protected")
    target = tmp_path / "elsewhere"
    target.mkdir(mode=0o700)
    (project.root / "inbox").symlink_to(target, target_is_directory=True)
    with pytest.raises(LedgerError):
        enqueue_marker(project.root, marker)
    with pytest.raises(LedgerError), project.writer() as writer:
        drain_inbox(writer, ())
    assert list(target.iterdir()) == []
    assert project.as_of().sequence == 0


def test_delayed_owner_boundary_quarantines_already_seen_contradictory_marker(project):

    f = Fixture(project)
    anchor, attempt = f.ref("anchor"), f.ref("attempt")
    owner = f.marker(
        1, 1, CHILD, "owner", phase=WorkPhase.DEVELOPMENT, attempt_ref=attempt
    )
    contrary = f.marker(2, 2, OTHER_CHILD, "contrary", attempt_ref=attempt)
    owner_proof = f.boundary(owner, 8, anchor=anchor)
    marker_proof = f.boundary(contrary, 9, anchor=anchor)

    enqueue_marker(project.root, contrary)
    with project.writer() as writer:
        assert (
            drain_inbox(writer, (marker_proof,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )
        usage = f.observe(writer, marker_proof)
        before = writer.as_of()
        assert resolve_scope(usage, before).scope.marker.item == OTHER_CHILD

        enqueue_command(
            project.root,
            InboxCommand(
                owner.marker_id, PROJECT, DevelopmentBinding(owner, anchor, 1)
            ),
        )
        assert (
            drain_inbox(writer, (owner_proof,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )
        assert resolve_scope(usage, writer.as_of()).reason is MarkerDisposition.CONFLICT
        assert (
            resolve_scope(usage, writer.as_of(before.sequence)).scope.marker.item
            == OTHER_CHILD
        )


def test_publication_mutex_excludes_other_process_on_pinned_inbox(project):

    f = Fixture(project)
    enqueue_marker(project.root, f.marker(1, 1, CHILD, "publication-mutex"))
    probe = """
import fcntl
import os
import sys

fd = os.open(sys.argv[1], os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
try:
    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    sys.exit(9)
"""

    with _pin_directory(project.root / "inbox") as pinned:
        with _publication(pinned):
            assert (
                subprocess.run(
                    [sys.executable, "-c", probe, str(pinned.path)], check=False
                ).returncode
                == 9
            )
        assert (
            subprocess.run(
                [sys.executable, "-c", probe, str(pinned.path)], check=False
            ).returncode
            == 0
        )
        with pytest.raises(LedgerError, match="Pinned private ledger path changed"):
            with _publication(pinned):
                pinned.path.rename(pinned.path.with_name("moved-inbox"))
                pinned.path.mkdir(mode=0o700)


def test_review_outside_checkout_cannot_claim_wrong_attempt(project):
    f = Fixture(project)
    anchor, attempt = f.ref("anchor"), f.ref("attempt")
    owner = f.marker(
        1, 1, CHILD, "owner", phase=WorkPhase.DEVELOPMENT, attempt_ref=attempt
    )
    reviewer = f.marker(
        2,
        1,
        CHILD,
        "review",
        provider=Provider.CLAUDE,
        session=CLAUDE,
        phase=WorkPhase.SOURCE_REVIEW,
        role=ReviewRole.SAR,
        participant_ref=f.ref("reviewer"),
        attempt_ref=f.ref("wrong-attempt"),
        review_ref=f.ref("review-id"),
    )
    enqueue_command(
        project.root,
        InboxCommand(owner.marker_id, PROJECT, DevelopmentBinding(owner, anchor, 1)),
    )
    enqueue_marker(project.root, reviewer)
    with project.writer() as writer:
        outcomes = drain_inbox(
            writer, (f.boundary(owner, 1, anchor=anchor), f.boundary(reviewer, 1))
        )
        assert [receipt.disposition for receipt in outcomes.receipts] == [
            MarkerDisposition.ACCEPTED,
            MarkerDisposition.CONFLICT,
        ]


def test_development_marker_waits_for_owner_binding(project):
    f = Fixture(project)
    anchor, attempt = f.ref("anchor"), f.ref("attempt")
    owner = f.marker(
        1, 1, CHILD, "owner", phase=WorkPhase.DEVELOPMENT, attempt_ref=attempt
    )
    marker = f.marker(
        2,
        2,
        CHILD,
        "explicit-development",
        phase=WorkPhase.DEVELOPMENT,
        attempt_ref=attempt,
    )
    proof = f.boundary(marker, 20, anchor=anchor)
    enqueue_marker(project.root, marker)

    with project.writer() as writer:
        initial = drain_inbox(writer, ()).receipts[0]
        assert initial.boundary is None
        pending = drain_inbox(writer, (proof,)).receipts[0]
        assert pending.disposition is MarkerDisposition.PENDING
        assert pending.boundary == proof.boundary
        assert pending.anchor_ref == anchor
        usage = f.observe(writer, proof)
        before = writer.as_of()
        assert resolve_scope(usage, before).reason is MarkerDisposition.PENDING

        enqueue_command(
            project.root,
            InboxCommand(
                owner.marker_id, PROJECT, DevelopmentBinding(owner, anchor, 1)
            ),
        )
        outcomes = drain_inbox(
            writer,
            (f.boundary(owner, 10, anchor=anchor), replace(proof, anchor_ref=None)),
        )
        assert [receipt.disposition for receipt in outcomes.receipts] == [
            MarkerDisposition.ACCEPTED,
            MarkerDisposition.ACCEPTED,
        ]
        assert (
            resolve_scope(usage, writer.as_of()).scope.marker.marker_id
            == marker.marker_id
        )
        assert resolve_scope(usage, writer.as_of(before.sequence)).scope is None


@pytest.mark.parametrize(
    ("generation", "ordinal", "expected"),
    [
        (1, 10, MarkerDisposition.ACCEPTED),
        (3, 10, MarkerDisposition.CONFLICT),
        (1, 30, MarkerDisposition.CONFLICT),
    ],
)
def test_same_stream_binding_generations_follow_proven_order(
    project, generation, ordinal, expected
):
    f = Fixture(project)
    anchor = f.ref("anchor")
    known = f.marker(
        1,
        20,
        CHILD,
        "known",
        phase=WorkPhase.DEVELOPMENT,
        attempt_ref=f.ref("known-attempt"),
    )
    proposed = f.marker(
        2,
        ordinal,
        CHILD,
        "proposed",
        phase=WorkPhase.DEVELOPMENT,
        attempt_ref=f.ref("proposed-attempt"),
    )
    with project.writer() as writer:
        enqueue_command(
            project.root,
            InboxCommand(
                known.marker_id, PROJECT, DevelopmentBinding(known, anchor, 2)
            ),
        )
        known_proof = f.boundary(known, 20, anchor=anchor)
        assert (
            drain_inbox(writer, (known_proof,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )
        enqueue_command(
            project.root,
            InboxCommand(
                proposed.marker_id,
                PROJECT,
                DevelopmentBinding(proposed, anchor, generation),
            ),
        )
        proof = f.boundary(proposed, ordinal, anchor=anchor)
        assert drain_inbox(writer, (proof,)).receipts[0].disposition is expected
        if expected is MarkerDisposition.ACCEPTED:
            old = f.observe(writer, proof)
            new = f.observe(writer, known_proof)
            assert resolve_scope(old, writer.as_of()).scope.generation == 1
            assert resolve_scope(new, writer.as_of()).scope.generation == 2


def test_cross_stream_rebind_preserves_recorded_prefix_only(project):
    f = Fixture(project)
    anchor = f.ref("anchor")
    previous = f.marker(
        1,
        1,
        CHILD,
        "previous-owner",
        phase=WorkPhase.DEVELOPMENT,
        attempt_ref=f.ref("previous-attempt"),
    )
    new = f.marker(
        2,
        1,
        CHILD,
        "new-owner",
        phase=WorkPhase.DEVELOPMENT,
        attempt_ref=f.ref("new-attempt"),
        session=UUID(int=300),
    )
    with project.writer() as writer:
        enqueue_command(
            project.root,
            InboxCommand(
                previous.marker_id, PROJECT, DevelopmentBinding(previous, anchor, 1)
            ),
        )
        drain_inbox(writer, (f.boundary(previous, 10, anchor=anchor),))
        old_scope = f.marker(3, 2, CHILD, "recorded-old-observation")
        old = f.observe(writer, f.boundary(old_scope, 12, proven=False, anchor=anchor))
        before = writer.as_of()
        assert resolve_scope(old, before).scope.generation == 1

        enqueue_command(
            project.root,
            InboxCommand(new.marker_id, PROJECT, DevelopmentBinding(new, anchor, 2)),
        )
        new_proof = f.boundary(new, 1, anchor=anchor)
        assert (
            drain_inbox(writer, (new_proof,)).receipts[0].disposition
            is MarkerDisposition.ACCEPTED
        )

        later = f.marker(4, 3, CHILD, "newly-observed-old-stream")
        unproven = f.observe(writer, f.boundary(later, 11, proven=False, anchor=anchor))
        new_usage = f.observe(writer, new_proof)
        corrected_usage = replace(old, tokens=TokenCounts(output_tokens=11))
        writer.apply(
            LedgerBatch(
                (
                    Revision(
                        f.ref(f"obs:{old.boundary.boundary_ref.value}"),
                        2,
                        corrected_usage,
                    ),
                )
            )
        )

        view = writer.as_of()
        assert resolve_scope(unproven, view).scope is None
        assert resolve_scope(new_usage, view).scope.generation == 2
        assert resolve_scope(corrected_usage, view).scope.generation == 1
        assert resolve_scope(old, writer.as_of(before.sequence)).scope.generation == 1


def test_pending_receipt_refines_location_without_authorizing_attribution(project):
    f = Fixture(project)
    epic = f.marker(1, 1, EPIC, "epic")
    marker = f.marker(2, 2, CHILD, "claimed-child-start")
    before_target = f.marker(3, 3, EPIC, "known-earlier-observation")
    hint = f.boundary(marker, 12, proven=False)
    proven = f.boundary(marker, 12)
    command = InboxCommand(marker.marker_id, PROJECT, marker)

    with project.writer() as writer:
        enqueue_marker(project.root, epic)
        drain_inbox(writer, (f.boundary(epic, 10),))
        earlier = f.observe(writer, f.boundary(before_target, 11, proven=False))
        target = f.observe(writer, hint)
        enqueue_command(project.root, command)
        initial = drain_inbox(writer, ()).receipts[0]
        assert initial.boundary is None
        before = writer.as_of()
        assert resolve_scope(earlier, before).reason is MarkerDisposition.PENDING

        located = drain_inbox(writer, (hint,)).receipts[0]
        assert located.disposition is MarkerDisposition.PENDING
        assert located.boundary == hint.boundary
        refined = writer.as_of()
        assert resolve_scope(earlier, refined).scope.marker.item == EPIC
        assert resolve_scope(target, refined).reason is MarkerDisposition.PENDING
        assert drain_inbox(writer, ()).receipts == (located,)
        assert drain_inbox(writer, (hint,)).receipts == (located,)
        assert enqueue_command(project.root, command) == located
        assert writer.as_of() == refined

        accepted = drain_inbox(writer, (proven,)).receipts[0]
        assert accepted.disposition is MarkerDisposition.ACCEPTED
        committed = writer.as_of()
        assert resolve_scope(target, committed).scope.marker.item == CHILD
        assert resolve_scope(earlier, writer.as_of(before.sequence)).scope is None
        assert resolve_scope(target, writer.as_of(refined.sequence)).scope is None
        assert enqueue_command(project.root, command) == accepted
        assert (
            writer.commit_command(located, (), expected_sequence=committed.sequence)
            == accepted
        )
        assert writer.as_of() == committed


def test_common_drain_applies_typed_effect_tuple_in_one_commit(project, monkeypatch):
    f = Fixture(project)
    marker = f.marker(1, 1, CHILD, "diagnostic-and-scope")
    diagnostic = Revision(
        f.ref("diagnostic"), 1, Diagnostic(DiagnosticCode.COVERAGE_GAP, NOW)
    )
    evaluate = scopes._evaluate

    def with_diagnostic(*args, **kwargs):
        status, evidence, effects = evaluate(*args, **kwargs)
        return status, evidence, (*effects, diagnostic)

    monkeypatch.setattr(scopes, "_evaluate", with_diagnostic)
    enqueue_marker(project.root, marker)
    with project.writer() as writer:
        receipt = drain_inbox(writer, (f.boundary(marker, 8),)).receipts[0]
        assert receipt.disposition is MarkerDisposition.ACCEPTED
        assert writer.as_of().sequence == 1
        assert len(writer.as_of().revisions) == 3
        assert diagnostic in writer.as_of().current
