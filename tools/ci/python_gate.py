"""Fail closed on incomplete Python validation evidence."""

import argparse
import json
import re
from hashlib import sha256
from pathlib import Path

PHASES = ("setup", "call", "teardown")
IDENTITY_DIGESTS = {
    "base": 40,
    "tree": 40,
    "observer": 64,
    "policy": 64,
    "lock": 64,
    "configuration": 64,
}


def _unique_names(values):
    return (
        isinstance(values, list)
        and bool(values)
        and all(isinstance(item, str) and item for item in values)
        and len(values) == len(set(values))
    )


def _policy_error(policy):
    if not isinstance(policy, dict) or policy.get("schema") != "aitm.ci-policy/v1":
        return "missing or malformed policy"
    if policy.get("package") != "aitm-usage":
        return "unknown required package"
    if policy.get("line_floor") != 90 or policy.get("product_root") != "src/aitm_usage":
        return "invalid coverage policy"
    for key in (
        "helpers",
        "required_tests",
        "required_children",
        "pr_jobs",
        "push_jobs",
    ):
        if not _unique_names(policy.get(key)):
            return f"invalid policy {key}"
    optional = policy.get("optional_skips")
    if not isinstance(optional, dict) or any(
        not isinstance(reason, str) or not reason or node in policy["required_tests"]
        for node, reason in optional.items()
    ):
        return "invalid policy optional skips"
    return None


def _disposition(failures, **data):
    return {"passed": not failures, "failures": failures, **data}


def check_jobs(policy, needs, mode):
    """The same predicate receives actual workflow dependency results."""
    if problem := _policy_error(policy):
        return _disposition([problem])
    if mode not in {"pr", "push"} or not isinstance(needs, dict):
        return _disposition(["invalid workflow job evidence"])
    results = {}
    for job in policy[f"{mode}_jobs"]:
        entry = needs.get(job)
        results[job] = (
            entry.get("result", "missing") if isinstance(entry, dict) else "missing"
        )
    failures = [
        f"required job {job}: {result}"
        for job, result in results.items()
        if result != "success"
    ]
    return _disposition(failures, jobs=results)


def _outcomes(document, optional_skips):
    if (
        not isinstance(document, dict)
        or document.get("schema") != "aitm.pytest-evidence/v1"
    ):
        return {}, ["invalid pytest evidence"]
    if not _unique_names(document.get("collected")):
        return {}, ["empty, malformed or duplicate test inventory"]
    failures = []
    if type(document.get("exit_code")) is not int or document["exit_code"] != 0:
        failures.append("nonzero or missing pytest exit")
    if document.get("deselected") != []:
        failures.append("unexpected deselected tests")
    reports = document.get("reports")
    if not isinstance(reports, list):
        return {}, [*failures, "missing pytest reports"]
    grouped = {node: {} for node in document["collected"]}
    for report in reports:
        if not isinstance(report, dict):
            failures.append("invalid pytest phase report")
            continue
        node, phase = report.get("nodeid"), report.get("when")
        if not isinstance(node, str) or node not in grouped or phase not in PHASES:
            failures.append("unknown node or phase in pytest reports")
            continue
        if phase in grouped[node]:
            failures.append(f"duplicate {phase} report for {node}")
            continue
        grouped[node][phase] = report

    outcomes = {}
    for node, phases in grouped.items():
        for phase, report in phases.items():
            if report.get("wasxfail") is not False:
                failures.append(f"unexpected xfail at {phase} for {node}")
            if report.get("outcome") not in {"passed", "skipped"}:
                failures.append(f"failed or invalid {phase} for {node}")
        setup = phases.get("setup", {})
        call = phases.get("call", {})
        teardown = phases.get("teardown", {})
        if teardown.get("outcome") != "passed":
            failures.append(f"teardown did not pass for {node}")
        if setup.get("outcome") == "passed" and call.get("outcome") == "passed":
            outcomes[node] = "passed"
        elif (
            (setup.get("outcome") == "skipped" and "call" not in phases)
            or (setup.get("outcome") == "passed" and call.get("outcome") == "skipped")
        ) and node in optional_skips:
            skipped = setup if setup.get("outcome") == "skipped" else call
            if skipped.get("skip_reason") == optional_skips[node]:
                outcomes[node] = "skipped"
            else:
                failures.append(f"unexpected skip reason for {node}")
        else:
            failures.append(f"missing or unexpected setup/call/skip for {node}")
    return outcomes, failures


