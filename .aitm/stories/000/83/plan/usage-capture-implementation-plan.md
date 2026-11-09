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

P1 is the backlog priority. #83 is first in the delivery sequence for this project. The eleven independently verifiable leaves below total **40 implementation agent-hours** including local verification and source review. Each leaf fits the four-hour cap. Shared file edits follow dependency order. Estimates are planning inputs for each leaf's own design, plan and JIT qualification.

| Key | Deliverable | Hours | Predecessors |
| --- | --- | ---: | --- |
| U01 | Package and private durable ledger | 4 | — |
| U02 | Scope inbox, aliases and rollups | 4 | U01 |
| U03 | Eligible source cursor and activation boundary | 3.5 | U02 |
| U04 | Codex cumulative usage adapter | 4 | U03 |
| U05 | Claude Code request usage adapter | 3.5 | U03 |
| U06 | Pricing and quota availability | 3 | U04, U05 |
| U07 | As-of export and C44 compatibility proof | 3.5 | U02, U06 |
| U08 | Continuous service and status | 3.5 | U07 |
| U09 | LaunchAgent install, upgrade and restore | 4 | U07, U08 |
| U10 | Qualification validator and on-host runbook | 3.5 | U09 |
| U11 | Project Mac activation and dogfood proof | 3.5 | U10 |

Paths below are relative to `packages/aitm-usage/`. Source files live in `src/aitm_usage/` and tests in `tests/`. U01 owns `pyproject.toml` and the package-local lockfile. No root workspace bootstrap files are required. Each CLI command is added in its owning leaf. U11 qualifies installed behavior with U10’s validator and updates the runbook from the observed result. The test-first instruction below applies to U01–U10. Leaves touching the shared CLI entry point run in order U01, U02, U07, U08, U09, U10. Other dependency-ready leaves may proceed independently on their owned files.

For each leaf, write the named tests first, run the leaf test file to show the expected missing behavior, implement the named contract, then run `uv run --project packages/aitm-usage pytest packages/aitm-usage/tests/<file> -q` and `uv run --project packages/aitm-usage ruff check packages/aitm-usage`. Require passing results and applicable review and delivery evidence on the actual source version. Retain the initial failure and passing proof. Product source and tests are execution deliverables.

### U01 — Package and private durable ledger

**Files** `pyproject.toml`, `uv.lock`, `src/aitm_usage/{__init__,cli,types,ledger}.py`, `tests/test_ledger.py`.

**Contract** `Ledger.initialize(root: Path, project_id: UUID) -> Ledger`, `Ledger.open(root: Path, project_id: UUID) -> Ledger`, `apply(batch: LedgerBatch) -> int`, and `as_of(sequence: int) -> LedgerView`. Define typed observation, revision, scope marker, diagnostic and cursor envelopes, including shared Registration, Eligibility, SourceBoundary, AdapterResult and a versioned sanitized ProviderCheckpoint. Acquire a nonblocking process-held exclusive file lock per project before any write path. Keep the lock file stable across the database lifetime so the kernel releases ownership on process exit. Open status and backup reads without a writer lease. Initialize a missing ledger explicitly and validate identity/schema on every ordinary open. A transaction appends revisions and moves the cursor and provider checkpoint together. The checkpoint preserves the counter baseline, verified logical epoch and ordinals, and the minimum sanitized request prefix for partial reconciliation. Apply only allowlisted fields to the ledger, inbox and checkpoint. Reject extra raw fields before writing any inbox file. Pseudonymize accepted source references before persisting any private or exported record. Store pseudonyms with a project key and include a key identifier in metadata.

- [ ] Write `test_atomic_cursor_and_revisions` with a forced exception between append and cursor advance, a second writer, same-key same-payload retry, and same-key conflicting immutable payload. Assert rollback, writer refusal, lease release on process exit, idempotence and explicit conflict. Verify state permissions and that unsupported schema and mismatched project/key fail before writes.
- [ ] Run `test_ledger.py` to show failure, implement the package, typed ledger and private state initialization, then pass leaf verification.

### U02 — Scope inbox, aliases and rollups

**Files** `src/aitm_usage/{scopes,rollup,cli}.py`, `tests/test_scopes.py`.

