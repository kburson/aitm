# Multi-project agent usage monitor implementation plan

> **For agentic workers** Use `subagent-driven-development` or `executing-plans` after implementation authorization. Execute one accepted leaf at a time with its own verification and review. The checkboxes describe future work.

**Goal** Extend #83 into a single local monitor that measures concurrent registered projects, wakes parked Codex, Claude Code and Grok Build CLI sessions, and reports observed usage and estimated cost by project and story.

**Architecture** Normalize each eligible provider stream once. A user-scoped routing journal reserves each source-proven observation and hands it to a guarded project ledger. The acknowledged revisions and a separate recovery fence define what reports and exports can show. Native host adapters own filesystem, watcher and supervisor behavior.

**Tech stack** Existing Python 3.13+, standard-library SQLite, `uv`, `pytest` and Ruff. Keep the current runtime dependency budget. Use existing native interfaces through narrow OS adapters. Use a real systemd user manager and authenticated provider sessions for Linux qualification.

**Spec** [Accepted #100 specification](../design/multi-project-usage-monitor-design.md), published at `58773ac4d5ac7f2ccf41821d35c259facfe01619`, SHA-256 `1a5e9bb35335ab294bfc3c0d3a925bcd5eefc72d399fee52971842c6a1c241a9`. [Native XPR acceptance](../design/reviews/xpr-2026-11-09-monitor-spec/review-manifest.md).

**Evidence** [Grok #101](../../101/attachments/report.md) proves the whole-turn carrier on macOS Grok Build 1.0.77. [Linux #102](../../102/attachments/report.md) proves pinned Linux arm64 executables and selected kernel primitives in a container. Neither spike qualifies a production adapter or release. [#83 source](https://github.com/kburson/aitm/tree/f80f22645e2008c4cac9dc6e4003640bba976b5f/packages/aitm-usage) is the qualified usage baseline. The inspected trunk reference for this review is `58fb8ba98c52c1409f85c58d24dd7da86a583c0a`, which retains the usage implementation and adds the CI bootstrap. Re-pin live source, dependencies, branch policy and host builds at JIT.

**Status** Acceptance applies to an exact revision and is recorded in the story and review collateral. The leaves are planning units. Graduation, Develop, package installation and production cutover are separate decisions. Follow-on work stays under #100.

## Global constraints

- One active coordinator per OS user. Keep existing project UUIDs, keys, ledger histories and writer guards. Every accepted observation has at most one charged project. Discovery handles each authorized provider root once per reconciliation.
- Authenticate scope proposals and prove native order. Hook wakes are scheduling inputs. Repository text, timestamps, mutable working directories and ordinary cross-project markers cannot establish a handoff.
- Preserve raw paths only in approved private configuration. Use keyed provider references and fixed payload allowlists in state, diagnostics and exports. Treat a user account and its explicitly approved integrations as trusted.
- Keep project and story eligibility, observation identity, coverage and pricing independent. Preserve Unknown, exclude unqualified surfaces and charge each covered native observation once. Provider cost ticks, comparable API-equivalent USD, billed spend and quota are separate.
- Preserve byte-identical #83 as-of exports at the frozen legacy sequence and rate card. Gate versioned current output on exact project ACK and a durable independent recovery fence. Preserve immutable receiver identities and prior acceptance receipts.
- Target macOS Codex Desktop, Claude Code and Grok Build CLI. Qualify Linux Codex CLI, Claude Code and Grok Build CLI independently on arm64 and x86-64, systemd user manager and local ext4. macOS Codex CLI is outside the initial matrix. Release claims are limited to proven surfaces. Windows is later release work.
- Use forward-only commits on an authorized implementation branch. Retain raw native proof privately, publish sanitized receipts, and preserve #83 production until an independently approved cutover.

## Review focus

1. **Late conflicting handoff after ACK** must dispute the affected current span without moving historical charges. M07 covers native order. M09, M13 and M14 cover post-ACK dispute and frozen snapshots.
2. **Restore before an accepted export** must fence replay even when restored stores agree. M12 and M16 cover missing independent tails and interrupted export acknowledgement.
3. **A failed project at capacity** can stall a shared stream while independent healthy work proceeds. M09 and M10 cover cursor safety and bounded scheduling.
4. **Copied legacy or inherited Grok history** must never become a new charge. M05 and M16 cover fork lineage and reintroduced archives.
5. **Qualified hookless Grok beside an unqualified shared-root source** must show the correct interval and coverage, with no sibling or raw source data in an export. M04, M05, M13 and M17 cover this path.

## File ownership and sequencing

Paths below are relative to `packages/aitm-usage`. `S` means `src/aitm_usage/`, `T` means `tests/`. These are proposed exact file targets. If discovery changes an interface or file owner, update the plan and its dependent leaves before pickup.

| Leaf | Depends on | Owned surfaces |
| --- | --- | --- |
| M01 Host path security | — | `S/host_fs.py`, `S/ledger.py` path checks |
| M02 Atomic filesystem operations | M01 | `S/host_fs.py`, `S/scopes.py`, `S/service.py`, `S/export.py`, `S/backup.py`, `S/install.py` filesystem call sites |
| M03 Versioned project persistence | M02 | `S/monitor_types.py`, `S/types.py`, `S/ledger.py`, `S/backup.py`, `S/install.py`, `S/cli.py` schema and legacy dispatch |
| M04 Adapter contract and existing providers | M03 | `S/sources/adapter.py`, `S/sources/scan.py`, `S/sources/codex.py`, `S/sources/claude.py` |
| M05 Grok evidence adapter | M04 | `S/sources/grok.py`, `S/monitor_types.py`, `S/pricing.py`, `S/rates/` monitor resource and fixtures |
| M06 Registry and capture epochs | M04 | `S/monitor_registry.py`, `S/monitor_control.py`, `S/cli.py` operator registry commands |
| M07 Native scope and handoff | M06 | `S/monitor_scope.py`, `S/scopes.py`, `S/monitor_control.py`, `S/cli.py` scope, relationships and dispositions |
| M08 Service journal and claim order | M07 | `S/monitor_journal.py`, identity and reservation |
| M09 Project writes and ACK | M08 | `S/monitor_journal.py`, `S/monitor_writer.py`, `S/ledger.py` monitor application API |
| M10 Wake and park scheduler | M05, M09 | `S/monitor_scheduler.py`, `S/monitor_control.py`, `S/sources/hooks.py`, `S/cli.py` wake and park commands |
| M11 Root watches and coordinator | M05, M10 | `S/host_watch.py`, `S/monitor.py`, `S/service.py` coordinator entry |
| M12 Recovery and publication fence | M09 | `S/monitor_recovery.py`, witness and receiver delivery fencing |
| M13 Snapshot reports | M11, M12 | `S/monitor_report.py`, `S/monitor.py` publication, `S/rollup.py`, `S/cli.py` reports |
| M14 Compatible export and reconciliation | M13 | `S/export.py`, `S/monitor_report.py`, `S/cli.py` receiver reconciliation, receiver fixtures |
| M15 Host service lifecycle | M11, M14 | `S/install.py`, `S/host_service.py`, `S/cli.py` lifecycle |
| M16 Backup, legacy adoption and rollback | M12, M14, M15 | `S/backup.py`, `S/monitor_recovery.py`, `S/install.py`, `S/cli.py` migration |
| M17 Privacy and scale integration | M16 | `S/monitor.py` counters, integration fixtures and tests |
| M18 Native macOS qualification | M17 | `S/qualification.py`, `T/test_activation_receipt.py`, `README.md` macOS runbook |
| M19 Native Linux qualification | M18 | `S/qualification.py`, `T/test_activation_receipt.py`, `README.md` Linux runbook |

The #101 and #102 evidence is an input to M04, M05, M15 and M19. Keep a leaf within four implementation agent-hours at JIT. M04, M11, M15, M16 and M19 may need further splitting once exact native capabilities and host access are confirmed. Preserve the dependency order if split. Record the declared target, latest compatible parent revision, read/write paths, evidence prerequisites, bounded estimate, closure owner and required validation for each leaf before pickup. Designate a separate integration target before any work that cannot land dormant. The table serializes shared-file edits. M05 can proceed alongside M06–M09, and M12 can proceed alongside M10–M11 once M09 is accepted.

## Verification convention

Run unit leaves from the implementation checkout with `uv run --project packages/aitm-usage --locked pytest -q packages/aitm-usage/tests/<named-file>`. A red run must fail on the new assertion or missing interface. A green run must pass that file plus the named related tests. Run `uv run --project packages/aitm-usage --locked ruff check packages/aitm-usage`, `uv run --project packages/aitm-usage --locked ruff format --check packages/aitm-usage` and `git diff --check` before each scoped commit. For a leaf with an applicable hosted lane, bind its result to the exact candidate and tested base. Record missing or incomplete lanes explicitly and apply the accepted story gates. Follow the [manual delivery checklist](../../../../manual-delivery-checklist.md). A hosted check does not replace native platform receipts. Keep the versioned, deterministic fixtures separate from host qualification receipts. Replace `<named-file>` with the concrete `T` file shown under the leaf.

## Legacy command surface after adoption

M03 uses distinct argparse destinations for global `--project STATE_DIR` and subcommand `--project UUID`, respectively `legacy_state_dir` and `project_id`. Only legacy handlers require a state directory. Reject mixed forms. Resolve an adopted state directory through the private registry and verify its pinned identity. Before adoption, legacy commands retain existing behavior.

| Legacy entry point | Owner and adopted behavior |
| --- | --- |
| `scope mark` and `development bind` | M07 preserves the exact #83 invocation and native receipt. The upgraded CLI queues through the admitted compatibility command path. M04 and M11 retain the recognizer and verify the next native boundary and owner proof before applying. |
| `scope correct`, `item alias` and `item parent` | M07 admits these through the same path with existing authority and versioned changes. M11 drains them and M13 pins applied scope and relationship revisions. |
| `register` and `source add-anchor` | M06 refuses mutation for adopted state with `project-adopted-use-monitor`. Use monitor registration and owner-approved source or anchor controls. |
| `collect-once`, all legacy `service` actions, `backup`, `restore` and `qualify` | M15 and M16 refuse these for adopted state with `project-adopted-use-monitor`. Use coordinated lifecycle, backup/restore and qualification. M03 proves the older binary refuses migrated schema even when stopped. |
| `status`, `rollup` and `export` | M13 maps read-only status and refuses unfenced rollup with the replacement report route. M14 preserves legacy export only at the frozen sequence or earlier and its legacy rate card. Current export uses the fenced monitor view. |

M09 retains every attached adopted project’s original writer guard throughout coordinator custody, including between transactions. M16 records the exact accepted or pending command manifest at the final checkpoint under the writer guard and inbox publication lock. Freeze legacy ingress at that boundary. Transfer pending command envelopes with original receipt IDs, replay once in order and reprove native boundaries. A legacy command cannot acknowledge a queue write unless an admitted monitor path can consume it. Make the upgraded CLI route available to existing workflows at cutover.

## Native acceptance case NA-1

M17 mirrors NA-1 deterministically. M18 and M19 exercise it with real overlapping Codex, Claude Code and Grok Build CLI sessions on each claimed target. Use two repositories with the same issue number and at least two checkouts for one project. Exercise driver, reviewer and researcher roles. Prove a cross-project handoff with a dependency and zero cost rollup across that edge. Include an unmarked review, project-wide work, an ambiguous project claim, and a valid ordinary marker for A in B’s registered checkout. Prove the ordinary conflict stays outside both totals before a prospective authorized handoff. Mix a qualified and an unqualified source in one approved root and verify a sanitized gap with zero usage from the unqualified source. On macOS use a real Codex CLI rollout alongside Desktop. On Linux include an actual unsupported client version or surface from the same approved root alongside the real qualified client sessions. Reconcile direct and inclusive totals and verify zero duplicate project charges. A receipt without each named outcome cannot qualify the target.

## Implementation leaves

### M01. Host path security

**Files** Create `S/host_fs.py` and `T/test_host_fs_security.py`. Modify private-path validation and per-user guard location in `S/ledger.py`.

**Contract** `check_private_acl(target: Path | int, *, ancestor: bool = False) -> None` and `account_control_root(uid: int) -> Path` in `host_fs`. Keep Darwin ancestry rules and POSIX fd-relative checks. Use checked ctypes where the standard library lacks native ACL bindings. On Linux inspect access and default ACLs separately and use a stable UID-resolved account root independent of environment overrides.

- [ ] Write `test_private_acl_rejects_linux_default_acl_and_unknown_enforcement`, `test_pinned_path_rejects_symlink_and_wrong_owner` and `test_uid_guard_ignores_home_override`. Assert `0700` with a permissive default ACL fails and an unavailable ACL capability refuses state admission.
- [ ] Run the named file to show red. Implement the checked OS boundary and run green with `test_ledger.py`. Exercise real ACL enforcement on the qualified Linux volume. Commit only M01 paths.

### M02. Atomic publication and restore operations

**Files** Extend `S/host_fs.py` and add `T/test_host_fs_publication.py`. Move native call sites in `S/scopes.py`, `S/service.py`, `S/export.py`, `S/backup.py` and `S/install.py` onto it.

**Contract** `publish_noreplace(src_dir: int, src: str, dst_dir: int, dst: str) -> bool` and `exchange_entries(src_dir: int, src: str, dst_dir: int, dst: str) -> None`. Keep exclusive file and directory publication, collision replay, atomic restore exchange and parent directory fsync. Probe `RENAME_EXCHANGE` separately because #102 exercised `RENAME_NOREPLACE` only.

- [ ] Write `test_existing_destination_survives_noreplace`, `test_directory_exchange_and_durability` and `test_unsupported_primitive_fails_without_replacement`. Assert EEXIST preserves both inode identities and a refused exchange leaves the original store intact.
- [ ] Run red. Wire native Darwin and Linux operations through checked ctypes bindings. Run green with `test_scopes.py`, `test_export.py` and `test_install.py`, including real supported filesystem runs. Commit M02.

### M03. Versioned project persistence

**Files** Create `S/monitor_types.py` and `T/test_monitor_ledger_version.py`. Extend version checks and serializers in `S/ledger.py` and `S/types.py`. Update format selection in `S/backup.py`, installer probes in `S/install.py` and CLI dispatch separation in the same leaf.

**Contract** `Ledger.upgrade_monitor_schema(expected_sequence: int) -> LedgerIdentity` and `Ledger.monitor_as_of(sequence: int) -> MonitorLedgerView`. Use the existing transaction sequence and append-only revision storage with an explicitly versioned monitor payload. Keep legacy decoding separate and retain `Ledger.as_of` and the legacy renderer for frozen views. Make the new runtime open and verify legacy and monitor schemas and their respective backup formats. Validate the declared version against its own schema fingerprint and legacy serialization, including installer probes. Bump the database schema version only under the guarded, rehearsed M16 migration. M03 supplies compatibility without invoking migration in production. Carry native host surface, normalized time basis, coverage and optional provider cost separately.

- [ ] Write `test_schema_upgrade_preserves_legacy_identity_and_export_bytes`, `test_old_binary_refuses_monitor_schema`, and `test_mixed_or_interrupted_upgrade_rolls_back`. Assert the legacy snapshot and key are unchanged and a stale expected sequence refuses migration. Add `test_new_runtime_accepts_unmodified_legacy_store_backup_and_installer_probe`. An old runtime refuses a migrated store without writing. `test_legacy_global_state_and_report_project_uuid_are_separate` covers both invocation forms and their mixed-form refusal.
- [ ] Run red. Implement versioned dispatch and transactional upgrade. Run green with `test_ledger.py`, `test_export.py` and `test_install.py`. Commit M03.

### M04. Adapter contract and Codex or Claude bridge

**Files** Create `S/sources/adapter.py` and `T/test_monitor_adapters.py`. Adapt `S/sources/{scan,codex,claude}.py` without rewriting proven token and marker logic.

**Contract** `ProviderAdapter.discover(root: SourceRoot) -> Iterable[SourceLocator]` and `ProviderAdapter.read_delta(locator: SourceLocator, cursor: StreamCursor | None) -> AdapterBatch`. `AdapterBatch` contains verified native lineage, boundary, time basis, usage revision, project context and diagnostics. The adapter declares a qualified host, client version and format tuple. Derive keyed service identity from verified lineage before choosing a project key. Keep transcript content transient and discard anything outside the field allowlist.

- [ ] Write `test_desktop_and_cli_in_shared_root_admit_only_qualified_surface`, `test_codex_archive_counter_epoch_replays_once`, and `test_claude_streamed_revision_and_nested_overlap`. Assert an unqualified macOS CLI rollout contributes zero with a sanitized coverage reason. Retain Desktop native receipt and Claude linked-request proof.
- [ ] Before fixing the interface or enabling a host surface, obtain a controlled native receipt, its adjoining request and durable cursor evidence for that surface. Explicitly prove the Linux Codex CLI carrier independently of Desktop and the Linux Claude Code request link. Record exact client and format. If a carrier is unavailable, split its M04 adapter slice at JIT, keep that surface disabled, and make the corresponding M19 qualification depend on the accepted slice. Run red. Implement the contract around the current collectors and add the verified receipts as sanitized fixtures. Run green with `test_scan.py`, `test_codex.py` and `test_claude.py`. Commit M04.

### M05. Grok whole-turn adapter

**Files** Create `S/sources/grok.py`, `T/test_grok.py` and allowlisted fixtures under `T/fixtures/grok/`. Extend the monitor-only provider/model enums and Grok payload in `S/monitor_types.py` with provider ticks and normalized cache categories. Generalize provider-specific rate validation in `S/pricing.py` and add a versioned monitor rate resource under `S/rates/`. Keep legacy decoder types, `2026-11-09.json`, its default and RateBasis digest unchanged. Grok fields enter only the versioned monitor export.

**Contract** `GrokAdapter.read_delta(locator: SourceLocator, cursor: StreamCursor | None) -> AdapterBatch`. Match a durable native `turn_completed` to a verified prompt lineage. Use completion time, validate persisted and headless token semantics separately, and use the snapshot for corroboration. A snapshot-only row, an incomparable native revision and unresolved overlap cannot create an attributable charge. Preserve Unknown API-equivalent pricing when the rate basis is missing.

- [ ] Write `test_resume_and_snapshot_replay_count_two_distinct_turns`, `test_hookless_eligible_completion_keeps_native_interval`, `test_fork_excludes_inherited_turns`, `test_late_folded_parent_never_adds_to_child`, and `test_snapshot_conflict_and_cache_categories`. Also add `test_complete_native_only_counts_with_corroboration_gap` and `test_snapshot_only_does_not_charge`. Add `test_grok_rate_classes_do_not_use_claude_defaults`, `test_unknown_grok_rate_and_provider_ticks_remain_separate`, and `test_grok_preserves_legacy_rate_digest_and_fixed_export`. Verify the v1 decoder refuses a Grok provider value. Cover cancellation, concurrent prompts, rewind, later append and copied history as gated fixture cases.
- [ ] Pin the approved production scope-marker carrier with a controlled native capture before finalizing the Grok contract. #101 is the macOS feasibility baseline. If the Linux carrier is unavailable, assign the remaining implementation to an explicit M05 slice required by M19 and keep that surface disabled. Run red. Implement versioned native decoding and separate rate provenance. Run green with `test_accounting.py`. Commit M05. Later qualification proves actual receipt authority on every advertised host.

### M06. Explicit registrations and capture epochs

**Files** Create `S/monitor_registry.py`, `S/monitor_control.py` and `T/test_monitor_registry.py`. Extend `S/cli.py` with `monitor project register --config FILE`, `monitor source approve --config FILE`, `monitor project anchor add --project UUID --config FILE`, `monitor capture enable|disable --project UUID --source ID` and `monitor command status --id ID`.

**Contract** `Registry.register_project(request: ProjectRegistrationRequest) -> RegisteredProject` and `Registry.set_permission(change: CaptureChange, boundary: VerifiedBoundary) -> CaptureEpoch`. Store owner-approved roots and project-to-provider permission edges outside Git. Resolve physical anchors and reject cross-project identical or nested anchors. A project’s immutable identity survives display-name and remote changes. Store an optional default driver per project and enforce the adopted legacy registry refusals. Preserve per-stream enrollment, disable and re-enable boundaries. `ControlInbox.enqueue(command: ControlCommand) -> ControlReceipt` stores owner-authorized commands with stable request IDs in a private inbox. Only the monitor writer applies them after validation. Bootstrap registration before activation uses the same command contract under the coordinator lease, and an enqueue receipt does not claim the boundary was applied.

- [ ] Write `test_two_clones_share_identity_but_nested_foreign_anchor_fails`, `test_disable_reenable_excludes_late_disabled_interval` and `test_revoked_root_is_not_reread_for_prior_revision`. Assert pre-disable admitted work can settle where authorized, a crossing unsplittable span is a gap, and re-enable cannot backfill the disabled interval.
- [ ] Run red. Implement registration and epoch matching, then run green with `test_scan.py`. Test exact command retries and the distinction between queued and applied status. Commit M06.

### M07. Authenticated scope, handoff and proof holds

**Files** Create `S/monitor_scope.py` and `T/test_monitor_scope.py`. Extend verified marker and owner-binding reuse in `S/scopes.py` and proposal admission in `S/monitor_control.py`. Add `monitor scope mark|handoff|dispose --request FILE` in `S/cli.py`.

**Contract** `resolve_route(observation: NativeObservation, registry: RegistryView, scopes: ScopeView) -> RouteDecision` and `ScopeState.apply_handoff(command: Handoff, receipt: VerifiedBoundary) -> HandoffDisposition`. Validate authority, exact before-boundary generation and next native boundary. A valid ordinary marker contradicting a registered anchor holds both totals. A dedicated handoff may override only the verified stale anchor lineage. Keep bounded provenance-only replay holds with expiry and explicit gaps. Scope proposals submitted through the M06 command envelope must name the registered integration or operator authority and join the corresponding native marker before admission. A queued command is never proof of scope.

- [ ] Write `test_foreign_ordinary_marker_conflicts_then_prospective_handoff_routes`, `test_handoff_A_to_B_to_C_with_retained_A`, `test_competing_receipts_conflict_in_both_native_delivery_orders` and `test_expired_hold_releases_no_usage`. Return the bounded affected observation lineage and scope span. M09 and M13 test the post-ACK published transition. Persist hold expiry on a UTC basis and verify expiry across restart. Test the legacy scope and relationship command path with exact receipt shapes and idempotent queue IDs. Test a development owner lacking destination worktree proof.
- [ ] Run red. Implement evidence-backed routing and hold dispositions. Run green with `test_scopes.py`. Commit M07.

### M08. Single-owner journal and verified revision order

**Files** Create `S/monitor_journal.py` and `T/test_monitor_journal.py`.

**Contract** `RoutingJournal.reserve(candidate: RoutedRevision, progress: StreamCursor) -> ClaimDisposition`. Take a stable per-user coordinator lease. In one transaction reserve the canonical observation’s only project and retain normalized pending revision and replay cursor. A causal successor can supersede the current revision. Identical or proven older revisions have no additive effect. Incomparable content becomes disputed. `RoutingJournal.record_disposition(change: VerifiedRouteDisposition) -> JournalChange` records a causal scope conflict, coverage change or folded-usage replacement against the affected keys. Preserve prior views. A superseding covering representation and the withdrawal of its children must share a single publication change.

- [ ] Write `test_competing_project_claims_cannot_double_charge`, `test_causal_revision_survives_stale_replay_after_restart` and `test_reservation_and_cursor_commit_together`. Assert provider archive copies keep one canonical key, a distinct verified retry keeps its own key, and an injected rollback leaves no partial claim or cursor movement.
- [ ] Run red. Implement private keyed journal and lease. Run green with `test_ledger.py`. Commit M08.

### M09. Guarded destination writes and ACK

**Files** Create `S/monitor_writer.py` and `T/test_monitor_delivery.py`. Extend `S/monitor_journal.py` and `S/ledger.py`.

**Contract** `ProjectDelivery.commit(claim: PendingClaim) -> ProjectWriteReceipt` and `RoutingJournal.ack(receipt: ProjectWriteReceipt) -> PublicationCandidate`. Reuse stable project pseudonyms and guarded transactions. `ProjectDelivery.attach(ledger: Ledger) -> WriterCustody` retains the original guard through coordinator attachment. M16 recognizes a late legacy revision only by verifying native lineage against the existing row with the adopted #83 project key and request-key algorithm. Bind the matching service claim to that original project. A project pseudonym alone cannot seed a service claim. Both operations compare exact lineage and revisions. Bound pending capacity per destination. A failed destination keeps pending state and backpressure for its shared stream. Reserve progress capacity for independent healthy streams. `RoutingJournal.publication_candidate(change: JournalChange) -> PublicationCandidate` creates a view change for a verified journal-only dispute or coverage event without inventing a project write ACK. A folded parent replaces eligible published children only after its actual write ACK and then in one publication candidate.

- [ ] Write `test_restart_at_reserve_commit_and_ack_yields_one_row`, `test_stale_ack_never_rewinds_publication`, and `test_full_destination_queue_preserves_independent_progress`. Add `test_late_conflict_after_ack_produces_dispute_without_new_write` and `test_folded_replacement_and_child_withdrawal_share_view`. Assert a blocked stream’s cursor remains replayable and settlement after recovery preserves two distinct project scopes.
- [ ] Run red. Implement guarded delivery and bounded dispositions. Run green with `test_monitor_journal.py` and `test_ledger.py`. Commit M09.

### M10. Private wake ingress and parked-session scheduling

**Files** Create `S/monitor_scheduler.py` and `T/test_monitor_scheduler.py`. Add wake ingress to `S/monitor_control.py`, approved provider producers in `S/sources/hooks.py` and `monitor park --session-ref ID` and `monitor hooks install --project UUID --provider ID` in `S/cli.py`.

**Contract** `Scheduler.notify(hint: WakeHint) -> None` and `Scheduler.take_due(now: float, limit: int) -> tuple[WorkItem, ...]`. Use a same-user Unix socket inside the pinned private state directory for wake ingress. Reject a mismatched peer UID, bounded-message violations and unauthorized source locators. Resolve raw locators transiently and return a nonblocking best-effort result so a failed wake cannot stall a provider. Persist only allowlisted keyed hints. Coalesce by native provider, session and verified turn where available. Apply Active, Settling and Parked as scheduling states. Explicit park carries no workflow or scope authority. `HookSender.notify(event: HookEvent) -> WakeDisposition` publishes bounded best-effort signals. The installer verifies owner approval and the pinned provider surface. Use an owned Codex user-local plugin in its private provider home, an owned Claude Code hook entry in user-local settings, and an owned Grok Build file in the private Grok user hooks directory. Filter out unauthorized context before persistence. Preserve foreign hooks and native trust. The installed launcher resolves approved private settings itself. Embed no checkout, state or socket path in the command and change no tracked repository files. M10 tests and M15 rehearsal use isolated provider homes. Use checked ctypes for peer credentials where required. [Codex plugins](https://developers.openai.com/plugins/build/plugins) · [Claude Code settings](https://code.claude.com/docs/en/settings) · [Grok hooks](https://docs.x.ai/build/features/skills-plugins-marketplaces#hooks) The Grok scope producer uses the qualified M05 prompt-scoped carrier to carry an M07 authorized marker proposal. The adapter joins it to a durable completion. A wake sender alone has no marking authority. Keep fairness when another project is blocked.

- [ ] Write `test_park_final_catchup_then_late_write_reopens`, `test_stale_stop_cannot_park_newer_turn`, and `test_duplicate_and_missing_hooks_keep_idempotent_progress`. Verify concurrent turns, resume, retained cursors and bounded quiet backoff. A lost or refused wake must allow the provider to proceed and leave native reconciliation able to recover. Test an approved install with unchanged tracked files, consumed wake retirement and explicit park without scope change.
- [ ] Run red. Implement the scheduler using monotonic deadlines and bounded work units. Run green with `test_monitor_delivery.py`. Commit M10.

### M11. Shared root watchers and coordinator

**Files** Create `S/host_watch.py`, `S/monitor.py` and `T/test_monitor_watches.py`. Add coordinator entry in `S/service.py` while keeping the old service interface available for rehearsal and rollback.

**Contract** `WatchSet.events(timeout: float) -> tuple[WatchEvent, ...]` and `Monitor.run_once(now: float) -> MonitorCycle`. Use checked ctypes bindings for Darwin FSEvents on a dedicated run-loop thread and Linux recursive inotify behind the same boundary. Include native resource ownership in the JIT split decision. Enroll new directories, invalidate stale locators after rotation, and request bounded metadata-first reconciliation after overflow or restart. Discover each authorized root once and reread only changed or due streams. Drain queued control commands through the coordinator, join scope proposals to native receipts before applying them, and return queued, applied or refused status. Exercise register, mark, handoff, dispose and park through their CLI paths, including a mismatched receipt and an unauthorized scope proposal.

- [ ] Write `test_watch_overflow_and_nested_rotation_reconcile`, `test_shared_root_enumerates_once_for_many_projects`, and `test_unchanged_parked_payload_is_not_read`. Verify a changed parked source wakes independently and a lost root becomes a coverage gap. Write during suspend or watch loss and recover on wake or bounded fallback without a queued event.
- [ ] Run red. Integrate scheduler, discovery, route decisions and guarded delivery. Run green with `test_monitor_scheduler.py`, `test_scan.py` and real watch probes. Commit M11.

### M12. Independent recovery and publication fence

**Files** Create `S/monitor_recovery.py` and `T/test_monitor_recovery_fence.py`.

**Contract** `RecoveryFence.protect(candidate: PublicationCandidate) -> FencedPublication` and `RecoveryFence.record_export_intent(delivery: ReceiverDelivery) -> ExportIntent`. Durably append the monotonic tail and authenticated decision digests before exposing a report view or sending an export. Keep the tail outside rollback snapshots. Prepared but interrupted publication can block replay without asserting it was exposed. Add `RecoveryFence.record_receiver_evidence(intent: ExportIntent, evidence: VerifiedReceiverEvidence) -> ReceiverDisposition`. Bind the intent and independently verified receipt or absence to the receiver identity, immutable key and payload digest. Record accepted or retry-eligible outcomes durably. Unknown or conflicting evidence remains held. A retry after verified absence must use the same receiver, key and bytes.

- [ ] Write `test_view_cannot_escape_before_recovery_fsync`, `test_restore_with_only_old_witness_holds_replay`, and `test_interrupted_export_requires_receiver_reconciliation`. Inject failure before and after persistence. Assert replay stops at the last proven common boundary when the current witness is missing.
- [ ] Run red. Implement durable write-ahead witness and recovery verification. Run green with `test_monitor_journal.py` and `test_monitor_delivery.py`. Commit M12.

### M13. Pinned project and story reports

**Files** Create `S/monitor_report.py` and `T/test_monitor_report.py`. Connect the fence to the coordinator in `S/monitor.py`, and reuse relationship and rollup logic in `S/rollup.py`. Add CLI `report projects` and `report stories --project UUID --snapshot ID` in `S/cli.py`.

**Contract** `ReportReader.projects(window: ReportWindow, rates: RateBasis) -> ProjectSummary` and `ReportReader.stories(project_id: UUID, snapshot_id: str) -> StoryBreakdown`. `Monitor.publish(candidate: PublicationCandidate) -> FencedPublication` must protect the candidate with M12 before making it visible to `ReportReader`. `PublishedViewStore.open(snapshot_id: str) -> PublishedView` reopens a durable manifest keyed by the fenced snapshot. Pin its journal view, ledger sequences, acknowledged revisions and scope history. `SnapshotToken.issue(publication: PublicationID, window: ReportWindow, rates: RateBasis) -> str` uses a versioned, authenticated read-only token binding the exact publication ID, canonical UTC interval, rate card digest and pricing basis. Summary issues the token without persisting new state. Drilldown verifies it and loads the retained publication and exact pricing inputs. Return unavailable if a pinned input expired and refuse malformed tokens. Keep unacknowledged undisputed changes on the previous visible revision. Refuse unfenced CLI rollup for adopted projects and direct users to the new report. Keep status read-only and legacy export confined to its frozen sequence and rate card. Expose the legacy baseline without synthetic ACKs. Use the declared native observation time basis and preserve legacy times. Direct totals reconcile to distinct stories, drafts, project-wide work and unattributed story scope.

- [ ] Write `test_snapshot_pins_scope_time_and_rates_across_commands`, `test_project_totals_reconcile_without_inclusive_epic_double_count` and `test_partial_unknown_and_hookless_grok_visibility`. Verify a time correction moves only a new snapshot and a missing historical view returns explicit unavailable. Assert an ACK alone is invisible through the CLI when the coordinator cannot persist the fence. Issue summaries for two intervals over one publication and a third after a rate-card update without a new usage write. Reopen all three from a separate process after restart. Require exact original window and price or explicit unavailable if a pinned input expired. Verify a late post-ACK dispute removes current usage while the previous report stays identical.
- [ ] Run red. Implement read-only local reporting with structured JSON. Run green with `test_rollup.py` and `test_monitor_recovery_fence.py`. Commit M13.

### M14. Versioned exports and immutable receiver compatibility

**Files** Extend `S/export.py` and `S/monitor_report.py`. Add `monitor receiver status --intent ID` and `monitor receiver reconcile --intent ID --evidence FILE` in `S/cli.py`. Add `T/test_monitor_export.py` and extend the receiver fixture in `T/fixtures/receiver.py`.

**Contract** `export_monitor_project(view: PublishedView, project_id: UUID, destination: Path) -> MonitorExportReceipt` and `compatible_delivery(view: PublishedView, receiver: ReceiverState) -> CompatibleDelivery`. Keep legacy `export_as_of` deterministic. Emit normalized monitor rows under a separate schema. Preserve Core-compatible original identity and receipt. Put changed immutable payloads into an explicit reconciliation queue instead of resending them. Use an approved receiver verification adapter to authenticate receipt or absence and feed M12’s exact-intent disposition. Refuse an unverified operator file. Persist the reconciliation disposition and original acceptance receipt. The fixture exercises this protocol until a real approved receiver exists. C44 itself remains separate.

- [ ] Write `test_legacy_export_bytes_remain_fixed`, `test_pending_and_disputed_rows_are_excluded_from_compatible_export`, and `test_time_correction_after_receiver_acceptance_never_reuses_key_or_charges_twice`. Add `test_accept_then_crash_resolves_receipt_or_retries_identical_after_absence`. Verify report and export use the same fenced revision and privacy allowlist, and test that a post-ACK dispute excludes the span without changing the previous view.
- [ ] Run red. Implement projection, export intent and receiver replay semantics. Run green with `test_export.py`, `test_rollup.py` and `test_monitor_recovery_fence.py`. Commit M14.

### M15. Single per-user supervisor on macOS and Linux

**Files** Create `S/host_service.py` and `T/test_monitor_install.py`. Extend `S/install.py` and `S/cli.py` lifecycle commands. Preserve the original LaunchAgent identity until guarded adoption. M15 permits isolated candidate rehearsal and a write-disabled readiness probe. Test each adopted legacy mutation refusal with no direct write or lifecycle change, including collect-once and restore between monitor transactions. The production activation path refuses without the M16 cutover receipt and exact target qualification.

**Contract** `Supervisor.install(runtime: VerifiedRuntime, state: MonitorState) -> ServiceReceipt` and `Supervisor.verify(expected: ServiceReceipt) -> ServiceHealth`. Register one per-user LaunchAgent or systemd user unit. Verify loaded definition, exact executable and same-user process incarnation plus a fresh matching heartbeat. Enable within the user manager. Report absent manager and operator-controlled lingering separately. Refuse unsupported filesystem and insecure state before activation.

- [ ] Write `test_second_service_and_legacy_writer_refuse_activation`, `test_stale_pid_and_heartbeat_do_not_certify_readiness`, and `test_no_systemd_user_bus_and_unapproved_linger_are_explicit`. Exercise isolated install, stop and restart using controlled manager fixtures.
- [ ] Run red. Implement supervisor selection and exact-runtime evidence. Run green with `test_install.py` and `test_service_process.py`. Commit M15. Real OS proofs occur in M18 and M19.

### M16. Coordinated backup, legacy adoption and rollback

**Files** Extend `S/backup.py`, `S/monitor_recovery.py`, `S/install.py` and `S/cli.py`. Add `T/test_monitor_cutover.py`.

**Contract** `capture_monitor_backup(store: MonitorStore, destination: Path) -> MonitorBackupReceipt` and `adopt_legacy(request: LegacyAdoption, receipt: MonitorBackupReceipt) -> LegacyBaseline`. Back up the journal, keys and ledger vector with pending routes. Verify the separate current recovery tail. Adopt the existing UUID, key, cutoff and ledger sequence under the original writer guard. Fence new projects behind proven enrollment baselines and reconcile provider activity during stop exactly once. `CutoverController.activate(request: ApprovedCutover, qualification: TargetQualification) -> ActivationReceipt` owns the ordered sequence. Confirm exact runtime and target qualification, verify independent recovery currentness, capture and verify the legacy backup, stop legacy collection, acquire the original guard, confirm the final checkpoint and frozen export, then verify the rollback bundle matches that stopped checkpoint. If the legacy writer advanced after backup, capture and verify a matching replacement bundle under the guard or refuse before schema migration. Record and transfer exact pending legacy commands and freeze ingress, then adopt the schema under the guard and verify the replacement in write-disabled readiness mode. Install production hooks only within the authorized cutover. Rollback removes exact owned hook entries and preserves foreign changes. If an owned entry cannot be safely removed, prove it inert under legacy service and record it. Enable writes only after the authorized cutover receipt binds those results. Before enabling writes, persist the adopted project ledger identities, head sequences and journal checkpoint as the rollback fence. Recovery checks the guarded durable project and journal state against that fence. A project commit beyond the fence is a write even if ACK or a separate marker was interrupted. Restore and restart legacy only when the absence of new durable usage writes and publication is proven. If a write exists or absence cannot be verified, preserve the state and require proven compatible rollback or forward recovery. A portable restore needs independently authenticated current-tail evidence outside the restored material.

- [ ] Write `test_cutover_first_report_and_fixed_export_parity`, `test_copied_pre_cutover_archive_cannot_reach_other_project`, `test_older_backup_before_handoff_and_accepted_export_holds_or_reconciles`, and `test_reversible_prewrite_failure_and_postwrite_forward_recovery`. Add `test_legacy_write_between_backup_and_stop_survives_cutover_failure` and `test_first_project_commit_without_ack_prevents_legacy_restore`. Add `test_pending_legacy_commands_apply_once_and_native_mark_remains_live`, `test_post_cutover_revision_updates_legacy_row_once`, `test_codex_counter_epoch_continues_across_cutover` and `test_legacy_restore_leaves_owned_hooks_removed_or_inert`. Verify frozen export bytes after each continuity case. Ambiguous lineage, mixed generations, missing independent tail and unverifiable post-fence state fail closed.
- [ ] Run red. Implement dry-run validation, staged restore and adoption checks. Rehearse on copied representative #83 state, including rollback before new writes and recovery of pending routes. Run green with `test_monitor_recovery_fence.py`, `test_install.py` and `test_export.py`. Commit M16.

### M17. Cross-project privacy, saturation and scale proof

**Files** Create `T/test_monitor_integration.py` and allowlisted two-project fixtures under `T/fixtures/monitor/`. Add sanitized work counters in `S/monitor.py` only where the verification needs them.

- [ ] Write `test_two_projects_same_issue_distinct_routes_and_three_roles`, `test_sentinel_secrets_never_persist_or_cross_export`, and `test_two_active_and_fifty_parked_with_one_changed_source` and `test_hookless_grok_beside_unqualified_shared_root_source_exports_no_sibling_data`. Include all NA-1 outcomes. Check actual persisted wake, hold, journal, witness, ledger, report and export data against field allowlists. Assert no unapproved path, raw provider ID or sibling identity in the emitted artifacts and no unapproved raw path in repository-visible files. Measure zero unchanged parked payload reads over a healthy reconciliation and constant root discovery count as project count increases.
- [ ] Run red if the proof finds a gap and return the fix to the owning leaf before continuing. Run all locked tests and Ruff. Capture workload read counts, latency, CPU and memory. Record release budgets from evidence. Commit M17 evidence and tests.

### M18. Controlled macOS qualification

**Files** Extend `S/qualification.py`, `T/test_activation_receipt.py` and `README.md`. Retain sanitized evidence outside the product checkout until the declared delivery step.

- [ ] Add receipt validation `test_monitor_mac_receipt_requires_exact_provider_and_service_proof`. It rejects wrong builds, insufficient overlap, a stale heartbeat, missing production scope-carrier proof or any missing NA-1 outcome. Run red, implement and run green with the activation and installer tests.
- [ ] Run on an isolated candidate with actual Codex Desktop, Claude Code and Grok Build CLI. Run NA-1 and the exact legacy marker invocation against adopted state. Verify a parked resume with two distinctly story-bound Grok turns through production admission, late writes, a separately eligible hookless Grok completion counted once in its interval without a story, fork and folded overlap, one LaunchAgent, crash catch-up and fixed #83 export parity. Keep private raw traces and publish only a sanitized receipt. Commit M18.

### M19. Controlled Linux qualification and delivery gate

**Files** Extend `S/qualification.py`, `T/test_activation_receipt.py` and `README.md` after M18.

- [ ] Add `test_linux_receipt_requires_user_manager_ext4_native_receipts_and_arch` and `test_container_evidence_cannot_satisfy_linux_activation`. Reject any missing NA-1 outcome per target. Run red, implement and run green.
- [ ] Reproduce #102 credential-free checks on arm64 and x86-64. On each real supported target, verify authenticated Linux-native receipt and cursor continuity on Codex CLI, Claude Code and Grok Build CLI. On each architecture require two distinctly story-bound Grok turns through production admission across resume and a separate hookless eligible Grok turn counted once in its interval without a story. Prove user-manager startup, logout, allowed headless persistence, exact unit/process heartbeat, recursive watch overflow, crash replay, safe restore and qualified atomic operations on ext4. Run the complete NA-1 case and capture release receipts per target.
- [ ] Run the full locked suite and Ruff on the release candidate. Confirm the documented supported matrix matches actual receipts. Keep unqualified surfaces out of support claims. A production installation needs a separately authorized cutover with an explicit rollback or forward-recovery decision. Commit M19 and submit the integrated package for the project’s applicable review and delivery gates.

## Coverage map and review handoff

The plan covers registration and authority (M06–M07), providers (M04–M05, M18–M19), routing and durable replay (M08–M12), reporting and compatibility (M13–M14), host state and lifecycle (M01–M03, M15), migration (M16), and privacy and scale (M17). The fixed test commands use the existing package location and locked environment. Provider, rate-card, architecture, host access and service authority evidence must be reconfirmed at JIT. Review this draft against the accepted spec before decomposing work into issue IDs.
