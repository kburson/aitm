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


class ClaudeScopeFixture:
    source_id = UUID(int=6)

    def __init__(self, native):
        from test_claude import user as claude_user

        self.native = native
        self.anchor = native.anchors[A]
        root_path = native.transcripts.parent / "claude-transcripts"
        root_path.mkdir()
        self.path = root_path / "claude.jsonl"
        self.root = replace(native.root, path=root_path)
        write(self.path, [claude_user(self.anchor)])

    def locator(self):
        (locator,) = self.native.adapter.discover(self.root)
        return locator

    def request(self, number, **changes):
        from test_claude import request as claude_request

        return claude_request(
            self.anchor,
            req=f"request-{number}",
            msg=f"message-{number}",
            uuid=str(UUID(int=0x310 + number)),
            isSidechain=False,
            **changes,
        )

    def append(self, *rows):
        start = len(self.path.read_bytes().splitlines())
        write(self.path, rows, append=True)
        return start

    def apply_capture(self, writer, project, enabled, number):
        change = CaptureChange(project, self.source_id, enabled)
        frontier = writer.capture_frontier(change, self.locator())
        self.append(self.request(number))
        boundary = writer.verify_boundary(change, self.locator(), frontier)
        return writer.set_permission(change, boundary)

    def approve(self, writer):
        writer.approve_source(
            SourceApprovalRequest(
                self.source_id,
                "claude",
                "claude-code-macos",
                "Darwin",
                "arm64",
                "2.1.318",
                1,
                str(self.root.path),
            )
        )
        self.apply_capture(writer, A, True, 1)
        self.apply_capture(writer, B, True, 2)

    def read(self, state):
        return state.read_source(self.source_id, self.locator())

    def queue_capture(self, writer, command_id, *, enabled):
        from aitm_usage.monitor_control import ControlInbox, ControlStatus
        from aitm_usage.monitor_registry import ControlCommand

        inbox = ControlInbox(writer.root)
        command = ControlCommand(command_id, CaptureChange(A, self.source_id, enabled))
        assert inbox.enqueue(command).status is ControlStatus.QUEUED

        def locate(_change, _known):
            return (self.locator(),)

        assert writer.apply_pending(inbox, writer.lease, locate) == ()
        (receipt,) = writer.apply_pending(inbox, writer.lease, locate)
        assert receipt.status is ControlStatus.APPLIED
        return writer.view().epochs[-1]


@pytest.fixture
def claude_scope(native):
    return ClaudeScopeFixture(native)


def test_late_claude_revision_keeps_its_original_native_scope(claude_scope):
    _assert_late_claude_revision_preserves_scope(claude_scope, same_project=False)


def test_late_claude_revision_keeps_original_scope_after_ordinary_mark(claude_scope):
    _assert_late_claude_revision_preserves_scope(claude_scope, same_project=True)


