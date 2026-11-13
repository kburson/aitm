"""Replay current and historical #103 provider evidence through the same intake."""
from copy import deepcopy
import json

import ci_advisory as ci
from verify_pr import GitHub


class Shadow:
    def __init__(self, github, run_id, missing_artifact=False):
        self.github = github
        self.run = github.document(f"actions/runs/{run_id}")
        self.missing_artifact = missing_artifact
        self.receipts = {}

    def document(self, endpoint):
        result = self.github.document(endpoint)
        if endpoint == "branches/trunk":
            result = deepcopy(result)
            result["commit"]["sha"] = self.run["head_sha"]
        if endpoint in ("", "branches/trunk", "actions/workflows/ci.yml"):
            keys = {
                "": ("id", "full_name"),
                "branches/trunk": ("name", "protected", "commit"),
                "actions/workflows/ci.yml": ("id", "path", "state"),
            }[endpoint]
            result = {key: result[key] for key in keys}
            if endpoint == "branches/trunk":
                result["commit"] = {"sha": result["commit"]["sha"]}
        elif endpoint.startswith("check-runs/"):
            result = {key: result[key] for key in (*ci.JOB_FIELDS, "check_suite", "app")}
            result["app"] = {key: result["app"][key] for key in ("id", "slug")}
        elif endpoint.startswith("check-suites/"):
            result = {
                key: result[key]
                for key in ("id", "head_branch", "head_sha", "app", "status", "conclusion")
            }
            result["app"] = {key: result["app"][key] for key in ("id", "slug")}
        elif endpoint.startswith("actions/runs/"):
            result = self.normalize_run(result)
        self.receipts[endpoint] = result
        return result

    @staticmethod
    def normalize_run(run):
        keys = (*ci.RUN_FIELDS, "workflow_id", "event", "path", "head_branch",
                "head_sha", "created_at", "repository", "head_repository")
        normalized = {key: run[key] for key in keys}
        for key in ("repository", "head_repository"):
            normalized[key] = {"id": normalized[key]["id"]}
        return normalized

    def pages(self, endpoint, key):
        if key == "workflow_runs":
            result = [self.normalize_run(self.run)]
        else:
            result = self.github.pages(endpoint, key)
        if key == "jobs":
            result = [
                {field: job[field] for field in (*ci.JOB_FIELDS, "run_id", "run_attempt")}
                for job in result
            ]
        if key == "artifacts" and self.missing_artifact:
            result = []
        self.receipts[endpoint] = result
        return result


def main():
    github = GitHub(ci.REPO)
    red = Shadow(github, 43250904624)
    artifact_path = "actions/runs/43250904624/artifacts?per_page=100"
    assert red.pages(artifact_path, "artifacts") == []
    historical = ci.observe(red)
    assert historical["status"] == "red" and historical["failures"] == ["collect-evidence:failure"]
    missing = Shadow(github, 43404405270, missing_artifact=True)
    incomplete = ci.observe(missing)
    assert incomplete["status"] == "incomplete"
    stale = ci.observe(github, expected=(43250904624, 1))
    assert stale["status"] == "stale"
    print(json.dumps({
        "provenance": "shadow-replay-and-live-stale-control",
        "historical": {"decision": historical, "responses": red.receipts},
        "missing_artifact": {"decision": incomplete, "responses": missing.receipts},
        "live_stale": stale,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
