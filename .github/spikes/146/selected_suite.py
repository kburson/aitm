"""Selected product execution and benign hosted controls for the #146 trial."""

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from zipfile import ZipFile

from full_suite import CHILDREN, ROOT, reconcile, observe, native_records, parse_trace


@dataclass(frozen=True)
class Trace:
    assignment: dict
    events: list
    children: dict
    clean: bool
    exit_code: int | None


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def authorize(identity, catalog, requested):
    if not requested or len(requested) != len(set(requested)) or not set(requested) <= set(catalog):
        raise ValueError("selection must be a nonempty exact subset of the catalog")
    if len(catalog) != len(set(catalog)):
        raise ValueError("duplicate inventory IDs")
    return {**identity, "catalog_sha256": digest(sorted(catalog)), "nodes": sorted(requested)}


def evaluate(assignment, catalog, evidence):
    if not isinstance(evidence, Trace):
        return {"accepted": False, "reason": "untrusted-origin"}
    if evidence.assignment != assignment:
        return {"accepted": False, "reason": "assignment-identity-mismatch"}
    nodes = assignment["nodes"]
    events = evidence.events
    result = reconcile([(kind, node) for kind, node in events
                        if kind not in {"dispatch", "dispatch-end"}], catalog, nodes)
    result["discovered_matches"] = Counter(node for kind, node in events if kind == "discovered") == Counter(catalog)
    result["dispatch_matches"] = (
        Counter(node for kind, node in events if kind == "dispatch") == Counter(nodes)
        and [node for kind, node in events if kind == "dispatch-end"] == [str(len(nodes))]
    )
    result["unobserved"] = sorted(set(catalog) - set(nodes))
    result["accepted"] = (
        evidence.clean and evidence.exit_code == 0 and result["collection_matches"]
        and result["discovered_matches"] and result["dispatch_matches"]
        and not any(result[key] for key in ("failed", "missing_or_inconsistent",
                                           "unexpected_execution", "ordering_errors"))
    )
    return result


CONTROL_TEST = """def test_a_observed_failure():
    assert False, "expected control failure"

def test_b_stopped_sibling():
    raise AssertionError("the stopped control sibling unexpectedly ran")
"""

WORKER_REPORT = r"""
import json, sys
nodes = json.loads(sys.argv[1])
print(json.dumps({
    "schema": "aitm.pytest-evidence/v1", "exit_code": 0, "collected": nodes,
    "deselected": [], "children": [],
    "reports": [{"nodeid": node, "when": phase, "outcome": "passed", "wasxfail": False,
                 "skip_reason": None}
                for node in nodes for phase in ("setup", "call", "teardown")],
}))
"""


def check_prior_attempt(receipt, assignment, catalog, command):
    identity = receipt["identity"]
    attempt = identity["attempt"] - 1
    if attempt < 1:
        return {"status": "no-prior-attempt"}
    endpoint = f"repos/{identity['repository']}/actions"
    run = identity["run"]

    def github(path):
        result = command(("gh", "api", f"{endpoint}/{path}"), timeout=30)
        if result.returncode:
            raise ValueError("unable to retrieve prior GitHub Actions evidence")
        return result.stdout

    prior = json.loads(github(f"runs/{run}/attempts/{attempt}"))
    metadata = json.loads(github(f"runs/{run}/artifacts"))["artifacts"]
    name = f"product-146-{run}-a{attempt}"
    matching = [row for row in metadata if row["name"] == name and not row["expired"]]
    if len(matching) != 1 or prior["id"] != run or prior["run_attempt"] != attempt or prior["head_sha"] != identity["head"]:
        raise ValueError("prior attempt provenance differs from intended replay input")
    artifact = matching[0]
    raw_zip = github(f"artifacts/{artifact['id']}/zip")
    if artifact["digest"] != "sha256:" + sha256(raw_zip).hexdigest():
        raise ValueError("prior attempt archive digest mismatch")
    with ZipFile(BytesIO(raw_zip)) as archive:
        raw_receipt = archive.read("receipt.json")
        older = json.loads(raw_receipt)
        selected = older["selected_observation"]
        execution = selected["execution"]
        trace = execution["tracer"]["stdout"]
        raw_trace = archive.read(trace["path"])
    if (older["identity"]["attempt"] != attempt or selected["status"] != "selected-observation-pass"
            or sha256(raw_trace).hexdigest() != trace["sha256"]
            or len(raw_trace) != trace["bytes"]):
        raise ValueError("prior attempt lacks complete selected evidence")
    expected_stale = {**assignment, "attempt": attempt}
    if selected["assignment"] != expected_stale:
        raise ValueError("prior assignment differs beyond attempt identity")
    product = Path(f"<trial>/source/{ROOT}/src/aitm_usage")
    events, children = parse_trace(raw_trace, execution["ready_pid"], product)
    stale = Trace(selected["assignment"], events, children, execution["trace_clean"], execution["driver"]["exit"])
    if not evaluate(expected_stale, catalog, stale)["accepted"]:
        raise ValueError("prior attempt trace is not independently complete")
    result = evaluate(assignment, catalog, stale)
    if result.get("reason") != "assignment-identity-mismatch":
        raise ValueError("prior GitHub attempt crossed evidence intake")
    return {**result, "status": "rejected-prior-attempt", "run": run, "prior_attempt": attempt,
            "expected_attempt": identity["attempt"], "artifact_id": artifact["id"],
            "archive_sha256": artifact["digest"], "receipt_sha256": sha256(raw_receipt).hexdigest(),
            "trace_sha256": trace["sha256"]}


