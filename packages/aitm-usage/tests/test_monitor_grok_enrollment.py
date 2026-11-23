"""Prospective Grok enrollment from an exact applied owner command."""

from contextlib import contextmanager
from dataclasses import dataclass, replace

import pytest
from grok_capture_policy_cases import grok_capture_policy as grok_capture_policy
from test_monitor_grok_capture import isolated_grok_capture as isolated_grok_capture

from aitm_usage.monitor_control import ControlInbox
from aitm_usage.monitor_registry import (
    BoundaryUnavailable,
    ControlStatus,
    RegistryView,
    _encode_registry,
    _GrokEpoch,
    _GrokPending,
)
from aitm_usage.monitor_scope import RouteStatus, ScopeState, resolve_route
from aitm_usage.sources import grok
from aitm_usage.sources.grok import GrokAdapter
from aitm_usage.types import DiagnosticCode, _decode


@dataclass(frozen=True, slots=True)
class _OldRegistryWithGrok(RegistryView):
    grok_records: tuple[_GrokEpoch | _GrokPending, ...] = ()


def _enroll(f, locator, *, scopes=None, inbox=None):
    if scopes is None:
        scopes = f.state
    if inbox is None:
        inbox = ControlInbox(f.writer.root)
    return scopes.enroll_grok(inbox, f.project, f.source_id, locator())


def _hookless(f):
    return f.rows[1:5]


@contextmanager
def _hide_original_stream(f, monkeypatch):
    original = f.locator()._source.path
    raw_transcripts = grok._transcripts

    def visible_transcripts(fd, root):
        return (path for path in raw_transcripts(fd, root) if path != original)

    with monkeypatch.context() as discovery:
        discovery.setattr(grok, "_transcripts", visible_transcripts)
        yield


def test_eligible_empty_root_grant_cannot_be_parsed_by_old_reader(
    grok_capture_policy, monkeypatch
):
    f = grok_capture_policy
    with _hide_original_stream(f, monkeypatch):
        enable = f.submit(33101, True)
        (receipt,) = f.evaluate()
        assert receipt.command_id == enable.command_id
        assert receipt.status is ControlStatus.APPLIED
        state = f.writer.view()
        wire = _encode_registry(state)
        with pytest.raises(ValueError):
            _decode(wire, _OldRegistryWithGrok)
        assert f.state.grok_enrollment_gaps() == ()
    assert _enroll(f, f.locator) is None


def test_first_enrollment_reuses_exact_applied_enable_and_keeps_future_turns(
    grok_capture_policy,
):
    f = grok_capture_policy
    enable = f.submit(33102, True)
    (receipt,) = f.evaluate()
    assert receipt.command_id == enable.command_id
    assert receipt.status is ControlStatus.APPLIED
    first = f.writer.view()
    legacy = _encode_registry(first)
    assert _encode_registry(_decode(legacy, _OldRegistryWithGrok)) == legacy
    other, write = f.add_stream()
    old = _hookless(f)
    write(old, 1)
    assert _enroll(f, other) is None
    current = f.writer.view()
    assert current.receipts == first.receipts
    assert _encode_registry(current) != legacy
    (gap,) = f.state.grok_enrollment_gaps()
    assert (gap.start, gap.end, gap.code) == (
        0,
        len(b"".join(old)),
        DiagnosticCode.COVERAGE_GAP,
    )
    assert _gaps_after_reopen(f) == (gap,)
    write([*old, f.rows[5], *f.rows[7:]], 2)
    batch = f.state.read_source(f.source_id, other())
    (observed,) = batch.observations
    route = resolve_route(observed, f.writer.view(), f.state.view(batch))
    assert route.status is RouteStatus.ROUTED
    assert route.project_id == f.project and route.scope is None


def _gaps_after_reopen(f):
    state = ScopeState(f.writer, grok_reader=GrokAdapter(f.find_origin, f.verifier))
    return state.grok_enrollment_gaps()


