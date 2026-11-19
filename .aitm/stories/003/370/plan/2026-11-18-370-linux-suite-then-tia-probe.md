# Remove the macOS-only host requirements

Yes. The order is this host cleanup, then a TIA probe. After the cleanup, every required test runs on Linux in the cloud. GitHub has no macOS job in that suite. The TIA program is platform agnostic: the same source runs anywhere the runtimes are installed (CPython 3.13, git, and the POSIX calls below). A developer machine can be a Mac. The cloud run is Linux.

The suite and the product executable run on any host that has those runtimes. APFS, `diskutil`, `chmod +a`, `launchctl`, and `libproc.dylib` stop being requirements. The safety properties those checks protect stay, expressed with `stat`, open flags, and a supervisor the same source starts on Linux and macOS.

Python stays the language. The ledger, the monitors, and the pytest suite are already Python, and the portable half of each host call is already in that source. A second language would reimplement the product. It would not make `st_dev`/`st_ino` or a pid file more portable. Node, Go, and Rust stay available for a later slice only if a spike shows a POSIX call this program cannot make.

This plan does not start development. It does not edit pull request #369 or the #355 advisory command. Those stay on the accepted scope until they land. The replacement is the next trunk work after that. #371's language question is closed by this decision: one Python program, Darwin utilities deleted from the required path. The TIA probe that builds the affected-test list is the step after this cleanup, under #370.

## Properties to keep

These are the behaviors the Darwin checks were standing in for. The replacement has to keep them.

- A private ledger file is mode `0600` or a directory is mode `0700`, owned by the effective uid, opened with `O_NOFOLLOW`, and rejected when a non-owner can write it. Root-owned sticky directories stay allowed as ancestors. This is `ledger._validated_path` and `ledger._private`.
- The writer-guard directory and the project directory are different physical directories. Identity is `(st_dev, st_ino)` from `ledger._path_id`. Two spellings of the same inode are one directory. That comparison is already in `ledger._guard_path`. The APFS firmlink is one way to get two spellings. A bind mount is another. The check does not ask which filesystem produced them.
- A private file that carries an extra access grant is refused. An absent ACL is safe. The product never needs to create an ACL in order to start.
- A published file appears under its final name in one rename. Linux uses `renameat2`. macOS uses `renameatx_np`. Both already live in `host_fs._rename_entries`. Each host uses the call it has.
- The monitor restarts from a heartbeat the same program writes. Service custody uses the private owner lease, the child record, and the service heartbeat. External Grok custody uses a host process reader.

## Where the macOS requirements live

### Gates that refuse the whole suite

These are the deletions. They force `macos-26` even for tests that never touch a firmlink or an ACL.

| Location | What it requires |
| --- | --- |
| `.github/workflows/ci.yml` jobs `python-base` (line 28) and `python` (line 134) | `runs-on: macos-26` |
| `ci.yml` around lines 93–97 and 189–194 | `diskutil` + `plutil`, and `test "$filesystem" = apfs`. The candidate job also records `xcodebuild -version` into `capability.json` |
| `tools/ci/python_gate.py` around lines 346–350 | Fails the result unless capability is `("Darwin", "apfs")` |
| `tools/ci/verify_pr.py` around lines 818–825 | Requires platform `(Darwin, apfs)` plus an Xcode string |
| `tools/ci/tia/baseline.py` around line 254 | Runner identity `("macos-26", "Darwin", "apfs")` |
| `tools/ci/tia/local.py` lines 35–36, 62–66, 98–124 | Platform `darwin-apfs`, capabilities `apfs`, `darwin`, `native-acl`. Git is hardcoded to `/usr/bin/git`. The probe runs `/bin/df`, `/usr/sbin/diskutil`, and `/bin/chmod +a` |
| `tools/ci/tia/snapshot.py` line 287 | `/usr/bin/git` when `sys.platform == "darwin"` |
| `tools/ci/tia/suites.json` | Every workload pair and the only runner are `darwin-apfs`. Profiles require `apfs` and `darwin`. The runner advertises `native-acl` |
| `tools/ci/policy.json` | Optional skip whose reason is the missing APFS firmlink path |
| `tools/ci/tests/test_tia_local.py`, `test_python_gate.py`, `test_verify_pr.py`, `test_tia_controls.py`, `test_tia_selection.py`, `test_tia_inventory.py` | Fixtures and assertions that the runner is Darwin APFS |

