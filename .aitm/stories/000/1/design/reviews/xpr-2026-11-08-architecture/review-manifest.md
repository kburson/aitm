---
schema: "aitm.review-manifest/v0"
level: "xpr"
story: 1
artifact_path: ".aitm/stories/000/1/design/architecture.md"
artifact_base_commit: "42c19d20382c324703e791390a6f8747640974b9"
artifact_base_blob: "53345663dd176a1c51703ad26ce34ae791ca83f8"
base_digest: "sha256:faa18da7dfaf52fd9180dcfa241f23020fb02f9bdfce4c5f678a97d4cfc3e6ba"
final_digest: "sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93"
rounds: 2
outcome: "exhausted"
native_review_id: "review-19d319c42ae6474b0b404114fd611a9c"
native_status: "accepted"
commit_mode: "normal"
authority_assurance: "unavailable"
reviewer_model_id: "claude-opus-5-5"
reviewer_effort: "high"
reviewer_session: "sha256:767689f69b20228949123d8faba84671fb404a4027e939125a5f4ad422c4d3a4"
author_model_id: "gpt-6-astra"
author_effort: "xhigh"
author_session: "sha256:7effef95c2db6a7365d1f213e89f5deaaa813da4a15d44efda962e8f41f4ed33"
session_identity_kind: "native-fingerprint"
verified_at: "2026-11-09T04:07:07Z"
native_revision_commit: "572a1772005290bcfcee8531bf5955f7b7d7bbed"
native_finalization_commit: "ac7395f8eb486e02781e554c9dc1c0cc7359b2d4"
---

# Architecture XPR review record

## Outcome and scope

Exhausted after two rounds. All five round 1 findings were accepted and resolved; round 2 accepts the exact final FUR digest above without required changes. The author finalized ordinary reviewer consensus through the project-local broker. No finding was declined, deferred or escalated to the owner. Acceptance concerns architecture.md only; it does not accept the core design or master plan or authorize implementation, closure, delivery or a trunk merge.

## Participants and procedure

The owner selected Astra-6/ExtraHigh as author and Opus 5.5/high as reviewer, resolved to `gpt-6-astra` / `xhigh` in Codex and `claude-opus-5-5` / `high` in Claude Code. The current author turn context confirmed the author selection. The native runtime records both exact selections, providers, hosts and distinct session fingerprints. Both Claude rounds used the same registered session; the second was resumed with the package's recorded selection. Author alone revised the FUR and invoked protocol commits.

Used installed `@kburson/ai-peer-review` 0.4.1 with project-local broker, XPR classification, normal commit mode and manual invitation transport. Native `start`, `launch-reviewer`, `submit`, same-session resume and `finalize` owned the protocol. The installed wrapper/help mismatch was handled by reading the installed package skill and command contracts; there was no direct-review fallback for XPR. Setup and scratch were isolated in the temporary XPR worktree and are excluded from planning publication.

**Assurance limitation:** native `authority_assurance` is `unavailable`; the terminal record reports `human-authority-unavailable`, no external acceptance attestation and declared participant/model evidence. This is normal-mode tool-recorded consensus, not a no-commit test, but it must not be represented as independently attested authority or proof of every turn's actual provider execution configuration. The model/effort selections are supported by runtime records and launch arguments; launch acknowledgements alone are not review completion. Terminal reviewer submission and author finalization establish completion.

Session fields in these exports carry the native SHA-256 fingerprints, identified explicitly as such, rather than raw private provider handles. No scratch state or raw handles are copied into this folder. Native response `started_at` values are participant-registration timestamps reused across rounds, not elapsed-time measurements.

## Acceptance lineage

