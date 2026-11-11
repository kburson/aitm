"""Exercise routing journal authority with real native capture and scope evidence."""

import json
import os
import shlex
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from shutil import copyfile
from types import SimpleNamespace
from uuid import UUID

import pytest
from test_codex import (
    AFTER,
    CUTOFF,
    begin,
    counter,
    end,
    response,
    startup,
    tool_call,
    tool_output,
    usage,
    write,
)

from aitm_usage.ledger import ConflictError, Ledger, LedgerError
from aitm_usage.monitor_registry import (
    CaptureChange,
    ProjectRegistrationRequest,
    Registry,
    SourceApprovalRequest,
)
from aitm_usage.monitor_scope import Mark, Scope, ScopeState
from aitm_usage.sources.adapter import ProviderAdapter, SourceRoot
from aitm_usage.types import BoundaryKind, DiagnosticCode, ItemKey, ItemKind, WorkPhase

A, B, LIVE, COPY = (UUID(int=number) for number in range(1, 5))


@pytest.fixture
def journal_disposition(tmp_path, monkeypatch, capsys):
    from test_monitor_scope import (
        SOURCE,
        NativeScopeFixture,
        _authorize_handoff,
        _issue,
        _sealed_disposition,
        _verify,
    )

    from aitm_usage.monitor_journal import RoutingJournal
    from aitm_usage.monitor_scope import Disposition

    @contextmanager
    def prepare(release_previous=False):
        monkeypatch.setattr(
            "aitm_usage.ledger._control_root", lambda: tmp_path / "control"
        )
        native = NativeScopeFixture(tmp_path, monkeypatch)
        with native.registry.writer() as writer:
            scopes = ScopeState(writer)
            journal = RoutingJournal(writer, scopes)
            owner = scopes.operator(A)
            mark_id, hold_id, legacy_id, command_id = (
                UUID(int=number) for number in range(0x630, 0x634)
            )
            mark = Mark(mark_id, _issue(A, 209), native.receipt_ref(mark_id))
            scopes.authorize(mark, owner)
            _, mark_at = native.append(mark_id)
            batch = scopes.read_source(SOURCE, native.locator())
            scopes.apply_mark(
                mark, _verify(scopes, native, mark, owner, batch, mark_at)
            )
            prior = journal.prepare(SOURCE, native.locator())
            journal.reserve_batch(prior)
            assert journal.cursor_for(SOURCE, native.locator()) is None
            # Seed the verified earlier cursor as fixture setup. The ordinary
            # journal retains the unresolved preexisting routing diagnostics.
            sequence = journal.as_of().sequence + 1
            with journal._store.transaction(write=True) as connection:
                journal._write_progress(connection, prior._read, sequence)
            prior_cursor = journal.cursor_for(SOURCE, native.locator())
            assert prior_cursor == prior.progress

            handoff, _ = _authorize_handoff(
                scopes, native, hold_id, A, _issue(B, 209), 1
            )
            _, held_at = native.append(hold_id)
            legacy = Disposition(
                legacy_id,
                A,
                hold_id,
                native.receipt_ref(legacy_id),
                release_previous=True,
            )
            scopes.authorize(legacy, owner)
            _, legacy_at = native.append(legacy_id)
            batch = scopes.read_source(SOURCE, native.locator())
            receipt = _verify(scopes, native, handoff, owner, batch, held_at)
            assert receipt.affected.start <= legacy_at < receipt.affected.end
            assert (receipt.affected.start, receipt.affected.end) == (41, 62)

            prepared = journal.prepare(SOURCE, native.locator())
            first, later, *_ = (
                item
                for item in prepared.candidates
                if receipt.affected.start <= item.observation.usage.boundary.ordinal
                and item.observation.span_end <= receipt.affected.end
            )
            assert journal.reserve(first, prepared.progress).status == "pending"
            assert journal.cursor_for(SOURCE, native.locator()) == prior_cursor
            hold = scopes.hold(receipt, retain_route_target=True)
            prefix = native.path.read_bytes()

            command = Disposition(
                command_id, A, hold_id, native.receipt_ref(command_id), release_previous
            )
            inbox, reader, request, _, target, batch, followup, when = (
                _sealed_disposition(
                    native, writer, scopes, command, tmp_path, monkeypatch, capsys
                )
            )
            terminal = scopes.verify_boundary(command, owner, batch, target)
            proof = scopes.verify_route_disposition(command, terminal)
            assert batch.cursor is None
            assert proof.hold == hold and hold.state == "held"
            assert proof.record.boundary.ordinal >= hold.affected.end
            assert (
                proof.record.boundary.session_ref,
                proof.record.boundary.stream_ref,
            ) == (
                hold.position.session_ref,
                hold.position.stream_ref,
            )
            yield SimpleNamespace(
                native=native,
                scopes=scopes,
                journal=journal,
                owner=owner,
                source_id=SOURCE,
                first=first.observation.key,
                later=later.observation.key,
                proof=proof,
                command=command,
                inbox=inbox,
                reader=reader,
                request=request,
                legacy=legacy,
                legacy_at=legacy_at,
                followup=followup,
                when=when,
                prefix=prefix,
                prior_cursor=prior_cursor,
                scope_file=writer.root / "scope-v1.json",
            )

    return prepare


def _prior_journal_rows(journal):
    with journal._store.transaction() as connection:
        return {
            table: connection.execute(
                f"SELECT * FROM {table} ORDER BY rowid"
            ).fetchall()
            for table in (
                "claims",
                "claim_revisions",
                "disputes",
                "content_disputes",
                "progress",
            )
        }


@pytest.mark.parametrize("release_previous", [False, True], ids=["gap", "resolved"])
def test_journal_records_native_disposition_without_settlement(
    journal_disposition, release_previous
):
    with journal_disposition(release_previous) as case:
        journal = case.journal
        before = journal.as_of()
        rows = _prior_journal_rows(journal)
        scope_bytes = case.scope_file.read_bytes()
        scope_view = case.scopes.view()
        change = journal.record_disposition(case.proof)
        assert change.sequence == before.sequence + 1
        assert change.disposition.record == case.proof.record
        assert change.disposition.record.outcome == (
            "resolved" if release_previous else "gap"
        )
        assert change.disposition.hold_digest == case.proof.hold.command_digest
        assert journal.record_disposition(case.proof) == change
        after = journal.as_of()
        assert replace(after, sequence=before.sequence, dispositions=()) == before
        assert journal.as_of(before.sequence) == before
        assert _prior_journal_rows(journal) == rows
        (projection,) = after.dispositions
        assert projection.change == change and projection.affected == (case.first,)
        assert case.scopes.view() == scope_view
        assert case.scope_file.read_bytes() == scope_bytes
        assert (
            journal.cursor_for(case.source_id, case.native.locator())
            == case.prior_cursor
        )


def test_journal_disposition_preserves_old_projection_when_late_claim_arrives(
    journal_disposition,
):
    from test_monitor_scope import _finish_disposition_turn, _verify

    from aitm_usage.monitor_journal import RoutingJournal

    with journal_disposition() as case:
        journal, scopes, native = case.journal, case.scopes, case.native
        before = journal.as_of()
        change = journal.record_disposition(case.proof)
        recorded = journal.as_of()
        assert recorded.dispositions[0].affected == (case.first,)
        _finish_disposition_turn(native, case.followup, case.when)
        assert native.path.read_bytes().startswith(case.prefix)
        with pytest.raises(LedgerError):
            journal.record_disposition(case.proof)
        assert journal.as_of() == recorded
        batch = scopes.read_source(case.source_id, native.locator())
        legacy = _verify(scopes, native, case.legacy, case.owner, batch, case.legacy_at)
        assert scopes.dispose(case.legacy, legacy).state == "resolved"
        prepared = journal.prepare(case.source_id, native.locator())
        (late,) = (
            item for item in prepared.candidates if item.observation.key == case.later
        )
        assert journal.reserve(late, prepared.progress).status == "pending"
        newer = journal.as_of()
        assert newer.dispositions[0].change == change
        assert set(newer.dispositions[0].affected) == {case.first, case.later}
        assert journal.as_of(change.sequence) == recorded
        assert journal.as_of(before.sequence) == before

    with native.registry.writer() as writer:
        reopened = RoutingJournal(writer, ScopeState(writer))
        assert reopened.as_of() == newer
        assert reopened.as_of(change.sequence) == recorded
        assert reopened.as_of(before.sequence) == before


