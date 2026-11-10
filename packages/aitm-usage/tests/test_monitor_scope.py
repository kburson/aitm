"""Native scope routing, handoff order, and proof-hold regressions."""

import json
import shlex
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import UUID

import pytest
from test_codex import (
    AFTER,
    CUTOFF,
    SESSION,
    begin,
    counter,
    end,
    response,
    row,
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
from aitm_usage.sources.adapter import ProviderAdapter, SourceRoot
from aitm_usage.sources.scan import checkout_anchor_reference
from aitm_usage.types import ItemKey, ItemKind, WorkPhase

A, B, C, UNKNOWN, SOURCE = (UUID(int=i) for i in range(1, 6))


class NativeScopeFixture:
    def __init__(self, base, monkeypatch):
        self.registry = Registry(base / "monitor")
        self.transcripts = base / "transcripts"
        self.transcripts.mkdir()
        self.path = self.transcripts / "desktop.jsonl"
        self.anchors = {key: base / f"worktree-{key.int}" for key in (A, B, C)}
        self.ledgers = {}
        for key, anchor in self.anchors.items():
            anchor.mkdir()
            self.ledgers[key] = Ledger.initialize(base / f"state-{key.int}", key)
        monkeypatch.setattr(
            "aitm_usage.sources.adapter.platform.system", lambda: "Darwin"
        )
        monkeypatch.setattr(
            "aitm_usage.sources.adapter.platform.machine", lambda: "arm64"
        )
        self.adapter = ProviderAdapter()
        self.total = 0
        self.turn = 0
        write(self.path, [startup(self.anchors[A], originator="Codex Desktop")])
        self.append()
        with self.registry.writer() as writer:
            self.evidence = writer.source_evidence()
            self.root = SourceRoot(
                self.transcripts, CUTOFF, tuple(self.anchors.values()), self.evidence
            )
            for key in self.anchors:
                writer.register_project(
                    ProjectRegistrationRequest(
                        key,
                        str(self.ledgers[key].root),
                        f"Project {key.int}",
                        anchors=(str(self.anchors[key]),),
                    )
                )
            writer.approve_source(
                SourceApprovalRequest(
                    SOURCE,
                    "codex",
                    "codex-desktop-macos",
                    "Darwin",
                    "arm64",
                    "0.167.0-alpha.3.2",
                    1,
                    str(self.transcripts),
                )
            )
            for key in self.anchors:
                change = CaptureChange(key, SOURCE, True)
                frontier = writer.capture_frontier(change, self.locator())
                self.append()
                proof = writer.verify_boundary(change, self.locator(), frontier)
                writer.set_permission(change, proof)

    def locator(self):
        (locator,) = self.adapter.discover(self.root)
        return locator

    def receipt_ref(self, command_id):
        return self.evidence.pseudonymize("scope-receipt", str(command_id))

    def anchor_ref(self, project_id):
        return checkout_anchor_reference(self.evidence, self.anchors[project_id])

    def revoke(self, writer):
        for project_id in self.anchors:
            disable = CaptureChange(project_id, SOURCE, False)
            frontier = writer.capture_frontier(disable, self.locator())
            self.append()
            proof = writer.verify_boundary(disable, self.locator(), frontier)
            writer.set_permission(disable, proof)

    def append(
        self,
        command_id=None,
        *,
        checkout=A,
        pad_before=False,
        pad_after=False,
        bind=False,
        scope_invocation=None,
    ):
        anchor = self.anchors.get(checkout, checkout)
        self.turn += 1
        turn = UUID(int=0x200 + self.turn)
        time = AFTER + timedelta(seconds=self.turn)
        rows = begin(anchor, turn, time=time)
        start = len(self.path.read_bytes().splitlines())

        def next_response(suffix):
            self.total += 4
            return response(
                f"response-{self.turn}-{suffix}",
                usage(self.total, self.total),
                usage(4, 4),
                time=time,
                turn=turn,
            )

        receipt_ordinal = None
        if command_id is not None:
            if pad_before:
                rows.append(
                    row("response_item", {"type": "reasoning", "summary": []}, time)
                )
            call = tool_call(SimpleNamespace(root=self.ledgers[A].root), bind=bind)
            if scope_invocation is None:
                result = tool_output(command_id)
            else:
                request, stdout = scope_invocation
                command = shlex.join(
                    (
                        "aitm-usage",
                        "monitor",
                        "scope",
                        "mark",
                        "--request",
                        str(request),
                        "--json",
                    )
                )
                arguments = json.dumps({"cmd": command}, separators=(",", ":"))
                call["payload"]["input"] = (
                    f"const marker = await tools.exec_command({arguments}); text(marker.output);"
                )
                result = tool_output(command_id, stdout=stdout)
            call["timestamp"] = result["timestamp"] = time.isoformat()
            rows.extend((call, next_response("tool"), result))
            receipt_ordinal = start + len(rows) - 1
            rows.append(counter(usage(self.total, self.total), usage(4, 4), time=time))
            if pad_after:
                rows.append(
                    row("response_item", {"type": "reasoning", "summary": []}, time)
                )
        target_ordinal = start + len(rows)
        rows.extend(
            (
                next_response("answer"),
                counter(usage(self.total, self.total), usage(4, 4), time=time),
                end(turn, time=time),
            )
        )
        write(self.path, rows, append=True)
        if command_id is not None:
            # Finish the native look-ahead turn so Codex can commit the prefix.
            self.append(checkout=checkout)
        return receipt_ordinal, target_ordinal

    def target(self, batch, command_id, ordinal=None):
        (target,) = (
            item
            for item in batch.boundaries
            if item.boundary.receipt_ref == self.receipt_ref(command_id)
            and (ordinal is None or item.boundary.ordinal == ordinal)
        )
        return target

    def observation(self, batch, ordinal):
        (observation,) = (
            item
            for item in batch.observations
            if item.usage.boundary.ordinal == ordinal
        )
        return observation

    def routed(self, state, batch, ordinal):
        from aitm_usage.monitor_scope import resolve_route

        return resolve_route(
            self.observation(batch, ordinal), self.registry.view(), state.view(batch)
        )


@pytest.fixture
def native(tmp_path, monkeypatch):
    monkeypatch.setattr("aitm_usage.ledger._control_root", lambda: tmp_path / "control")
    return NativeScopeFixture(tmp_path, monkeypatch)


def test_scope_fixture_uses_the_real_receipt_linked_native_observation(native):
    command_id = UUID(int=0x301)
    receipt, ordinal = native.append(command_id)
    batch = native.adapter.read_delta(native.locator(), None)
    target = native.target(batch, command_id, ordinal)
    observation = native.observation(batch, ordinal)
    assert receipt < ordinal
    assert target.project_context == native.anchor_ref(A)
    assert observation.usage.boundary == target.boundary


def _issue(project_id, identifier, *, phase=WorkPhase.PLANNING):
    from aitm_usage.monitor_scope import Scope

    return Scope(project_id, ItemKey(ItemKind.ISSUE, identifier), phase)


def _authorize_handoff(state, native, command_id, current, target, generation):
    from aitm_usage.monitor_scope import Handoff

    command = Handoff(
        command_id,
        current,
        target,
        generation,
        native.anchor_ref(A),
        native.receipt_ref(command_id),
    )
    authority = state.operator(current)
    state.authorize(command, authority)
    return command, authority


def _verify(state, native, command, authority, batch, ordinal):
    return state.verify_boundary(
        command, authority, batch, native.target(batch, command.command_id, ordinal)
    )


def test_unregistered_operator_cannot_create_a_scope_conflict(native):
    from aitm_usage.monitor_scope import Mark, ScopeState

    command_id = UUID(int=0x301)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        with pytest.raises(LedgerError):
            state.operator(UNKNOWN)
        mark = Mark(command_id, _issue(B, 117), native.receipt_ref(command_id))
        with pytest.raises(LedgerError):
            state.authorize(mark, state.operator(A))
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        assert native.routed(state, batch, ordinal).project_id == A
        assert state.view(batch).holds == ()


def test_foreign_ordinary_marker_conflicts_then_prospective_handoff_routes(native):
    from aitm_usage.monitor_scope import Mark, ScopeState, resolve_route

    mark_id, handoff_id = UUID(int=0x301), UUID(int=0x302)
    destination = _issue(B, 117)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        mark = Mark(mark_id, destination, native.receipt_ref(mark_id))
        authority = state.operator(B)
        state.authorize(mark, authority)
        handoff, owner = _authorize_handoff(
            state, native, handoff_id, A, destination, 0
        )
        _, mark_ordinal = native.append(mark_id)
        _, switch_ordinal = native.append(handoff_id)
        batch = state.read_source(SOURCE, native.locator())

        state.apply_mark(
            mark, _verify(state, native, mark, authority, batch, mark_ordinal)
        )
        conflict = native.routed(state, batch, mark_ordinal)
        assert conflict.project_id is None
        assert conflict.status == "held"
        assert set(conflict.affected_projects) == {A, B}
        forged = replace(state.view(batch), events=())
        invalid = resolve_route(
            native.observation(batch, mark_ordinal), native.registry.view(), forged
        )
        assert invalid.status == "held"
        assert invalid.project_id is None

        proof = _verify(state, native, handoff, owner, batch, switch_ordinal)
        assert state.apply_handoff(handoff, proof).status == "applied"
        assert native.routed(state, batch, switch_ordinal).scope == destination
        assert native.routed(state, batch, mark_ordinal).project_id is None


def test_handoff_A_to_B_to_C_with_retained_A(native):
    from aitm_usage.monitor_scope import ScopeState

    first_id, second_id = UUID(int=0x301), UUID(int=0x302)
    first_scope, second_scope = _issue(B, 117), _issue(C, 118)
    capture_before = native.registry.view()
    ledgers_before = {key: ledger.as_of() for key, ledger in native.ledgers.items()}
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        first, owner_a = _authorize_handoff(state, native, first_id, A, first_scope, 0)
        second, owner_b = _authorize_handoff(
            state, native, second_id, B, second_scope, 1
        )
        _, first_ordinal = native.append(first_id)
        _, second_ordinal = native.append(second_id)
        batch = state.read_source(SOURCE, native.locator())

        first_proof = _verify(state, native, first, owner_a, batch, first_ordinal)
        second_proof = _verify(state, native, second, owner_b, batch, second_ordinal)
        first_result = state.apply_handoff(first, first_proof)
        second_result = state.apply_handoff(second, second_proof)
        assert (first_result.status, first_result.generation) == ("applied", 1)
        assert (second_result.status, second_result.generation) == ("applied", 2)
        assert native.routed(state, batch, first_ordinal).scope == first_scope
        assert native.routed(state, batch, second_ordinal).scope == second_scope
        assert state.apply_handoff(second, second_proof) == second_result
    assert native.registry.view() == capture_before
    assert {
        key: ledger.as_of() for key, ledger in native.ledgers.items()
    } == ledgers_before
    snapshot = (native.registry.root / "scope-v1.json").read_text()
    for secret in (str(SESSION), str(native.path), str(native.anchors[A])):
        assert secret not in snapshot


def test_late_earlier_transition_reprojects_a_later_effective_handoff(native):
    from aitm_usage.monitor_scope import ScopeState

    first_id, second_id = UUID(int=0x301), UUID(int=0x302)
    early_scope, late_scope = _issue(B, 117), _issue(C, 118)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        earlier, owner_a = _authorize_handoff(
            state, native, first_id, A, early_scope, 0
        )
        later, owner_b = _authorize_handoff(state, native, second_id, A, late_scope, 0)
        _, first_ordinal = native.append(first_id)
        _, second_ordinal = native.append(second_id)
        batch = state.read_source(SOURCE, native.locator())
        earlier_proof = _verify(state, native, earlier, owner_a, batch, first_ordinal)
        later_proof = _verify(state, native, later, owner_b, batch, second_ordinal)

        assert state.apply_handoff(later, later_proof).status == "applied"
        assert native.routed(state, batch, second_ordinal).scope == late_scope
        earlier_result = state.apply_handoff(earlier, earlier_proof)
        assert earlier_result.status == "applied"
        assert earlier_result.affected.start == first_ordinal
        assert earlier_result.affected.end > second_ordinal
        assert (
            native.observation(batch, second_ordinal).key
            in earlier_result.affected.observation_keys
        )
        assert native.routed(state, batch, first_ordinal).scope == early_scope
        affected = native.routed(state, batch, second_ordinal)
        assert affected.project_id is None
        assert affected.status == "held"


def _competing(native, *, reverse=False, different_receipt_ordinals=False):
    from aitm_usage.monitor_scope import ScopeState

    first_id, second_id = UUID(int=0x301), UUID(int=0x302)
    accepted = native.path.read_bytes()
    baseline = (native.turn, native.total)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        commands = [
            _authorize_handoff(state, native, first_id, A, _issue(B, 117), 0),
            _authorize_handoff(state, native, second_id, A, _issue(C, 118), 0),
        ]
        order = (1, 0) if reverse else (0, 1)
        receipt_ordinals = set()
        target_ordinals = set()
        boundary_refs = set()
        for index, choice in enumerate(order):
            # Substitute only the unaccepted future tail at the enrolled inode.
            # Both receipts are independently emitted by the actual adapter.
            native.path.write_bytes(accepted)
            native.turn, native.total = baseline
            command, owner = commands[choice]
            receipt_ordinal, target_ordinal = native.append(
                command.command_id,
                pad_before=different_receipt_ordinals and choice == 0,
                pad_after=different_receipt_ordinals and choice == 1,
            )
            batch = state.read_source(SOURCE, native.locator())
            target = native.target(batch, command.command_id, target_ordinal)
            receipt_ordinals.add(receipt_ordinal)
            target_ordinals.add(target_ordinal)
            boundary_refs.add(target.boundary.boundary_ref)
            proof = state.verify_boundary(command, owner, batch, target)
            disposition = state.apply_handoff(command, proof)
            if index == 0:
                assert disposition.status == "applied"
                assert (
                    native.routed(state, batch, target_ordinal).scope
                    == command.destination
                )
            else:
                assert disposition.status == "conflict"
                assert disposition.affected.start == target_ordinal
                assert (
                    native.observation(batch, target_ordinal).key
                    in disposition.affected.observation_keys
                )

        assert len(target_ordinals) == 1
        assert len(boundary_refs) == 2
        if different_receipt_ordinals:
            assert len(receipt_ordinals) == 2
        conflicted = native.routed(state, batch, target_ordinal)
        assert conflicted.project_id is None
        assert conflicted.status == "held"
        assert set(conflicted.affected_projects) == {A, B, C}


@pytest.mark.parametrize("reverse", [False, True], ids=["B-first", "C-first"])
def test_competing_receipts_conflict_in_both_native_delivery_orders(native, reverse):
    _competing(native, reverse=reverse)


def test_receipts_at_different_ordinals_conflict_at_the_same_native_target(native):
    _competing(native, different_receipt_ordinals=True)


def test_develop_handoff_cannot_reuse_origin_as_destination_worktree(native):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x301)
    scope = _issue(B, 117, phase=WorkPhase.DEVELOPMENT)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command, owner = _authorize_handoff(state, native, command_id, A, scope, 0)
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        with pytest.raises(LedgerError):
            _verify(state, native, command, owner, batch, ordinal)
        assert native.routed(state, batch, ordinal).project_id != B


