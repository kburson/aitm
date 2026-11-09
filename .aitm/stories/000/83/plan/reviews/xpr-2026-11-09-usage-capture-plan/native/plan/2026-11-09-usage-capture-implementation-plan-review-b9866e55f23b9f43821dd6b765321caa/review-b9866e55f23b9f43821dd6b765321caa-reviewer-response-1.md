<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-b9866e55f23b9f43821dd6b765321caa"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
artifact_commit: "276b85a797c2d72a9919d2d06a2f1b48f8e7c478"
artifact_blob: "6eede19cdef846e435bdc17d094ccf2ef42494e1"
artifact_digest: "sha256:d4c46b81bb889277cd5a8563251317bfa15788081e9471c4a014d473eb378cdb"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:e57e6bd4e0710d76019f34694d7770a7c6f05803339de1ab2574fa46eddeaab4"
  identity_source: "runtime"
started_at: "2026-11-09T14:33:55.533Z"
submitted_at: "2026-11-09T14:37:10.995Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent XPR review, turn 1, of `.aitm/stories/000/83/plan/usage-capture-implementation-plan.md` at the sealed digest `sha256:d4c46b81bb889277cd5a8563251317bfa15788081e9471c4a014d473eb378cdb` (commit `276b85a`, blob `6eede19`).

Read evidence. The Read tool returned eight contiguous ranges of the plan: lines 1–20, 21–40, 41–60, 61–80, 81–100, 101–120, 121–140 and 141–151. A line count reports 150 newline-terminated lines. The last range reached EOF at line 151, which is an empty line. No output was truncated or replaced with an omission marker. This full-file review covers every section, including sections that did not change during the SAR and SPR rounds. This is the first turn of this review, so no prior response for this review ID exists and no dispositions need verification. For context only, I read the accepted design `.aitm/stories/000/83/design/usage-capture-design.md` in three contiguous ranges (lines 1–20, 21–40 and 41–51, through EOF, with no truncation). I also read lines 18–25 of the #73 report and the turn-1 reviewer response from the design XPR, which I used only for format. I did not rely on the conclusions of the earlier SAR or SPR rounds. I could not run commands outside the review join and submit commands, so I did not recompute the design digest cited on plan line 11.

Assessment by area:

- **Exact design coverage.** Coverage is broad and traceable. The plan covers the activation cut-off and delayed first scan (U03 and U08), segment eligibility and enrollment (U02 and U03), physical versus logical streams and archive continuity (U03), Codex epochs and aggregate spans (U04), and Claude revisions, terminal reconciliation and nested overlap (U05). It also covers Decimal pricing with Unknown, independent quota and spend records (U06), as-of export with an immutable receiver that tracks pending and reconciliation state (U07), status fields (U08), LaunchAgent, backup API, key-bound restore and refusal of unsupported schemas (U09), and the activation receipt (U10 and U11). The review focus list on lines 22–28 matches the riskiest parts of the design. The gaps in coverage are F1 (the writer lease versus "manual collection" and runtime binding updates, design line 17), F2 (the session reference for markers, design line 23) and optional items O1 and O2.
- **Prerequisites.** The dependency table is consistent and acyclic. The hour total is correct: 4+4+3.5+4+3.5+3+3.5+3.5+4+3.5+3.5 = 40. U08's dependency on U03–U05 is transitive through U06 and U07. The CLI serialization order on line 48 matches the predecessors. Two prerequisites are missing: how each agent obtains its own provider session reference (F2), and how the dedicated versioned environment and the upgrade-rehearsal version are produced (F5).
- **Public entry points.** The Python contracts are explicit. The CLI surface is only partly named. See F3.
- **Fresh restart, privacy and on-host qualification proof.** U04 and U05 restart from durable checkpoints in a fresh process, and U07 restarts a fresh receiver. U08's restart and canary proof are scoped too narrowly (F4). U10 and U11 name the right receipt contents, but U11 does not name the real work that will produce the required planning and graduation evidence, or its sizing basis (F7).
- **Delivery leaves of at most four hours.** Every leaf is nominally 4 hours or less. U08 bundles enough distinct contracts and end-to-end proofs that 3.5 hours, including source review and delivery evidence, is not credible (F6). U02 is similarly dense (O4).
- **Review outcome versus project policy.** Line 20 and U11 treat installation and the live receipt as later execution authority. Line 50 correctly frames estimates as inputs to each leaf's own JIT qualification. The findings below are outcomes of this review only. They do not propose project-wide policy.

Seven required findings and six optional suggestions follow.

## Findings

