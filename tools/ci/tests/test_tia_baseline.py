import json
from copy import deepcopy
from hashlib import sha256

import pytest
from tia.baseline import build_baseline

TARGETS = [
    "tools/ci/tests/test_python_gate.py",
    "tools/ci/tests/test_pytest_evidence.py",
    "tools/ci/tests/test_verify_pr.py",
    "tools/ci/tests/test_file_checks.py",
]
HELPERS = ["tools/ci/" + path.removeprefix("tools/ci/tests/test_") for path in TARGETS]
BASE_NODE = "packages/aitm-usage/tests/test_cli.py::test_show[one/two::three]"
CLI_NODE = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
LABELS = ("cli-help", "service-one-shot")
PLATFORM = {"os": "Darwin", "filesystem": "apfs", "image": "image", "xcode": "Xcode"}
POLICY = {
    "schema": "aitm.ci-policy/v1",
    "package": "aitm-usage",
    "product_root": "src/aitm_usage",
    "helpers": HELPERS,
    "required_tests": [BASE_NODE],
    "optional_skips": {},
    "required_children": list(LABELS),
    "line_floor": 90,
    "pr_jobs": ["python-base", "python", "quality", "file-checks"],
    "push_jobs": ["python", "quality", "file-checks"],
}
JOBS = [*POLICY["pr_jobs"], "collect-evidence", "aitm-ci"]
WHEEL_STEP = "Build and smoke-test the exact installed wheel"
FILE_STEP = "Check tracked Markdown, YAML and JSON"
CACHE_STEP = "Run astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2"
BOUNDARIES = {
    "queue": "run created to Python job start",
    "setup": "Python lane start to serial test bucket start",
    "test": "serial product and helper test bucket",
    "lane_wall": "Python lane start through installed wheel smoke",
    "python_job": "Python job start to completion",
    "collector_wait": "last required dependency completed to collector start",
    "collector": "collector start to completion",
    "feedback": "run created to last applicable job completion",
    "runner_consumption": "sum of non-skipped job elapsed time",
}


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(text):
    return sha256(text.encode()).hexdigest()


def receipt(nodes, children):
    return {
        "schema": "aitm.pytest-evidence/v1",
        "exit_code": 0,
        "collected": nodes,
        "deselected": [],
        "reports": [
            {
                "nodeid": node,
                "when": phase,
                "outcome": "passed",
                "wasxfail": False,
                "skip_reason": None,
            }
            for node in nodes
            for phase in ("setup", "call", "teardown")
        ],
        "children": children,
    }


def coverage(paths):
    return {
        "meta": {"format": 3, "branch_coverage": True},
        "files": {
            path: {
                "summary": {
                    "covered_lines": 9,
                    "num_statements": 10,
                    "covered_branches": 1,
                    "num_branches": 2,
                }
            }
            for path in paths
        },
        "totals": {
            "covered_lines": len(paths) * 9,
            "num_statements": len(paths) * 10,
            "covered_branches": len(paths),
            "num_branches": len(paths) * 2,
        },
    }


def make_jobs(binding, start_id, push=False):
    jobs = {}
    intervals = [(1, 5), (2, 12), (1, 5), (1, 6), (13, 15), (16, 18)]
    for i, (name, (start, end)) in enumerate(zip(JOBS, intervals, strict=True)):
        skipped = push and name in {"python-base", "aitm-ci"}
        job = {
            "name": name,
            "id": start_id + i,
            "run_id": binding["run_id"],
            "run_attempt": 1,
            "check_suite_id": binding["check_suite_id"],
            "status": "completed",
            "conclusion": "skipped" if skipped else "success",
            "started_at": None if skipped else f"2026-01-01T00:00:{start:02d}Z",
            "completed_at": None if skipped else f"2026-01-01T00:00:{end:02d}Z",
            "steps": {},
        }
        names = {"python": [CACHE_STEP, WHEEL_STEP], "file-checks": [FILE_STEP]}
        for number, step in enumerate(names.get(name, []), 1):
            job["steps"][step] = {"number": number, "conclusion": "success"}
        jobs[name] = job
    return jobs


