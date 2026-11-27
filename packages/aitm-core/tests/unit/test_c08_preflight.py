"""Check C08's policy and mutation boundary independently of the Git transport."""

from dataclasses import replace
from types import SimpleNamespace

import pytest

from aitm_core import services
from aitm_core.config import PolicyUnavailable
from aitm_core.models.common import (
    CommandResult,
    LocalOutcome,
    PublicationOutcome,
    StoreAnchor,
)
from aitm_core.store.backend import OperationResult, Snapshot

PIN = Snapshot("fixture-store", "a" * 40, "b" * 40)
CONTENT = "c" * 64


@pytest.fixture
def prepared(monkeypatch):
    anchor = SimpleNamespace(
        repository=object(),
        store=StoreAnchor(
            store_uuid="fixture-store",
            code_default_ref="refs/heads/trunk",
            planning_ref="refs/heads/planning",
            planning_remote=None,
            root_commit="a" * 40,
        ),
        policy_ref=lambda observation: "refs/heads/trunk",
    )
    policy = SimpleNamespace(revision="d" * 40, source=SimpleNamespace(digest=CONTENT))
    policy.writes_fenced = False
    views = SimpleNamespace(
        local=SimpleNamespace(observed_commit=policy.revision),
        planning=SimpleNamespace(observed_commit=PIN.revision),
        code_freshness="fresh",
        code_reason=None,
        shared=None,
    )
    calls = []

    def refresh(current, **options):
        assert current is anchor
        calls.append(("refresh", options.get("cached", False)))
        return views

    def resolve(current, received):
        assert current is anchor and received is views
        calls.append(("policy", received.local.observed_commit))
        return policy

    monkeypatch.setattr(services, "refresh", refresh)
    monkeypatch.setattr(services, "policy", resolve)
    return SimpleNamespace(anchor=anchor, policy=policy, views=views, calls=calls)


def operation(policy_digest=CONTENT):
    return SimpleNamespace(
        operation_id="fixture-op",
        policy_digest=policy_digest,
        change=SimpleNamespace(read_set=("path-version",)),
    )


def test_cached_preflight_requests_no_transport_and_pins_policy(prepared):
    result = services.preflight_policy(prepared.anchor, cached=True)
    assert result.outcome is LocalOutcome.COMPLETED
    assert result.policy is prepared.policy and result.views is prepared.views
    assert prepared.calls == [("refresh", True), ("policy", prepared.policy.revision)]


def test_stale_code_can_record_locally_and_keeps_shared_effects_pending(prepared):
    prepared.views.code_freshness = "stale"
    result = services.preflight_policy(prepared.anchor)
    assert result.outcome is LocalOutcome.COMPLETED
    assert result.publication is PublicationOutcome.PENDING
    assert result.policy is prepared.policy
    assert any("stale" in line for line in result.evidence)


def test_unknown_code_cannot_substitute_other_policy(prepared):
    prepared.views.code_freshness = "unknown"
    prepared.views.local.observed_commit = None
    result = services.preflight_policy(prepared.anchor)
    assert result.outcome is LocalOutcome.INTEGRITY_ERROR
    assert result.policy is None
    assert prepared.calls == [("refresh", False)]


def test_remote_code_rollback_cannot_reuse_stale_policy_for_mutation(prepared):
    prepared.views.code_freshness = "fenced"
    prepared.views.code_reason = "code-default rollback"
    result = services.preflight_policy(prepared.anchor)
    assert result.outcome is LocalOutcome.INTEGRITY_ERROR
    assert result.reason == "code-default rollback"
    assert prepared.calls == [("refresh", False)]


def test_invalid_committed_policy_does_not_fall_back_to_worktree(prepared, monkeypatch):
    def reject(*_args):
        raise PolicyUnavailable("unsupported committed setting")

    monkeypatch.setattr(services, "policy", reject)
    result = services.preflight_policy(prepared.anchor)
    assert result.outcome is LocalOutcome.INTEGRITY_ERROR
    assert result.policy is None and result.reason == "unsupported committed setting"


def test_changed_committed_routing_fences_the_current_mutation(prepared):
    prepared.policy.writes_fenced = True
    result = services.preflight_policy(prepared.anchor)
    assert result.outcome is LocalOutcome.INTEGRITY_ERROR
    assert result.policy is prepared.policy
    assert "routing" in result.reason


