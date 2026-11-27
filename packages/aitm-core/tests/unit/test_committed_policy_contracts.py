"""Require explicit, independent policy commitments and installation anchors."""

import tomllib
from dataclasses import replace

import pytest
from pydantic import ValidationError

from aitm_core.models.common import RefObservation
from aitm_core.models.config import CommittedConfig, EnabledExceptions, LegacyRoot
from tests.support.c07 import DEFAULT, PLANNING, installation, settings_at

GENESIS = "a" * 40
EXCEPTION_POLICY = {
    "enabled": True,
    "authority": "review-board",
    "scope": "exact-document-digest",
    "waived_requirement": "explicit",
    "rationale": "required",
    "validity": "bounded",
}


@pytest.fixture
def config():
    return tomllib.loads(settings_at(GENESIS))


def assert_field_refused(config, path):
    with pytest.raises(ValidationError) as error:
        CommittedConfig.model_validate(config)
    locations = [item["loc"] for item in error.value.errors()]
    assert locations and all(location[: len(path)] == path for location in locations)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        pytest.param(
            "documents",
            "binding",
            "latest-revision",
            id="document-review-must-bind-exact-content",
        ),
        pytest.param("documents", "plan", ["self"], id="unsupported-document-level"),
        pytest.param(
            "documents",
            "assurances",
            ["provider-signed"],
            id="source-proof-is-not-document-assurance",
        ),
        pytest.param(
            "source",
            "assurances",
            ["independently-attested"],
            id="document-proof-is-not-source-assurance",
        ),
        pytest.param(
            "source",
            "record_schema",
            "aitm.source-review/v2",
            id="unsupported-source-record-version",
        ),
        pytest.param("source", "assurances", [], id="no-source-assurance-selected"),
    ],
)
def test_source_and_document_policy_reject_incompatible_commitments(
    config, section, field, value
):
    config["review"][section][field] = value
    assert_field_refused(config, ("review", section, field))


def test_stronger_source_review_does_not_supply_document_levels_or_assurance(config):
    config["review"]["source"].update(
        independence="distinct-provider",
        assurances=["runtime-observed", "provider-signed"],
    )
    config["review"]["documents"]["assurances"] = [
        "native-consensus-authority-unavailable",
        "independently-attested",
    ]
    result = CommittedConfig.model_validate(config).review
    assert result.source.independence == "distinct-provider"
    assert result.source.assurances == ("runtime-observed", "provider-signed")
    assert result.documents.design == ("xpr",)
    assert result.documents.plan == ("sar",)
    assert result.documents.assurances == (
        "native-consensus-authority-unavailable",
        "independently-attested",
    )


def test_enabled_exceptions_retain_complete_bounded_authority(config):
    config["review"]["exceptions"] = EXCEPTION_POLICY.copy()
    result = CommittedConfig.model_validate(config).review.exceptions
    assert isinstance(result, EnabledExceptions)
    assert result.model_dump() == EXCEPTION_POLICY


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("authority", " ", id="missing-authority"),
        pytest.param("scope", "any-document", id="unbound-document"),
        pytest.param("waived_requirement", "implicit", id="implicit-waiver"),
        pytest.param("rationale", "optional", id="unexplained-waiver"),
        pytest.param("validity", "unbounded", id="unbounded-validity"),
    ],
)
def test_enabled_exception_cannot_weaken_its_authority_contract(config, field, value):
    config["review"]["exceptions"] = EXCEPTION_POLICY | {field: value}
    assert_field_refused(config, ("review", "exceptions", True, field))


