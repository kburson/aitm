# Multi-project agent usage monitor implementation plan

> **For agentic workers** Use `subagent-driven-development` or `executing-plans` after implementation authorization. Execute one accepted leaf at a time with its own verification and review. The checkboxes describe future work.

**Goal** Extend #83 into a single local monitor that measures concurrent registered projects, wakes parked Codex, Claude Code and Grok Build CLI sessions, and reports observed usage and estimated cost by project and story.

**Architecture** Normalize each eligible provider stream once. A user-scoped routing journal reserves each source-proven observation and hands it to a guarded project ledger. The acknowledged revisions and a separate recovery fence define what reports and exports can show. Native host adapters own filesystem, watcher and supervisor behavior.

**Tech stack** Existing Python 3.13+, standard-library SQLite, `uv`, `pytest` and Ruff. Keep the current runtime dependency budget. Use existing native interfaces through narrow OS adapters. Use a real systemd user manager and authenticated provider sessions for Linux qualification.

**Spec** [Accepted #100 specification](../design/multi-project-usage-monitor-design.md), published at `58773ac4d5ac7f2ccf41821d35c259facfe01619`, SHA-256 `1a5e9bb35335ab294bfc3c0d3a925bcd5eefc72d399fee52971842c6a1c241a9`. [Native XPR acceptance](../design/reviews/xpr-2026-11-09-monitor-spec/review-manifest.md).

**Evidence** [Grok #101](../../101/attachments/report.md) proves the whole-turn carrier on macOS Grok Build 1.0.77. [Linux #102](../../102/attachments/report.md) proves pinned Linux arm64 executables and selected kernel primitives in a container. Neither spike qualifies a production adapter or release. [#83 source](https://github.com/kburson/aitm/tree/f80f22645e2008c4cac9dc6e4003640bba976b5f/packages/aitm-usage) is the inspected implementation baseline. Re-pin live source, dependencies and host builds at JIT.

**Status** Draft for plan review. The proposed leaves are planning units. Graduation, Develop, package installation and production cutover are separate decisions. Follow-on work stays under #100.

## Global constraints

- One active coordinator per OS user. Keep existing project UUIDs, keys, ledger histories and writer guards. Every accepted observation has at most one charged project. Discovery handles each authorized provider root once per reconciliation.
- Authenticate scope proposals and prove native order. Hook wakes are scheduling inputs. Repository text, timestamps, mutable working directories and ordinary cross-project markers cannot establish a handoff.
- Preserve raw paths only in approved private configuration. Use keyed provider references and fixed payload allowlists in state, diagnostics and exports. Treat a user account and its explicitly approved integrations as trusted.
- Keep project and story eligibility, observation identity, coverage and pricing independent. Preserve Unknown, exclude unqualified surfaces and charge each covered native observation once. Provider cost ticks, comparable API-equivalent USD, billed spend and quota are separate.
- Preserve byte-identical #83 as-of exports at the frozen legacy sequence and rate card. Gate versioned current output on exact project ACK and a durable independent recovery fence. Preserve immutable receiver identities and prior acceptance receipts.
- Target macOS Codex Desktop, Claude Code and Grok Build CLI. Qualify Linux Codex CLI, Claude Code and Grok Build CLI independently on arm64 and x86-64, systemd user manager and local ext4. macOS Codex CLI is outside the initial matrix. Release claims are limited to proven surfaces. Windows is later release work.
- Use forward-only commits on an authorized implementation branch. Retain raw native proof privately, publish sanitized receipts, and preserve #83 production until an independently approved cutover.

## Review focus

1. **Late conflicting handoff after ACK** must dispute the affected current span without moving historical charges. M07 and M09 cover both receipt orders and snapshots.
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
| M03 Versioned project persistence | M02 | `S/monitor_types.py`, `S/types.py`, `S/ledger.py`, legacy schema and serializers |
| M04 Adapter contract and existing providers | M03 | `S/sources/adapter.py`, `S/sources/scan.py`, `S/sources/codex.py`, `S/sources/claude.py` |
| M05 Grok evidence adapter | M04 | `S/sources/grok.py`, `S/pricing.py`, Grok fixtures and rate treatment |
| M06 Registry and capture epochs | M04 | `S/monitor_registry.py`, registry and checkout evidence |
| M07 Native scope and handoff | M06 | `S/monitor_scope.py`, `S/scopes.py` scope bridges |
| M08 Service journal and claim order | M07 | `S/monitor_journal.py`, identity and reservation |
| M09 Project writes and ACK | M08 | `S/monitor_journal.py`, `S/monitor_writer.py`, `S/ledger.py` monitor application API |
| M10 Wake and park scheduler | M09 | `S/monitor_scheduler.py`, private local ingress and scheduling |
| M11 Root watches and coordinator | M05, M10 | `S/host_watch.py`, `S/monitor.py`, `S/service.py` coordinator entry |
| M12 Recovery and publication fence | M09 | `S/monitor_recovery.py`, witness and receiver delivery fencing |
| M13 Snapshot reports | M11, M12 | `S/monitor_report.py`, `S/monitor.py` publication, `S/rollup.py`, `S/cli.py` reports |
| M14 Compatible export and reconciliation | M13 | `S/export.py`, `S/monitor_report.py`, receiver fixtures |
| M15 Host service lifecycle | M11, M14 | `S/install.py`, `S/host_service.py`, `S/cli.py` lifecycle |
| M16 Backup, legacy adoption and rollback | M12, M14, M15 | `S/backup.py`, `S/monitor_recovery.py`, `S/install.py`, `S/cli.py` migration |
| M17 Privacy and scale integration | M16 | Integration fixtures and tests, sanitized health counters |
| M18 Native macOS qualification | M17 | `S/qualification.py`, macOS receipt and runbook sections |
| M19 Native Linux qualification | M18 | `S/qualification.py`, Linux receipts and runbook sections |

The #101 and #102 evidence is an input to M04, M05, M15 and M19. Keep a leaf within four implementation agent-hours at JIT. M04, M11, M15, M16 and M19 may need further splitting once exact native capabilities and host access are confirmed. Preserve the dependency order if split. The table serializes shared-file edits. M05 can proceed alongside M06–M10, and M12 can proceed alongside M10–M11 once M09 is accepted.

## Verification convention

Run unit leaves from the implementation checkout with `uv run --project packages/aitm-usage --locked pytest -q packages/aitm-usage/tests/<named-file>`. A red run must fail on the new assertion or missing interface. A green run must pass that file plus the named related tests. Run `uv run --project packages/aitm-usage --locked ruff check packages/aitm-usage` and `git diff --check` before each scoped commit. Keep the versioned, deterministic fixtures separate from host qualification receipts. Replace `<named-file>` with the concrete `T` file shown under the leaf.

## Implementation leaves

### M01. Host path security

**Files** Create `S/host_fs.py` and `T/test_host_fs_security.py`. Modify private-path validation and per-user guard location in `S/ledger.py`.

**Contract** `check_private_acl(target: Path | int, *, ancestor: bool = False) -> None` and `account_control_root(uid: int) -> Path` in `host_fs`. Keep Darwin ancestry rules and POSIX fd-relative checks. On Linux inspect access and default ACLs separately and use a stable UID-resolved account root independent of environment overrides.

- [ ] Write `test_private_acl_rejects_linux_default_acl_and_unknown_enforcement`, `test_pinned_path_rejects_symlink_and_wrong_owner` and `test_uid_guard_ignores_home_override`. Assert `0700` with a permissive default ACL fails and an unavailable ACL capability refuses state admission.
- [ ] Run the named file to show red. Implement the checked OS boundary and run green with `test_ledger.py`. Exercise real ACL enforcement on the qualified Linux volume. Commit only M01 paths.

### M02. Atomic publication and restore operations

**Files** Extend `S/host_fs.py` and add `T/test_host_fs_publication.py`. Move native call sites in `S/scopes.py`, `S/service.py`, `S/export.py`, `S/backup.py` and `S/install.py` onto it.

**Contract** `publish_noreplace(src_dir: int, src: str, dst_dir: int, dst: str) -> bool` and `exchange_entries(src_dir: int, src: str, dst_dir: int, dst: str) -> None`. Keep exclusive file and directory publication, collision replay, atomic restore exchange and parent directory fsync. Probe `RENAME_EXCHANGE` separately because #102 exercised `RENAME_NOREPLACE` only.

- [ ] Write `test_existing_destination_survives_noreplace`, `test_directory_exchange_and_durability` and `test_unsupported_primitive_fails_without_replacement`. Assert EEXIST preserves both inode identities and a refused exchange leaves the original store intact.
- [ ] Run red. Wire native Darwin and Linux operations. Run green with `test_scopes.py`, `test_export.py` and `test_install.py`, including real supported filesystem runs. Commit M02.

### M03. Versioned project persistence

**Files** Create `S/monitor_types.py` and `T/test_monitor_ledger_version.py`. Extend version checks and serializers in `S/ledger.py` and `S/types.py`.

**Contract** `Ledger.upgrade_monitor_schema(expected_sequence: int) -> LedgerIdentity` and `Ledger.monitor_as_of(sequence: int) -> MonitorLedgerView`. Use the existing transaction sequence and append-only revision storage with an explicitly versioned monitor payload. Keep legacy decoding separate and retain `Ledger.as_of` and the legacy renderer for frozen views. Bump the database schema version only under the guarded, rehearsed migration. Carry native host surface, normalized time basis, coverage and optional provider cost separately.

- [ ] Write `test_schema_upgrade_preserves_legacy_identity_and_export_bytes`, `test_old_binary_refuses_monitor_schema`, and `test_mixed_or_interrupted_upgrade_rolls_back`. Assert the legacy snapshot and key are unchanged and a stale expected sequence refuses migration.
- [ ] Run red. Implement versioned dispatch and transactional upgrade. Run green with `test_ledger.py` and `test_export.py`. Commit M03.

### M04. Adapter contract and Codex or Claude bridge

**Files** Create `S/sources/adapter.py` and `T/test_monitor_adapters.py`. Adapt `S/sources/{scan,codex,claude}.py` without rewriting proven token and marker logic.

**Contract** `ProviderAdapter.discover(root: SourceRoot) -> Iterable[SourceLocator]` and `ProviderAdapter.read_delta(locator: SourceLocator, cursor: StreamCursor | None) -> AdapterBatch`. `AdapterBatch` contains verified native lineage, boundary, time basis, usage revision, project context and diagnostics. The adapter declares a qualified host, client version and format tuple. Derive keyed service identity from verified lineage before choosing a project key. Keep transcript content transient and discard anything outside the field allowlist.

- [ ] Write `test_desktop_and_cli_in_shared_root_admit_only_qualified_surface`, `test_codex_archive_counter_epoch_replays_once`, and `test_claude_streamed_revision_and_nested_overlap`. Assert an unqualified macOS CLI rollout contributes zero with a sanitized coverage reason. Retain Desktop native receipt and Claude linked-request proof.
- [ ] Run red. Implement the common contract around the current collectors and add an independent Linux Codex CLI receipt fixture when #102’s interface can be verified. Run green with `test_scan.py`, `test_codex.py` and `test_claude.py`. Commit M04.

### M05. Grok whole-turn adapter

**Files** Create `S/sources/grok.py`, `T/test_grok.py` and allowlisted fixtures under `T/fixtures/grok/`. Update `S/pricing.py` for distinct reported ticks and rate availability.

**Contract** `GrokAdapter.read_delta(locator: SourceLocator, cursor: StreamCursor | None) -> AdapterBatch`. Match a durable native `turn_completed` to a verified prompt lineage. Use completion time, validate persisted and headless token semantics separately, and use the snapshot for corroboration. A snapshot-only row, an incomparable native revision and unresolved overlap cannot create an attributable charge. Preserve Unknown API-equivalent pricing when the rate basis is missing.

- [ ] Write `test_resume_and_snapshot_replay_count_two_distinct_turns`, `test_hookless_eligible_completion_keeps_native_interval`, `test_fork_excludes_inherited_turns`, `test_late_folded_parent_never_adds_to_child`, and `test_snapshot_conflict_and_cache_categories`. Cover cancellation, concurrent prompts, rewind, later append and copied history as gated fixture cases.
- [ ] Run red. Implement versioned native decoding and separate rate provenance. Run green with `test_accounting.py`. Commit M05. Later qualification proves actual receipt authority on every advertised host.

### M06. Explicit registrations and capture epochs

**Files** Create `S/monitor_registry.py` and `T/test_monitor_registry.py`.

**Contract** `Registry.register_project(request: ProjectRegistrationRequest) -> RegisteredProject` and `Registry.set_permission(change: CaptureChange, boundary: VerifiedBoundary) -> CaptureEpoch`. Store owner-approved roots and project-to-provider permission edges outside Git. Resolve physical anchors and reject cross-project identical or nested anchors. A project’s immutable identity survives display-name and remote changes. Preserve per-stream enrollment, disable and re-enable boundaries.

- [ ] Write `test_two_clones_share_identity_but_nested_foreign_anchor_fails`, `test_disable_reenable_excludes_late_disabled_interval` and `test_revoked_root_is_not_reread_for_prior_revision`. Assert pre-disable admitted work can settle where authorized, a crossing unsplittable span is a gap, and re-enable cannot backfill the disabled interval.
- [ ] Run red. Implement registration and epoch matching, then run green with `test_scan.py`. Commit M06.

### M07. Authenticated scope, handoff and proof holds

**Files** Create `S/monitor_scope.py` and `T/test_monitor_scope.py`. Extend verified marker and owner-binding reuse in `S/scopes.py`.

**Contract** `resolve_route(observation: NativeObservation, registry: RegistryView, scopes: ScopeView) -> RouteDecision` and `ScopeState.apply_handoff(command: Handoff, receipt: VerifiedBoundary) -> HandoffDisposition`. Validate authority, exact before-boundary generation and next native boundary. A valid ordinary marker contradicting a registered anchor holds both totals. A dedicated handoff may override only the verified stale anchor lineage. Keep bounded provenance-only replay holds with expiry and explicit gaps.

- [ ] Write `test_foreign_ordinary_marker_conflicts_then_prospective_handoff_routes`, `test_handoff_A_to_B_to_C_with_retained_A`, `test_late_competing_receipt_after_ack_disputes_in_both_orders` and `test_expired_hold_releases_no_usage`. Keep the historical accepted projection when current usage is disputed. Test a development owner lacking destination worktree proof.
- [ ] Run red. Implement evidence-backed routing and hold dispositions. Run green with `test_scopes.py`. Commit M07.

### M08. Single-owner journal and verified revision order

**Files** Create `S/monitor_journal.py` and `T/test_monitor_journal.py`.

**Contract** `RoutingJournal.reserve(candidate: RoutedRevision, progress: StreamCursor) -> ClaimDisposition`. Take a stable per-user coordinator lease. In one transaction reserve the canonical observation’s only project and retain normalized pending revision and replay cursor. A causal successor can supersede the current revision. Identical or proven older revisions have no additive effect. Incomparable content becomes disputed.

- [ ] Write `test_competing_project_claims_cannot_double_charge`, `test_causal_revision_survives_stale_replay_after_restart` and `test_reservation_and_cursor_commit_together`. Assert provider archive copies keep one canonical key, a distinct verified retry keeps its own key, and an injected rollback leaves no partial claim or cursor movement.
- [ ] Run red. Implement private keyed journal and lease. Run green with `test_ledger.py`. Commit M08.

### M09. Guarded destination writes and ACK

**Files** Create `S/monitor_writer.py` and `T/test_monitor_delivery.py`. Extend `S/monitor_journal.py` and `S/ledger.py`.

**Contract** `ProjectDelivery.commit(claim: PendingClaim) -> ProjectWriteReceipt` and `RoutingJournal.ack(receipt: ProjectWriteReceipt) -> PublicationCandidate`. Reuse stable project pseudonyms and existing guarded transactions. Both operations compare exact lineage and revisions. Bound pending capacity per destination. A failed destination keeps pending state and backpressure for its shared stream. Reserve progress capacity for independent healthy streams.

- [ ] Write `test_restart_at_reserve_commit_and_ack_yields_one_row`, `test_stale_ack_never_rewinds_publication`, and `test_full_destination_queue_preserves_independent_progress`. Assert a blocked stream’s cursor remains replayable and settlement after recovery preserves two distinct project scopes.
- [ ] Run red. Implement guarded delivery and bounded dispositions. Run green with `test_monitor_journal.py` and `test_ledger.py`. Commit M09.

### M10. Private wake ingress and parked-session scheduling

**Files** Create `S/monitor_scheduler.py` and `T/test_monitor_scheduler.py`.

**Contract** `Scheduler.notify(hint: WakeHint) -> None` and `Scheduler.take_due(now: float, limit: int) -> tuple[WorkItem, ...]`. Use local-only ingress that resolves native locators transiently. Persist only allowlisted keyed hints. Coalesce by native provider, session and verified turn where available. Apply Active, Settling and Parked as scheduling states. Explicit park carries no workflow or scope authority. Keep fairness when another project is blocked.

- [ ] Write `test_park_final_catchup_then_late_write_reopens`, `test_stale_stop_cannot_park_newer_turn`, and `test_duplicate_and_missing_hooks_keep_idempotent_progress`. Verify concurrent turns, resume, retained cursors and bounded quiet backoff. A lost wake must leave the next native reconciliation able to recover.
- [ ] Run red. Implement the scheduler using monotonic deadlines and bounded work units. Run green with `test_monitor_delivery.py`. Commit M10.

### M11. Shared root watchers and coordinator

**Files** Create `S/host_watch.py`, `S/monitor.py` and `T/test_monitor_watches.py`. Add coordinator entry in `S/service.py` while keeping the old service interface available for rehearsal and rollback.

**Contract** `WatchSet.events(timeout: float) -> tuple[WatchEvent, ...]` and `Monitor.run_once(now: float) -> MonitorCycle`. Use Darwin FSEvents and Linux recursive inotify coverage behind the same boundary. Enroll new directories, invalidate stale locators after rotation, and request bounded metadata-first reconciliation after overflow or restart. Discover each authorized root once and reread only changed or due streams.

- [ ] Write `test_watch_overflow_and_nested_rotation_reconcile`, `test_shared_root_enumerates_once_for_many_projects`, and `test_unchanged_parked_payload_is_not_read`. Verify a changed parked source wakes independently and a lost root becomes a coverage gap.
- [ ] Run red. Integrate scheduler, discovery, route decisions and guarded delivery. Run green with `test_monitor_scheduler.py`, `test_scan.py` and real watch probes. Commit M11.

### M12. Independent recovery and publication fence

**Files** Create `S/monitor_recovery.py` and `T/test_monitor_recovery_fence.py`.

**Contract** `RecoveryFence.protect(candidate: PublicationCandidate) -> FencedPublication` and `RecoveryFence.record_export_intent(delivery: ReceiverDelivery) -> ExportIntent`. Durably append the monotonic tail and authenticated decision digests before exposing a report view or sending an export. Keep the tail outside rollback snapshots. Prepared but interrupted publication can block replay without asserting it was exposed. Require verified current tail and receiver acceptance when resuming an ambiguous send.

- [ ] Write `test_view_cannot_escape_before_recovery_fsync`, `test_restore_with_only_old_witness_holds_replay`, and `test_interrupted_export_requires_receiver_reconciliation`. Inject failure before and after persistence. Assert replay stops at the last proven common boundary when the current witness is missing.
- [ ] Run red. Implement durable write-ahead witness and recovery verification. Run green with `test_monitor_journal.py` and `test_monitor_delivery.py`. Commit M12.

### M13. Pinned project and story reports

**Files** Create `S/monitor_report.py` and `T/test_monitor_report.py`. Connect the fence to the coordinator in `S/monitor.py`, and reuse relationship and rollup logic in `S/rollup.py`. Add CLI `report projects` and `report stories --project UUID --snapshot ID` in `S/cli.py`.

**Contract** `ReportReader.projects(window: ReportWindow, rates: RateBasis) -> ProjectSummary` and `ReportReader.stories(project_id: UUID, snapshot_id: str) -> StoryBreakdown`. `Monitor.publish(candidate: PublicationCandidate) -> FencedPublication` must protect the candidate with M12 before making it visible to `ReportReader`. Pin the resulting journal view, ledger sequences, acknowledged revisions, scope history, interval and rate card. Expose the legacy baseline without synthetic ACKs. Use the declared native observation time basis and preserve legacy times. Direct totals reconcile to distinct stories, drafts, project-wide work and unattributed story scope.

- [ ] Write `test_snapshot_pins_scope_time_and_rates_across_commands`, `test_project_totals_reconcile_without_inclusive_epic_double_count` and `test_partial_unknown_and_hookless_grok_visibility`. Verify a time correction moves only a new snapshot and a missing historical view returns explicit unavailable. Assert an ACK alone is invisible through the CLI when the coordinator cannot persist the fence.
- [ ] Run red. Implement read-only local reporting with structured JSON. Run green with `test_rollup.py` and `test_monitor_recovery_fence.py`. Commit M13.

### M14. Versioned exports and immutable receiver compatibility

**Files** Extend `S/export.py` and `S/monitor_report.py`. Add `T/test_monitor_export.py` and extend the receiver fixture in `T/fixtures/receiver.py`.

**Contract** `export_monitor_project(view: PublishedView, project_id: UUID, destination: Path) -> MonitorExportReceipt` and `compatible_delivery(view: PublishedView, receiver: ReceiverState) -> CompatibleDelivery`. Keep legacy `export_as_of` deterministic. Emit normalized monitor rows under a separate schema. Preserve Core-compatible original identity and receipt. Put changed immutable payloads into an explicit reconciliation queue instead of resending them. The future C44 consumer remains separate.

- [ ] Write `test_legacy_export_bytes_remain_fixed`, `test_pending_and_disputed_rows_are_excluded_from_compatible_export`, and `test_time_correction_after_receiver_acceptance_never_reuses_key_or_charges_twice`. Verify report and export use the same fenced revision and privacy allowlist.
- [ ] Run red. Implement projection, export intent and receiver replay semantics. Run green with `test_export.py`, `test_rollup.py` and `test_monitor_recovery_fence.py`. Commit M14.

### M15. Single per-user supervisor on macOS and Linux

**Files** Create `S/host_service.py` and `T/test_monitor_install.py`. Extend `S/install.py` and `S/cli.py` lifecycle commands. Preserve the original LaunchAgent identity until guarded adoption.

**Contract** `Supervisor.install(runtime: VerifiedRuntime, state: MonitorState) -> ServiceReceipt` and `Supervisor.verify(expected: ServiceReceipt) -> ServiceHealth`. Register one per-user LaunchAgent or systemd user unit. Verify loaded definition, exact executable and same-user process incarnation plus a fresh matching heartbeat. Enable within the user manager. Report absent manager and operator-controlled lingering separately. Refuse unsupported filesystem and insecure state before activation.

- [ ] Write `test_second_service_and_legacy_writer_refuse_activation`, `test_stale_pid_and_heartbeat_do_not_certify_readiness`, and `test_no_systemd_user_bus_and_unapproved_linger_are_explicit`. Exercise isolated install, stop and restart using controlled manager fixtures.
- [ ] Run red. Implement supervisor selection and exact-runtime evidence. Run green with `test_install.py` and `test_service_process.py`. Commit M15. Real OS proofs occur in M18 and M19.

### M16. Coordinated backup, legacy adoption and rollback

**Files** Extend `S/backup.py`, `S/monitor_recovery.py`, `S/install.py` and `S/cli.py`. Add `T/test_monitor_cutover.py`.

**Contract** `capture_monitor_backup(store: MonitorStore, destination: Path) -> MonitorBackupReceipt` and `adopt_legacy(request: LegacyAdoption, receipt: MonitorBackupReceipt) -> LegacyBaseline`. Back up the journal, keys and ledger vector with pending routes. Verify the separate current recovery tail. Adopt the existing UUID, key, cutoff and ledger sequence under the original writer guard. Fence new projects behind proven enrollment baselines and reconcile provider activity during stop exactly once.

- [ ] Write `test_cutover_first_report_and_fixed_export_parity`, `test_copied_pre_cutover_archive_cannot_reach_other_project`, `test_older_backup_before_handoff_and_accepted_export_holds_or_reconciles`, and `test_reversible_prewrite_failure_and_postwrite_forward_recovery`. Assert mixed generations and an unprovable independent tail fail closed.
- [ ] Run red. Implement dry-run validation, staged restore and adoption checks. Rehearse on copied representative #83 state, including rollback before new writes and recovery of pending routes. Run green with `test_monitor_recovery_fence.py`, `test_install.py` and `test_export.py`. Commit M16.

### M17. Cross-project privacy, saturation and scale proof

**Files** Create `T/test_monitor_integration.py` and allowlisted two-project fixtures under `T/fixtures/monitor/`. Add sanitized work counters in `S/monitor.py` only where the verification needs them.

- [ ] Write `test_two_projects_same_issue_distinct_routes_and_three_roles`, `test_sentinel_secrets_never_persist_or_cross_export`, and `test_two_active_and_fifty_parked_with_one_changed_source`. Check actual persisted wake, hold, journal, witness, ledger, report and export data against field allowlists. Assert no unapproved path, raw provider ID or sibling identity. Measure zero unchanged parked payload reads over a healthy reconciliation and constant root discovery count as project count increases.
- [ ] Run red if the proof finds a gap and return the fix to the owning leaf before continuing. Run all locked tests and Ruff. Capture workload read counts, latency, CPU and memory. Record release budgets from evidence. Commit M17 evidence and tests.

### M18. Controlled macOS qualification

**Files** Extend `S/qualification.py`, `T/test_activation_receipt.py` and `README.md`. Retain sanitized evidence outside the product checkout until the declared delivery step.

- [ ] Add receipt validation `test_monitor_mac_receipt_requires_exact_provider_and_service_proof`. It rejects wrong builds, insufficient overlap, a stale heartbeat, and missing production scope-carrier proof. Run red, implement and run green with the activation and installer tests.
- [ ] Run on an isolated candidate with actual Codex Desktop, Claude Code and Grok Build CLI. Verify two projects with the same story number, concurrent driver/reviewer/researcher usage, a foreign ordinary marker followed by a proven handoff, a parked resume, late writes, a hookless Grok completion, fork and folded overlap, one LaunchAgent, crash catch-up and fixed #83 export parity. Keep private raw traces and publish only a sanitized receipt. Commit M18.

### M19. Controlled Linux qualification and delivery gate

**Files** Extend `S/qualification.py`, `T/test_activation_receipt.py` and `README.md` after M18.

- [ ] Add `test_linux_receipt_requires_user_manager_ext4_native_receipts_and_arch` and `test_container_evidence_cannot_satisfy_linux_activation`. Run red, implement and run green.
- [ ] Reproduce #102 credential-free checks on arm64 and x86-64. On each real supported target, verify an authenticated turn and verified story boundary on Codex CLI, Claude Code and Grok Build CLI. Prove user-manager startup, logout, allowed headless persistence, exact unit/process heartbeat, recursive watch overflow, crash replay, safe restore and qualified atomic operations on ext4. Re-run the two-project, three-provider acceptance case and capture release receipts per target.
- [ ] Run the full locked suite and Ruff on the release candidate. Confirm the documented supported matrix matches actual receipts. Keep unqualified surfaces out of support claims. A production installation needs a separately authorized cutover with an explicit rollback or forward-recovery decision. Commit M19 and submit the integrated package for the project’s applicable review and delivery gates.

## Draft self-check and plan review handoff

The plan covers registration and authority (M06–M07), providers (M04–M05, M18–M19), routing and durable replay (M08–M12), reporting and compatibility (M13–M14), host state and lifecycle (M01–M03, M15), migration (M16), and privacy and scale (M17). The fixed test commands use the existing package location and locked environment. Provider, rate-card, architecture, host access and service authority evidence must be reconfirmed at JIT. Review this draft against the accepted spec before decomposing work into issue IDs.