def test_journal_disposition_rolls_back_sequence_and_row_on_final_recheck(
    journal_disposition, monkeypatch
):
    with journal_disposition() as case:
        journal = case.journal
        before = journal.as_of()
        scope_bytes = case.scope_file.read_bytes()
        require = case.scopes.require_route_disposition
        checks = []

        def fail_final(proof):
            record = require(proof)
            checks.append(record)
            if len(checks) == 2:
                raise LedgerError("injected final authority refusal")
            return record

        with monkeypatch.context() as patch:
            patch.setattr(case.scopes, "require_route_disposition", fail_final)
            with pytest.raises(LedgerError, match="injected final authority refusal"):
                journal.record_disposition(case.proof)
        assert checks == [case.proof.record] * 2
        assert journal.as_of() == before
        assert case.scope_file.read_bytes() == scope_bytes
        assert (
            journal.cursor_for(case.source_id, case.native.locator())
            == case.prior_cursor
        )
        assert journal.record_disposition(case.proof).sequence == before.sequence + 1


@pytest.mark.parametrize(
    "change", ["copy", "foreign-issuer", "consumed", "revoked", "expired"]
)
def test_journal_disposition_requires_live_issuer_even_on_replay(
    journal_disposition, monkeypatch, change
):
    from aitm_usage.monitor_control import _filename
    from aitm_usage.monitor_journal import RoutingJournal

    with journal_disposition() as case:
        journal, proof = case.journal, case.proof
        recorded = journal.record_disposition(proof)
        before = journal.as_of()
        scope_bytes = case.scope_file.read_bytes()
        if change == "copy":
            proof = replace(proof)
        elif change == "foreign-issuer":
            writer = case.scopes.registry
            journal = RoutingJournal(writer, ScopeState(writer))
        elif change == "consumed":
            with case.inbox.publication() as locked:
                os.unlink(
                    _filename(case.command.command_id), dir_fd=locked.directory.fd
                )
        elif change == "revoked":
            case.reader.revoke(case.request.grant_id)
        else:
            future = datetime.now(UTC) + timedelta(minutes=2)
            monkeypatch.setattr("aitm_usage.monitor_control._scope_now", lambda: future)
        with pytest.raises(LedgerError):
            journal.record_disposition(proof)
        assert journal.as_of() == before
        assert journal.as_of(recorded.sequence).dispositions[0].change == recorded
        assert case.scope_file.read_bytes() == scope_bytes
        assert (
            journal.cursor_for(case.source_id, case.native.locator())
            == case.prior_cursor
        )


@pytest.mark.parametrize("conflict", ["same-command", "same-hold"])
def test_journal_disposition_conflicting_durable_replay_preserves_the_row(
    journal_disposition, conflict
):
    from aitm_usage.types import _encode

    with journal_disposition() as case:
        journal = case.journal
        written = journal.record_disposition(case.proof)
        payload = written.disposition
        record = payload.record
        evidence = journal._store.evidence
        if conflict == "same-command":
            changed = "0" * 64 if payload.hold_digest != "0" * 64 else "1" * 64
            payload = replace(payload, hold_digest=changed)
            expected = "command changed"
        else:
            other_id = UUID(int=0x634)
            boundary = replace(
                record.boundary,
                receipt_ref=evidence.pseudonymize("scope-receipt", str(other_id)),
            )
            payload = replace(
                payload, record=replace(record, command_id=other_id, boundary=boundary)
            )
            expected = "hold already has"
        raw = _encode(payload, type(payload), validate_ref=evidence.validate_source_ref)
        with journal._store.transaction(write=True) as connection:
            connection.execute(
                "UPDATE route_dispositions SET command = ?, payload = ? WHERE sequence = ?",
                (str(payload.record.command_id), raw.encode("utf-8"), written.sequence),
            )
        before = journal.as_of()
        with pytest.raises(ConflictError, match=expected):
            journal.record_disposition(case.proof)
        assert journal.as_of() == before


@pytest.mark.parametrize(
    "damage", ["foreign-field", "noncanonical", "empty", "wrong-receipt", "wrong-hold"]
)
def test_journal_disposition_reader_refuses_invalid_stored_evidence(
    journal_disposition, damage
):
    with journal_disposition() as case:
        journal = case.journal
        written = journal.record_disposition(case.proof)
        with journal._store.transaction(write=True) as connection:
            (raw,) = connection.execute(
                "SELECT payload FROM route_dispositions"
            ).fetchone()
            decoded = json.loads(raw)
            hold = str(case.proof.hold.command_id)
            if damage == "foreign-field":
                decoded["foreign"] = None
            elif damage == "empty":
                decoded["end"] = decoded["start"]
            elif damage == "wrong-receipt":
                decoded["record"]["boundary"]["receipt_ref"] = (
                    journal._store.evidence.pseudonymize("scope-receipt", "other").value
                )
            elif damage == "wrong-hold":
                hold = str(UUID(int=0x635))
            raw = json.dumps(decoded, separators=(",", ":")).encode("utf-8")
            if damage == "noncanonical":
                raw += b"\n"
            connection.execute(
                "UPDATE route_dispositions SET payload = ?, hold = ? WHERE sequence = ?",
                (raw, hold, written.sequence),
            )
        with pytest.raises(
            LedgerError, match="Invalid stored routing journal disposition"
        ):
            journal.as_of()
        assert not journal.as_of(written.sequence - 1).dispositions


def test_journal_disposition_projects_each_matching_origin_once(journal_disposition):
    from aitm_usage.monitor_journal import (
        ContentDispute,
        OwnershipDispute,
        _affected_disposition_keys,
        _ContentEdge,
    )
    from aitm_usage.monitor_types import NativeSurface

    with journal_disposition() as case:
        journal = case.journal
        change = journal.record_disposition(case.proof)
        payload = change.disposition
        first = next(
            claim for claim in journal.as_of().claims if claim.key == case.first
        )
        origin = first.evidence
        evidence = journal._store.evidence

        def key(label):
            return evidence.pseudonymize("fixture-observation", label)

        other_source = replace(origin, source_id=UUID(int=0x636))
        contender_key = key("ownership")
        accepted_key = key("content-accepted")
        rival_key = key("content-contender")
        claims = [first, replace(first, key=contender_key, project_id=B)]
        for label, wrong_origin in (
            ("source", other_source),
            ("surface", replace(origin, surface=NativeSurface.CLAUDE_CODE_MACOS)),
            ("session", replace(origin, session_ref=key("different-session"))),
            ("stream", replace(origin, stream_ref=key("different-stream"))),
            ("left", replace(origin, start=payload.start - 1, end=payload.start)),
            ("right", replace(origin, start=payload.end, end=payload.end + 1)),
        ):
            claims.append(replace(first, key=key(label), evidence=wrong_origin))

        prefix = payload.record.prefix
        matching_edge = _ContentEdge(
            key("material"),
            origin,
            origin.end,
            prefix.anchor_ref,
            prefix.locator_ref,
            prefix.incarnation_ref,
        )
        other_edge = replace(matching_edge, origin=other_source)
        disputes = [
            OwnershipDispute(contender_key, A, origin, change.sequence),
            OwnershipDispute(first.key, A, origin, change.sequence),
            OwnershipDispute(key("foreign-project"), B, origin, change.sequence),
        ]
        content = [
            ContentDispute(
                accepted_key,
                A,
                key("common-a"),
                matching_edge,
                other_edge,
                change.sequence,
            ),
            ContentDispute(
                rival_key,
                A,
                key("common-b"),
                other_edge,
                matching_edge,
                change.sequence,
            ),
        ]
        expected = tuple(
            sorted(
                (first.key, contender_key, accepted_key, rival_key),
                key=lambda ref: ref.value,
            )
        )
        assert (
            _affected_disposition_keys(payload, claims, disputes, content) == expected
        )


class NativeJournalFixture:
    def __init__(self, base, monkeypatch):
        monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: base / "control")
        monkeypatch.setattr(
            "aitm_usage.sources.adapter.platform.system", lambda: "Darwin"
        )
        monkeypatch.setattr(
            "aitm_usage.sources.adapter.platform.machine", lambda: "arm64"
        )
        self.registry = Registry(base / "monitor")
        self.adapter = ProviderAdapter()
        self.anchors = {key: base / f"checkout-{key.int}" for key in (A, B)}
        self.ledgers = {}
        self.paths = {}
        self.roots = {}
        with self.registry.writer() as writer:
            self.evidence = writer.source_evidence()
            for key, anchor in self.anchors.items():
                anchor.mkdir()
                ledger = self.ledgers[key] = Ledger.initialize(
                    base / f"project-{key.int}", key
                )
                writer.register_project(
                    ProjectRegistrationRequest(
                        key,
                        str(ledger.root),
                        f"Project {key.int}",
                        anchors=(str(anchor),),
                    )
                )

            for source_id in (LIVE, COPY):
                root = base / f"transcripts-{source_id.int}"
                root.mkdir()
                path = self.paths[source_id] = root / "desktop.jsonl"
                self.roots[source_id] = SourceRoot(
                    root, CUTOFF, tuple(self.anchors.values()), self.evidence
                )
                write(
                    path,
                    [
                        startup(self.anchors[A], originator="Codex Desktop"),
                        *self.turn(1),
                    ],
                )
                writer.approve_source(
                    SourceApprovalRequest(
                        source_id,
                        "codex",
                        "codex-desktop-macos",
                        "Darwin",
                        "arm64",
                        "0.167.0-alpha.3.2",
                        1,
                        str(root),
                    )
                )
                armed = [
                    (change, writer.capture_frontier(change, self.locator(source_id)))
                    for project in (A, B)
                    for change in (CaptureChange(project, source_id, True),)
                ]
                self.append(source_id, self.turn(2))
                for change, frontier in armed:
                    proof = writer.verify_boundary(
                        change, self.locator(source_id), frontier
                    )
                    writer.set_permission(change, proof)

    def turn(self, number, *, checkout=A, increment=4, prior=None):
        turn = UUID(int=0x200 + number)
        time = AFTER + timedelta(seconds=number)
        prior = 4 * (number - 1) if prior is None else prior
        total = usage(prior + increment, prior + increment)
        last = usage(increment, increment)
        return [
            *begin(self.anchors[checkout], turn, time=time),
            response(f"native-response-{number}", total, last, time=time, turn=turn),
            counter(total, last, time=time),
            end(turn, time=time),
        ]

    def append(self, source, rows):
        write(self.paths[source], rows, append=True)

    def locator(self, source=LIVE):
        (locator,) = self.adapter.discover(self.roots[source])
        return locator