### Product calls that exist only on Darwin

These stay correct only while a Darwin backend is allowed to be absent. The required executable stops calling them.

| Location | Darwin-only call | Portable replacement already nearby |
| --- | --- | --- |
| `packages/aitm-usage/src/aitm_usage/host_fs.py` `_check_mac_acl` | `acl_get_link_np` / `acl_get_fd_np` via libc. Accepts only an empty ACL or the stock home-directory deny-delete ACE | `_check_linux_acl` treats a missing POSIX ACL xattr as safe and any present ACL as unsafe |
| `host_fs.account_control_root` | `~/Library/Application Support/aitm-usage-control` | `~/.local/state/aitm-usage-control` on Linux |
| `host_fs._rename_entries` | `renameatx_np` with `RENAME_SWAP` / `RENAME_EXCL` | `renameat2` with `RENAME_EXCHANGE` / `RENAME_NOREPLACE` |
| `ledger._guard_path` comment and `backup._require_outside` | Comment and tests treat APFS firmlinks as the only alias | The comparison is already `(st_dev, st_ino)` plus the normalized path tail |
| `install.py` `LaunchControl` and `_libproc` | `/bin/launchctl`, `~/Library/LaunchAgents`, `/usr/lib/libproc.dylib` `proc_pidinfo` / `proc_pidpath` | Linux peer credentials already exist in `monitor_control._LinuxPeer` |
| `sources/grok_scope_hook.py` and `scope_admission.py` | Darwin-specific external process identity | Shared Linux and Darwin readers for external Grok staging and hook verification |
| `host_watch.py` `_Darwin` | FSEvents. `WatchSet` already constructs `_Linux` (inotify) or `_Darwin` from `platform.system()`, and Darwin startup failure falls back to polling | Inotify on Linux. Polling fallback when the native stream is absent |
| `install.py` consumers: `cli.py`, `qualification.py` | Construct `LaunchControl()` and thread it through activate, restore, and qualification | One supervisor object the CLI constructs. The launchd object is no longer the type of that argument |

### Tests that can run only on a Mac

These encode the properties above by using a real firmlink or a real macOS ACL. Each one is rewritten onto the portable fixture so it runs on Linux. The Darwin path fixture leaves the suite.

- `packages/aitm-usage/tests/test_ledger.py` `test_apfs_firmlink_overlap_refused_before_private_creation` and `test_distinct_apfs_alias_cannot_admit_a_second_writer`. Both call `data_volume_alias`, which prefixes `/System/Volumes/Data`.
- `packages/aitm-usage/tests/test_install.py` the `skipif(sys.platform != "darwin")` inherited-ACL test, and the skip whose reason is the missing APFS firmlink path (also named by `policy.json`).
- `packages/aitm-usage/tests/test_host_watch.py` tests that touch `watches._darwin`.
- `tools/ci/tests/test_tia_local.py` skips unless the host is Darwin.

Tests that only pass `system="Darwin"` as data for an adapter (`test_grok.py`, `test_codex.py`, `test_monitor_adapters.py`, and the qualification tuples) are fixture data about a monitored desktop app. They do not call `diskutil` or `launchctl`. They stay. A Darwin desktop adapter remains a data record. It is not a host requirement.

## Replacement

### Filesystem identity

Keep `_path_id` as `(st_dev, st_ino)`. Keep the ancestry walk in `_validated_path`. Replace the firmlink tests with a fixture that presents two path spellings of one inode.