def test_queued_disable_fences_prospective_enrollment(grok_capture_policy):
    f = grok_capture_policy
    f.submit(33103, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, _ = f.add_stream()
    before = f.writer.view()
    disable = f.submit(33104, False)
    with pytest.raises(BoundaryUnavailable):
        _enroll(f, other)
    assert f.writer.view() == before
    assert f.writer.command_status(disable.command_id) is None


def test_rejected_enable_receipt_cannot_authorize_prospective_capture(
    grok_capture_policy,
    monkeypatch,
):
    f = grok_capture_policy
    enable = f.submit(33105, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    current = f.writer.view()
    rejected = tuple(
        replace(row, status=ControlStatus.REJECTED)
        if row.command_id == enable.command_id
        else row
        for row in current.receipts
    )
    f.writer._save(replace(current, receipts=rejected))
    other, _ = f.add_stream()
    monkeypatch.setattr(
        GrokAdapter,
        "_capture_material",
        lambda *a, **kw: pytest.fail("Rejected enable opened selected payload"),
    )
    with pytest.raises(BoundaryUnavailable, match="no proven applied enable"):
        _enroll(f, other)
    assert f.state.grok_enrollment_gaps() == ()


def test_reissued_enable_preserves_an_armed_stream_and_original_grant(
    grok_capture_policy,
):
    from aitm_usage.monitor_registry import _grok_records, _GrokGrant

    f = grok_capture_policy
    first = f.submit(33106, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, write = f.add_stream()
    first_turn = _hookless(f)
    write(first_turn[:1], 0)
    with pytest.raises(BoundaryUnavailable, match="finish"):
        _enroll(f, other)
    (armed,) = (
        row for row in _grok_records(f.writer.view()) if type(row) is _GrokGrant
    )
    assert armed.command_id == first.command_id
    assert f.state.grok_enrollment_gaps() == ()

    again = f.submit(33107, True)
    (receipt,) = f.evaluate()
    assert receipt.command_id == again.command_id
    assert receipt.status is ControlStatus.APPLIED
    assert armed in _grok_records(f.writer.view())
    assert not any(type(row) is _GrokPending for row in _grok_records(f.writer.view()))

    write(first_turn, 1)
    assert _enroll(f, other) is None
    committed = f.writer.view()
    (grant,) = (row for row in _grok_records(committed) if type(row) is _GrokGrant)
    assert grant.command_id == first.command_id
    assert {
        row.generation for row in _grok_records(committed) if type(row) is _GrokEpoch
    } == {grant.generation}
    assert _enroll(f, other) is None
    assert f.writer.view() == committed
    assert f.state.read_source(f.source_id, other()).observations == ()
    write([*first_turn, f.rows[5], *f.rows[7:]], 2)
    (next_turn,) = f.state.read_source(f.source_id, other()).observations
    assert next_turn.usage.tokens.output_tokens == 38


def test_wrong_terminal_and_rewritten_arm_hold_the_original_enrollment(
    grok_capture_policy,
):
    f = grok_capture_policy
    f.submit(33108, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, write = f.add_stream()
    write(f.rows[:2], 0)
    with pytest.raises(BoundaryUnavailable, match="finish"):
        _enroll(f, other)
    armed = f.writer.view()
    f.refs.clear()
    write(f.rows[:5], 1)
    with pytest.raises(BoundaryUnavailable, match="finish"):
        _enroll(f, other)
    assert f.writer.view() == armed
    changed = [b" " + f.rows[0], *f.rows[1:5]]
    write(changed, 1)
    with pytest.raises(BoundaryUnavailable, match="proof is unavailable"):
        _enroll(f, other)
    assert f.writer.view() == armed


def test_disable_retains_unresolved_gap_and_never_applies_a_later_enrollment(
    grok_capture_policy,
):
    f = grok_capture_policy
    f.submit(33109, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, write = f.add_stream()
    write(_hookless(f)[:1], 0)
    with pytest.raises(BoundaryUnavailable, match="finish"):
        _enroll(f, other)
    disable = f.submit(33110, False)
    with pytest.raises(BoundaryUnavailable, match="pending"):
        _enroll(f, other)
    assert f.evaluate()[0].command_id == disable.command_id
    (gap,) = _gaps_after_reopen(f)
    assert gap.start is None and gap.end is None
    assert gap.code is DiagnosticCode.COVERAGE_GAP
    write(_hookless(f), 1)
    with pytest.raises(BoundaryUnavailable, match="applied enable"):
        _enroll(f, other)
    assert f.state.grok_enrollment_gaps() == (gap,)


def test_replacement_stream_or_profile_requires_exact_new_owner_authority(
    isolated_grok_capture,
):
    f = isolated_grok_capture
    f.submit(33111, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, _ = f.add_stream()
    assert _enroll(f, other) is None
    before = f.writer.view()
    f.replace_incarnation()
    with pytest.raises(BoundaryUnavailable, match="fresh capture interval"):
        _enroll(f, f.locator)
    assert f.writer.view() == before

    f.revise("replace", 2)
    with pytest.raises(BoundaryUnavailable, match="current enable"):
        _enroll(f, other)
    assert f.writer.view() == before
    enable = f.submit(33112, True)
    assert f.evaluate()[0].command_id == enable.command_id
    assert _enroll(f, other) is None
    assert f.writer.command_status(enable.command_id).status is ControlStatus.APPLIED


def test_unmatched_checkout_cannot_open_payload_or_enroll(
    grok_capture_policy,
    monkeypatch,
):
    f = grok_capture_policy
    f.submit(33113, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, _ = f.add_stream()

    def unowned(file):
        origin = f.find_origin(file)
        return None if origin is None else replace(origin, checkout=None)

    adapter = GrokAdapter(unowned, f.verifier)
    scopes = ScopeState(f.writer, grok_reader=adapter)
    (locator,) = (
        row for row in adapter.discover(f.root) if row.stream_ref == other().stream_ref
    )
    before = f.writer.view()
    monkeypatch.setattr(
        GrokAdapter,
        "_capture_material",
        lambda *a, **kw: pytest.fail("Unmatched checkout opened selected payload"),
    )
    with pytest.raises(BoundaryUnavailable, match="no matching checkout"):
        _enroll(f, lambda: locator, scopes=scopes)
    assert f.writer.view() == before


def test_inherited_turn_cannot_complete_a_prospective_arm(grok_capture_policy):
    from test_grok import PROMPT_A

    f = grok_capture_policy
    f.submit(33114, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, write = f.add_stream()

    def inherited(file):
        origin = f.find_origin(file)
        return (
            None
            if origin is None
            else replace(origin, inherited_prompt_ids=frozenset({PROMPT_A}))
        )

    adapter = GrokAdapter(inherited, f.verifier)
    scopes = ScopeState(f.writer, grok_reader=adapter)

    def locate():
        (locator,) = (
            row
            for row in adapter.discover(f.root)
            if row.stream_ref == other().stream_ref
        )
        return locator

    turn = _hookless(f)
    write(turn[:1], 0)
    with pytest.raises(BoundaryUnavailable, match="finish"):
        _enroll(f, locate, scopes=scopes)
    before = f.writer.view()
    write(turn, 1)
    with pytest.raises(BoundaryUnavailable, match="proof is unavailable"):
        _enroll(f, locate, scopes=scopes)
    assert f.writer.view() == before


def test_reissue_cannot_replace_the_incarnation_of_an_existing_arm(
    grok_capture_policy,
    monkeypatch,
):
    f = grok_capture_policy
    f.submit(33115, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, write = f.add_stream()
    turn = _hookless(f)
    write(turn[:1], 0)
    with pytest.raises(BoundaryUnavailable, match="finish"):
        _enroll(f, other)
    armed = f.writer.view()
    path = other()._source.path
    evidence = f.writer.source_evidence()
    changed = replace(
        f.find_origin(path),
        incarnation=evidence.pseudonymize("grok-incarnation", "different-writer"),
    )

    def replaced(candidate):
        return changed if candidate == path else f.find_origin(candidate)

    monkeypatch.setattr(f.reader, "verify_origin", replaced)
    write(turn, 1)
    another = f.submit(33116, True)
    assert f.evaluate() == ()
    assert f.writer.command_status(another.command_id) is None
    assert f.writer.view() == armed


@pytest.mark.parametrize("open_turn", [False, True], ids=["quiet", "in-flight"])
def test_reissued_enable_retains_the_new_streams_pre_witness_gap(
    grok_capture_policy,
    monkeypatch,
    open_turn,
):
    f = grok_capture_policy
    with _hide_original_stream(f, monkeypatch):
        enable = f.submit(33117, True)
        assert f.evaluate()[0].command_id == enable.command_id
        other, write = f.add_stream()
        turn = _hookless(f)
        write(turn[:1] if open_turn else turn, 0 if open_turn else 1)
        again = f.submit(33118, True)
        with pytest.raises(BoundaryUnavailable, match="pending"):
            _enroll(f, other)
        if open_turn:
            assert f.evaluate() == ()
            assert f.state.grok_enrollment_gaps() == ()
            write(turn, 1)
        assert f.evaluate()[0].command_id == again.command_id
        (gap,) = _gaps_after_reopen(f)
        assert (gap.start, gap.end, gap.code) == (
            0,
            len(b"".join(turn)),
            DiagnosticCode.COVERAGE_GAP,
        )
        enrolled = f.writer.view()
        assert _enroll(f, other) is None
        assert f.writer.view() == enrolled
        assert f.state.read_source(f.source_id, other()).observations == ()


def test_retired_gap_survives_restored_approval_set_and_a_new_root_grant(
    grok_capture_policy,
    monkeypatch,
):
    from uuid import UUID

    from aitm_usage import monitor_control, monitor_registry
    from aitm_usage.ledger import ConflictError, LedgerError
    from aitm_usage.monitor_registry import (
        CaptureChange,
        ControlCommand,
        Registry,
        _grok_records,
        _GrokGrant,
        _PhysicalDirectory,
    )
    from aitm_usage.monitor_scope import _GrokCaptureHeld

    f = grok_capture_policy
    f.submit(33119, True)
    assert f.evaluate()[0].status is ControlStatus.APPLIED
    other, write = f.add_stream()
    write(_hookless(f), 1)
    assert _enroll(f, other) is None
    (old_gap,) = _gaps_after_reopen(f)
    disable = f.submit(33120, False)
    assert f.evaluate()[0].command_id == disable.command_id
    retired = f.writer.view()
    (old_source,) = retired.sources

    replacement = _PhysicalDirectory(
        str(f.root.path.with_name("replacement-capture")), (1, 99)
    )
    directory = monitor_registry._directory

    def observe_directory(path, **options):
        return replacement if path == replacement.path else directory(path, **options)

    monkeypatch.setattr(monitor_registry, "_directory", observe_directory)
    previous = f.writer._live_profile
    (installation,) = previous.installations
    new_installation = replace(installation, directory=replacement)
    f.writer._live_profile = replace(
        previous,
        generation=f.writer.source_evidence().pseudonymize(
            "fixture-profile", "replacement"
        ),
        installations=(new_installation,),
        current=lambda actual: actual is new_installation,
    )
    # The established approval contract does not allow reusing an old source ID.
    with pytest.raises(ConflictError, match="identity changed"):
        f.writer.approve_source(replace(old_source.approval, root=replacement.path))
    new_source = UUID(int=33121)
    f.writer.approve_source(
        replace(old_source.approval, source_id=new_source, root=replacement.path)
    )
    both = f.writer.view()
    # Exercise a retained approval snapshot with the retired source omitted.
    f.writer._save(
        replace(
            both,
            sources=tuple(row for row in both.sources if row.source_id == new_source),
        )
    )
    assert _gaps_after_reopen(f) == (old_gap,)

    inbox = ControlInbox(f.writer.root)
    enable = ControlCommand(UUID(int=33122), CaptureChange(f.project, new_source, True))
    inbox.enqueue(enable)
    (applied,) = f.writer.apply_pending(
        inbox,
        f.writer.lease,
        None,
        grok_evidence=lambda change, active, pending: f.state._grok_capture_evidence(
            change, (), active, pending
        ),
    )
    assert (
        applied.command_id == enable.command_id
        and applied.status is ControlStatus.APPLIED
    )
    grants = tuple(
        row for row in _grok_records(f.writer.view()) if type(row) is _GrokGrant
    )
    assert {(row.source_id, row.active) for row in grants} == {
        (f.source_id, False),
        (new_source, True),
    }
    assert _gaps_after_reopen(f) == (old_gap,)
    current = f.writer.view()
    f.writer._save(replace(current, sources=()))
    with pytest.raises(LedgerError, match="grant installation changed"):
        _gaps_after_reopen(f)

    f.writer._save(replace(current, sources=both.sources))
    monkeypatch.setattr(
        monitor_registry, "_read_private", monitor_control._read_private
    )
    reopened = Registry(f.writer.root, f.writer.lease)
    state = ScopeState(reopened, grok_reader=GrokAdapter(f.find_origin, f.verifier))
    with pytest.raises(_GrokCaptureHeld, match="authority"):
        state.read_source(f.source_id, f.locator())
