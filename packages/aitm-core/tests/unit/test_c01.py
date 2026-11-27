"""Command outcome and service capability contracts without a subprocess."""

import json

from typer.testing import CliRunner

from aitm_core.cli.app import build_cli
from aitm_core.models.common import CommandResult, LocalOutcome, PublicationOutcome
from aitm_core.services import ServicePorts, UnavailablePort


def test_result_schema_and_exit_codes():
    results = [
        CommandResult(operation_id="op", local=local, publication=publication)
        for local, publication in [
            ("completed", "not-applicable"),
            ("refused", "not-applicable"),
            ("conflict", "not-applicable"),
            ("integrity-error", "not-applicable"),
            ("completed", "pending"),
        ]
    ]
    assert LocalOutcome.REFUSED == "refused"
    assert PublicationOutcome.PENDING == "pending"
    for expected, result in enumerate(results):
        payload = result.model_dump_json()
        assert CommandResult.model_validate_json(payload) == result
        assert result.exit_code == expected
    payloads = [json.loads(result.model_dump_json()) for result in results]
    assert payloads[0] == {
        "schema": "aitm.command-result/v1",
        "operation_id": "op",
        "local": "completed",
        "publication": "not-applicable",
        "pending": [],
        "evidence": [],
        "recovery": None,
    }
    assert payloads[-1]["local"] == "completed"
    assert payloads[-1]["publication"] == "pending"


def test_missing_route_and_port_decline():
    result = CliRunner().invoke(
        build_cli({("probe",): "aitm_core.cli.deliberately_unregistered"}),
        ["--json", "probe"],
    )
    assert result.exit_code != 0
    assert json.loads(result.stdout)["local"] == "unavailable"
    ports = ServicePorts()
    for name in (
        "policy_resolution",
        "policy_refresh",
        "validation_gate",
        "write_authorization",
        "attempt_preflight",
        "init_hooks",
        "action_retry",
        "lane_selection",
        "kind_requirements",
        "aggregate_evidence",
        "story_exit_guards",
    ):
        try:
            ports.require(name)
        except UnavailablePort as error:
            assert error.port == name
        else:
            raise AssertionError(f"{name} reported available")
