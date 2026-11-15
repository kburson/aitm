"""Sync AITM dependency declarations and the Blocked-By field on demand."""

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import replace

from tools.board_sync import blocked_by as board

BASELINE = ".aitm/board/dependency-baseline.json"
SCHEMA = "aitm.dependency-baseline/v1"
Edge = tuple[int, int]

RELATIONSHIPS = (
    """
query($endCursor: String, $owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    issues(first: 40, after: $endCursor) {
      totalCount pageInfo { endCursor hasNextPage }
      nodes {
        number
        blockedBy(first: 40) { """
    + """
          totalCount pageInfo { endCursor hasNextPage }
          nodes { number repository { nameWithOwner } }
        }
      }
    }
  }
}
"""
)
MORE = """
query($issue: ID!, $after: String!) {
  node(id: $issue) {
    ... on Issue {
      blockedBy(first: 100, after: $after) {
        totalCount pageInfo { endCursor hasNextPage }
        nodes { number repository { nameWithOwner } }
      }
    }
  }
}
"""
ADD = """
mutation($issue: ID!, $blocker: ID!) {
  addBlockedBy(input: {issueId: $issue, blockingIssueId: $blocker}) {
    issue { id } blockingIssue { id }
  }
}
"""
REMOVE = ADD.replace("addBlockedBy", "removeBlockedBy")


class GitHub(board.GitHub):
    def relationships(self, issues: dict[int, board.Issue]) -> set[Edge]:
        pages = [
            row["repository"]["issues"]
            for row in self.graphql(RELATIONSHIPS, self.repo_vars, paginate=True)
        ]
        nodes = [node for page in pages for node in page["nodes"]]
        numbers = {node["number"] for node in nodes}
        if (
            pages[-1]["pageInfo"]["hasNextPage"]
            or {page["totalCount"] for page in pages} != {len(nodes)}
            or len(numbers) != len(nodes)
            or issues.keys() - numbers
        ):
            raise RuntimeError("Incomplete GitHub relationship scan")
        edges = set()
        for node in nodes:
            number = node["number"]
            if number not in issues:
                continue
            connection = node["blockedBy"]
            total = connection["totalCount"]
            dependencies = list(connection["nodes"])
            cursors = set()
            while connection["pageInfo"]["hasNextPage"]:
                cursor = connection["pageInfo"]["endCursor"]
                if not cursor or cursor in cursors:
                    raise RuntimeError(
                        f"Incomplete relationship pagination for #{number}"
                    )
                cursors.add(cursor)
                connection = self.graphql(
                    MORE, {"issue": issues[number].node_id, "after": cursor}
                )["node"]["blockedBy"]
                if connection["totalCount"] != total:
                    raise RuntimeError(
                        f"Relationships changed during pagination for #{number}"
                    )
                dependencies.extend(connection["nodes"])
            distinct = {item["number"] for item in dependencies}
            if (
                len(distinct) != len(dependencies)
                or len(dependencies) != total
                or any(
                    item["repository"]["nameWithOwner"].lower()
                    != self.repository.lower()
                    for item in dependencies
                )
                or distinct - issues.keys()
            ):
                raise RuntimeError(
                    f"#{number} has incomplete or out-of-scope relationship data"
                )
            edges.update((number, blocker) for blocker in distinct)
        return edges

    def change_relationship(self, issue: str, blocker: str, *, add: bool) -> None:
        self.pace_write()
        mutation, key = (ADD, "addBlockedBy") if add else (REMOVE, "removeBlockedBy")
        changed = self.graphql(mutation, {"issue": issue, "blocker": blocker})[key]
        if changed != {"issue": {"id": issue}, "blockingIssue": {"id": blocker}}:
            raise RuntimeError(
                f"GitHub did not confirm the relationship change for {issue}"
            )


def in_scope(
    mode: str, issue: int | None, edge: Edge, states: dict[int, board.Issue]
) -> bool:
    if mode == "single":
        return issue in edge
    return states[edge[0]].open == (mode == "open")


def valid_edges(edges: set[Edge], stories: dict[int, board.Story]) -> None:
    if any(
        dependent not in stories or blocker not in stories
        for dependent, blocker in edges
    ):
        raise ValueError("A dependency refers to a missing planning story")


def read_baseline(
    text: str | None, planning: set[Edge], github: set[Edge]
) -> set[Edge]:
    if text is None:
        if planning != github:
            raise ValueError(
                "The dependency baseline is missing and planning and GitHub disagree. Resolve the initial declarations before bootstrapping."
            )
        return set(planning)
    payload = json.loads(text)
    if payload["schema"] != SCHEMA or not isinstance(payload["edges"], list):
        raise ValueError("Invalid dependency baseline")
    edges = payload["edges"]
    if any(
        not isinstance(edge, list)
        or len(edge) != 2
        or any(type(n) is not int or n <= 0 for n in edge)
        for edge in edges
    ):
        raise ValueError("Invalid edge in the dependency baseline")
    result = {tuple(edge) for edge in edges}
    if len(result) != len(edges):
        raise ValueError("Duplicate edge in the dependency baseline")
    return result