def add_archive(role, stem, artifact_id, documents, supplemental=()):
    name = f"aitm-ci-{stem}-a1"
    raw = {member: dump(data) for member, data in documents.items()}
    role["raw"][name] = raw
    role["archives"][name] = {
        "name": name,
        "id": artifact_id,
        "run_id": role["binding"]["run_id"],
        "run_attempt": 1,
        "sha256": digest(name + str(artifact_id)),
        "members": sorted([*raw, *supplemental]),
        "custody": "authenticated",
    }


def bind_verification(role, kind, result=None, **details):
    role["verification"] = {
        "status": "pass",
        "kind": kind,
        "reference": "verified custody reference",
        "binding": deepcopy(role["binding"]),
        "jobs": {name: job["id"] for name, job in role["jobs"].items()},
        "archives": deepcopy(role["archives"]),
        "receipts": {
            name: {member: digest(text) for member, text in raw.items()}
            for name, raw in role["raw"].items()
        },
        "result": result,
        **details,
    }


@pytest.fixture
def proof():
    controls = dict(
        zip(
            ("workflow", "policy", "observer", "gate", "lock", "verifier"),
            "123456",
            strict=True,
        )
    )
    controls = {name: value * 40 for name, value in controls.items()}
    ids = {
        "observer": "a" * 64,
        "policy": digest(dump(POLICY)),
        "lock": "c" * 64,
        "configuration": "d" * 64,
    }
    shared = {
        "repository_id": 2,
        "repository": "org/repo",
        "workflow_id": 3,
        "workflow_path": ".github/workflows/ci.yml",
        "run_attempt": 1,
        "controls": controls,
        "identities": ids,
        "platform": {
            **PLATFORM,
            "runner": "macos-26",
            "python": "3.13.9",
            "uv": "0.10.6",
        },
    }
    base, head, tested, pushed, tree, base_tree = [
        character * 40 for character in "abcdef"
    ]
    identity = {
        "base": base,
        "tree": base_tree,
        **ids,
        "observer": "f" * 64,
        "runtime": "3.13.9",
        "image": "base-image",
    }
    pr_binding = {
        **shared,
        "event": "pull_request",
        "ref": "refs/pull/4/merge",
        "pr": 4,
        "base": base,
        "head": head,
        "commit": tested,
        "tree": tree,
        "parents": [base, head],
        "run_id": 5,
        "check_suite_id": 6,
    }
    base_binding = {
        **pr_binding,
        "commit": base,
        "tree": base_tree,
        "parents": [],
        "identities": {key: identity[key] for key in ids},
        "platform": {**shared["platform"], "image": "base-image"},
    }
    push_binding = {
        **shared,
        "event": "push",
        "ref": "refs/heads/trunk",
        "commit": pushed,
        "tree": tree,
        "parents": [base, head],
        "run_id": 7,
        "check_suite_id": 8,
    }
    roles = {}
    for role, binding, nodes in [
        ("pr_candidate", pr_binding, [BASE_NODE, CLI_NODE]),
        ("pr_base", base_binding, [BASE_NODE]),
        ("trunk_push", push_binding, [BASE_NODE, CLI_NODE]),
    ]:
        roles[role] = {
            "binding": binding,
            "jobs": {},
            "archives": {},
            "raw": {},
            "outcomes": dict.fromkeys(nodes, "passed"),
        }
    pr, trusted, push = (
        roles[key] for key in ("pr_candidate", "pr_base", "trunk_push")
    )
    pr["jobs"] = make_jobs(pr_binding, 20)
    push["jobs"] = make_jobs(push_binding, 30, push=True)
    trusted["jobs"] = {"python-base": deepcopy(pr["jobs"]["python-base"])}
    base_doc = {"identity": identity, "evidence": receipt([BASE_NODE], [])}
    base_name = "aitm-ci-base-a1"
    add_archive(
        trusted, "base", 40, {"base.json": base_doc, "base-policy.json": POLICY}
    )
    for field in ("raw", "archives"):
        pr[field][base_name] = deepcopy(trusted[field][base_name])
    bind_verification(trusted, "pr_base", {"tests": 1})

    children = [
        {"label": label, "pid": pid, "returncode": 0}
        for pid, label in enumerate(LABELS, 1)
    ]
    child_coverage = [{**child, "covered_lines": 8} for child in children]
    source_paths = ["src/aitm_usage/cli.py"]
    raw_lane = {"setup": 1, "test": 3, "total": 5, "cache": "warm"}
    py = {
        "pytest.json": receipt([BASE_NODE, CLI_NODE], children),
        "product-inventory.json": source_paths,
        "product-coverage.json": coverage(source_paths),
        "helper-coverage.json": coverage(HELPERS),
        "children.json": {
            "schema": "aitm.ci-child-evidence/v1",
            "children": child_coverage,
        },
        "capability.json": PLATFORM,
        "wheel.json": {"digest": "9" * 64},
        "timings.json": raw_lane,
    }
    counts = {
        "product": {"covered_lines": 9, "num_statements": 10},
        "helpers": {"covered_lines": 36, "num_statements": 40},
    }
    result = {
        "passed": True,
        "failures": [],
        "tests": 2,
        "baseline_tests": 1,
        "coverage": counts,
    }
    candidate = {
        "schema": "aitm.ci-candidate/v2",
        "run": 5,
        "attempt": 1,
        "pr": 4,
        "head": head,
        "base": base,
        "tested": tested,
        "tree": tree,
        "inventory": digest(dump(py["pytest.json"])),
        "source_inventory": digest(dump(source_paths)),
        "baseline": digest(dump(base_doc)),
        "controls": controls,
        "jobs": dict.fromkeys(POLICY["pr_jobs"], "success"),
        "checkouts": {
            **dict.fromkeys([*POLICY["pr_jobs"], "collector"], tested),
            "python-base": base,
        },
        "result": result,
        "children": child_coverage,
        "timings": {**raw_lane, "hosted_seconds": 10, "queue": 2},
        "wheel": "9" * 64,
        "platform": PLATFORM,
        "base_identity": identity,
        "branches": {
            "product": {"covered_branches": 1, "num_branches": 2},
            "helpers": {"covered_branches": 4, "num_branches": 8},
        },
    }
    add_archive(
        pr, "python", 41, {**py, "expected-base.json": identity}, ["product-junit.xml"]
    )
    add_archive(push, "python", 42, py, ["product-junit.xml"])
    add_archive(pr, "collector", 43, {"candidate.json": candidate})
    add_archive(
        pr,
        "evidence",
        44,
        {
            "candidate.json": candidate,
            "attestation.sigstore.json": {
                "mediaType": "application/vnd.dev.sigstore.bundle.v0.3+json",
                "verificationMaterial": {"certificate": {}},
                "dsseEnvelope": {
                    "payload": "a-payload",
                    "payloadType": "application/vnd.in-toto+json",
                    "signatures": [{"sig": "a-signature"}],
                },
            },
        },
    )

    helper_ids = sorted(f"{target}::test_help" for target in TARGETS)
    helper_raw = dump(receipt(helper_ids, []) | {"reports": []})
    roles["helper_collection"] = {
        "kind": "local_advisory",
        "tree": tree,
        "lock": ids["lock"],
        "observer": ids["observer"],
        "targets": TARGETS,
        "command": "PYTHONPATH=tools/ci uv run --project packages/aitm-usage --locked "
        "python -m pytest -p pytest_evidence --collect-only -q " + " ".join(TARGETS),
        "runner": {
            "os": "Darwin",
            "filesystem": "apfs",
            "python": "3.13.9",
            "uv": "0.10.6",
        },
        "deselected": 0,
        "exit_code": 0,
        "nodes": helper_ids,
        "sha256": digest(dump(helper_ids)),
        "observation_sha256": digest(helper_raw),
        "raw": helper_raw,
    }
    observations = {}
    for key, lane, gate, kind in [
        ("pr_candidate", pr, result, "pr_verifier"),
        ("trunk_push", push, {**result, "baseline_tests": 0}, "push_replay"),
    ]:
        bound = lane["binding"]
        job = lane["jobs"]["python"]
        cache = {
            "profile": "warm",
            "result": "hit",
            "key": "approved-key",
            "job_id": job["id"],
            "reference": "authenticated Python job log",
        }
        details = {
            "created_at": "2026-01-01T00:00:00Z",
            "cache": cache,
            "policy": dump(POLICY),
        }
        if lane is pr:
            details["subject_digest"] = digest(dump(candidate))
        bind_verification(lane, kind, gate, **details)
        unknown = {
            "status": "unknown",
            "role": key,
            "scope": "comparable cold",
            "reason": "no comparable cold sample",
        }
        seconds = dict(
            zip(
                BOUNDARIES,
                [
                    2,
                    1,
                    3,
                    5,
                    10,
                    1,
                    2,
                    18 if lane is pr else 15,
                    27 if lane is pr else 21,
                ],
                strict=True,
            )
        )
        metrics = {
            name: {
                "seconds": seconds[name],
                "boundary": boundary,
                "reference": "historical timing receipt",
            }
            for name, boundary in BOUNDARIES.items()
        }
        for name in ("test_only", "unit", "integration", "billed_cost"):
            metrics[name] = {
                **unknown,
                "scope": name,
                "reason": "boundary not measured",
            }
        observations[key] = {
            "cold": {**unknown, "binding": deepcopy(bound), "lane": "python"},
            "warm": {
                "status": "observed",
                "role": key,
                "binding": deepcopy(bound),
                "lane": "python",
                "cache": deepcopy(cache),
                "metrics": metrics,
            },
        }
    return {"schema": "aitm.tia-ci103-input/v1", "roles": roles}, {
        "schema": "aitm.tia-baseline-timings/v1",
        "observations": observations,
    }


