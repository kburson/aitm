# Continuous Usage Capture Implementation Plan

> **For agentic workers** Use superpowers:subagent-driven-development or superpowers:executing-plans after execution is authorized. Check off each verified step.

**Goal** Qualify a durable Codex and Claude Code usage collector before Core C01 starts. Keep it collecting through and after Core adoption.

**Architecture** A standalone local package owns an append-oriented SQLite ledger and import checkpoints. A LaunchAgent runs the collector, while a CLI records scope markers, reports health and exports a stable projection. C44 later consumes compatible records without replacing the producer or its database.

**Tech stack** Python 3.13+, standard-library SQLite, versioned JSONL, macOS per-user launchd. The package and its test configuration live under `packages/aitm-usage/`.

**Spec** [Continuous agent usage capture](../design/usage-capture-design.md), exact reviewed digest `sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee`.

## Global constraints

- Ship on trunk as a standalone package before any dependency on an installed Core. Keep the shared `planning` branch for planning artifacts. No change to the accepted Core leaf plan is required to build the collector.
- Use a per-user LaunchAgent and scan every 15 seconds while awake. Use a dedicated versioned environment and absolute interpreter and application paths. The service makes no model calls and has no workflow guard authority.
- Store the persistent ledger, pseudonym key and private diagnostics outside Git. Use a fixed allowlist for exported fields and diagnostics. Record partial coverage and Unknown without converting either to zero.
- Preserve the project UUID and the same ledger through installs, upgrades and C44 adoption. Back up via SQLite, and verify project and key identity before restore. Refuse unsupported schema versions before writes.
- Retain epic-wide and focused child scopes in one planning session and worktree. Bind owner, attempt and dedicated worktree from Develop through delivery. Keep model usage, API-equivalent USD, account quota and billed spend independent.
- Produce an installation and on-host activation receipt before [C01 / #3](../../3/story.md) enters Develop. Collecting real qualification evidence and installing the service are execution activities that follow later authority.

## Review focus

1. Delayed first scan, in-flight cutoff and re-enrollment must preserve eligible usage without absorbing unrelated segments (U03/U04/U05).
2. A marker can arrive after its provider boundary. The first child request, return to epic and a nonowner in a development worktree must retain correct or Unknown attribution (U02/U10/U11).
3. Archive replay, replaced files and counter resets can look alike. Prove identity before advancing the checkpoint or counting usage (U03/U04/U05).
4. Same-window quota changes, unsupported rates and missing receipts require explicit availability (U06).
5. A withheld record can finalize after the export watermark advances. Replay and corrections must preserve immutable receiver keys and reconsider pending keys (U07/U09).

## Dependency order and sizing

P1 is the backlog priority. #83 is first in the delivery sequence for this project. The thirteen independently verifiable leaves below total **46 implementation agent-hours** including local verification and source review. Each leaf fits the four-hour cap. Shared file edits follow dependency order. Estimates are planning inputs for each leaf's own design, plan and JIT qualification.

| Key | Deliverable | Hours | Predecessors |
| --- | --- | ---: | --- |
| U01 | Package and private durable ledger | 4 | — |
| U02 | Scope inbox and provider-session binding | 3.5 | U01 |
| U13 | Draft aliases, ancestry and direct/inclusive rollups | 2.5 | U02 |
| U03 | Eligible source cursor and activation boundary | 3.5 | U02 |
| U04 | Codex cumulative usage adapter | 4 | U03 |
| U05 | Claude Code request usage adapter | 3.5 | U03 |
| U06 | Pricing and quota availability | 3 | U04, U05 |
| U07 | As-of export and C44 compatibility proof | 3.5 | U13, U06 |
| U08 | Collector service, live commands and status | 3.5 | U07 |
| U12 | Integrated restart, enrollment and privacy proof | 4 | U08 |
| U09 | LaunchAgent install, upgrade and restore | 4 | U12 |
| U10 | Qualification validator and on-host runbook | 3.5 | U09 |
| U11 | Project Mac activation and dogfood proof | 3.5 | U10 |

Paths below are relative to `packages/aitm-usage/`. Source files live in `src/aitm_usage/` and tests in `tests/`. U01 owns `pyproject.toml` and the package-local lockfile. No root workspace bootstrap files are required. Each CLI command is added in its owning leaf. U11 qualifies installed behavior with U10’s validator and updates the runbook from the observed result. The test-first instruction applies to the other leaves. Leaves touching the shared CLI entry point run in order U01, U02, U13, U07, U08, U09, U10. Other dependency-ready leaves may proceed independently on their owned files.

For each leaf, write the named tests first, run the leaf test file to show the expected missing behavior, implement the named contract, then run `uv run --project packages/aitm-usage pytest packages/aitm-usage/tests/<file> -q` and `uv run --project packages/aitm-usage ruff check packages/aitm-usage`. Require passing results and applicable review and delivery evidence on the actual source version. Retain the initial failure and passing proof. Product source and tests are execution deliverables.

## Installed command contract

All commands use the `aitm-usage --project <state-dir>` prefix. The private default state root is `~/Library/Application Support/aitm-usage/<project-uuid>/` with directory mode 0700 and private files at 0600. U01 installs the console script `aitm-usage = aitm_usage.cli:main`. Use SQLite WAL and a 1-second busy timeout on read connections. A busy status read reports a read gap separately from the last known heartbeat.

| Owner | Subcommands after the prefix |
| --- | --- |
| U02 | `scope mark --marker <file> --json`, `scope correct --correction <file> --json`, `development bind --binding <file> --json` |
| U13 | `item alias --draft <id> --issue <id> --json`, `item parent --child <id> --epic <id> --json` |
| U07 | `export --as-of <sequence> --rate-card <id> --output <directory> --json` |
| U08 | `register --config <file> --json`, `source add-anchor --anchor <file> --json`, `collect-once --json`, `service run`, `status --json`, `rollup --item <id> --json` |
| U09 | `service install --wheel <file> --interpreter <path> --json`, `service upgrade --wheel <file> --interpreter <path> --json`, `service stop --json`, `service uninstall --json`, `backup --output <directory> --json`, `restore --backup <directory> --json` |
| U10 | `qualify --receipt <file> --json` |

Initial registration takes the exclusive lease before service startup. While the service is running, scope markers, bindings, corrections, aliases, ancestry and new worktree anchors are written as typed commands to the private inbox. The lease holder validates and appends them and acknowledges by command ID. Reject a repeat with conflicting bytes. A second `collect-once` refuses with `writer-active` while the service holds the lease. Status, export, rollup and backup read a SQLite snapshot. Restore and upgrade follow U09's stopped-writer protocol.

### U01 — Package and private durable ledger

**Files** `pyproject.toml`, `uv.lock`, `src/aitm_usage/{__init__,cli,types,ledger}.py`, `tests/test_ledger.py`.

**Contract** `Ledger.initialize(root: Path, project_id: UUID) -> Ledger`, `Ledger.open(root: Path, project_id: UUID) -> Ledger`, `apply(batch: LedgerBatch) -> int`, and `as_of(sequence: int) -> LedgerView`. Define typed observation, revision, scope marker, diagnostic and cursor envelopes, including shared Registration, Eligibility, SourceBoundary, AdapterResult and a versioned sanitized ProviderCheckpoint. Acquire a nonblocking process-held exclusive file lock per project before any write path. Keep the lock file stable across the database lifetime so the kernel releases ownership on process exit. Open status and backup reads without a writer lease. Initialize a missing ledger explicitly and validate identity/schema on every ordinary open. A transaction appends revisions and moves the cursor and provider checkpoint together. The checkpoint preserves the counter baseline, verified logical epoch and ordinals, and the minimum sanitized request prefix for partial reconciliation. Apply only allowlisted fields to the ledger, inbox and checkpoint. Reject extra raw fields before writing any inbox file. Pseudonymize accepted source references before persisting any private or exported record. Store pseudonyms with a project key and include a key identifier in metadata.

- [ ] Write `test_atomic_cursor_and_revisions` with a forced exception between append and cursor advance, a second writer, same-key same-payload retry, and same-key conflicting immutable payload. Assert rollback, writer refusal, lease release on process exit, idempotence and explicit conflict. Verify state permissions and that unsupported schema and mismatched project/key fail before writes.
- [ ] Run `test_ledger.py` to show failure, implement the package, typed ledger and private state initialization, then pass leaf verification.

### U02 — Scope inbox and provider-session binding

**Files** `src/aitm_usage/{scopes,cli}.py`, `tests/test_scopes.py`.

**Contract** `enqueue_marker(directory: Path, marker: ScopeMarker) -> MarkerId`, `resolve_scope(observation: Observation, view: LedgerView) -> ScopeResolution`, and `attest_marker(marker: ScopeMarker, boundary: SourceBoundary) -> MarkerDisposition`. The private inbox uses atomic file publication. Require a monotonic per-session scope sequence and proof the marker was published before its effective request or turn boundary. Validate against the SourceBoundary contract using fixtures in this leaf. A boundary may be proven for a candidate session under an approved source root before that session is enrolled. Candidate evidence carries no usage into the ledger. Admission covers only the explicit eligible segment after a proven marker. U04 and U05 provide real boundaries and U08 connects them. A late scan can resolve an already-published marker. A marker created after a claimed boundary can affect only a later verifiable boundary, and an explicit correction appends a revision. Return pending until the enrolled adapter validates the boundary, then commit the marker and return an accepted receipt. A supported serial request marker precedes the first child response in provider order. A turn-only marker is emitted before the child turn begins. Enrollment binds the explicit owner provider session and generation. A same-story marked reviewer keeps its own role and an unproven session is unassigned. Consume into the ledger before acknowledging. Expose scope mark, development bind and scope correct through the queued CLI operations in the command table.

**Normal session proof.** For Codex Desktop, derive the session reference from the invoking agent's `CODEX_THREAD_ID` and confirm it against the enrolled rollout's session metadata. A same-turn marker is admissible when a recognized in-session tool call and result carry its opaque command receipt in provider order before the next recorded model request boundary. Otherwise use a pre-turn marker with the next verifiable turn ID. For Claude Code, the controlled launcher reserves a session UUID with `--session-id` before work and verifies the emitted init or transcript session identity. An authorized resume uses the already enrolled session. For a native review launched by a broker, use its verified reviewer launch/join identity and bind the first provable boundary after enrollment. Setup work before that remains Unknown. A source-proven serialized tool receipt or a marker recorded before the next turn provides order. Timestamps on their own do not prove order. Keep unverifiable session or boundary claims pending or Unknown. Do not retain raw tool content.

- [ ] Write `test_planning_scope_and_development_owner` with one epic and two children in a single session. Verify first child request and switch-back for marker-first and observation-first arrival, Unknown while unresolved, scope before the next turn when the request boundary cannot be proven, owner-only development default, unmarked nonowner, compatible marked reviewer, conflicting marker quarantine, housekeeping and two review roles. Exercise actual CLI marker publication, idempotent inbox replay, recorded correction that preserves an earlier as-of result, invalid retroactive claim and duplicate sequence.
- [ ] Run `test_scopes.py` to show failure, implement the marker and rollup contract, then pass leaf verification.

### U13 — Draft aliases, ancestry and direct/inclusive rollups

**Files** `src/aitm_usage/{rollup,cli}.py`, `tests/test_rollup.py`.

**Contract** `rollup(root: ItemKey, view: LedgerView) -> UsageRollup`. Queue alias and parent commands through U02's inbox. Preserve revisions of ancestry and graduation aliases and compute inclusive totals from distinct canonical descendants. Represent known Decimal price and a separate Unknown count.

- [ ] Write `test_graduation_and_inclusive_rollup` with an epic, two children, an alias from draft to issue, epic batch usage and per-child usage. Assert each observation contributes once, previous as-of results remain intact and cycles or contradictory aliases are refused. Exercise real CLI publication of alias and parent commands. Use price fixtures until U06 supplies accounting.
- [ ] Run `test_rollup.py` to show failure, implement the rollup and alias/ancestry commands, then pass leaf verification.

### U03 — Eligible source cursor and activation boundary

**Files** `src/aitm_usage/sources/{__init__,scan}.py`, `tests/test_scan.py`.

**Contract** `discover(registration: Registration) -> Iterator[CandidateSource]` and `scan(source: CandidateSource, checkpoint: SourceCheckpoint | None, cutoff: datetime) -> FrameBatch`. Return sanitized source-boundary evidence from approved-root candidates so U02 can verify enrollment before any usage admission. Resolve project eligibility per segment using configured checkout/worktree anchors or a validated explicit enrollment from U02. Keep readable unbound segments excluded. Separate physical incarnation from verified logical stream. Use keyed source locators and anchors and rediscover under approved roots. Check root confinement before opening and after replacement detection. Keep raw paths transient and record observed client/format versions. Read complete JSONL rows only. Publish cursor and observations through U01.

- [ ] Write `test_activation_cutoff_and_archive_continuity` with pre-cutoff, delayed first scan, partial final row, verified archive copy, overlap without continuity, replacement mid-read and symlink escape. Assert that one logical stream resumes once, unverifiable overlap is quarantined, and diagnostics include neither raw path, cwd, branch nor malformed payload. An unsupported format, unfamiliar usage shape, and recognized turn activity without recognized usage report gaps independently of the heartbeat. Include an explicitly enrolled reviewer outside the checkout under an approved root, an unbound session under that root and a later unrelated segment from the same session. Verify only enrolled project evidence enters the ledger.
- [ ] Run `test_scan.py` to show failure, implement discovery, cutoff and cursor handling, then pass leaf verification.

### U04 — Codex cumulative usage adapter

**Files** `src/aitm_usage/sources/codex.py`, `tests/test_codex.py`, `tests/fixtures/codex/usage.jsonl`.

**Contract** `read_codex(batch: FrameBatch, state: CodexState, eligibility: Eligibility) -> AdapterResult`. Feed session metadata, turn context and token counters into the common observation format. Link scope boundaries to proven source order. Qualify a new epoch only with verified origin evidence. Priceable request usage needs a consistent delta and category relationship.

- [ ] Write `test_codex_deltas_exclusion_and_epochs` with a known-zero first request, pre-cutoff baseline, in-flight ambiguous request, repeated total, eligible→excluded→eligible, real reset reusing old totals, truncated start, conflicting key and unknown aggregate span. Assert exact known-category counts, separate gaps and no excluded usage spillover. Replay from the same logical archive without inflation. Restart a fresh process after an excluded segment and use the transactionally retained provider checkpoint to continue without spillover. Exercise model and effort change, a retried or errored request, an independently identified subprocess and one quota observation with reset metadata. Missing durable evidence is a gap.
- [ ] Run `test_codex.py` to show failure, implement the adapter using allowlisted field reads, then pass leaf verification.

### U05 — Claude Code request usage adapter

**Files** `src/aitm_usage/sources/claude.py`, `tests/test_claude.py`, `tests/fixtures/claude/usage.jsonl`.

**Contract** `read_claude(batch: FrameBatch, state: ClaudeState, eligibility: Eligibility) -> AdapterResult`. Group per-session request rows, validate message identity and retain immutable revisions. Compare terminal checkpoints against exact request prefix totals. Keep unsupported terminal or account signals qualified as Unknown.

- [ ] Write `test_claude_revisions_terminal_and_nested_usage` for partial streamed rows, terminal reconciliation, conflicting request/message identity, a late revision to a pre-cutoff request, same row on replay, and nested child usage overlapping a parent aggregate. Assert each independent request contributes once and unresolved overlap is separate. Test eligible and excluded segments, retry, model or effort change, missing terminal evidence and supported structured quota observations. Restart from a committed partial prefix and prove exact reconciliation with sanitized durable fields.
- [ ] Run `test_claude.py` to show failure, implement the adapter and read boundaries, then pass leaf verification.

### U06 — Pricing and quota availability

**Files** `src/aitm_usage/{pricing,accounting}.py`, `src/aitm_usage/rates/2026-11-09.json`, `tests/test_accounting.py`.

**Contract** `price(usage: UsageObservation, rates: RateCard) -> PriceResult` and `quota_snapshot(raw: QuotaEvidence) -> AccountObservation`, and `account_observations(batch: AdapterResult, rates: RateCard) -> LedgerBatch`. Use Decimal, versioned public rate references and explicit currency. Support the standard rates evidenced in #73 with applicable context and cache classes. Unsupported modes, tiers, models or incomplete category evidence return an Unknown price. Keep actual spend Unknown absent attributable billing. AccountObservation includes a pseudonymous account key, bucket, reset window, source, timestamp and observed precision. V1 records retained inline or structured observations. Additional active sampling is later work.

- [ ] Write `test_standard_rates_and_account_only_evidence` from sanitized #73 vectors. Verify cached input subtraction, supported long-context treatment and Claude cache-write TTL, with reasoning counted once. Check that unknown rates leave tokens visible, a changing same-window quota fixture leaves per-agent burn Unknown, and absent billing evidence remains Unknown.
- [ ] Run `test_accounting.py` to show failure, implement independent price, quota and spend records, then pass leaf verification.

### U07 — As-of export and C44 compatibility proof

**Files** `src/aitm_usage/{export,cli}.py`, `tests/test_export.py`, `tests/fixtures/receiver.py`.

**Contract** `export_as_of(view: LedgerView, rate_card: RateCard, destination: Path) -> ExportReceipt`. Snapshot a fixed ledger sequence. Produce deterministic UTF-8 JSONL and manifest with schema, project, cutoff and digest. Export stable pseudonymous source keys, observation revisions, explicit scope revision references, availability, and the immutable rate-card identifier and pricing basis using an allowlist. Do not include local paths, raw handles, key material or provider content. Receiver fixture models the C44 `ingest_usage(source, payload)` seam. Persist per-key accepted payload digests, pending and reconciliation dispositions and the watermark in a temporary SQLite receiver.

- [ ] Write `test_replay_cutoff_and_pending_finalization` with interrupted import, a withheld partial later finalized after restarting a fresh receiver from its durable watermark, a scope or pricing revision after acceptance, and a conflicting payload. Assert accepted identical retries are idempotent, pending keys survive advancing watermarks, corrections queue, and conflicts preserve prior acceptance. Verify identical fixed-cutoff exports after late ledger changes and a changed versioned price basis yields a distinct manifest. Feed a valid export source and canary-bearing malformed inputs, then check both JSONL and manifest for private material.
- [ ] Run `test_export.py` to show failure, implement deterministic export and the compatibility fixture, then pass leaf verification. Actual Core adapter adoption is a later reviewed integration.

### U08 — Collector service, live commands and status

**Files** `src/aitm_usage/{service,cli}.py`, `tests/test_service.py`.

**Contract** `collect_once(registration: Registration, ledger: Ledger) -> CollectionReport` and `run_service(registration: Registration, interval_seconds: int = 15) -> int`. Wire actual providers, cursors, inbox and heartbeat in the same process. An explicit register command pins approved roots, permitted checkout/worktree anchors, and the activation cut-off before scanning. Apply U06 accounting to each committed adapter batch and expose U02 task and feature rollups with tokens, known price and Unknown coverage. A restart reloads the registration without resetting the cut-off. `status --json` reports version, heartbeat, interpreter version, per-source watermarks, observed-through time, lag, known retention limits and coverage. Poll local sources without model calls. Restart from durable state.

- [ ] Write `test_service_commands_and_coverage` through the actual service entry point with temporary project roots and both providers. Verify the command table, confirmed registration, `collect-once` lease refusal, and that a bind, correction and anchor addition are queued and acknowledged while the same service keeps its writer lock. Test permission loss, incomplete rows, and separate heartbeat, watermarks and source lag. Verify known price reaches direct and inclusive rollups, Unknown price preserves tokens, and quota and spend remain separate.
- [ ] Run `test_service.py` to show failure, implement the loop and commands, then pass leaf verification.

### U12 — Integrated restart, enrollment and privacy proof

**Files** `tests/test_service_process.py`, `tests/fixtures/service/`, and `src/aitm_usage/service.py` for the controlled test seam and any integration repair. U08 owns the preceding service changes.

**Contract** Drive the U08 commands against real temporary SQLite state and both adapters in a separate OS process. Control the failure point without weakening the normal write lease. Preserve end-to-end coverage evidence.

- [ ] Write `test_real_service_crash_enrollment_and_private_state`. Prove the unbound approved-root reviewer produces no usage, a proven queued marker admits exactly the eligible segment, and surrounding unrelated segments remain excluded. Exercise both marker arrival orders and the first child request. Kill the service with SIGKILL once between scans and once after an append inside an uncommitted batch. Start a fresh process and assert lock release, rollback and exactly-once catch-up.
- [ ] In the same test use valid and malformed provider records and marker commands with canary values. Establish durable valid writes and scan every byte of private state, including SQLite and WAL or journals, logs, cursor and rejected or inbox files. Inspect status JSON and export JSONL and manifest. Exclude only the known private pseudonym key from the byte scan. U09 extends the scan to the backup bundle.
- [ ] Run `test_service_process.py` to show failure, add the controlled process proof and required integration fixes, then pass leaf verification.

### U09 — LaunchAgent install, upgrade and restore

**Files** `src/aitm_usage/{install,backup,cli}.py`, `tests/test_install.py`.

**Contract** `install_agent(project: Registration, executable: Path, launchctl: LaunchControl) -> InstallReceipt`, `backup(ledger: Ledger, destination: Path) -> BackupReceipt`, and `restore(source: Path, destination: Path, expected: LedgerIdentity) -> RestoreReceipt`. Plan and apply explicit install, stop and upgrade actions. Build the dedicated environment under `versions/<version>-<wheel-digest>/` from a verified wheel and a pinned absolute Python 3.13+ interpreter. Create the venv first and install the exact wheel without runtime dependency resolution. Keep the prior environment beside it through successful upgrade and receipt verification. Prune only inactive, explicitly selected versions with a retained recovery wheel and backup. Set RunAtLoad and KeepAlive. Set plist ProgramArguments to `[<absolute-aitm-usage>, "--project", <absolute-state-dir>, "service", "run"]`. Upgrade backs up state before activation and restores the previous compatible service registration on failure. Restore only into a stopped target under the same writer lock and replace state atomically after validation. Validate absolute paths, ownership and installed version. Use the SQLite backup API and capture the associated private pseudonym key in the same protected backup bundle. Verify project/key identity before restore. Preserve ledger and key when stopping or uninstalling.

- [ ] Write `test_owned_launchagent_and_recoverable_upgrade` with a fake launchctl and temporary state. Check correct plist paths, RunAtLoad, KeepAlive and 15-second polling, idempotent install, failure before activation and failure of the new launch leaving the prior service recoverable, stop and uninstall preserving data, wrong-key and wrong-project restore refusal, and stable pseudonyms and same-cutoff export parity after a supported restore with the backed-up key. Use two side-by-side wheel environments to verify rollback restores the previous plist path after a failed new launch. Scan the protected backup bundle bytes except the known secret key for canaries. V1 supports same-schema version changes and refuses other schema versions before mutation.
- [ ] Run `test_install.py` to show failure, implement installation and backup operations, then pass leaf verification.

### U10 — Qualification validator and on-host runbook

**Files** `README.md`, `src/aitm_usage/{qualification,cli}.py`, `tests/test_activation_receipt.py`, `tests/fixtures/activation/receipt.json`.

**Contract** `validate_activation_receipt(receipt: ActivationReceipt) -> QualificationResult`. Expose the validator as `aitm-usage qualify --receipt <file> --json`. The on-host runbook uses that installed command, both observed local provider routes and actual launchd. Require approved project scope, collector version, both provider routes and client versions, heartbeat, source watermarks, private state permissions, unattended startup, restart and supported backup/upgrade rehearsal, coverage, sanitized sample keys and export parity. Require verified scope-marker evidence on both local provider routes, including marker-first and observation-first processing. Validate labeled real controlled or normal project evidence. Reject fixture-only evidence for activation.

- [ ] Write `test_activation_requires_live_both_providers_and_parity` for fixture-only, stale heartbeat, one missing provider, missing scopes, duplicate records after restart, and receipt privacy. Require correct proof from one real shared planning session with epic hydration and at least two child scopes, overlapping author and reviewer, including graduation and the inclusive rollup, and authorized development and housekeeping. Development ownership can be exercised in a controlled worktree with a clearly labeled proof basis.
- [ ] Run `test_activation_receipt.py` to show failure, implement validation and runbook, then pass leaf verification.
### U11 — Project Mac activation and dogfood proof

**Files** `README.md` and the sanitized receipt at `.aitm/stories/000/83/attachments/activation-receipt.json` on planning. U10 supplies the installed qualification command and tests.

- [ ] After execution and activation are authorized, use scheduled Core #2 child preparation for C01/#3 and C02/#4 as the normal shared-chat observation where separately authorized. Use one controlled real Codex planning session with an epic and two draft children to supply any missing hydration, focused planning or graduation evidence. Use disposable scoped identities for graduation in that proof and label them controlled. Run an overlapping normal Claude review. The validator distinguishes these live sources from fixture-only evidence. The time spent on observed planning and review is outside U11’s 3.5-hour qualification estimate. If neither route produces sufficient evidence, retain the gap and keep the C01 checkpoint open.
- [ ] Build the two rehearsal environments from the reviewed wheel and a version-only rehearsal wheel of the same reviewed source, each with a recorded digest. Rehearse upgrade and rollback in isolated project state before installing the production collector.
- [ ] Install the reviewed package on the project Mac. Observe unattended launchd startup, verify restart catch-up, rehearse supported backup and upgrade with verified recovery and same-cutoff parity, exercise the real routes including supported nested work, model/effort changes and retry evidence or explicit coverage gaps, and validate and publish the receipt with the version, dated evidence and digest. Demonstrate an export replay without duplication and that Unknown remains visible.
- [ ] Verify that the collector is active and coverage is current before authorizing C01 pickup. The same service and ledger continue when Core is released and when C44 starts accepting compatible usage.

## Scope after activation

The collector remains active for AITM. Core's later adoption adds workflow-supplied scope markers and a qualified C44 import, with export parity before switching any consumer. UI, issue presentation, billing connectors, forecasts and additional capture environments can evolve from the same observations. This plan covers the initial delivery of the enduring producer and ledger.
