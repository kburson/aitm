"""Project closure-owner-verified #103 evidence into a serial comparison.

Archives and their JSON texts are keyed by artifact name, then member.
A verification record binds the role identity, authenticated job IDs,
archive metadata, and SHA-256 of each original JSON receipt. The tested
roles also carry the protected gate result, policy bytes, run creation time
and Python cache observation; the PR verifier binds the signed subject.
The projection checks these joins without authenticating their supplier.
"""

import json
import math
import re
import shlex
from datetime import datetime
from hashlib import sha256

Baseline = bytes

_BASE = "pr_base"
_PR = "pr_candidate"
_PUSH = "trunk_push"
_WORKFLOW = ".github/workflows/ci.yml"
_CONTROLS = ("workflow", "policy", "observer", "gate", "lock", "verifier")
_IDENTITIES = ("observer", "policy", "lock", "configuration")
_CAPABILITY = ("os", "filesystem", "image", "xcode")
_PLATFORM = (*_CAPABILITY, "runner", "python", "uv")
_ATTEMPT = (
    "repository",
    "repository_id",
    "workflow_id",
    "workflow_path",
    "run_id",
    "run_attempt",
    "check_suite_id",
)
_LANES = ("python", "quality", "file-checks")
_JOBS = ("python-base", *_LANES, "collect-evidence", "aitm-ci")
_LABELS = {"cli-help", "service-one-shot"}
_WHEEL_STEP = "Build and smoke-test the exact installed wheel"
_FILE_STEP = "Check tracked Markdown, YAML and JSON"
_CACHE_STEP = "Run astral-sh/setup-uv@68559e99cc807c1eb7e9238fd43a15bba460eec2"
_HELPERS = (
    "tools/ci/python_gate.py",
    "tools/ci/pytest_evidence.py",
    "tools/ci/verify_pr.py",
    "tools/ci/file_checks.py",
)
_TARGETS = {path.replace("tools/ci/", "tools/ci/tests/test_") for path in _HELPERS}
_CLI = "tools/ci/tests/test_cli_evidence.py::test_usage_console_help"
_PRODUCT_ROOT = "src/aitm_usage"
_PRODUCT_TESTS = "packages/aitm-usage/tests/"
_MEMBERS = {
    "base": {"base.json", "base-policy.json"},
    "python": {
        "pytest.json",
        "product-inventory.json",
        "product-coverage.json",
        "helper-coverage.json",
        "children.json",
        "capability.json",
        "wheel.json",
        "timings.json",
        "product-junit.xml",
    },
    "collector": {"candidate.json"},
    "evidence": {"candidate.json", "attestation.sigstore.json"},
}
_ARCHIVES = {
    _BASE: ("base",),
    _PR: ("base", "python", "collector", "evidence"),
    _PUSH: ("python",),
}
_BOUNDARIES = {
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
_UNMEASURED = {"test_only", "unit", "integration", "billed_cost"}


def _require(condition, reason):
    if not condition:
        raise ValueError(reason)


def _encode(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "json: duplicate object key")
        result[key] = value
    return result


def _finite(value):
    value = float(value)
    _require(math.isfinite(value), "json: non-finite number")
    return value


def _decode(value):
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    _require(isinstance(value, str), "json: expected UTF-8 JSON")
    return json.loads(
        value,
        object_pairs_hook=_unique_object,
        parse_float=_finite,
        parse_constant=_finite,
    )


def _envelope(raw, schema):
    _require(isinstance(raw, bytes), "json: expected UTF-8 envelope bytes")
    document = _schema(_decode(raw), schema)
    _require(raw == _encode(document), "json: noncanonical envelope")
    return document


def _map(value, reason, keys=None):
    _require(isinstance(value, dict), reason)
    if keys is not None:
        _require(set(value) == set(keys), reason)
    return value


def _same(left, right):
    return _encode(left) == _encode(right)


def _digest(value, length=64):
    return isinstance(value, str) and re.fullmatch(rf"[0-9a-f]{{{length}}}", value)


def _hash(text):
    return sha256(text.encode("utf-8")).hexdigest()


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _integer(value, minimum=0):
    return type(value) is int and value >= minimum


def _path(value):
    _require(
        isinstance(value, str)
        and "\\" not in value
        and not re.match(r"^[A-Za-z]:", value)
        and all(part not in {"", ".", ".."} for part in value.split("/"))
        and all(ord(character) >= 32 and ord(character) != 127 for character in value),
        "path: unsafe or aliased repository or archive path",
    )
    return value


def _node_source(node):
    _require(isinstance(node, str), "path: malformed node ID")
    source, separator, suffix = node.partition("::")
    _require(separator and suffix, "path: malformed node ID")
    return _path(source)


def _names(value, validate, reason):
    _require(isinstance(value, list) and bool(value), reason)
    for item in value:
        validate(item)
    _require(len(value) == len(set(value)), reason)
    return value


def _schema(document, expected):
    _require(
        isinstance(document, dict) and document.get("schema") == expected,
        f"schema: expected {expected}",
    )
    return document


def _attempt(record, binding):
    _require(
        _integer(record.get("run_attempt"), 1)
        and record["run_attempt"] == binding["run_attempt"]
        and _integer(record.get("run_id"), 1)
        and record["run_id"] == binding["run_id"],
        "attempt: run or attempt disagrees with the owning role",
    )


def _binding(binding, role):
    extra = () if role == _PUSH else ("pr", "base", "head")
    _map(
        binding,
        "binding: malformed role identity",
        (
            *_ATTEMPT,
            "event",
            "ref",
            "commit",
            "tree",
            "parents",
            "controls",
            "identities",
            "platform",
            *extra,
        ),
    )
    _require(
        all(
            _integer(binding[key], 1)
            for key in (
                "repository_id",
                "workflow_id",
                "run_id",
                "run_attempt",
                "check_suite_id",
            )
        )
        and _text(binding["repository"])
        and binding["workflow_path"] == _WORKFLOW
        and all(_digest(binding[key], 40) for key in ("commit", "tree"))
        and isinstance(binding["parents"], list)
        and all(_digest(item, 40) for item in binding["parents"]),
        "binding: invalid repository, workflow or checkout",
    )
    controls = _map(binding["controls"], "binding: incomplete controls", _CONTROLS)
    identities = _map(
        binding["identities"], "binding: incomplete control digests", _IDENTITIES
    )
    platform = _map(binding["platform"], "binding: incomplete platform", _PLATFORM)
    _require(
        all(_digest(value, 40) for value in controls.values())
        and all(_digest(value) for value in identities.values())
        and all(_text(value) for value in platform.values())
        and (platform["runner"], platform["os"], platform["filesystem"])
        == ("macos-26", "Darwin", "apfs")
        and (platform["python"], platform["uv"]) == ("3.13.9", "0.10.6"),
        "binding: invalid controls or historical platform",
    )
    if role == _PUSH:
        _require(
            (binding["event"], binding["ref"]) == ("push", "refs/heads/trunk"),
            "binding: invalid trunk push role",
        )
    else:
        pr = binding["pr"]
        _require(
            _integer(pr, 1)
            and (binding["event"], binding["ref"])
            == ("pull_request", f"refs/pull/{pr}/merge")
            and all(_digest(binding[key], 40) for key in ("base", "head"))
            and (
                binding["parents"] == [binding["base"], binding["head"]]
                if role == _PR
                else binding["commit"] == binding["base"]
            ),
            "binding: invalid PR checkout or ref",
        )
    return binding


def _join_roles(pr, base, push):
    _attempt(base, pr)
    _require(
        all(base[key] == pr[key] for key in (*_ATTEMPT, "pr", "ref", "base", "head"))
        and all(
            pr[key] == push[key]
            for key in (
                "repository",
                "repository_id",
                "workflow_id",
                "workflow_path",
                "tree",
                "parents",
                "controls",
                "identities",
                "platform",
            )
        )
        and push["run_id"] != pr["run_id"]
        and push["check_suite_id"] != pr["check_suite_id"]
        and len({base["commit"], pr["commit"], push["commit"]}) == 3,
        "binding: historical role identities disagree",
    )


def _job_records(role, binding, jobs, verified):
    names = {"python-base"} if role == _BASE else set(_JOBS)
    jobs = _map(jobs, "job: required jobs missing or unexpected", names)
    ids = set()
    for name, job in jobs.items():
        _map(job, "job: invalid job record")
        _attempt(job, binding)
        expected = (
            "skipped"
            if role == _PUSH and name in {"python-base", "aitm-ci"}
            else "success"
        )
        _require(
            job.get("name") == name
            and _integer(job.get("id"), 1)
            and job["id"] not in ids
            and _integer(job.get("check_suite_id"), 1)
            and job["check_suite_id"] == binding["check_suite_id"]
            and (job.get("status"), job.get("conclusion")) == ("completed", expected),
            "job: duplicate, failed or misbound required job",
        )
        ids.add(job["id"])
    _require(
        _same({name: job["id"] for name, job in jobs.items()}, verified),
        "job: IDs disagree with verified custody",
    )
    return jobs


def _archive_records(role, binding, archives, raw, verified):
    attempt = binding["run_attempt"]
    names = {f"aitm-ci-{kind}-a{attempt}": kind for kind in _ARCHIVES[role]}
    archives = _map(archives, "archive: missing or unexpected artifact", names)
    raw = _map(raw, "receipt: missing or unexpected artifact receipts", names)
    records = {}
    ids = set()
    for name, kind in names.items():
        archive = _map(archives[name], "archive: malformed artifact")
        _attempt(archive, binding)
        members = _names(
            archive.get("members"), _path, "archive: duplicate or missing member"
        )
        expected = _MEMBERS[kind] | (
            {"expected-base.json"} if kind == "python" and role == _PR else set()
        )
        _require(
            archive.get("name") == name
            and _integer(archive.get("id"), 1)
            and archive["id"] not in ids
            and _digest(archive.get("sha256"))
            and (
                archive.get("custody") == "authenticated"
                or (
                    archive.get("custody") == "retained"
                    and _text(archive.get("reference"))
                )
            )
            and set(members) == expected,
            "archive: invalid ownership, custody, digest or member list",
        )
        ids.add(archive["id"])
        texts = _map(
            raw[name],
            "receipt: incomplete raw JSON receipts",
            {member for member in expected if member.endswith(".json")},
        )
        records[kind] = {}
        for member, text in texts.items():
            _require(isinstance(text, str), "receipt: expected original UTF-8 text")
            records[kind][member] = (_decode(text), _hash(text))
    _require(
        _same(archives, verified.get("archives")), "archive: verified custody disagrees"
    )
    _require(
        _same(
            {
                name: {member: digest for member, (_, digest) in records[kind].items()}
                for name, kind in names.items()
            },
            verified.get("receipts"),
        ),
        "receipt: original bytes disagree with verified digests",
    )
    return records


def _verify(role, document):
    binding = _binding(document.get("binding"), role)
    verified = _map(document.get("verification"), "verification: missing disposition")
    kind = {_BASE: "pr_base", _PR: "pr_verifier", _PUSH: "push_replay"}[role]
    _require(
        verified.get("status") == "pass"
        and verified.get("kind") == kind
        and _text(verified.get("reference")),
        "verification: missing independent passing disposition",
    )
    trusted_binding = _map(
        verified.get("binding"), "binding: missing verified identity"
    )
    _attempt(trusted_binding, binding)
    _require(_same(binding, trusted_binding), "binding: verified identity disagrees")
    jobs = _job_records(role, binding, document.get("jobs"), verified.get("jobs"))
    records = _archive_records(
        role, binding, document.get("archives"), document.get("raw"), verified
    )
    return binding, jobs, records, verified


def _policy(document):
    _schema(document, "aitm.ci-policy/v1")
    helpers = _names(document.get("helpers"), _path, "policy: invalid helper scope")
    required = _names(
        document.get("required_tests"), _node_source, "policy: invalid required tests"
    )
    optional = _map(document.get("optional_skips"), "policy: invalid optional skips")
    for node, reason in optional.items():
        _node_source(node)
        _require(
            _text(reason) and node not in required, "policy: invalid optional skip"
        )
    _require(
        document.get("package") == "aitm-usage"
        and document.get("product_root") == _PRODUCT_ROOT
        and _integer(document.get("line_floor"))
        and document["line_floor"] == 90
        and set(helpers) == set(_HELPERS)
        and sorted(document.get("required_children", [])) == sorted(_LABELS)
        and sorted(document.get("pr_jobs", [])) == sorted(("python-base", *_LANES))
        and sorted(document.get("push_jobs", [])) == sorted(_LANES),
        "policy: unexpected #103 policy scope",
    )
    return document


def _product_outcomes(evidence, outcomes, policy, *, base=False):
    _schema(evidence, "aitm.pytest-evidence/v1")
    nodes = _names(
        evidence.get("collected"), _node_source, "inventory: invalid test IDs"
    )
    _map(outcomes, "outcome: classifier and collection domains disagree", nodes)
    _require(
        _integer(evidence.get("exit_code"))
        and evidence["exit_code"] == 0
        and evidence.get("deselected") == []
        and isinstance(evidence.get("reports"), list)
        and all(
            _node_source(node).startswith(_PRODUCT_TESTS) or (not base and node == _CLI)
            for node in nodes
        )
        and (base or _CLI in outcomes),
        "inventory: invalid product/CLI observer scope",
    )
    grouped = {node: {} for node in nodes}
    for report in evidence["reports"]:
        _map(report, "outcome: invalid observer report")
        node, when = report.get("nodeid"), report.get("when")
        _require(
            isinstance(node, str)
            and node in grouped
            and when in ("setup", "call", "teardown")
            and when not in grouped[node]
            and report.get("wasxfail") is False
            and report.get("outcome") in ("passed", "skipped"),
            "outcome: missing, duplicate or invalid observer phase",
        )
        grouped[node][when] = report
    for node, phases in grouped.items():
        setup, call, teardown = (
            phases.get(phase, {}) for phase in ("setup", "call", "teardown")
        )
        statuses = (setup.get("outcome"), call.get("outcome"), teardown.get("outcome"))
        if outcomes[node] == "passed":
            _require(
                statuses == ("passed", "passed", "passed"),
                "outcome: classifier disagrees with passed phases",
            )
        else:
            skip = setup if statuses[0] == "skipped" else call
            _require(
                outcomes[node] == "skipped"
                and statuses
                in (("skipped", None, "passed"), ("passed", "skipped", "passed"))
                and node in policy["optional_skips"]
                and skip.get("skip_reason") == policy["optional_skips"][node],
                "outcome: classifier disagrees with permitted skip",
            )
    _require(
        all(outcomes.get(node) == "passed" for node in policy["required_tests"]),
        "outcome: required product test did not pass",
    )
    return sorted(nodes)


def _base_projection(binding, receipts, verified, outcomes):
    base, digest = receipts["base.json"]
    base = _map(base, "receipt: invalid base proof", ("identity", "evidence"))
    expected = {
        "base": binding["commit"],
        "tree": binding["tree"],
        **binding["identities"],
        "runtime": binding["platform"]["python"],
        "image": binding["platform"]["image"],
    }
    _require(
        _same(base["identity"], expected), "binding: trusted base identity disagrees"
    )
    policy, policy_digest = receipts["base-policy.json"]
    _require(
        policy_digest == expected["policy"],
        "digest: trusted base policy bytes disagree",
    )
    nodes = _product_outcomes(base["evidence"], outcomes, _policy(policy), base=True)
    _require(
        base["evidence"].get("children") == [],
        "receipt: base lane must be product-only",
    )
    _require(
        _same(verified.get("result"), {"tests": len(nodes)}),
        "outcome: trusted base count disagrees",
    )
    return {"nodes": nodes, "receipt_sha256": digest}, expected


def _coverage(receipt, paths, *, exact):
    document, digest = receipt
    _map(document, "coverage: malformed report", ("meta", "files", "totals"))
    meta = _map(document["meta"], "coverage: malformed metadata")
    _require(
        type(meta.get("format")) is int
        and meta["format"] == 3
        and type(meta.get("branch_coverage")) is bool,
        "schema: unsupported coverage format",
    )
    files = _map(document["files"], "coverage: missing file summaries")
    for name in files:
        _path(name)
    _require(
        set(paths) <= set(files) and (not exact or set(files) == set(paths)),
        "coverage: denominator disagrees with source inventory",
    )
    keys = ("covered_lines", "num_statements")
    if meta["branch_coverage"]:
        keys += ("covered_branches", "num_branches")
    counts = dict.fromkeys(keys, 0)
    for name in paths:
        summary = _map(
            _map(files[name], "coverage: invalid file").get("summary"),
            "coverage: invalid file summary",
        )
        _require(
            all(_integer(summary.get(key)) for key in keys)
            and summary["covered_lines"] <= summary["num_statements"]
            and (
                len(keys) == 2 or summary["covered_branches"] <= summary["num_branches"]
            ),
            "coverage: malformed raw counts",
        )
        for key in keys:
            counts[key] += summary[key]
    if set(paths) == set(files):
        totals = _map(document["totals"], "coverage: missing receipt totals")
        _require(
            all(
                type(totals.get(key)) is int and totals[key] == value
                for key, value in counts.items()
            ),
            "coverage: inconsistent receipt totals",
        )
    _require(
        counts["num_statements"] > 0
        and counts["covered_lines"] * 100 >= 90 * counts["num_statements"],
        "coverage: raw line coverage below #103 floor",
    )
    return {
        "paths": sorted(paths),
        "receipt_sha256": digest,
        "lines": {key: counts[key] for key in keys[:2]},
        "branches": {key: counts[key] for key in keys[2:]} if len(keys) > 2 else None,
    }


def _children(receipt, observed):
    document, digest = receipt
    _schema(document, "aitm.ci-child-evidence/v1")
    rows = document.get("children")
    _require(
        isinstance(rows, list) and len(rows) == len(_LABELS),
        "child: incomplete normal exits",
    )
    labels, pids, expected = set(), set(), []
    for row in rows:
        _map(
            row,
            "child: malformed normal exit",
            ("label", "pid", "returncode", "covered_lines"),
        )
        label, pid, code = row["label"], row["pid"], row["returncode"]
        _require(
            isinstance(label, str)
            and label in _LABELS - labels
            and _integer(pid, 1)
            and pid not in pids
            and _integer(code)
            and code == 0
            and _integer(row["covered_lines"], 1),
            "child: invalid normal exit proof",
        )
        labels.add(label)
        pids.add(pid)
        expected.append({"label": label, "pid": pid, "returncode": code})
    _require(
        isinstance(observed, list)
        and len(observed) == len(expected)
        and {_encode(row) for row in observed} == {_encode(row) for row in expected},
        "child: observer and coverage exits disagree",
    )
    return {"receipts": rows, "receipt_sha256": digest}


def _step(job, name):
    steps = _map(job.get("steps"), "job: missing authenticated step records")
    step = _map(steps.get(name), "job: missing required authenticated step")
    _require(
        _integer(step.get("number"), 1) and step.get("conclusion") == "success",
        "job: required authenticated step did not pass",
    )
    return {"job_id": job["id"], "step": name, "step_number": step["number"]}


def _tested_projection(binding, jobs, receipts, verified, outcomes, baseline_count):
    py = receipts["python"]
    capability = {key: binding["platform"][key] for key in _CAPABILITY}
    _require(
        _same(py["capability.json"][0], capability), "binding: raw capability disagrees"
    )
    policy_text = verified.get("policy")
    _require(
        isinstance(policy_text, str)
        and _hash(policy_text) == binding["identities"]["policy"],
        "digest: verified policy bytes disagree",
    )
    policy = _policy(_decode(policy_text))
    observer, observer_digest = py["pytest.json"]
    nodes = _product_outcomes(observer, outcomes, policy)
    sources, source_digest = py["product-inventory.json"]
    paths = _names(sources, _path, "inventory: malformed or duplicate product sources")
    _require(
        all(path.startswith(_PRODUCT_ROOT + "/") for path in paths),
        "path: outside product source scope",
    )
    coverage = {
        "product": _coverage(py["product-coverage.json"], paths, exact=True),
        "helpers": _coverage(
            py["helper-coverage.json"], policy["helpers"], exact=False
        ),
    }
    result = {
        "passed": True,
        "failures": [],
        "tests": len(nodes),
        "baseline_tests": baseline_count,
        "coverage": {scope: counts["lines"] for scope, counts in coverage.items()},
    }
    _require(
        _same(result, verified.get("result")),
        "verification: protected gate disposition or counts disagree",
    )
    children = _children(py["children.json"], observer.get("children"))
    wheel, wheel_receipt = py["wheel.json"]
    _map(wheel, "wheel: malformed wheel evidence", ("digest",))
    _require(_digest(wheel["digest"]), "wheel: invalid installed wheel digest")
    return {
        "test_inventory": {"nodes": nodes, "receipt_sha256": observer_digest},
        "source_inventory": {"paths": sorted(paths), "receipt_sha256": source_digest},
        "coverage": coverage,
        "children": children,
        "wheel": {
            **wheel,
            "receipt_sha256": wheel_receipt,
            **_step(jobs["python"], _WHEEL_STEP),
        },
        "file_checks": _step(jobs["file-checks"], _FILE_STEP),
    }


def _signed_candidate(binding, receipts, verified, projected, base_identity):
    candidate, digest = receipts["evidence"]["candidate.json"]
    _schema(candidate, "aitm.ci-candidate/v2")
    _require(
        digest
        == receipts["collector"]["candidate.json"][1]
        == verified.get("subject_digest"),
        "digest: signed and collector subjects or verifier digest disagree",
    )
    attestation = _map(
        receipts["evidence"]["attestation.sigstore.json"][0],
        "schema: missing Sigstore bundle",
    )
    _require(
        attestation.get("mediaType") == "application/vnd.dev.sigstore.bundle.v0.3+json"
        and isinstance(attestation.get("verificationMaterial"), dict)
        and isinstance(attestation.get("dsseEnvelope"), dict),
        "schema: unsupported Sigstore bundle",
    )
    _require(
        _same(candidate.get("attempt"), binding["run_attempt"])
        and _same(candidate.get("run"), binding["run_id"]),
        "attempt: signed subject disagrees",
    )
    expected = {
        "pr": binding["pr"],
        "base": binding["base"],
        "head": binding["head"],
        "tested": binding["commit"],
        "tree": binding["tree"],
        "controls": binding["controls"],
        "platform": receipts["python"]["capability.json"][0],
        "base_identity": base_identity,
        "jobs": dict.fromkeys(("python-base", *_LANES), "success"),
        "checkouts": {
            **dict.fromkeys((*_LANES, "collector"), binding["commit"]),
            "python-base": binding["base"],
        },
    }
    _require(
        all(_same(candidate.get(key), value) for key, value in expected.items())
        and _same(receipts["python"]["expected-base.json"][0], base_identity),
        "binding: signed subject checkout, controls or trusted base disagrees",
    )
    digests = {
        "inventory": projected["test_inventory"]["receipt_sha256"],
        "source_inventory": projected["source_inventory"]["receipt_sha256"],
        "baseline": receipts["base"]["base.json"][1],
        "wheel": projected["wheel"]["digest"],
    }
    _require(
        all(candidate.get(key) == value for key, value in digests.items()),
        "digest: signed subject disagrees with raw inventory, base or wheel",
    )
    _require(
        _same(candidate.get("result"), verified["result"])
        and _same(candidate.get("children"), projected["children"]["receipts"])
        and _same(
            candidate.get("branches"),
            {key: value["branches"] for key, value in projected["coverage"].items()},
        ),
        "verification: signed and replayed result, children or branches disagree",
    )
    return candidate


def _helper_collection(collection, binding):
    collection = _map(collection, "helper: missing advisory collection")
    ids = binding["identities"]
    _require(
        collection.get("kind") == "local_advisory"
        and collection.get("tree") == binding["tree"]
        and collection.get("observer") == ids["observer"]
        and collection.get("lock") == ids["lock"]
        and _same(collection.get("deselected"), 0)
        and _same(collection.get("exit_code"), 0)
        and "outcomes" not in collection,
        "helper: unqualified advisory identity or collection result",
    )
    targets = _names(collection.get("targets"), _path, "helper: invalid target set")
    nodes = _names(
        collection.get("nodes"), _node_source, "helper: duplicate or missing node IDs"
    )
    runner = _map(collection.get("runner"), "helper: missing local runner provenance")
    command = collection.get("command")
    _require(_text(command), "helper: missing collection command")
    try:
        argv = shlex.split(command)
    except ValueError as error:
        raise ValueError("helper: malformed collection command") from error
    _require(
        set(targets) == _TARGETS
        and {_node_source(node) for node in nodes} == _TARGETS
        and nodes == sorted(nodes)
        and sha256(_encode(nodes)).hexdigest() == collection.get("sha256")
        and set(argv[-len(targets) :]) == _TARGETS
        and all(
            arg in argv
            for arg in ("uv", "--locked", "pytest_evidence", "--collect-only")
        )
        and _text(runner.get("os"))
        and _text(runner.get("filesystem"))
        and all(
            runner.get(key) == binding["platform"][key] for key in ("python", "uv")
        ),
        "helper: advisory targets, digest, command or runtime disagree",
    )
    raw = collection.get("raw")
    _require(
        isinstance(raw, str) and _hash(raw) == collection.get("observation_sha256"),
        "helper: original observation digest disagrees",
    )
    observer = _schema(_decode(raw), "aitm.pytest-evidence/v1")
    _require(
        _same(observer.get("exit_code"), 0)
        and all(
            observer.get(key) == [] for key in ("deselected", "reports", "children")
        )
        and sorted(
            _names(
                observer.get("collected"), _node_source, "helper: invalid observer IDs"
            )
        )
        == nodes,
        "helper: observer was not a matching collect-only run",
    )
    return {
        key: collection[key]
        for key in (
            "kind",
            "tree",
            "lock",
            "observer",
            "targets",
            "command",
            "runner",
            "deselected",
            "exit_code",
            "nodes",
            "sha256",
            "observation_sha256",
        )
    }


def _timestamp(value):
    _require(
        isinstance(value, str)
        and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value),
        "timing: expected UTC provider timestamp",
    )
    try:
        return datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("timing: invalid provider timestamp") from error