| Level | Published planning commit | Accepted raw FUR SHA-256 |
| --- | --- | --- |
| SAR (two rounds) | aaacec137378d8636d2a43bb4fa6619e8a417a5e | sha256:faa18da7dfaf52fd9180dcfa241f23020fb02f9bdfce4c5f678a97d4cfc3e6ba |
| SPR (one round) | 42c19d20382c324703e791390a6f8747640974b9 | sha256:faa18da7dfaf52fd9180dcfa241f23020fb02f9bdfce4c5f678a97d4cfc3e6ba |
| XPR (two rounds) | Publication is the planning commit containing this record | sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93 |

SAR and SPR did not review the five XPR additions and do not accept the revised raw digest retroactively. The final architecture acceptance is XPR round 2. Whether to request a delta SAR belongs to the existing open review-depth choice; the XPR reviewer did not require one. The new versioned authored-content digest is a design requirement for future core/peer-review implementation. This review's digests and patches remain raw full-file evidence; no semantic canonicalization has been implemented or used to broaden old acceptance.

## Patches and reconstruction

Apply patches 000 through 002 in order to an empty directory, preserving repository-relative paths. Patch 000 recreates the XPR base, patch 001 contains the reviewed revision and patch 002 is the empty final author acknowledgement (`git apply --allow-empty`). Source commits are provenance only; the patches reconstruct every version without those Git objects.

| Patch | Resulting raw SHA-256 | Patch bytes | Source commit |
| --- | --- | --- | --- |
| [patch-000.diff](patch-000.diff) | sha256:faa18da7dfaf52fd9180dcfa241f23020fb02f9bdfce4c5f678a97d4cfc3e6ba | 24351 | 42c19d20382c324703e791390a6f8747640974b9 |
| [patch-001.diff](patch-001.diff) | sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93 | 13134 | 572a1772005290bcfcee8531bf5955f7b7d7bbed |
| [patch-002.diff](patch-002.diff) | sha256:cf16a5b22f6eaf643885f6694f35d82181a684c36e1b4f2595fb4c8016138b93 | 0 | ac7395f8eb486e02781e554c9dc1c0cc7359b2d4 |

The native manifest's `final_commit` names the last artifact revision (572a177…), while the author-owned finalization commit is ac7395f8eb486e02781e554c9dc1c0cc7359b2d4. The FUR is identical in both. The exported round 2 acknowledgement was written after finalization and creates no additional FUR revision.

## Native-to-portable mapping

- [reviewer-response-1.md](reviewer-response-1.md) and [reviewer-response-2.md](reviewer-response-2.md) preserve their corresponding native bodies and input digests.
- [author-response-1.md](author-response-1.md) preserves the native body; its portable digest names the outgoing artifact from native manifest turn 1. The native protected author header names the incoming artifact. Both originals remain as produced by the tool.
- [author-response-2.md](author-response-2.md) is the explicit post-finalization acknowledgement required by the interim procedure. Native turn 2 has no author response; the terminal manifest plus finalization commit supplies its protocol provenance.
- Native startup/invitation paths describe the original temporary physical worktree. They are historical routing evidence, not runnable recovery instructions after that worktree is archived.

All native originals are retained unchanged:

| Native original | SHA-256 |
| --- | --- |
| [review-19d319c42ae6474b0b404114fd611a9c-author-response-1.md](native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-author-response-1.md) | sha256:420de6e0751b3e86c51859fb92878bd17f8f8878a703618145c342d0ba24038b |
| [review-19d319c42ae6474b0b404114fd611a9c-author-startup.md](native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-author-startup.md) | sha256:b2e7759797482052439d307c883f516b02fb5b2aa13f93c1920838e6ab36410c |
| [review-19d319c42ae6474b0b404114fd611a9c-review-manifest.md](native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-review-manifest.md) | sha256:6a3f51f17bca728d7ce55e1ab4ec9d43e0356fb80ba41c6141ab9ecb80d126ee |
| [review-19d319c42ae6474b0b404114fd611a9c-reviewer-invitation.md](native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-reviewer-invitation.md) | sha256:cc1831db120d865b70c889041730ee45fe2c4401179ea8ea65a4e4add13aaf29 |
| [review-19d319c42ae6474b0b404114fd611a9c-reviewer-response-1.md](native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-reviewer-response-1.md) | sha256:c38dbea3193984a27be1b4af6bd3c50ed71195446d4049c524de5cadda3b05e4 |
| [review-19d319c42ae6474b0b404114fd611a9c-reviewer-response-2.md](native/spec/2026-11-09-architecture-review-19d319c42ae6474b0b404114fd611a9c/review-19d319c42ae6474b0b404114fd611a9c-reviewer-response-2.md) | sha256:c0644aa843e02c1deb96540993cb9e5ea1764e1ae7609088d8a3dd079c42d586 |

