# Local story dashboard

Read a pinned AITM planning commit and generate a standalone HTML dashboard. It runs offline in a browser. Refresh by rebuilding from a new planning pin and explicit UTC cutoff.

## Build and open

Use a POSIX system, Python 3.13 or later, Git, and a complete clone of AITM with the dashboard tools on trunk. Run these commands from the source checkout. The qualification used macOS, Python 3.13.9 and Chrome. A shallow clone can omit historical planning pins. Keep output in a private directory outside every Git worktree. The UTC cutoff must be at or after the selected planning commit and the receipt registrations you intend to include.

```sh
git fetch origin refs/heads/planning:refs/remotes/origin/planning
reader="$(pwd -P)"
planning_sha="$(git rev-parse origin/planning)"
cutoff_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
output="$(mktemp -d "${TMPDIR:-/tmp}/aitm-story-dashboard.XXXXXX")"

python -m tools.story_dashboard.snapshot \
  --repo "$reader" --commit "$planning_sha" --as-of "$cutoff_utc" \
  --output "$output"
python -m tools.story_dashboard.render \
  --snapshot "$output/snapshot.json" --output "$output/dashboard.html"

shasum -a 256 "$output/snapshot.json"
printf 'Open %s\n' "$output/dashboard.html"
```

Match the digest to `snapshot_sha256` in `validation.json`. The report records source and coverage gaps. Open `dashboard.html` directly from disk. Use the epic, state and Actual coverage filters, then expand **Timing and evidence** on an epic or child. A link opens the corresponding GitHub issue or commit-pinned source when selected.

## Read the numbers

- **Actual** is qualified agent effort. It includes in-turn tool execution once and excludes owner waits and idle time. An epic combines direct and descendant effort. Parallel agents add effort for their overlapping minutes.
- **Observed working wall time** counts overlapping work once. Workflow elapsed and age use their own all-phase and implementation boundaries. Check the scope shown on each measure.
- **Owner wait** and **Cost** each have their own coverage and evidence. Owner wait needs evidenced boundaries. Cost uses separately verified provider usage at the chosen report cutoff. Supply a validated local selector with `--usage-report selector.json` on the snapshot command if available. Unknown Cost has no implied zero price.
- **Partial** marks observed evidence with incomplete coverage. Expand the measure to see its evidence-through, basis and sources. For calibration, compare estimates to complete Actual evidence for the same phase and agent scope.

Use the same planning pin, cutoff and optional usage selector to reproduce a view. To refresh, fetch planning, set a new pin and UTC cutoff, choose a separate output directory, and rerun both commands. Keep a prior snapshot and validation pair when you want to compare them later.

Use the [capture and board readback guide](operator.md) to record new evidence and verify a manual board update.

## Reproduce the qualification

Use the commands above with these exact planning inputs. Choose a fresh output directory for each view.

| View | Planning commit | UTC cutoff |
| --- | --- | --- |
| Historical backfill | `17761cc1928fd916cf32a9c078d4a742bfcb32b8` | `2026-11-11T04:23:16Z` |
| Live capture pilot | `527dce9bd7847181a67dc23c6bb2c9844f15c87f` | `2026-11-11T04:45:27Z` |

The historical view includes #111's 2.5 h estimate, 36m 26.725s of partial Actual, and 12m 54s of implementation elapsed. All-phase elapsed and Cost are Unknown for #111. The later view shows #191's separate partial pilot Actual and its Unknown owner wait. Filter by epic #100 or #181 to inspect the corresponding story and epic evidence.

[Qualification evidence](https://github.com/kburson/aitm/blob/planning/.aitm/stories/001/193/plan/delivery-checklist.md) retains the pinned digests and offline readback.
