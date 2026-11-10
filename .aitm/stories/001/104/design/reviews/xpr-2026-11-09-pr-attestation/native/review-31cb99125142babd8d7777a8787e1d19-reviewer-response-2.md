<!-- ai-peer-review-template version="1" digest="sha256:78e9a634af9d540baaf6790db82952eaf39cf7ab59a6cdc7938319ae07a4cbed" -->

<!-- protected-frontmatter -->

---
schema: "ai-peer-review.response/v1"
review_id: "review-31cb99125142babd8d7777a8787e1d19"
role: "reviewer"
turn: 2
commit_mode: "normal"
authority_assurance: "unavailable"
artifact_path: ".aitm/stories/001/104/design/github-tested-merge-binding-replan.md"
artifact_commit: "eb8ab8f471f33cdc52c1e67e01283ab8bc50cdd2"
artifact_blob: "9d6cd7ed0c822f4f70a9f1a3e0eddb20ac9627cc"
artifact_digest: "sha256:c5771f307d55aafe79d8dcb6fed4940f5d1dbdda2ee9e2eb616f208215abedf0"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  model_display: "claude-opus-5-5"
  session_fingerprint: "sha256:19aba777a140232c905945ba92b3184a1498366bb62ff2b21341e5c323631b7f"
  identity_source: "runtime"
started_at: "2026-11-10T04:18:50.207Z"
submitted_at: "2026-11-10T04:25:30.798Z"
finding_ids: []
answered_finding_ids: []
acknowledged_supplement_ids: []
---

Mode: `normal`

## Summary

**Read coverage.** I freshly reread the complete exact revised artifact `.aitm/stories/001/104/design/github-tested-merge-binding-replan.md` (blob `9d6cd7ed…`, commit `eb8ab8f`) through EOF in contiguous chunks of at most 20 lines: lines 1–20, 21–40 and 41–43. A line count returned 42 lines, so line 42 is the last line with content. Line 43 is the empty read past the final newline. I also read the relevant dispositions in full: the author response `review-31cb99125142babd8d7777a8787e1d19-author-response-1.md` (lines 1–55) and my turn-1 findings in `reviewer-response-1.md`. The #104 design (`design.md`, lines 1–13) was read in full in turn 1. This revision does not change the design, and the replan still points to the same parent. I used no Git, no network access and no shell commands except the prescribed submit.

**Disposition review.**

- **Finding 1, attestation availability and publication: resolved.** Line 11 now records that GitHub reports the repository as public. It also requires a visibility and entitlement preflight before any probe, and stops the route as infeasible if the repository is private or internal without GitHub Enterprise Cloud. Line 33 separates three things: the attempt archive, the repository attestation record and the permanent public Rekor entry. It lists the exposed metadata (repository, workflow path, merge ref/SHA, run ID and attempt, runner type and signing time) and the public subject digest. It states that disabling registry and linked-artifact storage still leaves attestation and transparency publication in effect. It requires separate future authorization for the single diagnostic and for recurring PR signing, and returns to Planning if either authorization is missing. Line 37 has the diagnostic record which Sigstore instance, trusted root and timestamp verified the bundle.
- **Finding 2, signer download and permission budget: resolved.** Line 32 now budgets `actions: read` and limits it to authenticated archive metadata. The artifact ID and SHA-256 digest come only from the reviewed collector's pinned upload outputs. The signer re-checks the run ID, the literal `aitm-ci-collector-a<attempt>` name, expiry, size and digest by ID. It downloads by the validated ID with `skip-decompress: true` and digest mismatch set to error, then recomputes the digest before a fixed, allowlisted extraction. Line 32 also states that a shared run namespace gives no uploader authority, and that a collision fails without substitution. Line 25 adds a per-attempt name allowlist, makes a collision, duplicate or unexpected artifact a hold, and says only the verified invocation and signed subject digest bind the bytes to the attempt. Line 37 requires the diagnostic to use the same two-job boundary and raw handoff. So if the pinned downloader cannot provide these inputs, the probe stops before production work.
- **Finding 3, rerun semantics and partial-rerun detection: resolved.** Line 26 states that reruns keep the original event SHA and ref, and that a full rerun is eligible only while that merge is still the live merge. Line 27 makes a new `synchronize` or an authorized `reopened` the only refresh after any movement, and states that a rerun or metadata edit cannot refresh the candidate. This matches the parent's SPR-CI02 rule. Line 23 gives the detection rule: every required job in `/attempts/<n>/jobs` must match `run_id` and `run_attempt` and must start at or after the attempt's authenticated `run_started_at`, and carried-over successes hold the gate. Line 39 adds "carryover after partial rerun" to the #105 negative fixture matrix.

**Turn-1 optional suggestions.** All three were adopted, each within its stated limit:
- Line 37 allows a full rerun in the diagnostic only when specifically authorized and within budget, and it does not replace the fresh-event rule.
- Line 37 rechecks the live merge ref and the PR field at the start and end of the diagnostic.
- Line 27 has the #104 closure owner run steps 1–5 manually, with pinned `gh` and trusted roots and retained sanitized output, until #105 exists.

**New content check.** Line 19 cites a public read-only verification on the official attestation action's ordinary PR #532. It is framed correctly as supporting evidence, not as authority. It names that example's test Sigstore instance and release predicate, and still requires #104 to prove the default public instance, the file-provenance subject and the two-job handoff on its own PR. The demonstrated refusals (PR head as the expected source digest, and a mismatched attempt) match the trust argument in lines 15 and 25.

**Requested checks re-verified.**
- *Approval before privilege scope changes:* lines 11, 33 and 37.
- *Signer job isolation:* lines 31–32.
- *Source, rerun and artifact semantics:* lines 23–27 and 32.
- *Live probe stop:* line 37, plus "no live proof is authorized" in lines 37 and 42.
- *Regular branch workflow with no CI staging branches:* line 7.
- *Budget:* line 40. 0.35 + 3.45 + 0.20 = 4.00 h, and the allocations add up to 3.45 h.
- *Unrounded 90% floor and meaningful tests:* lines 38–39.

Candidate assertions are never treated as authority. Lines 25–26 compare only authenticated certificate extensions and API records, and the JSON stays as reported evidence only.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. **Permission wording in line 32.** "Give the isolated `aitm-ci` signing job only the permissions required by the pinned file-attestation action" is followed by a budget that includes `actions: read`, which the attestation action itself does not need. Consider changing the wording to "only the permissions required by the pinned file-attestation action and the metadata check below". That keeps the sentence consistent with the budget during the control review.
2. **Pin-time check of downloader inputs (line 32).** `skip-decompress` and the digest-mismatch error mode exist only in some versions of the same-run downloader. Consider requiring the control review to confirm that the pinned SHA supports both inputs and fails on unknown inputs or ignored settings. A silently ignored input would bring back extraction before validation. The diagnostic already exercises this path, so this is a review-time convenience and not a gap.

## Decision

accepted
