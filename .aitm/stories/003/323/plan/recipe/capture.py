"""Save native provider facts before and after reading attempt evidence."""

from base64 import b64decode
from pathlib import Path
import sys

import evidence_io as io
from source.operator_recovery import WORKFLOW, need

ROOT = Path(__file__).resolve().parent
RECORDS = ROOT / "records"
CONTROL_FILES = (WORKFLOW, "operator_recovery.py", "run-recovery.sh", "scenario.json", "operator.allowed_signers")
MAX_ARCHIVE = 8 * 1024 * 1024


def controls(repo, sha, evidence):
    bundle = evidence / "controls"
    bundle.mkdir()
    for path in CONTROL_FILES:
        name = Path(path).name
        metadata = io.get(repo, f"contents/{path}?ref={sha}", bundle / (name + ".provider.json"))
        need(metadata["type"] == "file" and metadata["encoding"] == "base64", "lab control is not a regular blob")
        (bundle / name).write_bytes(b64decode(metadata["content"]))
    commit = io.get(repo, f"git/commits/{sha}", evidence / "lab-git-commit.json")
    io.get(repo, f"git/trees/{commit['tree']['sha']}?recursive=1", evidence / "lab-git-tree.json")


def capture(evidence, *, include_logs=False):
    evidence.mkdir()
    plan = io.read(RECORDS / "scenario.json")
    repo = plan["lab"]["repository"]
    sha = (RECORDS / "lab-sha").read_text().strip()
    workflow = io.read(RECORDS / "lab-workflow.json")["id"]
    hold_id = io.read(RECORDS / "lab-hold-response.json")["id"]
    identifier = io.read(RECORDS / "dispatch/dispatch-response.json")["workflow_run_id"]
    path = f"actions/runs/{identifier}"
    route = path + "/attempts/1"
    listing = f"actions/workflows/{workflow}/runs?branch=trunk&per_page=100"
    io.get(repo, "", evidence / "repository.json")
    branch = io.get(repo, "branches/trunk", evidence / "branch-before.json")
    io.get(repo, "rules/branches/trunk", evidence / "rules-before.json")
    io.get(repo, f"rulesets/{hold_id}", evidence / "hold-before.json")
    io.get(repo, f"actions/workflows/{workflow}", evidence / "workflow.json")
    io.pages(repo, listing, "workflow_runs", evidence / "workflow-runs-before.json")
    run = io.get(repo, path, evidence / "run-before.json")
    if run["run_attempt"] == 1:
        io.get(repo, route, evidence / "attempt.json")
        io.get(repo, f"check-suites/{run['check_suite_id']}", evidence / "suite.json")
        jobs = io.pages(repo, f"{route}/jobs?per_page=100", "jobs", evidence / "jobs.json")
        for job in jobs:
            io.get(repo, f"check-runs/{job['id']}", evidence / f"check-{job['id']}.json")
        artifacts = io.pages(repo, f"{path}/artifacts?per_page=100", "artifacts", evidence / "artifacts.json")
        found = [a for a in artifacts if a["name"] == "aitm-recovery-a1" and not a["expired"]]
        if len(found) == 1 and 0 < found[0]["size_in_bytes"] <= MAX_ARCHIVE:
            (evidence / "artifact.zip").write_bytes(io.raw(repo, f"actions/artifacts/{found[0]['id']}/zip"))
        if include_logs and run["status"] == "completed":
            (evidence / "actions-logs.zip").write_bytes(io.raw(repo, f"{route}/logs"))
    if branch["commit"]["sha"] == sha:
        controls(repo, sha, evidence)
    io.get(repo, "branches/trunk", evidence / "branch-after.json")
    io.get(repo, f"rulesets/{hold_id}", evidence / "hold-after.json")
    io.get(repo, "rules/branches/trunk", evidence / "rules-after.json")
    io.pages(repo, listing, "workflow_runs", evidence / "workflow-runs-after.json")
    io.get(repo, path, evidence / "run-after.json")


if __name__ == "__main__":
    capture(RECORDS / sys.argv[1], include_logs="--logs" in sys.argv)
