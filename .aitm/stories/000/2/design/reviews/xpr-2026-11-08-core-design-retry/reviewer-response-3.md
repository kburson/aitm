---
schema: "aitm.review-response/v0"
level: "xpr"
story: 2
role: "reviewer"
round: 3
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "63c7e85d66153db6dc03e5aa41fc8d8191845632"
artifact_digest: "sha256:1e7c48cd13c9919f430a3eaa4b7cbb89094e65c8cc468bf4b4ad8385f6946c5d"
agent:
  host: "claude-code"
  provider: "anthropic"
  model_id: "claude-opus-5-5"
  effort: "high"
reviewer_session: "sha256:e0d3511c0e8892f6656236e16d87ffc3fe607a88aa81d9beda23cebc6be44f01"
session_identity_kind: "native-fingerprint"
started_at: "2026-11-09T06:18:53.686Z"
submitted_at: "2026-11-09T06:19:59.902Z"
start_basis: "prior-submit"
start_source: "author-response-2.md"
finding_ids: []
answered_finding_ids: []
native_source: "native/spec/2026-11-09-core-design-review-095b15003bea70559dd3ce3bb285292a/review-095b15003bea70559dd3ce3bb285292a-reviewer-response-3.md"
native_source_digest: "sha256:fcffded238d61cc766f94b96534c9b84a9d988b2626d7ad143568171281b5298"
---

Mode: `normal`

## Summary

Accepted. This is round 3 of the independent cross-provider (XPR) review by an Anthropic model. I re-read the full current FUR at the digest in the frontmatter above, as the author response asked. I gave particular attention to the configuration, init/bootstrap, verification lane and preparation sections, the event table, the CLI table and the complete acceptance matrix. I checked them against the round-2 findings and the author response. I also searched the FUR for stale wording from the superseded design (mandatory containment, the old `network` key, "relevant tracked" inputs, "must execute the authoritative path") and found none. I made no network calls.

**Round-2 findings, verified against the current FUR:**

- **R2-F001 — resolved.** Lines 434–441 add the assurance table I proposed. `captured-export` (a private copied export, read-only permissions, separate writable roots, isolation from other story-worktree writers) and `contained` (the same plus an OS process-tree profile) are each stated with their limits. `[test] assurance` (line 110) is tip-effective policy chosen explicitly, and silent downgrade is ruled out. The example selects `captured-export`, so verified closure no longer depends on an OS sandbox probe. That resolves the conflict with the Intent's "never the reason a story can't close". Lines 432 and 441 now promise only what the selected level provides. Receipts carry the assurance (lines 260 and 432). Preparation is now concrete:
  - `aitm test prepare [--offline]` (lines 445 and 589);
  - a separate `prepare_network` key (line 111);
  - cache reuse limited to artifacts verified against lockfile hashes;
  - rejection of a stale prepared environment;
  - exact `preparation-unavailable` guidance.

  The Evidence/delivery acceptance row (line 641) tests both lanes, the probe-unavailable path, denied/allowed provisioning, cache reuse, offline misses and the command transformations.
- **R2-F002 — resolved.** Line 120 classifies the identity-issuing backlog provider and its repository/numbering namespace as anchor/routing fields, which require `init --reconfigure` with ID continuity. `githost` and other non-identity provider settings are tip-effective, and a `githost` change cannot redirect the anchored store remote/ref. This is now consistent with the migration namespace guarantees (lines 612–614) and the Init acceptance row (line 632).
- **Round-2 optional suggestions — all adopted.** Bootstrap recovery is now its own paragraph after the init steps (line 149), without the undefined fetch from the initializer. The bytecode and pytest-cache redirection is recorded (line 447). `doctor`/`init` report the macOS `sandbox-exec` deprecation and the specific Linux capability gaps (line 443).

The four round-1 findings remain resolved; I re-checked their current text (lines 120, 145 and 386–392, and the lane section). The FUR still respects every settled owner decision I checked in rounds 1 and 2. It leaves open the expansion-completion interpretation, the second-trip cap, the review-depth matrix and the hosted every-push audit, and it makes no claim that any runtime acceptance test has passed.

This XPR level accepts the pinned FUR version within its scope. Under the FUR's own exact-content rule (line 419), whether SAR/SPR evidence on this new digest is needed for overall acceptance depends on the still-open review-depth policy. This review does not decide that.

## Findings

None.

## Required changes

None.

## Optional suggestions

1. Lines 445–447: say where the prepared-environment identity record lives (clone-local scratch next to the index, or a story evidence record) and whether `test prepare` appends a planning event. Line 447 depends on "recorded" identities, and a builder needs to know whether preparation is a publishable operation, which would mean shared-order and publication cost, or local cache metadata.
2. Line 250: the `core.execution.recorded` phase `prepared` (admission preparation) and the new `aitm test prepare` (environment provisioning) use the same word for different things. Consider renaming one, for example the environment step to "provision" in events and receipts, so that timing reports and `explain` output cannot confuse them.

## Decision

accepted