def test_develop_mark_requires_accepted_destination_worktree_owner(native):
    from aitm_usage.monitor_scope import Mark, ScopeState

    command_id = UUID(int=0x301)
    scope = _issue(A, 117, phase=WorkPhase.DEVELOPMENT)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command = Mark(command_id, scope, native.receipt_ref(command_id))
        owner = state.operator(A)
        state.authorize(command, owner)
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        with pytest.raises(LedgerError):
            _verify(state, native, command, owner, batch, ordinal)
        assert native.routed(state, batch, ordinal).scope != scope
        assert state.view().events == ()


@pytest.mark.parametrize("matching_session", [True, False], ids=["same", "other"])
def test_develop_mark_requires_the_native_stream_of_its_accepted_owner(
    native, matching_session
):
    from aitm_usage.monitor_scope import Mark, Scope, ScopeState
    from aitm_usage.scopes import BoundaryEvidence, drain_inbox, enqueue_command
    from aitm_usage.types import (
        DevelopmentBinding,
        InboxCommand,
        MarkerDisposition,
        ReviewRole,
        ScopeMarker,
    )

    owner_id, command_id = UUID(int=0x301), UUID(int=0x302)
    ledger, worktree = native.ledgers[A], native.anchors[A]
    _, owner_ordinal = native.append(owner_id, bind=True)
    owner_root = native.transcripts
    if not matching_session:
        owner_root = native.transcripts.with_name("other-session")
        owner_root.mkdir()
        (owner_root / native.path.name).write_bytes(
            native.path.read_bytes().replace(
                str(SESSION).encode(), str(UUID(int=0x103)).encode()
            )
        )
    (locator,) = native.adapter.discover(
        SourceRoot(owner_root, CUTOFF, (worktree,), ledger)
    )
    legacy = native.adapter.read_delta(locator, None)
    receipt_ref = ledger.pseudonymize("scope-receipt", str(owner_id))
    (owner_target,) = (
        item
        for item in legacy.boundaries
        if item.boundary.receipt_ref == receipt_ref
        and item.boundary.ordinal == owner_ordinal
    )
    boundary = owner_target.boundary
    anchor = checkout_anchor_reference(ledger, worktree)
    assert owner_target.project_context == anchor
    item = ItemKey(ItemKind.ISSUE, 117)
    participant = ledger.pseudonymize("participant", "develop-owner")
    attempt = ledger.pseudonymize("attempt", "first")
    marker = ScopeMarker(
        owner_id,
        boundary.provider,
        boundary.session_ref,
        1,
        boundary.kind,
        boundary.boundary_ref,
        AFTER,
        item,
        WorkPhase.DEVELOPMENT,
        participant,
        A,
        ReviewRole.AUTHOR,
        receipt_ref,
        attempt,
    )
    binding = DevelopmentBinding(marker, anchor, 1)
    enqueue_command(ledger.root, InboxCommand(owner_id, A, binding))
    with ledger.writer() as writer:
        result = drain_inbox(writer, (BoundaryEvidence(boundary, anchor),))
        assert result.receipts[0].disposition is MarkerDisposition.ACCEPTED

    scope = Scope(
        A, item, WorkPhase.DEVELOPMENT, participant, ReviewRole.AUTHOR, attempt
    )
    command = Mark(command_id, scope, native.receipt_ref(command_id), binding)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        owner = state.operator(A)
        state.authorize(command, owner)
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        if matching_session:
            proof = _verify(state, native, command, owner, batch, ordinal)
            assert state.apply_mark(command, proof).status == "applied"
            assert native.routed(state, batch, ordinal).scope == scope
        else:
            with pytest.raises(LedgerError):
                _verify(state, native, command, owner, batch, ordinal)
            assert state.view().events == ()


