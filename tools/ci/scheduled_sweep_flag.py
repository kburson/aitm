"""Reconcile the advisory from the original attempts of scheduled category sweeps."""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

from verify_pr import GitHub, Hold, decode_json, digest, positive, require, timestamp

REPO = "kburson/aitm"
REPO_ID = 1450406435
BRANCH = "trunk"
WORKFLOW = ".github/workflows/category-full-sweep.yml"
WORKFLOW_ID = 425235652
WORKFLOW_BLOB = "b4f3f4bc22c9f93d4e7e02f7c012da7dbe20ae52"
FLOOR = 4
FLOOR_RUN = 44864075824
FLOOR_SHA = "8ab84ba0590286d4655ea94e4d9de99f25ea1f2e"
SCHEDULE_DEPLOYED = datetime(2026, 11, 20, 23, 8, 52, tzinfo=timezone.utc)
SCHEMA = "aitm.scheduled-sweep-flag/v1"
TITLE = "Scheduled category full sweep advisory"
BINDING_PATH = Path(__file__).with_suffix(".json")
BINDING_FIELDS = {
    "issue_number",
    "issue_id",
    "activation_floor",
}
FAILURES = {"failure", "timed_out"}
IGNORED = {"cancelled", "action_required", "neutral", "skipped", "stale"}
PENDING = {"queued", "in_progress", "requested", "waiting", "pending"}
RUN_FIELDS = {
    "repository_id",
    "workflow_id",
    "run_id",
    "run_number",
    "run_attempt",
    "head_sha",
    "conclusion",
    "result_at",
}
JOB_FIELDS = (
    "id",
    "name",
    "head_sha",
    "status",
    "conclusion",
    "started_at",
    "completed_at",
)
MAX_BODY = 8192
HISTORY_CAP = 1000
READ_ERRORS = (ValueError, TypeError, KeyError, AttributeError, OSError, RecursionError)
HISTORY_LIST = f"actions/workflows/{WORKFLOW_ID}/runs"
ISSUE_QUERY = """
query($number: Int!) {
  repository(owner: "kburson", name: "aitm") {
    databaseId nameWithOwner
    issue(number: $number) {
      number databaseId state title body lastEditedAt
      editor { __typename ... on Bot { databaseId } ... on User { databaseId } }
    }
  }
}
"""


def utc_string(date):
    return date.isoformat(timespec="seconds").replace("+00:00", "Z")


def utc_timestamp(value):
    require(
        isinstance(value, str)
        and re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value
        ),
        "expected a UTC timestamp",
    )
    try:
        return timestamp(value)
    except ValueError:
        raise Hold("invalid UTC timestamp") from None


def attempt_url(run):
    require(
        positive(run["run_id"])
        and type(run["run_attempt"]) is int
        and run["run_attempt"] == 1,
        "invalid attempt link",
    )
    return f"https://github.com/{REPO}/actions/runs/{run['run_id']}/attempts/1"


def validate_floor(number, run_id, source):
    require(
        (number == FLOOR) == (run_id == FLOOR_RUN),
        "activation floor identity disagrees",
    )
    if number == FLOOR:
        require(source == FLOOR_SHA, "activation floor source disagrees")


def validate_record(record):
    require(
        isinstance(record, dict) and set(record) == {"schema", "state", "run"},
        "invalid record fields",
    )
    require(record["schema"] == SCHEMA, "unknown advisory schema")
    state, run = record["state"], record["run"]
    if state == "uninitialized":
        require(run is None, "unexpected bootstrap run")
        return None
    require(isinstance(run, dict) and set(run) == RUN_FIELDS, "invalid run fields")
    require(
        run["repository_id"] == REPO_ID
        and run["workflow_id"] == WORKFLOW_ID
        and all(
            type(run[key]) is int
            for key in ("repository_id", "workflow_id", "run_attempt")
        )
        and positive(run["run_number"])
        and run["run_number"] >= FLOOR
        and digest(run["head_sha"]),
        "invalid record run identity",
    )
    attempt_url(run)
    validate_floor(run["run_number"], run["run_id"], run["head_sha"])
    utc_timestamp(run["result_at"])
    require(
        (
            state == "active"
            and run["conclusion"] in ("failure", "timed_out")
            and run["run_number"] > FLOOR
        )
        or (state == "clear" and run["conclusion"] == "success"),
        "record state disagrees with conclusion",
    )
    return record


