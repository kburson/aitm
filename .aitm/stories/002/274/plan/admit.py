"""Read-only qualification spike. The policy is pinned to reviewed evidence."""

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile


class Refusal(ValueError):
    """An exact receipt admission check refused the requested tuple."""


def require(condition, field):
    if not condition:
        raise Refusal(f"{field} differs from the approved evidence")


def sha(data):
    return sha256(data).hexdigest()


def load_policy(raw, approved_sha256):
    require(sha(raw) == approved_sha256, "reviewer-approved policy hash")
    return json.loads(raw)


def assignment_digest(nodes):
    raw = json.dumps(sorted(nodes), sort_keys=True, separators=(",", ":")).encode()
    return sha(raw)


def authorize(policy, request):
    keys = ("repository", "workflow_id", "workflow_path", "head", "observer_tree", "product_commit",
            "product_tree", "run", "attempt", "assignment_sha256", "mode")
    require(set(request) == set(keys), "request shape")
    for key in keys:
        require(type(request[key]) is type(policy[key]) and request[key] == policy[key], key)
    return {key: policy[key] for key in keys}


def git(root, *args):
    return subprocess.check_output(("git", "-C", str(root), *args))


def check_source(policy, root, *, expected_review):
    for revision, expected_tree in ((policy["head"], policy["observer_tree"]),
                                    (policy["product_commit"], policy["product_tree"])):
        actual = git(root, "rev-parse", f"{revision}^{{tree}}").decode().strip()
        require(actual == expected_tree, "Git tree")
    for name, (revision, path, digest) in policy["inputs"].items():
        require(sha(git(root, "show", f"{revision}:{path}")) == digest, name)
    if not expected_review:
        return
    reviewed = git(root, "show", f"{policy['planning_publication']}:{policy['review_path']}")
    require(sha(reviewed) == policy["review_sha256"], "independent review hash")
    for key in ("head", "run", "artifact_id", "receipt_sha256", "archive_sha256"):
        require(str(policy[key]).encode() in reviewed, f"independent review {key}")


def check_transport(policy, evidence):
    run, job, artifact = (evidence[key] for key in ("run", "job", "artifact"))
    for key, value in (("id", policy["run"]), ("run_attempt", policy["attempt"]),
                       ("head_sha", policy["head"]), ("workflow_id", policy["workflow_id"]),
                       ("path", policy["workflow_path"]), ("status", "completed"),
                       ("conclusion", "success"), ("event", policy["event"]),
                       ("head_branch", policy["ref"].removeprefix("refs/heads/"))):
        require(run[key] == value, f"GitHub run {key}")
    for key in ("repository", "head_repository"):
        require(run[key]["full_name"] == policy["repository"], f"GitHub {key}")
    for key, value in (("id", policy["job_id"]), ("run_id", policy["run"]),
                       ("run_attempt", policy["attempt"]), ("head_sha", policy["head"]),
                       ("name", policy["job_name"]), ("status", "completed"),
                       ("conclusion", "success")):
        require(job[key] == value, f"GitHub job {key}")
    require(job["labels"] == policy["runner_labels"], "GitHub runner labels")
    require(artifact["id"] == policy["artifact_id"] and artifact["name"] == policy["artifact_name"]
            and artifact["expired"] is False, "GitHub artifact identity")
    require(artifact["workflow_run"]["id"] == policy["run"]
            and artifact["workflow_run"]["head_sha"] == policy["head"]
            and artifact["workflow_run"]["repository_id"] == run["repository"]["id"]
            and artifact["workflow_run"]["head_repository_id"] == run["head_repository"]["id"],
            "GitHub artifact workflow")
    require(artifact["digest"] == f"sha256:{policy['archive_sha256']}", "GitHub archive digest")
    require(sha(evidence["archive"]) == policy["archive_sha256"], "downloaded archive digest")
    expected_log = f"Controller receipt SHA-256: {policy['receipt_sha256']}".encode()
    require(sum(expected_log in line for line in evidence["log"].splitlines()) == 1,
            "controller receipt log binding")