def test_native_boundary_cannot_be_substituted_between_streams(native):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x301)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 0
        )
        _, ordinal = native.append(command_id)
        original = native.locator()
        batch = state.read_source(SOURCE, original)
        second = native.transcripts / "other.jsonl"
        second.write_bytes(
            native.path.read_bytes().replace(
                str(SESSION).encode(), str(UUID(int=0x302)).encode()
            )
        )
        (other_locator,) = (
            locator
            for locator in native.adapter.discover(native.root)
            if locator.stream_ref != original.stream_ref
        )
        other_batch = native.adapter.read_delta(other_locator, None)
        foreign_target = native.target(other_batch, command_id, ordinal)
        assert foreign_target.boundary.stream_ref != original.stream_ref
        with pytest.raises(LedgerError):
            state.verify_boundary(command, owner, batch, foreign_target)
        assert native.routed(state, batch, ordinal).project_id == A


def test_cloned_scope_proof_and_changed_authorized_bytes_are_refused(native):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x301)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 0
        )
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        proof = _verify(state, native, command, owner, batch, ordinal)
        with pytest.raises(LedgerError):
            state.apply_handoff(command, replace(proof))
        changed = replace(command, destination=_issue(C, 118))
        with pytest.raises(LedgerError):
            state.authorize(changed, owner)
        assert state.apply_handoff(command, proof).status == "applied"
        assert native.routed(state, batch, ordinal).project_id == B