def _seconds(start, end):
    value = (end - start).total_seconds()
    _require(value >= 0, "timing: provider or lane boundaries are out of order")
    return int(value)


def _timing_values(jobs, verified, lane):
    lane = _map(
        lane, "timing: malformed Python receipt", ("setup", "test", "total", "cache")
    )
    _require(
        all(_integer(lane[key]) for key in ("setup", "test", "total"))
        and lane["setup"] + lane["test"] <= lane["total"]
        and lane["cache"] in ("cold", "warm"),
        "timing: invalid raw Python boundaries",
    )
    start = _timestamp(verified.get("created_at"))
    intervals = {
        name: (_timestamp(job.get("started_at")), _timestamp(job.get("completed_at")))
        for name, job in jobs.items()
        if job["conclusion"] == "success"
    }
    for job_start, _ in intervals.values():
        _seconds(start, job_start)
    python_start, python_end = intervals["python"]
    collector_start, collector_end = intervals["collect-evidence"]
    dependency_end = max(
        end for name, (_, end) in intervals.items() if name in {"python-base", *_LANES}
    )
    duration = _seconds(python_start, python_end)
    _require(lane["total"] <= duration, "timing: Python lane exceeds owning job")
    return {
        "queue": _seconds(start, python_start),
        "setup": lane["setup"],
        "test": lane["test"],
        "lane_wall": lane["total"],
        "python_job": duration,
        "collector_wait": _seconds(dependency_end, collector_start),
        "collector": _seconds(collector_start, collector_end),
        "feedback": _seconds(start, max(end for _, end in intervals.values())),
        "runner_consumption": sum(
            _seconds(*interval) for interval in intervals.values()
        ),
    }