The fixture is a same-inode pair the test creates without root and without APFS: a directory and a second name created by `os.link` is not available for directories, so the test injects the identity list at the boundary `_physical_ancestry` already returns, using a temporary directory for the real `stat` half and a second spelling whose `lstat` result is the same `(st_dev, st_ino)`. The overlap predicate in `_guard_path` is what the test calls. A real `/System/Volumes/Data` path is not part of the proof.

`backup._require_outside` uses the same identity list. Its test uses the same fixture.

### ACL

[#375](../../375/story.md) preserves the existing private-state policy. A private path must pass the mode, owner, ancestry, and identity checks. ACL validation refuses extra grants and inconclusive reads.

- On Linux, an absent `system.posix_acl_access` xattr passes. Directories also require an absent `system.posix_acl_default` xattr. `ENODATA` establishes absence. A present ACL xattr is refused as `Unsafe private ACL`.
- On Darwin, empty ACL text passes. The exact stock macOS home deny-delete ACL passes on ancestors only. The same ACL on a private leaf, any additional ACE, and any other nonempty ACL are refused as `Unsafe private ACL`.
- Darwin libc can return a null ACL and `ENOENT` for an existing ACL-free path or open file descriptor. The path reader is used with the ledger's path checks. For required existing paths, the ledger validates the object before the ACL read and rechecks its identity afterward, rejecting a missing or changed object.
- An unavailable reader, any other unsuccessful read, or a failed conversion to ACL text is refused. The control root stays under `~/Library/Application Support/aitm-usage-control` on Darwin and `~/.local/state/aitm-usage-control` on Linux, using the operating-system account home.
- The required suite keeps the portable custody and ACL fixtures delivered by #377. Native macOS ACL probes remain opt-in. Removing the `chmod +a` probe and the `native-acl` suite capability belongs to #376.

### Supervisor

[#374](../../374/story.md) uses one portable `ServiceSupervisor` for the AITM service. Route CLI install, upgrade, stop, uninstall, restore, and qualification through it. Public `backup.restore` uses the same stopped-writer preflight as CLI restore. Keep the exact wheel, registration, recovery journal, and writer exclusion checks.

- A detached owner process holds a per-project private lease and launches the existing installed service command as its child. Retain the child handle in the owner. Store the registration and mode-0600 PID record in the private account control area. The record binds the exact command, launch incarnation, child PID and recorded start time. The service loop writes its mode-0600 heartbeat under the private ledger root. Qualification checks it against the child PID, recorded start time, and approved runtime, and confirms liveness through a read-only, same-account socket response from the owner. The owner polls its child handle before responding.
- Stop disables respawn and sends a private request bound to the current launch incarnation. Only the owner signals and reaps its own child. It ignores requests for other incarnations, keeps the lease if a child has yet to be reaped, and retires the PID record only if it still describes that launch. Stop waits for both retirement and lease release. A stale or unreadable record holds lifecycle operations. Recovery requires the operator to establish independently that the owner and child have stopped before retiring the stale records. The lease file remains in place. PID and heartbeat fields alone cannot authorize a signal. Stop, upgrade, uninstall, and restore require writer exclusion, including when there is no portable registration.
- A legacy macOS LaunchAgent registration blocks managed lifecycle operations until the operator unloads it and retires its plist. The portable supervisor never invokes launchctl. Keep the retained wheel and backup artifacts available for the new supervisor. There is no login-time installation in this story.

External Grok sessions remain supported. The hook walks its own ancestry up to eight hops and checks the qualified PID, birth time, and executable identity. Share the host process reader between `stage_grok_attempt` and the hook. Linux reads `/proc` and Darwin reads `proc_pidinfo` and `proc_pidpath` through a lazy Darwin adapter used by Grok. Recheck process identity before committing the receipt and before accepting the hook. Missing, unstable, or mismatched observations refuse custody. The AITM supervisor has its own managed-process record.

Verify a real portable start, status and stop across controller instances, the mode-0600 heartbeat, wrong-incarnation stop refusal, missing or replaced PID records during normal transitions, and refusal of a reaped child. Verify stale records, legacy registration, writer exclusion, and existing recovery and restore tests. Exercise Linux external Grok staging and hook ancestry together, including a changed incarnation refusal. Keep the required suite on Ubuntu. Use macOS to check portable service execution and the Darwin Grok adapter.

Delivered to trunk in [PR #381](https://github.com/kburson/aitm/pull/381). The [delivery sign-off](../../374/retro/2026-11-18-374-delivery.md) records the exact Ubuntu trunk run and Grok's review.


### Watch

`WatchSet` already picks inotify or FSEvents. The cloud suite constructs the Linux backend, and where the native stream cannot start it uses the polling fallback. Tests that reach into `_darwin` are rewritten against the public watch events so they run on Linux. The suite has no test that waits on FSEvents.

### CI and the local selector

- `python-base` and `python` run on `ubuntu-24.04`, the same runner `quality` and `file-checks` already use.
- Delete both `diskutil` / `plutil` / `test "$filesystem" = apfs` blocks.
- `capability.json` records `os` from `uname -s` and `runtime`. It no longer records filesystem type or Xcode.
- `python_gate.evaluate` accepts a result whose tests passed. It stops appending "required Darwin APFS capability is absent".
- `verify_pr.py` stops requiring `(Darwin, apfs)` and an Xcode string. It still requires the runner image string and Python `3.13.9`.
- `baseline.py` records the Ubuntu image, `Linux`, and the filesystem `df` reports, as an identity of the run. It does not compare that identity to `apfs`.
- `suites.json` replaces runner `darwin-apfs` with one runner whose capabilities are the portable set: private mode bits, `O_NOFOLLOW`, and exclusive rename. Profiles `product-base`, `product-cli`, and `ci-helpers` require that set. They do not require `apfs`, `darwin`, or `native-acl`.
- `local.py` deletes `_capabilities`. Git is `shutil.which("git")` on every host, including the Darwin branch in `snapshot.py`.
- `policy.json` drops the firmlink skip. The portable overlap test runs everywhere, so there is nothing to skip.
- Cache suffix in the workflow changes from `macos-26-python-3.13.9` to the Ubuntu image plus the same Python version.

The hosted path map (`tools/ci/path_map.py`, `path_map.json`) stays the delivered PR selector. This plan does not rebuild it. #370's import-chain selector is still the later feature, written after this host work, and it is the same Python program.

## Order

Each slice is one function. A slice lands only with its tests. The gate comes off after the portable tests exist, so the safety properties are proved on Ubuntu before Darwin stops being required.

1. **Portable custody tests.** Add the same-inode overlap fixture and the ACL-refusal fixture. Run them on the current macOS suite so the new tests pass before the runner moves. The old firmlink tests still pass on Darwin during this slice.
2. **Supervisor.** Introduce `ServiceSupervisor` for CLI lifecycle, qualification, and public restore. Share the external process identity reader between Grok receipt staging and hook verification.
3. **ACL verification.** Confirm the Linux and Darwin absence cases, the ancestor-only stock Darwin ACL, and refusal of grants and inconclusive reads. On Darwin, verify that the ledger refuses a missing or changed required path even when the ACL read returns `ENOENT`.
4. **Delete the gate.** Edit `suites.json`, `local.py`, `snapshot.py`, `python_gate.py`, `verify_pr.py`, `baseline.py`, `policy.json`, and `ci.yml` as listed above. Move `python-base` and `python` to `ubuntu-24.04`. Update the CI tests that assert the Darwin capability.
5. **Retire the Darwin-only tests.** Delete `data_volume_alias` from the ledger tests and keep the same-inode fixture. Rewrite the `_darwin` watch tests and the `chmod +a` install test onto the portable fixtures. Delete the `test_tia_local.py` Darwin skip by making that test run on Linux. After this slice the suite has no test that requires a Mac.

#355 / PR #369 stay untouched while they are open. Slice 4 edits `local.py`, which that pull request uses. Start slice 4 from trunk after #369 merges, or from a branch that does not rewrite the #355 advisory command. Slices 1–3 can land beside it when they do not change the advisory launcher's Darwin refusal.

## Verification

On an Ubuntu runner, before the story is called done:

- `uv run --project packages/aitm-usage pytest packages/aitm-usage/tests tools/ci/tests` exits 0. The run does not call `diskutil`, `launchctl`, `plutil`, `xcodebuild`, or `chmod +a`.
- `python -m tools.ci.tia.local` reaches selection on a Linux checkout. It does not refuse with "Darwin is required", "APFS is required", or "native ACL support is required".
- A same-inode pair is refused by `Ledger.initialize` with "Writer guard must be outside project state".
- Linux refuses a present ACL xattr and admits an ACL-free file. Darwin admits an ACL-free file and the stock deny-delete ACL on ancestors only. Both platforms refuse an inconclusive ACL read. The Darwin ledger checks also refuse a missing or changed required path after a null ACL result with `ENOENT`.
- `aitm` service start writes the pid file and heartbeat without `/bin/launchctl` on `PATH`.
- The workflow jobs `python-base` and `python` show `runs-on: ubuntu-24.04`, and a pull-request run completes those jobs.
- The workflow file contains no `macos-26` runner and no `diskutil` invocation. A pull request goes green with Linux runners only.

The same source still runs on a developer Mac, because that Mac has CPython and git. The cloud suite does not ask for a Mac.

## After this work: the TIA probe

When the Linux suite is the required suite, start the TIA probe under #370. The probe builds the list of tests for one change. It is the same Python program on the developer machine and in the cloud.

The change set is one of these, all compared with the commit where the branch diverges from its parent:

- The staging area, for uncommitted work on the developer machine.
- `HEAD`, for a local commit.
- The pull-request head against its base, for a cloud run.

From that diff, the probe follows the chain among tests, imported functions, and libraries and unwinds it to the application. The output is the test list for that commit or pull request. Tests named by the list run on the Linux cloud runners. The probe needs CPython and git. It does not need APFS, a native ACL, or a macOS runner.

The delivered path map stays in place until the probe's list is accepted. The probe writes the list and the evidence that the list is sufficient. Wiring that list into the pull-request gate is the feature story after the probe, still on Linux.

## Out of scope

- Rewriting the product in another language.
- Opening the Windows epic. Windows facilities are a later epic that runs this same program.
- Building the TIA test list inside the host-cleanup slices. That probe starts after this work is done.
- Rebuilding the hosted path map before the probe is accepted.
- Changing #133, #351's close condition, or the #355 advisory command.
- A systemd unit or a launchd plist. The supervisor is in-process. OS login items are a later epic.
- A macOS cloud job. Darwin-only tests are rewritten onto the portable fixtures so the required suite has nothing left that waits on a Mac.

## Owner correction: remove the Mac tests first

Owner direction on 2026-11-19T01:20:00Z, after the five stories were filed. GitHub is limiting macOS CI instances. If the tests that require a Mac stay on the required path, #373, #374, #375, and #376 cannot pass CI. #377 is rank 490 and blocks those four.

#377 also moves `python-base` and `python` to `ubuntu-24.04`, deletes the `diskutil`, `plutil`, APFS, and `xcodebuild` steps, and stops `python_gate.py` and `verify_pr.py` from failing a result that is not Darwin APFS. Deleting the tests while those jobs stay on `macos-26` would still queue the pull request. The jobs replace `shasum` and the macOS `gh` archive with `sha256sum` and the Linux `gh` archive. `local.py` stays out of #377 because pull request #369 already edits it.

#376 keeps `suites.json`, `baseline.py`, `local.py`, the snapshot git path, and the `policy.json` firmlink skip. The `local.py` edit still starts after pull request #369 merges. That wait is a note. The slice list in Order stays as the record of the accepted plan. The backlog order is the table in the decomposition addendum.