**Contract** `enqueue_marker(directory: Path, marker: ScopeMarker) -> MarkerId`, `resolve_scope(observation: Observation, view: LedgerView) -> ScopeResolution`, and `rollup(root: ItemKey, view: LedgerView) -> UsageRollup`. The private inbox uses atomic file publication. Require a monotonic per-session scope sequence and proof the marker was published before its effective request or turn boundary. Validate against the SourceBoundary contract using fixtures in this leaf. A boundary may be proven for a candidate session under an approved source root before that session is enrolled. Candidate evidence carries no usage into the ledger. Admission covers only the explicit eligible segment after a proven marker. U04 and U05 provide real boundaries and U08 connects them. A late scan can resolve an already-published marker. A marker created after a claimed boundary can affect only a later verifiable boundary, and an explicit correction appends a revision. Return pending until the enrolled adapter validates the boundary, then commit the marker and return an accepted receipt. A supported serial request marker precedes the first child response in provider order. A turn-only marker is emitted before the child turn begins. Enrollment binds the explicit owner provider session and generation. A same-story marked reviewer keeps its own role and an unproven session is unassigned. Consume into the ledger before acknowledging. Expose scope mark, development bind, scope correct, alias and parent operations through the CLI.

- [ ] Write `test_planning_scope_and_development_owner` with one epic and two children in a single session. Verify first child request and switch-back for marker-first and observation-first arrival, Unknown while unresolved, scope before the next turn when the request boundary cannot be proven, owner-only development default, unmarked nonowner, compatible marked reviewer, conflicting marker quarantine, housekeeping and two review roles. Exercise actual CLI marker publication, idempotent inbox replay, recorded correction that preserves an earlier as-of result, invalid retroactive claim, duplicate sequence, draft graduation, cycles and one inclusive total. Price coverage in the rollup uses known Decimal values and a separate unknown count, supplied by a fixture here.
- [ ] Run `test_scopes.py` to show failure, implement the marker and rollup contract, then pass leaf verification.

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

**Contract** `price(usage: UsageObservation, rates: RateCard) -> PriceResult` and `quota_snapshot(raw: QuotaEvidence) -> AccountObservation`, and `account_observations(batch: AdapterResult, rates: RateCard) -> LedgerBatch`. Use Decimal, versioned public rate references and explicit currency. Support the standard rates evidenced in #73 with applicable context and cache classes. Unsupported modes, tiers, models or incomplete category evidence return an Unknown price. Keep actual spend Unknown absent attributable billing.

- [ ] Write `test_standard_rates_and_account_only_evidence` from sanitized #73 vectors. Verify cached input subtraction, supported long-context treatment and Claude cache-write TTL, with reasoning counted once. Check that unknown rates leave tokens visible, a changing same-window quota fixture leaves per-agent burn Unknown, and absent billing evidence remains Unknown.
- [ ] Run `test_accounting.py` to show failure, implement independent price, quota and spend records, then pass leaf verification.

### U07 — As-of export and C44 compatibility proof

**Files** `src/aitm_usage/{export,cli}.py`, `tests/test_export.py`, `tests/fixtures/receiver.py`.

**Contract** `export_as_of(view: LedgerView, rate_card: RateCard, destination: Path) -> ExportReceipt`. Snapshot a fixed ledger sequence. Produce deterministic UTF-8 JSONL and manifest with schema, project, cutoff and digest. Export stable pseudonymous source keys, observation revisions, explicit scope revision references, availability, and the immutable rate-card identifier and pricing basis using an allowlist. Do not include local paths, raw handles, key material or provider content. Receiver fixture models the C44 `ingest_usage(source, payload)` seam. Persist per-key accepted payload digests, pending and reconciliation dispositions and the watermark in a temporary SQLite receiver.

- [ ] Write `test_replay_cutoff_and_pending_finalization` with interrupted import, a withheld partial later finalized after restarting a fresh receiver from its durable watermark, a scope or pricing revision after acceptance, and a conflicting payload. Assert accepted identical retries are idempotent, pending keys survive advancing watermarks, corrections queue, and conflicts preserve prior acceptance. Verify identical fixed-cutoff exports after late ledger changes and a changed versioned price basis yields a distinct manifest.
- [ ] Run `test_export.py` to show failure, implement deterministic export and the compatibility fixture, then pass leaf verification. Actual Core adapter adoption is a later reviewed integration.

### U08 — Continuous service and status

**Files** `src/aitm_usage/{service,cli}.py`, `tests/test_service.py`.

**Contract** `collect_once(registration: Registration, ledger: Ledger) -> CollectionReport` and `run_service(registration: Registration, interval_seconds: int = 15) -> int`. Wire actual providers, cursors, inbox and heartbeat in the same process. An explicit register command pins approved roots, permitted checkout/worktree anchors, and the activation cut-off before scanning. Apply U06 accounting to each committed adapter batch and expose U02 task and feature rollups with tokens, known price and Unknown coverage. A restart reloads the registration without resetting the cut-off. `status --json` reports version, heartbeat, interpreter version, per-source watermarks, observed-through time, lag, known retention limits and coverage. Poll local sources without model calls. Restart from durable state.