@pytest.fixture
def native(tmp_path, monkeypatch):
    return NativeJournalFixture(tmp_path, monkeypatch)


def test_verified_first_claim_is_immutable_across_exact_replay(native):
    from aitm_usage.monitor_journal import RoutingJournal

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        locator = native.locator()
        prepared = journal.prepare(LIVE, locator)
        (candidate,) = prepared.candidates
        outcome = journal.reserve(candidate, prepared.progress)
        assert outcome.status == "pending"
        assert outcome.key == candidate.observation.key
        assert outcome.project_id == A
        first = journal.as_of()
        (claim,) = first.claims
        assert claim.project_id == A
        assert claim.usage.tokens.input_tokens == 4
        assert claim.usage.tokens.output_tokens == 4
        assert journal.cursor_for(LIVE, locator) == prepared.progress

        replay = journal.prepare(LIVE, native.locator())
        (original,) = replay.candidates
        assert journal.reserve(original, replay.progress).status == "replay"
        assert journal.as_of() == first


def test_journal_rejects_cloned_proof_and_foreign_physical_cursor(native):
    from aitm_usage.monitor_journal import RoutingJournal

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        live, copied = native.locator(), native.locator(COPY)
        prepared = journal.prepare(LIVE, live)
        copy = journal.prepare(COPY, copied)
        (candidate,) = prepared.candidates
        with pytest.raises(LedgerError):
            journal.reserve(replace(candidate), prepared.progress)
        with pytest.raises(LedgerError):
            journal.reserve(candidate, replace(prepared.progress))
        with pytest.raises(LedgerError):
            journal.reserve(candidate, copy.progress)
        assert journal.as_of().claims == ()
        assert journal.cursor_for(LIVE, live) is None
        assert journal.cursor_for(COPY, copied) is None


def test_native_transcript_copy_deduplicates_but_a_distinct_retry_counts(native):
    from aitm_usage.monitor_journal import RoutingJournal

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        live, copied = native.locator(), native.locator(COPY)
        # Both installations are independently admitted against their own
        # exact physical prefixes. Copy bytes without replacing the enrolled inode.
        copyfile(native.paths[LIVE], native.paths[COPY])
        assert native.paths[LIVE].read_bytes() == native.paths[COPY].read_bytes()
        prepared = journal.prepare(LIVE, live)
        (first,) = prepared.candidates
        first_result = journal.reserve(first, prepared.progress)
        assert first_result.status == "pending"

        copy = journal.prepare(COPY, copied)
        (reproduced,) = copy.candidates
        assert reproduced.observation.key == first.observation.key
        assert (
            prepared.progress.checkpoint.cursor.locator_ref
            != copy.progress.checkpoint.cursor.locator_ref
        )
        assert (
            prepared.progress.checkpoint.cursor.incarnation_ref
            != copy.progress.checkpoint.cursor.incarnation_ref
        )
        assert journal.reserve(reproduced, copy.progress).status == "replay"
        assert journal.cursor_for(LIVE, live) == prepared.progress
        assert journal.cursor_for(COPY, copied) == copy.progress
        assert [claim.key for claim in journal.as_of().claims] == [first_result.key]

        native.append(LIVE, native.turn(3))
        retry = journal.prepare(LIVE, native.locator())
        _, second = retry.candidates
        assert (
            second.observation.usage.request_ref != first.observation.usage.request_ref
        )
        assert second.observation.usage.tokens == first.observation.usage.tokens
        second_result = journal.reserve(second, retry.progress)
        assert second_result.status == "pending"
        assert second_result.key != first_result.key
        assert {claim.key for claim in journal.as_of().claims} == {
            first_result.key,
            second_result.key,
        }


def test_competing_project_claims_cannot_double_charge(native):
    from aitm_usage.monitor_journal import RoutingJournal

    copy_prefix = native.paths[COPY].read_bytes()
    native.append(COPY, native.turn(3, checkout=B))
    native.append(LIVE, native.turn(3))
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        live = journal.prepare(LIVE, native.locator())
        copied = journal.prepare(COPY, native.locator(COPY))
        (_, contender) = copied.candidates
        assert live.candidates[-1].observation.key == contender.observation.key

        initial, winner = journal.reserve_batch(live)
        assert (initial.status, winner.status) == ("pending", "pending")
        assert winner.project_id == A
        before = journal.as_of()

        repeated_initial, dispute = journal.reserve_batch(copied)
        assert (repeated_initial.status, dispute.status) == ("replay", "disputed")
        assert dispute.key == winner.key
        assert journal.cursor_for(COPY, native.locator(COPY)) is None
        after = journal.as_of()
        assert after.claims == before.claims
        (record,) = after.disputes
        assert record.key == winner.key
        assert record.contender == B
        assert record.sequence > before.sequence

        retry = journal.prepare(COPY, native.locator(COPY))
        journal.reserve_batch(retry)
        assert journal.as_of() == after
        assert journal.cursor_for(COPY, native.locator(COPY)) is None

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        assert journal.as_of(before.sequence) == before
        assert journal.as_of() == after
        owner_replay = journal.prepare(LIVE, native.locator())
        (original,) = (
            item
            for item in owner_replay.candidates
            if item.observation.key == winner.key
        )
        assert journal.reserve(original, owner_replay.progress).status == "disputed"
        assert journal.as_of() == after

        native.paths[COPY].write_bytes(copy_prefix)
        native.append(COPY, native.turn(3, checkout=A, increment=5))
        changed = journal.prepare(COPY, native.locator(COPY))
        (unrecorded,) = (
            item for item in changed.candidates if item.observation.key == winner.key
        )
        assert unrecorded.route.project_id == A
        assert unrecorded.observation.usage != original.observation.usage
        assert journal.reserve(unrecorded, changed.progress).status == "held"
        assert journal.cursor_for(COPY, native.locator(COPY)) is None
        assert journal.cursor_for(LIVE, native.locator()) == live.progress
        assert journal.as_of() == after


def test_changed_same_owner_usage_is_held_without_advancing_prior_cursor(native):
    from aitm_usage.monitor_journal import RoutingJournal

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        first = journal.prepare(LIVE, native.locator())
        (owner,) = first.candidates
        assert journal.reserve(owner, first.progress).status == "pending"
        copy = journal.prepare(COPY, native.locator(COPY))
        (duplicate,) = copy.candidates
        assert journal.reserve(duplicate, copy.progress).status == "replay"

        native.append(LIVE, native.turn(3))
        live = journal.prepare(LIVE, native.locator())
        _, new_claim = live.candidates
        assert journal.reserve(new_claim, live.progress).status == "pending"
        before = journal.as_of()

        native.append(COPY, native.turn(3, increment=7))
        changed = journal.prepare(COPY, native.locator(COPY))
        _, candidate = changed.candidates
        assert candidate.observation.key == new_claim.observation.key
        assert candidate.observation.usage.tokens.input_tokens == 7
        assert journal.reserve(candidate, changed.progress).status == "held"
        assert journal.as_of() == before
        assert journal.cursor_for(COPY, native.locator(COPY)) == copy.progress


