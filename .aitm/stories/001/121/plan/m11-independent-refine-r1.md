[12:14:46]
REFINE_121: HOLD

The split itself is justified. The proposed graph does not preserve every M11 obligation, and the watcher leaf does not yet have the resource ownership the accepted plan requires at the split decision. This review does not authorize Develop, issue creation, or Blocked-By and rank edits. Those changes are outward-facing and need your approval.

## Findings

**1. Shared-root scan: the metadata-first read boundary has no owner (blocking).**
- `_discover_sources` calls `_open_snapshot` and `_origin` on every transcript. That is a physical payload open.
- `_current_candidate` calls `ProviderAdapter().discover(candidate._registration)` for every locator. Admitting one due stream therefore reopens every parked sibling.
- `stream_ref` comes from payload-derived `session_ref`. Exact-locator uniqueness therefore needs each sibling's origin. Counting coordinator API calls cannot satisfy `test_unchanged_parked_payload_is_not_read`.
- The only other route skips `_approved_candidate`, which would bypass fail-closed admission. That is forbidden.
- The required edits are in `sources/scan.py`, `sources/adapter.py` and `monitor_registry.py`. `grok.py:609` may also need edits if its `discover` does not route through `_discover_sources`.
- None of those files is in either proposed leaf, and neither estimate covers the work.
- To the question in the refinement: yes, a second dependency is required.

**2. Native watcher ownership is not designated (blocking).** The accepted plan puts native resource ownership into the split decision. The refinement defers it to "exact JIT." The resource owner, startup signal and teardown order must be in the extraction's scope before it is accepted.

**3. Test-file ownership conflicts (blocking).**
- The proposal gives `test_monitor_watches.py` to the extraction.
- That file carries the three accepted test names, and all three need coordinator reconciliation, shared-root discovery or payload custody.
- So two leaves would write one file.

**4. Coordinator custody: adequately mapped to existing primitives.** The relevant primitives are:
- `ControlInbox`, `WakeIngress` and `Scheduler.take_due`/`finish`
- `Registry.apply_pending` and `verify_boundary` (registry and scope)
- `RoutingJournal` and `ProjectDelivery.attach`

One condition remains: the JIT must name the coordinator as the sole durable writer.

**5. Command integration is not verified.** Register, mark, handoff, dispose and park must each already enqueue through `ControlInbox` from their CLI paths. If any of them applies synchronously, a CLI module edit enters scope and #121 must be re-estimated. I could not verify this without tools.

