import pytest

from tools.ci import category_sweep as sweep
from tools.ci import hosted_category_sweep as hosted

COMMON = "packages/aitm-usage/tests/test_case.py::test_common"
MAC_ONLY = "packages/aitm-usage/tests/test_case.py::test_errno[45]"
LINUX_ONLY = "packages/aitm-usage/tests/test_case.py::test_errno[95]"
NATIVE = "packages/aitm-usage/native-tests/test_case.py::test_host"


def test_hosted_assignment_covers_exact_union_and_runs_native_on_darwin():
    linux = {
        COMMON: "fast-unit",
        NATIVE: "systems-integration",
        LINUX_ONLY: "local-integration",
    }
    darwin = {
        COMMON: "fast-unit",
        NATIVE: "systems-integration",
        MAC_ONLY: "local-integration",
    }
    assert hosted.allocate(linux, darwin) == {
        ("linux", "fast-unit"): {"product": [COMMON]},
        ("linux", "local-integration"): {"product": [LINUX_ONLY]},
        ("darwin", "local-integration"): {"product": [MAC_ONLY]},
        ("darwin", "systems-integration"): {"native": [NATIVE]},
    }


def test_hosted_reconciliation_refuses_missing_or_unexpected_artifacts(tmp_path):
    assignments = {("linux", "fast-unit"): {"product": [COMMON]}}
    (tmp_path / "darwin-fast-unit").mkdir()
    with pytest.raises(sweep.Refusal, match="missing or unexpected"):
        hosted.aggregate(
            assignments,
            {"commit": "source", "tree": "tree"},
            {"attempt": "2"},
            tmp_path,
        )


def test_attempt_is_included_in_worker_plan_binding():
    source = {"commit": "source", "tree": "tree"}
    args = (source, ("linux", "fast-unit"), {"product": [COMMON]})
    one = hosted.slot_plan(*args, {"run_id": "123", "attempt": "1"})
    two = hosted.slot_plan(*args, {"run_id": "123", "attempt": "2"})
    assert sweep.digest(sweep.encoded(one)) != sweep.digest(sweep.encoded(two))
    assert hosted.artifact_name(args[1], one["run"]) != hosted.artifact_name(
        args[1], two["run"]
    )