- [ ] Write `test_service_restart_and_coverage` through the actual service entry point with temporary project roots and both providers. Simulate permission loss, incomplete rows, missed scans and restart. Assert processed inputs catch up once, stale source lag remains distinct from live heartbeat, and service diagnostics remain sanitized. Drive both actual adapters and the real marker inbox with valid observations and malformed inputs containing synthetic canary handles, paths, prompt and tool fields. Assert valid observations and checkpoints were durably written, then scan the observation tables, provider checkpoints, rejected-marker paths and inbox bytes for canaries. Require only allowlisted pseudonyms and diagnostics. Drive the actual collector path from a readable unbound candidate with zero observations, through a proven reviewer marker, to one enrolled segment while earlier and later unrelated segments remain excluded. Verify through the installed CLI or its real command dispatch that measured tokens and known price reach task and epic rollups, Unknown price preserves token counts, and quota and billed spend remain separate records.
- [ ] Run `test_service.py` to show failure, implement loop, read-only status and recovery behavior, then pass leaf verification.

### U09 — LaunchAgent install, upgrade and restore

**Files** `src/aitm_usage/{install,backup,cli}.py`, `tests/test_install.py`.

**Contract** `install_agent(project: Registration, executable: Path, launchctl: LaunchControl) -> InstallReceipt`, `backup(ledger: Ledger, destination: Path) -> BackupReceipt`, and `restore(source: Path, destination: Path, expected: LedgerIdentity) -> RestoreReceipt`. Plan and apply explicit install, stop and upgrade actions. Put RunAtLoad, KeepAlive and the absolute versioned executable in the plist. Upgrade backs up state before activation and restores the previous compatible service registration on failure. Restore only into a stopped target under the same writer lock and replace state atomically after validation. Validate absolute paths, ownership and installed version. Use the SQLite backup API and capture the associated private pseudonym key in the same protected backup bundle. Verify project/key identity before restore. Preserve ledger and key when stopping or uninstalling.

- [ ] Write `test_owned_launchagent_and_recoverable_upgrade` with a fake launchctl and temporary state. Check correct plist paths, RunAtLoad, KeepAlive and 15-second polling, idempotent install, failure before activation and failure of the new launch leaving the prior service recoverable, stop and uninstall preserving data, wrong-key and wrong-project restore refusal, and stable pseudonyms and same-cutoff export parity after a supported restore with the backed-up key. Verify that an unsupported schema refuses the upgrade before data mutation.
- [ ] Run `test_install.py` to show failure, implement installation and backup operations, then pass leaf verification.

### U10 — Qualification validator and on-host runbook

**Files** `README.md`, `src/aitm_usage/{qualification,cli}.py`, `tests/test_activation_receipt.py`, `tests/fixtures/activation/receipt.json`.

**Contract** `validate_activation_receipt(receipt: ActivationReceipt) -> QualificationResult`. Expose the validator as `aitm-usage qualify --receipt <file> --json`. The on-host runbook uses that installed command, both observed local provider routes and actual launchd. Require approved project scope, collector version, both provider routes and client versions, heartbeat, source watermarks, private state permissions, unattended startup, restart and supported backup/upgrade rehearsal, coverage, sanitized sample keys and export parity. Store the approved sanitized live receipt with #83 on `planning`.

- [ ] Write `test_activation_requires_live_both_providers_and_parity` for fixture-only, stale heartbeat, one missing provider, missing scopes, duplicate records after restart, and receipt privacy. Require correct proof from one real shared planning session with epic hydration and at least two child scopes, overlapping author and reviewer, including graduation and the inclusive rollup, and authorized development and housekeeping. Development ownership can be exercised in a controlled worktree with a clearly labeled proof basis.
- [ ] Run `test_activation_receipt.py` to show failure, implement validation and runbook, then pass leaf verification.
### U11 — Project Mac activation and dogfood proof

**Files** `README.md` and the sanitized receipt at `.aitm/stories/000/83/attachments/activation-receipt.json` on planning. U10 supplies the installed qualification command and tests.

- [ ] After execution and activation are authorized, install the reviewed package on the project Mac. Observe unattended launchd startup, verify restart catch-up, rehearse supported backup and upgrade with verified recovery and same-cutoff parity, exercise the real routes including supported nested work, model/effort changes and retry evidence or explicit coverage gaps, and validate and publish the receipt with the version, dated evidence and digest. Demonstrate an export replay without duplication and that Unknown remains visible.
- [ ] Verify that the collector is active and coverage is current before authorizing C01 pickup. The same service and ledger continue when Core is released and when C44 starts accepting compatible usage.

## Scope after activation

The collector remains active for AITM. Core's later adoption adds workflow-supplied scope markers and a qualified C44 import, with export parity before switching any consumer. UI, issue presentation, billing connectors, forecasts and additional capture environments can evolve from the same observations. This plan covers the initial delivery of the enduring producer and ledger.
