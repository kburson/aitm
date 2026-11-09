---
schema: "aitm.review-manifest/v0"
level: "sar"
story: 2
artifact_path: ".aitm/stories/000/2/design/core-design.md"
artifact_base_commit: "981b8d77e2e988e9ec3f79768c7c9728cb66c11a"
integrated_upstream_commit: "7e829d53c39bb100ab6761ea2861c6720a891e70"
integrated_upstream_digest: "sha256:aceb88b37eb36d2bc08b48e639aef4784de2949e95307ead02e5dc13ac9ccbea"
integrated_upstream_blob: "40f1e9f0b9240289c3ebc75e13679aae9a97d6e1"
artifact_base_blob: "1416b6731677c511bb3acc60e665f657e6476902"
base_digest: "sha256:2a31083b0095233d9d2d8ba1bc11d3054bd43fe977b6f90376eda9e8593d4026"
final_digest: "sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9"
rounds: 3
outcome: "exhausted"
reviewer_model_id: "gpt-6.1-sol"
reviewer_effort: "high"
reviewer_session: "01a1be88-ab35-75f0-aa41-1f21e6062d95"
author_model_id: "gpt-6-astra"
author_effort: "xhigh"
author_session: "01a1be2f-9c32-79b1-9385-b18044d32156"
verified_at: "2026-11-09T04:52:32Z"
---

# Core design SAR review record

## Outcome

Exhausted after 3 rounds: the final reviewer response has no required changes and accepts the exact final FUR digest above. This level does not constitute XPR, implementation acceptance or review of the master plan.

## Participants and procedure

The owner selected GPT-6.1 Sol at high effort for the reviewer and GPT-6 Astra at ExtraHigh for the author. The isolated reviewer session wrote only reviewer-response files. The main author session alone revised the FUR and made every commit. Author model/effort were read from its current Codex turn context; they were not inferred from the reviewer choice.

Used the owner’s manual SAR interim procedure and common response templates; the installed peer-review tool has no SAR command. No setup, broker, wrappers or old ai-task-manager tooling were used for this level. Reused the existing clean managed worktree on a new temporary review branch from the refreshed planning tip. The reviewer is the one selected SAR review worker; an independent session is required for the following SPR.

## Review base and incoming upstream

The first reviewer read planning 981b8d77e2e988e9ec3f79768c7c9728cb66c11a with raw digest sha256:2a31083b0095233d9d2d8ba1bc11d3054bd43fe977b6f90376eda9e8593d4026. Before author turn 1, the owner instructed a fast-forward to 7e829d53c39bb100ab6761ea2861c6720a891e70, whose raw FUR digest is sha256:aceb88b37eb36d2bc08b48e639aef4784de2949e95307ead02e5dc13ac9ccbea. Both are recorded above; the first review base is not silently changed.

Upstream independently added document-review turn/completion events, planning/review timing and start bases, backfill provenance and timestamp-fold proposal, review turn/complete/import CLI, migration preservation and acceptance 5c. These were not reviewer requests. The detailed overlap dispositions are in author-response-1.md; the reviewer re-read the complete combined file in round 2. The upstream commit also changed story 1 context/events, which this review did not edit.

upstream-7e829d5.diff isolates that incoming FUR change for attribution. It is not an extra numbered reconstruction step: patch 001 already includes it. Patch 000 remains creation of the original 981b8d7 FUR.

## Patches and reconstruction

Apply patches in numerical order to an empty directory, retaining repository-relative paths. Patch 000 creates the base file. A zero-byte author patch records a no-change turn and is a no-op (git apply --allow-empty). Every resulting file was compared byte for byte to its author-turn FUR and checked by SHA-256.

| Patch | Resulting SHA-256 | Bytes | Source commit |
| --- | --- | --- | --- |
| patch-000.diff | sha256:2a31083b0095233d9d2d8ba1bc11d3054bd43fe977b6f90376eda9e8593d4026 | 39741 | 981b8d77e2e988e9ec3f79768c7c9728cb66c11a |
| patch-001.diff | sha256:195fff0b8903bf1a94d5ae3337d368ba0a7bfeb7110d7dd5276f0f6900d9f4f3 | 104266 | ce2a0da923ddfa98b2bc947f13703ef8447cb76c |
| patch-002.diff | sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9 | 45591 | 74fbdc673cb76eb4b1c27c16cf8bceeb303c1890 |
| patch-003.diff | sha256:d28699369045b9c54451bdb460d70158053e419bd9cfe72ca62bcc3b47183cd9 | 0 | 08f87d4957b4ad65156ced79420a475e8f08c2fc |

The commits are provenance only: reconstruction needs the patches, not these Git objects.

## Finding dispositions

All 14 round 1 findings and all 7 round 2 findings were accepted and resolved. Round 3 independently re-read the complete current FUR and source decisions, including incoming upstream text, and had no required changes. Detailed findings/dispositions remain in the six response files. The final optional suggestion is a reminder for the later build plan to cover the already-defined provisional advisory attempt; it is not a deferred required correction.

## Declined and flagged for owner

None. No required finding was declined or deferred and no new owner decision was needed. Existing open expansion-completion interpretation, second-trip cap, review-depth matrix and GitHub every-push audit mechanism remain open. The task continues to SPR and stops before XPR.

## Calls changed or clarified

Replaced the unsafe event-union exception with ordered core operations and retained conflicts; removed the unconfirmed cap from defaults/tests; defined policy anchors, canonical acceptance/import, actual-evidence delivery, binding generations, trip ordering, qualified timing and review provenance, migration and extension ownership. These refine provisional builder choices under the accepted architecture, without changing owner decisions or numerical limits. The upstream event/timing/CLI additions are separately attributed above and in author-response-1. Manual/native assurance remains explicit rather than inferred from matching bytes.

## Verification

- Parsed every response frontmatter and checked role, level, round, story, model, effort, timestamps, artifact path and base.
- Verified each reviewer input digest against the previous version, each author output digest against its version, and complete finding-ID coverage.
- Applied every patch in order in a temporary directory inside the story collateral folder; every intermediate and final result matched byte for byte. Removed that temporary replay directory.
- Checked relative Markdown links and FUR/Markdown whitespace; no implementation tests apply to this document review. Saved diff context markers are preserved and validated through patch replay.
- Separately replayed patch 000 plus the isolated upstream delta and verified the upstream FUR bytes/digest. The numbered author patch chain already includes that delta.
- Only the final FUR and this level’s collateral are eligible for import into planning; context documents are unchanged.