def test_reservation_and_cursor_commit_together(native, monkeypatch):
    from aitm_usage.monitor_journal import RoutingJournal

    locator = native.locator()
    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        prepared = journal.prepare(LIVE, locator)
        (candidate,) = prepared.candidates
        initial = journal.as_of()
        write_progress = RoutingJournal._write_progress

        def fail_after_writing_progress(self, *args, **kwargs):
            write_progress(self, *args, **kwargs)
            raise RuntimeError("injected before commit")

        with monkeypatch.context() as fault:
            fault.setattr(
                RoutingJournal, "_write_progress", fail_after_writing_progress
            )
            with pytest.raises(RuntimeError, match="injected before commit"):
                journal.reserve(candidate, prepared.progress)

    with native.registry.writer() as writer:
        reopened = RoutingJournal(writer, ScopeState(writer))
        assert reopened.as_of() == initial
        assert reopened.cursor_for(LIVE, locator) is None
        prepared = reopened.prepare(LIVE, locator)
        (candidate,) = prepared.candidates
        committed = reopened.reserve(candidate, prepared.progress)
        assert committed.status == "pending"
        assert reopened.cursor_for(LIVE, locator) == prepared.progress
        (claim,) = reopened.as_of().claims
        assert claim.key == committed.key
        assert claim.usage.tokens.input_tokens == 4


def test_partial_batch_keeps_prior_across_reopen_until_whole_batch_settles(native):
    from aitm_usage.monitor_journal import RoutingJournal

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        initial = journal.prepare(LIVE, native.locator())
        (first,) = initial.candidates
        assert journal.reserve(first, initial.progress).status == "pending"

        native.append(LIVE, [*native.turn(3), *native.turn(4)])
        next_read = journal.prepare(LIVE, native.locator())
        _, staged, outstanding = next_read.candidates
        assert journal.reserve(staged, next_read.progress).status == "pending"
        assert journal.cursor_for(LIVE, native.locator()) == initial.progress
        assert [claim.key for claim in journal.as_of().claims] == [
            first.observation.key,
            staged.observation.key,
        ]

    with native.registry.writer() as writer:
        reopened = RoutingJournal(writer, ScopeState(writer))
        locator = native.locator()
        assert reopened.cursor_for(LIVE, locator) == initial.progress
        replay = reopened.prepare(LIVE, locator)
        assert [item.observation.key for item in replay.candidates] == [
            first.observation.key,
            staged.observation.key,
            outstanding.observation.key,
        ]
        assert [item.status for item in reopened.reserve_batch(replay)] == [
            "replay",
            "replay",
            "pending",
        ]
        assert reopened.cursor_for(LIVE, locator) == replay.progress
        assert replay.progress == next_read.progress
        assert len(reopened.as_of().claims) == 3


def test_stale_expected_prior_and_replaced_incarnation_are_refused(native):
    from aitm_usage.monitor_journal import RoutingJournal

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        old = journal.prepare(LIVE, native.locator())
        (first,) = old.candidates
        native.append(LIVE, native.turn(3))
        current = journal.prepare(LIVE, native.locator())
        journal.reserve_batch(current)
        with pytest.raises(LedgerError):
            journal.reserve(first, old.progress)

        original = native.paths[LIVE]
        prior = native.locator()
        replacement = original.with_suffix(".new")
        copyfile(original, replacement)
        replacement.replace(original)
        replaced = native.locator()
        assert prior.stream_ref == replaced.stream_ref
        assert journal.cursor_for(LIVE, replaced) is None
        with pytest.raises(LedgerError):
            journal.prepare(LIVE, replaced)
        assert len(journal.as_of().claims) == 2


def test_existing_native_identity_conflict_diagnostic_blocks_progress(native):
    from aitm_usage.monitor_journal import RoutingJournal

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        first = journal.prepare(LIVE, native.locator())
        (candidate,) = first.candidates
        assert journal.reserve(candidate, first.progress).status == "pending"

        conflicting_turn = native.turn(4)
        conflicting_turn[2]["payload"]["thread_id"] = str(UUID(int=0xBAD))
        native.append(LIVE, [*native.turn(3), *conflicting_turn])
        locator = native.locator()
        adapter_read = native.adapter.read_delta(locator, None)
        assert any(
            item.code is DiagnosticCode.IDENTITY_CONFLICT
            for item in adapter_read.diagnostics
        )
        scope_read = state.read_source(LIVE, locator)
        assert any(
            item.code is DiagnosticCode.IDENTITY_CONFLICT
            for item in scope_read.diagnostics
        )
        assert scope_read.cursor is not None

        blocked = journal.prepare(LIVE, locator)
        journal.reserve_batch(blocked)
        assert journal.cursor_for(LIVE, locator) == first.progress


def test_unfinished_native_turn_cannot_reserve_without_a_cursor(native):
    from aitm_usage.monitor_journal import RoutingJournal

    native.append(LIVE, native.turn(3)[:-1])
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        locator = native.locator()
        assert state.read_source(LIVE, locator).cursor is None
        with pytest.raises(LedgerError):
            journal.prepare(LIVE, locator)
        assert journal.as_of().claims == ()
        assert journal.cursor_for(LIVE, locator) is None


def test_copy_without_verified_native_session_cannot_create_an_owner(native):
    from aitm_usage.monitor_journal import RoutingJournal

    original = native.locator()
    copy_path = native.paths[LIVE].with_name("no-session.jsonl")
    header = startup(native.anchors[A], originator="Codex Desktop")
    del header["payload"]["id"]
    del header["payload"]["session_id"]
    write(copy_path, [header, *native.turn(1), *native.turn(2)])
    copy = next(
        item
        for item in native.adapter.discover(native.roots[LIVE])
        if item.stream_ref != original.stream_ref
    )
    assert copy._source.session_ref is None
    assert copy.stream_ref == copy._source.locator_ref

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        with pytest.raises(LedgerError):
            journal.prepare(LIVE, copy)
        assert journal.as_of().claims == ()
        assert journal.cursor_for(LIVE, original) is None


def _append_terminal_receipt(native, command_id):
    turn = native.turn(3)
    moment = AFTER + timedelta(seconds=3)
    call, output = tool_call(native.ledgers[A]), tool_output(command_id)
    call["timestamp"] = output["timestamp"] = moment.isoformat()
    followup = UUID(int=0x204)
    next_moment = moment + timedelta(seconds=1)
    # The result arrives after the preceding response's counter. Codex
    # links it to the next turn start, beyond the last admitted usage.
    # Its delayed pre-cutoff counter closes that turn structurally.
    native.append(
        LIVE,
        [
            *turn[:2],
            call,
            *turn[2:4],
            output,
            turn[-1],
            *begin(native.anchors[A], followup, time=next_moment),
            counter(usage(16, 16), usage(4, 4), time=CUTOFF - timedelta(seconds=1)),
            end(followup, time=next_moment),
        ],
    )


def test_terminal_receipt_without_following_usage_requires_exact_scope_event(native):
    from aitm_usage.monitor_journal import RoutingJournal

    command_id = UUID(int=0x301)
    scope = Scope(A, ItemKey(ItemKind.ISSUE, 118), WorkPhase.PLANNING)
    receipt = native.evidence.pseudonymize("scope-receipt", str(command_id))
    mark = Mark(command_id, scope, receipt)

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        initial = journal.prepare(LIVE, native.locator())
        (first,) = initial.candidates
        assert journal.reserve(first, initial.progress).status == "pending"

        _append_terminal_receipt(native, command_id)
        locator = native.locator()
        batch = state.read_source(LIVE, locator)
        assert batch.diagnostics == ()
        assert (
            batch.cursor.checkpoint.cursor.offset == native.paths[LIVE].stat().st_size
        )
        (target,) = [
            item for item in batch.boundaries if item.boundary.receipt_ref == receipt
        ]
        assert target.boundary.kind is BoundaryKind.TURN
        assert all(
            item.span_end <= target.boundary.ordinal for item in batch.observations
        )

        unsettled = journal.prepare(LIVE, locator)
        assert [result.status for result in journal.reserve_batch(unsettled)] == [
            "replay",
            "pending",
        ]
        assert journal.cursor_for(LIVE, locator) == initial.progress
        staged = journal.as_of()
        assert len(staged.claims) == 2

        authority = state.operator(A)
        state.authorize(mark, authority)
        verified = state.verify_boundary(mark, authority, batch, target)
        assert state.apply_mark(mark, verified).status == "applied"

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        assert journal.cursor_for(LIVE, locator) == initial.progress
        settled = journal.prepare(LIVE, locator)
        assert [result.status for result in journal.reserve_batch(settled)] == [
            "replay",
            "replay",
        ]
        assert journal.cursor_for(LIVE, locator) == settled.progress
        assert journal.as_of().claims == staged.claims

        native.append(LIVE, native.turn(5))
        next_read = journal.prepare(LIVE, native.locator())
        result = journal.reserve(next_read.candidates[-1], next_read.progress)
        assert result.status == "pending"
        assert journal.as_of().claims[-1].scope == scope


