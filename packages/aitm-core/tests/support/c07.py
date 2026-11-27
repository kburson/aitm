"""Committed-policy fixtures shared by schema and Git adapter tests."""

from aitm_core.models.common import StoreAnchor
from aitm_core.models.config import BacklogIssuer
from aitm_core.store.installation import Installation

DEFAULT = "refs/heads/trunk"
PLANNING = "refs/heads/records"
WORKFLOW = ".aitm/workflows/fixture.toml"
WORKFLOW_BYTES = b"id = 'fixture-workflow'\n"


def installation(repository, genesis):
    return Installation(
        repository=repository,
        store=StoreAnchor(
            store_uuid="fixture-store",
            code_default_ref=DEFAULT,
            planning_ref=PLANNING,
            planning_remote=None,
            root_commit=genesis,
        ),
        code_repository="fixture-code",
        planning_repository="fixture-records",
        issuer=BacklogIssuer(
            backlog="local",
            backlog_repository="fixture-issues",
            numbering_namespace="fixture-ids",
        ),
        bootstrap_source="explicit-default",
    )


def settings_at(genesis):
    return f"""
[store]
branch = "records"
trunk = "trunk"
uuid = "fixture-store"
root_commit = "{genesis}"
code_repository = "fixture-code"
repository = "fixture-records"

[enforcement]
mode = "enforce"

[limits]
leaf_agent_hours = 4
expansions_per_attempt = 1
idle_gap_minutes = 15

[providers]
backlog = "local"
backlog_repository = "fixture-issues"
numbering_namespace = "fixture-ids"
githost = "none"

[extensions]
enabled = []

[test]
command = "uv run pytest"
inputs = []
assurance = "captured-export"
prepare_network = "deny"

[review]
schema = "aitm.review-policy/v1"
id = "explicit-fixture"

[review.documents]
binding = "exact-content"
design_coverage = "own-document"
design = ["xpr"]
plan = ["sar"]
assurances = ["declared-manual"]

[review.source]
record_schema = "aitm.source-review/v1"
independence = "distinct-session"
assurances = ["declared-manual"]

[review.exceptions]
enabled = false

[workflow]
file = "{WORKFLOW}"
"""


def updated_effective_settings(settings):
    return (
        settings.replace('mode = "enforce"', 'mode = "advisory"')
        .replace("leaf_agent_hours = 4", "leaf_agent_hours = 2")
        .replace("uv run pytest", "false")
        .replace('githost = "none"', 'githost = "github"')
    )
