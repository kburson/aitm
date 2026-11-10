# Native reviewer response, round 1

Native source SHA-256 `sha256:16bda4afc6a15efc6147456d308b6c26ecf876e867e4ea1b4a927f437a46befa`. Submitted `2026-11-10T13:37:39.066Z`.

Mode: `normal`

## Summary

This is an independent cross-provider review of the full #100 implementation plan (237 lines, sealed digest `sha256:57b0fc3f…7e37`). I checked it against the accepted #100 specification (85 lines) and the prior SPR rounds (`spr-2026-11-10-monitor-plan` reviewer responses 1–3). I did not repeat findings that the SPR already resolved: schema compatibility, post-ACK dispute ownership, receiver reconciliation, operator entry points, native carrier discovery, cutover crash windows and snapshot-token identity. To ground the file-ownership claims, I read the existing `packages/aitm-usage` source in the local trunk checkout at `[local trunk checkout]`. I did not run Git, so I could not confirm that checkout's HEAD against the plan's pinned reference `58fb8ba`. The cited code facts are long-standing #83 structure, so they are unlikely to differ.

The plan is well structured. Its leaf order, contracts and red/green tests trace closely to the spec. Five gaps remain. The largest is that the plan never decides what happens to the existing #83 per-project command surface and inbox after adoption. That surface is the live production scope-marker carrier, so the omission can silently lose story attribution or let a legacy writer bypass the routing journal. The other four are smaller. The Grok leaf does not own the closed provider and rate-card types it must extend. Cutover tests leave out stream continuity across the cutover boundary. The live qualification leaves leave out several cases the spec requires. Hook installation does not specify where hooks are written or what privacy rules they follow.

## Findings

### R1-F001 — High: The #83 per-project command surface, inbox and writer custody have no post-adoption owner

**Where.** Plan lines 116, 125, 152, 161–163, 179–181, 197 and 208. Spec lines 13–17, 21–23, 61, 65 and 67.

**Evidence.** In the #83 package, `cli.py` lines 389–482 give one global `--project STATE_DIR` option, which is mandatory (lines 480–481). The same file defines these per-project commands: `scope mark`, `scope correct`, `development bind`, `item alias`, `item parent`, `source add-anchor`, `register`, `collect-once`, `service run|install|upgrade|stop|uninstall|prune`, `backup`, `restore`, `status`, `rollup` and `export`. `scope`, `development`, `item` and `source add-anchor` queue commands into the project's private inbox. The legacy collector drains that inbox (`service.py` line 911, `drain_inbox`). The package README (lines 58–70) documents the production marker carrier: a native tool call that runs `aitm-usage --project '<state>' scope mark --marker FILE` inside the turn. The native transcript record of that exact command string is the boundary receipt. `run_service` holds the project writer guard for its whole lifetime (`service.py` lines 1006–1016). `collect-once` takes the guard only for one poll (lines 999–1003).

The plan adds new user-scoped commands: `monitor scope mark|handoff|dispose --request FILE` (M07), the `monitor …` registry, capture and park commands (M06 and M10) and `report …` (M13). It also adds a new `ControlInbox` (M06). M13 confines the legacy `rollup` and `export`, but no leaf decides what happens after adoption to the other legacy entry points:

1. **Legacy marker carrier.** Existing AITM workflow turns emit `aitm-usage --project … scope mark` and `development bind`. M04 and M07 do not say whether the monitor's native-receipt recognizer accepts this legacy command form for an adopted project, rejects it with a visible coverage reason, or requires the workflow to migrate to `monitor scope mark`. If the legacy command still exits 0 and queues into an inbox that nothing drains, every post-cutover story marker for AITM is silently lost. That usage falls into **Unattributed to a story** with no diagnostic.
2. **Legacy inbox at cutover.** M16 confirms the "final checkpoint" but does not drain or carry over legacy inbox entries that were queued before the stop and not yet applied. These include markers, corrections, development bindings, item alias and parent relationships, and anchors. Spec line 65 requires adopting scope history and registration. Spec line 59 needs the draft aliases and epic parents for story drilldown.
3. **`item alias|parent` and `scope correct` after cutover.** No leaf owns ingesting relationship and correction commands into the monitor. M13's drilldown "reuse[s] relationship and rollup logic", but it does not say where new relationships come from.
4. **Legacy writers.** `collect-once`, `service run`, `register`, `restore` and legacy `service install|upgrade` can still be invoked against an adopted project. M09 "reuse[s] existing guarded transactions", which suggests the guard is taken per write. In that case a legacy `collect-once` can acquire the guard between monitor transactions and commit rows directly. Those rows bypass the journal's single-claim reservation, which violates spec lines 13 and 53. A legacy `restore` can also replace a ledger behind the journal. M15 tests only refusal at activation.
5. **CLI shape.** The new subcommands `report stories --project UUID`, `monitor capture … --project UUID` and `monitor hooks install --project UUID` reuse the `project` destination of the mandatory global `--project STATE_DIR` (a `Path`). In argparse the subparser value overwrites the global one, so the types collide. The user-scoped `monitor` and `report` commands have no project state directory at all, yet `main()` currently refuses any invocation without one.

