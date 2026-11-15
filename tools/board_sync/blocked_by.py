"""Project the planning dependency graph into the AITM Blocked-By issue field."""

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from functools import cache

REPOSITORY = "kburson/aitm"
BRANCH = "refs/heads/planning"
ISSUE_FIELD_ID = "IFT_kgDOAvni2w"
PROJECTION = ".aitm/board/blocked-by.json"
STORY_PATH = re.compile(r"\.aitm/stories/[0-9]{3}/([1-9][0-9]*)/story\.md")
ISSUES = """
query($endCursor: String) {
  repository(owner: "kburson", name: "aitm") {
    issues(first: 75, after: $endCursor) {
      totalCount
      pageInfo { endCursor hasNextPage }
      nodes {
        id number state
        issueFieldValues(first: 50) {
          pageInfo { hasNextPage }
          nodes {
            ... on IssueFieldTextValue {
              value
              field { ... on IssueFieldText { id } }
            }
          }
        }
      }
    }
  }
}
"""
HEAD = """
query {
  repository(owner: "kburson", name: "aitm") {
    ref(qualifiedName: "refs/heads/planning") { target { oid } }
  }
}
"""
COMMIT = """
mutation($input: CreateCommitOnBranchInput!) {
  createCommitOnBranch(input: $input) { commit { oid } }
}
"""
SET_FIELD = """
mutation($issue: ID!, $field: ID!, $text: String!) {
  setIssueFieldValue(input: {
    issueId: $issue, issueFields: [{fieldId: $field, textValue: $text}]
  }) {
    issue { id }
    issueFieldValues {
      ... on IssueFieldTextValue { value field { ... on IssueFieldText { id } } }
    }
  }
}
"""
CLEAR_FIELD = """
mutation($issue: ID!, $field: ID!) {
  deleteIssueFieldValue(input: {issueId: $issue, fieldId: $field}) {
    issue { id }
    success
  }
}
"""


@dataclass(frozen=True)
class Story:
    blockers: tuple[int, ...]
    done: bool


@dataclass(frozen=True)
class Issue:
    node_id: str
    open: bool
    value: str | None


def read_story(text: str, number: int) -> Story:
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError(f"#{number} has no frontmatter")
    header = {}
    for line in lines[1 : lines.index("---", 1)]:
        key, separator, value = line.partition(":")
        if separator and key in {"id", "state", "blocked-by"}:
            if key in header:
                raise ValueError(f"#{number} has duplicate {key} frontmatter")
            header[key] = value.strip()
    if header.get("id") != str(number) or not header.get("state"):
        raise ValueError(f"#{number} has invalid story identity or state")
    blockers = json.loads(header.get("blocked-by", "null"))
    if (
        not isinstance(blockers, list)
        or any(type(blocker) is not int or blocker <= 0 for blocker in blockers)
        or len(set(blockers)) != len(blockers)
    ):
        raise ValueError(f"#{number} has invalid blocked-by frontmatter")
    state = header["state"].strip("\"'").lower()
    return Story(tuple(blockers), state == "done")


def project(
    stories: dict[int, Story], open_issues: set[int]
) -> dict[int, tuple[int, ...]]:
    visiting = set()

    @cache
    def ancestors(number: int) -> frozenset[int]:
        if number in visiting:
            raise ValueError(f"Dependency cycle at #{number}")
        visiting.add(number)
        upstream = set()
        for blocker in stories[number].blockers:
            if blocker not in stories:
                raise ValueError(f"#{number} declares unknown blocker #{blocker}")
            upstream.update(ancestors(blocker))
            if blocker in open_issues and number in open_issues:
                upstream.add(blocker)
        visiting.remove(number)
        # Validate the whole graph, and only use paths made of open issues for reduction.
        return frozenset(upstream) if number in open_issues else frozenset()

    for number in stories:
        ancestors(number)
    result = {}
    for number, story in sorted(stories.items()):
        direct = set(story.blockers) & open_issues
        redundant = set().union(*(ancestors(blocker) for blocker in direct))
        result[number] = (
            tuple(sorted(direct - redundant))
            if number in open_issues and not story.done
            else ()
        )
    return result


def command(*args: str, data: str | None = None) -> bytes:
    result = subprocess.run(
        args, input=data, capture_output=True, text=True, timeout=120, check=False
    )
    if result.returncode:
        raise RuntimeError(
            result.stderr.strip() or f"{args[0]} exited with {result.returncode}"
        )
    return result.stdout.encode()


def git(*args: str) -> str:
    return command("git", *args).decode()


def read_planning() -> tuple[str, dict[int, Story], str | None]:
    depth = (
        ("--depth=1",)
        if git("rev-parse", "--is-shallow-repository").strip() == "true"
        else ()
    )
    git("fetch", "--no-tags", *depth, "origin", BRANCH)
    head = git("rev-parse", "--verify", "FETCH_HEAD^{commit}").strip()
    listing = git("ls-tree", "-r", "-z", head, "--", ".aitm/stories", PROJECTION)
    stories = {}
    snapshot = None
    for entry in listing.rstrip("\0").split("\0"):
        if not entry:
            continue
        metadata, path = entry.split("\t", 1)
        match = STORY_PATH.fullmatch(path)
        if not match and path != PROJECTION:
            continue
        mode, kind, blob = metadata.split()
        if mode != "100644" or kind != "blob":
            raise ValueError(f"Expected a regular file at {path}")
        content = git("cat-file", "blob", blob)
        if path == PROJECTION:
            snapshot = content
            continue
        number = int(match[1])
        if number in stories:
            raise ValueError(f"Unexpected story path {path}")
        stories[number] = read_story(content, number)
    if not stories:
        raise ValueError("The planning commit contains no story records")
    return head, stories, snapshot