def test_content_invalid_remote_tip_blocks_mutation_after_refresh(prepared):
    prepared.views.shared = SimpleNamespace(
        status="quarantined", reason="planning path refused", local_diverged=False
    )
    result = services.prepare_mutation(prepared.anchor, operation(), PIN)
    assert result.outcome is LocalOutcome.INTEGRITY_ERROR
    assert result.reason == "planning path refused"


def test_unpublished_local_divergence_keeps_shared_effects_pending(prepared):
    prepared.views.shared = SimpleNamespace(
        status="verified", reason=None, local_diverged=True
    )
    result = services.prepare_mutation(prepared.anchor, operation(), PIN)
    assert result.outcome is LocalOutcome.COMPLETED
    assert result.publication is PublicationOutcome.PENDING


def test_first_offline_planning_observation_cannot_authorize_shared_effects(prepared):
    prepared.views.shared = SimpleNamespace(
        status="unknown", reason=None, local_diverged=False
    )
    result = services.preflight_policy(prepared.anchor)
    assert result.outcome is LocalOutcome.COMPLETED
    assert result.publication is PublicationOutcome.PENDING


def test_reconciled_remote_observation_marks_shared_operation_pending(prepared):
    prepared.views.shared = SimpleNamespace(
        status="verified", reason=None, local_diverged=False
    )
    result = services.prepare_mutation(prepared.anchor, operation(), PIN)
    assert result.outcome is LocalOutcome.COMPLETED
    assert result.publication is PublicationOutcome.PENDING


def test_local_only_observation_keeps_publication_not_applicable(prepared):
    prepared.views.code_freshness = "local-only"
    prepared.views.shared = SimpleNamespace(
        status="local-only", reason=None, local_diverged=False
    )
    result = services.prepare_mutation(prepared.anchor, operation(), PIN)
    assert result.outcome is LocalOutcome.COMPLETED
    assert result.publication is PublicationOutcome.NOT_APPLICABLE


def test_advanced_planning_view_requires_a_new_pinned_operation(prepared):
    result = services.prepare_mutation(
        prepared.anchor, operation(), replace(PIN, revision="e" * 40)
    )
    assert result.outcome is LocalOutcome.CONFLICT
    assert "planning" in result.reason


def test_exact_policy_digest_must_match_operation_guard_basis(prepared):
    result = services.prepare_mutation(prepared.anchor, operation("e" * 64), PIN)
    assert result.outcome is LocalOutcome.CONFLICT
    assert "policy" in result.reason


def test_mutation_refreshes_before_the_backend_can_evaluate_guards(
    prepared, monkeypatch
):
    op = operation()
    prepared.views.code_freshness = "stale"

    def create_backend(*_args, **_options):
        assert _options["code_pin"] == ("refs/heads/trunk", prepared.policy.revision)
        assert _args[1].code_default_ref == "refs/heads/trunk"
        prepared.calls.append(("backend", None))

        def transact(request, expected):
            assert request is op and expected is PIN
            prepared.calls.append(("guarded-transaction", None))
            command = CommandResult(
                operation_id=op.operation_id, local=LocalOutcome.COMPLETED
            )
            return OperationResult(command, PIN)

        return SimpleNamespace(transact=transact)

    monkeypatch.setattr(services, "backend", create_backend)
    result = services.mutate(prepared.anchor, op, PIN)
    assert prepared.calls == [
        ("refresh", False),
        ("policy", prepared.policy.revision),
        ("backend", None),
        ("guarded-transaction", None),
    ]
    assert result.command.local is LocalOutcome.COMPLETED
    assert result.command.publication is PublicationOutcome.PENDING
    assert any("stale" in line for line in result.command.evidence)


def test_mutation_refusal_never_constructs_the_guarded_backend(prepared, monkeypatch):
    prepared.policy.writes_fenced = True

    def unavailable(*_args, **_options):
        pytest.fail("the guarded backend was entered with fenced policy")

    monkeypatch.setattr(services, "backend", unavailable)
    result = services.mutate(prepared.anchor, operation(), PIN)
    assert result.command.local is LocalOutcome.INTEGRITY_ERROR
    assert result.snapshot == PIN
    assert prepared.calls == [("refresh", False), ("policy", prepared.policy.revision)]