**Required change.** Add an explicit "legacy command surface after adoption" contract with a named owning leaf for each legacy entry point:

- `scope mark`, `scope correct` and `development bind`: decide whether each is accepted as a native carrier, translated, or refused visibly (M07 or M04).
- `item alias|parent`: decide where relationship commands are ingested (M07 or M13).
- `register` and `source add-anchor`: map them onto the M06 registry or refuse them (M06).
- `collect-once`, `service run|install|upgrade` and `restore`: refuse them for adopted projects with a stable reason (M15 or M16).

State that the coordinator holds each adopted project's writer guard for its whole lifetime, or that every legacy writer path refuses once the store is in monitor schema. M16 must drain or explicitly carry over pending legacy inbox entries under the guard before migration, and record them in the cutover receipt. Define the new CLI's global-option handling so `--project STATE_DIR` and `--project UUID` cannot collide, and so user-scoped commands do not require a state directory. Update the ownership table to match.

**Test acceptance.**
- After a rehearsed cutover, run the README's exact legacy `scope mark` command shape in a native turn. Prove it either routes the next boundary to the marked story or produces a visible refusal or coverage reason. It must never exit successfully without any effect.
- A legacy inbox entry queued just before the legacy stop is applied exactly once after cutover.
- `collect-once`, `service run` and `restore` against an adopted project refuse without writing while the monitor runs, including between monitor transactions.
- `report stories --project <uuid>` parses alongside the legacy global option.

### R1-F002 — Medium: M05 does not own the closed provider, model and rate-card types it must extend for Grok

**Where.** Plan lines 41–45, 89–91 and 105–112. Spec lines 47 and 61.

**Evidence.** `types.py` line 17 defines `Provider` as a closed `StrEnum` with only `CODEX` and `CLAUDE`. `ModelLabel` at line 89 is also closed. `pricing.py` lines 29–39 hard-code `_RateSource` and the `_MODELS` map, and `_ModelRate.__post_init__` (lines 67–76) treats every non-Codex provider as Claude. It rejects any Grok row unless that row carries Claude's 5-minute and 1-hour cache-write classes. Rates load from the packaged resource `rates/<version>.json`, with the default version pinned at `_DEFAULT_VERSION = "2026-11-09"`. `RateCard.basis` digests the full card. The legacy `export.py` row (around line 117) serializes the existing token categories. `qualification.py` lines 102–103 enumerate only the Codex Desktop and Claude native surfaces.

M05's "Files" entry names only `S/sources/grok.py`, `S/pricing.py` and the Grok fixtures. `S/types.py` belongs to M03, which runs earlier, and the `rates/` resource is unowned. Unless the plan says so, an implementer may add Grok rows to the existing `2026-11-09.json` or change `_DEFAULT_VERSION`. Either change alters the card digest and breaks the frozen-rate-card byte-identity guarantee (plan line 23, spec line 61). M05's tests also cannot express Grok's distinct cache semantics ("persisted input includes cache", spec line 47) or provider cost ticks without edits to `types.py`.

**Required change.**
- Give M05 ownership of the `Provider` and `ModelLabel` extension and the Grok token-category and provider-tick fields in `S/types.py`, or move those additions into M03 explicitly.
- Add the `rates/` resource to M05 and require a new versioned rate card. The legacy `2026-11-09.json` and the default legacy-export rate card must stay unchanged.
- Generalize `_ModelRate` validation per provider instead of using the Codex-versus-everything-else branch.
- State whether the M05 Grok fields enter only the versioned monitor export (M14) and never the legacy `export_as_of` row.