def test_journal_reconfirms_visible_scope_replacement_before_durable_progress(
    native, monkeypatch
):
    from aitm_usage.monitor_journal import RoutingJournal

    command_id = UUID(int=0x305)
    scope = Scope(A, ItemKey(ItemKind.ISSUE, 118), WorkPhase.PLANNING)
    receipt = native.evidence.pseudonymize("scope-receipt", str(command_id))
    mark = Mark(command_id, scope, receipt)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        journal = RoutingJournal(writer, state)
        initial = journal.prepare(LIVE, native.locator())
        journal.reserve_batch(initial)
        original = journal.as_of()
        _append_terminal_receipt(native, command_id)
        locator = native.locator()
        batch = state.read_source(LIVE, locator)
        (target,) = [
            item for item in batch.boundaries if item.boundary.receipt_ref == receipt
        ]
        authority = state.operator(A)
        state.authorize(mark, authority)
        proof = state.verify_boundary(mark, authority, batch, target)
        root = native.registry.root
        actual_sync = os.fsync

        def interrupted_scope_sync(fd):
            if (
                os.path.samestat(os.fstat(fd), root.stat())
                and (root / "scope-v1.json").exists()
            ):
                raise OSError("scope directory sync interrupted")
            actual_sync(fd)

        with monkeypatch.context() as interrupted:
            interrupted.setattr(os, "fsync", interrupted_scope_sync)
            with pytest.raises(OSError, match="scope directory sync"):
                state.apply_mark(mark, proof)
            assert state.view().events
            prepared = journal.prepare(LIVE, locator)
            with pytest.raises(OSError, match="scope directory sync"):
                journal.reserve_batch(prepared)

        assert journal.as_of() == original
        assert journal.cursor_for(LIVE, locator) == initial.progress
        prepared = journal.prepare(LIVE, locator)
        journal.reserve_batch(prepared)
        assert journal.cursor_for(LIVE, locator) == prepared.progress
        assert len(journal.as_of().claims) == len(original.claims) + 1


@pytest.fixture
def journal_claude(tmp_path, monkeypatch):
    from test_monitor_scope import ClaudeScopeFixture, NativeScopeFixture

    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    return ClaudeScopeFixture(NativeScopeFixture(tmp_path, monkeypatch))


def _claude_candidates(prepared, ordinal):
    return tuple(
        item
        for item in prepared.candidates
        if item.observation.usage.boundary.ordinal == ordinal
    )


def _claim_for(view, key):
    (claim,) = (claim for claim in view.claims if claim.key == key)
    return claim


def _prepare_claude_mark(state, native):
    from test_claude import SESSION as CLAUDE_SESSION
    from test_claude import _native_tool_turn

    command_id = UUID(int=0x450)
    scope = Scope(A, ItemKey(ItemKind.ISSUE, 201), WorkPhase.PLANNING)
    command = Mark(command_id, scope, native.native.receipt_ref(command_id))
    owner = state.operator(A)
    state.authorize(command, owner)
    invocation = shlex.join(
        (
            "aitm-usage",
            "--project",
            str(native.native.ledgers[A].root),
            "scope",
            "mark",
            "--marker",
            "/private/tmp/marker.json",
            "--session-id",
            str(CLAUDE_SESSION),
            "--json",
        )
    )
    native.append(
        *_native_tool_turn(
            native.anchor,
            invocation,
            json.dumps({"command_id": str(command_id), "status": "queued"}),
        )
    )
    batch = native.read(state)
    target = native.native.target(batch, command_id)
    boundary = state.verify_boundary(command, owner, batch, target)
    return command, boundary


def test_causal_revision_survives_stale_replay_after_restart(journal_claude):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        first = journal.prepare(native.source_id, native.locator())
        (original,) = _claude_candidates(first, ordinal)
        journal.reserve_batch(first)
        prior = journal.as_of()
        saved = _claim_for(prior, original.observation.key)
        assert journal.cursor_for(native.source_id, native.locator()) is None

    with registry.writer() as writer:
        scopes = ScopeState(writer)
        command, boundary = _prepare_claude_mark(scopes, native)
        assert scopes.apply_mark(command, boundary).status == "applied"
        native.append(
            native.request(3, counts=claude_usage(output=6), stop=None),
            native.request(3, counts=claude_usage(output=7)),
        )
        journal = RoutingJournal(writer, scopes)
        prepared = journal.prepare(native.source_id, native.locator())
        original, middle, latest = _claude_candidates(prepared, ordinal)
        assert journal.reserve(latest, prepared.progress).status == "held"
        assert journal.as_of() == prior

        outcomes = journal.reserve_batch(prepared)
        selected = tuple(
            outcome
            for candidate, outcome in zip(prepared.candidates, outcomes, strict=True)
            if candidate in (original, middle, latest)
        )
        assert [outcome.status for outcome in selected] == [
            "replay",
            "pending",
            "pending",
        ]
        assert selected[1].sequence == selected[2].sequence == prior.sequence + 1
        current = journal.as_of()
        revised = _claim_for(current, original.observation.key)
        assert revised.usage.tokens.output_tokens == 7
        assert revised.revision == 3 and revised.sequence == current.sequence
        assert (revised.project_id, revised.scope, revised.evidence) == (
            saved.project_id,
            saved.scope,
            saved.evidence,
        )
        assert revised.usage.observed_at == saved.usage.observed_at
        assert journal.as_of(prior.sequence) == prior
        assert journal.cursor_for(native.source_id, native.locator()) is None

    with registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        replay = journal.prepare(native.source_id, native.locator())
        original, older, latest = _claude_candidates(replay, ordinal)
        for candidate in (older, original, latest):
            assert journal.reserve(candidate, replay.progress).status == "replay"
        assert journal.as_of() == current
        assert journal.as_of(prior.sequence) == prior
        assert journal.cursor_for(native.source_id, native.locator()) is None


def test_claude_revision_cold_reads_behind_an_earlier_persisted_cursor(journal_claude):
    from test_claude import MODEL, cost, model_counts
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        first = journal.prepare(native.source_id, native.locator())
        journal.reserve_batch(first)
        cursor = first.progress
        assert journal.cursor_for(native.source_id, native.locator()) is None
        sequence = journal.as_of().sequence + 1
        # Represent an exact earlier isolated checkpoint. The real quota
        # diagnostic remains unresolved and cannot grant progress in this leaf.
        with journal._store.transaction(write=True) as connection:
            journal._write_progress(connection, first._read, sequence)

    native.append(
        native.request(3, counts=claude_usage(output=6)),
        cost(**{MODEL: model_counts(14, 6, 15, 9, 12)}),
    )
    with registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        assert journal.cursor_for(native.source_id, native.locator()) == cursor
        prepared = journal.prepare(native.source_id, native.locator())
        original, successor, terminal = _claude_candidates(prepared, ordinal)
        for candidate in (successor, terminal):
            assert journal._scopes.verified_revision(
                prepared._read.batch, candidate.observation
            )
        assert original.observation.revision == 1
        assert {item.code for item in prepared._read.batch.diagnostics} == {
            DiagnosticCode.COVERAGE_GAP
        }
        assert len(prepared.candidates) == len(prepared._read.batch.observations)
        assert journal._boundaries_settled(
            prepared._read, journal._scopes.view(prepared._read.batch)
        )
        outcomes = journal.reserve_batch(prepared)
        assert all(outcome.status in ("replay", "pending") for outcome in outcomes)
        selected = [
            outcome.status
            for candidate, outcome in zip(prepared.candidates, outcomes, strict=True)
            if candidate in (original, successor, terminal)
        ]
        assert selected == ["replay", "pending", "pending"]
        assert journal.cursor_for(native.source_id, native.locator()) == cursor


@pytest.mark.parametrize("rewrite", ["before-original", "between-edges", "predecessor"])
def test_v2_claude_replay_requires_the_whole_durable_edge(journal_claude, rewrite):
    from test_claude import usage as claude_usage
    from test_claude import user as claude_user

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        before = native.append(claude_user(native.anchor))
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        journal.reserve_batch(journal.prepare(native.source_id, native.locator()))
        between = native.append(claude_user(native.anchor))
        native.append(native.request(3, counts=claude_usage(output=6), stop=None))
        current = journal.prepare(native.source_id, native.locator())
        original, successor = _claude_candidates(current, ordinal)
        assert journal.reserve(successor, current.progress).status == "pending"
        saved = journal.as_of()

    rows = [json.loads(line) for line in native.path.read_bytes().splitlines()]
    if rewrite == "predecessor":
        rows[ordinal]["message"]["usage"] = claude_usage(output=5)
    else:
        edited = before if rewrite == "before-original" else between
        rows[edited]["message"]["content"] = "rewritten without changing usage"
    write(native.path, rows)
    native.append(native.request(3, counts=claude_usage(output=7)))

    with registry.writer() as writer:
        scopes = ScopeState(writer)
        journal = RoutingJournal(writer, scopes)
        prepared = journal.prepare(native.source_id, native.locator())
        _, known, later = _claude_candidates(prepared, ordinal)
        assert known.observation.usage == successor.observation.usage
        assert scopes.verified_revision(prepared._read.batch, known.observation)
        assert scopes.verified_revision(prepared._read.batch, later.observation)
        for candidate in (known, later):
            assert journal.reserve(candidate, prepared.progress).status == "held"
        assert journal.as_of() == saved
        assert _claim_for(saved, original.observation.key).revision == 2