def test_prepare_mutation_retains_expected_snapshot_and_operation_read_set(prepared):
    request = operation()
    result = services.prepare_mutation(prepared.anchor, request, PIN)
    assert result.expected is PIN
    assert result.read_set is request.change.read_set
    assert result.policy is prepared.policy


def test_refresh_port_cannot_silently_supply_an_untyped_view():
    ports = services.ServicePorts(policy_refresh=lambda _: object())
    with pytest.raises(services.UnavailablePort, match="policy_refresh"):
        services.refresh(object(), ports=ports)


def test_cached_refresh_does_not_call_the_registered_transport(monkeypatch):
    from aitm_core.store import fetch

    anchor = object()
    observation = object()

    def lookup(request):
        assert request.installation is anchor
        return observation

    def transport(_):
        pytest.fail("cached reads must not call the refresh port")

    monkeypatch.setattr(fetch, "cached_refs", lookup)
    ports = services.ServicePorts(policy_refresh=transport)
    assert services.refresh(anchor, cached=True, ports=ports) is observation


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        pytest.param(b"[]", "JSON object", id="object-required"),
        pytest.param(
            b'{"code_repository":"first","code_repository":"shadow"}',
            "duplicate",
            id="route-key-cannot-be-shadowed",
        ),
        pytest.param(
            b'{"code_repository":"code","planning_repository":"store",'
            b'"bootstrap_source":"explicit","store":{}}',
            "Invalid anchored",
            id="descriptor-cannot-replace-trusted-store",
        ),
    ],
)
def test_installation_coordinates_refuse_ambiguous_or_unowned_input(raw, message):
    descriptor = SimpleNamespace(read_bytes=lambda: raw)
    with pytest.raises(ValueError, match=message):
        services.load_installation(object(), object(), descriptor)


def test_installed_policy_uses_c07_coordinates_and_preserves_anchor():
    repo = SimpleNamespace(
        ref="refs/heads/planning",
        _git=lambda *args: b"",
        _oid=lambda value: value,
    )
    store = StoreAnchor(
        store_uuid="fixture-store",
        code_default_ref="refs/heads/trunk",
        planning_ref=repo.ref,
        planning_remote="planning-remote",
        root_commit="a" * 40,
    )
    descriptor = SimpleNamespace(
        read_bytes=lambda: (
            b'{"code_repository":"code","planning_repository":"store",'
            b'"bootstrap_source":"explicit","code_remote":"code-remote",'
            b'"code_remote_ref":"refs/heads/main","issuer":{"backlog":"local",'
            b'"backlog_repository":"fixture-issues","numbering_namespace":"fixture"}}'
        )
    )
    bound = services.load_installation(repo, store, descriptor)
    assert bound.store is store
    assert bound.repository is repo and bound.bootstrap_source == "explicit"
    assert bound.routing.trunk == "code-remote/main"
    assert bound.routing.store.planning_remote == "planning-remote"


def test_operation_gate_refuses_if_admitted_code_pin_changes(monkeypatch):
    from aitm_core.store import gate

    def read(command, *_args):
        if command == "symbolic-ref":
            return SimpleNamespace(returncode=1)
        assert command == "show-ref"
        return SimpleNamespace(returncode=0, stdout=b"b" * 40 + b"\n")

    def make_gate(_repo, _target, _purpose, *, planning_validation):
        return planning_validation

    monkeypatch.setattr(gate, "ref_gate", make_gate)
    repo = SimpleNamespace(_run=read)
    store = StoreAnchor(
        store_uuid="fixture-store",
        code_default_ref="refs/heads/trunk",
        planning_ref="refs/heads/planning",
        planning_remote=None,
        root_commit="e" * 40,
    )
    bound = services.backend(repo, store, code_pin=("refs/heads/trunk", "a" * 40))
    validate = bound._gate(repo, store.planning_ref)
    report = validate(PIN.revision)
    assert report.outcome is LocalOutcome.CONFLICT
    assert report.tip == PIN.revision and "pin changed" in report.reason