**Test acceptance.**
- The legacy rate card's `RateBasis` digest and the `test_legacy_export_bytes_remain_fixed` bytes are unchanged after M05.
- A Grok rate row validates under its own cache semantics.
- A Grok observation with no matching rate prices as Unknown.
- A legacy-schema decoder cannot be reached with a `grok` provider value.

### R1-F003 — Medium: Cutover tests do not cover stream continuity across the cutover boundary

**Where.** Plan lines 136–138, 145 and 208–211. Spec lines 51, 55, 65, 67 and 80.

**Evidence.** Spec line 65 says to "resume existing streams at verified continuity with the established request-key algorithm." Spec line 67 adds that "delayed revisions may update [existing AITM history] only when they prove the original lineage and observation key," and that "project-keyed legacy references alone cannot seed the service-wide claim index." The journal's service-level claim index therefore starts empty for all pre-cutover AITM history. M09 says only "reuse stable project pseudonyms." No leaf states how the monitor matches a post-cutover revision, or a later counter-epoch read of a pre-cutover observation, to its existing legacy row. That match is needed so the revision updates the row instead of reserving a new service claim and project key. Nothing says either how such a revision is prevented from being reserved for a different project.

The M16 tests cover export parity, copied archives, an older backup, pre-write and post-write failure, a legacy write between backup and stop, and an unACKed first commit. None covers:
- a Claude streamed request whose first revision is written by the legacy collector and whose later revision arrives after cutover;
- a Codex Desktop stream whose counter epoch continues across cutover.

These are the ordinary cases on the first day after cutover, not edge cases.

**Required change.** In M16, or in M09 with an M16 rehearsal, define how the journal handles a revision whose verified lineage matches an adopted legacy row. Use the established #83 request-key algorithm and the adopted project key to recognize the row. Bind the revision to that row's project as an existing claim seeded only by proven lineage. Refuse any other project. Keep the M04 Codex counter-epoch rules continuous across the stop interval.

**Test acceptance.** Add these M16 tests:
- `test_post_cutover_revision_updates_legacy_row_once`: a Claude request partially written before the stop gets its final streamed revision after cutover. The report counts it once at the adopted key, with the newer revision.
- `test_codex_counter_epoch_continues_across_cutover`: no duplicate and no gap at the stop boundary.

Both must keep the frozen legacy export bytes unchanged.

### R1-F004 — Medium: The live qualification leaves omit several cases spec line 75 requires on the supported matrix

**Where.** Plan lines 29–33, 217, 225 and 232. Spec lines 75 and 80.

**Evidence.** Spec line 75 requires these cases to run on real overlapping sessions "in the supported platform matrix":
- two repositories with the same issue number and **at least two checkouts for one project**;
- a cross-project handoff **with a dependency**;
- an **unmarked review**, a **project-wide task** and an **ambiguous project claim**;
- a valid ordinary marker for A in a registered B checkout;
- **qualified and unqualified host surfaces mixed in one approved root**, with the coverage gap verified;
- sums that reconcile, with no double charge.

M18 lists only same-story-number projects, three roles, a foreign marker followed by a handoff, Grok cases, fork and fold, a LaunchAgent, crash recovery and export parity. M19 says "re-run the two-project, three-provider acceptance case" without defining it. On macOS the mixed-surface case is concrete: the spec places the Codex CLI rollout in the Desktop source root (spec line 11). That is exactly the configuration a live run must prove contributes zero, and it is missing from M18. Review focus #5 (plan line 33) says M17 covers the hookless-Grok-beside-unqualified-shared-root path, but none of M17's three named tests (line 217) exercises it.

**Required change.**
- Define one named "two-project, three-provider acceptance case" in the plan, M17 or M18, that enumerates every spec line 75 item above.
- Make M18 and M19 run that case per target. On macOS include a real Codex CLI rollout in the Desktop root, verified to contribute zero with a sanitized coverage reason.
- Add an M17 deterministic test for focus #5 so the coverage claim on line 33 is true, or correct line 33.