def test_v1_layout_genesis_reauthenticates_normalized_material_after_capture(
    journal_claude,
):
    from test_claude import usage as claude_usage
    from test_claude import user as claude_user

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        padding = native.append(claude_user(native.anchor))
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        current = journal.prepare(native.source_id, native.locator())
        (original,) = _claude_candidates(current, ordinal)
        journal.reserve_batch(current)
        saved = journal.as_of()
        with journal._store.transaction() as connection:
            assert connection.execute(
                "SELECT count(*) FROM claim_revisions"
            ).fetchone() == (0,)

    rows = [json.loads(line) for line in native.path.read_bytes().splitlines()]
    rows[padding]["message"]["content"] = "rewritten after the original capture witness"
    write(native.path, rows)
    native.append(native.request(3, counts=claude_usage(output=6)))
    with registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        prepared = journal.prepare(native.source_id, native.locator())
        replay, successor = _claude_candidates(prepared, ordinal)
        assert replay.observation.usage == original.observation.usage
        assert journal.reserve(successor, prepared.progress).status == "pending"
        assert journal.as_of(saved.sequence) == saved


def test_claude_revision_archive_can_replay_but_cannot_advance_owner(journal_claude):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal, _original_capture

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        first = journal.prepare(native.source_id, native.locator())
        journal.reserve_batch(first)
        native.append(native.request(3, counts=claude_usage(output=6), stop=None))
        current = journal.prepare(native.source_id, native.locator())
        _, successor = _claude_candidates(current, ordinal)
        assert journal.reserve(successor, current.progress).status == "pending"
        saved = journal.as_of()
        original_evidence = _claim_for(saved, successor.observation.key).evidence
        assert _original_capture(
            current._read.batch, A, original_evidence, writer.view()
        )

        root_path = native.root.path.with_name("claude-archive")
        root_path.mkdir()
        path = root_path / "claude.jsonl"
        root = replace(native.root, path=root_path)
        archive_source = UUID(int=7)
        rows = [json.loads(line) for line in native.path.read_bytes().splitlines()]
        write(path, rows[:1])
        writer.approve_source(
            SourceApprovalRequest(
                archive_source,
                "claude",
                "claude-code-macos",
                "Darwin",
                "arm64",
                "2.1.318",
                1,
                str(root_path),
            )
        )
        (locator,) = native.native.adapter.discover(root)
        capture = CaptureChange(A, archive_source, True)
        frontier = writer.capture_frontier(capture, locator)
        write(path, rows[1:], append=True)
        (locator,) = native.native.adapter.discover(root)
        writer.set_permission(
            capture, writer.verify_boundary(capture, locator, frontier)
        )

        archive = journal.prepare(archive_source, locator)
        assert not _original_capture(
            archive._read.batch, A, original_evidence, writer.view()
        )
        original, known = _claude_candidates(archive, ordinal)
        assert known.observation.key == successor.observation.key
        assert journal.reserve(original, archive.progress).status == "replay"
        assert journal.reserve(known, archive.progress).status == "replay"

        write(path, [native.request(3, counts=claude_usage(output=7))], append=True)
        (locator,) = native.native.adapter.discover(root)
        extended = journal.prepare(archive_source, locator)
        _, _, new = _claude_candidates(extended, ordinal)
        assert journal._scopes.verified_revision(extended._read.batch, new.observation)
        assert journal.reserve(new, extended.progress).status == "held"
        assert journal.as_of() == saved
        assert journal.cursor_for(native.source_id, native.locator()) is None
        assert journal.cursor_for(archive_source, locator) is None


def test_claude_journal_never_bypasses_a_disabled_intermediate(journal_claude):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        first = journal.prepare(native.source_id, native.locator())
        journal.reserve_batch(first)
        saved = journal.as_of()
        native.apply_capture(writer, A, False, 4)
        native.append(native.request(3, counts=claude_usage(output=6), stop=None))
        native.apply_capture(writer, A, True, 5)
        native.append(native.request(3, counts=claude_usage(output=7)))
        prepared = journal.prepare(native.source_id, native.locator())
        _, disabled, later = _claude_candidates(prepared, ordinal)
        for candidate in (disabled, later):
            assert journal.reserve(candidate, prepared.progress).status == "held"
        assert journal.as_of() == saved
        assert journal.cursor_for(native.source_id, native.locator()) is None


def test_claude_revision_rolls_back_when_the_final_read_check_fails(
    journal_claude, monkeypatch
):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        first = journal.prepare(native.source_id, native.locator())
        journal.reserve_batch(first)
        saved = journal.as_of()
        native.append(native.request(3, counts=claude_usage(output=6)))
        prepared = journal.prepare(native.source_id, native.locator())
        _, successor = _claude_candidates(prepared, ordinal)
        fresh = journal._fresh_view
        checked = False

        def reject_final(read):
            nonlocal checked
            if checked:
                raise LedgerError("test final native custody failure")
            checked = True
            return fresh(read)

        monkeypatch.setattr(journal, "_fresh_view", reject_final)
        with pytest.raises(LedgerError, match="test final native custody failure"):
            journal.reserve(successor, prepared.progress)
        assert journal.as_of() == saved

    with registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        assert journal.as_of() == saved
        assert journal.cursor_for(native.source_id, native.locator()) is None
        prepared = journal.prepare(native.source_id, native.locator())
        _, successor = _claude_candidates(prepared, ordinal)
        assert journal.reserve(successor, prepared.progress).status == "pending"
        assert journal.as_of().sequence == saved.sequence + 1


def test_verified_claude_revision_does_not_change_saved_original_scope(journal_claude):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    with registry.writer() as writer:
        native.approve(writer)
        scopes = ScopeState(writer)
        command, boundary = _prepare_claude_mark(scopes, native)
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, scopes)
        first = journal.prepare(native.source_id, native.locator())
        (original,) = _claude_candidates(first, ordinal)
        assert journal.reserve(original, first.progress).status == "pending"
        saved = journal.as_of()
        assert _claim_for(saved, original.observation.key).scope is None

        assert scopes.apply_mark(command, boundary).status == "applied"
        native.append(native.request(3, counts=claude_usage(output=6)))
        prepared = journal.prepare(native.source_id, native.locator())
        _, successor = _claude_candidates(prepared, ordinal)
        proof = scopes.verified_revision(prepared._read.batch, successor.observation)
        assert proof is not None and proof.route.scope == command.scope
        assert journal.reserve(successor, prepared.progress).status == "held"
        assert journal.as_of() == saved


def test_journal_refuses_mismatched_v1_first_claim_payload(native):
    from aitm_usage.monitor_journal import RoutingJournal, _ClaimPayload
    from aitm_usage.types import _decode, _encode

    with native.registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        locator = native.locator()
        prepared = journal.prepare(LIVE, locator)
        (candidate,) = prepared.candidates
        assert journal.reserve(candidate, prepared.progress).status == "pending"
        key = candidate.observation.key.value
        with journal._store.transaction(write=True) as connection:
            (raw,) = connection.execute(
                "SELECT payload FROM claims WHERE key = ?", (key,)
            ).fetchone()
            original = _decode(raw, _ClaimPayload)
            changed_usage = replace(
                original.material.usage,
                observed_at=original.material.usage.observed_at + timedelta(seconds=1),
            )
            corrupt = replace(
                original, material=replace(original.material, usage=changed_usage)
            )
            connection.execute(
                "UPDATE claims SET payload = ? WHERE key = ?",
                (_encode(corrupt, _ClaimPayload).encode(), key),
            )

        replay = journal.prepare(LIVE, locator)
        (same,) = replay.candidates
        with pytest.raises(LedgerError, match="Stored first claim material changed"):
            journal.reserve(same, replay.progress)
        with pytest.raises(LedgerError, match="Stored first claim material changed"):
            journal.as_of()


def _claude_archive(native, writer, rows, source_id, *, projects=(A,), relocate=False):
    root_path = native.root.path.with_name(f"claude-archive-{source_id.int}")
    root_path.mkdir()
    path = root_path / "claude.jsonl"
    root = replace(native.root, path=root_path)
    if relocate:
        native.path.rename(path)
    write(path, rows[:1])
    writer.approve_source(
        SourceApprovalRequest(
            source_id,
            "claude",
            "claude-code-macos",
            "Darwin",
            "arm64",
            "2.1.318",
            1,
            str(root_path),
        )
    )

    def locate():
        (locator,) = native.native.adapter.discover(root)
        return locator

    armed = [
        (change, writer.capture_frontier(change, locate()))
        for project in projects
        for change in (CaptureChange(project, source_id, True),)
    ]
    write(path, rows[1:3], append=True)
    for change, frontier in armed:
        proof = writer.verify_boundary(change, locate(), frontier)
        writer.set_permission(change, proof)
    write(path, rows[3:], append=True)
    return path, locate