def summary(record):
    if record is None:
        return "Scheduled category full sweep advisory unavailable: no verified result yet."
    run = record["run"]
    link = (
        f"[run {run['run_number']}, attempt {run['run_attempt']}]({attempt_url(run)})"
    )
    if record["state"] == "active":
        return f"Scheduled category full sweep failed: {link} at {run['result_at']}."
    return (
        f"Scheduled category full sweep flag clear as of {run['result_at']} ({link})."
    )


def render_body(record):
    if record is None:
        record = {"schema": SCHEMA, "state": "uninitialized", "run": None}
    return f"{summary(validate_record(record))}\n\n```json\n{json.dumps(record, indent=2)}\n```\n"


def parse_body(body):
    require(
        isinstance(body, str) and len(body.encode()) <= MAX_BODY,
        "invalid advisory body size",
    )
    match = re.fullmatch(r"([^\r\n]+)\n\n```json\n([^\r`]+)\n```\n", body)
    require(match is not None, "malformed advisory body")
    try:
        record = validate_record(decode_json(match[2]))
    except (ValueError, RecursionError):
        raise Hold("invalid advisory JSON or record") from None
    require(match[1] == summary(record), "advisory summary disagrees with record")
    return record


def load_binding():
    binding = decode_json(BINDING_PATH.read_bytes())
    require(
        isinstance(binding, dict)
        and set(binding) == BINDING_FIELDS
        and all(positive(value) for value in binding.values())
        and binding["activation_floor"] >= FLOOR,
        "invalid advisory issue binding",
    )
    return binding


@dataclass(frozen=True)
class Snapshot:
    body: str
    edited_at: str | None
    editor_id: int | None
    record: dict | None


class InvalidRecord(Hold):
    """The advisory issue is readable but its body is invalid."""


def validate_snapshot(repo, binding):
    require(
        repo
        and repo["nameWithOwner"] == REPO
        and repo["databaseId"] == REPO_ID
        and isinstance(repo["issue"], dict),
        "advisory issue unavailable or repository binding disagrees",
    )
    issue = repo["issue"]
    require(
        issue["number"] == binding["issue_number"]
        and issue["databaseId"] == binding["issue_id"]
        and issue["state"] == "OPEN"
        and issue["title"] == TITLE,
        "advisory issue is closed or binding disagrees",
    )
    body, edited_at, editor = issue["body"], issue["lastEditedAt"], issue["editor"]
    try:
        record = parse_body(body)
    except READ_ERRORS as exc:
        raise InvalidRecord("invalid advisory issue body") from exc
    if edited_at is not None:
        utc_timestamp(edited_at)
    editor_id = editor.get("databaseId") if isinstance(editor, dict) else None
    return Snapshot(body, edited_at, editor_id, record)


class IssueStore:
    def __init__(self, github, binding):
        self.github = github
        self.binding = binding

    def read(self):
        response = decode_json(
            self.github.command(
                [
                    "api",
                    "graphql",
                    "--hostname",
                    "github.com",
                    "-f",
                    f"query={ISSUE_QUERY}",
                    "-F",
                    f"number={self.binding['issue_number']}",
                ],
                65536,
            )
        )
        require("errors" not in response, "advisory issue query failed")
        return validate_snapshot(response["data"]["repository"], self.binding)

    def write(self, body):
        self.github.command(
            [
                "api",
                "--hostname",
                "github.com",
                "--method",
                "PATCH",
                f"repos/{REPO}/issues/{self.binding['issue_number']}",
                "--raw-field",
                f"body={body}",
            ],
            65536,
        )