def reconcile(
    baseline: set[Edge],
    planning: set[Edge],
    github: set[Edge],
    mode: str,
    issue: int | None,
    issues: dict[int, board.Issue],
) -> set[Edge]:
    result = set(baseline)
    for edge in planning | github | baseline:
        if not in_scope(mode, issue, edge, issues):
            continue
        # A change from either side wins over the previously matched value.
        if (
            edge in planning
            and edge in github
            or edge not in baseline
            and edge in planning | github
        ):
            result.add(edge)
        else:
            result.discard(edge)
    return result


def update_index(
    text: str, field: str, current: set[int], remove: set[int], add: set[int]
) -> str:
    if not remove and not add:
        return text
    lines = text.splitlines(keepends=True)
    end = next(i for i, line in enumerate(lines[1:], 1) if line.rstrip("\r\n") == "---")
    matches = [i for i in range(1, end) if lines[i].startswith(f"{field}:")]
    if len(matches) > 1:
        raise ValueError(f"Duplicate {field} declaration")
    if matches:
        existing = json.loads(lines[matches[0]].split(":", 1)[1])
        if (
            not isinstance(existing, list)
            or any(type(n) is not int or n <= 0 for n in existing)
            or len(existing) != len(set(existing))
        ):
            raise ValueError(f"Invalid {field} declaration")
    else:
        existing = sorted(current)
    if matches and set(existing) == (set(existing) - remove) | add:
        return text
    updated = [n for n in existing if n not in remove]
    updated.extend(sorted(add - set(updated)))
    newline = "\r\n" if lines[0].endswith("\r\n") else "\n"
    index = matches[0] if matches else end
    lines[index : index + bool(matches)] = [f"{field}: {json.dumps(updated)}{newline}"]
    return "".join(lines)


def story_changes(
    paths: dict[int, str],
    files: dict[str, str],
    before: set[Edge],
    after: set[Edge],
    baseline: set[Edge],
    agreed: set[Edge],
) -> dict[str, str]:
    changes = {}
    added, removed = after - before, before - after
    # Repair reciprocals for both imported and already-declared planning edits.
    reverse_added = (agreed - baseline) | added
    reverse_removed = (baseline - agreed) | removed
    touched = {
        n for edge in added | removed | reverse_added | reverse_removed for n in edge
    }
    for number in sorted(touched):
        path = paths[number]
        content = files[path]
        for field, index, inserts, deletes in (
            ("blocked-by", 0, added, removed),
            ("blocking", 1, reverse_added, reverse_removed),
        ):
            current, to_remove, to_add = (
                {edge[1 - index] for edge in edges if edge[index] == number}
                for edges in (before, deletes, inserts)
            )
            content = update_index(content, field, current, to_remove, to_add)
        if content != files[path]:
            changes[path] = content
    return changes


def project(
    stories: dict[int, board.Story], edges: set[Edge], issues: dict[int, board.Issue]
) -> dict[int, tuple[int, ...]]:
    incoming: dict[int, list[int]] = {number: [] for number in stories}
    for dependent, blocker in sorted(edges):
        incoming[dependent].append(blocker)
    updated = {
        number: replace(story, blockers=tuple(incoming[number]))
        for number, story in stories.items()
    }
    return board.project(
        updated, {number for number, issue in issues.items() if issue.open}
    )


