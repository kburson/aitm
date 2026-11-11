"""Exercise routing journal authority with real native capture and scope evidence."""

import json
import os
import shlex
from dataclasses import replace
from datetime import timedelta
from shutil import copyfile
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

from aitm_usage.ledger import Ledger, LedgerError
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