def project(proof):
    return build_baseline(*(dump(envelope).encode() for envelope in proof))


@pytest.mark.parametrize("location", ["base-archive", "python-archive", "timing"])
def test_baseline_rejects_mixed_attempts(proof, location):
    evidence, timings = proof
    if location == "timing":
        timings["observations"]["pr_candidate"]["warm"]["binding"]["run_attempt"] = 2
    elif location == "base-archive":
        evidence["roles"]["pr_base"]["archives"]["aitm-ci-base-a1"]["run_attempt"] = 2
    else:
        evidence["roles"]["pr_candidate"]["archives"]["aitm-ci-python-a1"][
            "run_attempt"
        ] = 2
    with pytest.raises(ValueError, match="attempt"):
        project(proof)


def test_baseline_projects_exact_pair(proof):
    encoded = project(proof)
    assert encoded == project(proof)
    projected = json.loads(encoded)
    assert encoded == dump(projected).encode()
    assert projected["schema"] == "aitm.tia-baseline/v1"
    pr, base, push = (
        projected["roles"][key] for key in ("pr_candidate", "pr_base", "trunk_push")
    )
    assert pr["binding"]["tree"] == push["binding"]["tree"] == "e" * 40
    assert pr["binding"]["commit"] == "c" * 40 and push["binding"]["commit"] == "d" * 40
    assert base["binding"]["tree"] == "f" * 40 and base["outcomes"] == {
        BASE_NODE: "passed"
    }
    assert pr["outcomes"] == {BASE_NODE: "passed", CLI_NODE: "passed"}
    assert pr["source_inventory"]["paths"] == ["src/aitm_usage/cli.py"]
    assert push["jobs"]["python-base"]["conclusion"] == "skipped"
    assert pr["coverage"]["product"]["lines"] == {
        "covered_lines": 9,
        "num_statements": 10,
    }
    assert pr["coverage"]["helpers"]["branches"] == {
        "covered_branches": 4,
        "num_branches": 8,
    }
    assert {receipt["label"] for receipt in pr["children"]["receipts"]} == set(LABELS)
    assert pr["wheel"]["digest"] == "9" * 64
    assert push["file_checks"]["job_id"] == 33
    assert projected["helper_collection"]["kind"] == "local_advisory"
    assert "outcomes" not in projected["helper_collection"]
    assert "outcomes" not in push["coverage"]["helpers"]
    assert (
        projected["timings"]["trunk_push"]["warm"]["metrics"]["runner_consumption"][
            "seconds"
        ]
        == 21
    )