## Finding dispositions and calls clarified

| Finding | Disposition and resulting architecture obligation |
| --- | --- |
| R1-F001 | Accepted: one versioned canonical authored-content digest excludes only schema-defined generated metadata; retain raw reconstruction evidence and require M1 migration of v0 acceptance before metadata regeneration. |
| R1-F002 | Accepted: pre-M1 checkout import becomes M1 core compare-and-swap import before checkout retirement; review branches remain distinct from the protected planning ref. |
| R1-F003 | Accepted: git-host owns delivery/merge evidence; verified mapping handles squash/rebase without equal SHA requirements; core-only/offline delivery needs verifiable evidence and uncertain remote delivery stays pending. |
| R1-F004 | Accepted: committed default-branch policy governs transitions; branch-local edits take effect after delivery and effective policy provenance is recorded. |
| R1-F005 | Accepted: viewer builds share the workflow-ref constraint; suitable non-push triggers may disclose freshness while every-push audit remains required. |

Optional wording clarifies that event-union/multiple-writer is not granted an exception to the owning-writer rule. Core review must reconcile its proposed root README allowance without assuming a new planning-path exception. Export normalization preserves protected native originals. These are architecture refinements and section obligations, not changes to `[user]`/`[agreed]` decisions, numerical limits or milestone order. The choice of canonicalization instead of relocating required frontmatter preserves the owner's metadata decision.

## Open decisions and limitations

No new owner decision is required to complete XPR. Existing open items remain: expansion-trigger interpretation; unconfirmed second-trip cap; every-push audit mechanism for an isolated data-only planning ref; PyPI meta-package name; peer-review refactor location and review-depth matrix (including which document comes next); GitHub human-edit handling; Grok MCP and Codex/Grok custom-agent capabilities. The core's concurrency, canonicalization/migration, policy selection/freshness, delivery and evidence algorithms still require their own review. No context document is accepted or modified here.

## Verification

Verified at 2026-11-09T04:07:07Z:

- Parsed all four exported response headers and checked schema, role, level, round, story, model, effort, fingerprint, timestamps, path, base and per-turn raw digests.
- Matched every finding ID to the author disposition; checked round 2 acceptance and no remaining findings.
- Verified native response hashes against the terminal manifest, export-source hashes against unchanged originals, and artifact history against Git blobs.
- Applied patches 000, 001 and 002 to an empty temporary directory inside this folder; every intermediate result and the final file matched the corresponding Git artifact byte for byte and by SHA-256. Removed the replay directory.
- Checked FUR/export relative links and Markdown whitespace; checked the FUR diff with `git diff --check`. The staged Markdown whitespace check also passes. The unrestricted staged check reports 18 trailing-whitespace lines, all exactly the single-space blank-context marker in patch-001.diff; these are required patch syntax and are preserved. No Markdown whitespace errors occur. Patches are checked by their Git-generated bytes and full replay.
- Checked that native revision/finalization commits change only the FUR and this XPR folder. Context documents and existing SAR/SPR records are unchanged. Only these two exact paths are eligible for import into planning.
- No implementation tests apply to this documentation-only review.

Planning publication and cleanup are operational steps after these checks; the containing planning commit identifies publication without a self-referential hash in this file.
