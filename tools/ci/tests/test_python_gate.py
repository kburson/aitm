import copy
import json

import pytest
from python_gate import check_jobs, evaluate, main


def evidence(*ids):
    return {
        "schema": "aitm.pytest-evidence/v1",
        "exit_code": 0,
        "collected": list(ids),
        "deselected": [],
        "reports": [
            {"nodeid": node, "when": phase, "outcome": "passed", "wasxfail": False}
            for node in ids
            for phase in ("setup", "call", "teardown")
        ],
        "children": [],
    }


def coverage(files, covered=9, total=10):
    return {
        "files": {
            name: {"summary": {"covered_lines": covered, "num_statements": total}}
            for name in files
        }
    }


@pytest.fixture
def inputs():
    identity = {
        "base": "a" * 40,
        "tree": "b" * 40,
        "observer": "c" * 64,
        "policy": "d" * 64,
        "lock": "e" * 64,
        "configuration": "f" * 64,
        "runtime": "3.13.9",
        "image": "macos-26-arm64",
    }
    policy = {
        "schema": "aitm.ci-policy/v1",
        "line_floor": 90,
        "package": "aitm-usage",
        "product_root": "src/aitm_usage",
        "helpers": ["tools/ci/python_gate.py", "tools/ci/pytest_evidence.py"],
        "required_tests": ["tests/test_core.py::test_keeps_state"],
        "optional_skips": {"tests/test_core.py::test_alias": "unavailable alias"},
        "required_children": ["cli-help", "service-one-shot"],
        "pr_jobs": ["python-base", "python", "quality"],
        "push_jobs": ["python", "quality"],
    }
    values = {
        "policy": policy,
        "candidate": evidence(
            "tests/test_core.py::test_keeps_state", "tests/test_core.py::test_alias"
        ),
        "product": coverage(["src/aitm_usage/state.py"]),
        "product_inventory": ["src/aitm_usage/state.py"],
        "helpers": coverage(policy["helpers"]),
        "child": {
            "schema": "aitm.ci-child-evidence/v1",
            "children": [
                {"label": "cli-help", "pid": 10, "returncode": 0, "covered_lines": 1},
                {
                    "label": "service-one-shot",
                    "pid": 11,
                    "returncode": 0,
                    "covered_lines": 10,
                },
            ],
        },
        "capability": {"os": "Darwin", "filesystem": "apfs"},
        "base": {
            "identity": identity,
            "evidence": evidence("tests/test_core.py::test_keeps_state"),
        },
        "expected_base": identity.copy(),
        "base_policy": copy.deepcopy(policy),
    }

    values["candidate"]["children"] = [
        {"label": "cli-help", "pid": 10, "returncode": 0},
        {"label": "service-one-shot", "pid": 11, "returncode": 0},
    ]
    return values


def test_exact_floor_accepts_behavior_and_counts(inputs):
    result = evaluate(**inputs)
    assert result["passed"]
    assert result["coverage"] == {
        "product": {"covered_lines": 9, "num_statements": 10},
        "helpers": {"covered_lines": 18, "num_statements": 20},
    }