def set_at(document, path, value):
    for part in path[:-1]:
        document = document[part]
    if value is None:
        del document[path[-1]]
    else:
        document[path[-1]] = value


@pytest.mark.parametrize(
    ("path", "replacement", "reason"),
    [
        (("archives", "aitm-ci-python-a1"), None, "archive"),
        (("raw", "aitm-ci-python-a1", "wheel.json"), None, "receipt"),
        (("binding", "repository_id"), 99, "binding"),
        (("binding", "ref"), "refs/pull/42/merge", "binding"),
        (("binding", "commit"), "b" * 40, "binding"),
        (("binding", "base"), "b" * 40, "binding"),
        (("binding", "head"), "a" * 40, "binding"),
        (("binding", "tree"), "b" * 40, "binding"),
        (("binding", "controls", "gate"), "b" * 40, "binding"),
        (("binding", "identities", "lock"), "b" * 64, "binding"),
        (("binding", "platform", "runner"), "macos-latest", "binding"),
        (("jobs", "collect-evidence"), None, "job"),
        (("jobs", "file-checks", "conclusion"), "cancelled", "job"),
        (("jobs", "file-checks", "id"), 21, "job"),
        (("archives", "aitm-ci-python-a1", "sha256"), "f" * 64, "archive"),
        (("archives", "aitm-ci-python-a1", "custody"), "expired", "archive"),
    ],
)
def test_baseline_rejects_incomplete_or_conflicting_proof(
    proof, path, replacement, reason
):
    set_at(proof[0]["roles"]["pr_candidate"], path, replacement)
    with pytest.raises(ValueError, match=reason):
        project(proof)