def _common_claude_revision(native, writer):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native.approve(writer)
    ordinal = native.append(native.request(3, stop=None))
    journal = RoutingJournal(writer, ScopeState(writer))
    journal.reserve_batch(journal.prepare(native.source_id, native.locator()))
    native.append(native.request(3, counts=claude_usage(output=6), stop=None))
    prepared = journal.prepare(native.source_id, native.locator())
    _, common = _claude_candidates(prepared, ordinal)
    assert journal.reserve(common, prepared.progress).status == "pending"
    rows = [json.loads(line) for line in native.path.read_bytes().splitlines()]
    return journal, ordinal, rows


@pytest.mark.parametrize("descendant", [False, True], ids=["head-child", "later-head"])
def test_verified_claude_branches_record_one_durable_content_dispute(
    journal_claude, descendant, monkeypatch
):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    registry = native.native.registry
    source_id, exact_source = UUID(int=7), UUID(int=8)
    with registry.writer() as writer:
        journal, ordinal, prefix = _common_claude_revision(native, writer)
        archive_path, locate = _claude_archive(native, writer, prefix, source_id)
        before = journal.as_of()
        stale = journal.prepare(source_id, locate())
        assert all(item.status == "replay" for item in journal.reserve_batch(stale))
        assert journal.as_of() == before

        native.append(native.request(3, counts=claude_usage(output=7)))
        write(
            archive_path,
            [native.request(3, counts=claude_usage(output=8))],
            append=True,
        )
        live = journal.prepare(native.source_id, native.locator())
        rival = journal.prepare(source_id, locate())
        _, live_common, accepted = _claude_candidates(live, ordinal)
        _, rival_common, contender = _claude_candidates(rival, ordinal)
        live_proof = journal._scopes.verified_revision(
            live._read.batch, live_common.observation
        )
        rival_proof = journal._scopes.verified_revision(
            rival._read.batch, rival_common.observation
        )
        assert live_proof.witness.prefix_ref == rival_proof.witness.prefix_ref
        assert (
            live._read.batch._native_cursor.incarnation_ref
            != rival._read.batch._native_cursor.incarnation_ref
        )
        assert contender.observation.usage != accepted.observation.usage
        assert journal._scopes.verified_revision(
            rival._read.batch, contender.observation
        )
        assert journal.reserve(contender, rival.progress).status == "held"
        assert journal.as_of() == before
        assert journal.reserve(accepted, live.progress).status == "pending"

        exact_rows = [
            json.loads(line) for line in native.path.read_bytes().splitlines()
        ]
        _, exact_locate = _claude_archive(native, writer, exact_rows, exact_source)
        exact = journal.prepare(exact_source, exact_locate())
        _, _, copy = _claude_candidates(exact, ordinal)
        assert journal.reserve(copy, exact.progress).status == "replay"

        if descendant:
            native.append(native.request(3, counts=claude_usage(output=9)))
            latest = journal.prepare(native.source_id, native.locator())
            *_, fourth = _claude_candidates(latest, ordinal)
            assert journal.reserve(fourth, latest.progress).status == "pending"
            equal_source = UUID(int=9)
            _, equal_locate = _claude_archive(
                native,
                writer,
                [*prefix, native.request(3, counts=claude_usage(output=9))],
                equal_source,
            )
            equal = journal.prepare(equal_source, equal_locate())
            *_, equal_usage = _claude_candidates(equal, ordinal)
            assert equal_usage.observation.usage == fourth.observation.usage
            assert equal_usage.observation.revision != fourth.observation.revision
            assert journal._scopes.verified_revision(
                equal._read.batch, equal_usage.observation
            )
            before_equal = journal.as_of()
            assert journal.reserve(equal_usage, equal.progress).status == "held"
            assert journal.as_of() == before_equal
        saved = journal.as_of()
        rival = journal.prepare(source_id, locate())
        *_, contender = _claude_candidates(rival, ordinal)
        fresh = journal._fresh_view
        checked = False

        def reject_final(read):
            nonlocal checked
            if checked:
                raise LedgerError("injected content dispute final custody failure")
            checked = True
            return fresh(read)

        with monkeypatch.context() as fault:
            fault.setattr(journal, "_fresh_view", reject_final)
            with pytest.raises(
                LedgerError, match="injected content dispute final custody"
            ):
                journal.reserve(contender, rival.progress)
        assert journal.as_of() == saved
        outcome = journal.reserve(contender, rival.progress)
        assert outcome.status == "disputed" and outcome.project_id == A
        disputed = journal.as_of()
        assert disputed.claims == saved.claims
        (record,) = disputed.content_disputes
        assert record.key == contender.observation.key and record.project_id == A
        assert record.sequence == outcome.sequence == saved.sequence + 1
        assert record.common == rival_proof.witness.successor_material
        assert record.accepted.origin.source_id == native.source_id
        assert record.contender.origin.source_id == source_id
        assert record.accepted.incarnation_ref != record.contender.incarnation_ref
        assert journal.as_of(saved.sequence) == saved
        assert journal.cursor_for(native.source_id, native.locator()) is None
        assert journal.cursor_for(source_id, locate()) is None

        foreign_source = UUID(int=10)
        rival_rows = [
            json.loads(line) for line in archive_path.read_bytes().splitlines()
        ]
        _, foreign_locate = _claude_archive(native, writer, rival_rows, foreign_source)
        foreign = journal.prepare(foreign_source, foreign_locate())
        *_, same_rival = _claude_candidates(foreign, ordinal)
        assert same_rival.observation.usage == contender.observation.usage
        assert journal._scopes.verified_revision(
            foreign._read.batch, same_rival.observation
        )
        assert journal.reserve(same_rival, foreign.progress).status == "held"
        assert journal.as_of() == disputed

    with registry.writer() as writer:
        journal = RoutingJournal(writer, ScopeState(writer))
        live = journal.prepare(native.source_id, native.locator())
        outcomes = [
            journal.reserve(candidate, live.progress).status
            for candidate in _claude_candidates(live, ordinal)
        ]
        assert outcomes == ["held", "held", "disputed"] + (
            ["held"] if descendant else []
        )
        rival = journal.prepare(source_id, locate())
        assert [
            journal.reserve(candidate, rival.progress).status
            for candidate in _claude_candidates(rival, ordinal)
        ] == ["held", "held", "disputed"]
        exact = journal.prepare(exact_source, exact_locate())
        assert (
            journal.reserve(
                _claude_candidates(exact, ordinal)[-1], exact.progress
            ).status
            == "disputed"
        )
        assert journal.as_of() == disputed
        assert journal.as_of(saved.sequence) == saved
        if not descendant:
            from aitm_usage.monitor_journal import _ContentDisputePayload
            from aitm_usage.types import _decode, _encode

            with journal._store.transaction(write=True) as connection:
                (raw,) = connection.execute(
                    "SELECT payload FROM content_disputes WHERE key = ?",
                    (record.key.value,),
                ).fetchone()
                payload = _decode(raw, _ContentDisputePayload)
                altered = replace(
                    payload,
                    accepted=replace(
                        payload.accepted, prefix_ref=record.contender.prefix_ref
                    ),
                )
                connection.execute(
                    "UPDATE content_disputes SET payload = ? WHERE key = ?",
                    (
                        _encode(altered, _ContentDisputePayload).encode(),
                        record.key.value,
                    ),
                )
            with pytest.raises(LedgerError, match="Stored content dispute"):
                journal.as_of()
            assert journal.as_of(saved.sequence) == saved


