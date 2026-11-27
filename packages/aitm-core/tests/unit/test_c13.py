"""Pure proofs for the C13 extension registration boundary."""

from types import SimpleNamespace

import pytest

from aitm_core.ext.api import (
    ActivityProducerRegistration,
    CapabilitySlot,
    Dependency,
    DirectiveRegistration,
    Extension,
    InitStepRegistration,
)
from aitm_core.ext.registry import RegistrationError, RegistryStatus, load_extensions
from aitm_core.models.config import BacklogIssuer, ExtensionConfig
from aitm_core.providers.backlog import BacklogObservation, IssueRef


def policy(*enabled):
    return SimpleNamespace(
        config=SimpleNamespace(extensions=ExtensionConfig(enabled=enabled))
    )


def extension(name, **values):
    return Extension(
        **(
            {
                "name": name,
                "namespace": name,
                "version": "0.1.0",
                "requires_core": ">=0.1,<0.2",
            }
            | values
        )
    )


def slot(id, **values):
    return CapabilitySlot(
        **(
            {"id": id, "version": 1, "kind": "guard", "placements": ("onExit",)}
            | values
        )
    )


def test_registry_uses_committed_selection_and_declaration_order_is_irrelevant():
    metrics = extension("metrics")
    provider = extension(
        "hosting", dependencies=(Dependency(name="metrics", version=">=0.1"),)
    )
    reports = extension("reports")
    hidden = extension("unselected")
    selection = policy("reports", "hosting", "metrics", "absent")
    expected = ("metrics", "hosting", "reports")

    for declarations in (
        (reports, provider, hidden, metrics),
        (metrics, hidden, provider, reports),
    ):
        registry = load_extensions(selection, declarations)
        assert tuple(item.name for item in registry.ordered) == expected
        assert registry.extension_status("metrics").status is RegistryStatus.ENABLED
        assert registry.extension_status("unselected").status is RegistryStatus.DISABLED
        assert registry.extension_status("absent").status is RegistryStatus.MISSING


def test_dependencies_use_inclusive_and_exclusive_version_limits():
    dependency = Dependency(name="metrics", version=">=0.1,<0.2")
    hosting = extension("hosting", dependencies=(dependency,))
    metrics = extension("metrics", version="0.2.0")
    with pytest.raises(RegistrationError, match="metrics.*incompatible"):
        load_extensions(policy("hosting", "metrics"), (hosting, metrics))


@pytest.mark.parametrize(
    ("installed", "selection", "reason"),
    [
        ((), ("hosting",), "missing"),
        (("metrics",), ("hosting",), "disabled"),
        (("metrics",), ("hosting", "metrics"), "incompatible"),
    ],
)
def test_dependencies_must_resolve_before_dependent_can_be_enabled(
    installed, selection, reason
):
    hosting = extension(
        "hosting", dependencies=(Dependency(name="metrics", version=">=0.1"),)
    )
    declarations = [hosting]
    declarations.extend(
        extension(name, requires_core=">=2")
        if reason == "incompatible"
        else extension(name)
        for name in installed
    )
    with pytest.raises(RegistrationError, match=rf"metrics.*{reason}"):
        load_extensions(policy(*selection), tuple(declarations))


def test_dependency_cycle_fails_closed():
    first = extension(
        "first", dependencies=(Dependency(name="second", version=">=0.1"),)
    )
    second = extension(
        "second", dependencies=(Dependency(name="first", version=">=0.1"),)
    )
    with pytest.raises(RegistrationError, match="cycle"):
        load_extensions(policy("first", "second"), (first, second))


@pytest.mark.parametrize(
    "declarations",
    [
        (extension("one"), extension("one", version="0.2")),
        (extension("one"), extension("two", namespace="one")),
        (extension("one", namespace="core"),),
        (extension("one", capabilities=(slot("two.ready"),)),),
        (
            extension(
                "one", capabilities=(slot("one.ready"), slot("one.ready", version=2))
            ),
        ),
    ],
    ids=(
        "duplicate-name",
        "duplicate-namespace",
        "reserved-namespace",
        "foreign-id",
        "duplicate-id",
    ),
)
def test_ambiguous_or_foreign_declarations_are_refused(declarations):
    with pytest.raises(RegistrationError):
        load_extensions(policy(*(item.name for item in declarations)), declarations)


