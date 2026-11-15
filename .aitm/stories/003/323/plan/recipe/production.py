"""Capture read-only production controls and exact-source missed-window evidence."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

import evidence_io as io


ROOT = Path(__file__).resolve().parent
SUBJECT = ROOT / "subject"
PRODUCTION = "kburson/aitm"
GATE = (
    ".github/workflows/ci.yml", "packages/aitm-usage/pyproject.toml", "packages/aitm-usage/uv.lock",
    "tools/ci/policy.json", "tools/ci/python_gate.py", "tools/ci/verify_pr.py",
    "tools/ci/pytest_evidence.py", "tools/ci/file_checks.py", "tools/ci/file-lint",
)
SHADOW = (
    ".github/workflows/scheduled-full-shadow.yml", "tools/ci/run_scheduled_shadow.sh",
    "tools/ci/ci_scheduled_shadow.py", ".github/workflows/fast-story-shadow.yml",
    "tools/ci/ci_fast_story_shadow.py", "tools/ci/ci_advisory.py",
    "tools/ci/ci_incident.py", "tools/ci/ci_recovery.py",
)


def git(*args):
    return subprocess.check_output(["git", "-C", str(SUBJECT), *args]).decode().strip()


def capture(out):
    out.mkdir()
    repo = io.get(PRODUCTION, "", out / "repository.json")
    branch = io.get(PRODUCTION, "branches/trunk", out / "branch.json")
    rules = io.get(PRODUCTION, "rules/branches/trunk", out / "rules.json")
    rulesets = {
        str(id): io.get(PRODUCTION, f"rulesets/{id}", out / f"ruleset-{id}.json")
        for id in sorted({row["ruleset_id"] for row in rules})
    }
    workflows = {
        name: io.get(PRODUCTION, f"actions/workflows/{name}", out / name.replace(".yml", ".json"))
        for name in ("ci.yml", "scheduled-full-shadow.yml", "fast-story-shadow.yml")
    }
    assert repo["id"] == 1450406435 and repo["full_name"] == PRODUCTION
    assert repo["default_branch"] == branch["name"] == "trunk" and branch["protected"]
    head = branch["commit"]["sha"]
    if head != git("rev-parse", "HEAD"):
        git("fetch", "--no-tags", "--depth", "1", "https://github.com/kburson/aitm.git", head)
    gate = {path: git("rev-parse", f"{head}:{path}") for path in (*GATE, *SHADOW)}
    assert gate == {path: git("rev-parse", f"HEAD:{path}") for path in (*GATE, *SHADOW)}
    summary = {
        "captured_at": datetime.now(timezone.utc).isoformat(), "repository": PRODUCTION,
        "head": head, "source_checkout": git("rev-parse", "HEAD"), "gate_and_shadow_blobs": gate,
        "effective_rules": rules,
        "rulesets": {id: {k: doc[k] for k in ("id", "enforcement", "rules", "conditions", "bypass_actors")}
                     for id, doc in rulesets.items()},
        "workflows": {name: {k: data[k] for k in ("id", "path", "state")}
                      for name, data in workflows.items()},
    }
    io.write(out / "gate-summary.json", summary)
    scheduled_id = workflows["scheduled-full-shadow.yml"]["id"]
    all_runs = io.pages(PRODUCTION, f"actions/workflows/{scheduled_id}/runs?per_page=100", "workflow_runs",
                        out / "schedule-workflow-runs.json")
    io.pages(PRODUCTION, f"actions/workflows/{scheduled_id}/runs?event=schedule&per_page=100", "workflow_runs",
             out / "schedule-filtered-runs.json")
    for run in all_runs:
        run_id, attempt = run["id"], run["run_attempt"]
        route = f"actions/runs/{run_id}/attempts/{attempt}"
        io.get(PRODUCTION, route, out / f"run-{run_id}-attempt-{attempt}.json")
        io.pages(PRODUCTION, f"{route}/jobs?per_page=100", "jobs", out / f"jobs-{run_id}.json")
        io.pages(PRODUCTION, f"actions/runs/{run_id}/artifacts?per_page=100", "artifacts",
                 out / f"artifacts-{run_id}.json")

    for name, args in (("native-scheduled-reader", []), ("native-diagnostic-reader", ["--dispatch-diagnostic"])):
        result = subprocess.run(
            [sys.executable, "tools/ci/ci_scheduled_shadow.py", *args],
            cwd=SUBJECT, capture_output=True, check=True,
        )
        (out / f"{name}.json").write_bytes(result.stdout)
    scheduled = json.loads((out / "native-scheduled-reader.json").read_bytes())
    diagnostic = json.loads((out / "native-diagnostic-reader.json").read_bytes())
    assert scheduled["sha"] == diagnostic["sha"] == head
    assert scheduled["status"] == "incomplete" and scheduled["artifact"] is None
    assert scheduled["current_verified"] is False and diagnostic["event"] == "workflow_dispatch"
    assert diagnostic["slot"] is None
    print(json.dumps({"scheduled": scheduled, "diagnostic": diagnostic}, sort_keys=True))


if __name__ == "__main__":
    capture(ROOT / "records" / sys.argv[1])