def replace_raw(role, stem, member, edit):
    name = f"aitm-ci-{stem}-a1"
    document = json.loads(role["raw"][name][member])
    replacement = edit(document)
    text = dump(document if replacement is None else replacement)
    role["raw"][name][member] = text
    role["verification"]["receipts"][name][member] = digest(text)


@pytest.mark.parametrize(
    ("stem", "member", "field"),
    [
        ("python", "pytest.json", "inventory"),
        ("python", "product-inventory.json", "source_inventory"),
        ("base", "base.json", "baseline"),
    ],
)
def test_baseline_rejects_unbound_signed_subject_digests(proof, stem, member, field):
    pr = proof[0]["roles"]["pr_candidate"]
    for archive in ("collector", "evidence"):
        replace_raw(
            pr, archive, "candidate.json", lambda doc: doc.update({field: "1" * 64})
        )
    pr["verification"]["subject_digest"] = pr["verification"]["receipts"][
        "aitm-ci-evidence-a1"
    ]["candidate.json"]
    assert member in pr["raw"][f"aitm-ci-{stem}-a1"]
    with pytest.raises(ValueError, match="digest"):
        project(proof)


@pytest.mark.parametrize(
    "case",
    [
        "nested-duplicate",
        "raw-duplicate",
        "schema",
        "nonfinite",
        "source",
        "member",
        "coverage",
        "node",
    ],
)
def test_baseline_rejects_noncanonical_or_unsafe_input(proof, case):
    envelope, timings = proof
    role = envelope["roles"]["trunk_push"]
    if case in {"nested-duplicate", "nonfinite"}:
        raw = dump(envelope)
        if case == "nested-duplicate":
            raw = raw.replace(
                '"repository_id":2', '"repository_id":2,"repository_id":2', 1
            )
        else:
            raw = raw.replace('"repository_id":2', '"repository_id":1e999', 1)
        with pytest.raises(ValueError, match="json"):
            build_baseline(raw.encode(), dump(timings).encode())
        return
    if case == "raw-duplicate":
        text = '{"digest":"a","digest":"b"}'
        role["raw"]["aitm-ci-python-a1"]["wheel.json"] = text
        role["verification"]["receipts"]["aitm-ci-python-a1"]["wheel.json"] = digest(
            text
        )
    elif case == "schema":
        envelope["schema"] = "unsupported/v9"
    elif case == "source":
        replace_raw(
            role,
            "python",
            "product-inventory.json",
            lambda _: ["/src/aitm_usage/cli.py"],
        )
    elif case == "member":
        role["archives"]["aitm-ci-python-a1"]["members"].append("./wheel.json")
    elif case == "coverage":
        replace_raw(
            role,
            "python",
            "helper-coverage.json",
            lambda d: d["files"].update({"tools\\ci\\file_checks.py": {}}),
        )
    elif case == "node":
        replace_raw(
            role,
            "python",
            "pytest.json",
            lambda d: d["collected"].append("packages/../escape.py::test_wrong"),
        )
    with pytest.raises(
        ValueError,
        match={"raw-duplicate": "json", "schema": "schema"}.get(case, "path"),
    ):
        project(proof)