class GitHub:
    def __init__(self) -> None:
        self.last_write = None

    def graphql(
        self, query: str, variables: dict | None = None, *, paginate: bool = False
    ):
        if paginate:
            data = json.loads(
                command(
                    "gh",
                    "api",
                    "graphql",
                    "--paginate",
                    "--slurp",
                    "-f",
                    f"query={query}",
                )
            )
            if not data or any(page.get("errors") for page in data):
                raise RuntimeError("GitHub returned incomplete pages")
            return [page["data"] for page in data]
        data = json.loads(
            command(
                "gh",
                "api",
                "graphql",
                "--input",
                "-",
                data=json.dumps({"query": query, "variables": variables or {}}),
            )
        )
        if data.get("errors"):
            raise RuntimeError("GitHub returned a GraphQL error")
        return data["data"]

    def branch_head(self) -> str:
        return self.graphql(HEAD)["repository"]["ref"]["target"]["oid"]

    def issues(self, required: set[int]) -> dict[int, Issue]:
        pages = [
            page["repository"]["issues"] for page in self.graphql(ISSUES, paginate=True)
        ]
        nodes = [issue for page in pages for issue in page["nodes"]]
        counts = {page["totalCount"] for page in pages}
        if (
            pages[-1]["pageInfo"]["hasNextPage"]
            or counts != {len(nodes)}
            or len({issue["number"] for issue in nodes}) != len(nodes)
        ):
            raise RuntimeError("GitHub returned an incomplete issue list")
        result = {}
        for issue in nodes:
            number = issue["number"]
            if number not in required:
                continue
            field_values = issue["issueFieldValues"]
            if (
                issue["state"] not in {"OPEN", "CLOSED"}
                or field_values["pageInfo"]["hasNextPage"]
            ):
                raise RuntimeError(
                    f"Incomplete state or issue field read for #{number}"
                )
            values = [
                field["value"]
                for field in field_values["nodes"]
                if (field.get("field") or {}).get("id") == ISSUE_FIELD_ID
            ]
            if len(values) > 1:
                raise RuntimeError(f"Ambiguous Blocked-By field on #{number}")
            result[number] = Issue(
                issue["id"], issue["state"] == "OPEN", next(iter(values), None)
            )
        if missing := required - result.keys():
            raise RuntimeError(
                f"GitHub did not return planning issues {sorted(missing)}"
            )
        return result

    def commit_snapshot(self, head: str, content: str) -> str:
        payload = {
            "branch": {"repositoryNameWithOwner": REPOSITORY, "branchName": "planning"},
            "expectedHeadOid": head,
            "message": {"headline": "chore: reconcile the Blocked-By board projection"},
            "fileChanges": {
                "additions": [
                    {
                        "path": PROJECTION,
                        "contents": base64.b64encode(content.encode()).decode(),
                    }
                ]
            },
        }
        return self.graphql(COMMIT, {"input": payload})["createCommitOnBranch"][
            "commit"
        ]["oid"]

    def write_blockers(self, issue: str, text: str | None) -> None:
        if self.last_write is not None:
            time.sleep(max(0, 1.05 - (time.monotonic() - self.last_write)))
        variables = {"issue": issue, "field": ISSUE_FIELD_ID}
        if text is None:
            result = self.graphql(CLEAR_FIELD, variables)["deleteIssueFieldValue"]
            confirmed = result["success"] is True
        else:
            result = self.graphql(SET_FIELD, {**variables, "text": text})[
                "setIssueFieldValue"
            ]
            confirmed = {"value": text, "field": {"id": ISSUE_FIELD_ID}} in result[
                "issueFieldValues"
            ]
        self.last_write = time.monotonic()
        if not confirmed or result["issue"] != {"id": issue}:
            raise RuntimeError(
                f"GitHub did not confirm the Blocked-By update for {issue}"
            )


def publish(
    github: GitHub,
    head: str,
    prior: str | None,
    issues: dict[int, Issue],
    desired: dict[int, tuple[int, ...]],
    *,
    apply: bool,
) -> None:
    snapshot = (
        json.dumps(
            {"schema": "aitm.board-blocked-by/v1", "blocked_by": desired}, indent=2
        )
        + "\n"
    )
    changes = {}
    for number, blockers in desired.items():
        text = ", ".join(f"#{blocker}" for blocker in blockers) or None
        if text != issues[number].value:
            changes[number] = text
    print(
        f"Checked {len(desired)} issues; {len(changes)} board changes; planning projection {'differs' if snapshot != prior else 'matches'}.",
        flush=True,
    )
    if not apply:
        if changes:
            print(f"Board differences: {changes}")
        return
    if github.branch_head() != head:
        raise RuntimeError(
            "Planning changed during reconciliation; run against the new head"
        )
    if snapshot != prior:
        published = github.commit_snapshot(head, snapshot)
        print(f"Published planning projection at {published}", flush=True)
    for number, text in changes.items():
        github.write_blockers(issues[number].node_id, text)
    print(f"Verified {len(changes)} Blocked-By issue field writes.", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Publish to planning and update GitHub"
    )
    args = parser.parse_args()
    os.environ["GH_PROMPT_DISABLED"] = "1"
    try:
        head, stories, prior = read_planning()
        github = GitHub()
        issues = github.issues(set(stories))
        desired = project(
            stories, {number for number, issue in issues.items() if issue.open}
        )
        publish(github, head, prior, issues, desired, apply=args.apply)
    except (
        RuntimeError,
        ValueError,
        KeyError,
        TypeError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"Blocked-By reconciliation failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