def test_expired_hold_releases_no_usage(native):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x301)
    now = AFTER

    def clock():
        return now

    with native.registry.writer() as writer:
        state = ScopeState(writer, clock=clock)
        command, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 1
        )
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        proof = _verify(state, native, command, owner, batch, ordinal)
        hold = state.hold(proof)
        expiry = AFTER + timedelta(minutes=15)
        assert hold.expires_at == expiry
        assert hold.state == "held"
        assert native.routed(state, batch, ordinal).project_id is None
        now -= timedelta(minutes=5)
        assert state.hold(proof).expires_at == expiry
        now = expiry - timedelta(seconds=1)
        assert state.hold(proof).expires_at == expiry
        assert state.expire() == ()

    native.append()
    with native.registry.writer() as writer:
        resumed = ScopeState(writer, clock=clock)
        owner = resumed.operator(A)
        resumed.authorize(command, owner)
        batch = resumed.read_source(SOURCE, native.locator())
        assert (
            resumed.hold(_verify(resumed, native, command, owner, batch, ordinal))
            == hold
        )
        now = expiry
        (expired,) = resumed.expire()
        assert expired.state == "gap"
        assert expired.expires_at == expiry
        assert native.routed(resumed, batch, ordinal).project_id is None
        assert resumed.expire() == ()


