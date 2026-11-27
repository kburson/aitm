"""Explicit commitments in the supported Core policy."""

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictStr,
    StringConstraints,
)

from aitm_core.models.common import StoreAnchor

Name = Annotated[StrictStr, StringConstraints(strip_whitespace=False, pattern=r"\S")]
Oid = Annotated[
    StrictStr, StringConstraints(pattern=r"^(?:[a-f0-9]{40}|[a-f0-9]{64})$")
]
ReviewLevel = Literal["sar", "spr", "xpr"]
DocumentAssurance = Literal[
    "declared-manual",
    "native-consensus-authority-unavailable",
    "independently-attested",
]
SourceAssurance = Literal["declared-manual", "runtime-observed", "provider-signed"]


class ConfigSection(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class LegacyRoot(ConfigSection):
    root_commit: Oid
    approved_tip: Oid
    adapter_version: Name
    allowed_deviations: tuple[Name, ...]


class StoreConfig(ConfigSection):
    code_repository: Name
    repository: Name
    branch: Name
    trunk: Name
    remote: Name | None = None
    uuid: Name
    root_commit: Oid
    legacy_root: LegacyRoot | None = None


class BacklogIssuer(ConfigSection):
    backlog: Name
    backlog_repository: Name
    numbering_namespace: Name


class ProviderConfig(BacklogIssuer):
    githost: Name


class EnforcementConfig(ConfigSection):
    mode: Literal["advisory", "enforce"]


class Limits(ConfigSection):
    leaf_agent_hours: Annotated[float, Field(strict=True, gt=0, le=4)]
    expansions_per_attempt: Annotated[int, Field(strict=True, ge=0, le=1)]
    idle_gap_minutes: Annotated[float, Field(strict=True, gt=0, allow_inf_nan=False)]


class ExtensionConfig(ConfigSection):
    enabled: tuple[Name, ...]


class TestSelection(ConfigSection):
    strategy: Name
    on_unavailable: Literal["baseline", "hold"]


class TestConfig(ConfigSection):
    command: Name
    inputs: tuple[Name, ...]
    environment: tuple[Name, ...] | None = None
    assurance: Literal["captured-export", "contained"]
    prepare_network: Literal["deny", "allow"]
    selection: TestSelection | None = None


class DocumentPolicy(ConfigSection):
    binding: Literal["exact-content"]
    design_coverage: Literal["own-document"]
    design: tuple[ReviewLevel, ...]
    plan: tuple[ReviewLevel, ...]
    assurances: Annotated[tuple[DocumentAssurance, ...], Field(min_length=1)]


class SourcePolicy(ConfigSection):
    record_schema: Literal["aitm.source-review/v1"]
    independence: Literal["distinct-session", "distinct-provider"]
    assurances: Annotated[tuple[SourceAssurance, ...], Field(min_length=1)]


class DisabledExceptions(ConfigSection):
    enabled: Literal[False]


class EnabledExceptions(ConfigSection):
    enabled: Literal[True]
    authority: Name
    scope: Literal["exact-document-digest"]
    waived_requirement: Literal["explicit"]
    rationale: Literal["required"]
    validity: Literal["bounded"]


class ReviewPolicy(ConfigSection):
    schema_version: Literal["aitm.review-policy/v1"] = Field(alias="schema")
    id: Name
    documents: DocumentPolicy
    source: SourcePolicy
    exceptions: Annotated[
        DisabledExceptions | EnabledExceptions, Field(discriminator="enabled")
    ]


class WorkflowConfig(ConfigSection):
    file: Name


class CommittedConfig(ConfigSection):
    store: StoreConfig
    enforcement: EnforcementConfig
    limits: Limits
    providers: ProviderConfig
    extensions: ExtensionConfig
    test: TestConfig
    review: ReviewPolicy
    workflow: WorkflowConfig


class Routing(ConfigSection):
    store: StoreAnchor
    code_repository: Name
    planning_repository: Name
    trunk: Name
    issuer: BacklogIssuer
    legacy_root: LegacyRoot | None = None