def run(src, venv, fixtures, private, logs, receipt, uid, worker, worker_args, command, require,
        args, targets, catalog, collection):
    project = src / ROOT
    product = project / "src/aitm_usage"
    identity = {key: receipt["identity"][key] for key in ("run", "attempt", "head", "tree", "product_tree")}
    result = receipt["selected_observation"] = {"status": "incomplete"}
    require(collection["collection_matches"] and collection["discovered_matches"],
            "selected assignment requires complete collection")
    chosen = [*CHILDREN, *(node for node in catalog
                           if "::test_quota_authority_is_exact_stream_and_provider[" in node)]
    require(len(chosen) == 4, "selected catalog did not include both parameter rows")
    assignment = authorize({**identity, "invocation": "product-selected"}, catalog, chosen)
    result["assignment"] = assignment

    def traced(label, path_targets, context, bind=None, options=(), timeout=100, expected=catalog):
        events, children = observe(label, (*args, "--basetemp", str(fixtures / label),
                                          *options, *path_targets),
                                   worker_args, uid, project, product, private, logs, command, context,
                                   timeout=timeout, assignment=None if bind is None else bind["nodes"],
                                   expected_inventory=digest(sorted(expected)))
        return Trace(bind or {}, events, children, context["trace_clean"], context["driver"]["exit"])

    execution = result["execution"] = {}
    observation = traced("observed-selected", targets, execution, assignment)
    execution.update(evaluate(assignment, catalog, observation))
    result["native_children"] = children = native_records(observation.children, venv)
    require(execution["accepted"] and all(len(rows) == 1 and rows[0]["os_exit_status"] == 0
                                          and rows[0]["os_exit_reason"] == 1
                                          for rows in children.values()), "selected evidence is incomplete")

    controls = result["controls"] = {}
    missing = controls["missing-inventory"] = {}
    omitted = traced("negative-missing-inventory", targets, missing, assignment, options=(
        "--ignore", str(project / "tests/test_accounting.py"),
    ))
    missing.update(reconcile([(kind, data) for kind, data in omitted.events if kind != "dispatch-refused"], catalog, []))
    missing["rejection"] = [data for kind, data in omitted.events if kind == "dispatch-refused"]
    missing["dispatch_refused"] = (
        omitted.clean and omitted.exit_code == 4 and missing["rejection"] == ["inventory-mismatch"]
        and not missing["collection_matches"]
        and not missing["unexpected_execution"] and not any(kind == "dispatch" for kind, _ in omitted.events)
    )
    require(missing["dispatch_refused"], "missing inventory control did not refuse before dispatch")

    untrusted = controls["worker-result"] = {}
    proc = logs.run("negative-worker-report", untrusted, worker, str(venv / "bin/python"), "-I", "-c",
                    WORKER_REPORT, json.dumps(assignment["nodes"]))
    require(proc.returncode == 0, "worker could not emit benign control report")
    report = json.loads(proc.stdout)
    untrusted.update(evaluate(assignment, catalog, report))
    require(untrusted.get("reason") == "untrusted-origin", "worker report crossed evidence intake")

    control_file = src / "trial-harness/test_failure_control.py"
    control_nodes = [f"trial-harness/{control_file.name}::{name}"
                     for name in ("test_a_observed_failure", "test_b_stopped_sibling")]
    failure = controls["failed-and-missing"] = {}
    control_collect = traced("negative-failure-collection", (str(control_file),),
                             failure.setdefault("collection", {}), options=("--collect-only",))
    require(control_collect.clean and control_collect.exit_code == 0
            and reconcile(control_collect.events, control_nodes, [])["collection_matches"],
            "negative control collection was incomplete")
    control_assignment = authorize({**identity, "invocation": "failure-control"}, control_nodes, control_nodes)
    stopped = traced("negative-failed-and-missing", (str(control_file),), failure.setdefault("execution", {}),
                     control_assignment, ("--maxfail=1",), expected=control_nodes)
    failure.update(evaluate(control_assignment, control_nodes, stopped))
    require(stopped.clean and stopped.exit_code == 1 and failure["dispatch_matches"]
            and failure["failed"] == control_nodes[:1] and failure["missing_or_inconsistent"] == control_nodes[1:]
            and not failure["accepted"], "failed-and-missing live control did not fail closed")

    replay = controls["different-invocation-replay"] = evaluate(
        {**assignment, "invocation": "replacement-selected"}, catalog, observation,
    )
    require(replay.get("reason") == "assignment-identity-mismatch", "stale invocation crossed evidence intake")
    controls["actual-prior-attempt-replay"] = check_prior_attempt(receipt, assignment, catalog, command)
    result["status"] = "selected-observation-pass"
    return result["status"]