def test_baseline_rejects_unsupported_raw_receipt_schema(proof):
    role = proof[0]["roles"]["trunk_push"]
    replace_raw(
        role, "python", "children.json", lambda d: d.update(schema="unsupported/v9")
    )
    with pytest.raises(ValueError, match="schema"):
        project(proof)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("missing", None),
        ("tree", "a" * 40),
        ("lock", "a" * 64),
        ("observer", "b" * 64),
        ("targets", TARGETS[1:]),
        ("deselected", 1),
        ("nodes", ["tools/ci/tests/test_python_gate.py::test_help"] * 2),
        ("sha256", "f" * 64),
    ],
)
def test_baseline_rejects_unqualified_helper_collection(proof, field, replacement):
    roles = proof[0]["roles"]
    if field == "missing":
        del roles["helper_collection"]
    else:
        roles["helper_collection"][field] = replacement
    with pytest.raises(ValueError, match="helper"):
        project(proof)


def test_baseline_distinguishes_unknown_and_observed_timing(proof):
    timings = json.loads(project(proof))["timings"]
    cold, warm = (timings["pr_candidate"][profile] for profile in ("cold", "warm"))
    assert (cold["status"], cold["role"], cold["scope"], cold["reason"]) == (
        "unknown",
        "pr_candidate",
        "comparable cold",
        "no comparable cold sample",
    )
    assert warm["cache"]["result"] == "hit" and warm["cache"]["key"] == "approved-key"
    assert warm["metrics"]["test"]["seconds"] == 3
    assert warm["metrics"]["test"]["reference"] == "historical timing receipt"
    assert warm["metrics"]["unit"]["status"] == "unknown"


@pytest.mark.parametrize(
    ("field", "value"),
    [("key", "other-key"), ("profile", "cold"), ("job_id", 20), ("result", "miss")],
)
def test_baseline_rejects_unbound_cache_observation(proof, field, value):
    proof[1]["observations"]["pr_candidate"]["warm"]["cache"][field] = value
    with pytest.raises(ValueError, match="cache"):
        project(proof)


def test_baseline_unknown_timing_cannot_fill_missing_proof(proof):
    del proof[0]["roles"]["trunk_push"]["jobs"]["file-checks"]
    with pytest.raises(ValueError, match="job"):
        project(proof)


def test_baseline_rejects_unbound_timing_boundary(proof):
    warm = proof[1]["observations"]["pr_candidate"]["warm"]
    warm["metrics"]["setup"]["boundary"] = warm["metrics"]["queue"]["boundary"]
    with pytest.raises(ValueError, match="timing"):
        project(proof)


def test_baseline_requires_canonical_envelopes_but_hashes_original_receipts(proof):
    evidence, timings = proof
    with pytest.raises(ValueError, match="json"):
        build_baseline((dump(evidence) + "\n").encode(), dump(timings).encode())
    with pytest.raises(ValueError, match="json"):
        build_baseline(dump(evidence).encode(), json.dumps(timings, indent=2).encode())

    push = evidence["roles"]["trunk_push"]
    raw = push["raw"]["aitm-ci-python-a1"]
    verification = push["verification"]["receipts"]["aitm-ci-python-a1"]
    raw["wheel.json"] += "\n"
    verification["wheel.json"] = digest(raw["wheel.json"])
    wheel = json.loads(project(proof))["roles"]["trunk_push"]["wheel"]
    assert (
        wheel["receipt_sha256"]
        == "fde8ef0610bfc53d363face259c1693ed07c268b333d600a4503b5b530daa979"
    )
