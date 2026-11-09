<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9a11494429336f06db1d427236d5aa0e"
role: "reviewer"
turn: 1
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_commit: "e6411995f65df61da29fa737bcfcfa722a8a9265"
artifact_blob: "913cf7e4702c87f79f37ef4e8e9b2bb002bf9396"
artifact_digest: "sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:d152a032112c1f0a4b7f47ca982a1df6a355843f086c6e3f1eb3b8d62d7a81a9"
  identity_source: "runtime"
started_at: "2026-11-09T14:21:04.838Z"
submitted_at: "2026-11-09T14:22:59.391Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent XPR review, turn 1, of `.aitm/stories/000/83/design/usage-capture-design.md` at the sealed digest `sha256:e32c98ded171e8128b088553090ee87a4a851e82c427318392cd362bed5057de` (commit `e641199`).

Read evidence. The Read tool returned three contiguous ranges: lines 1–20, 21–40 and 41–50. The file has 50 lines, and the last range reached EOF. No output was truncated or replaced with an omission marker. This full-file review covers every section, including sections unchanged since the SAR and SPR rounds. This is the first turn of this review, so no prior response exists for this review ID and there are no dispositions to verify. For context only, I also read the story record, the accepted round-2 SAR and SPR reviewer responses, and lines 20–35 of the #73 report (its identity, deduplication, rate-basis and subscription evidence). I did not rely on those reviews' conclusions.

Assessment by area:

- **Scope and cutoff.** Sound. The design names its scope (lines 11 and 13) and excludes viewers, billing reconciliation, forecasts and remote capture. It persists the activation cut-off before scanning, baselines open sessions at the last provable pre-cutoff record, keeps in-flight spans Unknown, assigns revisions to the pre-cutoff request and leaves backfill to separate work (line 19).
- **Replay.** Strong. The design covers source incarnation, byte cursor and validation anchor; partial lines; live-to-archive continuity; quarantined overlap; Codex counter epochs; Claude cumulative revisions; and as-of export replay (lines 31–35 and 40).
- **Source privacy.** Mostly sound. Finding F2 identifies a conflict between the source cursors and the rule that session identifiers persist only as pseudonyms.
- **Worktree and participant binding.** Finding F1 shows that the owner-only default in a dedicated development worktree has no rule for identifying the owner. That gap matters because the peer-review protocol launches reviewers in the same physical worktree.
- **Failure handling and long-lived operations.** Backup, upgrade, migration and rollback are well specified (lines 17 and 42). Finding F3 identifies a silent-loss path when a provider log format drifts. Finding F4 covers missing acceptance evidence for behavior that #73 says the adapters must prove.
- **Transition to Core.** Sound. The design keeps one collector and ledger across integration, makes the ledger authoritative over Core's rebuildable index, uses deterministic as-of exports and handles immutable receivers. It also tracks withheld keys after the watermark moves and adds C44 later through its own qualification (lines 40–42 and 48).
- **Review outcome versus project policy.** Line 50 correctly treats the activation receipt as a sequencing checkpoint for this project and leaves installation and activation to later execution authority. The findings below are outcomes of this review only and do not propose project-wide policy.

Four required findings and four optional suggestions follow.

## Findings

