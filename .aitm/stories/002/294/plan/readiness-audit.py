"""Read live gate and hosted evidence. Run with the planning checkout as the argument."""

import json
import subprocess
import sys
from datetime import UTC, datetime
from hashlib import sha256
from math import ceil
from pathlib import Path
from tempfile import TemporaryDirectory

REPO = "kburson/aitm"
EVIDENCE_REV = "f45459b8830449efe66f664bbc14a414abb3900d"
SCHEDULE_ID = 418826440
FAST_ID = 419184012
INPUTS = (
    ".github/workflows/ci.yml",
    "packages/aitm-usage/pyproject.toml",
    "packages/aitm-usage/uv.lock",
    "tools/ci/policy.json",
    "tools/ci/python_gate.py",
    "tools/ci/verify_pr.py",
    "tools/ci/pytest_evidence.py",
    "tools/ci/file_checks.py",
    "tools/ci/file-lint",
)
SHADOW_INPUTS = (
    ".github/workflows/fast-story-shadow.yml",
    ".github/workflows/scheduled-full-shadow.yml",
    "tools/ci/ci_fast_story_shadow.py",
    "tools/ci/ci_scheduled_shadow.py",
    "tools/ci/run_scheduled_shadow.sh",
    "tools/ci/ci_advisory.py",
    "tools/ci/ci_incident.py",
    "tools/ci/ci_recovery.py",
)
STORIES = (277, 278, 279, 285, 286, 287, 288, 289, 290, 291, 292, 293)
ROOT = Path(sys.argv[1]).resolve()


def run(*args, **kwargs):
    return subprocess.check_output(args, cwd=ROOT, **kwargs)


def git(*args):
    return run("git", *args).decode().strip()


def provider(path):
    endpoint = f"repos/{REPO}/{path}".rstrip("/")
    return json.loads(run("gh", "api", endpoint))


def digest(data):
    return sha256(data).hexdigest()


def evidence(path):
    return run("git", "show", f"{EVIDENCE_REV}:{path.as_posix()}")


def sample(name, rows):
    values = sorted(rows)
    return {
        "label": name,
        "n": len(values),
        "p95_seconds": values[ceil(0.95 * len(values)) - 1],
        "samples_seconds": values,
    }


def scheduled_reader(head):
    with TemporaryDirectory(prefix="aitm-294-read-") as scratch:
        archive = run("git", "archive", head, "tools/ci")
        subprocess.run(["tar", "-xf", "-", "-C", scratch], input=archive, check=True)
        return json.loads(
            run(sys.executable, f"{scratch}/tools/ci/ci_scheduled_shadow.py")
        )


def deliveries():
    result = {}
    for number in STORIES:
        story = Path(f".aitm/stories/002/{number}")
        receipt = evidence(story / "plan/delivery.json")
        packet = json.loads(receipt)
        signed = evidence(story / packet["review"])
        assert packet["issue"] == number and packet["status"] == "accepted"
        assert packet["review_sha256"] == digest(signed)
        closure = json.loads(evidence(story / "plan/closure-receipt.json"))
        assert closure["board"]["stateReason"] == "COMPLETED"
        result[number] = {
            "delivery_sha256": digest(receipt),
            "review": packet["review"],
            "review_sha256": digest(signed),
        }
    return result


def workflow_history(workflow, event=None):
    filter_event = f"&event={event}" if event else ""
    doc = provider(
        f"actions/workflows/{workflow}/runs?branch=trunk&per_page=100{filter_event}"
    )
    rows = doc["workflow_runs"]
    assert len(rows) == doc["total_count"]
    fields = (
        "id",
        "event",
        "head_branch",
        "head_sha",
        "created_at",
        "status",
        "conclusion",
        "run_attempt",
    )
    return [{key: row[key] for key in fields} for row in rows]


def readback():
    run(
        "git",
        "fetch",
        "--quiet",
        "origin",
        "refs/heads/trunk:refs/remotes/origin/trunk",
    )
    head = git("rev-parse", "origin/trunk")
    branch = provider("branches/trunk")
    assert branch["commit"]["sha"] == head and branch["protected"]
    repo = provider("")
    assert repo["default_branch"] == "trunk"
    rules = provider("rules/branches/trunk")
    ruleset_id = {r["ruleset_id"] for r in rules}
    rule_details = []
    for identifier in sorted(ruleset_id):
        rule = provider(f"rulesets/{identifier}")
        rule_details.append(
            {
                key: rule[key]
                for key in ("id", "enforcement", "conditions", "rules", "bypass_actors")
            }
        )
    legacy = subprocess.run(
        ["gh", "api", f"repos/{REPO}/branches/trunk/protection"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    legacy_read = json.loads(legacy.stdout)
    if legacy.returncode:
        assert (
            legacy_read["status"] == "404"
            and legacy_read["message"] == "Branch not protected"
        )
    scheduled = provider(f"actions/workflows/{SCHEDULE_ID}")
    fast = provider(f"actions/workflows/{FAST_ID}")
    assert scheduled["state"] == fast["state"] == "active"
    return {
        "repository": REPO,
        "trunk": head,
        "authenticated_identity_has_repository_admin_role": repo["permissions"][
            "admin"
        ],
        "gate": {path: git("rev-parse", f"{head}:{path}") for path in INPUTS},
        "effective_rules": rules,
        "rulesets": rule_details,
        "legacy_branch_protection": legacy_read,
        "shadow": {path: git("rev-parse", f"{head}:{path}") for path in SHADOW_INPUTS},
        "scheduled_runs": workflow_history(SCHEDULE_ID, "schedule"),
        "fast_shadow_runs": workflow_history(FAST_ID),
        "current_scheduled_reader": scheduled_reader(head),
    }


evidence_root = Path(".aitm/stories/002")
plan293 = evidence_root / "293/plan"
matrix_bytes = evidence(plan293 / "qualification-summary.json")
matrix = json.loads(matrix_bytes)
data293 = json.loads(evidence(plan293 / "delivery.json"))
assert data293["summary_sha256"] == digest(matrix_bytes)
assert data293["archive_sha256"] == digest(evidence(plan293 / "benchmark-evidence.zip"))
assert matrix["all_paired_examples_reconciled"]
assert len(matrix["cases"]) == 6
timings = [
    sample(
        mode,
        [
            r["timing"]["first_trigger_to_effective"]
            for r in matrix["cases"].values()
            if r["mode"] == mode
        ],
    )
    for mode in ("selected", "full-required")
]
timings.append(
    sample(
        "full-reference",
        [
            r["timing"]["first_trigger_to_full_reference"]
            for r in matrix["cases"].values()
        ],
    )
)
for row in timings:
    assert (
        row["p95_seconds"]
        == matrix["groups"][row["label"]]["trigger_to_verdict_p95_seconds"]
    )
print(
    json.dumps(
        {
            "schema": "aitm.294.readiness-audit/v1",
            "captured_at": datetime.now(UTC).isoformat(),
            "retained_planning_commit": EVIDENCE_REV,
            **readback(),
            "predecessors": deliveries(),
            "qualification_293": {
                "summary_sha256": digest(matrix_bytes),
                "archive_sha256": data293["archive_sha256"],
                "timings": timings,
                "workload": matrix["workload"],
            },
        },
        indent=2,
        sort_keys=True,
    )
)