def _line_totals(document, *, root=None, names):
    files = document.get("files") if isinstance(document, dict) else None
    if not isinstance(files, dict) or not files:
        raise ValueError("missing line coverage")
    if root is not None:
        if (
            not _unique_names(names)
            or any(not name.startswith(root + "/") for name in names)
            or set(files) != set(names)
        ):
            raise ValueError(
                "product coverage does not match the tracked source inventory"
            )
    elif any(name not in files for name in names):
        raise ValueError("missing helper in coverage denominator")

    covered = total = 0
    for name in names:
        try:
            summary = files[name]["summary"]
            file_covered = summary["covered_lines"]
            file_total = summary["num_statements"]
        except (KeyError, TypeError) as exc:
            raise ValueError("malformed line counts") from exc
        if (
            type(file_covered) is not int
            or type(file_total) is not int
            or not 0 <= file_covered <= file_total
        ):
            raise ValueError("invalid raw line counts")
        covered += file_covered
        total += file_total
    if not total:
        raise ValueError("empty line denominator")
    return {"covered_lines": covered, "num_statements": total}


def _trusted_identity(actual, expected):
    if not isinstance(actual, dict) or actual != expected:
        return False
    for key, length in IDENTITY_DIGESTS.items():
        value = actual.get(key)
        if (
            not isinstance(value, str)
            or re.fullmatch(f"[0-9a-f]{{{length}}}", value) is None
        ):
            return False
    return all(
        isinstance(actual.get(key), str) and actual[key] for key in ("runtime", "image")
    )


def _child_errors(document, observed, required):
    if (
        not isinstance(document, dict)
        or document.get("schema") != "aitm.ci-child-evidence/v1"
    ):
        return ["invalid child coverage evidence"]
    children = document.get("children")
    if not isinstance(children, list):
        return ["missing child coverage evidence"]
    labels, pids = set(), set()
    errors = []
    receipts = []
    for row in children:
        if not isinstance(row, dict):
            errors.append("invalid child receipt")
            continue
        label, pid = row.get("label"), row.get("pid")
        count = row.get("covered_lines")
        if (
            label not in required
            or label in labels
            or type(pid) is not int
            or pid <= 0
            or pid in pids
            or type(row.get("returncode")) is not int
            or row["returncode"] != 0
            or type(count) is not int
            or count <= 0
        ):
            errors.append("invalid or duplicate normal child coverage receipt")
            continue
        labels.add(label)
        pids.add(pid)
        receipts.append({"label": label, "pid": pid, "returncode": row["returncode"]})
    if (
        not isinstance(observed, list)
        or len(observed) != len(receipts)
        or any(receipt not in observed for receipt in receipts)
    ):
        errors.append("observer child receipts do not match raw coverage evidence")
    if labels != set(required):
        errors.append("missing required normal child coverage")
    return errors


def collect_child_coverage(evidence, prefix):
    """Read product line receipts from raw coverage.py files before combining."""
    from coverage import CoverageData

    directory = Path(prefix).parent
    name = Path(prefix).name
    result = []
    for child in evidence["children"]:
        executed = {}
        pid = child["pid"]
        for shard in directory.glob(f"{name}.*.pid{pid}.*"):
            data = CoverageData(basename=str(shard))
            data.read()
            for filename in data.measured_files():
                if filename.startswith("src/aitm_usage/"):
                    executed.setdefault(filename, set()).update(
                        data.lines(filename) or ()
                    )
        result.append({**child, "covered_lines": sum(map(len, executed.values()))})
    return {"schema": "aitm.ci-child-evidence/v1", "children": result}