**6. Native proof is sufficient for availability only.**
- The probes prove symbol binding, callback delivery, thread join, nested enrollment and descriptor release, on arm64 only.
- If x86_64 is an approved platform/architecture tuple, it must be either tested or declared unsupported.
- Recorded actuals (#120 at 0.0715, #304 at 0.131) are partial-coverage. They cannot be used to calibrate estimates.

**7. Current scope housekeeping.**
- The JIT must confirm that `f235fe00` is on trunk and contains the #120 completion. The current checkout is the #120 branch, not the frozen base.
- The story body lists #115 and #120 as required predecessors, but the frontmatter also lists #304. Correct the body.
- Epic #2, C01, cutover and the Claude coverage gap stay excluded.

## Required graph (three leaves)

| Leaf | Blocked-by | Blocking | Rank |
|---|---|---|---|
| **W**: dormant native watcher (new, child of #100) | #120 | #121 | ~245 |
| **I**: metadata-first inventory and selected admission (new, child of #100) | #115, #120, #304 | #121 | ~247.5 |
| **#121**: coordinator, commands, dormant service entry | #115, #120, #304, W, I | #123, #125 | 250 |

- W and I are independent of each other and can run in parallel.
- #123 and #125 keep their dependency through #121, unless either consumes `WatchSet` or the inventory directly. Confirm this at the JIT.
- Every leaf keeps its own Refine/JIT, signed Test, independent source review and Close.

## Conditions for an exact revised scope

### W: watcher
- **Paths.** Create `S/host_watch.py` and `T/test_host_watch.py`. Leave `test_monitor_watches.py` to #121 so the accepted test names stay in their accepted file. Record the new file as a deviation in the revised scope; do not edit the hashed plan.
- **Dormant.** No import from `monitor`, `service` or the CLI. Test verifies this.
- **No new pytest marker.** Use platform `skipif`. A marker would pull `pyproject.toml` or `conftest` into scope.
- **Interface.**
  - The constructor takes `WatchRoot(key, path, expected (st_dev, st_ino))`.
  - `events(timeout) -> tuple[WatchEvent, ...]`.
  - Event kinds are `CHANGED(key, hint)`, `RECONCILE(key, reason)`, `ROOT_LOST` and `ROOT_REPLACED`.
  - `close()` is idempotent, and `WatchSet` works as a context manager.
- **Boundaries.**
  - The watcher only stats directories and never opens a payload.
  - Hints stay in memory.
  - The watcher writes nothing durable.
- **Owner.** `WatchSet` owns every native resource:
  - Darwin: the stream, the retained `CFUNCTYPE` callback, the CF path array and strings, the run-loop reference and the thread.
  - Linux: the inotify fd and the wd→dir map.
- **Startup signal.**
  - Darwin: the run-loop thread sets a `threading.Event` after `FSEventStreamStart` returns true and before `CFRunLoopRun`.
  - Linux: the signal is set when the bounded initial recursive registration completes.
  - Both: the constructor waits with a bounded timeout. A failure tears down and raises a creation error.
  - Both: the first event is always `RECONCILE(startup)`, so the baseline scan runs only after the watch is live.
- **Teardown.**
  - Darwin, in order: Stop, Invalidate, Release, `CFRunLoopStop`, bounded join, then drop the callback reference.
  - Linux: closing the fd releases every watch.
  - Repeated stop is tested.
- **Flag mapping.**
  - FSEvents: `MustScanSubDirs`, `UserDropped`, `KernelDropped` and `EventIdsWrapped` map to `RECONCILE`. `RootChanged` triggers identity revalidation, which yields `LOST` or `REPLACED`.
  - inotify: `IN_Q_OVERFLOW` maps to `RECONCILE`. `IN_IGNORED`, `IN_DELETE_SELF` or `IN_MOVE_SELF` on a root triggers identity revalidation, which yields `LOST` or `REPLACED`.
  - New directory: add the watch, then emit `RECONCILE(enrollment)` to close the race.
- **Bounds.** Directory count is capped per root and in total. The internal queue is bounded with a lock and condition. Exceeding either bound coalesces to `RECONCILE` and moves that root to metadata-only POSIX polling of the same roots.
- **Proof.**
  - Linux overflow is real: exceed `/proc/sys/fs/inotify/max_queued_events` without draining.
  - FSEvents drop flags are injected at the decoder, with the rationale recorded.
  - The signed Test records the Darwin arm64 run and the isolated, network-disabled Linux arm64 run.

### I: inventory and admission
- **Paths.** `sources/scan.py` gets a new inventory and admission function. `_discover_sources` and `discover(registration)` behavior stays unchanged. Other paths:
  - `sources/adapter.py` (monitor entry)
  - `monitor_registry.py` (`_current_candidate` uses the inventory)
  - `grok.py` (include it, or state why it is excluded)
  - Existing `test_scan.py` and the registry tests. Confirm the names at the JIT.
- **Cache validity.**
  - The cached origin is keyed by root identity chain, path, full snapshot identity, size, `mtime_ns` and `ctime_ns`.
  - It is bound to the source `key_id`, the pinned key digest and the current Registry lease.
  - It is held in memory only and dropped on restart.
- **Racy timestamps.** An entry filled within the filesystem's timestamp granularity of the observation is unverified. This is the same rule git uses for racy index entries.
- **Fail-closed rules.**
  - A changed root identity discards all entries.
  - A rotation (identity change) forces reauthentication.
  - Two paths with the same `(dev, ino)` raise `BoundaryUnavailable`.
  - A key mismatch, or a layout, surface, provider or platform mismatch, keeps its current exception.
  - The uniqueness check stays: exactly one `stream_ref` match with the same path.
- **Proof.** `sys.addaudithook` `open` events show zero opens of an unchanged parked sibling during a due sibling's admission, and a reopen of a changed sibling. The legacy `test_scan.py` passes unmodified.

### #121: coordinator
- **Paths.**
  - `S/monitor.py`.
  - The `S/service.py` coordinator entry. `poll` and `run_service` stay untouched and callable.
  - `T/test_monitor_watches.py` with the three accepted tests, plus parked, lost-root, overlapping-root, suspend-write and no-wake reconcile cases.
  - Targeted CLI tests.
- **Named writers.** The coordinator alone writes:
  - coverage gaps through the journal
  - scheduler and park state
  - locator invalidation
  - resume and restart detection, using the clock-gap check and the startup `RECONCILE`

  W and I are read-only producers.
- **Stop condition.** Any CLI or command-path edit, or any further cross-module edit, requires re-estimation and a separately reviewed split.

## Estimates (implementation agent-hours)

| Leaf | Range | Point | Basis |
|---|---|---|---|
| W | 2.75–3.25 | 3.0 | Raised from 2.5–3.0 for the fallback poller, the real Linux overflow and two-host signed runs. Probes de-risk binding. |
| I | 2.0–2.75 | 2.5 | New inventory, registry admission change and audit-hook proof. Legacy path frozen. |
| #121 | 3.25–3.75 | 3.5 | Holds only once W and I are delivered and no CLI edit is required. |

Each leaf is under the four-hour cap. Total M11 rises to about 8.0–9.75 hours. The earlier combined figure understated M11 because it omitted the inventory boundary.

## To clear HOLD
1. Approve the three-leaf graph, or choose another owner for the inventory boundary.
2. Revise the W scope with owner, startup signal, teardown and test-file assignment as above.
3. Confirm at the JIT that the CLI paths for all five commands already queue, and that `f235fe00` contains #120.