def test_disabled_exception_policy_cannot_carry_undisclosed_authority(config):
    config["review"]["exceptions"]["authority"] = "review-board"
    assert_field_refused(config, ("review", "exceptions", False, "authority"))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("leaf_agent_hours", 0, id="empty-attempt-budget"),
        pytest.param("leaf_agent_hours", "4", id="coerced-attempt-budget"),
        pytest.param("expansions_per_attempt", -1, id="negative-expansion-budget"),
        pytest.param("expansions_per_attempt", 0.5, id="fractional-expansion-budget"),
        pytest.param("idle_gap_minutes", float("inf"), id="unbounded-idle-estimate"),
    ],
)
def test_budget_and_timing_values_fail_closed_without_coercion(config, field, value):
    config["limits"][field] = value
    assert_field_refused(config, ("limits", field))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        pytest.param("assurance", "best-effort", id="unqualified-test-assurance"),
        pytest.param("prepare_network", "auto", id="implicit-network-provisioning"),
        pytest.param(
            "selection",
            {"strategy": "tia"},
            id="selection-requires-unavailability-decision",
        ),
    ],
)
def test_test_policy_requires_explicit_assurance_and_fallback(config, field, value):
    config["test"][field] = value
    path = (
        ("test", "selection", "on_unavailable")
        if field == "selection"
        else ("test", field)
    )
    assert_field_refused(config, path)


def test_explicit_baseline_fallback_retains_containment_and_provisioning_choices(
    config,
):
    config["test"].update(
        assurance="contained",
        prepare_network="allow",
        inputs=["fixtures/*.json"],
        environment=["LANG"],
        selection={"strategy": "tia", "on_unavailable": "baseline"},
    )
    result = CommittedConfig.model_validate(config).test
    assert result.assurance == "contained"
    assert result.prepare_network == "allow"
    assert result.inputs == ("fixtures/*.json",)
    assert result.environment == ("LANG",)
    assert result.selection.on_unavailable == "baseline"


class RefFormatPort:
    """Require the installation to ask its Git boundary to check routing names."""

    ref = PLANNING

    def __init__(self):
        self.checked = []

    def _git(self, command, ref):
        assert command == "check-ref-format"
        self.checked.append(ref)
        return b""

    def _oid(self, value):
        assert value == GENESIS
        return value


def test_hosted_policy_cache_rejects_the_correct_branch_from_wrong_remote():
    repo = RefFormatPort()
    local = installation(repo, GENESIS)
    repo.checked.clear()
    route = replace(local, code_remote="code", code_remote_ref=DEFAULT)
    assert set(repo.checked) == {DEFAULT, "refs/remotes/code/HEAD"}
    wrong = RefObservation(ref=DEFAULT, remote="mirror", observed_commit=GENESIS)
    assert route.policy_ref(wrong) is None
    assert (
        route.policy_ref(wrong.model_copy(update={"remote": "code"}))
        == route.validated_code_ref
    )
    assert route.routing.trunk == "code/trunk"


def test_hosted_policy_cache_rejects_a_different_branch_from_correct_remote():
    route = replace(
        installation(RefFormatPort(), GENESIS),
        code_remote="code",
        code_remote_ref=DEFAULT,
    )
    feature = RefObservation(
        ref="refs/heads/story", remote="code", observed_commit=GENESIS
    )
    assert route.policy_ref(feature) is None


def test_installation_refuses_to_treat_planning_ref_as_default():
    anchor = installation(RefFormatPort(), GENESIS)
    with pytest.raises(ValueError, match="distinct anchored code and planning refs"):
        replace(
            anchor, store=anchor.store.model_copy(update={"code_default_ref": PLANNING})
        )


def test_partial_hosted_route_is_unavailable_instead_of_falling_back_to_local():
    anchor = installation(RefFormatPort(), GENESIS)
    with pytest.raises(ValueError, match="complete code remote/ref pair"):
        replace(anchor, code_remote="code")


def test_legacy_declaration_cannot_replace_independently_anchored_root():
    anchor = installation(RefFormatPort(), GENESIS)
    legacy = LegacyRoot(
        root_commit="b" * 40,
        approved_tip="c" * 40,
        adapter_version="v0",
        allowed_deviations=("root-readme",),
    )
    with pytest.raises(ValueError, match="must name the anchored root"):
        replace(anchor, legacy_root=legacy)