def test_project_wide_mark_is_distinct_from_anchor_only_scope(native):
    from aitm_usage.monitor_scope import Mark, Scope, ScopeState

    command_id = UUID(int=0x301)
    project_scope = Scope(A, ItemKey(ItemKind.PROJECT), WorkPhase.PLANNING)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command = Mark(command_id, project_scope, native.receipt_ref(command_id))
        owner = state.operator(A)
        state.authorize(command, owner)
        _, anchor_only = native.append()
        _, marked = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        state.apply_mark(command, _verify(state, native, command, owner, batch, marked))
        unassigned = native.routed(state, batch, anchor_only)
        assert unassigned.project_id == A
        assert unassigned.scope != project_scope
        assert native.routed(state, batch, marked).scope == project_scope


def test_ordinary_mark_routes_unanchored_usage_after_native_rescan(native):
    from aitm_usage.monitor_scope import Mark, ScopeState

    command_id = UUID(int=0x301)
    outside = native.transcripts.parent / "unregistered-worktree"
    outside.mkdir()
    scope = _issue(B, 117)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command = Mark(command_id, scope, native.receipt_ref(command_id))
        owner = state.operator(B)
        state.authorize(command, owner)
        _, historical = native.append(checkout=outside)
        _, marked = native.append(command_id, checkout=outside)
        before = state.read_source(SOURCE, native.locator())
        target = native.target(before, command_id, marked)
        assert target.project_context is None
        assert not any(
            observation.usage.boundary.ordinal >= historical
            for observation in before.observations
        )

        proof = state.verify_boundary(command, owner, before, target)
        assert state.apply_mark(command, proof).status == "applied"
        after = state.read_source(SOURCE, native.locator())
        observation = native.observation(after, marked)
        assert observation.project_context is None
        assert (
            observation.key
            == native.observation(
                state.read_source(SOURCE, native.locator()), marked
            ).key
        )
        assert not any(
            candidate.usage.boundary.ordinal == historical
            for candidate in after.observations
        )
        assert native.routed(state, after, marked).scope == scope


def test_late_claude_revision_keeps_its_original_native_scope(native):
    from test_claude import SESSION as CLAUDE_SESSION
    from test_claude import _native_tool_turn
    from test_claude import request as claude_request
    from test_claude import usage as claude_usage
    from test_claude import user as claude_user

    from aitm_usage.monitor_scope import ScopeState

    source_id, command_id = UUID(int=6), UUID(int=0x301)
    root_path = native.transcripts.parent / "claude-transcripts"
    root_path.mkdir()
    path = root_path / "claude.jsonl"
    anchor = native.anchors[A]
    root = replace(native.root, path=root_path)

    def locate():
        (locator,) = native.adapter.discover(root)
        return locator

    def request(number, **changes):
        return claude_request(
            anchor,
            req=f"request-{number}",
            msg=f"message-{number}",
            uuid=str(UUID(int=0x310 + number)),
            isSidechain=False,
            **changes,
        )

    write(path, [claude_user(anchor), request(0)])
    with native.registry.writer() as writer:
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
        for number, project_id in enumerate((A, B), 1):
            change = CaptureChange(project_id, source_id, True)
            frontier = writer.capture_frontier(change, locate())
            write(path, [request(number)], append=True)
            proof = writer.verify_boundary(change, locate(), frontier)
            writer.set_permission(change, proof)

        state = ScopeState(writer)
        original_ordinal = len(path.read_bytes().splitlines())
        write(path, [request(3, stop=None)], append=True)
        early = state.read_source(source_id, locate())
        original = native.observation(early, original_ordinal)
        assert native.routed(state, early, original_ordinal).project_id == A

        handoff, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 0
        )
        shell_command = shlex.join(
            [
                "aitm-usage",
                "--project",
                str(native.ledgers[A].root),
                "scope",
                "mark",
                "--marker",
                "/private/tmp/marker.json",
                "--session-id",
                str(CLAUDE_SESSION),
                "--json",
            ]
        )
        carrier = _native_tool_turn(
            anchor,
            shell_command,
            json.dumps({"command_id": str(command_id), "status": "queued"}),
        )
        write(path, carrier, append=True)
        handoff_batch = state.read_source(source_id, locate())
        target = native.target(handoff_batch, command_id)
        boundary = state.verify_boundary(handoff, owner, handoff_batch, target)
        assert state.apply_handoff(handoff, boundary).status == "applied"

        write(path, [request(3, counts=claude_usage(output=6))], append=True)
        current = state.read_source(source_id, locate())
        (revised,) = (
            observation
            for observation in current.observations
            if observation.key == original.key
            and observation.revision > original.revision
        )
        assert revised.usage.boundary.ordinal == original_ordinal
        from aitm_usage.monitor_scope import resolve_route

        decision = resolve_route(revised, native.registry.view(), state.view(current))
        assert decision.project_id == A
        assert native.routed(state, current, target.boundary.ordinal).project_id == B