@pytest.mark.parametrize(
    ("change", "reason"),
    [
        (lambda x: x.update(policy=None), "policy"),
        (lambda x: x["policy"].update(line_floor=89), "policy"),
        (lambda x: x["policy"].update(package="unknown"), "package"),
        (lambda x: x["policy"].update(helpers=["tools/ci/absent.py"]), "helper"),
        (
            lambda x: x.update(product=coverage(["src/aitm_usage/state.py"], 179, 200)),
            "product",
        ),
        (
            lambda x: x.update(helpers=coverage(x["policy"]["helpers"], 179, 200)),
            "helpers",
        ),
        (lambda x: x.update(product=coverage(["unrelated.py"])), "product"),
        (lambda x: x["candidate"].update(exit_code=1), "pytest"),
        (lambda x: x["candidate"].update(collected=[]), "inventory"),
        (
            lambda x: x["candidate"]["collected"].append(
                x["candidate"]["collected"][0]
            ),
            "inventory",
        ),
        (lambda x: x["candidate"]["reports"][0].update(outcome="failed"), "setup"),
        (lambda x: x["candidate"]["reports"][1].update(outcome="failed"), "call"),
        (lambda x: x["candidate"]["reports"][2].update(outcome="failed"), "teardown"),
        (lambda x: x["candidate"]["reports"][1].update(wasxfail=True), "xfail"),
        (lambda x: x["candidate"]["reports"].pop(1), "call"),
        (
            lambda x: x["candidate"]["reports"].append(
                copy.copy(x["candidate"]["reports"][1])
            ),
            "duplicate",
        ),
        (
            lambda x: x["candidate"]["reports"][1].update(
                outcome="skipped", skip_reason="no"
            ),
            "skip",
        ),
        (lambda x: x["candidate"]["deselected"].append("old-test"), "deselected"),
        (lambda x: x["base"]["evidence"]["collected"].append("removed-test"), "base"),
        (lambda x: x["base"]["identity"].pop("observer"), "base"),
        (lambda x: x["base"]["identity"].update(observer="0" * 64), "base"),
        (lambda x: x["expected_base"].update(tree="0" * 40), "base"),
        (lambda x: x["child"]["children"].pop(), "child"),
        (lambda x: x["child"]["children"][0].update(covered_lines=0), "child"),
        (lambda x: x["child"]["children"][0].update(returncode=-9), "child"),
        (lambda x: x["child"]["children"][0].update(pid=11), "child"),
        (lambda x: x["capability"].update(os="Linux"), "Darwin"),
        (lambda x: x["capability"].update(filesystem="hfs"), "Darwin"),
    ],
)
def test_green_unrelated_evidence_cannot_mask_refusal(inputs, change, reason):
    change(inputs)
    result = evaluate(**inputs)
    assert not result["passed"]
    assert any(reason in failure for failure in result["failures"])


def test_only_exact_documented_optional_capability_skip_is_allowed(inputs):
    inputs["candidate"]["reports"][4].update(
        outcome="skipped", skip_reason="unavailable alias"
    )
    assert evaluate(**inputs)["passed"]
    inputs["base"]["evidence"] = evidence(*inputs["candidate"]["collected"])
    assert not evaluate(**inputs)["passed"]


@pytest.mark.parametrize("result", ["failure", "skipped", "cancelled", "neutral", None])
def test_required_jobs_do_not_inherit_a_pass(inputs, result):
    needs = {"python": {"result": "success"}, "quality": {"result": "success"}}
    if result is not None:
        needs["python-base"] = {"result": result}
    assert not check_jobs(inputs["policy"], needs, "pr")["passed"]
    assert check_jobs(inputs["policy"], needs, "push")["passed"]


def test_real_needs_predicate_and_cli_reject_malformed_policy(tmp_path, inputs, capsys):
    policy = tmp_path / "policy.json"
    needs = tmp_path / "needs.json"
    policy.write_text(json.dumps(inputs["policy"]))
    needs.write_text(
        json.dumps(
            {name: {"result": "success"} for name in inputs["policy"]["pr_jobs"]}
        )
    )
    args = ["--policy", str(policy), "--needs", str(needs), "--mode", "pr"]
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["passed"]
    policy.write_text("{")
    assert main(args) == 1
    assert "policy" in capsys.readouterr().out


def test_child_shards_use_exact_process_and_product_lines(tmp_path):
    from coverage import CoverageData
    from python_gate import collect_child_coverage

    payload = evidence("test_cli")
    payload["children"] = [
        {"label": "cli-help", "pid": 10, "returncode": 0},
        {"label": "service-one-shot", "pid": 11, "returncode": 0},
    ]
    prefix = tmp_path / ".coverage"
    for pid, files in (
        (10, {"src/aitm_usage/cli.py": [1, 2]}),
        (110, {"src/aitm_usage/service.py": [1, 2, 3]}),
        (11, {"tests/fixture.py": [1, 2, 3]}),
    ):
        data = CoverageData(basename=f"{prefix}.runner.host.pid{pid}.Xsuffix.1")
        data.add_lines(files)
        data.write()
    result = collect_child_coverage(payload, prefix)
    assert [(x["label"], x["covered_lines"]) for x in result["children"]] == [
        ("cli-help", 2),
        ("service-one-shot", 0),
    ]