def _assert_late_claude_revision_preserves_scope(claude_scope, *, same_project):
    from test_claude import AFTER as CLAUDE_AFTER
    from test_claude import SESSION as CLAUDE_SESSION
    from test_claude import _native_tool_turn
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_scope import Mark, ScopeState

    native = claude_scope.native
    command_id = UUID(int=0x301)
    path, anchor = claude_scope.path, claude_scope.anchor

    with native.registry.writer() as writer:
        claude_scope.approve(writer)
        state = ScopeState(writer)
        original_ordinal = claude_scope.append(claude_scope.request(3, stop=None))
        early = claude_scope.read(state)
        original = native.observation(early, original_ordinal)
        assert native.routed(state, early, original_ordinal).project_id == A

        destination = _issue(A if same_project else B, 117)
        if same_project:
            command = Mark(command_id, destination, native.receipt_ref(command_id))
            owner = state.operator(A)
            state.authorize(command, owner)
        else:
            command, owner = _authorize_handoff(
                state, native, command_id, A, destination, 0
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
        handoff_batch = claude_scope.read(state)
        target = native.target(handoff_batch, command_id)
        boundary = state.verify_boundary(command, owner, handoff_batch, target)
        apply = state.apply_mark if same_project else state.apply_handoff
        assert apply(command, boundary).status == "applied"

        claude_scope.append(
            claude_scope.request(
                3,
                counts=claude_usage(output=6),
                time=CLAUDE_AFTER + timedelta(seconds=10),
            )
        )
        current = claude_scope.read(state)
        (revised,) = (
            observation
            for observation in current.observations
            if observation.key == original.key
            and observation.revision > original.revision
        )
        assert revised.usage.boundary.ordinal == original_ordinal
        from aitm_usage.monitor_scope import resolve_route

        decision = resolve_route(revised, native.registry.view(), state.view(current))
        assert decision.project_id == A and decision.scope is None
        assert (
            native.routed(state, current, target.boundary.ordinal).scope == destination
        )

        proof = state.verified_revision(current, revised)
        assert proof is not None and proof.route == decision
        assert proof.original.ordinal == original_ordinal
        assert proof.later.ordinal == len(path.read_bytes().splitlines()) - 1
        assert proof.observation is revised
        assert revised.usage.observed_at == original.usage.observed_at
        with pytest.raises(LedgerError):
            state.verified_revision(replace(current), revised)
        with pytest.raises(LedgerError):
            ScopeState(writer).verified_revision(current, revised)
        assert state.verified_revision(current, replace(revised)) is None

        claude_scope.apply_capture(writer, A, False, 4)
        with pytest.raises(LedgerError):
            state.verified_revision(current, revised)


def test_claude_revision_rejects_a_replaced_fixed_prefix(claude_scope):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_scope import ScopeState

    native = claude_scope.native
    with native.registry.writer() as writer:
        claude_scope.approve(writer)
        state = ScopeState(writer)
        claude_scope.append(
            claude_scope.request(3, stop=None),
            claude_scope.request(3, counts=claude_usage(output=6)),
        )
        batch = claude_scope.read(state)
        ((revision, _),) = batch._revision_witnesses
        assert state.verified_revision(batch, revision) is not None

        path = claude_scope.path
        original = path.rename(path.with_suffix(".retained"))
        path.write_bytes(original.read_bytes())
        with pytest.raises(LedgerError):
            state.verified_revision(batch, revision)


def test_claude_cumulative_revision_cannot_cross_disabled_capture(claude_scope):
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_scope import ScopeState

    native = claude_scope.native
    with native.registry.writer() as writer:
        claude_scope.approve(writer)
        state = ScopeState(writer)
        original_ordinal = claude_scope.append(claude_scope.request(3, stop=None))
        early = claude_scope.read(state)
        original = native.observation(early, original_ordinal)
        disabled = claude_scope.apply_capture(writer, A, False, 4)
        during = claude_scope.append(
            claude_scope.request(3, counts=claude_usage(output=6), stop=None)
        )
        enabled = claude_scope.apply_capture(writer, A, True, 5)
        after = claude_scope.append(
            claude_scope.request(3, counts=claude_usage(output=7))
        )
        assert original_ordinal < disabled.ordinal <= during < enabled.ordinal <= after

        current = claude_scope.read(state)
        witnesses = [
            (observation, witness)
            for observation, witness in current._revision_witnesses
            if observation.key == original.key
        ]
        assert [entry.later_ordinal for _, entry in witnesses] == [during, after]
        assert all(
            state.verified_revision(current, observation) is None
            for observation, _ in witnesses
        )


def test_claude_terminal_proof_cannot_certify_disabled_counters(claude_scope):
    from test_claude import MODEL, cost, model_counts
    from test_claude import usage as claude_usage

    from aitm_usage.monitor_scope import ScopeState
    from aitm_usage.types import Availability

    native = claude_scope.native
    with native.registry.writer() as writer:
        claude_scope.approve(writer)
        state = ScopeState(writer)
        original_ordinal = claude_scope.append(claude_scope.request(3, stop=None))
        early = claude_scope.read(state)
        original = native.observation(early, original_ordinal)
        disabled = claude_scope.apply_capture(writer, A, False, 4)
        during = claude_scope.append(
            claude_scope.request(3, counts=claude_usage(output=6))
        )
        enabled = claude_scope.apply_capture(writer, A, True, 5)
        later = claude_scope.append(cost(**{MODEL: model_counts(22, 10, 25, 15, 20)}))
        assert original_ordinal < disabled.ordinal <= during < enabled.ordinal <= later

        current = claude_scope.read(state)
        (update, terminal) = (
            (observation, witness)
            for observation, witness in current._revision_witnesses
            if observation.key == original.key
        )
        assert update[1].later_ordinal == during
        assert terminal[1].later_ordinal == later
        assert terminal[1].predecessor is update[0]
        assert terminal[0].usage.availability is Availability.COMPLETE
        assert state.verified_revision(current, update[0]) is None
        assert state.verified_revision(current, terminal[0]) is None


def test_claude_terminal_proof_cannot_depend_on_other_disabled_counters(claude_scope):
    from test_claude import MODEL, cost, model_counts

    from aitm_usage.monitor_scope import ScopeState
    from aitm_usage.types import Availability

    native = claude_scope.native
    with native.registry.writer() as writer:
        claude_scope.approve(writer)
        state = ScopeState(writer)
        original_ordinal = claude_scope.append(claude_scope.request(3))
        early = claude_scope.read(state)
        original = native.observation(early, original_ordinal)
        disabled = claude_scope.apply_capture(writer, A, False, 4)
        enabled = claude_scope.apply_capture(writer, A, True, 5)
        later = claude_scope.append(cost(**{MODEL: model_counts(20, 10, 25, 15, 20)}))
        assert original_ordinal < disabled.ordinal < enabled.ordinal <= later

        current = claude_scope.read(state)
        (revision,) = [
            item
            for item in current.observations
            if item.key == original.key
            and item.usage.availability is Availability.COMPLETE
        ]
        assert state.verified_revision(current, revision) is None


@pytest.mark.parametrize("reenable", [False, True], ids=["disabled", "reenabled"])
def test_claude_cost_state_checks_its_physical_row(claude_scope, reenable):
    from test_claude import MODEL, cost, model_counts
    from test_claude import user as claude_user

    from aitm_usage.monitor_scope import ScopeState
    from aitm_usage.types import Availability, Eligibility

    native = claude_scope.native
    with native.registry.writer() as writer:
        claude_scope.approve(writer)
        state = ScopeState(writer)
        original_ordinal = claude_scope.append(claude_scope.request(3))
        early = claude_scope.read(state)
        original = native.observation(early, original_ordinal)
        assert original.usage.availability is Availability.PARTIAL
        disable = claude_scope.queue_capture(writer, UUID(int=0x370), enabled=False)
        context = original_ordinal
        if reenable:
            context = claude_scope.append(claude_user(claude_scope.anchor))
            enable = claude_scope.queue_capture(writer, UUID(int=0x371), enabled=True)
            assert disable.ordinal <= context < enable.ordinal
        position = claude_scope.append(cost(**{MODEL: model_counts(12, 6, 15, 9, 12)}))
        decide = writer.span_disposition
        stream = original.usage.boundary.stream_ref
        assert decide(A, claude_scope.source_id, stream, context, context + 1) is (
            Eligibility.EXCLUDED if reenable else Eligibility.ELIGIBLE
        )
        assert decide(A, claude_scope.source_id, stream, position, position + 1) is (
            Eligibility.ELIGIBLE if reenable else Eligibility.EXCLUDED
        )

        current = claude_scope.read(state)
        (revision,) = [
            item
            for item in current.observations
            if item.key == original.key
            and item.usage.availability is Availability.COMPLETE
        ]
        result = state.verified_revision(current, revision)
        if reenable:
            assert result is not None and result.later.ordinal == position
            assert result.original.ordinal == original_ordinal
            assert result.route.project_id == A
        else:
            assert result is None


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


def _scope_file(native):
    return native.registry.root / "scope-v1.json"


def _scope_bytes(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def _held_receipt(state, native, command_id):
    command, owner = _authorize_handoff(state, native, command_id, A, _issue(B, 117), 1)
    _, ordinal = native.append(command_id)
    batch = state.read_source(SOURCE, native.locator())
    return _verify(state, native, command, owner, batch, ordinal)


def _append_storage_fixture_terminal(native, command_id):
    native.turn += 1
    turn = UUID(int=0x200 + native.turn)
    time = AFTER + timedelta(seconds=native.turn)
    call, output = tool_call(native.ledgers[A]), tool_output(command_id)
    call["timestamp"] = output["timestamp"] = time.isoformat()
    native.total += 4
    total, delta = usage(native.total, native.total), usage(4, 4)
    write(
        native.path,
        [
            *begin(native.anchors[A], turn, time=time),
            call,
            response(
                f"response-{native.turn}-terminal", total, delta, time=time, turn=turn
            ),
            counter(total, delta, time=time),
            output,
            end(turn, time=time),
        ],
        append=True,
    )
    native.append()


def _stored_disposition_fixture(state, native):
    """Seed storage from real native boundaries without issuing a proposal."""
    from aitm_usage.monitor_scope import Disposition
    from aitm_usage.types import SourceBoundary, SourceCursor, _encode

    held_id, legacy_id, terminal_id = (UUID(int=i) for i in range(0x501, 0x504))
    owner = state.operator(A)
    command, _ = _authorize_handoff(state, native, held_id, A, _issue(B, 117), 1)
    legacy = Disposition(legacy_id, A, held_id, native.receipt_ref(legacy_id))
    state.authorize(legacy, owner)
    _, held_at = native.append(held_id)
    _, legacy_at = native.append(legacy_id)
    batch = state.read_source(SOURCE, native.locator())
    receipt = _verify(state, native, command, owner, batch, held_at)
    hold = state.hold(receipt)

    path = _scope_file(native)
    payload = json.loads(path.read_bytes())
    terminal = Disposition(terminal_id, A, held_id, native.receipt_ref(terminal_id))
    state.authorize(terminal, owner)
    _append_storage_fixture_terminal(native, terminal_id)
    current = state.read_source(SOURCE, native.locator())
    target = native.target(current, terminal_id)
    terminal_receipt = state.verify_boundary(terminal, owner, current, target)
    legacy_receipt = _verify(state, native, legacy, owner, current, legacy_at)
    payload["format"] = "aitm.usage.monitor-scope/v2"
    payload["held_route_targets"] = [
        {
            "hold_id": str(held_id),
            "boundary": json.loads(_encode(receipt.native_boundary, SourceBoundary)),
            "prefix": json.loads(_encode(batch._native_cursor, SourceCursor)),
        }
    ]
    payload["route_dispositions"] = [
        {
            "command_id": str(terminal_id),
            "command_digest": terminal_receipt.digest,
            "request_digest": "a" * 64,
            "hold_id": str(held_id),
            "hold_state": "held",
            "outcome": "gap",
            "boundary": json.loads(
                _encode(terminal_receipt.native_boundary, SourceBoundary)
            ),
            "prefix": json.loads(_encode(current._native_cursor, SourceCursor)),
            "checkout": native.anchor_ref(A).value,
        }
    ]
    path.write_bytes(_scope_bytes(payload))
    return hold, legacy, legacy_receipt, terminal, terminal_receipt, payload


def test_retained_hold_writes_its_boundary_and_fixed_prefix_together(native):
    from aitm_usage.monitor_scope import ScopeState
    from aitm_usage.types import SourceBoundary, SourceCursor, _encode

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command_id = UUID(int=0x501)
        receipt = _held_receipt(state, native, command_id)
        with pytest.raises(LedgerError, match="writer-verified native scope receipt"):
            state.hold(replace(receipt), retain_route_target=True)
        assert not _scope_file(native).exists()
        hold = state.hold(receipt, retain_route_target=True)
        path = _scope_file(native)
        data = path.read_bytes()
        assert json.loads(data) == {
            "format": "aitm.usage.monitor-scope/v2",
            "events": [],
            "holds": [json.loads(_encode(hold, type(hold)))],
            "resolutions": [],
            "held_route_targets": [
                {
                    "hold_id": str(hold.command_id),
                    "boundary": json.loads(
                        _encode(receipt.native_boundary, SourceBoundary)
                    ),
                    "prefix": json.loads(
                        _encode(receipt._batch._native_cursor, SourceCursor)
                    ),
                }
            ],
            "route_dispositions": [],
        }
        assert state.hold(receipt, retain_route_target=True) == hold
        native.append()
        command, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 1
        )
        batch = state.read_source(SOURCE, native.locator())
        refreshed = _verify(state, native, command, owner, batch, hold.position.ordinal)
        assert refreshed.native_boundary == receipt.native_boundary
        assert (
            refreshed._batch._native_cursor.offset
            > receipt._batch._native_cursor.offset
        )
        with pytest.raises(LedgerError, match="conflicting native proof"):
            state.hold(refreshed, retain_route_target=True)
        assert path.read_bytes() == data
    assert ScopeState(native.registry).view().holds == (hold,)


def test_default_hold_keeps_v1_and_cannot_be_retroactively_retained(native):
    from aitm_usage.monitor_scope import ProofHold, ScopeState
    from aitm_usage.types import _encode

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        receipt = _held_receipt(state, native, UUID(int=0x501))
        hold = state.hold(receipt)
        path = _scope_file(native)
        data = path.read_bytes()
        assert data == _scope_bytes(
            {
                "events": [],
                "format": "aitm.usage.monitor-scope/v1",
                "holds": [json.loads(_encode(hold, ProofHold))],
                "resolutions": [],
            }
        )
        with pytest.raises(LedgerError, match="no retained route target"):
            state.hold(receipt, retain_route_target=True)
        assert path.read_bytes() == data
        assert state.hold(receipt) == hold


@pytest.mark.parametrize("checkout", [B, UNKNOWN])
def test_route_target_requires_the_receipts_anchored_owner(native, checkout):
    from aitm_usage.monitor_scope import ScopeState

    command_id = UUID(int=0x501)
    with native.registry.writer() as writer:
        state = ScopeState(writer)
        command, owner = _authorize_handoff(
            state, native, command_id, A, _issue(B, 117), 1
        )
        cwd = native.anchors[checkout] if checkout == B else native.transcripts
        _, ordinal = native.append(command_id, checkout=cwd)
        batch = state.read_source(SOURCE, native.locator())
        receipt = _verify(state, native, command, owner, batch, ordinal)
        assert receipt.eligible and receipt.anchor_project != A
        with pytest.raises(LedgerError, match="owned native route target"):
            state.hold(receipt, retain_route_target=True)
        assert not _scope_file(native).exists()
        assert state.hold(receipt).project_id == A


def test_retained_hold_refuses_capacity_gap_before_publication(native, monkeypatch):
    from aitm_usage import monitor_scope

    monkeypatch.setattr(monitor_scope, "_MAX_HOLDS", 1)
    with native.registry.writer() as writer:
        state = monitor_scope.ScopeState(writer)
        first = state.hold(_held_receipt(state, native, UUID(int=0x501)))
        second = _held_receipt(state, native, UUID(int=0x502))
        path = _scope_file(native)
        data = path.read_bytes()
        with pytest.raises(LedgerError, match="route target.*capacity"):
            state.hold(second, retain_route_target=True)
        assert path.read_bytes() == data
        overflow = state.hold(second)
        assert overflow.state == "gap"
        assert state.view().holds == (first, overflow)


@pytest.mark.parametrize("when", ["before-replace", "after-replace"])
def test_interrupted_retained_hold_publication_preserves_atomic_snapshot(
    native, monkeypatch, when
):
    import os

    from aitm_usage.monitor_scope import ScopeState

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        first = state.hold(_held_receipt(state, native, UUID(int=0x501)))
        receipt = _held_receipt(state, native, UUID(int=0x502))
        path = _scope_file(native)
        data = path.read_bytes()
        real_replace, real_fsync = os.replace, os.fsync
        published = False

        def interrupt_replace(source, destination, **kwargs):
            nonlocal published
            if destination != path.name:
                return real_replace(source, destination, **kwargs)
            if when == "before-replace":
                raise OSError("interrupted scope publication")
            real_replace(source, destination, **kwargs)
            published = True

        def interrupt_sync(fd):
            if published:
                raise OSError("interrupted scope publication")
            real_fsync(fd)

        with monkeypatch.context() as patch:
            patch.setattr(os, "replace", interrupt_replace)
            patch.setattr(os, "fsync", interrupt_sync)
            with pytest.raises(OSError, match="interrupted scope publication"):
                state.hold(receipt, retain_route_target=True)
        if when == "before-replace":
            assert path.read_bytes() == data
            assert state.view().holds == (first,)
        else:
            payload = json.loads(path.read_bytes())
            assert len(payload["holds"]) == 2
            assert [row["hold_id"] for row in payload["held_route_targets"]] == [
                str(receipt.command_id)
            ]
        hold = state.hold(receipt, retain_route_target=True)
        assert state.view().holds == (first, hold)
        assert not list(path.parent.glob(".publishing-*"))


@pytest.mark.parametrize("operation", ["mark", "handoff", "hold", "expire", "dispose"])
def test_legacy_writers_preserve_both_v2_collections(native, operation):
    from aitm_usage.monitor_scope import Mark, ScopeState

    with native.registry.writer() as writer:
        moment = AFTER
        state = ScopeState(writer, clock=lambda: moment)
        hold, legacy, legacy_receipt, _, _, payload = _stored_disposition_fixture(
            state, native
        )
        initial = state.view()
        assert initial.holds == (hold,)
        assert ScopeState(native.registry).view() == initial

        command_id = UUID(int=0x504)
        if operation == "mark":
            mark = Mark(command_id, _issue(A, 116), native.receipt_ref(command_id))
            owner = state.operator(A)
            state.authorize(mark, owner)
            _, ordinal = native.append(command_id)
            batch = state.read_source(SOURCE, native.locator())
            assert (
                state.apply_mark(
                    mark, _verify(state, native, mark, owner, batch, ordinal)
                ).status
                == "applied"
            )
        elif operation == "handoff":
            command, owner = _authorize_handoff(
                state, native, command_id, A, _issue(B, 117), 1
            )
            _, ordinal = native.append(command_id)
            batch = state.read_source(SOURCE, native.locator())
            assert (
                state.apply_handoff(
                    command, _verify(state, native, command, owner, batch, ordinal)
                ).status
                == "held"
            )
        elif operation == "hold":
            state.hold(_held_receipt(state, native, command_id))
        elif operation == "expire":
            moment = hold.expires_at
            assert len(state.expire()) == 1
        else:
            assert state.dispose(legacy, legacy_receipt).state == "gap"
        data = _scope_file(native).read_bytes()
        assert data != _scope_bytes(payload)
        updated = json.loads(data)
        assert data == _scope_bytes(updated)
        assert updated["format"] == "aitm.usage.monitor-scope/v2"
        for collection in ("held_route_targets", "route_dispositions"):
            assert _scope_bytes(updated[collection]) == _scope_bytes(
                payload[collection]
            )
        assert ScopeState(native.registry).view() == state.view()


@pytest.mark.parametrize(
    "changed",
    [
        "unknown",
        "mixed",
        "missing",
        "extra",
        "nested",
        "hold-digest",
        "command-digest",
        "request-digest",
        "held-state",
        "outcome",
        "resolved-from-gap",
        "duplicate-target",
        "duplicate-disposition",
        "second-disposition",
        "unowned-target",
        "unowned-disposition",
        "terminal-too-early",
        "terminal-reused-receipt",
        "terminal-reused-boundary",
        "empty-prefix",
        "same-prefix",
        "changed-stream",
        "changed-locator",
        "changed-incarnation",
        "changed-session",
        "wrong-provider",
        "wrong-target-position",
        "wrong-hold-surface",
    ],
)
def test_v2_decoder_rejects_malformed_or_unowned_shape(native, changed):
    from aitm_usage.monitor_scope import ScopeState

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        *_, payload = _stored_disposition_fixture(state, native)
        target = payload["held_route_targets"][0]
        record = payload["route_dispositions"][0]
        hold = payload["holds"][0]
        boundary, prefix = record["boundary"], record["prefix"]
        other = native.receipt_ref(UUID(int=0x505)).value
        if changed == "unknown":
            payload["format"] = "aitm.usage.monitor-scope/v3"
        elif changed == "mixed":
            payload["format"] = "aitm.usage.monitor-scope/v1"
        elif changed == "missing":
            del payload["held_route_targets"]
        elif changed == "extra":
            payload["extra"] = None
        elif changed == "nested":
            record["extra"] = None
        elif changed == "hold-digest":
            hold["command_digest"] = "X" * 64
        elif changed == "command-digest":
            record["command_digest"] = "A" * 64
        elif changed == "request-digest":
            record["request_digest"] = "a" * 63
        elif changed == "held-state":
            record["hold_state"] = "resolved"
        elif changed == "outcome":
            record["outcome"] = "held"
        elif changed == "resolved-from-gap":
            record["hold_state"], record["outcome"] = "gap", "resolved"
        elif changed == "duplicate-target":
            payload["held_route_targets"].append(target)
        elif changed == "duplicate-disposition":
            payload["route_dispositions"].append(record)
        elif changed == "second-disposition":
            payload["route_dispositions"].append(
                record
                | {
                    "command_id": str(UUID(int=0x505)),
                    "boundary": boundary | {"receipt_ref": other},
                }
            )
        elif changed == "unowned-target":
            target["hold_id"] = str(UUID(int=0x505))
        elif changed == "unowned-disposition":
            record["hold_id"] = str(UUID(int=0x505))
        elif changed == "terminal-too-early":
            boundary["ordinal"] = hold["affected"]["end"] - 1
        elif changed == "terminal-reused-receipt":
            boundary["receipt_ref"] = target["boundary"]["receipt_ref"]
        elif changed == "terminal-reused-boundary":
            boundary["boundary_ref"] = target["boundary"]["boundary_ref"]
        elif changed == "empty-prefix":
            target["prefix"]["offset"] = 0
        elif changed == "same-prefix":
            prefix["offset"] = target["prefix"]["offset"]
        elif changed == "changed-stream":
            prefix["source_ref"] = boundary["stream_ref"] = other
        elif changed == "changed-locator":
            prefix["locator_ref"] = other
        elif changed == "changed-incarnation":
            prefix["incarnation_ref"] = other
        elif changed == "changed-session":
            boundary["session_ref"] = other
        elif changed == "wrong-provider":
            boundary["provider"] = "claude"
        elif changed == "wrong-target-position":
            target["boundary"]["ordinal"] += 1
        else:
            hold["position"]["surface"] = "codex-cli-linux"
        path = _scope_file(native)
        data = _scope_bytes(payload)
        path.write_bytes(data)
        with pytest.raises(LedgerError, match="Invalid private scope"):
            ScopeState(native.registry).view()
        with pytest.raises(LedgerError, match="Invalid private scope"):
            state.expire()
        assert path.read_bytes() == data


@pytest.mark.parametrize(
    "changed",
    [
        "target-receipt",
        "record-receipt",
        "target-boundary",
        "record-boundary",
        "target-epoch",
        "record-epoch",
        "target-prefix",
        "record-prefix",
        "checkout",
        "source-id",
    ],
)
def test_v2_writer_requires_service_custody_before_mutation(native, changed):
    from aitm_usage.monitor_scope import ScopeState

    with native.registry.writer() as writer:
        now = AFTER
        state = ScopeState(writer, clock=lambda: now)
        hold, *_, payload = _stored_disposition_fixture(state, native)
        target = payload["held_route_targets"][0]
        record = payload["route_dispositions"][0]
        foreign = native.ledgers[A].pseudonymize("foreign", "ref").value
        wrong = native.receipt_ref(UUID(int=0x505)).value
        if changed == "checkout":
            record["checkout"] = foreign
        elif changed == "source-id":
            payload["holds"][0]["position"]["source_id"] = str(UNKNOWN)
        else:
            collection, field = changed.split("-")
            row = target if collection == "target" else record
            if field == "prefix":
                row["prefix"]["anchor_ref"] = foreign
            else:
                row["boundary"][f"{field}_ref"] = (
                    wrong if field == "receipt" else foreign
                )
        path = _scope_file(native)
        data = _scope_bytes(payload)
        path.write_bytes(data)
        reader_view = ScopeState(native.registry).view()
        assert reader_view.events == ()
        assert len(reader_view.holds) == 1
        now = hold.expires_at
        with pytest.raises(LedgerError):
            state.expire()
        assert path.read_bytes() == data


def test_v2_writer_refuses_uninitialized_source_key_without_creating_it(
    native, tmp_path
):
    from aitm_usage.monitor_scope import ScopeState

    with native.registry.writer() as writer:
        *_, payload = _stored_disposition_fixture(ScopeState(writer), native)
    target = Registry(tmp_path / "separate-monitor")
    with target.writer() as writer:
        path = writer.root / "scope-v1.json"
        data = _scope_bytes(payload)
        path.write_bytes(data)
        path.chmod(0o600)
        before = tuple(writer.root.iterdir())
        assert ScopeState(target).view().holds
        with pytest.raises(LedgerError, match="initialized monitor source key"):
            ScopeState(writer).expire()
        assert tuple(writer.root.iterdir()) == before
        assert path.read_bytes() == data


def test_v2_snapshot_does_not_follow_a_link_to_another_file(native):
    from aitm_usage.monitor_scope import ScopeState

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        _stored_disposition_fixture(state, native)
        path = _scope_file(native)
        external = native.path.parent / "external-scope.json"
        data = path.read_bytes()
        path.rename(external)
        path.symlink_to(external)
        with pytest.raises(LedgerError):
            ScopeState(native.registry).view()
        with pytest.raises(LedgerError):
            state.expire()
        assert path.is_symlink()
        assert external.read_bytes() == data


def test_stored_route_disposition_id_is_reserved_against_legacy_writes(native):
    from aitm_usage.monitor_scope import Mark, ScopeState

    with native.registry.writer() as writer:
        state = ScopeState(writer)
        _, _, _, command, receipt, _ = _stored_disposition_fixture(state, native)
        path = _scope_file(native)
        data = path.read_bytes()
        assert state.receipt(command, state.operator(A)) is None
        with pytest.raises(LedgerError, match="route disposition ID"):
            state.dispose(command, receipt)
        with pytest.raises(LedgerError, match="route disposition ID"):
            state.hold(receipt)

        fresh = ScopeState(writer)
        mark = Mark(command.command_id, _issue(A, 116), command.receipt_ref)
        owner = fresh.operator(A)
        fresh.authorize(mark, owner)
        batch = fresh.read_source(SOURCE, native.locator())
        mark_receipt = _verify(
            fresh, native, mark, owner, batch, receipt.position.ordinal
        )
        with pytest.raises(LedgerError, match="route disposition ID"):
            fresh.apply_mark(mark, mark_receipt)
        assert path.read_bytes() == data