def test_verified_disposition_only_releases_its_covered_hold(native):
    from aitm_usage.monitor_scope import Disposition, Mark, ScopeState

    marker_id, held_id, outside_id, unrelated_id, resolve_id = (
        UUID(int=i) for i in range(0x301, 0x306)
    )
    original = _issue(A, 116)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        owner = state.operator(A)
        mark = Mark(marker_id, original, native.receipt_ref(marker_id))
        state.authorize(mark, owner)
        _, marked = native.append(marker_id)
        batch = state.read_source(SOURCE, native.locator())
        state.apply_mark(mark, _verify(state, native, mark, owner, batch, marked))

        prefix = native.path.read_bytes()
        baseline = native.turn, native.total
        held, _ = _authorize_handoff(state, native, held_id, A, _issue(B, 117), 1)
        _, held_at = native.append(held_id)
        batch = state.read_source(SOURCE, native.locator())
        hold = state.hold(_verify(state, native, held, owner, batch, held_at))
        assert native.routed(state, batch, held_at).status == "held"

        outside = Disposition(
            outside_id,
            A,
            held_id,
            native.receipt_ref(outside_id),
            release_previous=True,
        )
        state.authorize(outside, owner)
        _, outside_at = native.append(outside_id)
        assert outside_at >= hold.affected.end
        batch = state.read_source(SOURCE, native.locator())
        with pytest.raises(LedgerError):
            state.dispose(
                outside, _verify(state, native, outside, owner, batch, outside_at)
            )
        assert state.view().holds == (hold,)

        native.path.write_bytes(prefix)
        native.turn, native.total = baseline
        unrelated = Disposition(
            unrelated_id,
            B,
            held_id,
            native.receipt_ref(unrelated_id),
            release_previous=True,
        )
        owner_b = state.operator(B)
        state.authorize(unrelated, owner_b)
        _, unrelated_at = native.append(unrelated_id)
        assert unrelated_at == held_at
        batch = state.read_source(SOURCE, native.locator())
        with pytest.raises(LedgerError):
            state.dispose(
                unrelated,
                _verify(state, native, unrelated, owner_b, batch, unrelated_at),
            )
        assert state.view().holds == (hold,)

        # A second real receipt matches the held position without changing its
        # accepted native prefix or the previously verified scope.
        native.path.write_bytes(prefix)
        native.turn, native.total = baseline
        resolve = Disposition(
            resolve_id,
            A,
            held_id,
            native.receipt_ref(resolve_id),
            release_previous=True,
        )
        state.authorize(resolve, owner)
        _, resolved_at = native.append(resolve_id)
        assert resolved_at == held_at
        batch = state.read_source(SOURCE, native.locator())
        proof = _verify(state, native, resolve, owner, batch, resolved_at)
        resolved = state.dispose(resolve, proof)
        assert resolved.state == "resolved"
        assert state.dispose(resolve, proof) == resolved
        assert native.routed(state, batch, resolved_at).scope == original


def test_resolved_hold_rejects_original_handoff_after_restart(native):
    from aitm_usage.monitor_scope import Disposition, Mark, ScopeState

    marker_id, held_id, resolve_id = (UUID(int=i) for i in range(0x301, 0x304))
    original = _issue(A, 116)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        owner = state.operator(A)
        mark = Mark(marker_id, original, native.receipt_ref(marker_id))
        state.authorize(mark, owner)
        _, marked = native.append(marker_id)
        batch = state.read_source(SOURCE, native.locator())
        state.apply_mark(mark, _verify(state, native, mark, owner, batch, marked))

        held, _ = _authorize_handoff(state, native, held_id, A, _issue(B, 117), 1)
        resolve = Disposition(
            resolve_id,
            A,
            held_id,
            native.receipt_ref(resolve_id),
            release_previous=True,
        )
        state.authorize(resolve, owner)
        _, held_at = native.append(held_id)
        _, resolved_at = native.append(resolve_id)
        batch = state.read_source(SOURCE, native.locator())
        hold = state.hold(_verify(state, native, held, owner, batch, held_at))
        assert held_at < resolved_at < hold.affected.end
        resolved = state.dispose(
            resolve, _verify(state, native, resolve, owner, batch, resolved_at)
        )
        assert resolved.state == "resolved"
        assert state.receipt(held, owner) == resolved
        assert native.routed(state, batch, held_at).scope == original

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        owner = state.operator(A)
        state.authorize(held, owner)
        batch = state.read_source(SOURCE, native.locator())
        events = state.view().events
        outcome = state.apply_handoff(
            held, _verify(state, native, held, owner, batch, held_at)
        )
        assert outcome.status == "rejected"
        assert outcome.affected == resolved.affected
        assert state.view().events == events
        assert state.receipt(held, owner) == resolved
        assert native.routed(state, batch, held_at).scope == original


