"""Verify approved historical evidence against authenticated GitHub reads."""

import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess

from admit import Refusal, admit, authorize, load_policy


def github(path):
    return subprocess.check_output(("gh", "api", path))


def obtain(policy):
    base = f"repos/{policy['repository']}/actions"
    attempt = f"{base}/runs/{policy['run']}/attempts/{policy['attempt']}"
    run = json.loads(github(attempt))
    jobs = json.loads(github(f"{attempt}/jobs"))["jobs"]
    if len(jobs) != 1:
        raise Refusal("expected one GitHub observation job")
    artifact = f"{base}/artifacts/{policy['artifact_id']}"
    return {
        "run": run,
        "job": jobs[0],
        "artifact": json.loads(github(artifact)),
        "archive": github(f"{artifact}/zip"),
        "log": subprocess.check_output(("gh", "run", "view", str(policy["run"]), "--repo", policy["repository"],
                                        "--attempt", str(policy["attempt"]), "--log")),
    }


def refused(call):
    try:
        call()
    except Refusal as exc:
        return {"decision": "refuse", "reason": str(exc)}
    raise AssertionError("the negative control was accepted")


def run(policy, root, *, expected_review=True):
    tuple_keys = ("repository", "workflow_id", "workflow_path", "head", "observer_tree", "product_commit",
                  "product_tree", "run", "attempt", "assignment_sha256", "mode")
    request = {key: policy[key] for key in tuple_keys}
    authorize(policy, request)
    evidence = obtain(policy)

    def verify(policy, evidence):
        return admit(policy, request, evidence, root, expected_review=expected_review)
    result = {
        "positive": verify(policy, evidence),
        "negative": {},
    }
    alternate_values = {
        "product_tree": policy["observer_tree"],
        "head": "90684bbdeb375a4c39f65973a4f56259fa4a6b3e",
        "observer_tree": "be26ec4655d26fa77987b3cf5b82817dde384816",
        "attempt": policy["attempt"] + 1,
        "assignment_sha256": "0" * 64,
        "mode": "selected" if policy["mode"] == "full" else "full",
    }
    for key, value in alternate_values.items():
        changed = {**request, key: value}
        result["negative"][key] = refused(lambda: authorize(policy, changed))
    result["negative"]["worker-assertion-only"] = refused(lambda: verify(policy, None))
    wrong_observer = deepcopy(policy)
    wrong_observer["inputs"]["controller_sha256"][2] = "0" * 64
    result["negative"]["observer-file"] = refused(lambda: verify(wrong_observer, evidence))
    wrong_attempt = {**evidence, "run": {**evidence["run"], "run_attempt": policy["attempt"] + 1}}
    result["negative"]["transport-attempt"] = refused(lambda: verify(policy, wrong_attempt))
    wrong_archive = {**evidence, "archive": evidence["archive"] + b"benign marker"}
    result["negative"]["archive-bytes"] = refused(lambda: verify(policy, wrong_archive))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--approved-policy-sha256", required=True)
    parser.add_argument("--provisional", action="store_true")
    args = parser.parse_args()
    raw = args.policy.read_bytes()
    policy = load_policy(raw, args.approved_policy_sha256)
    result = run(policy, args.repo_root, expected_review=not args.provisional)
    changed = {**policy, "product_tree": policy["observer_tree"]}
    changed_raw = json.dumps(changed, indent=2, sort_keys=True).encode() + b"\n"
    result["negative"]["mutated-approved-policy"] = refused(
        lambda: load_policy(changed_raw, args.approved_policy_sha256))
    result["policy_sha256"] = args.approved_policy_sha256
    print(json.dumps(result, indent=2, sort_keys=True))