class SweepGitHub(GitHub):
    def optional_attempt(self, run_id):
        """Distinguish a missing cached link from an unavailable GitHub API."""
        try:
            response = subprocess.run(
                [
                    "gh",
                    "api",
                    "--hostname",
                    "github.com",
                    "--method",
                    "GET",
                    "--include",
                    f"repos/{REPO}/actions/runs/{run_id}/attempts/1",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            raise Hold("cached attempt unavailable") from None
        headers, separator, body = response.stdout.partition("\n\n")
        status = headers.splitlines()[0].split() if headers else []
        if response.returncode != 0 and status[1:2] == ["404"]:
            return None
        require(
            response.returncode == 0
            and status[1:2] == ["200"]
            and separator
            and len(body.encode()) <= 65536,
            "cached attempt unavailable",
        )
        return decode_json(body)


def verify_target(github):
    repo = github.document("")
    require(
        repo["id"] == REPO_ID
        and repo["full_name"] == REPO
        and repo["default_branch"] == BRANCH,
        "scheduled sweep repository or default branch disagrees",
    )
    workflow = github.document(f"actions/workflows/{WORKFLOW_ID}")
    require(
        workflow["id"] == WORKFLOW_ID
        and workflow["path"] == WORKFLOW
        and workflow["state"] == "active",
        "scheduled sweep workflow identity or state disagrees",
    )


@dataclass(frozen=True)
class RunIdentity:
    run_id: int
    number: int
    source: str
    created_at: str


def identity(raw):
    require(
        raw["workflow_id"] == WORKFLOW_ID
        and raw["path"] == WORKFLOW
        and raw["event"] == "schedule"
        and raw["head_branch"] == BRANCH
        and raw["repository"]["id"] == raw["head_repository"]["id"] == REPO_ID
        and positive(raw["id"])
        and positive(raw["run_number"])
        and digest(raw["head_sha"]),
        "scheduled sweep run identity disagrees",
    )
    require(
        utc_timestamp(raw["created_at"]) >= SCHEDULE_DEPLOYED,
        "run predates schedule activation",
    )
    validate_floor(raw["run_number"], raw["id"], raw["head_sha"])
    return RunIdentity(raw["id"], raw["run_number"], raw["head_sha"], raw["created_at"])


def history(github, observed_at):
    """Read the complete visible provider range with bounded subdivision at the search cap."""
    base = {"event": "schedule", "branch": BRANCH}
    windows = [(SCHEDULE_DEPLOYED, observed_at)]
    by_id = {}
    by_number = {}
    for _ in range(64):
        if not windows:
            return by_number
        start, end = windows.pop()
        options = dict(base, created=f"{utc_string(start)}..{utc_string(end)}")
        route = f"{HISTORY_LIST}?{urlencode(options)}"
        count = github.document(f"{route}&per_page=1")["total_count"]
        require(type(count) is int and count >= 0, "invalid scheduled history count")
        if count >= HISTORY_CAP:
            seconds = int((end - start).total_seconds())
            require(
                seconds > 1,
                "scheduled history cannot be read within the provider search cap",
            )
            middle = start + timedelta(seconds=seconds // 2)
            windows.extend([(start, middle), (middle, end)])
            continue
        rows = github.pages(f"{route}&per_page=100", "workflow_runs")
        require(len(rows) == count, "scheduled history changed while paging")
        seen = set()
        for row in rows:
            run = identity(row)
            require(
                start <= utc_timestamp(run.created_at) <= end,
                "history row falls outside query window",
            )
            require(
                run.run_id not in seen
                and by_id.get(run.run_id, run) == run
                and by_number.get(run.number, run) == run,
                "duplicate or contradictory scheduled history identity",
            )
            seen.add(run.run_id)
            by_id[run.run_id] = by_number[run.number] = run
    raise Hold("scheduled history exceeded the reconciliation window budget")


def verify_success(github, run, attempt, route):
    blob = github.document(f"contents/{WORKFLOW}?ref={run.source}")
    require(
        blob["type"] == "file" and blob["sha"] == WORKFLOW_BLOB,
        "sweep source lacks the reviewed reconciliation contract",
    )
    jobs = github.pages(f"{route}/jobs?per_page=100", "jobs")
    matches = [job for job in jobs if job["name"] == "reconcile"]
    require(len(matches) == 1, "successful sweep lacks one exact reconcile job")
    job = matches[0]
    require(
        positive(job["id"])
        and sum(other["id"] == job["id"] for other in jobs) == 1
        and job["run_id"] == run.run_id
        and type(job["run_attempt"]) is int
        and job["run_attempt"] == 1
        and job["head_sha"] == run.source
        and job["status"] == "completed"
        and job["conclusion"] == "success"
        and utc_timestamp(attempt["run_started_at"])
        <= utc_timestamp(job["started_at"])
        <= utc_timestamp(job["completed_at"])
        <= utc_timestamp(attempt["updated_at"]),
        "reconcile job is unverified for this attempt",
    )
    suite = github.document(f"check-suites/{attempt['check_suite_id']}")
    check = github.document(f"check-runs/{job['id']}")
    require(
        suite["id"] == attempt["check_suite_id"] == check["check_suite"]["id"]
        and suite["head_sha"] == run.source
        and suite["head_branch"] == BRANCH
        and suite["app"]["slug"] == check["app"]["slug"] == "github-actions"
        and positive(suite["app"]["id"])
        and suite["app"]["id"] == check["app"]["id"]
        and all(check[key] == job[key] for key in JOB_FIELDS),
        "GitHub Actions reconcile check or suite disagrees",
    )


def attempt_route(run_id):
    return f"actions/runs/{run_id}/attempts/1"


def record_for_attempt(github, run, attempt):
    require(
        identity(attempt) == run
        and type(attempt["run_attempt"]) is int
        and attempt["run_attempt"] == 1
        and positive(attempt["check_suite_id"]),
        "original attempt disagrees with scheduled history",
    )
    status, conclusion = attempt["status"], attempt["conclusion"]
    if status in PENDING and conclusion is None:
        return None
    require(
        status == "completed" and isinstance(conclusion, str),
        "unrecognized original attempt status",
    )
    require(
        utc_timestamp(run.created_at)
        <= utc_timestamp(attempt["run_started_at"])
        <= utc_timestamp(attempt["updated_at"]),
        "original attempt timestamps disagree",
    )
    require(
        conclusion in FAILURES | IGNORED | {"success"},
        "unrecognized original attempt conclusion",
    )
    if conclusion in IGNORED:
        return None
    if conclusion == "success":
        verify_success(github, run, attempt, attempt_route(run.run_id))
    return validate_record(
        {
            "schema": SCHEMA,
            "state": "clear" if conclusion == "success" else "active",
            "run": {
                "repository_id": REPO_ID,
                "workflow_id": WORKFLOW_ID,
                "run_id": run.run_id,
                "run_number": run.number,
                "run_attempt": 1,
                "head_sha": run.source,
                "conclusion": conclusion,
                "result_at": attempt["updated_at"],
            },
        }
    )


def select_record(github, runs, activation_floor):
    for number in sorted(runs, reverse=True):
        if number < activation_floor:
            break
        run = runs[number]
        attempt = github.document(attempt_route(run.run_id))
        decision = record_for_attempt(github, run, attempt)
        if decision:
            return decision
    return None


def check_cached_link(github, cached, desired, runs, activation_floor):
    """Treat a newer cached link as a hint when it is missing from the listing."""
    if not cached:
        return desired
    run = cached["run"]
    minimum = desired["run"]["run_number"] + 1 if desired else activation_floor
    if run["run_number"] < minimum or any(
        row.run_id == run["run_id"] for row in runs.values()
    ):
        return desired
    attempt = github.optional_attempt(run["run_id"])
    if attempt is None or (
        attempt["workflow_id"],
        attempt["event"],
        attempt["head_branch"],
    ) != (WORKFLOW_ID, "schedule", BRANCH):
        return desired
    linked = identity(attempt)
    require(
        linked.run_id == run["run_id"], "cached attempt endpoint disagrees with its ID"
    )
    if linked.number < minimum:
        return desired
    return record_for_attempt(github, linked, attempt) or desired


def reconcile(github, *, activation_floor=FLOOR, cached=None):
    verify_target(github)
    for _ in range(2):
        cutoff = datetime.now(timezone.utc).replace(microsecond=0)
        runs = history(github, cutoff)
        desired = select_record(github, runs, activation_floor)
        desired = check_cached_link(github, cached, desired, runs, activation_floor)
        if runs == history(github, cutoff):
            require(desired is not None, "no verified sweep result")
            return desired
    raise Hold("scheduled history membership did not stabilize")


def publish(github, store, *, activation_floor=FLOOR):
    initial = store.read()
    for _ in range(2):
        desired = reconcile(
            github, activation_floor=activation_floor, cached=initial.record
        )
        body = render_body(desired)
        if initial.body == body:
            return "unchanged"
        require(store.read() == initial, "advisory changed before publication")
        try:
            store.write(body)
        except Hold:
            # The provider might have applied the PATCH before the response was lost.
            pass
        current = store.read()
        if current.body == body and current.record == desired:
            return desired["state"]
        require(current == initial, "advisory changed during publication")
    raise Hold("advisory write was not confirmed after bounded retry")


def unavailable(reason):
    return {"schema": SCHEMA, "state": "unavailable", "run": None, "reason": reason}


def check_record(github, store, *, activation_floor=FLOOR):
    """Verify the issue's linked sweep attempt without publishing anything."""
    try:
        advertised = store.read().record
    except InvalidRecord:
        return unavailable("invalid-record")
    except READ_ERRORS:
        return unavailable("store-unavailable")
    if advertised is None:
        return unavailable("uninitialized")
    run = advertised["run"]
    if run["run_number"] < activation_floor:
        return unavailable("invalid-record")
    try:
        attempt = github.document(attempt_route(run["run_id"]))
        try:
            linked = identity(attempt)
        except Hold:
            return unavailable("evidence-mismatch")
        if (linked.run_id, linked.number, linked.source) != (
            run["run_id"],
            run["run_number"],
            run["head_sha"],
        ):
            return unavailable("evidence-mismatch")
        verified = record_for_attempt(github, linked, attempt)
    except READ_ERRORS:
        return unavailable("evidence-unavailable")
    if verified != advertised:
        return unavailable("evidence-mismatch")
    return {**verified, "run_url": attempt_url(verified["run"])}


def run_check(as_json):
    try:
        binding = load_binding()
        github = SweepGitHub(REPO)
        result = check_record(
            github,
            IssueStore(github, binding),
            activation_floor=binding["activation_floor"],
        )
    except READ_ERRORS:
        result = unavailable("store-unavailable")
    state = result["state"]
    if as_json:
        print(json.dumps(result))
    elif state == "unavailable":
        reason = result["reason"].replace("-", " ")
        print(f"Scheduled category full sweep advisory unavailable ({reason}).")
    else:
        label = "failed" if state == "active" else "flag clear"
        print(
            f"Scheduled category full sweep {label} as of {result['run']['result_at']}."
        )
        print(result["run_url"])
    return 2 if state == "unavailable" else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("bootstrap-body", "publish", "check"))
    parser.add_argument(
        "--json", action="store_true", help="machine-readable check output"
    )
    args = parser.parse_args(argv)
    if args.operation == "check":
        return run_check(args.json)
    if args.json:
        parser.error("--json requires check")
    try:
        if args.operation == "bootstrap-body":
            print(render_body(None), end="")
        else:
            github = SweepGitHub(REPO)
            require(
                os.environ.get("GH_TOKEN"), "authenticated Actions token unavailable"
            )
            binding = load_binding()
            store = IssueStore(github, binding)
            result = publish(
                github, store, activation_floor=binding["activation_floor"]
            )
            print(f"Scheduled sweep advisory: {result}")
    except Hold as exc:
        print(f"Scheduled sweep reconciliation unavailable: {exc}", file=sys.stderr)
        return 2
    except READ_ERRORS:
        print(
            "Scheduled sweep reconciliation unavailable: invalid or incomplete provider response",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