def test_hold_overflow_becomes_a_gap_without_displacing_existing_hold(
    native, monkeypatch
):
    from aitm_usage import monitor_scope

    monkeypatch.setattr(monitor_scope, "_MAX_HOLDS", 1)
    first_id, second_id = UUID(int=0x301), UUID(int=0x302)
    with native.registry.writer() as writer:
        state = monitor_scope.ScopeState(writer, clock=lambda: AFTER)
        first, owner = _authorize_handoff(state, native, first_id, A, _issue(B, 117), 1)
        _, first_at = native.append(first_id)
        batch = state.read_source(SOURCE, native.locator())
        pending = state.hold(_verify(state, native, first, owner, batch, first_at))

    with native.registry.writer() as writer:
        state = monitor_scope.ScopeState(writer, clock=lambda: AFTER)
        second, owner = _authorize_handoff(
            state, native, second_id, A, _issue(C, 118), 1
        )
        _, second_at = native.append(second_id)
        batch = state.read_source(SOURCE, native.locator())
        overflow = state.hold(_verify(state, native, second, owner, batch, second_at))
        assert pending.state == "held"
        assert overflow.state == "gap"
        assert state.view().holds == (pending, overflow)
        assert native.routed(state, batch, second_at).project_id is None


def test_exact_handoff_retry_after_restart_and_source_growth_keeps_one_event(native):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x301)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        handoff, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 0
        )
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        proof = _verify(state, native, handoff, owner, batch, ordinal)
        original = state.apply_handoff(handoff, proof)
        assert original.status == "applied"

    _, added = native.append()
    with native.registry.writer() as writer:
        resumed = ScopeState(writer)
        owner = resumed.operator(A)
        resumed.authorize(handoff, owner)
        batch = resumed.read_source(SOURCE, native.locator())
        proof = _verify(resumed, native, handoff, owner, batch, ordinal)
        assert resumed.apply_handoff(handoff, proof) == original
        assert len(resumed.view().events) == 1
        assert native.routed(resumed, batch, added).scope == handoff.destination

        native.revoke(writer)

    with native.registry.writer() as writer:
        resumed = ScopeState(writer)
        with pytest.raises(LedgerError):
            resumed.read_source(SOURCE, native.locator())
        owner = resumed.operator(A)
        assert resumed.receipt(handoff, owner) == original
        with pytest.raises(LedgerError):
            resumed.receipt(handoff, resumed.operator(B))
        with pytest.raises(LedgerError):
            resumed.receipt(replace(handoff, destination=_issue(C, 118)), owner)
        assert len(resumed.view().events) == 1


def test_handoff_consumes_the_first_verified_receipt_target_once(native):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x301)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        handoff, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 0
        )
        _, first = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        (later,) = (
            item
            for item in batch.boundaries
            if item.boundary.receipt_ref == native.receipt_ref(command_id)
            and item.boundary.ordinal > first
        )
        with pytest.raises(LedgerError):
            state.verify_boundary(handoff, owner, batch, later)
        proof = _verify(state, native, handoff, owner, batch, first)
        assert state.apply_handoff(handoff, proof).status == "applied"
        assert native.routed(state, batch, first).scope == handoff.destination


@pytest.mark.parametrize("operation", ["mark", "handoff"])
def test_grok_scope_proves_native_target_and_holds_without_capture(native, operation):
    from test_grok import FIXTURES, GROK_BINARY, PROMPT_A
    from test_grok import SESSION as GROK_SESSION

    from aitm_usage.monitor_scope import Handoff, Mark, ScopeState
    from aitm_usage.sources.grok import GrokAdapter, GrokOrigin

    source_id, command_id = UUID(int=6), UUID(int=0x301)
    approved_root = native.transcripts.parent / "grok-transcripts"
    session_dir = approved_root / GROK_SESSION
    session_dir.mkdir(parents=True)
    updates = session_dir / "updates.jsonl"
    updates.write_bytes((FIXTURES / "updates.jsonl").read_bytes())
    (session_dir / "usage.json").write_bytes((FIXTURES / "usage.json").read_bytes())
    root = replace(
        native.root, path=approved_root, cutoff=datetime(2026, 1, 1, tzinfo=UTC)
    )
    receipt_ref = native.evidence.pseudonymize("grok-receipt", str(command_id))
    origin = GrokOrigin(
        session_id=GROK_SESSION,
        system="Darwin",
        architecture="arm64",
        version="1.0.77",
        build="50ca579fa996",
        executable_digest=GROK_BINARY,
        format_version=1,
        lineage_id=GROK_SESSION,
        incarnation=native.evidence.pseudonymize("grok-incarnation", "fixture"),
        checkout=native.anchor_ref(A),
    )

    def verify_receipt(*hook):
        return (
            receipt_ref
            if hook == (GROK_SESSION, PROMPT_A, "synthetic-event-1")
            else None
        )

    reader = GrokAdapter(
        lambda path: origin if path == updates else None, verify_receipt
    )
    (locator,) = reader.discover(root)
    with native.registry.writer() as writer:
        writer.approve_source(
            SourceApprovalRequest(
                source_id,
                "grok",
                "grok-build-macos",
                "Darwin",
                "arm64",
                "1.0.77",
                1,
                str(approved_root),
            )
        )
        capture_before = writer.view()
        state = ScopeState(writer, grok_reader=reader)
        owner = state.operator(A)
        if operation == "mark":
            command = Mark(command_id, _issue(A, 117), receipt_ref)
            apply = state.apply_mark
        else:
            command = Handoff(
                command_id, A, _issue(B, 117), 0, native.anchor_ref(A), receipt_ref
            )
            apply = state.apply_handoff
        state.authorize(command, owner)
        batch = state.read_source(source_id, locator)
        marked, following = batch.observations
        (linked,) = batch.boundaries
        assert linked.boundary.receipt_ref == receipt_ref
        assert marked.position.ordinal == linked.boundary.ordinal
        assert following.position.ordinal > marked.position.ordinal
        assert following.position.stream_ref == marked.position.stream_ref
        proof = state.verify_boundary(command, owner, batch, linked)
        expected = marked.position if operation == "mark" else following.position
        assert proof.position.ordinal == expected.ordinal
        assert not proof.eligible
        assert apply(command, proof).status == "held"

        from aitm_usage.monitor_scope import resolve_route

        view = state.view(batch)
        for observation in batch.observations:
            route = resolve_route(observation, writer.view(), view)
            assert route.status == "held"
            assert route.project_id is None
        assert writer.view() == capture_before
        assert not any(epoch.source_id == source_id for epoch in writer.view().epochs)


