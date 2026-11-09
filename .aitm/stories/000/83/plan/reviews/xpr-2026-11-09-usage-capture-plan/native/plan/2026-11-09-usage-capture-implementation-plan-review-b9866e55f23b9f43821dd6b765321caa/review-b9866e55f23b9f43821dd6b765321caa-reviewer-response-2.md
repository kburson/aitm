<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-b9866e55f23b9f43821dd6b765321caa"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/plan/usage-capture-implementation-plan.md"
artifact_commit: "cc1dc6c099cbd3ad7282feea51c8725f94491437"
artifact_blob: "a31e8b1db2a9536495629a11f5995dc97bcc1cfb"
artifact_digest: "sha256:07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:e57e6bd4e0710d76019f34694d7770a7c6f05803339de1ab2574fa46eddeaab4"
  identity_source: "runtime"
started_at: "2026-11-09T14:33:55.533Z"
submitted_at: "2026-11-09T14:40:41.348Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent XPR review, turn 2, of `.aitm/stories/000/83/plan/usage-capture-implementation-plan.md` at the sealed digest `sha256:07919dde4475310b7fe277791206f611ce5cd615eeaed491d3a619e61142daf5` (commit `cc1dc6c`, blob `a31e8b1`).

Read evidence. I freshly read the full current file with the Read tool in ten contiguous ranges: lines 1–20, 21–40, 41–60, 61–80, 81–100, 101–120, 121–140, 141–160, 161–180 and 181–191. A line count reports 190 newline-terminated lines. The last range reached EOF at line 191, which is an empty line. No output was truncated or replaced with an omission marker. This full-file review covers unchanged sections (lines 1–28 and U03–U06) as well as revised ones. I also read the prior response documents for this review: my turn-1 reviewer response (findings F1–F7 and O1–O6) and the author's turn-1 response. I verified each disposition below against the current plan text, not against the author's summary. The accepted design `.aitm/stories/000/83/design/usage-capture-design.md` remains the context I read in turn 1 (lines 1–51 through EOF). I could not run commands outside join and submit, so I did not recompute the design digest cited on line 11.

Verification of required dispositions:

- **F1 — Resolved.** Line 67 states that initial registration takes the exclusive lease before the service starts. While the service is running, markers, bindings, corrections, aliases, ancestry and new worktree anchors are written as typed inbox commands, which the lease holder validates, appends and acknowledges by command ID. A repeat with conflicting bytes is rejected. A second `collect-once` refuses with `writer-active`. Readers use a snapshot, and restore and upgrade follow U09's stopped-writer protocol. Line 63 adds `source add-anchor`, and U13 (line 93) routes alias and parent commands through the inbox. U08's test (line 149) queues and acknowledges a bind, a correction and an anchor addition while the same service keeps its writer lock, and verifies the `collect-once` refusal.
- **F2 — Resolved.** Line 84 names a session-reference source for each route: Codex `CODEX_THREAD_ID` checked against enrolled rollout metadata; a Claude Code launcher that reserves `--session-id` and verifies the init or transcript identity; and a broker-launched reviewer's verified launch or join identity. Line 84 also names the ordering evidence: an opaque command receipt in a recognized serial tool call and result before the next request boundary, otherwise a pre-turn marker for the next verifiable turn. It states explicitly that timestamps alone do not prove order, keeps unverifiable claims pending or Unknown, and retains no raw tool content. Line 175 requires the validator to see verified marker evidence on both provider routes, including marker-first and observation-first processing. U12 (line 158) exercises both arrival orders end to end.
- **F3 — Resolved.** Lines 54–65 add an installed command contract: the `--project` prefix, the console script `aitm-usage = aitm_usage.cli:main`, and the owning leaf for each subcommand. That covers scope, alias and parent, export, register, add-anchor, collect-once, service run, status, rollup, install, upgrade, stop, uninstall, backup, restore and qualify. Line 166 fixes the plist `ProgramArguments`. The CLI edit order on line 50 includes U13.
- **F4 — Resolved.** U12 (lines 156–159) runs the service as a separate OS process. It sends SIGKILL once between scans and once after an append inside an uncommitted batch, then asserts lock release, rollback and catch-up exactly once in a fresh process. It byte-scans all private state (SQLite with WAL or journals, logs, cursor, inbox and rejected files), status JSON and export JSONL and manifest, excluding only the known key. U07 (line 140) adds canary checks on the export. U09 (line 168) scans the backup bundle.
- **F5 — Resolved.** U09 (line 166) builds `versions/<version>-<wheel-digest>/` from a verified wheel and a pinned Python 3.13+ interpreter without runtime dependency resolution. It keeps the prior environment through upgrade and receipt verification and prunes only inactive, explicitly selected versions that have a retained recovery wheel and backup. The U09 test (line 168) uses two side-by-side environments to prove a rollback re-points the plist. U11 (line 184) builds a recorded-digest rehearsal wheel that changes only the version, and rehearses in isolated state before production install.
- **F6 — Resolved.** U08 is now service, live commands and status (lines 143–150). Integrated crash, enrollment and privacy proof moved to U12 (4 h), and aliases, ancestry and rollups moved to U13 (2.5 h). The table (lines 34–48) lists 13 leaves, and the stated 46-hour total is correct: 4+3.5+2.5+3.5+4+3.5+3+3.5+3.5+4+4+3.5+3.5 = 46. Every leaf is 4 hours or less. Predecessors remain acyclic: U13 after U02; U07 after U13 and U06; U12 after U08; U09 after U12. U12 edits only `service.py` and tests, so it correctly stays out of the CLI serialization order.
- **F7 — Resolved.** U11 (line 183) names Core #2 child preparation for C01/#3 and C02/#4 as the normal shared-chat source where separately authorized. Its fallback is a controlled real Codex planning session with an epic and two draft children, using disposable scoped identities for graduation labeled as controlled, and an overlapping normal Claude review. Line 183 excludes the observed work time from the 3.5-hour estimate and keeps the C01 checkpoint open if neither route produces enough evidence. U10 (line 175) validates labeled real controlled or normal evidence and rejects fixture-only evidence.