def test_cli_checks_identity_and_supplies_exit_code(tmp_path, inputs, capsys):
    names = {
        "policy": "policy",
        "inventory": "candidate",
        "outcomes": "candidate",
        "coverage": "product",
        "product-inventory": "product_inventory",
        "helpers": "helpers",
        "child-evidence": "child",
        "capability": "capability",
        "base-evidence": "base",
        "base-policy": "base_policy",
        "expected-base": "expected_base",
    }
    from hashlib import sha256

    policy_digest = sha256(json.dumps(inputs["base_policy"]).encode()).hexdigest()
    inputs["base"]["identity"]["policy"] = policy_digest
    inputs["expected_base"]["policy"] = policy_digest
    args = ["--mode", "pr"]
    for flag, key in names.items():
        path = tmp_path / flag
        path.write_text(json.dumps(inputs[key]))
        args.extend([f"--{flag}", str(path)])
    assert main(args) == 0
    assert (
        json.loads(capsys.readouterr().out)["coverage"]["product"]["covered_lines"] == 9
    )
    (tmp_path / "inventory").write_text('{"collected":[]}')
    assert main(args) == 1
    assert "disagree" in capsys.readouterr().out


def test_an_omitted_product_module_cannot_raise_coverage(inputs):
    inputs["product_inventory"].append("src/aitm_usage/unimported.py")
    result = evaluate(**inputs)
    assert not result["passed"]
    assert "inventory" in result["failures"][-1]


def test_baseline_cannot_borrow_candidates_skip_allowance(inputs):
    node = "tests/test_core.py::test_alias"
    base = evidence(*inputs["candidate"]["collected"])
    base["reports"][4].update(outcome="skipped", skip_reason="unavailable alias")
    inputs["base"]["evidence"] = base
    inputs["base_policy"]["optional_skips"].pop(node)
    result = evaluate(**inputs)
    assert not result["passed"]
    assert any(
        "base:" in failure and "skip" in failure for failure in result["failures"]
    )


@pytest.mark.parametrize(
    "mismatch", [None, {"pid": 14}, {"returncode": 1}, {"label": "wrong"}]
)
def test_separate_child_coverage_cannot_replace_observer_receipts(inputs, mismatch):
    if mismatch is None:
        inputs["candidate"]["children"] = []
    else:
        inputs["candidate"]["children"][0].update(mismatch)
    result = evaluate(**inputs)
    assert not result["passed"]
    assert any("observer child" in failure for failure in result["failures"])


def test_needs_cli_refuses_duplicate_job_keys(tmp_path, inputs, capsys):
    policy = tmp_path / "policy.json"
    needs = tmp_path / "needs.json"
    policy.write_text(json.dumps(inputs["policy"]))
    needs.write_text('{"python":{"result":"failure"},"python":{"result":"success"}}')
    assert main(["--policy", str(policy), "--needs", str(needs), "--mode", "push"]) == 1
    assert "duplicate JSON" in capsys.readouterr().out
    assert not check_jobs(inputs["policy"], {}, "unknown")["passed"]


def test_missing_or_malformed_documents_have_blocked_dispositions(inputs):
    inputs.update(
        candidate={}, product={"files": {"src/aitm_usage/state.py": {}}}, child={}
    )
    result = evaluate(**inputs)
    assert not result["passed"]
    assert "invalid pytest evidence" in result["failures"]
    assert "product: malformed line counts" in result["failures"]
    assert "invalid child coverage evidence" in result["failures"]