1. **F1 — Required — The process-lifetime writer lock conflicts with CLI mutations and new worktree anchors during continuous operation (lines 56, 65, 119 and 128; design lines 17 and 26).** U01 acquires "a nonblocking process-held exclusive file lock per project before any write path," and the lock is released on process exit. The U08 service runs continuously under KeepAlive, so in normal operation it holds that lock permanently. U02 exposes "development bind, scope correct, alias and parent operations through the CLI." U08 adds an explicit `register` command that pins approved roots and checkout or worktree anchors. The plan does not say whether these commands write the ledger directly, which the nonblocking lock would refuse while the service runs, or go through the private inbox that the service consumes. Each story from Develop onward gets a fresh dedicated worktree (design line 26), so a new worktree anchor or development binding must be added while the collector is live. As written, that requires stopping the service, which opens a collection gap, or bypassing the lease. The design's lease "covers manual collection," but the plan names no manual-collection command and no rule for how it coexists with the running service.
2. **F2 — Required — The marker's session reference and its boundary-ordering evidence are unspecified (lines 24–25, 65 and 67; design line 23).** U02 requires "proof the marker was published before its effective request or turn boundary," and enrollment "binds the explicit owner provider session and generation." The plan does not say how an agent running in Codex or Claude Code obtains its own provider session reference to put in the marker. The #73 evidence (report lines 22–24) recovers session IDs from log files after the fact. It does not establish a self-identification route available to the running agent. The plan also does not name the evidence that orders a marker against a provider boundary. Candidates include inbox publication time compared with provider row timestamps on the same host clock, or the transcript's own tool-call record of the marker command. Without either, U02's fixtures can pass against a synthetic `SourceBoundary` while the real routes in U11 cannot produce provable markers. Every child or reviewer attribution would then fall to Unknown, and review focus item 2 would be unproven.
3. **F3 — Required — The public CLI surface and console entry point are incompletely named (lines 48, 65, 110, 119, 128 and 137).** Only `status --json`, `qualify --receipt <file> --json`, a `register` command and the operation nouns in U02 are named. The plan does not name these:
   - the console script declared in U01's `pyproject.toml` (`aitm-usage` appears only in U10);
   - the long-running service command that U09's plist `ProgramArguments` invokes (`install_agent` takes only `executable: Path`);
   - the export command (U07 edits `cli.py` but names no command);
   - backup, restore, stop, uninstall and upgrade commands (U09 says "plan and apply explicit install, stop and upgrade actions" but tests uninstall and restore without naming them);
   - a manual collect-once command (see F1);
   - the task and epic rollup report command that U08's test exercises "through the installed CLI."

   The U10 runbook and U11 on-host steps depend on these exact commands, and line 48 serializes CLI edits by leaf. Unnamed commands leave each leaf free to choose names and argument shapes, and the runbook cannot be validated against them.
4. **F4 — Required — The privacy canary proof misses export, status, logs and raw database bytes, and the restart is not specified as a fresh, abruptly terminated process (lines 112 and 121; design line 49).** U08 scans "the observation tables, provider checkpoints, rejected-marker paths and inbox bytes" for canaries. That scope misses other tables (diagnostics, cursors, registration and scope revisions), SQLite WAL or journal files and residual pages, private log files, `status --json` output, the U07 export JSONL and manifest, and the U09 backup bundle apart from the key. U07's test has no privacy assertion on export output at all, even though the design requires that exports contain no private content. Separately, U08 says "simulate … restart" without requiring a separate OS process that is killed abruptly between scans and within an uncommitted batch. That case is what proves lock release, transactional checkpoint durability and catch-up exactly once under real crash conditions. U01's "lease release on process exit" proves only the lock, and only in isolation.
5. **F5 — Required — Provisioning of the versioned environment and the upgrade-rehearsal target is unspecified (lines 16, 128, 130 and 145; design line 17).** The plan requires "a dedicated versioned environment and absolute interpreter and application paths," and requires that a failed new launch leave the prior service recoverable. The prior service is recoverable only if each version's environment exists side by side and is not replaced in place. No leaf says how the environment is built, for example from a locked wheel into a per-version directory under the private state root, where it lives, or when old versions are pruned. U09's fake-launchctl test can pass without any real environment. U11 must "rehearse supported backup and upgrade," but nothing produces a second installable version to upgrade to or a version to roll back to.
6. **F6 — Required — U08 exceeds a credible 3.5-hour leaf (lines 115–122).** U08 delivers registration persistence and the `register` command, `collect_once` wiring of both adapters, U06 accounting and the inbox, `run_service`, `status --json` with eight field groups, and rollup exposure through the CLI. Its single test also has to prove permission loss, incomplete rows, missed scans, restart catch-up, separation of lag from heartbeat, a canary scan of every persisted surface, the candidate→reviewer-marker→enrolled→excluded path, and price, quota and spend separation through the real dispatch. The leaf estimate also includes source review and delivery evidence (line 32). These are several independently verifiable contracts. A shortfall here would push back U09–U11 and the C01 gate.
7. **F7 — Required — U11 does not name the real work that supplies its qualification evidence, or the basis for its 3.5-hour estimate (lines 139, 145 and 146; design lines 46 and 50).** U10 requires the receipt to show "one real shared planning session with epic hydration and at least two child scopes, overlapping author and reviewer, including graduation." U11 must also exercise nested work, model or effort changes and retry evidence on real routes. That depends on real planning work, including a draft graduating to an issue, happening during the activation window. The plan does not identify that work, for example a named epic's child planning. It also does not say whether the duration of the observed work is excluded from the 3.5 hours, or what happens if no qualifying graduation occurs before C01 is due. Because the receipt gates C01 entering Develop, an unidentified source of evidence is a sequencing risk that cannot be detected until U11.