Optional dispositions: O1 was adopted at line 129, which limits V1 to inline or structured observations and makes sampling later work. O2 was declined with a rationale consistent with design line 42, which permits refusal of unsupported schemas. Line 168 now states same-schema version changes only. O3 was adopted at line 56 (state root, modes, WAL and busy timeout). O4 was adopted as U13. O5 was adopted: U10 line 175 no longer stores the receipt. O6 was adopted at line 129.

Area assessment for this round: design coverage, prerequisites, public entry points, fresh restart and privacy proof, on-host qualification and leaf sizing now meet the review bar. The remaining items below are optional. Acceptance here is the outcome of this review only and does not set project-wide policy.

## Findings

No required findings remain. The following minor, non-blocking observations come from the full-file read:

1. **N1 — Optional — Stale rollup references after the U13 split (lines 87 and 147).** U02's run step still says "implement the marker and rollup contract," but rollup now belongs to U13. U08's contract still says "expose U02 task and feature rollups," but these are now U13 rollups.
2. **N2 — Optional — The Claude "controlled launcher" has no owning leaf (line 84).** Line 84 relies on a launcher that reserves `--session-id` for Claude Code author or owner sessions that the broker does not launch. The command table names no launcher command, and no leaf names a runbook procedure for it. Qualification does not depend on it, because U11 uses a broker-launched Claude review and the unproven case falls back to Unknown. Without it, though, Claude-authored planning or development usage outside the broker would remain Unknown for the life of the project.
3. **N3 — Optional — Formatting (lines 178–179).** No blank line separates U10's last checklist item from the `### U11` heading. Most renderers still show the heading, but the layout is inconsistent with the rest of the plan.

## Required changes

None.

## Optional suggestions

1. **N1:** On line 87, change "marker and rollup contract" to "marker and binding contract". On line 147, refer to U13 rollups.
2. **N2:** Assign the Claude launcher procedure to U10's runbook, or add a small launcher command to the command table. For example, the runbook step could reserve a UUID, start `claude --session-id <uuid>` and publish the matching `scope mark`. That would give non-broker Claude work a documented enrollment route.
3. **N3:** Add a blank line before `### U11` on line 179.

## Decision

accepted
