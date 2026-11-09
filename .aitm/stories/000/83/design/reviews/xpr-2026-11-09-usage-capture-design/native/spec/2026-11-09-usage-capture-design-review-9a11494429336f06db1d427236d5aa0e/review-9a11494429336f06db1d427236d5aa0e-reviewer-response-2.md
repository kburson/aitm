<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-9a11494429336f06db1d427236d5aa0e"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/000/83/design/usage-capture-design.md"
artifact_commit: "670ce2fbe3e4b3752c38cead1b9c49283d54d591"
artifact_blob: "a8deae9f23ca1c78a62d3c5c8544b7d3f24266cd"
artifact_digest: "sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:d152a032112c1f0a4b7f47ca982a1df6a355843f086c6e3f1eb3b8d62d7a81a9"
  identity_source: "runtime"
started_at: "2026-11-09T14:21:04.838Z"
submitted_at: "2026-11-09T14:24:26.424Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

Independent XPR review, turn 2, of `.aitm/stories/000/83/design/usage-capture-design.md` at the sealed digest `sha256:d716e3bb03ed4622935df0af39fb87891feb4132c1278441ddc3db7fbf0ee8ee` (commit `670ce2f`).

Read evidence. I read the current file afresh with the Read tool in three contiguous ranges: lines 1–20, 21–40 and 41–50. The file has 50 lines, and the last range reached EOF. No output was truncated or replaced with an omission marker. This full-file review covers every section, including sections unchanged since turn 1: "Intent and sequence," the Before Develop and graduation bullets, the Codex, cost and quota bullets, the Core handoff, and the export-handoff and on-host acceptance bullets. I also read the prior response documents for this review: my reviewer response 1 (F1–F4 required, S1–S4 optional) and author response 1, which accepts all four required findings and incorporates all four suggestions. I checked each disposition below against the current text, not against the author's summary.

Disposition verification:

- **F1 (owner and participant binding in a dedicated worktree) — resolved.** Line 26 now says that the owner launcher or the first verified marker explicitly enrolls the provider session and generation in the development binding. An unmarked session with no owner proof stays unassigned. A separate participant marker for the same story and review ID is compatible and records that participant. A contradictory item or owner claim creates a conflict, leaving the affected observations unassigned. This closes the misattribution path for a same-worktree reviewer. Line 47 now exercises both unmarked and explicitly marked nonowner reviewers in the development checkout.
- **F2 (persisted locators versus the pseudonym rule) — resolved.** Line 19 keys file locators and persisted validation anchors with the private project key, rediscovers files by enumerating the approved roots, keeps transcript paths transient and persists only the approved configuration roots. It now states the fixed field allowlist as a design rule that keeps raw absolute paths, current directories and branch names out of exports and diagnostics. Line 40 now specifies "stable pseudonymous source keys." Line 49 continues to verify the rule.
- **F3 (silent loss when a provider format drifts) — resolved.** Line 31 records the observed client and format version on each source and observation and skips only allowlisted non-usage shapes. Unknown or malformed usage shapes, unsupported versions, and turn activity with no recognizable usage now yield explicit coverage gaps and sanitized diagnostics. The line also states that a current watermark or heartbeat cannot hide these gaps in status. Line 47 adds a format-drift exercise.
- **F4 (acceptance coverage for nested agents, model changes and retries) — resolved.** Line 47 now verifies a model or effort switch at a supported boundary, a retried or errored request and observed parent-child agent usage. It also exercises a Claude nested agent and a Codex subprocess or sub-agent where the supported route exposes one, and records explicit coverage gaps where durable provider evidence is missing. This matches #73 recommendation 4.
- **S1–S4 (optional) — incorporated.** Line 17 now covers the writer lease (manual collection, restart and upgrade), the dedicated versioned environment, the interpreter version and known retention limits in `status --json`. Line 50's receipt now names both provider client versions and routes, plus pseudonymous sample keys.

Fresh full-file assessment. The new text introduces no regression or internal contradiction. Line 19's "Store provider request and session identifiers only as stable local keyed pseudonyms" is now consistent with line 31's cursor and anchor requirements. The unknown-attribution bucket (line 25), the unassigned outcomes (line 26) and Unknown items outside attributed totals (line 27) form one consistent fail-visible model. The areas assessed in turn 1 — scope and cutoff, replay, source privacy, worktree and participant binding, failure handling, long-lived operations and transition to Core — have no remaining material gap. Detailed lease takeover after a crash and per-provider marker mechanics belong in the implementation plan, not the design.

This acceptance is the outcome of this review only. Line 50 keeps the activation receipt as a sequencing checkpoint for this project and leaves installation, activation and Core delivery to later execution authority. This review sets no project-wide policy.

## Findings

None.

## Required changes

None.

## Optional suggestions

None.

## Decision

accepted