def _unknown(document, role, extra=()):
    _map(
        document,
        "timing: invalid Unknown",
        ("status", "role", "scope", "reason", *extra),
    )
    _require(
        document["status"] == "unknown"
        and document["role"] == role
        and _text(document["scope"])
        and _text(document["reason"]),
        "timing: Unknown must carry its role, scope and reason",
    )


def _timings(role, slots, binding, jobs, verified, receipts, candidate=None):
    slots = _map(slots, "timing: cold or warm slot missing", ("cold", "warm"))
    raw_lane = receipts["python"]["timings.json"][0]
    values = _timing_values(jobs, verified, raw_lane)
    if candidate is not None:
        _require(
            _same(
                candidate.get("timings"),
                {
                    **raw_lane,
                    "hosted_seconds": values["python_job"],
                    "queue": values["queue"],
                },
            ),
            "timing: signed Python timing disagrees",
        )
    for profile, slot in slots.items():
        _map(slot, "timing: invalid observation")
        slot_binding = _map(slot.get("binding"), "binding: missing timing role")
        _attempt(slot_binding, binding)
        _require(
            _same(slot_binding, binding)
            and slot.get("role") == role
            and slot.get("lane") == "python",
            "binding: timing role or lane disagrees",
        )
        if profile != raw_lane["cache"]:
            _unknown(slot, role, ("binding", "lane"))
            continue
        _map(
            slot,
            "timing: invalid observed slot",
            ("status", "role", "binding", "lane", "cache", "metrics"),
        )
        _require(
            slot["status"] == "observed", "timing: measured Python profile missing"
        )
        cache = _map(
            slot["cache"],
            "cache: malformed observation",
            ("profile", "result", "key", "job_id", "reference"),
        )
        _step(jobs["python"], _CACHE_STEP)
        _require(
            _same(cache, verified.get("cache"))
            and cache["profile"] == profile
            and cache["result"] == ("hit" if profile == "warm" else "miss")
            and _same(cache["job_id"], jobs["python"]["id"])
            and _text(cache["key"])
            and _text(cache["reference"]),
            "cache: observed key, result or owning Python job disagrees",
        )
        metrics = _map(
            slot["metrics"],
            "timing: incomplete metrics",
            _BOUNDARIES.keys() | _UNMEASURED,
        )
        for key, seconds in values.items():
            metric = _map(
                metrics[key],
                "timing: malformed measured metric",
                ("seconds", "boundary", "reference"),
            )
            _require(
                _same(metric["seconds"], seconds)
                and metric["boundary"] == _BOUNDARIES[key]
                and _text(metric["reference"]),
                "timing: measurement or provenance disagrees",
            )
        for key in _UNMEASURED:
            _unknown(metrics[key], role)
            _require(
                metrics[key]["scope"] == key, "timing: Unknown metric scope disagrees"
            )
    return slots


