# Use the local Blocked-By sync

Use the local sync after editing GitHub Relationships, to change a dependency from the command line, or to refresh the AITM backlog. It reconciles dependency declarations in GitHub and the `planning` branch, then updates the project board's **Blocked-By** field.

Run the commands from the root of an up-to-date AITM source checkout. Have Git, an authenticated GitHub CLI, and Python 3.13 available. The commands use your Git access to fetch the planning branch and your GitHub CLI authentication to update relationships, commit to planning, and set issue fields. Use `gh auth status` to check which GitHub account is active.

## Sync a change from GitHub

After editing an issue's Relationships panel, pass its number to `single`. For example, use these commands after editing #61. The first command previews the changes. The second applies them.

```sh
python3 -m tools.board_sync.local_sync --check single 61
python3 -m tools.board_sync.local_sync single 61
```

Choose a scope based on what you edited.

| Mode | Dependency declarations reconciled |
| --- | --- |
| `single ISSUE` | Relationships involving that issue in either direction |
| `open` | Dependencies declared by issues currently open in GitHub |
| `closed` | Dependencies declared by issues currently closed in GitHub |

A scoped sync can refresh other issues' board fields when the selected relationship change affects their blockers. Use `--check` before any subcommand to see counts of planned relationship, planning file, and board field changes without publishing.

To ask an agent to run the tool, say “Sync Blocked-By for issue #61 in single mode” or “Preview Blocked-By sync for all open issues.”

## Add or remove a dependency

The first argument is the issue that is blocked. The second is its blocker. In the examples below, replace `ISSUE` and `BLOCKER` with issue numbers. Choose the command that matches the edit you intend.

```text
python3 -m tools.board_sync.local_sync add ISSUE BLOCKER
python3 -m tools.board_sync.local_sync remove ISSUE BLOCKER
```

The command reconciles the selected issue's relationships, publishes the corresponding planning changes, and updates the board. A proposed change that would create a dependency cycle stops before publishing.

## Read the backlog and board

Run `make backlog` to sync open issues and print the blocker projection as JSON. Run `make sync-blocked-by` to sync open issues without printing the JSON. `make dashboard` syncs open issues before building the live dashboard.

The board field lists open blockers in issue-number order. If another open blocker already depends on an upstream issue, that upstream issue can be omitted from the field. An empty result clears the field. Closed issues and stories marked Done in planning have blank fields.

## Set up another backlog

The AITM repository uses `kburson/aitm`, the `origin` remote, its `planning` branch, and its own Blocked-By issue field as defaults. For another project, supply the backlog repository and the Git remote that points to it. Use the node ID of the text issue field shown on that project's board.

```sh
python3 -m tools.board_sync.local_sync --repository OWNER/REPO \
  --remote backlog --planning-branch planning --field-id FIELD_NODE_ID --check open
```

The first apply records the last agreed relationships in `.aitm/board/dependency-baseline.json`. If the tool reports that the baseline is missing and GitHub and planning disagree, reconcile those initial declarations before applying. If planning advances during a sync or a write is interrupted, rerun the same scope to reconcile from current data.

For details about the board projection and GitHub Actions integration, see [the Blocked-By sync reference](../tools/board_sync/README.md).