1. **F1 — Required — No rule identifies the owner of an unmarked session in a dedicated worktree (lines 23, 26 and 47).** Line 26 makes a dedicated binding "a default for that owner only," and acceptance line 47 exercises "a nonowner in the development checkout." The design never states how the collector proves that an unmarked provider session belongs to the owner rather than a nonowner. An unmarked session gives the collector only the worktree anchor and the provider session. The ai-peer-review protocol requires reviewers to "join from a distinct session in the same physical worktree." Without a marker, a reviewer session in the development checkout would therefore receive the owner default. Its usage would be credited to the owner's development work, which breaks distinct participant attribution. Line 26 also does not say whether a reviewer marker for the *same* story and review ID counts as a "conflicting marker." If it does, legitimate reviewer usage lands in an attribution conflict.
2. **F2 — Required — Persisted source locators conflict with the pseudonym-only rule for session identifiers (lines 19 and 31).** Line 19 stores provider session identifiers "only as stable local keyed pseudonyms." Line 31 requires a durable source incarnation, byte cursor and validation anchor for each source file. Claude Code transcripts are named by session UUID, and Codex rollout filenames embed the session UUID, so a cursor that stores the raw file path also stores the raw session identifier. The `cwd` and branch fields in both providers' records also reveal home-directory and branch names. Line 40 puts "stable source keys" in the export but does not say that they are pseudonymous. The fixed field allowlist on line 49 is listed only as an acceptance check, not a design rule. An implementer must either break the pseudonym rule or invent a locator scheme that the design does not describe.
3. **F3 — Required — Provider log-format drift can lose usage silently (lines 31–34).** The collector has to run for the life of the project against two client log formats that change between releases. The design creates gaps for replaced files, counter regressions, missing identity and unverifiable overlap. It says nothing about records the parser does not recognize, or sessions that show turn activity but no recognized usage rows. Suppose a Codex release renames `token_count`, or Claude Code moves `usage` into a new envelope. The collector would advance its cursors, record no usage and report a healthy heartbeat with current watermarks. `status --json` (line 17) would show full coverage while measurement had stopped.
4. **F4 — Required — Acceptance omits nested agents, model or effort changes and retries (lines 33–34 and 47).** Line 34 specifies nested-agent handling, and line 33 tracks model and effort with the boundary that supplied them. Recommendation 4 of the #73 report says the harness adapters must prove collection "including retries, model changes, subprocesses and overlapping quota usage." Acceptance line 47 exercises none of these: Claude Code sub-agent or sidechain transcripts, Codex sub-agents, a mid-session model or effort switch, or a retried or errored request. Parent-total versus child-detail double counting and per-boundary model pricing are the riskiest accounting paths for an inclusive rollup, and they would ship without qualification evidence.

## Required changes

1. **F1:** In "Work scopes," state how the owner's provider session or sessions become bound to a dedicated development binding. For example, the owner's launcher or first marker enrolls the session, so the binding is not inferred from the worktree alone. State that an unmarked session in a dedicated worktree that is not proven to be the owner's receives the story scope with participant Unknown, or goes to the unknown bucket. It must never receive the owner default. State that a marker for the same story from a different participant, such as a reviewer carrying the review ID and role, is compatible and is recorded as that participant. A marker that names a different item or contradicts the binding is the conflict case. Extend the line 47 nonowner exercise to cover both an unmarked and a marked reviewer session in the development checkout.
2. **F2:** In "Local collection and operation," choose and state one locator rule. Option (a): file locators and anchors live only in the private per-user ledger, which is explicitly allowed to hold raw paths, and every export and diagnostic carries only keyed pseudonyms. Option (b): the ledger keys cursors by a keyed pseudonym of the locator and rediscovers files by enumerating the allowlisted roots. Either way, state that the export's "stable source keys" are keyed pseudonyms. State that `cwd`, absolute paths and branch names are excluded or pseudonymized in exports and diagnostics. Move the fixed field allowlist from acceptance into the design.
3. **F3:** In "Provider records and accounting," require each adapter to record the provider client or format version for each source and observation. An unrecognized usage-bearing or unknown record shape, an unsupported version, or a session with recognized turn activity but no recognized usage should open an explicit coverage gap with a diagnostic, rather than being skipped. Require `status --json` to surface the gap so that drift degrades visibly. Add a format-drift fixture to acceptance.
4. **F4:** Extend acceptance line 47 to exercise a Claude Code nested sub-agent, including the case where a parent total already contains the child, and a Codex sub-agent or subprocess session where present. Also cover a mid-session model or effort change priced at the correct boundary, and a retried or errored request that is neither double-counted nor dropped. If one of these cannot be produced on the supported surfaces, say that it remains an explicit coverage gap.

## Optional suggestions

1. **S1 — Optional — Single-writer guard.** State that only one collector process may write to a ledger at a time, for example through a lock or lease checked at startup. This prevents an upgrade overlap or a manual `collect` run from racing the LaunchAgent. Per-source transactions limit the damage, but a guard keeps that case out of the diagnostics.
2. **S2 — Optional — Source-retention check.** Claude Code prunes local transcripts after its configured cleanup period, and Codex archives and rotates rollouts. Have `status --json` or install report the effective retention settings and warn when a heartbeat gap approaches them. Otherwise, catch-up after a long outage can lose history without a per-session gap record.
3. **S3 — Optional — Interpreter stability.** The plist pins absolute interpreter paths. Install into a dedicated virtual environment or a versioned interpreter path that survives package-manager upgrades, and include the interpreter version in `status --json`.
4. **S4 — Optional — Receipt detail.** This review independently agrees with the SPR suggestion: have the line 50 activation receipt name the provider client versions observed and a sample of pseudonymous observation keys, so later reprocessing can be compared with it.

## Decision

revisions-requested