def run(
    github: GitHub,
    remote: str,
    mode: str,
    issue: int | None,
    *,
    edit: Edge | None = None,
    add: bool = False,
    check: bool = False,
) -> dict[int, tuple[int, ...]]:
    head, files = board.read_planning_files(remote, github.ref, (BASELINE,))
    paths = board.story_paths(files)
    stories = {
        number: board.read_story(files[path], number) for number, path in paths.items()
    }
    issues = github.issues(set(stories))
    if mode == "single" and issue not in issues:
        raise ValueError(f"#{issue} is outside the planning backlog")
    planning = {
        (number, blocker)
        for number, story in stories.items()
        for blocker in story.blockers
    }
    native = github.relationships(issues)
    baseline = read_baseline(files.get(BASELINE), planning, native)
    for edges in (planning, native, baseline):
        valid_edges(edges, stories)

    agreed = reconcile(baseline, planning, native, mode, issue, issues)
    if edit is not None:
        valid_edges({edit}, stories)
        if add:
            agreed.add(edit)
        else:
            agreed.discard(edit)

    def selected(edge):
        return in_scope(mode, issue, edge, issues)

    scoped = {edge for edge in agreed if selected(edge)}
    next_planning = {edge for edge in planning if not selected(edge)} | scoped
    next_native = {edge for edge in native if not selected(edge)} | scoped
    # Validate both destination graphs before the first external write.
    desired = project(stories, next_planning, issues)
    project(stories, next_native, issues)
    updates = story_changes(paths, files, planning, next_planning, baseline, agreed)
    for path, data in (
        (
            BASELINE,
            json.dumps(
                {"schema": SCHEMA, "edges": sorted(agreed)}, separators=(",", ":")
            )
            + "\n",
        ),
        (board.PROJECTION, board.projection_text(desired)),
    ):
        if data != files.get(path):
            updates[path] = data
    board_writes = {}
    for number, blockers in desired.items():
        text = ", ".join(f"#{blocker}" for blocker in blockers) or None
        if text != issues[number].value:
            board_writes[number] = text
    removing, adding = native - next_native, next_native - native
    print(
        f"Blocked-By {mode}: {len(removing)} relationship removals, {len(adding)} additions, "
        f"{len(updates)} planning files, {len(board_writes)} board fields.",
        file=sys.stderr,
    )
    if check:
        return desired
    if github.branch_head() != head:
        raise RuntimeError(
            "Planning changed during sync. Rerun to reconcile the new state."
        )
    for edges, adding_flag in ((removing, False), (adding, True)):
        for dependent, blocker in sorted(edges):
            github.change_relationship(
                issues[dependent].node_id, issues[blocker].node_id, add=adding_flag
            )
    if removing or adding or next_planning != planning:
        current_native = github.relationships(issues)
        if {edge for edge in current_native if selected(edge)} != scoped:
            raise RuntimeError(
                "GitHub relationships changed during sync. Rerun before publishing planning."
            )
    if updates:
        head = github.commit_files(
            head, updates, "chore: sync AITM dependency declarations and board"
        )
    for number, text in board_writes.items():
        try:
            github.write_blockers(issues[number].node_id, text)
        except RuntimeError:
            # The hosted issue-event workflow may have written the same value.
            if github.issues({number})[number].value != text:
                raise
    if github.branch_head() != head:
        raise RuntimeError(
            "Planning advanced while publishing board fields. Rerun sync."
        )
    return desired


def issue_number(text: str) -> int:
    if not re.fullmatch(r"#?[1-9][0-9]*", text):
        raise argparse.ArgumentTypeError("Expected a positive issue number")
    return int(text.lstrip("#"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repository",
        default=board.REPOSITORY,
        help="GitHub backlog repository (OWNER/REPO)",
    )
    parser.add_argument(
        "--remote", default="origin", help="Git remote containing the planning branch"
    )
    parser.add_argument("--planning-branch", default="planning")
    parser.add_argument(
        "--field-id",
        default=board.ISSUE_FIELD_ID,
        help="GitHub Blocked-By issue-field node ID",
    )
    parser.add_argument(
        "--check", action="store_true", help="Calculate changes without writing"
    )
    commands = parser.add_subparsers(dest="command", required=True)
    single = commands.add_parser(
        "single", help="Sync all relationships touching one issue"
    )
    single.add_argument("issue", type=issue_number)
    commands.add_parser("open", help="Sync relationships for all open issues")
    commands.add_parser("closed", help="Sync relationships for all closed issues")
    commands.add_parser(
        "backlog", help="Sync open issues and print their computed blockers"
    )
    for action in ("add", "remove"):
        edit = commands.add_parser(
            action, help=f"{action.capitalize()} a blocker and sync the affected issue"
        )
        edit.add_argument("issue", type=issue_number)
        edit.add_argument("blocker", type=issue_number)
    args = parser.parse_args()
    os.environ["GH_PROMPT_DISABLED"] = "1"
    try:
        github = GitHub(
            args.repository, f"refs/heads/{args.planning_branch}", args.field_id
        )
        if args.command in {"add", "remove"}:
            run(
                github,
                args.remote,
                "single",
                args.issue,
                edit=(args.issue, args.blocker),
                add=args.command == "add",
                check=args.check,
            )
        else:
            mode = "open" if args.command == "backlog" else args.command
            result = run(
                github,
                args.remote,
                mode,
                getattr(args, "issue", None),
                check=args.check,
            )
            if args.command == "backlog":
                print(board.projection_text(result), end="")
    except (
        RuntimeError,
        ValueError,
        KeyError,
        TypeError,
        OSError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"Blocked-By sync failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