def evaluate(
    policy,
    candidate,
    product,
    product_inventory,
    helpers,
    child,
    capability,
    base=None,
    expected_base=None,
    base_policy=None,
    mode="pr",
):
    if problem := _policy_error(policy):
        return _disposition([problem])
    if mode not in {"pr", "push"}:
        return _disposition(["unknown validation mode"])

    failures = []
    if not isinstance(capability, dict) or (
        capability.get("os"),
        capability.get("filesystem"),
    ) != ("Darwin", "apfs"):
        failures.append("required Darwin APFS capability is absent")
    actual, errors = _outcomes(candidate, policy["optional_skips"])
    failures.extend(errors)
    for node in policy["required_tests"]:
        if actual.get(node) != "passed":
            failures.append(f"required test did not pass: {node}")

    baseline = {}
    if mode == "pr":
        if not isinstance(base, dict) or not _trusted_identity(
            base.get("identity"), expected_base
        ):
            failures.append("missing or drifted trusted base identity")
        elif problem := _policy_error(base_policy):
            failures.append(f"base: {problem}")
        else:
            baseline, errors = _outcomes(
                base.get("evidence"), base_policy["optional_skips"]
            )
            failures.extend(f"base: {error}" for error in errors)
            for node in base_policy["required_tests"]:
                if baseline.get(node) != "passed":
                    failures.append(f"required base test did not pass: {node}")
            for node, status in baseline.items():
                if node not in actual or (
                    status == "passed" and actual[node] != "passed"
                ):
                    failures.append(
                        f"required base outcome removed or degraded: {node}"
                    )
    observed_children = (
        candidate.get("children") if isinstance(candidate, dict) else None
    )
    failures.extend(
        _child_errors(child, observed_children, policy["required_children"])
    )

    counts = {}
    for name, document, scope in (
        (
            "product",
            product,
            {"root": policy["product_root"], "names": product_inventory},
        ),
        ("helpers", helpers, {"names": policy["helpers"]}),
    ):
        try:
            counts[name] = totals = _line_totals(document, **scope)
        except ValueError as exc:
            failures.append(f"{name}: {exc}")
            continue
        if (
            totals["covered_lines"] * 100
            < policy["line_floor"] * totals["num_statements"]
        ):
            failures.append(f"{name}: raw line coverage below 90%")
    return _disposition(
        failures, coverage=counts, tests=len(actual), baseline_tests=len(baseline)
    )


def _read(path):
    def object_without_duplicates(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError("duplicate JSON object member")
        return result

    if path is None:
        raise ValueError("required input is absent")
    return json.loads(
        Path(path).read_text(), object_pairs_hook=object_without_duplicates
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--mode", choices=("pr", "push"), required=True)
    for field in (
        "inventory",
        "outcomes",
        "coverage",
        "product-inventory",
        "helpers",
        "child-evidence",
        "capability",
        "base-evidence",
        "base-policy",
        "expected-base",
        "needs",
    ):
        parser.add_argument(f"--{field}")
    args = parser.parse_args(argv)
    try:
        policy = _read(args.policy)
    except (OSError, ValueError) as exc:
        result = _disposition([f"invalid policy: {exc}"])
    else:
        try:
            if args.needs:
                result = check_jobs(policy, _read(args.needs), args.mode)
            else:
                candidate = _read(args.outcomes)
                if _read(args.inventory) != candidate:
                    raise ValueError("inventory and outcome records disagree")
                expected_base = _read(args.expected_base) if args.mode == "pr" else None
                base_policy = None
                if args.mode == "pr":
                    base_policy = _read(args.base_policy)
                    if not isinstance(expected_base, dict) or sha256(
                        Path(args.base_policy).read_bytes()
                    ).hexdigest() != expected_base.get("policy"):
                        raise ValueError(
                            "base policy digest disagrees with trusted identity"
                        )
                result = evaluate(
                    policy,
                    candidate,
                    _read(args.coverage),
                    _read(args.product_inventory),
                    _read(args.helpers),
                    _read(args.child_evidence),
                    _read(args.capability),
                    _read(args.base_evidence) if args.mode == "pr" else None,
                    expected_base,
                    base_policy,
                    args.mode,
                )
        except (OSError, ValueError) as exc:
            result = _disposition([f"invalid evidence: {exc}"])
    print(json.dumps(result, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