## Required changes

1. **F1:** In U01 and U02, state the mutation path. Either (a) every CLI mutation (scope mark, development bind, correct, alias, parent and anchor or registration updates) is published to the private inbox, and the lease holder consumes and acknowledges it, or (b) the lock is held per transaction with a bounded blocking wait instead of for the process lifetime. State how a new dedicated worktree anchor is admitted while the service runs without a collection gap. Name the manual collect-once command and its behavior while the service holds the lease, for example refusing with a clear diagnostic or delegating to the service. Add a U02 or U08 test that performs a bind, a correction and an anchor addition while a live service process holds the lease.
2. **F2:** In U02, or in a named prerequisite, state for each provider (Codex and Claude Code) how the running agent obtains the session reference it passes to the marker command, together with the evidence that orders the marker against a request or turn boundary. If a route cannot self-identify, state the fallback, such as a turn-boundary marker or a launcher-supplied binding, and state that unresolved cases remain Unknown. Add a U10 receipt requirement and a U11 step that qualify this mechanism on both real routes, including at least one marker-first and one observation-first arrival.
3. **F3:** Add a command table, or one sentence per leaf, that names each CLI command and its owning leaf. It should include the U01 console script, the U02 scope commands, the U07 export command, the U08 register, collect-once, service-run, status and rollup commands, and the U09 install, upgrade, stop, uninstall, backup and restore commands. State the exact plist `ProgramArguments`, and require U10's runbook to use only those commands.
4. **F4:** Change U08's canary assertion to scan every byte under the private state directory, including the SQLite database with its WAL or journal files, logs and the inbox and rejected areas. The scan must also cover `status --json` output, a U07 export (JSONL and manifest) and a U09 backup bundle, with the pseudonym key excluded only as a known secret. Add an export privacy assertion to U07's test. Require U08's restart to run the service as a separate process, terminate it with SIGKILL both between scans and during an uncommitted batch, and prove lock release, no partial commit and catch-up exactly once.
5. **F5:** In U09, state how a versioned environment is built (source artifact, location under the private state root, interpreter pin) and that versions coexist until a successful upgrade is verified, with a stated pruning rule. Add a test that rollback re-points the plist to the still-present prior environment. In U11, name how the upgrade-rehearsal target version is produced, for example two tagged builds of the reviewed package.
6. **F6:** Split U08 into at least two leaves of 4 hours or less. For example, U08a could cover registration, `collect_once`, status and rollup CLI with restart catch-up, and U08b could cover the continuous loop with the end-to-end enrollment path and the full canary and crash proofs. Update the dependency table, the CLI order on line 48 and the hour total. Alternatively, justify the 3.5-hour estimate against the listed proofs and move some proofs to an existing leaf with spare capacity, without exceeding 4 hours.
7. **F7:** In U11, name the planned real work expected to supply the required planning-session, graduation and overlapping-review evidence. State that the duration of that observed work is outside U11's estimate. State the fallback, for example a controlled real session with a clearly labeled proof basis, and its validator treatment in U10, if no qualifying graduation occurs before C01 pickup.

## Optional suggestions

1. **O1:** The design (line 36) allows "optional explicitly invoked read-only sampling" of quota. State in U06 or under "Scope after activation" that V1 records inline quota observations only and defers sampling, so the omission is explicit.
2. **O2:** The ledger must last the life of the project, so a schema-version record and migration hook (back up, migrate, validate) in U01 or U09 would cover the design's "versioned migration" branch. The plan currently tests only the refusal branch. A trivial v1→v1′ test migration would prove the path before the first real migration is needed.
3. **O3:** Name the private state root, for example under `~/Library/Application Support/aitm-usage/<project-uuid>/`, along with its permission mode. Also state the SQLite journal mode (WAL) and busy-timeout policy, because status and backup readers run alongside the live writer.
4. **O4:** U02 at 4 hours is also dense: inbox, marker validation, enrollment, owner binding, conflicts, aliases, cycles, as-of corrections and rollups. Consider moving aliases, parent links and rollup into a separate leaf if U02's JIT qualification confirms the pressure.
5. **O5:** U10's contract (line 137) says to "store the approved sanitized live receipt with #83 on `planning`," and U11 owns that file (line 143). Keep the storage action in U11 only, so that it has one owner.
6. **O6:** In U06, state explicitly that `AccountObservation` carries a pseudonymous account key, bucket, reset window, source, timestamp and observed precision, matching design line 36.

## Decision

revisions-requested