def test_duplicate_policy_selection_is_refused():
    with pytest.raises(RegistrationError, match="duplicate"):
        load_extensions(policy("one", "one"), (extension("one"),))


@pytest.mark.parametrize(
    ("field", "value"),
    [("version", "wrong"), ("requires_core", "0.1"), ("requires_core", ">=999x")],
)
def test_malformed_installed_version_is_configuration_error(field, value):
    with pytest.raises(ValueError, match="version|specifier"):
        load_extensions(policy("one"), (extension("one", **{field: value}),))


def test_capability_resolution_pins_version_and_allowed_placement():
    registration = slot("github.review", version=2, placements=("onEnter", "onExit"))
    builtin = slot("core.story.identity-recorded")
    github = extension("github", capabilities=(registration,))
    registry = load_extensions(policy("github"), (github,), builtins=(builtin,))
    found = registry.resolve("github.review", version=2, placement="onEnter")
    assert found.status is RegistryStatus.ENABLED
    assert found.registration is registration
    assert (
        registry.resolve(builtin.id, version=1, placement="onExit").registration
        is builtin
    )
    assert (
        registry.resolve("github.review", version=1).status
        is RegistryStatus.INCOMPATIBLE
    )
    assert (
        registry.resolve("github.review", placement="action").status
        is RegistryStatus.INCOMPATIBLE
    )
    assert registry.resolve("github.unknown").status is RegistryStatus.MISSING


def test_disabled_and_incompatible_slots_remain_observable_without_granting_registration():
    disabled = extension("disabled", capabilities=(slot("disabled.guard"),))
    incompatible = extension(
        "incompatible",
        requires_core=">=2.0",
        capabilities=(slot("incompatible.guard"),),
    )
    registry = load_extensions(policy("incompatible"), (disabled, incompatible))
    for identifier, state in (
        ("disabled.guard", RegistryStatus.DISABLED),
        ("incompatible.guard", RegistryStatus.INCOMPATIBLE),
    ):
        found = registry.resolve(identifier)
        assert found.status is state and found.reason and found.registration is None


@pytest.mark.parametrize(
    ("kind", "placement"),
    [("guard", "action"), ("directive", "onExit"), ("action", "onEnter")],
)
def test_declared_slot_cannot_claim_incompatible_placement(kind, placement):
    with pytest.raises(ValueError, match="placement"):
        slot("one.invalid", kind=kind, placements=(placement,))


def test_directive_resolution_returns_typed_metadata_without_loading_a_factory():
    directive = DirectiveRegistration(
        slot=slot("github.describe", kind="directive", placements=("action",)),
        markdown=".aitm/directives/describe.md",
        requested_evidence=("issue-description",),
    )
    enabled = extension("github", directives=(directive,))
    result = load_extensions(policy("github"), (enabled,)).resolve(
        "github.describe", version=1, placement="action"
    )
    assert result.status is RegistryStatus.ENABLED
    assert result.registration is directive
    assert result.registration.markdown == ".aitm/directives/describe.md"


def test_slots_and_directives_share_the_registration_identity_namespace():
    directive = DirectiveRegistration(
        slot=slot("github.conflict", kind="directive", placements=("action",)),
        markdown=".aitm/directives/description.md",
    )
    manifest = extension(
        "github", capabilities=(slot("github.conflict"),), directives=(directive,)
    )
    with pytest.raises(RegistrationError, match="duplicate.*github.conflict"):
        load_extensions(policy("github"), (manifest,))