**Test acceptance.**
- The M18 and M19 receipt validators (`test_monitor_mac_receipt_…` and `test_linux_receipt_…`) reject a receipt that lacks any enumerated case.
- M17 includes `test_hookless_grok_beside_unqualified_shared_root_source_exports_no_sibling_data`, or an equivalently named test.

### R1-F005 — Medium: Hook installation does not specify its target location or its privacy and rollback rules

**Where.** Plan lines 152–156, 197 and 208. Spec lines 17, 21–23 and 29.

**Evidence.** M10 installs "an owned project hook" with `monitor hooks install --project UUID --provider ID`, preserving foreign hooks. Each provider has several hook locations: user scope, a tracked project file such as `.claude/settings.json`, an untracked local file, or a plugin. A wake hook must reach the same-user socket in the pinned private state directory and run the installed executable. If the hook is written into a tracked repository file, it puts raw private paths into Git. That contradicts spec line 17: "Preserve raw paths only in approved private configuration." It also creates a repository-configuration artifact that the spec says carries no authority. In addition, nothing says whether M10's tests or the M15 candidate rehearsal may write to the operator's real provider configuration before the M16 cutover, or what M16 rollback does with installed hooks.

**Required change.**
- State the per-provider install target. It must be user-scope or untracked local configuration, never a tracked repository file.
- Hook command lines must contain no raw private state path beyond what approved private configuration allows.
- Require M10 tests and the M15 rehearsal to use isolated provider homes.
- Define the M16 rollback disposition for installed hooks: remove them, or leave them as harmless failing wakes, with evidence either way.

**Test acceptance.**
- After `monitor hooks install` in a fixture checkout, there is no change to tracked files.
- The M17 sentinel scan finds no unapproved raw path in any repository-visible file.
- A legacy restore leaves the providers working, with hooks removed or inert.

## Required changes

1. R1-F001: Add a post-adoption contract for every legacy #83 command and inbox entry point, with an owner and tests. This covers the marker carrier, the inbox drain at cutover, relationships and corrections, legacy writer refusal or lifetime guard custody, and the CLI `--project` collision.
2. R1-F002: Give M05, or M03 explicitly, ownership of the `Provider`, `ModelLabel` and token-category extensions in `types.py` and the `rates/` resource. Require a new versioned rate card and leave the legacy card unchanged.
3. R1-F003: Define and test how post-cutover revisions and Codex counter epochs continue pre-cutover legacy rows exactly once.
4. R1-F004: Define the named live acceptance case so it covers every spec line 75 item. Make the M18 and M19 receipts require it, including the macOS mixed-surface case. Make review focus #5's M17 claim true.
5. R1-F005: Specify the hook install location, the no-raw-path rule, isolated provider homes for tests and rehearsal, and the rollback disposition.

## Optional suggestions

### R1-F006 — Add sleep/wake and fallback-cadence reconciliation to M11's tests

Spec line 37 lists startup, watch overflow, **sleep/wake** and a **bounded fallback cadence** as reconciliation triggers. M11 tests overflow and restart only. Add a test in which a source changes while the coordinator is suspended or the watch is lost. The fallback cadence must pick up the change without a watch event.

### R1-F007 — Base hold expiry on persisted time, not monotonic deadlines

M10 uses monotonic deadlines for scheduling, but M07's provenance holds and their expiry survive restarts. State that hold expiry uses a persisted wall-clock or boundary basis, which a monotonic clock reset at reboot cannot provide. Add an expiry-across-restart case to `test_expired_hold_releases_no_usage`.

### R1-F008 — Carry forward the remaining small spec items

Spec line 29 says to "retire consumed wake records after reconciliation." Add a retirement assertion to M10 or M17. Spec line 43 says "a project can set a default driver." Include it in M06's registration contract, or record why it is deferred.

### R1-F009 — Name the native-binding approach under the zero runtime dependency budget

`pyproject.toml` declares `dependencies = []`. FSEvents, recursive inotify, Linux POSIX ACL xattrs, `RENAME_NOREPLACE`/`renameatx_np`/`RENAME_EXCHANGE`, and macOS peer credentials have no standard-library API. They need `ctypes`, following the precedent in `install.py` lines 167–192. FSEvents also needs a CFRunLoop or dispatch-queue thread. State this in M01, M02, M10 and M11 so the four-hour leaf estimates and the M11 split decision account for it.

## Decision

revisions-requested