def _project(verified_ci103, timings):
    evidence = _envelope(verified_ci103, "aitm.tia-ci103-input/v1")
    clock = _envelope(timings, "aitm.tia-baseline-timings/v1")
    inputs = _map(evidence.get("roles"), "binding: invalid role set")
    _require("helper_collection" in inputs, "helper: missing advisory collection")
    _map(
        inputs,
        "binding: missing or unexpected role",
        (_BASE, _PR, _PUSH, "helper_collection"),
    )
    clock = _map(
        clock.get("observations"), "timing: missing historical roles", (_PR, _PUSH)
    )
    bound = {
        role: _verify(role, _map(inputs[role], "binding: missing role"))
        for role in (_BASE, _PR, _PUSH)
    }
    base_binding, base_jobs, base_receipts, base_verified = bound[_BASE]
    pr_binding, pr_jobs, pr_receipts, _ = bound[_PR]
    push_binding, push_jobs, _, _ = bound[_PUSH]
    _join_roles(pr_binding, base_binding, push_binding)
    archive = f"aitm-ci-base-a{pr_binding['run_attempt']}"
    _require(
        _same(inputs[_BASE]["archives"][archive], inputs[_PR]["archives"][archive])
        and _same(inputs[_BASE]["raw"][archive], inputs[_PR]["raw"][archive]),
        "archive: repeated PR base reference disagrees",
    )
    _require(
        _same(base_jobs["python-base"], pr_jobs["python-base"]),
        "job: repeated PR base job disagrees",
    )
    _require(
        {item["id"] for item in pr_jobs.values()}.isdisjoint(
            item["id"] for item in push_jobs.values()
        )
        and {item["id"] for item in inputs[_PR]["archives"].values()}.isdisjoint(
            item["id"] for item in inputs[_PUSH]["archives"].values()
        ),
        "archive/job: ID reused by distinct attempts",
    )
    base_outcomes = inputs[_BASE].get("outcomes")
    test_inventory, base_identity = _base_projection(
        base_binding, base_receipts["base"], base_verified, base_outcomes
    )
    projected = {_BASE: {"test_inventory": test_inventory}}
    observations = {}
    for role in (_PR, _PUSH):
        binding, jobs, receipts, verified = bound[role]
        outcomes = inputs[role].get("outcomes")
        scope = _tested_projection(
            binding,
            jobs,
            receipts,
            verified,
            outcomes,
            len(base_outcomes) if role == _PR else 0,
        )
        candidate = None
        if role == _PR:
            _require(
                all(
                    node in outcomes
                    and (status != "passed" or outcomes[node] == "passed")
                    for node, status in base_outcomes.items()
                ),
                "outcome: PR candidate removed or degraded a trusted base result",
            )
            candidate = _signed_candidate(
                binding, pr_receipts, verified, scope, base_identity
            )
        projected[role] = scope
        observations[role] = _timings(
            role, clock[role], binding, jobs, verified, receipts, candidate
        )
    _require(
        projected[_PR]["source_inventory"]["paths"]
        == projected[_PUSH]["source_inventory"]["paths"],
        "inventory: shared tested tree has conflicting source scopes",
    )
    for role, projection in projected.items():
        binding, jobs, _, verified = bound[role]
        projection.update(
            binding=binding,
            jobs=jobs,
            archives=inputs[role]["archives"],
            outcomes=inputs[role]["outcomes"],
            verification={
                key: verified[key]
                for key in (
                    "kind",
                    "status",
                    "reference",
                    "result",
                    "receipts",
                    "subject_digest",
                )
                if key in verified
            },
        )
    return {
        "schema": "aitm.tia-baseline/v1",
        "roles": projected,
        "helper_collection": _helper_collection(
            inputs["helper_collection"], pr_binding
        ),
        "timings": observations,
    }


def build_baseline(verified_ci103: bytes, timings: bytes) -> Baseline:
    """Return canonical baseline JSON or raise ValueError with a reason category."""
    try:
        return _encode(_project(verified_ci103, timings))
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ValueError("json: malformed UTF-8 JSON") from error
    except (KeyError, TypeError, OverflowError, RecursionError) as error:
        raise ValueError("input: malformed or incomplete proof") from error