def test_claude_rewritten_common_prefix_cannot_create_a_content_dispute(journal_claude):
    from test_claude import usage as claude_usage
    from test_claude import user as claude_user

    native = journal_claude
    registry = native.native.registry
    source_id = UUID(int=7)
    with registry.writer() as writer:
        native.approve(writer)
        padding = native.append(claude_user(native.anchor))
        ordinal = native.append(native.request(3, stop=None))
        from aitm_usage.monitor_journal import RoutingJournal

        journal = RoutingJournal(writer, ScopeState(writer))
        journal.reserve_batch(journal.prepare(native.source_id, native.locator()))
        native.append(native.request(3, counts=claude_usage(output=6), stop=None))
        current = journal.prepare(native.source_id, native.locator())
        _, common = _claude_candidates(current, ordinal)
        assert journal.reserve(common, current.progress).status == "pending"
        prefix = [json.loads(line) for line in native.path.read_bytes().splitlines()]
        archive_path, locate = _claude_archive(native, writer, prefix, source_id)
        native.append(native.request(3, counts=claude_usage(output=7)))
        live = journal.prepare(native.source_id, native.locator())
        assert (
            journal.reserve(_claude_candidates(live, ordinal)[-1], live.progress).status
            == "pending"
        )
        changed = [json.loads(line) for line in archive_path.read_bytes().splitlines()]
        changed[padding]["message"]["content"] = (
            "changed raw prefix, equal normalized counters"
        )
        write(archive_path, changed)
        write(
            archive_path,
            [native.request(3, counts=claude_usage(output=8))],
            append=True,
        )
        rival = journal.prepare(source_id, locate())
        _, archived_common, contender = _claude_candidates(rival, ordinal)
        original_proof = journal._scopes.verified_revision(
            live._read.batch, _claude_candidates(live, ordinal)[1].observation
        )
        archived_proof = journal._scopes.verified_revision(
            rival._read.batch, archived_common.observation
        )
        assert (
            original_proof.witness.successor_material
            == archived_proof.witness.successor_material
        )
        assert original_proof.witness.prefix_ref != archived_proof.witness.prefix_ref
        assert journal._scopes.verified_revision(
            rival._read.batch, contender.observation
        )
        assert journal.reserve(contender, rival.progress).status == "held"
        assert journal.as_of().content_disputes == ()


@pytest.mark.parametrize("ownership_first", [True, False], ids=["before", "after"])
def test_claude_content_and_ownership_disputes_remain_separate(
    journal_claude, ownership_first
):
    from test_claude import usage as claude_usage

    native = journal_claude
    source_id, other_source = UUID(int=7), UUID(int=8)
    with native.native.registry.writer() as writer:
        journal, ordinal, prefix = _common_claude_revision(native, writer)
        _, locate = _claude_archive(
            native,
            writer,
            [*prefix, native.request(3, counts=claude_usage(output=8))],
            source_id,
        )
        other_rows = [
            {**row, "cwd": str(native.native.anchors[B])}
            for row in prefix[: ordinal + 1]
        ]
        _, other_locate = _claude_archive(
            native, writer, other_rows, other_source, projects=(B,)
        )
        native.append(native.request(3, counts=claude_usage(output=7)))
        live = journal.prepare(native.source_id, native.locator())
        original, _, accepted = _claude_candidates(live, ordinal)
        assert journal.reserve(accepted, live.progress).status == "pending"
        saved = journal.as_of()
        other = journal.prepare(other_source, other_locate())
        (foreign,) = _claude_candidates(other, ordinal)
        assert foreign.route.project_id == B
        assert foreign.observation.key == original.observation.key
        rival = journal.prepare(source_id, locate())
        *_, contender = _claude_candidates(rival, ordinal)
        assert contender.route.project_id == A
        assert journal._scopes.verified_revision(
            rival._read.batch, contender.observation
        )

        if ownership_first:
            ownership = journal.reserve(foreign, other.progress)
            assert journal.reserve(contender, rival.progress).status == "held"
        else:
            assert journal.reserve(contender, rival.progress).status == "disputed"
            ownership = journal.reserve(foreign, other.progress)
        assert ownership.status == "disputed" and ownership.project_id == A
        assert journal.reserve(original, live.progress) == ownership
        current = journal.as_of()
        assert current.claims == saved.claims
        (record,) = current.disputes
        assert record.contender == B and record.sequence == ownership.sequence
        assert len(current.content_disputes) == int(not ownership_first)
        assert journal.cursor_for(source_id, locate()) is None
        assert journal.cursor_for(other_source, other_locate()) is None


def test_claude_genesis_alone_cannot_prove_a_common_dispute_parent(journal_claude):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import RoutingJournal

    native = journal_claude
    source_id = UUID(int=7)
    with native.native.registry.writer() as writer:
        native.approve(writer)
        ordinal = native.append(native.request(3, stop=None))
        journal = RoutingJournal(writer, ScopeState(writer))
        journal.reserve_batch(journal.prepare(native.source_id, native.locator()))
        prefix = [json.loads(line) for line in native.path.read_bytes().splitlines()]
        _, locate = _claude_archive(
            native,
            writer,
            [*prefix, native.request(3, counts=claude_usage(output=8))],
            source_id,
        )
        native.append(native.request(3, counts=claude_usage(output=7)))
        live = journal.prepare(native.source_id, native.locator())
        _, accepted = _claude_candidates(live, ordinal)
        assert journal.reserve(accepted, live.progress).status == "pending"
        saved = journal.as_of()
        rival = journal.prepare(source_id, locate())
        _, contender = _claude_candidates(rival, ordinal)
        assert journal._scopes.verified_revision(
            rival._read.batch, contender.observation
        )
        assert journal.reserve(contender, rival.progress).status == "held"
        assert journal.as_of() == saved


def test_claude_common_usage_repeat_cannot_create_a_content_dispute(journal_claude):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_journal import _distinct_accepted_child

    native = journal_claude
    source_id = UUID(int=7)
    with native.native.registry.writer() as writer:
        journal, ordinal, prefix = _common_claude_revision(native, writer)
        _, locate = _claude_archive(
            native,
            writer,
            [*prefix, native.request(3, counts=claude_usage(output=6), stop=None)],
            source_id,
        )
        native.append(native.request(3, counts=claude_usage(output=7)))
        live = journal.prepare(native.source_id, native.locator())
        _, common, accepted = _claude_candidates(live, ordinal)
        assert journal.reserve(accepted, live.progress).status == "pending"
        saved = journal.as_of()
        repeat = journal.prepare(source_id, locate())
        _, repeated_common = _claude_candidates(repeat, ordinal)
        assert repeated_common.observation.usage == common.observation.usage
        assert journal.reserve(repeated_common, repeat.progress).status == "replay"
        proof = journal._scopes.verified_revision(live._read.batch, common.observation)
        with journal._store.transaction() as connection:
            assert (
                _distinct_accepted_child(
                    connection,
                    common.observation.key,
                    proof.witness.successor_material,
                    common.observation.usage,
                    journal._store.evidence,
                )
                is None
            )
        assert journal.as_of() == saved


@pytest.mark.parametrize("control", ["equal-child", "disabled", "relocated"])
def test_claude_conflict_requires_distinct_usage_and_current_independent_custody(
    journal_claude, control
):
    from test_claude import usage as claude_usage
    from test_claude import user as claude_user

    native = journal_claude
    source_id = UUID(int=7)
    with native.native.registry.writer() as writer:
        journal, ordinal, prefix = _common_claude_revision(native, writer)
        native.append(native.request(3, counts=claude_usage(output=7)))
        live = journal.prepare(native.source_id, native.locator())
        _, _, accepted = _claude_candidates(live, ordinal)
        accepted_proof = journal._scopes.verified_revision(
            live._read.batch, accepted.observation
        )
        assert journal.reserve(accepted, live.progress).status == "pending"
        saved = journal.as_of()
        archive_path, locate = _claude_archive(
            native, writer, prefix, source_id, relocate=control == "relocated"
        )
        if control == "equal-child":
            write(archive_path, [claude_user(native.anchor)], append=True)
        if control == "disabled":
            disable = CaptureChange(A, source_id, False)
            frontier = writer.capture_frontier(disable, locate())
            write(archive_path, [native.request(4)], append=True)
            writer.set_permission(
                disable, writer.verify_boundary(disable, locate(), frontier)
            )
        output = 7 if control == "equal-child" else 8
        write(
            archive_path,
            [native.request(3, counts=claude_usage(output=output))],
            append=True,
        )
        if control == "disabled":
            enable = CaptureChange(A, source_id, True)
            frontier = writer.capture_frontier(enable, locate())
            write(archive_path, [native.request(5)], append=True)
            writer.set_permission(
                enable, writer.verify_boundary(enable, locate(), frontier)
            )
        rival = journal.prepare(source_id, locate())
        _, _, contender = _claude_candidates(rival, ordinal)
        proof = journal._scopes.verified_revision(
            rival._read.batch, contender.observation
        )
        if control == "disabled":
            assert proof is None
        else:
            assert proof is not None
            assert (
                proof.witness.predecessor_material
                == accepted_proof.witness.predecessor_material
            )
            assert proof.witness.prefix_ref != accepted_proof.witness.prefix_ref
        if control == "equal-child":
            assert contender.observation.usage == accepted.observation.usage
        if control == "relocated":
            original_cursor = live._read.batch._native_cursor
            rival_cursor = rival._read.batch._native_cursor
            assert original_cursor.locator_ref != rival_cursor.locator_ref
            assert original_cursor.incarnation_ref == rival_cursor.incarnation_ref
        assert journal.reserve(contender, rival.progress).status == "held"
        assert journal.as_of() == saved
