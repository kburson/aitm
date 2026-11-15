# Blocked-By sync

The `planning` branch owns dependency declarations in story frontmatter. GitHub issue state supplies close and reopen status. The sync walks paths of open issues and removes a declared blocker when another open blocker already depends on it. Closed issues and stories marked Done in planning have an empty result. Record lifecycle changes through the AITM procedure so planning and the board status stay aligned. Closing or reopening an issue changes its eligibility as a blocker for other stories.

Each run reconciles all planning stories so a later event can also repair a partial write or cover an event superseded in the Actions queue. One generated file, `.aitm/board/blocked-by.json`, carries the projected IDs in planning. The workflow retries a failed apply once with fresh inputs. It mirrors the projected IDs to the GitHub issue field that the board displays. The generated commit uses GitHub's expected-head check and preserves the declarative story records. An empty projection deletes that issue's field value.

The workflow on `trunk` handles GitHub issue closes and reopens. Deploy `planning-relay.yml` as `.github/workflows/blocked-by-relay.yml` on the `planning` branch to relay pushes to the default-branch workflow. Writes made by the workflow's repository token do not trigger the push relay. For dependency edits, publish the owning change to `planning` through the normal AITM procedure. Editing a native GitHub dependency link by itself does not update the planning declaration.

Run **Sync Blocked-By** manually from `trunk` for a read-only check. Select **apply** to publish, including after an interrupted reconciliation. Workflows that close issues through their built-in token should also dispatch `aitm-planning-dependencies-changed` if they do not publish a planning checkpoint, since GitHub does not emit a new Actions run for those issue edits.

## Local relationship sync

Use the local sync through a Git checkout with Python, Git and an authenticated GitHub CLI. An agent can invoke the same commands. The local sync has three scopes:

| Command | Relationships checked for changes |
| --- | --- |
| `python3 -m tools.board_sync.local_sync single 61` | Incoming and outgoing relationships involving issue #61 |
| `python3 -m tools.board_sync.local_sync open` | Dependencies declared by open issues |
| `python3 -m tools.board_sync.local_sync closed` | Dependencies declared by closed issues |

An AITM dependency edit uses `python3 -m tools.board_sync.local_sync add 61 58` or `python3 -m tools.board_sync.local_sync remove 61 58`. The second ID is the blocker. The command updates GitHub Relationships and the planning declarations, then refreshes derived Blocked-By values. Run all three sync scopes with `--check` before the subcommand to preview changes. The first sync seeds the baseline when the declared relationships agree on both sides.

Use `make backlog` for a live blocker read. It imports GitHub UI changes through the open scope before returning the projection. `make dashboard` runs the same open sync before it reads planning. A scoped import can refresh downstream board values affected by that change. Closed stories retain relationship records and display a blank Blocked-By value. Historical dashboard builds can still read a pinned commit directly.

The baseline tracks the last matched dependency declarations and is published on the planning branch. Future runs compare both sources with that baseline, update only differences, and reject cycles before publishing. If a write leaves one surface ahead, rerunning sync reconciles it. The existing GitHub workflow also refreshes the projection on issue closes and reopens. The local path runs when invoked, with Git and GitHub as its services.

Run in this repository with the defaults. For another GitHub backlog, pass `--repository OWNER/REPO`, `--remote REMOTE` pointing to its planning Git remote, `--planning-branch BRANCH`, and `--field-id NODE_ID` before the subcommand. The GitHub issue field must be the one displayed by that project's board.
