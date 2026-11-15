# Blocked-By sync

The `planning` branch owns dependency declarations in story frontmatter. GitHub issue state supplies close and reopen status. The sync walks paths of open issues and removes a declared blocker when another open blocker already depends on it. Closed issues and stories marked Done in planning have an empty result.

Each run reconciles all planning stories so a later event can also repair a partial write or cover an event superseded in the Actions queue. One generated file, `.aitm/board/blocked-by.json`, carries the projected IDs in planning. The workflow mirrors those IDs to the GitHub issue field that the board displays. The generated commit uses GitHub's expected-head check and preserves the declarative story records. An empty projection deletes that issue's field value.

The workflow on `trunk` handles GitHub issue closes and reopens. Deploy `planning-relay.yml` as `.github/workflows/blocked-by-relay.yml` on the `planning` branch to relay pushes to the default-branch workflow. Writes made by the workflow's repository token do not trigger the push relay. For dependency edits, publish the owning change to `planning` through the normal AITM procedure. Editing a native GitHub dependency link by itself does not update the planning declaration.

Run **Sync Blocked-By** manually from `trunk` for a read-only check. Select **apply** to publish, including after an interrupted reconciliation. Workflows that close issues through their built-in token should also dispatch `aitm-planning-dependencies-changed` if they do not publish a planning checkpoint, since GitHub does not emit a new Actions run for those issue edits.