@pytest.mark.parametrize("cause", ["revoked", "replaced-inode"])
def test_scope_native_read_requires_current_enrolled_physical_source(native, cause):
    from aitm_usage.monitor_scope import ScopeState

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        assert state.read_source(SOURCE, native.locator()).observations
        if cause == "revoked":
            native.revoke(writer)
        else:
            original = native.transcripts.parent / "retired.jsonl"
            native.path.rename(original)
            native.path.write_bytes(original.read_bytes())
            assert native.path.stat().st_ino != original.stat().st_ino

        native.append()
        with pytest.raises(LedgerError):
            state.read_source(SOURCE, native.locator())


@pytest.mark.parametrize("changed", ["source-inode", "source-prefix", "anchor"])
def test_scope_proof_requires_current_physical_identity_before_apply(native, changed):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x301)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 0
        )
        _, ordinal = native.append(command_id)
        batch = state.read_source(SOURCE, native.locator())
        proof = _verify(state, native, command, owner, batch, ordinal)

        if changed == "source-inode":
            retired = native.transcripts.parent / "retired.jsonl"
            native.path.rename(retired)
            native.path.write_bytes(retired.read_bytes())
            assert native.path.stat().st_ino != retired.stat().st_ino
        elif changed == "source-prefix":
            accepted = native.path.read_bytes()
            rewritten = accepted.replace(b"Codex Desktop", b"Codex desktop", 1)
            assert rewritten != accepted
            native.path.write_bytes(rewritten)
        else:
            anchor = native.anchors[A]
            retired = anchor.with_name("retired-worktree")
            anchor.rename(retired)
            anchor.mkdir()
            assert anchor.stat().st_ino != retired.stat().st_ino

        with pytest.raises(LedgerError):
            state.apply_handoff(command, proof)
        with pytest.raises(LedgerError):
            state.view(batch)
        assert state.view().events == ()


def test_queued_monitor_scope_cli_joins_only_first_native_target(
    native, monkeypatch, capsys
):
    import sys

    from aitm_usage import cli, monitor_registry
    from aitm_usage.monitor_control import ControlInbox, ScopeInboxReader
    from aitm_usage.monitor_scope import Mark, ScopeState
    from aitm_usage.scope_admission import MarkRequest

    command_id, grant_id = UUID(int=0x410), UUID(int=0x411)
    scope = _issue(A, 116)
    request = native.path.parent.parent / "scope-request.json"
    request.write_text(
        json.dumps(
            {
                "command_id": str(command_id),
                "grant_id": str(grant_id),
                "scope": {
                    "project_id": str(A),
                    "item": {"kind": "issue", "identifier": 116},
                    "phase": "planning",
                },
            }
        )
    )
    request.chmod(0o600)
    monkeypatch.setattr(
        monitor_registry, "default_monitor_root", lambda: native.registry.root
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["aitm-usage", "monitor", "scope", "mark", "--request", str(request), "--json"],
    )
    with native.registry.writer() as writer:
        inbox = ControlInbox(writer.root)
        reader = ScopeInboxReader(writer, inbox)
        reader.register(grant_id, A, ("mark",))
        reader.advertise(reader.probe(MarkRequest(command_id, grant_id, scope)))
        assert cli.main() == 0
        output = capsys.readouterr().out
        assert output == f'{{"command_id": "{command_id}", "status": "queued"}}\n'
        with inbox.publication() as locked:
            (envelope,) = reader.iter_verified(locked)
        assert envelope.body.request == MarkRequest(command_id, grant_id, scope)

        _, first = native.append(command_id, scope_invocation=(request, output))
        _, later = native.append(command_id, scope_invocation=(request, output))
        state = ScopeState(writer)
        batch = state.read_source(SOURCE, native.locator())
        mark = Mark(command_id, scope, native.receipt_ref(command_id))
        owner = state.operator(A)
        state.authorize(mark, owner)
        assert (
            _verify(state, native, mark, owner, batch, first).position.ordinal == first
        )
        with pytest.raises(LedgerError, match="first unique"):
            _verify(state, native, mark, owner, batch, later)
        assert state.view().events == ()
        assert state.receipt(mark, owner) is None