def check_report(policy, receipt):
    identity = receipt["identity"]
    for key in ("repository", "run", "attempt", "head", "product_commit", "product_tree", "ref",
                "platform", "image", "product_python", "uv"):
        require(identity[key] == policy[key], f"receipt {key}")
    require(identity["tree"] == policy["observer_tree"], "receipt observer tree")
    for key, (_, _, digest) in policy["inputs"].items():
        if key in identity:
            require(identity[key] == digest, f"receipt {key}")
    boundary = receipt["boundary"]
    require(boundary["filesystem"] == "apfs" and boundary["worker_uid"] not in (0, boundary["controller_uid"]),
            "recorded separate APFS worker")
    for key in ("worker_locked_inputs_write", "worker_marker_read_write", "worker_noninteractive_elevation",
                "worker_private_and_staged_directory_read_write", "worker_staged_receipt_create"):
        require(boundary[key] == "denied", f"recorded boundary {key}")
    require(receipt["status"] == policy["receipt_status"] and receipt["production_qualification"] == "unqualified",
            "receipt disposition")
    full = receipt["full_observation"]
    collection = full["collection"]
    require(all(collection[key] is True for key in ("collection_matches", "discovered_matches", "trace_clean"))
            and collection["collected"] == policy["catalog_size"]
            and collection["driver"]["exit"] == collection["tracer"]["exit"] == 0,
            "complete collection")
    require(full["catalog"]["ids_sha256"] == policy["catalog_sha256"], "catalog digest")
    require(full["toolchain"] == policy["toolchain"], "recorded observer toolchain")
    if policy["mode"] == "full":
        outcome = full["execution"]
        require(outcome["assignment_sha256"] == policy["assignment_sha256"] and outcome["collection_matches"],
                "full assignment")
        require(outcome["tracer"]["exit"] == 0, "full tracer exit")
    else:
        selected = receipt["selected_observation"]
        assignment = selected["assignment"]
        require(assignment["run"] == policy["run"] and assignment["attempt"] == policy["attempt"]
                and assignment["head"] == policy["head"] and assignment["tree"] == policy["observer_tree"]
                and assignment["product_tree"] == policy["product_tree"]
                and assignment["catalog_sha256"] == policy["catalog_sha256"]
                and assignment_digest(assignment["nodes"]) == policy["assignment_sha256"],
                "selected assignment")
        outcome = selected["execution"]
        require(outcome["accepted"] is True and outcome["dispatch_matches"] is True
                and set(outcome["passed"]) == set(assignment["nodes"])
                and not set(outcome["unobserved"]) & set(assignment["nodes"])
                and assignment_digest(outcome["unobserved"] + assignment["nodes"]) == policy["catalog_sha256"],
                "selected assignment and complement")
    native = (full if policy["mode"] == "full" else receipt["selected_observation"])["native_children"]
    required = {
        "tools/ci/tests/test_cli_evidence.py::test_usage_console_help": ("cli.py", 417),
        "packages/aitm-usage/tests/test_service.py::test_one_shot_status_uses_collecting_subprocess_pid":
            ("service.py", 1052),
    }
    require(set(native) == set(required), "required child identities")
    for node, (source, line) in required.items():
        rows = native[node]
        require(len(rows) == 1 and rows[0]["os_exit_status"] == 0
                and rows[0]["os_exit_reason"] == 1
                and rows[0]["test"] == node and rows[0]["required_file"] == source
                and rows[0]["required_line"] == line and line in rows[0]["files"][source],
                f"required child for {node}")
    require(outcome["trace_clean"] is True and outcome["driver"]["exit"] == 0
            and len(outcome["passed"]) == policy["assignment_size"]
            and assignment_digest(outcome["passed"]) == policy["assignment_sha256"]
            and not any(outcome[key] for key in ("failed", "missing_or_inconsistent", "unexpected_execution",
                                                "ordering_errors")), "passing assignment outcomes")
    return outcome


def stream_declarations(value):
    if isinstance(value, dict):
        if {"path", "bytes", "sha256"} <= value.keys() and value["path"].startswith("diagnostics/"):
            yield value
        for item in value.values():
            yield from stream_declarations(item)
    elif isinstance(value, list):
        for item in value:
            yield from stream_declarations(item)


def admit(policy, request, evidence, root, *, expected_review=True):
    exact = authorize(policy, request)
    require(evidence is not None and root is not None, "evidence")
    check_source(policy, root, expected_review=expected_review)
    check_transport(policy, evidence)
    with ZipFile(BytesIO(evidence["archive"])) as bundle:
        raw = bundle.read("receipt.json")
        require(sha(raw) == policy["receipt_sha256"], "receipt digest")
        receipt = json.loads(raw)
        require(receipt["identity"]["runner"] == evidence["job"]["runner_name"], "receipt job binding")
        report = check_report(policy, receipt)
        streams = list(stream_declarations(receipt))
        expected_names = {entry["path"] for entry in streams} | {"receipt.json"}
        require(len(expected_names) == len(streams) + 1
                and sorted(bundle.namelist()) == sorted(expected_names), "archive stream inventory")
        for entry in streams:
            data = bundle.read(entry["path"])
            require(len(data) == entry["bytes"] and sha(data) == entry["sha256"], f"stream {entry['path']}")
    return {
        "decision": ("admit-reviewed-observation-only" if expected_review else
                     "verify-provisional-transport-and-observation"),
        "approved_tuple": exact,
        "artifact_id": policy["artifact_id"],
        "archive_sha256": policy["archive_sha256"],
        "receipt_sha256": policy["receipt_sha256"],
        "verified_streams": len(streams),
        "observed_passing": len(report["passed"]),
        "production_qualification": "unqualified",
    }