def test_factories_and_init_steps_are_lazy_registered_calls():
    calls = []

    def cli():
        calls.append("cli")
        return object()

    class FakeBacklog:
        name = "fixture"

        def observe_issue(self, issue):
            return BacklogObservation(issue=issue, status="pending")

    def backlog():
        calls.append("backlog")
        return FakeBacklog()

    def initialize():
        calls.append("init")
        return object()

    step = InitStepRegistration(id="github.setup", version=1, factory=initialize)
    manifest = extension(
        "github",
        init_steps=(step,),
        cli_factory=cli,
        backlog_factory=backlog,
    )
    disabled = load_extensions(policy(), (manifest,))
    assert disabled.ordered == ()
    assert disabled.extension_status("github").status is RegistryStatus.DISABLED
    enabled = load_extensions(policy("github"), (manifest,))
    assert enabled.ordered[0].init_steps[0] is step
    assert enabled.ordered[0].cli_factory is cli
    assert enabled.ordered[0].backlog_factory is backlog
    assert enabled.ordered[0].githost_factory is None
    assert calls == []

    issue = IssueRef(
        issuer=BacklogIssuer(
            backlog="fixture",
            backlog_repository="records",
            numbering_namespace="issues",
        ),
        number=42,
    )
    observation = enabled.ordered[0].backlog_factory().observe_issue(issue)
    assert calls == ["backlog"]
    assert observation.issue == issue and observation.is_present is None


def producer(**values):
    return ActivityProducerRegistration(
        **(
            {
                "id": "fixture.activity",
                "version": 1,
                "measurement_contract": "engaged-interval/v1",
                "coverage_class": "measured-engagement",
            }
            | values
        )
    )


def test_registry_pins_an_activity_producer_to_exact_declared_contract():
    contract = producer()
    fixture = extension("fixture", activity_producers=(contract,))
    registry = load_extensions(policy("fixture"), (fixture,))
    registered = registry.register_activity(contract)
    assert (registered.id, registered.version, registered.measurement_contract) == (
        contract.id,
        1,
        contract.measurement_contract,
    )
    with pytest.raises(RegistrationError, match="not enabled"):
        load_extensions(policy(), (fixture,)).register_activity(contract)


@pytest.mark.parametrize(
    "contract",
    [
        producer(measurement_contract="unknown/v1"),
        producer(coverage_class="tool-duration"),
    ],
)
def test_unsupported_or_contradictory_measurement_contract_is_refused(contract):
    fixture = extension("fixture", activity_producers=(contract,))
    with pytest.raises(RegistrationError, match="measurement"):
        load_extensions(policy("fixture"), (fixture,))


def test_directive_slot_without_markdown_metadata_remains_unavailable():
    manifest = extension(
        "github",
        capabilities=(
            slot("github.describe", kind="directive", placements=("action",)),
        ),
    )
    with pytest.raises(RegistrationError, match="directive.*metadata"):
        load_extensions(policy("github"), (manifest,))


def test_actions_declare_their_execution_mode_and_scoped_applicability():
    from aitm_core.ext.api import CapabilityScope

    scope = CapabilityScope(state_ids=("review",), story_kinds=("story", "defect"))
    registration = slot(
        "github.project",
        kind="action",
        placements=("action",),
        execution="queued",
        scope=scope,
        required_facts=("core.story.publication",),
        produced_evidence=("github.project.observation",),
    )
    manifest = extension("github", capabilities=(registration,))
    resolved = load_extensions(policy("github"), (manifest,)).resolve("github.project")
    assert resolved.registration.scope == scope
    assert resolved.registration.execution == "queued"
    assert resolved.registration.required_facts == ("core.story.publication",)


@pytest.mark.parametrize(
    ("kind", "execution"),
    [("action", None), ("guard", "queued"), ("directive", "requested")],
)
def test_only_effect_actions_have_an_explicit_execution_mode(kind, execution):
    placement = "onExit" if kind == "guard" else "action"
    with pytest.raises(ValueError, match="execution"):
        slot("github.effect", kind=kind, placements=(placement,), execution=execution)


def test_extension_event_names_obey_the_c02_event_envelope_contract():
    from pydantic import BaseModel

    from aitm_core.ext.api import EventRegistration

    class Evidence(BaseModel):
        revision: str

    event = EventRegistration(
        id="github.publication.observed", version=1, model=Evidence
    )
    assert (
        load_extensions(policy("github"), (extension("github", event_types=(event,)),))
        .ordered[0]
        .event_types[0]
        is event
    )
    with pytest.raises(ValueError, match="pattern"):
        EventRegistration(id="github.invalid", version=1, model=Evidence)
